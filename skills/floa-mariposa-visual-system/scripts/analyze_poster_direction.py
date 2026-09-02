#!/usr/bin/env python3
"""Extract lightweight palette and composition signals for poster art direction."""

from __future__ import annotations

import argparse
import colorsys
import json
import math
import statistics
from pathlib import Path

from PIL import Image, ImageStat


def hex_color(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def luminance(rgb: tuple[int, int, int]) -> float:
    red, green, blue = rgb
    return (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255


def hsv(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    red, green, blue = (value / 255 for value in rgb)
    return colorsys.rgb_to_hsv(red, green, blue)


def crop_activity(crop: Image.Image) -> dict[str, float]:
    small = crop.convert("L").resize((32, 32), Image.Resampling.BILINEAR)
    if hasattr(small, "get_flattened_data"):
        values = list(small.get_flattened_data())
    else:
        values = list(small.getdata())
    spread = statistics.pstdev(values) / 255
    horizontal = [abs(values[index] - values[index - 1]) for index in range(1, len(values))]
    return {
        "tone_mean": round(statistics.fmean(values) / 255, 4),
        "tone_spread": round(spread, 4),
        "edge_activity": round(statistics.fmean(horizontal) / 255, 4),
        "visual_activity": round((spread * 0.65) + (statistics.fmean(horizontal) / 255 * 0.35), 4),
    }


def grid_activity(image: Image.Image, columns: int, rows: int) -> list[dict]:
    width, height = image.size
    cells = []
    for row in range(rows):
        for column in range(columns):
            left = math.floor(width * column / columns)
            top = math.floor(height * row / rows)
            right = math.floor(width * (column + 1) / columns)
            bottom = math.floor(height * (row + 1) / rows)
            metrics = crop_activity(image.crop((left, top, right, bottom)))
            metrics.update(
                {
                    "column": column,
                    "row": row,
                    "region": f"{column + 1},{row + 1}",
                }
            )
            cells.append(metrics)
    return cells


def direction_label(palette: list[dict], average_luminance: float, contrast: float) -> str:
    if not palette:
        return "threshold"
    max_saturation = max(item["saturation"] for item in palette)
    if average_luminance < 0.34 and max_saturation > 0.42:
        return "signal"
    if average_luminance > 0.67 and contrast > 0.45:
        return "threshold"
    if contrast > 0.62 and palette[0]["saturation"] < 0.22:
        return "archive"
    return "orbit"


def analyze(path: Path, color_count: int, grid_columns: int, grid_rows: int) -> dict:
    try:
        image = Image.open(path).convert("RGB")
    except OSError as error:
        raise SystemExit(f"error: cannot open image {path}: {error}") from error

    preview = image.copy()
    preview.thumbnail((320, 480), Image.Resampling.LANCZOS)
    quantized = preview.quantize(
        colors=max(3, min(color_count, 12)),
        method=Image.Quantize.MEDIANCUT,
    )
    color_counts = quantized.getcolors(maxcolors=quantized.width * quantized.height) or []
    color_counts.sort(reverse=True)
    palette_data = quantized.getpalette() or []
    palette = []
    for count, index in color_counts[:color_count]:
        rgb = tuple(palette_data[index * 3 : index * 3 + 3])
        hue, saturation, value = hsv(rgb)
        palette.append(
            {
                "hex": hex_color(rgb),
                "share": round(count / (quantized.width * quantized.height), 4),
                "luminance": round(luminance(rgb), 4),
                "hue": round(hue, 4),
                "saturation": round(saturation, 4),
                "value": round(value, 4),
            }
        )

    stats = ImageStat.Stat(preview)
    average_rgb = tuple(round(value) for value in stats.mean[:3])
    luminances = [item["luminance"] for item in palette]
    contrast = (max(luminances) - min(luminances)) if luminances else 0
    cells = grid_activity(preview, grid_columns, grid_rows)
    quiet = sorted(cells, key=lambda cell: cell["visual_activity"])[:2]
    active = sorted(cells, key=lambda cell: cell["visual_activity"], reverse=True)[:2]

    return {
        "input": path.name,
        "dimensions": {"width": image.width, "height": image.height},
        "ratio": round(image.width / image.height, 4),
        "orientation": "portrait" if image.height > image.width else "landscape" if image.width > image.height else "square",
        "average_rgb": hex_color(average_rgb),
        "palette": palette,
        "contrast_span": round(contrast, 4),
        "grid": {"columns": grid_columns, "rows": grid_rows, "cells": cells},
        "quiet_zone_candidates": [cell["region"] for cell in quiet],
        "visual_anchor_candidates": [cell["region"] for cell in active],
        "suggested_direction": direction_label(
            palette,
            luminance(average_rgb),
            contrast,
        ),
        "use_note": "Heuristic signals only; confirm the subject, typography, source text, and visual metaphor with visual inspection.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--colors", type=int, default=6)
    parser.add_argument("--grid-columns", type=int, default=3)
    parser.add_argument("--grid-rows", type=int, default=3)
    args = parser.parse_args()
    if args.grid_columns < 1 or args.grid_rows < 1:
        raise SystemExit("error: grid dimensions must be positive")
    print(
        json.dumps(
            analyze(args.input.expanduser().resolve(), args.colors, args.grid_columns, args.grid_rows),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
