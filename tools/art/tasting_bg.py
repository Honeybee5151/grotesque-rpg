"""The Tasting hall battle backdrop (bg "tasting"): where the Ever-Sow rampages, in Plenty.

A long feast hall in one-point perspective: festival bunting and strings of sausages overhead,
tables end to end down both sides, the feast toppled, a carving board the size of a door leaning by
the wall with its cleaver in it - and at the far end the gourmet examiner's empty throne, his napkin
still tucked into its back. Yolk yellow and roast red, candle-lit. Carnival, but kept calm in the
middle where the boss stands (the throne's high back shows above her).

    python tools/art/tasting_bg.py [OUT.png] [--preview PNG]   # default art/battle/tasting.png

--preview composites the Ever-Sow on it at the battle position, 3x.
"""
import os
import sys
import numpy as np
from PIL import Image

W, H = 320, 180
VPX, VPY = 160, 56
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0

C = {k: np.array([int(v[i:i + 2], 16) for i in (1, 3, 5)] + [255], np.uint8) for k, v in {
    "dark": "#120604", "wall0": "#2a0e0a", "wall1": "#4a1a12", "wall2": "#6e2a1a", "trim": "#8e5a22",
    "far": "#1e0a08", "farlit": "#34140e",
    "floor0": "#2a160c", "floor1": "#4a2e1a", "floor2": "#6a4426", "seam": "#1c0e06",
    "cloth0": "#7e7262", "cloth1": "#b0a488", "cloth2": "#d8ccb0",
    "yolk": "#f0c840", "yolkdk": "#a8821e", "red": "#c03a2c", "reddk": "#7a1e16",
    "saus": "#8e2420", "saushi": "#c84a3a",
    "gold": "#d8b23a", "golddk": "#8a6a18", "goldhi": "#f8e080", "velvet": "#6e1a16", "velvethi": "#a8302a",
    "wax": "#e8d8b0", "flame": "#f8d060", "flame2": "#e09a30", "napkin": "#f0eeea",
    "board": "#6e4a2a", "boarddk": "#4a301a", "steel": "#9aa0a8", "steeldk": "#585e66",
    "plate": "#e4dccc", "roast": "#8e4a22",
}.items()}


def dither(img, mask, lo, hi, t):
    ys, xs = np.nonzero(mask)
    pick = t[ys, xs] > BAYER4[ys % 4, xs % 4]
    img[ys[pick], xs[pick]] = C[hi]
    img[ys[~pick], xs[~pick]] = C[lo]


def lerp(a, b, t):
    return a + (b - a) * t


def poly_mask(pts):
    from PIL import ImageDraw
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(float(x), float(y)) for x, y in pts], fill=255)
    return np.array(m) > 0


