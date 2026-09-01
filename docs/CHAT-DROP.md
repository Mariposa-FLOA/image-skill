# 直接拖进聊天框使用

如果你的智能体支持上传 Markdown 或文本文件，不需要先安装整个 Skills 目录。到 chat-ready/ 下载一个与需求对应的 .md 文件，直接拖进 Codex、豆包、WorkBuddy 或其他聊天智能体，然后发送：

```text
请把我上传的 Markdown 当作本次任务的视觉工作规范。
不要复述规范，直接按它完成下面的图片任务。
目标：<写清楚主题；平台/比例可选，未指定则由 AI 根据源图决定；必须保留和禁止出现的内容>
先返回 test 图，等我确认后再做 accepted 成品。
```

## 豆包

在豆包对话中上传 chat-ready/<skill-name>.md，再使用上面的调用句式。豆包负责理解附件和任务；需要出图时，在豆包可用的图片创作入口中选择 Image 2、Seedream 或实际显示的生图模型。如果使用自定义智能体，也可以把该文件的完整内容粘贴到智能体设定中。

## Codex

需要长期复用时，把完整目录安装到 ~/.codex/skills/；只想临时试一次时，直接上传同一个 chat-ready/<skill-name>.md 并说明“按附件执行”。

## 其他图片模型

只要聊天产品能读取附件并调用图片生成，就可以采用相同方式。模型不支持某个参数时，只调整调用格式，保留附件中的构图、主体保护、文字和负面约束。若产品只能生成提示词而不能出图，就把返回的提示词复制到它的图片生成入口。

## 注意

- 一次上传一个主 Skill，避免多个视觉机制互相覆盖。
- 需要参考图时，把参考图和 Skill 文件一起上传，并明确哪张是必须保留的源图、哪张只是风格参考。
- page-flip-showcase 的脚本输出、可编辑分层或精确排版仍可能需要宿主的文件工具；单靠图片模型不能保证交互或像素级可编辑结果。
- chat-ready/ 是由 skills/ 导出的单文件副本；修改 Skill 后重新运行 python3 scripts/build_chat_drop.py。

## page-flip-showcase 的投喂方式

如果只想让一个智能体处理这一组海报，直接下载 [`chat-ready/page-flip-showcase.md`](../chat-ready/page-flip-showcase.md)，连同图片一起上传，并明确你要哪一种结果：

```text
请按附件中的 page-flip-showcase 规则处理这些海报。
输出：可点击的一篇一篇翻页电子画册（如果当前环境不支持网页，请明确告诉我）。
顺序：按上传顺序；固定身份文字：左上 FLOA，右下 Mariposa。
视觉要求：逐张分析海报色彩、构图、排版和母题，背景用源图相关的拼贴纸片组织，不要使用一套固定线条。
先给 test，确认后再给 accepted 成品。
```

要长期在 Codex、WorkBuddy 或其他 Skill 系统中复用，则导入完整的 `skills/page-flip-showcase/` 文件夹。完整导入才能使用同目录的参考契约和静态合成脚本；单文件投喂适合理解规则，但不保证宿主一定能写网页或渲染 MP4。

## FLOA Mariposa 品牌 Skill

一次性使用时，下载 [`chat-ready/floa-mariposa-visual-system.md`](../chat-ready/floa-mariposa-visual-system.md)，和你的海报或产品图一起上传：

```text
请把附件中的 Markdown 当作 FLOA Mariposa 的视觉工作规范。
把我上传的图片做成产品品牌海报，使用“新编辑主义视觉”，不要简单套复古、Y2K 或赛博朋克。
保留 FLOA Mariposa 的准确拼写；根据源图分析色彩、构图、视觉事件和留白；先返回 test，不要自动归档。
```

如果要做多张系列海报，额外说明“保持品牌统一，但每张改变源图隐喻、构图轴线和色彩关系”。如果要做可点击画册或 MP4，再同时使用 `page-flip-showcase` 处理翻页机制。
