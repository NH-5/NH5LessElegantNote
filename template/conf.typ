#import "lib.typ": documentclass

#let conf(
  info: (:),
  twoside: false,
  // 允许传入 content 作为 body
  doc
) = {
  // 调用 documentclass 获取配置好的函数
  let (
    doc: doc-setup, 
    mainmatter, 
    cover, 
    outline-page,
    appendix,
  ) = documentclass(
    twoside: twoside,
    info: info,
  )

  // 1. 应用基础文档设置 (页面大小, margin 等)
  show: doc-setup

  // 2. 显示封面
  cover()

  // 3. 显示目录
  outline-page()

  // 4. 应用正文格式设置 (字体, 标题编号等)
  show: mainmatter

  // 5. 显示正文内容
  doc
}
