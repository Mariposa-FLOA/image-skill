# Editable Layer Delivery

Read this reference whenever the user wants a reusable master, secondary editing, variants, localisation, platform crops, or a complete release package. A flat AI render cannot become honestly layered by renaming or duplicating it; plan separable elements before generation.

## Universal delivery contract

Every editable delivery contains:

```text
release-name/
|-- preview/
|   `-- cover-flat.png
|-- editable/
|   |-- cover-master.svg
|   `-- cover-master.ora
|-- layers/
|   |-- 00-background.png
|   |-- 10-environment.png
|   |-- 20-subject.png
|   |-- 30-cover-event.png
|   |-- 40-light-colour.png
|   |-- 50-type-preview.png
|   `-- 60-finish.png
|-- source/
|-- manifest/
|   `-- project.json
`-- EDITING.md
```

The minimum portable master is aligned PNG layers plus `cover-master.svg` and `project.json`. `cover-master.ora` preserves named raster layers in an open exchange format. Provide a PSD only when a real Photoshop-compatible layered document can be created and opened; never rename a PNG, SVG, ZIP, or ORA file to `.psd`.

## Layer architecture

All raster layers use the exact master canvas size and origin `(0,0)` so they align when imported.

| Order | Group | Purpose | Editing expectation |
| --- | --- | --- | --- |
| 00 | Background | base colour, sky, wall, paper, or clean field | independently recolourable or replaceable |
| 10 | Environment | architecture, room, landscape, props behind the anchor | separate when it needs depth or variant control |
| 20 | Subject | person, object, vehicle, pet, or primary anchor | transparent edges, no halo, identity protected |
| 30 | Cover event | source-derived symbol, graphic interruption, collage relation, or constructed mark | the release-specific visual mechanism |
| 40 | Light and colour | motivated shadows, reflected colour, controlled atmosphere | maskable; do not bake unrelated global noise into it |
| 50 | Type | artist name, release title, supplied copy | live text in SVG plus a raster preview layer |
| 60 | Finish | one bounded material treatment when conceptually justified | optional and hideable; never used to conceal weak edges |

Merge groups only when separation would create fake or unusable pixels. Mark a merged element as `baked` in the manifest instead of claiming full editability.

## Build layers from the beginning

1. Lock ratio, pixel dimensions, safe area, and colour space.
2. Write the layer plan before generating. Every major visible element must have an owner group.
3. Create the clean background without the subject.
4. Preserve or generate the subject on transparency at the final canvas scale; inspect hair, glasses, fingers, clothing edges, and contact shadows.
5. Build the cover event as its own raster or vector layer. It must still relate correctly when the subject moves slightly.
6. Keep colour/light adjustments separate when they are likely to be tuned later.
7. Add exact type as live text or editable vector. Keep a raster preview so the intended appearance is visible even when the font is unavailable.
8. Composite a flat preview, then package the aligned layers.

If the generation tool can only return one flattened image, treat that image as a concept preview. Rebuild or extract the accepted direction into honest layers before calling it editable.

## Project manifest

Use `assets/layered-package-template/project.json` as the starting point. Record:

- project and release name;
- width, height, ratio, DPI, and colour space;
- exact artist/title copy;
- source files and provenance notes;
- layer order, role, filename, visibility, opacity, blend mode, and whether it is `editable` or `baked`;
- live text position, family, weight, size, tracking, colour, and raster preview path;
- palette tokens and any required font files or substitution notes.

The manifest is the reconstruction contract. Do not store invented credits, labels, barcodes, release dates, or font licences in it.

## Format routing

- **Photoshop requested and available:** provide a real PSD with named groups, editable type, masks, and Smart Objects where appropriate; also keep the universal PNG/SVG/manifest package.
- **Illustrator, Figma, Affinity Designer, or Inkscape:** use the SVG master with named groups, linked aligned PNGs, and live type.
- **GIMP, Krita, or another raster editor:** use the ORA master and PNG layers.
- **Editor unknown:** deliver all universal files and explain that SVG is the vector/type master while ORA is the raster-layer master.

Adobe documents that Photoshop can export named layers as individual files and preserve ICC profiles, while SVG export can preserve scalable vector/text assets. OpenRaster is designed for interoperable, non-destructive layer stacks. These formats complement rather than replace an app-native master.

## Packaging command

After preparing `project.json`, the flat preview, and aligned layer files, run:

```bash
python3 scripts/build_editable_album_package.py \
  --project /absolute/path/to/project.json \
  --output /absolute/path/to/release-name
```

The builder refuses to overwrite a non-empty destination. It validates canvas dimensions, copies source and layer files, writes the named-layer SVG and ORA masters, preserves the manifest, and adds editing notes.

## Layer QA

Before delivery:

- toggle every layer independently and confirm its role is understandable;
- confirm all raster layers match the master dimensions and origin;
- inspect transparency at 200% for white halos, clipped hair, doubled edges, and opaque boxes;
- confirm the preview matches the intended stack order;
- proof live text and its raster preview character by character;
- confirm hidden layers, masks, opacity, and blend mode are documented;
- open the SVG and ORA when compatible software is available;
- keep the original source unchanged in `source/` or record its external path when copying is not authorised;
- label the package `test` or `accepted` honestly.
