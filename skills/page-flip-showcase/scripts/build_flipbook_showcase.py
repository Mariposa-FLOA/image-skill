#!/usr/bin/env python3
"""Build a static page-flip showcase from supplied images.

The script is intentionally deterministic and source-preserving. It creates a
portrait editorial scene with a small page sequence, an open spread, and one
perspective-warped turning page. It does not redraw or ask a model to rewrite
the image contents.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps


CANVAS = (1600, 2200)
PAPER = (244, 241, 235, 255)
PAGE = (252, 250, 246, 255)
INK = (33, 30, 27, 255)


def solve_linear(matrix: list[list[float]], values: list[float]) -> list[float]:
    """Solve a small dense linear system with Gaussian elimination."""

    n = len(values)
    augmented = [row[:] + [value] for row, value in zip(matrix, values)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-10:
            raise ValueError("Perspective points are degenerate")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        pivot_value = augmented[col][col]
        augmented[col] = [item / pivot_value for item in augmented[col]]
        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            if abs(factor) < 1e-12:
                continue
            augmented[row] = [
                current - factor * pivot_item
                for current, pivot_item in zip(augmented[row], augmented[col])
            ]
    return [augmented[row][-1] for row in range(n)]


def perspective_coefficients(
    source_points: Sequence[tuple[float, float]],
    target_points: Sequence[tuple[float, float]],
) -> tuple[float, ...]:
    """Return Pillow coefficients mapping target output points to source points."""

    matrix: list[list[float]] = []
    values: list[float] = []
    for (target_x, target_y), (source_x, source_y) in zip(
        target_points, source_points
    ):
        matrix.append(
            [
                target_x,
                target_y,
                1.0,
                0.0,
                0.0,
                0.0,
                -source_x * target_x,
                -source_x * target_y,
            ]
        )
        values.append(source_x)
        matrix.append(
            [
                0.0,
                0.0,
                0.0,
                target_x,
                target_y,
                1.0,
                -source_y * target_x,
                -source_y * target_y,
            ]
        )
        values.append(source_y)
    return tuple(solve_linear(matrix, values))


def fit_source(source: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Fit an image inside a page area without stretching it."""

    source = source.convert("RGB")
    fitted = ImageOps.contain(source, size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, PAGE)
    left = (size[0] - fitted.width) // 2
    top = (size[1] - fitted.height) // 2
    canvas.paste(fitted.convert("RGBA"), (left, top))
    return canvas


def make_page(
    source: Image.Image,
    size: tuple[int, int],
    padding: int,
    edge_colour: tuple[int, int, int, int] = PAGE,
) -> Image.Image:
    """Create a clean paper page with the source image contained inside."""

    page = Image.new("RGBA", size, edge_colour)
    draw = ImageDraw.Draw(page)
    draw.rectangle((0, 0, size[0] - 1, size[1] - 1), outline=(215, 209, 199, 255), width=2)
    content = fit_source(source, (size[0] - 2 * padding, size[1] - 2 * padding))
    left = (size[0] - content.width) // 2
    top = (size[1] - content.height) // 2
    page.alpha_composite(content, (left, top))
    return page


def composite_rotated(
    canvas: Image.Image,
    page: Image.Image,
    center: tuple[int, int],
    angle: float,
    shadow_blur: int = 22,
    shadow_offset: tuple[int, int] = (22, 28),
) -> None:
    """Paste one rotated page with a soft contact shadow."""

    rotated = page.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    alpha = rotated.getchannel("A")
    shadow_alpha = alpha.filter(ImageFilter.GaussianBlur(shadow_blur))
    shadow = Image.new("RGBA", rotated.size, (40, 34, 29, 92))
    shadow.putalpha(shadow_alpha.point(lambda value: int(value * 0.68)))

    left = int(center[0] - rotated.width / 2)
    top = int(center[1] - rotated.height / 2)
    canvas.alpha_composite(shadow, (left + shadow_offset[0], top + shadow_offset[1]))
    canvas.alpha_composite(rotated, (left, top))


def quad_shift(
    points: Iterable[tuple[int, int]], offset: tuple[int, int]
) -> list[tuple[int, int]]:
    return [(x + offset[0], y + offset[1]) for x, y in points]


