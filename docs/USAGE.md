# 如何使用这些 Skill

这部分给第一次接触 Skill 的用户看。不同智能体的菜单名称可能不同，但共同点都是：加载一个包含 `SKILL.md` 的 Skill 文件夹，然后用自然语言提出任务。

## 先写清楚你的需求

一次请求最好包含四件事：

1. **要做什么**：例如“把这张照片做成平面构成海报”。
2. **用哪个平台/比例**：例如“小红书 3:4”“抖音 9:16”。按用途原生构图，不要让智能体最后硬拉伸。
3. **保留和禁止什么**：人物身份、产品文字、原图关系、不能出现的元素。
4. **要什么状态**：先要 `test` 返图，还是已经确认后要 `accepted` 成品。

可以直接复制这个句式：

```text
请使用 <skill-name>。
目标：<我要做的图>。
平台/比例：<平台 + 原生比例>。
必须保留：<人物/物体/文字/关系>。
禁止出现：<不想要的元素>。
先给我 test 返图，不要自动归档。
```

## 在 Codex 中使用

### 从 GitHub 安装

```bash
git clone https://github.com/Mariposa-FLOA/image-skill.git
mkdir -p ~/.codex/skills
cp -R image-skill/skills/graphic-composition-poster ~/.codex/skills/
```

把最后一行的目录名换成需要的 Skill。安装本次发布的全部 Skill：

```bash
for skill in image-skill/skills/*; do
  cp -R "$skill" ~/.codex/skills/
done
```

重启 Codex 后，用目录名对应的 `$skill-name` 调用：

```text
请用 $symbolic-narrative-poster，把这张照片做成小红书 3:4 海报。
只保留一个视觉隐喻，文字用中文，先给 test，不要归档。
```

### 只安装一个 Skill

复制完整的 Skill 目录，不要只复制 `SKILL.md` 后删除它依赖的 `references/`、`scripts/` 或 `assets/`。

### Image 2 或其他出图模型

这些 Skill 是模型无关的 Markdown 工作流，不锁定某一家出图模型。先在 Codex、豆包、WorkBuddy 等智能体中加载 Skill，再让智能体调用 Image 2、Seedream 或其他出图模型（例如“使用这个 Skill，让 Image 2 按规则出图”）。模型不支持某个参数时，保留 Skill 的构图、人物/物体保护和负面约束，只按该模型的输入格式改写调用层；不要删掉 `SKILL.md` 的规则。

如果只是临时在聊天框试用，可从 chat-ready/ 下载单个 .md 文件，连同参考图一起上传，并发送“请把附件当作本次任务的视觉工作规范，不要复述，直接按它出图”。完整句式和豆包示例见 docs/CHAT-DROP.md。

## 在 WorkBuddy / Workbuddy 中使用

WorkBuddy 的菜单会随版本、企业配置和客户端形态变化。请在它的 **Skills / 技能 / 自定义能力 / Agent 指令** 位置选择下面一种通用路径：

### 路径 A：导入 Skill 文件夹

1. 下载或克隆本仓库。
2. 选择“导入本地文件夹”或“上传技能包”。
3. 选择 `skills/<skill-name>/` 这一层目录。
4. 确认 `SKILL.md` 和同目录的 `references/`、`scripts/`、`assets/` 一起保留。
5. 启用后用自然语言调用：

```text
使用 graphic-composition-poster，做一张抖音 9:16 竖版图。
画面先做无字构图，再加我提供的准确文字；先返回 test。
```

### 路径 B：平台只接受 Markdown 或提示词

1. 打开对应目录的 `SKILL.md`。
2. 将完整内容粘贴到“自定义 Skill / Agent 指令 / 工作流说明”。
3. 如果平台支持附件，再上传同一目录的参考文件和脚本。
4. 首次运行时写出 Skill 名称、平台比例和保留项。

只粘贴 Markdown 时，缺少配套文件可能导致部分参考资料或脚本不可用；不要把一段文字当成完整安装。

### 路径 C：平台支持 Git URL 导入

如果 WorkBuddy 提供“从 GitHub/Git URL 导入”，使用：

```text
https://github.com/Mariposa-FLOA/image-skill
```

导入后检查技能列表是否识别到 `skills/` 下的子目录。若只支持本地上传，改用路径 A。

## 如何选择 Skill

- 电影叙事、campaign 主视觉：`cinematic-key-art-poster`
- 网格、裁切、字体和留白：`graphic-composition-poster`
- 空间折叠、尺度矛盾：`impossible-space-editorial-poster`
- 专辑封面与分层母版：`music-album-cover-art`
- 折射、镜面、玻璃和透明介质：`optical-refraction-visual`
- 一个清楚的视觉隐喻：`symbolic-narrative-poster`
- Y2K 街头剪裁拼贴：`y2k-street-cutout-poster`
- 限色丝网、动态轮廓、纸雕、矿物浮雕、混合媒介、复古胶印或翻页展示：选择对应的 Skill。

一次只选一个主导视觉 Skill，避免多个冲突机制同时接管一张图。

## 图片、文字和交付状态

- 上传图片时说明它是“必须保留的源图”“参考图”还是“仅供灵感”。
- 产品、包装、截图中的关键文字写明“保持原样”。
- 文字较多时，先做无字核心视觉，再用本地活字或 SVG 加字。
- 请求中直接写平台和原生比例：`小红书 3:4`、`抖音 9:16` 等。
- `test` 是测试稿；只有明确确认后才进入 `accepted` 成品归档。

## 安全边界

本仓库只发布我们的原创 Skill。外部初始 Skill、蒸馏加强 Skill、私人输入文件和未授权示例图不在发布范围内。安装第三方 Skill 前，先检查来源、许可证和脚本内容。
