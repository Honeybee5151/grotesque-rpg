"""The Long Swallow battle backdrop (bg "swallow"): inside the Ever-Sow's gullet, under Plenty.

The Examination's first phase is an endless tunnel - and it is the holy pig's throat. Ribbed, wet,
fleshy walls recede to a dark gulp at the centre, where the monster stands out against the dark;
cartilage rings catch the light, mucus hangs in strands, saliva pools on the floor. Earlier
applicants stuck candles into the ribs to light their way in; far down the throat, a pale shape walks
away - the examiner, too far to make out. Carnival-warm but
visceral, and still restrained like the other backdrops so the monster carries the picture.

    python tools/art/swallow_bg.py [OUT.png] [--preview PNG]   # default art/battle/swallow.png

--preview composites a pack of Gorgers on it at the battle positions, 3x.
"""
import os
import sys
import numpy as np
from PIL import Image

W, H = 320, 180
VPX, VPY = 160, 70                 # the throat: where the tunnel goes down
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0

C = {k: np.array([int(v[i:i + 2], 16) for i in (1, 3, 5)] + [255], np.uint8) for k, v in {
    "deep0": "#08030a", "deep1": "#14060e", "deep2": "#220a16",
    "wall0": "#30101e", "wall1": "#46162a", "wall2": "#5e1e34", "rib1": "#7a2a40", "rib2": "#9a3c52",
    "ribhi": "#c46478", "wet": "#e8a4ae",
    "floor0": "#3a1222", "floor1": "#521a2e", "spit": "#7e3e52", "spithi": "#c08a96",
    "amb0": "#5a2a12", "amb1": "#a85e22", "amb2": "#e09a30", "amb3": "#f8d060", "iron": "#1a1014",
    "wax": "#e8d8b0", "pale": "#b8a8ac",
}.items()}


def dither(img, mask, lo, hi, t):
    ys, xs = np.nonzero(mask)
    pick = t[ys, xs] > BAYER4[ys % 4, xs % 4]
    img[ys[pick], xs[pick]] = C[hi]
    img[ys[~pick], xs[~pick]] = C[lo]


