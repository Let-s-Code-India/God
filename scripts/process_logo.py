#!/usr/bin/env python3
"""Rasterize the project logo and export the required sizes for docs and packaging."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import cairosvg
except ImportError:  # pragma: no cover - installation path
    cairosvg = None

ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = ROOT / "assets" / "logo.svg"
DOCS_ASSET_DIR = ROOT / "docs" / "assets"
STATIC_ASSET_DIR = ROOT / "src" / "god_ai" / "static"


def ensure_svg_valid(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing logo SVG: {path}")
    text = path.read_text(encoding="utf-8")
    if "<svg" not in text.lower() or "</svg>" not in text.lower():
        raise ValueError(f"Invalid SVG structure in {path}")


def convert_svg_to_png(svg_path: Path, png_path: Path, size: tuple[int, int]) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    if cairosvg is not None:
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=size[0], output_height=size[1])
        return
    raise RuntimeError("CairoSVG is required to rasterize the logo. Install it with: python -m pip install cairosvg")


def main() -> int:
    ensure_svg_valid(SVG_PATH)
    target_sizes = {
        "logo_255x255.png": (255, 255),
        "favicon_64x64.png": (64, 64),
        "badge_32x32.png": (32, 32),
    }
    for directory in (DOCS_ASSET_DIR, STATIC_ASSET_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    for filename, size in target_sizes.items():
        convert_svg_to_png(SVG_PATH, DOCS_ASSET_DIR / filename, size)
        convert_svg_to_png(SVG_PATH, STATIC_ASSET_DIR / filename, size)
    print(f"Generated logo assets for {SVG_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
