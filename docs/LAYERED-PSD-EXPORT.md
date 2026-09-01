# 海报 PSD 分层导出

仓库新增 `poster-layered-psd-export`，用于把已经完成分层规划的海报导出为可以在 Photoshop 继续编辑的 PSD。

## 真实支持什么

- PSD 画布尺寸、DPI 和 RGB/8 位信息；
- 背景、主体、几何色块、拼贴、阴影、纹理、字标等命名图层；
- 图层顺序、可见性、不透明度和常用混合模式；
- 中文图层名称；
- 内嵌合并预览；
- 对应的 `.manifest.json`，记录每层的来源、角色和编辑性。

导出的是栅格像素图层。它们可以在 Photoshop 里移动、蒙版、涂抹、擦除、调色和继续合成。文字只有在宿主额外创建了原生 Photoshop 文字层时才是可编辑文字；默认导出器会把文字标记为 `[raster text]`，不会虚报成活字。

## 使用方式

先准备一个 `project.json`。`layers` 按从下到上的顺序写，每个 PNG 与画布保持同尺寸：

```json
{
  "canvas": { "width": 1080, "height": 1440, "dpi": 300 },
  "preview": "preview/final.png",
  "layers": [
    {
      "id": "background",
      "name": "背景 / 色场",
      "kind": "background",
      "file": "layers/background.png",
      "opacity": 1,
      "blend": "normal",
      "visible": true
    },
    {
      "id": "source-anchor",
      "name": "主体 / 源图锚点",
      "kind": "source",
      "file": "layers/source-anchor.png",
      "opacity": 1,
      "blend": "normal",
      "visible": true
    },
    {
      "id": "brand-lockup",
      "name": "FLOA Mariposa 字标",
      "kind": "text",
      "file": "layers/brand-lockup.png",
      "opacity": 1,
      "blend": "normal",
      "visible": true,
      "native_text": false
    }
  ]
}
```

运行导出和验证：

```bash
python3 skills/poster-layered-psd-export/scripts/export_layered_psd.py \
  --project path/to/project.json \
  --output path/to/poster.psd

python3 skills/poster-layered-psd-export/scripts/validate_psd.py \
  path/to/poster.psd
```

输出 PSD 和同名 `.manifest.json`。导出器拒绝覆盖已有文件。

## 和海报 Skill 一起使用

```text
请使用 $floa-mariposa-visual-system。
先做 FLOA Mariposa 海报，并从一开始保留背景、主体、几何图形、字标、纹理和阴影的独立图层。
最后使用 $poster-layered-psd-export 导出 Photoshop PSD 和分层清单。
文字如果不是原生 PS 文字层，请明确标注为栅格文字。
先返回 test。
```

如果只有一张已经合并的 PNG，可以把它作为一个诚实命名的 `flattened artwork` 图层放进 PSD，但不能把它拆成虚假的背景、主体、文字层，也不能声称这些元素已经独立可编辑。
