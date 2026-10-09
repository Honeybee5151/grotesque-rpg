"""Debug view: upscale a sprite with a pixel grid and coordinate labels.
    python3 tools/art/grid.py in.png out.png [x0 y0 x1 y1] [scale]"""
import sys
from PIL import Image, ImageDraw

src = Image.open(sys.argv[1]).convert("RGBA")
x0, y0, x1, y1 = (int(v) for v in sys.argv[3:7]) if len(sys.argv) >= 7 else (0, 0, src.width, src.height)
sc = int(sys.argv[7]) if len(sys.argv) >= 8 else 8
crop = src.crop((x0, y0, x1, y1))
bg = Image.new("RGBA", crop.size, (48, 40, 60, 255))
bg.alpha_composite(crop)
big = bg.resize((crop.width * sc, crop.height * sc), Image.NEAREST)
pad = 22
out = Image.new("RGBA", (big.width + pad, big.height + pad), (16, 12, 20, 255))
out.paste(big, (pad, pad))
d = ImageDraw.Draw(out)
for i in range(crop.width + 1):
    X = pad + i * sc
    col = (255, 255, 255, 90) if (x0 + i) % 4 == 0 else (255, 255, 255, 28)
    d.line([(X, pad), (X, out.height)], fill=col)
    if (x0 + i) % 4 == 0 and i < crop.width:
        d.text((X + 1, 2), str(x0 + i), fill=(255, 220, 120, 255))
for j in range(crop.height + 1):
    Y = pad + j * sc
    col = (255, 255, 255, 90) if (y0 + j) % 4 == 0 else (255, 255, 255, 28)
    d.line([(pad, Y), (out.width, Y)], fill=col)
    if (y0 + j) % 4 == 0 and j < crop.height:
        d.text((1, Y + 1), str(y0 + j), fill=(255, 220, 120, 255))
out.save(sys.argv[2])
