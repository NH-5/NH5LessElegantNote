// 封面页

#import "../utils/font-style.typ": 字号, 字体

#let cover-image-url-error = "Typst 不能直接从 HTTP/HTTPS 链接读取封面图。请使用 template/tools/compile-with-cover-url.py 编译，或先把图片下载到本地后通过 cover-image: image(\"...\") 传入。"

#let is-url(value) = {
  type(value) == str and (
    value.starts-with("http://") or value.starts-with("https://")
  )
}

#let render-cover-image(source) = {
  if type(source) == content {
    source
  } else if is-url(source) {
    panic(cover-image-url-error)
  } else {
    image(source)
  }
}

#let elegant-cover(
  // documentclass 传入的参数
  twoside: false,
  info: (:),
  // datetime-display: datetime-display,
) = {
  // 1.  默认参数
  info = (
    title: ("LessElegantNote：Typst笔记模版"),
    author: "Choglost",
    date: datetime.today(),
    cover-image: none,
    cover-image-url: none,
  ) + info

  // 2.  对参数进行处理
  // 处理提交日期
  if type(info.date) == datetime {
    info.date = info.date.display("[year]/[month]/[day]")
  }
  // // 如果是字符串，则使用换行符将标题分隔为列表
  if type(info.title) == str {
    info.title = info.title.split("\n")
  }

  // 3.  正式渲染
  // 双面打印模式
  // pagebreak(weak: true, to: if twoside { "odd" })

  set page(margin: 0pt)

  let cover-source = if info.cover-image-url != none {
    info.cover-image-url
  } else {
    info.cover-image
  }

  if cover-source != none {
    render-cover-image(cover-source)
    v(20pt)
  } else {

  }

  set align(horizon)

  for s in range(info.title.len()) {
    text(font: 字体.宋体, size: 字号.一号)[#h(40pt)*#info.title.at(s)*]
    v(20pt)
  }

  text(font: 字体.楷体, size: 字号.小四)[#h(50pt)作者：#info.author]
  v(0pt)
  if (info.date != none) {
    text(font: 字体.楷体, size: 字号.小四)[#h(50pt)日期：#info.date]
  }
  v(50pt)
}
