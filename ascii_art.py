import re
import sys
import argparse
from PIL import Image

# denser = brighter. tweaked this by eye until it looked good on dark terminals
CHARS = " .,:;i1tfLCG08@#"

def load(path, w):
    try:
        img = Image.open(path)
    except FileNotFoundError:
        print(f"cant find {path}", file=sys.stderr)
        sys.exit(1)

    ow, oh = img.size
    # terminal chars are roughly 2x taller than wide, so we squish height
    h = int(oh * w / ow * 0.45)
    return img.resize((w, h))

def to_ascii(img, grayscale):
    rgb = img.convert("RGB")
    px = rgb.load()
    w, h = rgb.size
    lines = []

    for y in range(h):
        row = []
        for x in range(w):
            r, g, b = px[x, y]
            # weights from ITU-R BT.601, green contributes most because eyes are most sensitive to it
            luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
            ch = CHARS[int(luma / 255 * (len(CHARS) - 1))]

            if grayscale:
                row.append(ch)
            else:
                row.append(f"\x1b[38;2;{r};{g};{b}m{ch}")
        lines.append("".join(row))

    if not grayscale:
        lines = [l + "\x1b[0m" for l in lines]
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser(description="image to ascii art")
    p.add_argument("image", help="path to image file")
    p.add_argument("--width", type=int, default=100, help="output width in chars (default 100)")
    p.add_argument("--grayscale", action="store_true", help="no color, just chars")
    p.add_argument("--out", help="save output to a text file instead of printing")
    # TODO: add --invert flag for light terminal backgrounds
    args = p.parse_args()

    img = load(args.image, args.width)
    art = to_ascii(img, args.grayscale)

    if args.out:
        clean = re.sub(r"\x1b\[[0-9;]*m", "", art)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(clean)
        print(f"saved to {args.out}")
    else:
        print(art)

if __name__ == "__main__":
    main()
