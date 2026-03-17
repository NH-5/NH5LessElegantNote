# NH5LessElegantNote

## 项目特色 Features
这是一个Typst笔记模板，是在[LessElegantNote](https://github.com/choglost/LessElegantNote)的基础上修改而成的。感谢原作者的工作。

- **公式自动编号**：支持按章节自动编号（例如 1.5, 2.3），并可手动开启或关闭。
- **项目结构清晰**：基于模块化设计，方便自定义。

## 使用指南 Usage

### 1. 准备环境
- 安装 [VS Code](https://code.visualstudio.com/)。
- 安装 [Tinymist Typst](https://marketplace.visualstudio.com/items?itemName=myriad-dreamin.tinymist) 插件。

### 2. 快速开始
1. 克隆或下载本仓库。
2. 在项目根目录下创建 your `.typ` 文件（例如 `note.typ`）。
3. 使用以下代码调用模板：

```typst
#import "template/conf.typ": conf

#show: conf.with(
  info: (
    title: "LessElegantNote：一个Typst笔记模版",
    author: "Your Name",
    date: datetime.today(),
    // cover-image: "assets/coverimage.jpg", // 可选封面图
    style-name: "maths", // 可选风格: "maths", "literature", "book"
    equation-numbering: true, // 是否开启公式按章节自动编号，默认为 true
  )
)

= 第一章

这里是正文内容。
```

### 3. 项目结构
- `template/`: 模板核心文件。
  - `conf.typ`: 模板入口，推荐通过此文件调用。
