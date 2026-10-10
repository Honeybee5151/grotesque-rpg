"""The Black Mere battle backdrop (bg "mere"): night on the ferrywoman's barge.

Black water under fog, a far dead shore, the barge's lantern swinging on its post - the only warm
colour - with its light broken on the water, and the barge's harpoon lines sagging off the rails
into the dark. Restrained like the cave: dark, dithered, low contrast, so the monster carries the
picture. The centre stays calm where Old Iron rises; its base sits on the ground line (y=122).

    python tools/art/mere_bg.py [OUT.png] [--preview PNG]   # default art/battle/mere.png

--preview composites Old Iron on it at the battle position, 3x, for judging.
"""
import os
import sys
import numpy as np
from PIL import Image

W, H = 320, 180
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0

C = {k: np.array([int(v[i:i + 2], 16) for i in (1, 3, 5)] + [255], np.uint8) for k, v in {
    "sky0": "#06040a", "sky1": "#0a0812", "sky2": "#0e0a18", "sky3": "#130e20",
    "fog1": "#18122a", "fog2": "#221a34", "fog3": "#2c263e",
    "wat0": "#07080e", "wat1": "#0a0c14", "wat2": "#10141c", "rip1": "#1a2232", "rip2": "#2a3650",
    "foam": "#9ab4cc", "shore": "#05040a",
    "wood0": "#0c0806", "wood1": "#1c140c", "wood2": "#34261a",
    "rope": "#46402a", "ropehi": "#6a6240", "iron": "#141010",
    "amb0": "#4e2a08", "amb1": "#a85e12", "amb2": "#d88a1c", "amb3": "#f4c040",
}.items()}


def dither(img, mask, lo, hi, t):
    """Where mask, blend colour lo -> hi by t (0..1) with an ordered 4x4 dither."""
    ys, xs = np.nonzero(mask)
    pick = t[ys, xs] > BAYER4[ys % 4, xs % 4]
    img[ys[pick], xs[pick]] = C[hi]
    img[ys[~pick], xs[~pick]] = C[lo]


