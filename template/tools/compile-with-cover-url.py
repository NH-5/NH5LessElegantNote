#!/usr/bin/env python3
import argparse
import hashlib
import mimetypes
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


COVER_URL_RE = re.compile(
    r"(?P<key>\bcover-image(?:-url)?)(?P<space>\s*:\s*)\"(?P<url>https?://(?:\\.|[^\"\\])*)\""
)

EXT_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
}

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".pdf"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compile a Typst file after caching cover-image URLs locally."
    )
    parser.add_argument("input", help="Input .typ file")
    parser.add_argument(
        "output",
        nargs="?",
        help="Output file. Defaults to the input filename with a .pdf suffix.",
    )
    parser.add_argument(
        "typst_args",
        nargs=argparse.REMAINDER,
        help="Extra arguments passed to `typst compile` after `--`.",
    )
    return parser.parse_args()


def typst_string(value):
    return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\""


def guess_ext(url, headers, data):
    url_ext = Path(urlparse(url).path).suffix.lower()
    if url_ext in SUPPORTED_EXTS:
        return url_ext

    content_type = headers.get("Content-Type", "").split(";")[0].strip().lower()
    if content_type in EXT_BY_CONTENT_TYPE:
        return EXT_BY_CONTENT_TYPE[content_type]

    guessed = mimetypes.guess_extension(content_type)
    if guessed in SUPPORTED_EXTS:
        return guessed

    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if data[:12].startswith(b"RIFF") and data[8:12] == b"WEBP":
        return ".webp"
    if data.lstrip().startswith(b"<svg"):
        return ".svg"
    if data.startswith(b"%PDF"):
        return ".pdf"

    return ".img"


def cache_cover_image(url, base_dir):
    cache_dir = base_dir / ".typst-cache" / "cover-images"
    cache_dir.mkdir(parents=True, exist_ok=True)

    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    existing = list(cache_dir.glob(f"{digest}.*"))
    if existing:
        return existing[0]

    request = Request(url, headers={"User-Agent": "NH5LessElegantNote/cover-url"})
    with urlopen(request, timeout=30) as response:
        data = response.read()
        headers = response.headers

    ext = guess_ext(url, headers, data)
    target = cache_dir / f"{digest}{ext}"
    target.write_bytes(data)
    return target


def split_typst_comment(line):
    in_string = False
    escaped = False

    for index, char in enumerate(line):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "\"":
                in_string = False
        else:
            if char == "\"":
                in_string = True
            elif char == "/" and index + 1 < len(line) and line[index + 1] == "/":
                return line[:index], line[index:]

    return line, ""


def rewrite_cover_urls(source, base_dir):
    downloaded = []

    def replace(match):
        url = match.group("url")
        cached = cache_cover_image(url, base_dir)
        downloaded.append((url, cached))
        relative = cached.relative_to(base_dir).as_posix()
        return f"cover-image{match.group('space')}image({typst_string(relative)})"

    rewritten_lines = []
    for line in source.splitlines(keepends=True):
        code, comment = split_typst_comment(line)
        rewritten_lines.append(COVER_URL_RE.sub(replace, code) + comment)

    rewritten = "".join(rewritten_lines)
    return rewritten, downloaded


def main():
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.is_file():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_path.with_suffix(".pdf")
    )
    typst_args = args.typst_args
    if typst_args[:1] == ["--"]:
        typst_args = typst_args[1:]

    base_dir = input_path.parent
    source = input_path.read_text(encoding="utf-8")
    rewritten, downloaded = rewrite_cover_urls(source, base_dir)

    for url, cached in downloaded:
        print(f"Cached cover image: {url} -> {cached}", file=sys.stderr)

    cmd = ["typst", "compile", *typst_args, "-", str(output_path)]
    result = subprocess.run(
        cmd,
        input=rewritten,
        cwd=base_dir,
        text=True,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
