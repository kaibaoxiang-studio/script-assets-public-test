#!/usr/bin/env python3
"""Render scene-adapted, equal-width color swatches with Chinese labels."""
import argparse
import json
import re
from pathlib import Path


def font_path(explicit):
    if explicit:
        candidate = Path(explicit)
        if not candidate.is_file():
            raise ValueError("Specified font file is unavailable")
        return str(candidate)
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "C:/Windows/Fonts/msyh.ttc",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate
    raise ValueError("No Chinese font found; provide --font with a CJK font")


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("Palette must be a JSON object")
    colors = data.get("colors")
    if not isinstance(colors, list) or not colors:
        raise ValueError("colors must be a nonempty list")
    if len(colors) > 24:
        raise ValueError("Canvas safety limit exceeded; use at most 24 swatches")
    for item in colors:
        if not isinstance(item, dict):
            raise ValueError("Each swatch must be an object")
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", str(item.get("hex", ""))):
            raise ValueError("Each swatch needs a six-digit HEX color")
        name, use = item.get("name"), item.get("use")
        if not isinstance(name, str) or not name.strip() or "\n" in name:
            raise ValueError("Each swatch needs a single-line name")
        if not isinstance(use, list) or not 1 <= len(use) <= 2:
            raise ValueError("use must contain one or two short lines")
        if any(not isinstance(line, str) or not line.strip() or "\n" in line for line in use):
            raise ValueError("Use descriptions must be nonempty single-line strings")
        if any("%" in line or "％" in line for line in [name, *use]):
            raise ValueError("Do not put percentage ratios on the palette")
    return colors


def fit_font(draw, value, path, size, width):
    from PIL import ImageFont
    while size >= 16:
        font = ImageFont.truetype(path, size=size)
        if draw.textlength(value, font=font) <= width:
            return font
        size -= 1
    raise ValueError("Label too long; shorten it rather than clipping text")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--font")
    args = parser.parse_args()
    try:
        from PIL import Image, ImageDraw
        colors = validate(json.loads(args.input.read_text(encoding="utf-8")))
        path = font_path(args.font)
        if args.output.suffix.lower() != ".png":
            raise ValueError("Output must be a .png file")
        if args.output.exists():
            raise ValueError("Output exists; choose a new filename")
        block_w, block_h, gap, margin, top = 240, 440, 28, 36, 104
        width = margin * 2 + len(colors) * block_w + (len(colors) - 1) * gap
        image = Image.new("RGB", (width, 760), "white")
        draw = ImageDraw.Draw(image)
        for index, item in enumerate(colors):
            x = margin + index * (block_w + gap)
            draw.rectangle((x, top, x + block_w - 1, top + block_h - 1), fill=item["hex"])
            font = fit_font(draw, item["name"], path, 30, block_w)
            draw.text((x + block_w / 2, 588), item["name"], font=font, fill="#111111", anchor="mm")
            for row, line in enumerate(item["use"]):
                font = fit_font(draw, line, path, 22, block_w)
                draw.text((x + block_w / 2, 634 + row * 34), line, font=font, fill="#333333", anchor="mm")
        # Exclusive creation prevents overwriting an existing artifact, including races.
        with args.output.open("xb") as output:
            image.save(output, format="PNG")
        print(json.dumps({"output": str(args.output.resolve()), "colors": len(colors), "size": image.size}, ensure_ascii=False))
    except (ValueError, OSError, ImportError) as error:
        parser.exit(2, f"Palette rendering failed: {error}\n")


if __name__ == "__main__":
    main()
