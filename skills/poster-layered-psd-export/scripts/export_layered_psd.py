#!/usr/bin/env python3
"""Export aligned RGBA poster layers to a Photoshop-readable PSD."""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Iterable

from PIL import Image


PSD_SIGNATURE = b"8BPS"
PSD_VERSION = 1
PSD_CHANNELS = (0, 1, 2, -1)  # R, G, B, transparency
MAX_DIMENSION = 30000

BLEND_KEYS = {
    "normal": b"norm",
    "passthrough": b"pass",
    "multiply": b"mul ",
    "screen": b"scrn",
    "overlay": b"over",
    "darken": b"dark",
    "lighten": b"lite",
    "color-dodge": b"div ",
    "color-burn": b"idiv",
    "hard-light": b"hLit",
    "soft-light": b"sLit",
    "difference": b"diff",
    "exclusion": b"smud",
    "subtract": b"fsub",
}


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def u16(value: int) -> bytes:
    return struct.pack(">H", value)


def i16(value: int) -> bytes:
    return struct.pack(">h", value)


def u32(value: int) -> bytes:
    return struct.pack(">I", value)


def i32(value: int) -> bytes:
    return struct.pack(">i", value)


def pad4(data: bytes) -> bytes:
    return data + b"\0" * ((-len(data)) % 4)


def safe_name(value: object, fallback: str) -> str:
    name = str(value or fallback).strip()
    if not name:
        fail("layer name cannot be empty")
    return name


def resolve_file(project_root: Path, value: object, label: str) -> Path:
    path = Path(str(value or "")).expanduser()
    if not path.is_absolute():
        path = project_root / path
    path = path.resolve()
    if not path.is_file():
        fail(f"{label} not found: {path}")
    return path


def packbits_row(row: bytes) -> bytes:
    """Encode one row using PSD's PackBits variant."""

    result = bytearray()
    literal = bytearray()

    def flush_literal() -> None:
        while literal:
            count = min(len(literal), 128)
            result.append(count - 1)
            result.extend(literal[:count])
            del literal[:count]

    index = 0
    while index < len(row):
        run = 1
        while (
            index + run < len(row)
            and row[index + run] == row[index]
            and run < 128
        ):
            run += 1

        if run >= 3:
            flush_literal()
            # A repeat packet stores 257 - run as an unsigned byte.
            result.append(257 - run)
            result.append(row[index])
            index += run
            continue

        literal.append(row[index])
        index += 1
        if len(literal) == 128:
            flush_literal()

    flush_literal()
    return bytes(result)


def channel_rle(channel: bytes, width: int, height: int) -> bytes:
    rows = [channel[row * width : (row + 1) * width] for row in range(height)]
    encoded_rows = [packbits_row(row) for row in rows]
    if any(len(row) > 65535 for row in encoded_rows):
        fail("a compressed channel row is too large for PSD RLE")
    return b"".join(u16(len(row)) for row in encoded_rows) + b"".join(encoded_rows)


def channel_payload(channel: bytes, width: int, height: int) -> bytes:
    encoded = channel_rle(channel, width, height)
    return u16(1) + encoded


def split_channels(image: Image.Image) -> list[bytes]:
    rgba = image.convert("RGBA")
    channels = rgba.split()
    return [bytes(channel.tobytes()) for channel in channels]


def pascal_name(name: str) -> bytes:
    # Photoshop keeps a legacy Pascal name and a Unicode `luni` name.
    legacy = name.encode("ascii", errors="replace")[:255]
    return pad4(bytes([len(legacy)]) + legacy)


def resource_pascal_name(name: str = "") -> bytes:
    raw = bytes([len(name.encode("ascii", errors="replace")[:255])]) + name.encode(
        "ascii", errors="replace"
    )[:255]
    return raw + b"\0" * ((-len(raw)) % 2)


