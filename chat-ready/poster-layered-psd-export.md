---
name: poster-layered-psd-export
description: Export a poster, campaign visual, brand image, or other composed artwork as a real Photoshop-readable layered PSD for continued editing. Use whenever the user asks for PSD, Photoshop layers, editable poster files, layered export, or wants to continue editing a generated poster in Photoshop. Require an explicit layer manifest and never claim a flattened PNG is a layered PSD.
---

# Poster Layered PSD Export

## Mission

Turn an already-composed poster project into a Photoshop-readable PSD with named, aligned pixel layers, preserved opacity, supported blend modes, an embedded merged preview, and a sidecar manifest that tells the designer what can be edited.

This Skill is an export step, not an image generator. The upstream poster or brand Skill must create the layer assets while composing the visual. A final flattened PNG cannot be reliably reverse-engineered into semantic background, subject, text, texture, and shadow layers.

The bundled scripts require Python 3 and Pillow for PNG decoding. A Photoshop installation is not required to write or structurally validate the file, but the final `accepted` status should wait for the user or a host tool to open the PSD and confirm the layer experience.

## When to use

Use this Skill when the user says:

- “导出 PSD” / “给我 Photoshop 分层文件”；
- “我要拿去 PS 继续编辑”；
- “背景、主体、文字、阴影分开”；
- “给我可编辑的海报源文件”；
- “不要只有一张 PNG，要分层”。

If the user only asks for a PNG/JPG, do not create a PSD by default. If the host can only provide a flattened image, say so and do not rename the image as a PSD.

## Layer contract

Read [references/layer-manifest-contract.md](references/layer-manifest-contract.md) before building or validating the project manifest.

The manifest must define:

- canvas width, height, and optional DPI;
- one flattened preview with the same dimensions;
- at least two meaningful layers for a layered deliverable;
- layer order from bottom to top;
- one full-canvas RGBA PNG per layer;
- layer name, kind, opacity, visibility, and supported blend mode;
- notes describing whether a layer is a background, source image, shape, shadow, texture, or text fallback.

Use full-canvas aligned assets rather than arbitrary trimmed fragments. This makes the file easy to continue editing and prevents layer registration drift.

## Recommended poster layer stack

Use only the layers the actual design contains. A typical stack is:

1. `background / colour field`;
2. `depth plane / architectural shape`;
3. `source image / subject`;
4. `headline / product lockup`;
5. `collage / print material`;
6. `shadow / light`;
7. `finishing grain or registration`.

Do not create meaningless empty layers just to increase the layer count. If two visual roles were baked together upstream, label the layer honestly instead of pretending they are independently editable.

## Export

From the repository root, run:

```bash
python3 skills/poster-layered-psd-export/scripts/export_layered_psd.py \
  --project path/to/project.json \
  --output path/to/floa-mariposa-poster.psd
```

The exporter refuses to overwrite an existing PSD or manifest. It writes:

- the PSD with RGBA pixel layers, layer names, opacity, visibility, blend mode, and an embedded composite preview;
- a matching `.manifest.json` sidecar with canvas, order, layer roles, and editability notes.

Then validate the generated file:

```bash
python3 skills/poster-layered-psd-export/scripts/validate_psd.py \
  path/to/floa-mariposa-poster.psd
```

The validator checks the Photoshop signature, RGB/8 structure, canvas, layer count, layer records, channel data, compression sections, Unicode names, and composite image data.

## Text and editability truth

The exporter creates raster pixel layers. A layer named `headline [raster text]` can be moved, masked, recoloured, erased, and retouched in Photoshop, but its characters are not a native Photoshop type layer.

Only call text “live/editable text” when the host actually produced a native Photoshop text layer or a separate verified vector/text source. Otherwise include the raster-text warning in the sidecar manifest and delivery note.

## Quality gate

Before delivery, confirm:

- the output is a valid PSD file, not a renamed PNG or ZIP;
- the preview and every layer share the declared canvas size;
- Photoshop layer order matches the manifest's bottom-to-top order;
- opacity, visibility, and supported blend modes are preserved;
- Chinese and product-name layer labels survive through Unicode names;
- at least two meaningful visual roles are independently editable;
- text editability is reported truthfully;
- existing output files were not overwritten;
- the sidecar manifest is present and matches the PSD;
- the PSD opens or is structurally validated by an available host tool before claiming completion.

## Boundaries

- Do not promise semantic separation from a single flattened image.
- Do not invent hidden layers, masks, vectors, or live text that were never created.
- Do not include user source images in a public repository unless the user explicitly authorizes that exact publication.
- Do not silently change the visual result while exporting; the embedded preview must match the approved composite.
- Do not require a paid plugin or a specific Photoshop installation. The PSD writer and validator are local, standard-library/Pillow-based tools.

## Delivery contract

Return the PSD path, sidecar manifest path, layer count, canvas/DPI, and an explicit note distinguishing raster layers from native live text. Mark the result `test` until the user confirms it opens and remains useful in Photoshop; only then mark it `accepted`.
