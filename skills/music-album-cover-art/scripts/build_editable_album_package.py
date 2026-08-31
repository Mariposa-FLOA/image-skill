#!/usr/bin/env python3
"""Build a portable editable album-cover package from aligned layers."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import struct
import sys
import zipfile
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.sax.saxutils import escape, quoteattr


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ORA_MIMETYPE = "image/openraster"
BLEND_TO_ORA = {
    "normal": "svg:src-over",
    "multiply": "svg:multiply",
    "screen": "svg:screen",
    "overlay": "svg:overlay",
    "darken": "svg:darken",
    "lighten": "svg:lighten",
    "color-dodge": "svg:color-dodge",
    "color-burn": "svg:color-burn",
    "hard-light": "svg:hard-light",
    "soft-light": "svg:soft-light",
    "difference": "svg:difference",
    "hue": "svg:hue",
    "saturation": "svg:saturation",
    "color": "svg:color",
    "luminosity": "svg:luminosity",
}


def die(message: str) -> None:
    raise SystemExit(f"error: {message}")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-.")
    if not slug:
        die(f"invalid empty identifier derived from {value!r}")
    return slug


def resolve_file(root: Path, value: str, label: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not path.is_file():
        die(f"{label} not found: {path}")
    return path


def png_info(path: Path) -> tuple[int, int, int]:
    with path.open("rb") as handle:
        header = handle.read(33)
    if len(header) < 33 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        die(f"expected PNG file: {path}")
    width, height, _bit_depth, color_type, _compression, _filter, _interlace = struct.unpack(
        ">IIBBBBB", header[16:29]
    )
    return width, height, color_type


def copy_asset(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def validate_opacity(value: object, layer_name: str) -> float:
    try:
        opacity = float(value)
    except (TypeError, ValueError):
        die(f"invalid opacity for layer {layer_name!r}")
    if not 0.0 <= opacity <= 1.0:
        die(f"opacity must be between 0 and 1 for layer {layer_name!r}")
    return opacity


def build_svg(width: int, height: int, layers: list[dict], output: Path) -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
            f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        ),
    ]

    for layer in layers:
        label = quoteattr(layer["name"])
        layer_id = quoteattr(layer["id"])
        visibility = "inline" if layer["visible"] else "none"
        style = quoteattr(
            f"display:{visibility};opacity:{layer['opacity']};mix-blend-mode:{layer['blend']}"
        )
        lines.append(
            f'  <g id={layer_id} inkscape:groupmode="layer" inkscape:label={label} style={style}>'
        )

        if layer["kind"] in {"raster", "vector"}:
            href = quoteattr(f"../layers/{layer['package_file']}")
            lines.append(
                f'    <image href={href} xlink:href={href} x="0" y="0" width="{width}" height="{height}"/>'
            )
        elif layer["kind"] == "text":
            text = escape(str(layer["text"]))
            x = float(layer.get("x", 0))
            y = float(layer.get("y", 0))
            family = quoteattr(str(layer.get("font_family", "Arial")))
            weight = quoteattr(str(layer.get("font_weight", "400")))
            size = float(layer.get("font_size", 64))
            spacing = float(layer.get("letter_spacing", 0))
            fill = quoteattr(str(layer.get("fill", "#000000")))
            anchor = quoteattr(str(layer.get("text_anchor", "start")))
            transform = layer.get("transform")
            transform_attr = f" transform={quoteattr(str(transform))}" if transform else ""
            lines.append(
                f'    <text x="{x:g}" y="{y:g}" font-family={family} font-weight={weight} '
                f'font-size="{size:g}" letter-spacing="{spacing:g}" fill={fill} '
                f'text-anchor={anchor}{transform_attr}>{text}</text>'
            )
        lines.append("  </g>")

    lines.append("</svg>")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_ora(
    width: int,
    height: int,
    dpi: int,
    layers: list[dict],
    preview: Path,
    output: Path,
) -> None:
    root = Element(
        "image",
        {
            "version": "0.0.6",
            "w": str(width),
            "h": str(height),
            "xres": str(dpi),
            "yres": str(dpi),
            "xmlns:svg": "http://www.w3.org/2000/svg",
        },
    )
    stack = SubElement(root, "stack")
    ora_layers: list[tuple[dict, str, Path]] = []

    for index, layer in enumerate(reversed(layers)):
        raster_path = layer.get("ora_source")
        if not raster_path:
            continue
        archive_path = f"data/{index:03d}-{safe_slug(layer['id'])}.png"
        ora_layers.append((layer, archive_path, Path(raster_path)))
        SubElement(
            stack,
            "layer",
            {
                "name": layer["name"],
                "src": archive_path,
                "x": "0",
                "y": "0",
                "opacity": f"{layer['opacity']:.6f}",
                "visibility": "visible" if layer["visible"] else "hidden",
                "composite-op": BLEND_TO_ORA.get(layer["blend"], "svg:src-over"),
            },
        )

    xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, encoding="utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("mimetype", ORA_MIMETYPE, compress_type=zipfile.ZIP_STORED)
        archive.writestr("stack.xml", xml_bytes, compress_type=zipfile.ZIP_DEFLATED)
        archive.write(preview, "mergedimage.png", compress_type=zipfile.ZIP_DEFLATED)
        archive.write(preview, "Thumbnails/thumbnail.png", compress_type=zipfile.ZIP_DEFLATED)
        for _layer, archive_path, source in ora_layers:
            archive.write(source, archive_path, compress_type=zipfile.ZIP_DEFLATED)


def build_package(project_file: Path, output: Path) -> dict:
    project_root = project_file.parent.resolve()
    try:
        project = json.loads(project_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        die(f"cannot read project JSON: {error}")

    canvas = project.get("canvas") or {}
    try:
        width = int(canvas["width"])
        height = int(canvas["height"])
        dpi = int(canvas.get("dpi", 300))
    except (KeyError, TypeError, ValueError):
        die("canvas.width, canvas.height, and canvas.dpi must be integers")
    if width <= 0 or height <= 0 or dpi <= 0:
        die("canvas dimensions and DPI must be positive")

    if output.exists() and not output.is_dir():
        die(f"destination exists and is not a directory: {output}")
    if output.exists() and any(output.iterdir()):
        die(f"destination is not empty; refusing to overwrite: {output}")
    output.mkdir(parents=True, exist_ok=True)

    preview_source = resolve_file(project_root, str(project.get("preview", "")), "preview")
    preview_width, preview_height, _ = png_info(preview_source)
    if (preview_width, preview_height) != (width, height):
        die(
            f"preview is {preview_width}x{preview_height}; expected {width}x{height}"
        )
    preview_target = output / "preview" / "cover-flat.png"
    copy_asset(preview_source, preview_target)

    normalized_layers: list[dict] = []
    for index, raw in enumerate(project.get("layers") or []):
        if not isinstance(raw, dict):
            die(f"layer {index} must be an object")
        layer_id = safe_slug(str(raw.get("id", f"layer-{index}")))
        name = str(raw.get("name", layer_id))
        kind = str(raw.get("kind", "raster"))
        if kind not in {"raster", "vector", "text"}:
            die(f"unsupported kind {kind!r} for layer {name!r}")
        opacity = validate_opacity(raw.get("opacity", 1.0), name)
        blend = str(raw.get("blend", "normal"))
        visible = bool(raw.get("visible", True))
        layer = dict(raw)
        layer.update(
            {
                "id": layer_id,
                "name": name,
                "kind": kind,
                "opacity": opacity,
                "blend": blend,
                "visible": visible,
            }
        )

        if kind in {"raster", "vector"}:
            source = resolve_file(project_root, str(raw.get("file", "")), f"layer {name}")
            suffix = source.suffix.lower()
            if kind == "raster" and suffix != ".png":
                die(f"raster layer must be PNG: {source}")
            if kind == "vector" and suffix != ".svg":
                die(f"vector layer must be SVG: {source}")
            if kind == "raster":
                layer_width, layer_height, color_type = png_info(source)
                if (layer_width, layer_height) != (width, height):
                    die(
                        f"layer {name!r} is {layer_width}x{layer_height}; expected {width}x{height}"
                    )
                if raw.get("require_alpha") and color_type not in {4, 6}:
                    die(f"layer {name!r} requires PNG alpha transparency")
                layer["ora_source"] = str(source)
            package_name = f"{index:02d}-{layer_id}{suffix}"
            copy_asset(source, output / "layers" / package_name)
            layer["package_file"] = package_name
            layer["source_file"] = str(source)
            layer["file"] = f"layers/{package_name}"
        else:
            if not str(raw.get("text", "")):
                die(f"text layer {name!r} has no text")
            raster_value = raw.get("raster_file")
            if raster_value:
                raster_source = resolve_file(
                    project_root, str(raster_value), f"raster preview for {name}"
                )
                layer_width, layer_height, _ = png_info(raster_source)
                if (layer_width, layer_height) != (width, height):
                    die(
                        f"text preview {name!r} is {layer_width}x{layer_height}; expected {width}x{height}"
                    )
                package_name = f"{index:02d}-{layer_id}-preview.png"
                copy_asset(raster_source, output / "layers" / package_name)
                layer["raster_package_file"] = package_name
                layer["source_raster_file"] = str(raster_source)
                layer["raster_file"] = f"layers/{package_name}"
                layer["ora_source"] = str(raster_source)

        normalized_layers.append(layer)

    if not normalized_layers:
        die("project must define at least one layer")

    copied_sources = []
    for index, source_entry in enumerate(project.get("sources") or []):
        if not isinstance(source_entry, dict):
            die(f"source {index} must be an object")
        source = resolve_file(project_root, str(source_entry.get("file", "")), f"source {index}")
        target_name = safe_slug(str(source_entry.get("name") or source.name))
        copy_asset(source, output / "source" / target_name)
        copied_sources.append({"name": target_name, "original": str(source)})

    build_svg(width, height, normalized_layers, output / "editable" / "cover-master.svg")
    build_ora(
        width,
        height,
        dpi,
        normalized_layers,
        preview_target,
        output / "editable" / "cover-master.ora",
    )

    normalized_project = dict(project)
    normalized_project["preview"] = "preview/cover-flat.png"
    normalized_project["layers"] = [
        {key: value for key, value in layer.items() if key != "ora_source"}
        for layer in normalized_layers
    ]
    normalized_project["packaged_sources"] = copied_sources
    manifest_path = output / "manifest" / "project.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(normalized_project, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    notes = f"""# Editing this album-cover package

- Canvas: {width} x {height}px at {dpi} DPI; colour space: {canvas.get('color_space', 'sRGB')}.
- `preview/cover-flat.png` is the approved visual reference for the layer stack.
- `editable/cover-master.svg` contains named groups and live text where supplied.
- `editable/cover-master.ora` contains named raster layers for compatible editors.
- `layers/` contains full-canvas aligned assets; import them without trimming.
- `manifest/project.json` records copy, layer order, opacity, blend mode, and editability.
- A missing native PSD is intentional unless a real Photoshop-layered file was created and verified.
"""
    (output / "EDITING.md").write_text(notes, encoding="utf-8")

    return {
        "output": str(output.resolve()),
        "canvas": f"{width}x{height}",
        "layers": len(normalized_layers),
        "sources": len(copied_sources),
        "svg": str((output / "editable" / "cover-master.svg").resolve()),
        "ora": str((output / "editable" / "cover-master.ora").resolve()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path, help="Path to project.json")
    parser.add_argument("--output", required=True, type=Path, help="New or empty output directory")
    args = parser.parse_args()
    result = build_package(args.project.expanduser().resolve(), args.output.expanduser().resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
