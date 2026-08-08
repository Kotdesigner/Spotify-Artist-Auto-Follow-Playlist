#!/usr/bin/env python3
"""Generate original cross-platform app icons without external assets."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SIZE = 1024


def generate_icon():
    ASSETS.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gradient = Image.new("RGBA", (SIZE, SIZE))
    pixels = gradient.load()

    start = (91, 68, 220)
    end = (30, 190, 186)
    for y in range(SIZE):
        for x in range(SIZE):
            ratio = (x + y) / (2 * (SIZE - 1))
            color = tuple(
                round(start[channel] * (1 - ratio) + end[channel] * ratio)
                for channel in range(3)
            )
            pixels[x, y] = (*color, 255)

    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (32, 32, SIZE - 32, SIZE - 32),
        radius=220,
        fill=255,
    )
    image.paste(gradient, (0, 0), mask)
    draw = ImageDraw.Draw(image)

    shadow = (18, 20, 34, 70)
    white = (255, 255, 255, 245)
    soft = (255, 255, 255, 210)

    draw.ellipse((286, 250, 546, 510), fill=shadow)
    draw.ellipse((478, 330, 678, 530), fill=shadow)
    draw.ellipse((198, 368, 398, 568), fill=shadow)
    draw.rounded_rectangle((225, 530, 626, 790), radius=190, fill=shadow)
    draw.rounded_rectangle((472, 560, 756, 754), radius=130, fill=shadow)

    draw.ellipse((270, 230, 530, 490), fill=white)
    draw.ellipse((466, 312, 666, 512), fill=soft)
    draw.ellipse((186, 350, 386, 550), fill=soft)
    draw.rounded_rectangle((210, 510, 610, 770), radius=190, fill=white)
    draw.rounded_rectangle((460, 542, 744, 736), radius=130, fill=soft)

    plus_center = (756, 286)
    draw.ellipse((650, 180, 862, 392), fill=(20, 23, 32, 210))
    draw.rounded_rectangle(
        (plus_center[0] - 22, 220, plus_center[0] + 22, 352),
        radius=20,
        fill=white,
    )
    draw.rounded_rectangle(
        (690, plus_center[1] - 22, 822, plus_center[1] + 22),
        radius=20,
        fill=white,
    )

    png_path = ASSETS / "app.png"
    ico_path = ASSETS / "app.ico"
    icns_path = ASSETS / "app.icns"
    image.save(png_path)
    image.save(
        ico_path,
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    image.save(
        icns_path,
        sizes=[(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)],
    )
    print(f"Generated {png_path}, {ico_path}, and {icns_path}")


if __name__ == "__main__":
    generate_icon()
