# 视觉 Skill 的参考与升级机制

这个仓库会持续参考国内外设计作品、品牌识别、编辑设计、印刷/拼贴实践和 Agent Skill 规范，但只提炼可复用的判断，不复制外部作品。

## 第一轮升级结论

本轮研究把我们的升级方向从“找一个更漂亮的风格词”改成了四个可执行层：

1. **系统而不是模板**：固定品牌识别、排版态度和质量标准；每张作品改变源图隐喻、构图轴线、色场和材质。
2. **文字是结构**：建立字体行为、比例、边缘、裁切和层级，而不是每次换一个看起来酷的字体。
3. **材质是动作**：撕、贴、错位、半调、扫描、折叠等材质必须改变构图关系，不能只覆盖一层“复古颗粒”。
4. **本土证据与国际方法并用**：可以观察中文环境中的真实文字痕迹，也可以借鉴国际编辑系统的网格和变体逻辑，但不制造假民俗、假档案或照搬外部版式。

## 研究来源与落地

- 国内： [GDC Award 2025 / TDC](https://tdc.org/winner/gdc-award-2025-3/) 展示了从街头店招、错位文字和时间痕迹提炼系列识别的方法；这被转成 FLOA 的“真实文字证据 + 系列变化”规则。
- 国内： [ZCOOL 2025 海报汇总](https://www.zcool.com.cn/work/ZNzE1OTk4NDA%3D.html) 显示中英文字、多变色彩和不同构图可以在清晰概念下共存；这被转成多语言层级和单一首读事件规则。
- 国外： [AIGA Eye on Design 的 Acid Grotesk 案例](https://eyeondesign.aiga.org/a-highly-functional-sans-serif-with-a-healthy-dose-of-weirdness/) 说明字体身份应能跨海报、书籍、网站等触点适配；这被转成 FLOA 的字体行为系统。
- 国外： [AIGA 关于杂志情绪与变化的案例](https://eyeondesign.aiga.org/david-benski-on-the-mood-of-magazines-and-the-virtues-of-change/) 说明稳定工具包可以支撑每期不同的表面；这被转成品牌固定项与系列变量分离。
- 国外： [It’s Nice That 的 Tapeface](https://www.itsnicethat.com/articles/varanda-rege-tapeface-graphic-design-project-061025) 和 [Yoffdog](https://www.itsnicethat.com/articles/yoffdog-graphic-design-discover-300925) 说明材质和字形可以形成自己的动作/规则；这被转成“材质必须服务概念”的检查。

详细的逐条记录、应用方式和排除项见 [`skills/floa-mariposa-visual-system/references/reference-led-evolution.md`](../skills/floa-mariposa-visual-system/references/reference-led-evolution.md)。

## 每次升级的操作标准

1. 先做一轮有边界的检索：至少两条国内、两条国外来源，并记录日期。
2. 每条来源只提炼一个可观察的设计决策，不把“高级”“未来感”“复古”等形容词直接写进 Skill。
3. 对每条决策写清楚：学什么、如何转成我们的规则、明确不复制什么。
4. 每轮最多引入两个新的结构动作，并保留上一版作为对照。
5. 用未作为研究样本的图片做 test，检查品牌名、源图特异性、首读层级、构图质量和原创边界。
6. 通过校验后再更新 `SKILL.md`、参考文件、`chat-ready` 和变更记录。

## Agent Skill 侧的升级标准

Skill 不是一段散文提示词，而是可加载的文件夹：核心 `SKILL.md`、按需加载的 `references/`、必要时的脚本和测试用例。触发描述要写清楚“做什么”和“什么时候用”；主文件负责路由、决策、边界和验收，研究笔记放在参考文件中。

这与 [GitHub 的 Agent Skills 文档](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)所说明的文件夹、`SKILL.md`、可选资源和按需加载方式一致。第三方 Skill 只学习其结构和方法，安装前仍要审查来源、脚本和权限。