def build():
    img = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    # distance from the throat in "tunnel space": the walls are ellipses around the vanishing point
    d0 = np.sqrt(((xx - VPX) / 1.0) ** 2 + ((yy - VPY) / 0.62) ** 2)
    ang = np.arctan2(yy - VPY, xx - VPX)
    d = d0 + (1.8 + d0 * 0.025) * np.sin(ang * 5 + d0 * 0.05) + (1.0 + d0 * 0.012) * np.sin(ang * 11 - d0 * 0.03)
    depth = np.clip(d / 210.0, 0, 1)                 # 0 at the throat, 1 at the frame
    # the flesh: darkest down the throat, warmer toward you
    for lo, hi, a, b in [("deep0", "deep1", 0.0, 0.12), ("deep1", "deep2", 0.12, 0.24), ("deep2", "wall0", 0.24, 0.42),
                         ("wall0", "wall1", 0.42, 0.66), ("wall1", "wall2", 0.66, 1.01)]:
        band = (depth >= a) & (depth < b)
        dither(img, band, lo, hi, (depth - a) / (b - a))
    # cartilage rings: bands spaced in perspective, lit along their top edges
    rng0 = np.random.default_rng(4)
    ring_r = [26 * 1.32 ** i for i in range(9)]
    for i, r in enumerate(ring_r):
        thick = (1.2 + i * 0.55) * (0.75 + 0.35 * np.sin(ang * 3 + i))
        band = np.abs(d - r) < thick
        lit = (yy < VPY + 0.62 * r * 0.15) & band
        near = min(1.0, r / 200.0)
        img[band] = C["rib1"] if near > 0.35 else C["wall1"]
        img[lit & (np.abs(d - r) < thick * 0.55)] = C["rib2"] if near > 0.35 else C["rib1"]
        # wet glints along the upper-left of the nearer rings
        if near > 0.3:
            glint = band & (np.abs(d - r) < 0.8) & (ang > -2.6) & (ang < -1.9)
            img[glint] = C["ribhi"]
    # veins branching out from the throat along the walls
    for a0 in [-2.8, -2.2, -1.4, -0.7, -0.2, 0.5, 2.6, 3.0]:
        r = 30.0
        a = a0
        while r < 230:
            x, y = int(VPX + r * np.cos(a)), int(VPY + 0.62 * r * np.sin(a))
            if 0 <= x < W and 0 <= y < 96 and depth[y, x] > 0.3:
                img[y, x] = C["wall0"]
            r += 1.4
            a += rng0.uniform(-0.012, 0.012)
    # the floor: the tunnel's bottom flattens into a wet, fleshy floor where things stand
    floor = yy > 96 + 0.0 * xx
    tf = np.clip((yy - 96) / 28.0, 0, 1)
    dither(img, floor & (yy < 124), "floor0", "floor1", tf * 0.8)
    rng = np.random.default_rng(9)
    # saliva pooled on the floor, with highlights; kept out of the monsters' footing in the middle
    for (px, py, rx, ry) in [(52, 112, 18, 3), (268, 116, 22, 3.5), (110, 104, 10, 2), (214, 106, 12, 2)]:
        m = ((xx - px) / rx) ** 2 + ((yy - py) / ry) ** 2 < 1
        img[m] = C["spit"]
        hl = ((xx - px + rx * 0.3) / (rx * 0.4)) ** 2 + ((yy - py + ry * 0.3) / (ry * 0.35)) ** 2 < 1
        img[hl & m] = C["spithi"]
    # mucus strands hanging from the roof of the throat
    for x0 in [64, 92, 124, 198, 232, 262, 286]:
        y0 = int(VPY - 0.62 * np.sqrt(max(0, 150 ** 2 - (x0 - VPX) ** 2)) * 0.6) + 8
        y0 = max(2, y0)
        length = int(rng.uniform(10, 26))
        sway = rng.uniform(-2, 2)
        for j in range(length):
            x = int(x0 + sway * j / length)
            y = y0 + j
            if 0 <= y < 96:
                img[y, x] = C["wet"] if j % 5 == 0 else C["rib2"]
        drop = y0 + length + 1
        if drop < 96:
            img[drop, int(x0 + sway)] = C["wet"]
    # candles earlier applicants stuck into the ribs to light their way in - guttering, warm
    for (cx, cy) in [(38, 44), (60, 26), (26, 80), (100, 16), (222, 18), (258, 30), (292, 50), (284, 86)]:
        halo = np.exp(-(((xx - cx) / 11.0) ** 2 + ((yy - cy) / 9.0) ** 2))
        hm = (halo > 0.35) & (yy < 124)
        dither(img, hm & (halo <= 0.75), "wall2", "amb0", (halo - 0.35) / 0.4 * 0.45)
        dither(img, hm & (halo > 0.75), "amb0", "amb1", (halo - 0.75) / 0.25 * 0.3)
        img[cy:cy + 4, cx] = C["wax"]
        img[cy + 3, cx - 1:cx + 2] = C["wax"]
        img[cy - 1, cx] = C["amb3"]
        img[cy - 2, cx] = C["amb2"]
        img[cy + 1, cx + 1] = C["wax"]                       # a drip of wax down the rib
    # far down the throat, a pale shape walking away: the examiner, too far to make out
    ex, ey = 182, 60
    img[ey:ey + 2, ex] = C["pale"]
    img[ey + 2:ey + 6, ex - 1:ex + 2] = C["pale"]
    img[ey + 6:ey + 8, ex - 1] = C["pale"]
    img[ey + 6:ey + 8, ex + 1] = C["pale"]
    # a vignette: the frame sinks toward the dark
    v = ((xx - 160) / 190.0) ** 2 + ((yy - 80) / 120.0) ** 2
    corner = v > 0.8
    for y, x in zip(*np.nonzero(corner)):
        if BAYER4[y % 4, x % 4] < (v[y, x] - 0.8) * 2.2:
            img[y, x] = C["deep0"]
    return img


def preview(img, path):
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    bg = Image.fromarray(img, "RGBA")
    pack = [Image.open(os.path.join(root, "art", "monsters", "gorger", f"{p}.png")).convert("RGBA")
            for p in ("normal", "telegraph", "normal_3")]
    total = sum(p.width for p in pack) + 8
    x = 160 - total // 2
    for p in pack:
        bg.alpha_composite(p, (x, 122 - p.height))
        x += p.width + 4
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
        out = args[0] if args else "art/battle/swallow.png"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        Image.fromarray(img, "RGBA").save(out)
        print("wrote", out)
