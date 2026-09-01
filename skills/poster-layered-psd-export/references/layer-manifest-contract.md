# Layer manifest contract

`project.json` is the input contract for the PSD exporter. It is deliberately small so a poster Skill, compositor, or another agent can create it without adopting a framework.

## Example

```json
{
  "canvas": {
    "width": 1080,
    "height": 1440,
    "dpi": 300
  },
  "preview": "preview/final.png",
  "layers": [
    {
      "id": "background",
      "name": "背景 / 色场",
      "kind": "background",
      "file": "layers/background.png",
      "opacity": 1,
      "blend": "normal",
      "visible": true,
      "notes": "Full-canvas colour field"
    },
    {
      "id": "source-anchor",
      "name": "主体 / 源图锚点",
      "kind": "source",
      "file": "layers/source-anchor.png",
      "opacity": 1,
      "blend": "normal",
      "visible": true,
      "notes": "Protected source-derived subject"
    },
    {
      "id": "brand-lockup",
      "name": "FLOA Mariposa 字标",
      "kind": "text",
      "file": "layers/brand-lockup.png",
      "opacity": 1,
      "blend": "normal",
      "visible": true,
      "native_text": false,
      "notes": "Raster text fallback; replace with live type in Photoshop"
    }
  ]
}
```

## Rules

- `layers` are listed bottom to top in the JSON; the PSD stores them in Photoshop's top-to-bottom record order.
- `preview` must be a PNG with the exact declared width and height.
- Every `layer.file` must be a PNG with the exact declared width and height. Use RGBA PNG for transparent overlays; RGB PNG is accepted for opaque layers.
- `opacity` is a number from `0` to `1` and is written to the PSD layer record.
- Supported `blend` values are `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, and `subtract`.
- `kind` is descriptive metadata. Common values are `background`, `source`, `shape`, `text`, `texture`, `shadow`, and `raster`.
- `native_text` is informational. The bundled exporter always writes pixel data; set it to `false` unless a separate native Photoshop text layer was created and verified by the host.
- `notes` should describe what a designer can safely edit, not a fictional implementation detail.

## Editability levels

| Level | Meaning |
| --- | --- |
| `raster-pixel-layer` | Move, mask, paint, recolour, erase, and retouch in Photoshop; text is not live type. |
| `native-text` | Native Photoshop text layer made by a host-specific exporter; not produced by the bundled writer. |
| `vector-source` | Keep a separate SVG/vector source when crisp geometric editing is required. |

When native text or vector fidelity matters, deliver the extra source alongside the PSD rather than overstating what the PSD contains.
