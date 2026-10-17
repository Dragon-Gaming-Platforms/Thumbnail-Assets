#!/usr/bin/env python3
"""ReportLab SVG adapter and install-time checks for the Python rasterizers.

Run after installing .github/requirements-image-toolchain.txt. The check renders
real SVGs, including text, and decodes the PNGs: imports alone do not prove that
ReportLab's separately packaged bitmap backend or Cairo's runtime is available.
"""

from io import BytesIO
from pathlib import Path
import tempfile


def rasterize_svglib(src, dst, width=1600):
    """Render an SVG through svglib and the explicitly installed bitmap backend."""
    from reportlab.graphics import renderPM
    from svglib.svglib import svg2rlg

    drawing = svg2rlg(str(src))
    if drawing is None:
        raise RuntimeError("svg2rlg returned None")
    scale = width / drawing.width if drawing.width else 1.0
    drawing.width *= scale
    drawing.height *= scale
    drawing.scale(scale, scale)
    # ReportLab 4 defaults to rlPyCairo, which is a different optional stack.
    # Use the rl-renderPM wheel installed by our requirements file instead.
    renderPM.drawToFile(drawing, str(dst), fmt="PNG", backend="_renderPM")


def check_python_rasterizers():
    import cairosvg
    from PIL import Image

    svg = b'''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="52">
      <rect width="160" height="52" fill="#ff0000"/>
      <text x="8" y="28" font-family="Helvetica" font-size="16" fill="white">SVG</text>
    </svg>'''
    with tempfile.TemporaryDirectory() as directory:
        src = Path(directory) / "fixture.svg"
        dst = Path(directory) / "reportlab.png"
        src.write_bytes(svg)
        # Exercise the same function and scaling used by the publisher.
        rasterize_svglib(src, dst, width=320)
        for name, source in (
            ("svglib + ReportLab + _renderPM", dst),
            ("CairoSVG", BytesIO(cairosvg.svg2png(bytestring=svg, output_width=320))),
        ):
            with Image.open(source) as image:
                image.load()
                if image.format != "PNG" or image.size != (320, 104):
                    raise RuntimeError(f"{name}: invalid PNG output {image.format} {image.size}")
                if image.convert("RGB").getpixel((310, 94)) != (255, 0, 0):
                    raise RuntimeError(f"{name}: SVG fill did not render correctly")
                # A solid rectangle is insufficient: exercise bundled font rendering.
                if not any(pixel == (255, 255, 255)
                           for pixel in image.convert("RGB").crop((10, 10, 100, 65)).getdata()):
                    raise RuntimeError(f"{name}: SVG text did not render")
            print(f"OK: {name} rendered and decoded SVG shapes/text at 320x104")


if __name__ == "__main__":
    check_python_rasterizers()
