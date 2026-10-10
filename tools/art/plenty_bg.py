"""Plenty's streets battle backdrop (bg "plenty"): for street Gorgers and the Second Chin at the gate.

A festival street at dusk in one-point perspective: timber-framed shopfronts with lit windows, shop
signs shaped like cuts of meat hanging on their brackets (a ham, sausages, a T-bone, a pig's head),
bunting across the street, cobbles, a gutter running with gravy down the middle, paper crowns
trodden into the mud - and the town gate at the far end, behind where the monster stands. Carnival:
roast red, yolk yellow, warm. Calm in the middle.

    python tools/art/plenty_bg.py [OUT.png] [--preview PNG]   # default art/battle/plenty.png

--preview composites the Second Chin on it at the battle position, 3x.
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw

W, H = 320, 180
VPX, VPY = 160, 66
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0

C = {k: np.array([int(v[i:i + 2], 16) for i in (1, 3, 5)] + [255], np.uint8) for k, v in {
    "sky0": "#3e1e3a", "sky1": "#6e2e48", "sky2": "#b04a50", "sky3": "#e07a58", "sky4": "#f4a868",
    "beam": "#2e1a10", "plas0": "#4e3828", "plas1": "#6e5038", "plas2": "#8e6c4c", "roof": "#7a2018", "roofhi": "#a8342a",
    "win": "#d8a04a", "windk": "#8e5e22", "door": "#3a1e12",
    "cob0": "#3a2a22", "cob1": "#5a4234", "cob2": "#7a5a46", "mud": "#2e2018",
    "gravy": "#6e3e18", "gravyhi": "#c08a40",
    "yolk": "#f0c840", "yolkdk": "#a8821e", "red": "#c03a2c",
    "ham": "#d06a72", "hamdk": "#8e3a44", "bone": "#ece0c8", "saus": "#8e2420", "steak": "#a83a30",
    "iron": "#1e1410", "gate": "#4a2a1a", "gatedk": "#1c0e08", "dark": "#140a08",
}.items()}


def dither(img, mask, lo, hi, t):
    ys, xs = np.nonzero(mask)
    pick = t[ys, xs] > BAYER4[ys % 4, xs % 4]
    img[ys[pick], xs[pick]] = C[hi]
    img[ys[~pick], xs[~pick]] = C[lo]


def poly(pts):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(float(x), float(y)) for x, y in pts], fill=255)
    return np.array(m) > 0


def lerp(a, b, t):
    return a + (b - a) * t


def build():
    img = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    img[:] = C["dark"]
    # dusk sky over the street: deep at the top, a festival-orange glow low behind the gate
    sky = yy < VPY + 4
    t = np.clip(yy / (VPY + 4), 0, 1)
    for lo, hi, a, b in [("sky0", "sky1", 0.0, 0.35), ("sky1", "sky2", 0.35, 0.65), ("sky2", "sky3", 0.65, 0.88),
                         ("sky3", "sky4", 0.88, 1.01)]:
        band = sky & (t >= a) & (t < b)
        dither(img, band, lo, hi, (t - a) / (b - a))
    # the street: cobbles from the gate toward you, mud at the edges, a gravy gutter down the middle
    street = poly([(0, 180), (VPX - 14, VPY), (VPX + 14, VPY), (W, 180)])
    ts = np.clip((yy - VPY) / (124 - VPY), 0, 1)
    dither(img, street, "cob0", "cob1", ts * 0.9)
    for k in range(1, 12):                                   # cobble courses, closer together far off
        y = int(VPY + (124 - VPY) * (k / 11.0) ** 1.8)
        for x in range(W):
            if street[y, x] and (x + k * 3) % 7 != 0:
                img[y, x] = C["cob0"]
    for k in range(-8, 9):                                   # cobble joints converging
        for y in range(VPY + 2, 124):
            tt = (y - VPY) / (124 - VPY)
            x = int(lerp(VPX + k * 1.6, VPX + k * 22, tt))
            if 0 <= x < W and street[y, x] and (y * 3 + k) % 4 != 0:
                img[y, x] = C["cob0"]
    gutter = poly([(VPX - 1, VPY + 1), (VPX + 1, VPY + 1), (VPX + 7, 180), (VPX - 7, 180)])
    img[gutter] = C["gravy"]
    for y in range(VPY + 4, 124, 3):                          # glints on the running gravy
        tt = (y - VPY) / (124 - VPY)
        x = int(VPX - 1 + tt * 3 * ((y // 3) % 2 * 2 - 1))
        img[y, x] = C["gravyhi"]
    # shopfronts down both sides: timber frames over plaster, lit windows, red-tiled eaves
    for side in (-1, 1):
        def X(x):
            return x if side < 0 else W - 1 - x
        face = poly([(X(0), 0), (X(VPX - 16), VPY - 30), (X(VPX - 16), VPY + 2), (X(0), 180)])
        dither(img, face, "plas0", "plas1", np.clip(1 - np.abs(xx - VPX) / 170.0, 0, 1) * 0.8)
        roof = poly([(X(0), 0), (X(VPX - 16), VPY - 30), (X(VPX - 16), VPY - 33), (X(0), -14)])
        img[roof & (yy >= 0)] = C["roof"]
        # shops: vertical posts at perspective-spaced positions, each with a window and a door
        posts = [0, 52, 86, 106, 118, 126, 132, 140]
        for i in range(len(posts) - 1):
            x0, x1 = posts[i], posts[i + 1]
            if x1 > VPX - 16:
                break
            for x in (x0, x0 + 1):
                xs = X(x)
                col = [y for y in range(H) if face[y, xs]]
                if col:
                    img[min(col):max(col), xs] = C["beam"]
            # a lit window high in each shop, a door at street level
            tc = (x0 + x1) / 2.0 / (VPX - 16)
            wy0, wy1 = int(lerp(30, VPY - 21, tc)), int(lerp(48, VPY - 14, tc))
            wx0, wx1 = int(lerp(x0 + 12, x0 + 3, tc)), int(lerp(x1 - 14, x1 - 3, tc))
            if wx1 - wx0 >= 2:
                win = poly([(X(wx0), wy0), (X(wx1), wy0 + (wy1 - wy0) * 0.08 * (1 if side < 0 else 1)), (X(wx1), wy1), (X(wx0), wy1)])
                img[win] = C["win"]
                cx = X(int((wx0 + wx1) / 2))
                img[wy0:wy1, cx] = C["windk"]
            dy0, dy1 = int(lerp(84, VPY - 4, tc)), int(lerp(120, VPY + 2, tc))
            dx0, dx1 = int(lerp(x0 + 14, x0 + 3, tc)), int(lerp(x1 - 12, x1 - 3, tc))
            if dx1 - dx0 >= 2 and dy1 > dy0:
                img[poly([(X(dx0), dy0), (X(dx1), dy0), (X(dx1), dy1), (X(dx0), dy1)])] = C["door"]
        # a horizontal beam along the shopfronts
        for x in range(0, VPX - 16):
            tt = x / (VPX - 16)
            img[int(lerp(70, VPY - 8, tt)), X(x)] = C["beam"]
    # the town gate at the far end, behind where the monster stands
    gx0, gx1, gy0 = VPX - 16, VPX + 16, VPY - 28
    img[gy0:VPY + 2, gx0:gx1] = C["gate"]
    img[gy0 + 8:VPY + 2, VPX - 9:VPX + 10] = C["gatedk"]            # the open arch
    img[gy0 - 4:gy0, gx0 + 6:gx1 - 6] = C["gate"]
    img[gy0 - 7:gy0 - 4, VPX - 4:VPX + 5] = C["ham"]                # a carved pig's head over it
    img[gy0 - 6, VPX - 2] = C["iron"]
    img[gy0 - 6, VPX + 2] = C["iron"]
    # shop signs shaped like cuts of meat, hanging on iron brackets over the street
    signs = [(-1, 20, 40, "ham"), (-1, 96, 52, "saus"), (1, 30, 44, "steak"), (1, 100, 54, "pig")]
    for side, xd, y, kind in signs:
        tt = xd / (VPX - 16)
        s = max(2, int(lerp(9, 3, tt)))
        bx = xd if side < 0 else W - 1 - xd
        arm = int(lerp(16, 5, tt)) * (-side)
        img[y, min(bx, bx + arm):max(bx, bx + arm) + 1] = C["iron"]
        sx = bx + arm
        img[y + 1:y + 3, sx] = C["iron"]
        cy = y + 3 + s
        if kind == "ham":
            m = ((xx - sx) / (s * 1.2)) ** 2 + ((yy - cy) / s) ** 2 < 1
            img[m] = C["ham"]
            img[m & (yy > cy + s * 0.3)] = C["hamdk"]
            img[cy - 1:cy + 1, sx + int(s * 1.1):sx + int(s * 1.1) + max(2, s // 2)] = C["bone"]
        elif kind == "saus":
            for j in range(3):
                m = ((xx - sx) / (s * 0.45)) ** 2 + ((yy - (y + 4 + j * s * 0.9)) / (s * 0.5)) ** 2 < 1
                img[m] = C["saus"]
        elif kind == "steak":
            m = ((xx - sx) / (s * 1.1)) ** 2 + ((yy - cy) / (s * 0.8)) ** 2 < 1
            img[m] = C["steak"]
            img[cy - s // 2:cy + s // 2 + 1, sx] = C["bone"]
            img[cy, sx - s // 2:sx + s // 2 + 1] = C["bone"]
        else:
            m = ((xx - sx) / s) ** 2 + ((yy - cy) / (s * 0.9)) ** 2 < 1
            img[m] = C["ham"]
            img[cy, sx - s // 3] = C["iron"]
            img[cy, sx + s // 3] = C["iron"]
            img[cy + s // 2: cy + s // 2 + 2, sx - 1:sx + 2] = C["hamdk"]
    # bunting strung across the street
    for (depth, sag) in [(0.0, 10), (0.45, 6), (0.75, 3)]:
        x0, x1 = int(lerp(0, VPX - 16, depth)), int(lerp(W - 1, VPX + 16, depth))
        y0 = int(lerp(12, VPY - 30, depth))
        flag = max(2, int(lerp(6, 2, depth)))
        for x in range(x0, x1):
            tt = (x - x0) / max(1, (x1 - x0))
            y = int(y0 + sag * np.sin(np.pi * tt))
            img[y, x] = C["yolkdk"]
            if (x - x0) % (flag * 2 + 2) == 0:
                col = C["yolk"] if ((x - x0) // (flag * 2 + 2)) % 2 == 0 else C["red"]
                for j in range(flag):
                    img[y + 1 + j, x + j // 2:x + flag - j // 2] = col
    # paper crowns trodden into the mud along the street's edges
    for (x, y) in [(40, 116), (72, 104), (252, 112), (226, 100), (100, 120)]:
        for j, dx in enumerate(range(-3, 4)):
            img[y, x + dx] = C["yolk"]
            if dx % 2 == 0:
                img[y - 1, x + dx] = C["yolk"]
        img[y + 1, x - 3:x + 4] = C["mud"]
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
    chin = Image.open(os.path.join(root, "art", "monsters", "second_chin", "normal.png")).convert("RGBA")
    bg.alpha_composite(chin, (160 - chin.width // 2, 122 - chin.height))
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
        out = args[0] if args else "art/battle/plenty.png"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        Image.fromarray(img, "RGBA").save(out)
        print("wrote", out)