def unicode_name_block(name: str) -> bytes:
    encoded = name.encode("utf-16-be")
    payload = u32(len(encoded) // 2) + encoded
    return b"8BIM" + b"luni" + u32(len(payload)) + pad4(payload)


def layer_record(
    name: str,
    blend: str,
    opacity: int,
    visible: bool,
    channel_lengths: Iterable[int],
    width: int,
    height: int,
) -> bytes:
    if blend not in BLEND_KEYS:
        fail(f"unsupported blend mode {blend!r}; use one of {sorted(BLEND_KEYS)}")

    record = bytearray()
    record.extend(i32(0))
    record.extend(i32(0))
    record.extend(i32(height))
    record.extend(i32(width))
    lengths = list(channel_lengths)
    if len(lengths) != len(PSD_CHANNELS):
        fail("each layer must have RGBA channel data")
    record.extend(u16(len(PSD_CHANNELS)))
    for channel_id, length in zip(PSD_CHANNELS, lengths):
        record.extend(i16(channel_id))
        record.extend(u32(length))

    record.extend(b"8BIM")
    record.extend(BLEND_KEYS[blend])
    record.extend(bytes([opacity, 0, 0x02 if visible else 0, 0]))

    extra = bytearray()
    extra.extend(u32(0))  # layer mask data
    extra.extend(u32(0))  # layer blending ranges
    extra.extend(pascal_name(name))
    extra.extend(unicode_name_block(name))
    record.extend(u32(len(extra)))
    record.extend(extra)
    return bytes(record)


def image_resources(dpi: int) -> bytes:
    """Write Photoshop's resolution-info resource (ID 1005)."""

    fixed_dpi = max(1, min(dpi, 65535)) * 65536
    resolution_payload = (
        u32(fixed_dpi)
        + u16(1)
        + u16(1)
        + u32(fixed_dpi)
        + u16(1)
        + u16(1)
    )
    resource = b"8BIM" + u16(1005) + resource_pascal_name() + u32(len(resolution_payload)) + resolution_payload
    return u32(len(resource)) + resource


def color_mode_data() -> bytes:
    return u32(0)


def composite_payload(preview: Image.Image, width: int, height: int) -> bytes:
    channels = split_channels(preview)
    encoded_rows = [
        [
            packbits_row(channel[row * width : (row + 1) * width])
            for row in range(height)
        ]
        for channel in channels
    ]
    return (
        u16(1)
        + b"".join(u16(len(row)) for rows in encoded_rows for row in rows)
        + b"".join(row for rows in encoded_rows for row in rows)
    )


def write_psd(
    output: Path,
    width: int,
    height: int,
    dpi: int,
    layers: list[dict],
    preview: Image.Image,
) -> None:
    if not 1 <= width <= MAX_DIMENSION or not 1 <= height <= MAX_DIMENSION:
        fail(f"canvas must be between 1 and {MAX_DIMENSION}px on each side")
    if not layers:
        fail("project must contain at least one layer")
    if len(layers) > 32767:
        fail("PSD supports at most 32767 layers in this exporter")

    # PSD layer records are stored top-to-bottom. The project contract is
    # bottom-to-top so that a manifest reads naturally to a designer.
    ordered = list(reversed(layers))
    record_bytes = bytearray()
    pixel_bytes = bytearray()

    for layer in ordered:
        image = layer["image"]
        channels = split_channels(image)
        payloads = [channel_payload(channel, width, height) for channel in channels]
        record_bytes.extend(
            layer_record(
                layer["psd_name"],
                layer["blend"],
                layer["opacity"],
                layer["visible"],
                [len(payload) for payload in payloads],
                width,
                height,
            )
        )
        for payload in payloads:
            pixel_bytes.extend(payload)

    layer_info = i16(len(ordered)) + record_bytes + pixel_bytes
    layer_mask_info = u32(len(layer_info)) + layer_info + u32(0)

    preview_rgba = preview.convert("RGBA")
    composite = composite_payload(preview_rgba, width, height)

    header = (
        PSD_SIGNATURE
        + u16(PSD_VERSION)
        + b"\0" * 6
        + u16(4)
        + u32(height)
        + u32(width)
        + u16(8)
        + u16(3)
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        fail(f"refusing to overwrite existing file: {output}")
    manifest_path = output.with_suffix(".manifest.json")
    if manifest_path.exists():
        fail(f"refusing to overwrite existing file: {manifest_path}")

    output.write_bytes(
        header
        + color_mode_data()
        + image_resources(dpi)
        + u32(len(layer_mask_info))
        + layer_mask_info
        + composite
    )

    manifest = {
        "schema_version": "poster-layered-psd-export/v1",
        "canvas": {"width": width, "height": height, "dpi": dpi, "color_space": "RGB/8"},
        "preview": "embedded composite preview",
        "layer_order": "bottom-to-top in this manifest; Photoshop displays top-to-bottom",
        "layers": [
            {
                "id": layer["id"],
                "name": layer["name"],
                "psd_name": layer["psd_name"],
                "kind": layer["kind"],
                "file": layer["relative_file"],
                "opacity": layer["opacity"] / 255,
                "blend": layer["blend"],
                "visible": layer["visible"],
                "editability": "raster-pixel-layer",
                "notes": layer.get("notes", ""),
            }
            for layer in layers
        ],
        "text_note": "Text layers are raster pixel layers unless the host separately creates native Photoshop text layers.",
        "psd": output.name,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_project(project_file: Path) -> tuple[int, int, int, list[dict], Image.Image]:
    try:
        project = json.loads(project_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot read project JSON: {error}")
    if not isinstance(project, dict):
        fail("project JSON must be an object")

    root = project_file.parent.resolve()
    canvas = project.get("canvas") or {}
    try:
        width = int(canvas["width"])
        height = int(canvas["height"])
        dpi = int(canvas.get("dpi", 300))
    except (KeyError, TypeError, ValueError):
        fail("canvas.width, canvas.height, and canvas.dpi must be integers")
    if width <= 0 or height <= 0 or dpi <= 0:
        fail("canvas dimensions and dpi must be positive")

    preview_path = resolve_file(root, project.get("preview"), "preview")
    try:
        preview = Image.open(preview_path).convert("RGBA")
    except OSError as error:
        fail(f"cannot open preview: {error}")
    if preview.size != (width, height):
        fail(f"preview is {preview.size[0]}x{preview.size[1]}; expected {width}x{height}")

    raw_layers = project.get("layers")
    if not isinstance(raw_layers, list) or not raw_layers:
        fail("project.layers must be a non-empty array")

    layers: list[dict] = []
    for index, raw in enumerate(raw_layers):
        if not isinstance(raw, dict):
            fail(f"layer {index} must be an object")
        layer_id = str(raw.get("id") or f"layer-{index + 1}").strip()
        if not layer_id:
            fail(f"layer {index} has an empty id")
        name = safe_name(raw.get("name"), layer_id)
        source = resolve_file(root, raw.get("file"), f"layer {name}")
        try:
            image = Image.open(source).convert("RGBA")
        except OSError as error:
            fail(f"cannot open layer {name!r}: {error}")
        if image.size != (width, height):
            fail(f"layer {name!r} is {image.size[0]}x{image.size[1]}; expected {width}x{height}")

        try:
            opacity = float(raw.get("opacity", 1.0))
        except (TypeError, ValueError):
            fail(f"invalid opacity for layer {name!r}")
        if not 0.0 <= opacity <= 1.0:
            fail(f"opacity for layer {name!r} must be between 0 and 1")
        blend = str(raw.get("blend", "normal"))
        if blend not in BLEND_KEYS:
            fail(f"unsupported blend mode {blend!r} for layer {name!r}")
        kind = str(raw.get("kind", "raster"))
        psd_name = name
        if kind == "text" and not bool(raw.get("native_text", False)):
            psd_name = f"{name} [raster text]"

        layers.append(
            {
                "id": layer_id,
                "name": name,
                "psd_name": psd_name,
                "kind": kind,
                "file": str(source),
                "relative_file": (
                    str(source.relative_to(root))
                    if source.is_relative_to(root)
                    else source.name
                ),
                "image": image,
                "opacity": round(opacity * 255),
                "blend": blend,
                "visible": bool(raw.get("visible", True)),
                "notes": str(raw.get("notes", "")),
            }
        )
    return width, height, dpi, layers, preview


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path, help="Layer manifest JSON (layers are bottom-to-top)")
    parser.add_argument("--output", required=True, type=Path, help="New PSD path; existing files are never overwritten")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    output = args.output.expanduser().resolve()
    width, height, dpi, layers, preview = load_project(project)
    write_psd(output, width, height, dpi, layers, preview)
    print(
        json.dumps(
            {
                "psd": str(output),
                "manifest": str(output.with_suffix(".manifest.json")),
                "canvas": f"{width}x{height}",
                "dpi": dpi,
                "layers": len(layers),
                "layer_order": "bottom-to-top in project.json",
                "text_layers": "raster unless native Photoshop text was created separately",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
