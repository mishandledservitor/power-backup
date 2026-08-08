"""Generates AppIcon.icns for the Rsync Sync GUI app.

Draws a simple flat icon: a rounded-square gradient background (macOS app
icons are conventionally pre-rounded with ~10% padding, matching Apple's
squircle template) with a soft drop shadow and a clean two-arrow sync glyph
centered on top. Everything is drawn at 4x and downsampled with LANCZOS for
antialiasing, since PIL's ImageDraw does not antialias on its own. Rendered
at multiple resolutions and packed into an .icns via macOS's iconutil.
Not part of the app itself - a one-off asset generator.
"""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

BG_TOP_LEFT = (100, 164, 249)
BG_BOTTOM_RIGHT = (28, 92, 182)
ARROW_COLOR = (255, 255, 255)

SIZES = [16, 32, 64, 128, 256, 512, 1024]
SUPERSAMPLE = 4

PADDING_RATIO = 0.10
CORNER_RATIO = 0.225
SHADOW_BLUR_RATIO = 0.02
SHADOW_OFFSET_RATIO = 0.012
SHADOW_ALPHA = 90


def _gradient_square(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    denom = max(size - 1, 1)
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * denom)
            r = int(BG_TOP_LEFT[0] + (BG_BOTTOM_RIGHT[0] - BG_TOP_LEFT[0]) * t)
            g = int(BG_TOP_LEFT[1] + (BG_BOTTOM_RIGHT[1] - BG_TOP_LEFT[1]) * t)
            b = int(BG_TOP_LEFT[2] + (BG_BOTTOM_RIGHT[2] - BG_TOP_LEFT[2]) * t)
            px[x, y] = (r, g, b, 255)
    return img


def _draw_sync_glyph(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float, width: float, color) -> None:
    gap_deg = 24

    def arrowed_arc(start_deg: float, end_deg: float) -> None:
        bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
        draw.arc(bbox, start=start_deg, end=end_deg, fill=color, width=int(width))
        end_rad = math.radians(end_deg)
        tip_x = cx + radius * math.cos(end_rad)
        tip_y = cy + radius * math.sin(end_rad)
        tangent = end_rad + math.pi / 2
        head_len = width * 1.15
        head_w = width * 0.85
        p1 = (tip_x + head_w * math.cos(end_rad), tip_y + head_w * math.sin(end_rad))
        p2 = (
            tip_x - head_len * math.cos(end_rad) + head_w * math.cos(tangent),
            tip_y - head_len * math.sin(end_rad) + head_w * math.sin(tangent),
        )
        p3 = (
            tip_x - head_len * math.cos(end_rad) - head_w * math.cos(tangent),
            tip_y - head_len * math.sin(end_rad) - head_w * math.sin(tangent),
        )
        draw.polygon([p1, p2, p3], fill=color)

    arrowed_arc(180 + gap_deg, 360 - gap_deg)
    arrowed_arc(gap_deg, 180 - gap_deg)


def _render_at(size: int) -> Image.Image:
    """Render the icon at `size` px, drawn internally at SUPERSAMPLE x for antialiasing."""
    big = size * SUPERSAMPLE
    canvas = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    pad = int(big * PADDING_RATIO)
    content_size = big - 2 * pad
    corner_radius = int(content_size * CORNER_RATIO)

    # Soft drop shadow, offset slightly down, blurred.
    shadow = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    offset = int(big * SHADOW_OFFSET_RATIO)
    shadow_draw.rounded_rectangle(
        [pad, pad + offset, pad + content_size, pad + offset + content_size],
        radius=corner_radius,
        fill=(0, 0, 0, SHADOW_ALPHA),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(big * SHADOW_BLUR_RATIO))
    canvas = Image.alpha_composite(canvas, shadow)

    bg = _gradient_square(content_size)
    mask = Image.new("L", (content_size, content_size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, content_size - 1, content_size - 1], radius=corner_radius, fill=255
    )
    canvas.paste(bg, (pad, pad), mask)

    draw = ImageDraw.Draw(canvas)
    radius = content_size * 0.20
    width = max(2, content_size * 0.075)
    _draw_sync_glyph(draw, big / 2, big / 2, radius, width, ARROW_COLOR)

    return canvas.resize((size, size), Image.LANCZOS)


def main() -> int:
    out_dir = Path(__file__).parent
    iconset = out_dir / "AppIcon.iconset"
    iconset.mkdir(exist_ok=True)

    for size in SIZES:
        _render_at(size).save(iconset / f"icon_{size}x{size}.png")
        if size <= 512:
            _render_at(size * 2).save(iconset / f"icon_{size}x{size}@2x.png")

    icns_path = out_dir / "AppIcon.icns"
    subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(icns_path)], check=True)
    print(f"Wrote {icns_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