def build():
    img = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    fx0, fx1, fy0, fy1 = 116, 204, 14, VPY          # the far wall
    img[:] = C["dark"]                               # nothing left unfilled
    # the room in one-point perspective: ceiling, two side walls, floor, far wall
    ceiling = poly_mask([(0, 0), (W, 0), (fx1, fy0), (fx0, fy0)])
    lwall = poly_mask([(0, 0), (fx0, fy0), (fx0, fy1), (0, 150)])
    rwall = poly_mask([(W, 0), (fx1, fy0), (fx1, fy1), (W, 150)])
    floor = poly_mask([(0, 150), (fx0, fy1), (fx1, fy1), (W, 150)]) | (yy > 150)
    far = (xx >= fx0) & (xx <= fx1) & (yy >= fy0) & (yy <= fy1)
    dither(img, ceiling, "dark", "wall0", np.clip(yy / fy0, 0, 1) * 0.6)
    tw = np.clip(np.abs(xx - VPX) / 160.0, 0, 1)
    dither(img, lwall | rwall, "wall1", "wall2", 1 - tw * 0.9)
    dither(img, far, "far", "farlit", np.clip(1 - np.abs(xx - VPX) / 50.0, 0, 1) * 0.8)
    tf = np.clip((yy - VPY) / (124 - VPY), 0, 1)
    dither(img, floor, "floor0", "floor1", tf)
    # panels down the walls (verticals stay vertical), a wainscot rail along each
    for x in list(range(8, fx0, 14)) + list(range(fx1 + 6, W, 14)):
        for y in range(H):
            if (lwall[y, x] if x < fx0 else rwall[y, x]):
                img[y, x] = C["wall0"]
    for side in (-1, 1):
        for x in (range(0, fx0) if side < 0 else range(fx1 + 1, W)):
            t = (x / fx0) if side < 0 else ((W - x) / (W - fx1))
            y = int(lerp(98, fy1 - 14, t))
            if 0 <= y < H:
                img[y, x] = C["trim"]
    # floorboards converging on the far wall
    for k in range(-9, 10):
        for y in range(VPY + 1, 124):
            t = (y - VPY) / (124 - VPY)
            x = int(lerp(VPX + k * 4.5, VPX + k * 38, t))
            if 0 <= x < W and floor[y, x]:
                img[y, x] = C["seam"]
    # tables end to end down both walls: a narrow cloth top, its front hanging toward the aisle
    for side in (-1, 1):
        def X(x):
            return x if side < 0 else W - 1 - x
        top = poly_mask([(X(0), 96), (X(fx0 - 4), fy1 - 2), (X(fx0 + 6), fy1 + 1), (X(60), 110)])
        face = poly_mask([(X(60), 110), (X(fx0 + 6), fy1 + 1), (X(fx0 + 6), fy1 + 4), (X(60), 121)])
        img[face] = C["cloth1"]
        hem = face & ~poly_mask([(X(60), 110), (X(fx0 + 6), fy1 + 1), (X(fx0 + 6), fy1 + 3), (X(60), 119)])
        img[hem] = C["cloth0"]
        dither(img, top, "cloth1", "cloth2", np.clip(1 - np.abs(xx - VPX) / 170.0, 0, 1) * 0.9 + 0.1)
    rng = np.random.default_rng(12)
    # the feast along the tables: plates, roasts, candelabras, toppled goblets (more chaos near you)
    for side in (-1, 1):
        for t in np.linspace(0.06, 0.88, 7):
            y = int(lerp(103, fy1, t))
            x = int(lerp(30, fx0 - 2, t))
            x = x if side < 0 else W - 1 - x
            s = max(1, int(lerp(5, 1, t)))
            img[y - 1:y + 1, x - s:x + s] = C["plate"]
            if rng.uniform() < 0.55:
                img[y - s - 1:y - 1, x + s:x + s + 2] = C["roast"]
            if rng.uniform() < 0.5:
                cx = x - side * (s + 4)
                ch = int(lerp(9, 3, t))
                img[y - ch:y, cx] = C["gold"]
                img[y - ch - 1, cx - 1:cx + 2] = C["gold"]
                img[y - ch - 3:y - ch - 1, cx] = C["wax"]
                img[y - ch - 4, cx] = C["flame"]
                img[y - ch - 5, cx] = C["flame2"]
            elif rng.uniform() < 0.6:
                img[y - 1, x + s + 2:x + s + 6] = C["gold"]
                img[y, x + s + 5:x + s + 10] = C["red"]
    # the empty throne at the far end: a high red-velvet back in a gold frame, the napkin still tucked
    tx = VPX
    img[16:52, tx - 9:tx + 10] = C["golddk"]
    img[17:50, tx - 8:tx + 9] = C["gold"]
    img[19:48, tx - 6:tx + 7] = C["velvet"]
    img[20:28, tx - 5:tx + 6] = C["velvethi"]
    img[13:17, tx - 6:tx + 7] = C["gold"]
    img[11:13, tx - 3:tx + 4] = C["goldhi"]
    for x in range(tx - 4, tx + 5):
        img[17:22 + abs(x - tx) // 2, x] = C["napkin"]
    img[48:56, tx - 10:tx - 7] = C["golddk"]
    img[48:56, tx + 8:tx + 11] = C["golddk"]
    # bunting strung wall to wall, sagging, in perspective; swags of sausages near the ceiling
    for (depth, sag) in [(0.05, 9), (0.4, 6), (0.75, 3)]:
        x0, x1 = int(lerp(0, fx0, depth)), int(lerp(W - 1, fx1, depth))
        y0 = int(lerp(4, fy0, depth)) + 2
        flag = max(2, int(lerp(6, 2, depth)))
        for x in range(x0, x1):
            t = (x - x0) / max(1, (x1 - x0))
            y = int(y0 + sag * np.sin(np.pi * t))
            img[y, x] = C["yolkdk"]
            if (x - x0) % (flag * 2 + 2) == 0:
                col = C["yolk"] if ((x - x0) // (flag * 2 + 2)) % 2 == 0 else C["red"]
                for j in range(flag):
                    xa, xb = x + j // 2, x + flag - j // 2
                    if y + 1 + j < H:
                        img[y + 1 + j, xa:xb] = col
    for (x0, x1, y0, sag) in [(4, 64, 22, 10), (256, 316, 22, 10), (70, 110, 34, 6), (210, 250, 34, 6)]:
        for x in range(x0, x1):
            t = (x - x0) / max(1, (x1 - x0))
            y = int(y0 + sag * np.sin(np.pi * t))
            if (x // 3) % 2 == 0:
                img[y:y + 2, x] = C["saus"]
                img[y, x] = C["saushi"]
    # the carving board the size of a door, leaning on the right wall, its cleaver bitten in
    for y in range(64, 120):
        lean = (y - 64) * 0.2
        x0 = int(270 + lean)
        img[y, x0:x0 + 24] = C["board"]
        img[y, x0] = C["boarddk"]
        img[y, x0 + 23] = C["boarddk"]
    for y in (78, 95, 110):
        x0 = int(270 + (y - 64) * 0.2)
        img[y, x0:x0 + 24] = C["boarddk"]
    img[72:82, 276:288] = C["steel"]
    img[72:82, 276] = C["steeldk"]
    img[77:80, 288:297] = C["boarddk"]
    # a vignette
    v = ((xx - 160) / 190.0) ** 2 + ((yy - 80) / 120.0) ** 2
    corner = v > 0.82
    for y, x in zip(*np.nonzero(corner)):
        if BAYER4[y % 4, x % 4] < (v[y, x] - 0.82) * 2.2:
            img[y, x] = C["dark"]
    return img


def preview(img, path):
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    bg = Image.fromarray(img, "RGBA")
    sow = Image.open(os.path.join(root, "art", "monsters", "ever_sow", "normal.png")).convert("RGBA")
    bg.alpha_composite(sow, (160 - sow.width // 2, 122 - sow.height))
    a = np.array(bg)
    a[124:180, :, :3] = (12, 10, 26)
    a[124, :, :3] = (200, 192, 240)
    Image.fromarray(a, "RGBA").resize((W * 3, H * 3), Image.NEAREST).save(path)


if __name__ == "__main__":
    img = build()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--preview" in sys.argv:
        preview(img, sys.argv[sys.argv.index("--preview") + 1])
    else:
        out = args[0] if args else "art/battle/tasting.png"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        Image.fromarray(img, "RGBA").save(out)
        print("wrote", out)