def composite_turning_page(
    canvas: Image.Image,
    page: Image.Image,
    target_quad: Sequence[tuple[int, int]],
) -> None:
    """Warp a page into one raised sheet and add thickness/shadow at its hinge."""

    source_quad = [
        (0.0, 0.0),
        (float(page.width), 0.0),
        (float(page.width), float(page.height)),
        (0.0, float(page.height)),
    ]
    target_float = [(float(x), float(y)) for x, y in target_quad]
    # Pillow's perspective transform asks for source coordinates for each
    # output pixel, so solve the inverse mapping: target canvas quad -> page
    # local rectangle. The helper's first argument is the source side of each
    # correspondence, despite the target-first wording in its internals.
    coefficients = perspective_coefficients(source_quad, target_float)

    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_draw.polygon(quad_shift(target_quad, (22, 34)), fill=(35, 28, 23, 118))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(26))
    canvas.alpha_composite(shadow_layer)

    thickness_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    thickness_draw = ImageDraw.Draw(thickness_layer)
    for step in range(18, 0, -3):
        shifted = quad_shift(target_quad, (int(step * 0.20), int(step * 0.65)))
        thickness_draw.line(
            shifted + [shifted[0]],
            fill=(142, 129, 112, max(22, 88 - step * 3)),
            width=3,
            joint="curve",
        )
    canvas.alpha_composite(thickness_layer)

    warped = page.transform(
        canvas.size,
        Image.Transform.PERSPECTIVE,
        coefficients,
        resample=Image.Resampling.BICUBIC,
    )
    polygon_mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(polygon_mask).polygon(target_quad, fill=255)
    warped_alpha = ImageChops.multiply(warped.getchannel("A"), polygon_mask)
    warped.putalpha(warped_alpha)
    canvas.alpha_composite(warped)

    # A narrow inner line makes the hinge readable without adding fake graphics.
    foreground = ImageDraw.Draw(canvas)
    foreground.line(
        [target_quad[0], target_quad[3]],
        fill=(90, 77, 63, 150),
        width=5,
    )
    foreground.line(
        [target_quad[0], target_quad[1]],
        fill=(255, 255, 255, 115),
        width=3,
    )


def load_sources(paths: Sequence[str]) -> list[Image.Image]:
    loaded: list[Image.Image] = []
    for raw_path in paths:
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Input image not found: {path}")
        loaded.append(Image.open(path).convert("RGB"))
    return loaded


def build_showcase(sources: Sequence[Image.Image]) -> Image.Image:
    if not 1 <= len(sources) <= 8:
        raise ValueError("Provide between 1 and 8 images for this preview")

    canvas = Image.new("RGBA", CANVAS, PAPER)
    draw = ImageDraw.Draw(canvas)

    # A quiet ground shadow anchors the book without inventing a prop-heavy set.
    ground_shadow = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(ground_shadow)
    shadow_draw.ellipse((130, 1120, 1510, 2130), fill=(60, 54, 47, 62))
    ground_shadow = ground_shadow.filter(ImageFilter.GaussianBlur(44))
    canvas.alpha_composite(ground_shadow)

    # The earlier pages form a visible sequence behind the open spread.
    mini_specs = [
        ((250, 475), -8),
        ((520, 390), -4),
        ((790, 350), 0),
        ((1060, 390), 4),
        ((1330, 475), 8),
    ]
    mini_size = (300, 455)
    for source_index, (center, angle) in zip(range(1, min(6, len(sources))), mini_specs):
        mini = make_page(sources[source_index], mini_size, padding=18)
        composite_rotated(canvas, mini, center, angle, shadow_blur=15, shadow_offset=(10, 15))

    # The open spread is deliberately larger so at least two source pages read.
    if len(sources) >= 2:
        left_index = min(6, len(sources) - 1)
        right_index = min(7, len(sources) - 1)
        left_page = make_page(sources[left_index], (560, 840), padding=26)
        right_page = make_page(sources[right_index], (560, 840), padding=26)
        composite_rotated(canvas, left_page, (555, 1555), -5.5, shadow_blur=26)
        composite_rotated(canvas, right_page, (1055, 1515), 5.5, shadow_blur=26)

        # Subtle gutter: it explains that the two cards belong to one spread.
        draw = ImageDraw.Draw(canvas)
        draw.line((804, 1135, 804, 1965), fill=(100, 91, 81, 100), width=5)
        draw.line((815, 1140, 815, 1958), fill=(255, 255, 255, 105), width=3)

    # The first uploaded image is the active sheet, lifted from the gutter.
    turning = make_page(sources[0], (530, 825), padding=24)
    # Clockwise order: top-left, top-right, bottom-right, bottom-left. Keeping
    # this order aligned with source_quad prevents the lifted sheet from
    # appearing upside down.
    target_quad = [(840, 435), (1325, 330), (1175, 1000), (785, 1140)]
    composite_turning_page(canvas, turning, target_quad)

    # Keep a minimal edge frame so the page action has a clean visual boundary.
    frame = ImageDraw.Draw(canvas)
    frame.rectangle((42, 42, CANVAS[0] - 43, CANVAS[1] - 43), outline=(218, 212, 203, 255), width=2)
    frame.line((110, 2100, 1490, 2100), fill=(215, 207, 196, 170), width=2)
    return canvas.convert("RGB")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", help="Source images in intended reading order")
    parser.add_argument("--output", required=True, help="Output PNG/JPG path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = load_sources(args.images)
    result = build_showcase(sources)
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    print(f"Wrote {output} ({result.width}x{result.height})")


if __name__ == "__main__":
    main()
