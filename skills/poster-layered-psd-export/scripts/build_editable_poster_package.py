#!/usr/bin/env python3
"""Build a portable poster-editing package containing PSD and aligned layers."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from export_layered_psd import load_project, write_psd


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-.")
    return slug or "layer"


def build_package(project_file: Path, output: Path) -> dict:
    if output.exists():
        fail(f"refusing to overwrite existing package directory: {output}")

    width, height, dpi, layers, preview = load_project(project_file)
    output.mkdir(parents=True)
    preview_dir = output / "preview"
    layers_dir = output / "layers"
    editable_dir = output / "editable"
    preview_dir.mkdir()
    layers_dir.mkdir()
    editable_dir.mkdir()

    preview_target = preview_dir / "final.png"
    preview_source = project_file.parent / "preview.png"
    raw_project = json.loads(project_file.read_text(encoding="utf-8"))
    raw_preview = raw_project.get("preview")
    if raw_preview:
        preview_source = Path(str(raw_preview)).expanduser()
        if not preview_source.is_absolute():
            preview_source = project_file.parent / preview_source
    preview_source = preview_source.resolve()
    if not preview_source.is_file():
        fail(f"preview not found: {preview_source}")
    shutil.copy2(preview_source, preview_target)

    normalized_layers: list[dict] = []
    for index, layer in enumerate(layers):
        source = Path(layer["file"])
        target = layers_dir / f"{index:02d}-{safe_slug(layer['id'])}.png"
        shutil.copy2(source, target)
        normalized_layers.append(
            {
                "id": layer["id"],
                "name": layer["name"],
                "kind": layer["kind"],
                "file": str(target.relative_to(output)),
                "opacity": layer["opacity"] / 255,
                "blend": layer["blend"],
                "visible": layer["visible"],
                "native_text": False,
                "notes": layer.get("notes", ""),
            }
        )

    packaged_project = {
        "canvas": {"width": width, "height": height, "dpi": dpi},
        "preview": str(preview_target.relative_to(output)),
        "layers": normalized_layers,
    }
    project_target = output / "project.json"
    project_target.write_text(
        json.dumps(packaged_project, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    psd_target = editable_dir / "poster.psd"
    packaged_width, packaged_height, packaged_dpi, packaged_layers, packaged_preview = load_project(project_target)
    write_psd(
        psd_target,
        packaged_width,
        packaged_height,
        packaged_dpi,
        packaged_layers,
        packaged_preview,
    )

    notes = f"""# Poster editing package

- Canvas: {width} x {height}px at {dpi} DPI, RGB/8.
- `editable/poster.psd`: Photoshop-readable PSD with named aligned pixel layers.
- `editable/poster.manifest.json`: layer order, opacity, blend mode, and editability metadata.
- `preview/final.png`: merged preview used to verify the PSD composite.
- `layers/`: full-canvas aligned PNG assets, listed bottom-to-top in `project.json`.
- `project.json`: portable input manifest for rebuilding the package.
- Text layers are raster unless a host separately creates native Photoshop text layers.
- The package is a `test` artifact until it is opened and checked in Photoshop.
"""
    (output / "EDITING.md").write_text(notes, encoding="utf-8")

    return {
        "package": str(output.resolve()),
        "psd": str(psd_target.resolve()),
        "manifest": str(psd_target.with_suffix(".manifest.json").resolve()),
        "project": str(project_target.resolve()),
        "preview": str(preview_target.resolve()),
        "layers": len(normalized_layers),
        "canvas": f"{width}x{height}",
        "dpi": dpi,
        "text_layers": "raster unless native Photoshop text was created separately",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path, help="Source project.json")
    parser.add_argument("--output", required=True, type=Path, help="New package directory; existing directories are rejected")
    args = parser.parse_args()
    result = build_package(args.project.expanduser().resolve(), args.output.expanduser().resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
