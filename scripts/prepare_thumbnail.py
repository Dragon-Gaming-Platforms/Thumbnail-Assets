#!/usr/bin/env python3
"""Prepare one flat source JPEG (requires Pillow; never writes CI derivatives)."""
import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--crop", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"))
    parser.add_argument("--brightness", type=float, default=1.0)
    args = parser.parse_args()
    if args.output.suffix != ".jpg" or args.output.name != args.output.name.lower():
        parser.error("Output must be a lowercase <catalog-id>.jpg")
    if args.output.parent.resolve().name == "jpg":
        parser.error("Do not write into the CI-generated jpg/ directory")
    if args.output.exists():
        parser.error("Output already exists; inspect it rather than overwrite another agent's work")
    with Image.open(args.input) as original:
        image = ImageOps.exif_transpose(original).convert("RGBA")
        if args.crop:
            left, top, right, bottom = args.crop
            if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
                parser.error("Crop must be a nonempty box within the image")
            image = image.crop(args.crop)
        background = Image.new("RGB", image.size, "#09090f")
        background.paste(image, mask=image.getchannel("A"))
        image = ImageOps.fit(background, (800, 260), method=Image.Resampling.LANCZOS)
        if args.brightness <= 0:
            parser.error("Brightness must be positive")
        if args.brightness != 1:
            image = ImageEnhance.Brightness(image).enhance(args.brightness)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        for quality in range(90, 34, -5):
            image.save(args.output, "JPEG", quality=quality, optimize=True, progressive=True)
            if args.output.stat().st_size <= 40 * 1024:
                break
        else:
            args.output.unlink()
            parser.error("Cannot fit 800x260 within 40 KiB; simplify the source")
    with Image.open(args.output) as checked:
        checked.verify()
    print(f"{args.output}: 800x260, {args.output.stat().st_size} bytes, quality={quality}")


if __name__ == "__main__":
    main()