def build():
    img = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    HORIZON = 70

    # sky: darkest at the top, a fog bank lying on the horizon
    sky = yy < HORIZON
    t = np.clip(yy / HORIZON, 0, 1) ** 1.4
    for lo, hi, a, b in [("sky0", "sky1", 0.0, 0.3), ("sky1", "sky2", 0.3, 0.55), ("sky2", "sky3", 0.55, 0.75),
                         ("sky3", "fog1", 0.75, 1.01)]:
        band = sky & (t >= a) & (t < b)
        dither(img, band, lo, hi, (t - a) / (b - a))
    # the fog bank, thickest just above the water, a little lighter behind the middle
    fog = np.exp(-((yy - (HORIZON - 6)) / 9.0) ** 2) * (0.75 + 0.25 * np.exp(-((xx - 160) / 120.0) ** 2))
    band = (yy < HORIZON + 6) & (fog > 0.25)
    dither(img, band & (fog <= 0.6), "fog1", "fog2", (fog - 0.25) / 0.35)
    dither(img, band & (fog > 0.6), "fog2", "fog3", (fog - 0.6) / 0.4)

    # the far shore: a low black line of dead trees, broken, nothing behind the middle
    rng = np.random.default_rng(3)
    for x in range(W):
        if 120 < x < 200:
            continue
        h = 1 + int(2 * abs(np.sin(x * 0.11)) + rng.uniform(0, 1.2))
        img[HORIZON - h:HORIZON + 1, x] = C["shore"]
    for x in [14, 31, 52, 77, 96, 228, 247, 266, 291, 309]:
        h = int(rng.uniform(6, 12))
        img[HORIZON - h:HORIZON, x] = C["shore"]
        for k in range(int(rng.uniform(1, 3))):
            by = HORIZON - h + int(rng.uniform(1, h - 2))
            d = int(rng.choice([-1, 1]))
            img[by, x + d] = C["shore"]
            img[by - 1, x + 2 * d] = C["shore"]

    # water: black, a little less so toward you, ripples lengthening as they come near
    water = yy >= HORIZON
    tw = np.clip((yy - HORIZON) / (H - HORIZON), 0, 1)
    dither(img, water & (tw < 0.5), "wat0", "wat1", tw / 0.5)
    dither(img, water & (tw >= 0.5), "wat1", "wat2", (tw - 0.5) / 0.5)
    # a calmer, faintly lit stretch where the monster rises (the barge lantern's reach)
    lit = np.exp(-(((xx - 160) / 70.0) ** 2 + ((yy - 112) / 22.0) ** 2))
    dither(img, water & (lit > 0.35), "wat2", "rip1", np.clip((lit - 0.35) * 1.2, 0, 1) * 0.45)
    for i in range(240):
        y = int(HORIZON + 2 + (H - HORIZON - 2) * rng.uniform(0, 1) ** 1.6)
        near = (y - HORIZON) / (H - HORIZON)
        x = int(rng.uniform(0, W))
        if abs(x - 160) < 46 and 96 < y < 124:      # keep the monster's footing quiet
            continue
        ln = int(1 + near * 9 * rng.uniform(0.4, 1.0))
        col = "rip2" if near > 0.55 and rng.uniform() < 0.35 else "rip1"
        img[y, max(0, x):min(W, x + ln)] = C[col]
    # rings in the water around the monster's footing
    for r, col in [(46, "rip1"), (58, "rip1"), (70, "wat2")]:
        for a in np.linspace(0, 2 * np.pi, 220, endpoint=False):
            x, y = int(160 + r * np.cos(a)), int(120 + r * 0.16 * np.sin(a))
            if 0 <= x < W and HORIZON < y < H and (int(a * 20) % 3):
                img[y, x] = C[col]

    # the barge's lantern, swinging on its post at the left; the only warm thing on the Mere
    post_x = 26
    img[34:124, post_x:post_x + 2] = C["wood1"]
    img[34:124, post_x] = C["wood2"]
    img[34:36, post_x:post_x + 14] = C["wood1"]
    lx, ly = 41, 50                                   # the lantern, hanging a little off true
    for y in range(36, ly - 4):
        img[y, post_x + 12 + (y - 36) // 6] = C["iron"]
    halo = np.exp(-(((xx - lx) / 12.0) ** 2 + ((yy - ly) / 10.0) ** 2))
    hmask = (halo > 0.35) & (yy < HORIZON + 4)
    dither(img, hmask & (halo <= 0.75), "fog2", "amb0", (halo - 0.35) / 0.4 * 0.45)
    dither(img, hmask & (halo > 0.75), "amb0", "amb1", (halo - 0.75) / 0.25 * 0.35)
    img[ly - 4:ly + 5, lx - 3:lx + 4] = C["iron"]
    img[ly - 3:ly + 4, lx - 2:lx + 3] = C["amb2"]
    img[ly - 2:ly + 3, lx - 1:lx + 2] = C["amb3"]
    img[ly - 5, lx - 1:lx + 2] = C["iron"]
    img[ly + 5, lx - 2:lx + 3] = C["iron"]
    # its light broken on the water below it
    for y in range(HORIZON + 3, 124, 3):
        near = (y - HORIZON) / (124 - HORIZON)
        half = int(1 + near * 4)
        jit = int(rng.integers(-2, 3))
        x0 = lx - half + jit
        col = "amb2" if y < HORIZON + 7 else ("amb1" if y < 96 else "amb0")
        seg = int(rng.integers(1, half * 2 + 1))
        img[y, max(0, x0):min(W, x0 + seg)] = C[col]

    # the barge's rails at the bottom corners, and its harpoon lines sagging out into the dark
    for x in range(0, 64):
        top = int(104 + x * 0.3)
        img[top:124, x] = C["wood0"]
        img[top, x] = C["wood2"]
        img[top + 1, x] = C["wood1"]
    for x in range(256, W):
        top = int(104 + (W - x) * 0.3)
        img[top:124, x] = C["wood0"]
        img[top, x] = C["wood2"]
        img[top + 1, x] = C["wood1"]
    for (x0, y0, x1, y1, sag) in [(50, 117, 104, 98, 9), (270, 117, 222, 96, 8), (58, 118, 128, 104, 5)]:
        for i in range(0, 81):
            t = i / 80.0
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t + sag * np.sin(np.pi * t)
            img[int(y), int(x)] = C["ropehi" if i % 9 == 0 else "rope"]
        for a in np.linspace(0, 2 * np.pi, 16, endpoint=False):     # where it goes into the water
            img[int(y1 + 1 + np.sin(a)), int(x1 + 3 * np.cos(a))] = C["rip2"]
    # a coil of rope on the right rail, an iron cleat on the left
    for a in np.linspace(0, 2 * np.pi, 30, endpoint=False):
        for r in (4, 6):
            img[int(110 + r * 0.45 * np.sin(a)), int(290 + r * np.cos(a))] = C["rope"]
    img[107:110, 44:49] = C["iron"]

    # a few wisps of mist low over the water
    for (x0, y0, ln) in [(70, 84, 46), (196, 80, 58), (118, 92, 30), (240, 96, 34)]:
        for x in range(x0, x0 + ln):
            if (x + y0) % 2 == 0:
                img[y0, x] = C["fog2"]
        for x in range(x0 + 6, x0 + ln - 8):
            if (x + y0) % 3 == 0:
                img[y0 - 1, x] = C["fog1"]
    # a vignette, like the cave: corners sink toward black
    v = ((xx - 160) / 190.0) ** 2 + ((yy - 80) / 120.0) ** 2
    corner = v > 0.82
    darker = {k: "sky0" for k in ["sky1", "sky2", "sky3", "fog1", "wat1", "wat2", "rip1"]}
    for y, x in zip(*np.nonzero(corner)):
        if BAYER4[y % 4, x % 4] < (v[y, x] - 0.82) * 2.2:
            img[y, x] = C["sky0"]
    return img


def preview(img, path):
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    bg = Image.fromarray(img, "RGBA")
    whale = Image.open(os.path.join(root, "art", "monsters", "old_iron", "normal.png")).convert("RGBA")
    bg.alpha_composite(whale, (160 - whale.width // 2, 122 - whale.height))
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
        out = args[0] if args else "art/battle/mere.png"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        Image.fromarray(img, "RGBA").save(out)
        print("wrote", out)
