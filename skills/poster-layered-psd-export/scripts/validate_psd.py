#!/usr/bin/env python3
"""Validate the structural sections of a Photoshop PSD exported by this Skill."""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


class Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.offset = 0

    def take(self, size: int) -> bytes:
        if size < 0 or self.offset + size > len(self.data):
            fail(f"unexpected end of file at offset {self.offset}")
        value = self.data[self.offset : self.offset + size]
        self.offset += size
        return value

    def u16(self) -> int:
        return struct.unpack(">H", self.take(2))[0]

    def i16(self) -> int:
        return struct.unpack(">h", self.take(2))[0]

    def u32(self) -> int:
        return struct.unpack(">I", self.take(4))[0]

    def i32(self) -> int:
        return struct.unpack(">i", self.take(4))[0]


def parse_unicode_name(extra: bytes) -> str | None:
    reader = Reader(extra)
    if len(extra) < 8:
        return None
    # Skip layer mask data, blending ranges, and the padded Pascal name.
    reader.u32()
    reader.u32()
    pascal_start = reader.offset
    length = reader.take(1)[0]
    reader.take(length)
    reader.offset = pascal_start + ((1 + length + 3) // 4) * 4

    while reader.offset + 12 <= len(extra):
        signature = reader.take(4)
        key = reader.take(4)
        length = reader.u32()
        payload = reader.take(length)
        reader.offset += (-length) % 4
        if signature in {b"8BIM", b"8B64"} and key == b"luni" and len(payload) >= 4:
            units = struct.unpack(">I", payload[:4])[0]
            raw = payload[4 : 4 + units * 2]
            try:
                return raw.decode("utf-16-be")
            except UnicodeDecodeError:
                return None
    return None


def parse_resolution(resources: bytes) -> int | None:
    reader = Reader(resources)
    while reader.offset + 12 <= len(resources):
        signature = reader.take(4)
        resource_id = reader.u16()
        name_length = reader.take(1)[0]
        reader.take(name_length)
        reader.offset += (-(1 + name_length)) % 2
        length = reader.u32()
        payload = reader.take(length)
        reader.offset += (-length) % 2
        if signature in {b"8BIM", b"MeSa"} and resource_id == 1005 and len(payload) >= 4:
            return round(struct.unpack(">I", payload[:4])[0] / 65536)
    return None


def parse(path: Path) -> dict:
    reader = Reader(path.read_bytes())
    if reader.take(4) != b"8BPS":
        fail("missing 8BPS signature")
    version = reader.u16()
    if version != 1:
        fail(f"unsupported PSD version: {version}")
    reader.take(6)
    channels = reader.u16()
    height = reader.u32()
    width = reader.u32()
    depth = reader.u16()
    color_mode = reader.u16()
    if channels != 4 or depth != 8 or color_mode != 3:
        fail(f"expected RGB/8 RGBA document, got channels={channels}, depth={depth}, mode={color_mode}")

    color_mode_length = reader.u32()
    reader.take(color_mode_length)
    resources_length = reader.u32()
    resources = reader.take(resources_length)
    dpi = parse_resolution(resources)
    layer_mask_length = reader.u32()
    layer_mask_start = reader.offset
    layer_mask_end = layer_mask_start + layer_mask_length
    layer_info_length = reader.u32()
    layer_info_start = reader.offset
    layer_info_end = layer_info_start + layer_info_length
    layer_count = reader.i16()
    if layer_count <= 0:
        fail("PSD has no positive layer count")

    layers = []
    channel_data_bytes = 0
    for _ in range(layer_count):
        bounds = [reader.i32(), reader.i32(), reader.i32(), reader.i32()]
        channel_count = reader.u16()
        channels_info = []
        for _ in range(channel_count):
            channel_id = reader.i16()
            length = reader.u32()
            channels_info.append({"id": channel_id, "length": length})
            channel_data_bytes += length
        if reader.take(4) != b"8BIM":
            fail("layer blend signature is not 8BIM")
        blend = reader.take(4).decode("latin1")
        opacity = reader.take(1)[0]
        reader.take(1)  # clipping
        flags = reader.take(1)[0]
        reader.take(1)  # filler
        extra_length = reader.u32()
        extra = reader.take(extra_length)
        legacy_length = extra[8] if len(extra) > 8 else 0
        legacy_start = 9
        legacy_name = extra[legacy_start : legacy_start + legacy_length].decode("ascii", errors="replace")
        unicode_name = parse_unicode_name(extra)
        layers.append(
            {
                "legacy_name": legacy_name,
                "name": unicode_name or legacy_name,
                "bounds": bounds,
                "blend": blend,
                "opacity": round(opacity / 255, 6),
                "visible": bool(flags & 0x02),
                "channels": channels_info,
            }
        )

    pixel_start = reader.offset
    reader.take(channel_data_bytes)
    if reader.offset != layer_info_end:
        fail(f"layer pixel data ended at {reader.offset}, expected {layer_info_end}")
    if reader.u32() != 0:
        fail("global layer mask data is not empty")
    if reader.offset != layer_mask_end:
        fail(f"layer/mask section ended at {reader.offset}, expected {layer_mask_end}")

    composite_compression = reader.u16()
    if composite_compression == 0:
        reader.take(channels * width * height)
    elif composite_compression == 1:
        row_lengths = [reader.u16() for _ in range(channels * height)]
        reader.take(sum(row_lengths))
    else:
        fail(f"unsupported composite compression: {composite_compression}")
    if reader.offset != len(reader.data):
        fail(f"trailing bytes after composite image: {len(reader.data) - reader.offset}")

    return {
        "file": str(path),
        "bytes": len(reader.data),
        "canvas": {"width": width, "height": height, "depth": depth, "channels": channels},
        "dpi": dpi,
        "layers": layers,
        "layer_pixel_data_offset": pixel_start,
        "composite_compression": composite_compression,
        "valid": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("psd", type=Path)
    args = parser.parse_args()
    print(json.dumps(parse(args.psd.expanduser().resolve()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
