"""Plenty's bestiary: three concepts (world's region 2 - the mouth that gorges; carnival: bodies
overflowing, almost funny, saturated - roast reds, yolk yellows, pinks). A regional idea: whatever
ate the Ever-Sow's meat grows back, and salt stops it (the hero is applying to the Salt Guild).

  A  The Gorger       a walking stomach with a second mouth chewing in its belly. Hook: it eats until
                      it can't move - its telegraph is an opening: it heals, then lies bloated, helpless.
  B  The Second Chin  an alderman whose double chin grew its own face and took charge. Hook: the
                      critic - do the same thing twice and it yawns and punishes it: vary.
  C  The Ever-Sow     the holy pig that regrows whatever is carved off. Hook: it grows back - salt the
                      wound while it knits.

    python tools/art/plenty_concepts.py [OUTDIR] [a b c]   # default art/concepts -> plenty_options.png
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import sculpt as sc
from host_concepts import PAL as HOST_PAL, M, strand, sheet
from host import Frame, fell, fingers, add

PAL = dict(HOST_PAL)
PAL.update({
    "gorge":  dict(ramp=["#5a1e2e", "#9a3a4e", "#d0607a", "#f08ca0", "#ffc2c8"], outline="#2a0c16",
                   spec="#fff0f0", shin=26.0, spec_thr=0.55),
    "velvet": dict(ramp=["#2a0a0a", "#5a1414", "#8e2420", "#c03a2c", "#e0644a"], outline="#140404"),
    "gold":   dict(ramp=["#3a2a06", "#6e5210", "#a8821e", "#d8b23a", "#f8e080"], outline="#1c1404",
                   spec="#fffbe0", shin=30.0, spec_thr=0.5),
    "yolk":   dict(ramp=["#4e3a06", "#8e6a10", "#c89a1e", "#f0c840", "#fff09a"], outline="#261c04"),
    "wig":    dict(ramp=["#4a4648", "#7a7678", "#a8a4a4", "#d0ccca", "#f0eeea"], outline="#242022"),
    "sow":    dict(ramp=["#4e1e28", "#8a3a48", "#c0606e", "#e48c94", "#f8bcc0"], outline="#260c12",
                   spec="#fff2f2", shin=22.0, spec_thr=0.6),
    "raw":    dict(ramp=["#5a0a1a", "#9a1a30", "#d03048", "#f06070", "#ffa0a8"], outline="#2a040c",
                   spec="#ffe0e4", shin=20.0, spec_thr=0.5),
    "wax":    dict(ramp=["#6e5a3a", "#a08a60", "#ccb88a", "#ece0b8", "#fffbe6"], outline="#36281a"),
    "throat": dict(ramp=["#10060c", "#1c0a13", "#2b0e1b", "#3f1424", "#5a1c30"], outline="#0a0408"),
    "steel":  dict(ramp=["#1a1c22", "#34383e", "#585e66", "#8a9098", "#c4cad0"], outline="#0c0e10",
                   spec="#f4f8ff", shin=40.0, spec_thr=0.45),
    "wood":   dict(ramp=["#1c140c", "#34261a", "#504028", "#6e5a3a", "#8e7a52"], outline="#0e0a06"),
})
NAMES = ["gorge", "velvet", "gold", "yolk", "wig", "sow", "raw", "wax", "throat", "steel", "wood", "bone"]


def carnival_light(S):
    """Plenty's light: warmer and fuller than the fen's - fat catches it."""
    L = np.array((-0.45, -0.7, 0.55))
    S.L = L / np.linalg.norm(L)
    S.ambient = 0.3
    S.thresholds = [0.18, 0.34, 0.54, 0.78]
    S.rim_col = sc.hexc("#7a4a62")


def materials(S):
    m = M()
    for name in NAMES:
        setattr(m, name, S.mat(name, **PAL[name]))
    return m


# ==============================================================================================
# A - The Gorger: a walking stomach, a second mouth chewing in its belly
# ==============================================================================================

def gorger():
    S = sc.Scene(72, 80)
    carnival_light(S)
    m = materials(S)
    S.group()
    # stubby legs under a vast belly
    for sx in (-1, 1):
        S.cone((36 + 9 * sx, 64, 0), (36 + 11 * sx, 75, 2), 5, 4.2, m.gorge, k=1.5)
        S.ell((36 + 12 * sx, 77, 4), (5, 2.2, 5.5), m.gorge, k=1.0)
    S.ell((36, 50, 0), (27, 25, 22), m.gorge, k=0)
    # arms too short for the body: a fork in one fist, a drumstick in the other
    for sx in (-1, 1):
        S.cone((36 + 22 * sx, 40, 6), (36 + 29 * sx, 50, 12), 4, 3.2, m.gorge, k=2.0)
        S.sphere((36 + 30 * sx, 52, 13), 3.4, m.gorge, k=1.0)
    # a little head on top, cheeks stuffed, eyes shut in bliss
    S.ell((36, 22, 6), (9, 8, 8), m.gorge, k=3.0)
    for sx in (-1, 1):
        S.sphere((36 + 6 * sx, 25, 10), 4.4, m.gorge, k=2.0)
    S.carve_ell((36, 28, 13), (3, 1.2, 3), k=0.5, mat=m.throat)
    # the belly-mouth: a wide wet grin right across the stomach
    S.carve_ell((36, 54, 21), (15, 5.5, 8), k=1.5, mat=m.throat)
    S.group(k=1.2)
    S.ell((36, 59, 17), (8, 3, 4), m.raw)                     # a tongue lolling out of it
    # a paper festival crown; a stained bib over the top of the belly
    S.group(k=0.5)
    for i, x in enumerate((29, 33, 37, 41)):
        S.cone((x + 1, 15, 6), (x + 1 + (i - 1.5) * 0.6, 9.5, 5), 1.8, 0.4, m.yolk)
    S.ell((36, 15.5, 6), (7.5, 2.0, 6.5), m.yolk)
    # a napkin tucked into its collar, hanging over the top of the belly
    S.ell((36, 37, 17), (11, 8, 2.4), m.wig, rot=(38, 0, 0))
    for sx in (-1, 1):
        S.sphere((36 + 3.5 * sx, 30.5, 13), 1.8, m.wig)
    S.group(k=0.0)
    S.cone((64, 46, 14), (68, 38, 14), 0.9, 0.6, m.steel)    # the fork
    for d in (-1.5, 0, 1.5):
        S.cone((68 + d * 0.3, 38, 14), (68 + d, 33, 14), 0.5, 0.4, m.steel)
    S.cone((7, 50, 14), (3, 44, 14), 1.2, 1.0, m.bone)       # the drumstick
    S.sphere((2.5, 41.5, 14), 3.2, m.velvet)
    R = S.render(ss=2)
    R.cleanup()
    # teeth along the belly-mouth; bliss-shut eyes; sauce on the bib
    for x in range(24, 49, 2):
        y = int(50 + 0.02 * (x - 36) ** 2)
        if R.on(x, y, m.throat) or R.on(x, y + 1, m.throat):
            R.px(x, y, "#fff8e8")
    for x in range(26, 47, 3):
        y = int(59 - 0.015 * (x - 36) ** 2)
        if R.on(x, y, m.throat):
            R.px(x, y, "#ece0c8")
    for sx in (-1, 1):
        R.pxs([(36 + 3 * sx - 1, 21), (36 + 3 * sx, 22), (36 + 3 * sx + 1, 21)], "#5a1e2e")
    for x, y in [(32, 36), (33, 36), (39, 38), (35, 40), (41, 35), (30, 39)]:
        if R.on(x, y, m.wig):
            R.px(x, y, "#c03a2c")
    strand(R, [(30, 60), (29, 64), (30, 67)], "#ffc2c8", only=(m.gorge,))     # drool down the belly
    return R


# ==============================================================================================
# B - The Second Chin: an alderman whose double chin grew its own face and took charge
# ==============================================================================================

def second_chin():
    S = sc.Scene(88, 118)
    carnival_light(S)
    m = materials(S)
    S.group()
    # buckled shoes, white stockings, short legs under a pear of a body
    for sx in (-1, 1):
        S.ell((44 + 8 * sx, 114, 3), (5, 2.5, 6), m.wood, k=1.0)
        S.cone((44 + 7 * sx, 98, 0), (44 + 8 * sx, 112, 1), 5, 4, m.wig, k=1.5)
    S.ell((44, 82, 0), (26, 24, 20), m.velvet, k=0)
    S.ell((44, 58, 2), (19, 15, 15), m.velvet, k=4.0)
    # short arms; one hand clutching a gold goblet
    for sx in (-1, 1):
        S.cone((44 + 18 * sx, 56, 4), (44 + 24 * sx, 76, 10), 5, 4, m.velvet, k=2.0)
        S.sphere((44 + 25 * sx, 79, 11), 3.4, m.gorge, k=1.0)
    S.cone((70, 76, 13), (71, 68, 13), 1.2, 3.0, m.gold, k=0.5)
    # his own head on top, small and frightened, in a powdered wig
    S.ell((44, 27, 6), (8, 9, 8), m.gorge, k=0)
    for (x, y, r) in [(35, 25, 3.8), (53, 25, 3.8), (37, 18, 3.6), (51, 18, 3.6), (44, 16, 4.2), (34, 32, 3.0), (54, 32, 3.0)]:
        S.sphere((x, y, 4), r, m.wig, k=1.0)
    # the chin: bigger than the head, hanging on the chest, with a face of its own
    S.ell((44, 45, 11), (15, 10.5, 11), m.gorge, k=3.0)
    S.carve_ell((45, 50, 21), (8.5, 2.6, 4), k=0.8, mat=m.throat, rot=(0, 0, -6))
    # lace at the throat, half swallowed; the chain of office
    S.group(k=0.6)
    for x in (36, 40, 44, 48, 52):
        S.sphere((x, 57, 15), 2.6, m.wig)
    S.torus((44, 64, 13), (0, -0.35, 1), 11, 1.1, m.gold)
    S.ell((44, 75, 15), (3.6, 3.6, 1.4), m.gold)
    R = S.render(ss=2)
    R.cleanup()
    # his eyes wide with fright, a small round mouth
    for sx in (-1, 1):
        R.pxs([(44 + 3 * sx - 1, 26), (44 + 3 * sx, 26)], "#fff8f0")
        R.px(44 + 3 * sx - (1 if sx < 0 else 0), 26, "#1a0a10")
    R.pxs([(44, 31), (43, 31)], "#5a1e2e")
    # the chin's beady eyes, narrowed; teeth in its sneer
    for sx in (-1, 1):
        R.pxs([(44 + 5 * sx - 1, 43), (44 + 5 * sx, 43), (44 + 5 * sx + 1, 43)], "#5a1e2e")
        R.px(44 + 5 * sx, 44, "#1a0a10")
    for x in range(38, 53, 2):
        y = int(49 + (x - 45) * -0.1)
        if R.on(x, y, m.throat):
            R.px(x, y, "#fff8e8")
    for y in range(60, 90, 6):        # gold buttons down the coat
        if R.on(44, y + 14, m.velvet):
            R.px(44, y + 14, "#f8e080")
    return R


# ==============================================================================================
# C - The Ever-Sow: the holy pig that regrows whatever is carved off
# ==============================================================================================

def ever_sow():
    S = sc.Scene(104, 96)
    carnival_light(S)
    m = materials(S)
    S.group()
    # a vast sow, three-quarter on, facing left
    S.ell((60, 58, -4), (40, 24, 22), m.sow, k=0)
    S.ell((58, 70, 4), (30, 13, 14), m.sow, k=4.0)                  # the hanging belly
    for (x, z) in [(30, 8), (38, -12), (82, 6), (88, -12)]:
        S.cone((x, 72, z), (x - 2, 90, z), 5.5, 4.4, m.sow, k=2.0)
        S.ell((x - 2.5, 92, z + 1), (4.5, 2.4, 5), m.wood, k=0.8)    # trotters
    S.ell((22, 52, 6), (16, 14, 14), m.sow, k=5.0)                  # the head
    S.ell((8, 57, 10), (5, 5.5, 5), m.sow, k=2.0)                   # the snout
    for sz in (1, -1):
        S.ell((24, 39, 6 + 7 * sz), (7, 3, 9), m.sow, k=1.5, rot=(0, 0, -30))   # ears
    # carved flanks: slabs cut away to raw meat, budding back
    for (x, y, w, h) in [(54, 50, 9, 7), (72, 54, 8, 9), (63, 66, 7, 5)]:
        S.carve_ell((x, y, 20), (w, h, 6), k=0.8, mat=m.raw)
    S.group(k=0.8)
    for (x, y) in [(52, 49), (56, 52), (70, 52), (74, 57), (61, 66), (65, 67)]:
        S.sphere((x, y, 16), 2.2, m.raw)
    # dressed like a shrine: a velvet cloth, candles, a gold ring through the snout, a cleaver left in
    S.group(k=1.0)
    S.ell((64, 37, -2), (22, 6, 18), m.velvet)
    S.group(k=0.0)
    for (x, z, h) in [(52, 4, 9), (60, -6, 11), (68, 4, 8), (76, -4, 10)]:
        S.cone((x, 33, z), (x, 33 - h, z), 1.6, 1.4, m.wax)
    S.torus((4, 60, 12), (1, 0, 0.3), 3.0, 0.9, m.gold)
    S.cone((84, 40, 2), (90, 30, 2), 1.2, 1.0, m.wood)
    S.ell((83, 44, 2), (5, 6, 1.0), m.steel, rot=(0, 0, 30))
    R = S.render(ss=2)
    R.cleanup()
    # candle flames, serene shut eyes, nostrils, ribbons
    for (x, h) in [(52, 9), (60, 11), (68, 8), (76, 10)]:
        R.px(x, 33 - h - 1, "#fff09a")
        R.px(x, 33 - h - 2, "#f0c840")
    R.pxs([(18, 48), (19, 49), (20, 49), (21, 48)], "#4e1e28")
    R.pxs([(6, 56), (9, 56)], "#260c12")
    for x in range(40, 90, 3):
        y = int(44 + 0.004 * (x - 64) ** 2)
        if R.on(x, y, m.sow):
            R.px(x, y, "#f0c840")
    return R


CONCEPTS = {"a": gorger, "b": second_chin, "c": ever_sow}
LABELS = {"a": ("A  -  The Gorger", "a walking stomach; it eats until it can't move"),
          "b": ("B  -  The Second Chin", "the chin is in charge; it punishes repeats"),
          "c": ("C  -  The Ever-Sow", "it grows back; salt the wound")}


def compose(img, bg, pos=None):
    h, w = img.shape[:2]
    canvas = bg.copy()
    canvas.alpha_composite(Image.fromarray(img, "RGBA"), pos or (160 - w // 2, 122 - h))
    return canvas


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "art/concepts"
    which = args[1:] or list(CONCEPTS)
    os.makedirs(out, exist_ok=True)
    bg = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_bg.png")).convert("RGBA")
    scenes = []
    for k in which:
        res = CONCEPTS[k]()
        imgs = res if isinstance(res, list) else [res]
        imgs = [r.to_rgba() for r in imgs]
        for j, img in enumerate(imgs):
            sc.save(img, os.path.join(out, f"plenty_{k}{j if len(imgs) > 1 else ''}_x6.png"), 6)
        canvas = bg.copy()
        total = sum(i.shape[1] for i in imgs) + 4 * (len(imgs) - 1)
        x = 160 - total // 2
        for img in imgs:
            canvas.alpha_composite(Image.fromarray(img, "RGBA"), (x, 122 - img.shape[0]))
            x += img.shape[1] + 4
        scenes.append(canvas)
        print("rendered", k)
    sheet(scenes, [LABELS[k] for k in which], os.path.join(out, "plenty_options.png"))
    print("sheet:", os.path.join(out, "plenty_options.png"))
