"""The Hush's bestiary: three concepts (world's region 3 - the mouth sewn shut; dread: bone white, ash
grey, one cold blue - and the cold blue is every monster's focal accent). In a game about a mute
hero, the Hush makes silence the mechanic.

  A  The Hushed Brother  a monk with his mouth sewn shut and a second mouth whispering in his belly.
                         Hook: the hush - it whispers, then seals the hero's skills, unless struck.
  B  The Ear Tree        a dead white tree crusted with human ears. Hook: it hears you - when its ears
                         turn to you, a loud skill draws its branches; quiet actions are safe.
  C  The One Who Waits   impossibly tall, faceless but for a seam, an open palm held out. Hook:
                         silence is consent - each round it waits; unless he strikes it, it takes.

    python tools/art/hush_concepts.py [OUTDIR] [a b c]   # default art/concepts -> hush_options.png
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
    "habit": dict(ramp=["#3a3a40", "#5e5e66", "#8e8e94", "#bcbcbe", "#e4e2dc"], outline="#18181c"),
    "ash":   dict(ramp=["#2e2c30", "#4e4c52", "#76747a", "#a29ea2", "#ccc8c6"], outline="#141216"),
    "ear":   dict(ramp=["#3e2e32", "#6a5054", "#96787a", "#c0a2a2", "#e2caca"], outline="#1c1214"),
    "barkw": dict(ramp=["#2e2c2a", "#56524e", "#837e76", "#b0aa9e", "#d8d2c4"], outline="#141210"),
    "cold":  dict(ramp=["#0a1a2e", "#14325a", "#2a5a96", "#4a8acc", "#9ac8f4"], outline="#04080e",
                  spec="#e0f2ff", shin=26.0, spec_thr=0.45),
    "void":  dict(ramp=["#06060a", "#0c0c12", "#14141c", "#1c1c26", "#262632"], outline="#020204"),
    "robe":  dict(ramp=["#1e1e24", "#2e2e36", "#44444c", "#5e5e66", "#7e7e86"], outline="#0c0c10"),
})
NAMES = ["habit", "ash", "ear", "barkw", "cold", "void", "robe"]
THREAD = "#0a0a0e"


def hush_light(S):
    """The Hush's light: cold, high and thin; long cool shadows."""
    L = np.array((-0.35, -0.82, 0.45))
    S.L = L / np.linalg.norm(L)
    S.ambient = 0.16
    S.thresholds = [0.2, 0.38, 0.58, 0.82]
    S.rim_col = sc.hexc("#3e5872")


def materials(S):
    m = M()
    for name in NAMES:
        setattr(m, name, S.mat(name, **PAL[name]))
    return m


# ==============================================================================================
# A - The Hushed Brother: mouth sewn shut, a second mouth whispering in his belly
# ==============================================================================================

def hushed_brother():
    S = sc.Scene(56, 96)
    hush_light(S)
    m = materials(S)
    S.group()
    # the habit: narrow shoulders falling to a wide hem on the ground
    S.cone((28, 34, 0), (28, 90, 2), 10, 17, m.habit, k=0)
    S.ell((28, 92, 2), (17, 3.5, 12), m.habit, k=2.0)
    S.ell((28, 34, 0), (12, 6, 9), m.habit, k=3.0)
    # the hood, the face sunk in it
    S.ell((28, 19, 1), (10, 11, 9.5), m.habit, k=2.0)
    S.carve_ell((28, 21, 10), (6.5, 8, 4), k=1.2)
    S.group(k=1.0)
    S.ell((28, 21, 5), (5.5, 7, 5), m.ash)
    # hands clasped at the chest
    S.group(k=1.5)
    for sx in (-1, 1):
        S.cone((28 + 11 * sx, 38, 2), (28 + 4 * sx, 48, 10), 3.2, 2.6, m.habit, k=2.0)
    S.sphere((28, 49, 11), 3.6, m.ash, k=1.0)
    # the habit parted at the belly: a second mouth there, upright, whispering, cold blue inside
    S.group(k=0.0)
    S.carve_ell((28, 66, 14), (5, 10, 6), k=1.0, mat=m.ash)
    S.carve_ell((28, 66, 18), (1.6, 6.5, 4), k=0.6, mat=m.cold)
    R = S.render(ss=2)
    R.cleanup()
    # downcast eyes; the mouth sewn shut with black thread
    R.pxs([(25, 18), (26, 19), (30, 19), (31, 18)], "#2e2c30")
    for x in range(24, 33):
        R.px(x, 25, "#2e2c30")
    for x in (25, 27, 29, 31):
        R.pxs([(x, 24), (x + 1, 26)], THREAD)
        R.pxs([(x + 1, 24), (x, 26)], THREAD)
    # the habit parted at the belly: dark edges, grey skin, an upright mouth with lips, cold blue inside
    for y in range(56, 78):
        half = int(5.5 * np.sin(np.pi * (y - 56) / 22.0)) + 1
        R.pxs([(28 - half - 1, y), (28 + half + 1, y)], "#18181c")
        for x in range(28 - half, 28 + half + 1):
            R.px(x, y, "#76747a" if abs(x - 28) > 1 else "#4e4c52")
    for y in range(60, 74):
        R.pxs([(27, y), (29, y)], "#a29ea2" if y % 4 else "#ccc8c6")
        R.px(28, y, "#4a8acc" if 62 < y < 72 else "#2a5a96")
    R.px(28, 66, "#9ac8f4")
    strand(R, [(16, 56), (28, 58), (40, 56)], "#5e5e66")
    strand(R, [(22, 57), (21, 66), (22, 72)], "#5e5e66")
    return R


# ==============================================================================================
# B - The Ear Tree: a dead white tree crusted with human ears
# ==============================================================================================

def ear_tree():
    S = sc.Scene(96, 112)
    hush_light(S)
    m = materials(S)
    S.group()
    # roots like fingers gripping the ground
    for (a, b) in [((40, 100, 4), (18, 109, 8)), ((44, 102, 2), (30, 110, 12)), ((54, 102, 2), (70, 110, 10)),
                   ((58, 100, 4), (80, 108, 6)), ((48, 103, 0), (50, 110, 14))]:
        S.cone(a, b, 4.5, 1.6, m.barkw, k=2.0)
    # a twisted trunk, a dark hollow like an ear canal in it
    S.chain([(48, 104, 0), (44, 84, 2), (50, 64, 2), (46, 46, 0)], [13, 11, 10, 8], m.barkw, k=2.0)
    S.carve_ell((47, 74, 9), (3.5, 9, 6), k=1.2, mat=m.void)
    S.group(k=1.0)
    S.ell((47, 77, 5), (2, 4, 2), m.cold)
    # branches reaching up and out like grasping fingers
    S.group(k=1.5)
    for pts, rr in [([(46, 48, 0), (30, 32, 2), (18, 14, 0), (12, 6, 0)], [7, 5, 3, 1.6]),
                    ([(46, 46, 0), (60, 30, 2), (74, 18, 0), (82, 8, 0)], [7, 5, 3, 1.6]),
                    ([(47, 46, 0), (46, 26, 3), (50, 10, 1)], [6, 4, 1.8]),
                    ([(30, 32, 2), (16, 30, 3), (8, 34, 2)], [4, 2.6, 1.4]),
                    ([(62, 30, 2), (78, 34, 3), (88, 32, 2)], [4, 2.6, 1.4])]:
        S.chain(pts, rr, m.barkw, k=1.2)
    # ears: grown all over it, turned every way
    S.group(k=0.4)
    rng = np.random.default_rng(21)
    spots = [(44, 92, 9), (52, 88, 8), (40, 80, 8), (54, 70, 8), (42, 60, 8), (52, 54, 7), (38, 66, 7),
             (30, 34, 5), (22, 22, 4), (62, 32, 5), (72, 22, 4), (46, 30, 5), (50, 16, 3), (16, 32, 3),
             (80, 34, 3), (56, 96, 8), (36, 96, 8)]
    ears = []
    for (x, y, z) in spots:
        rot = rng.uniform(-60, 60)
        S.ell((x, y, z), (3.4, 5.0, 1.6), m.ear, rot=(0, 0, rot))
        ears.append((x, y, rot))
    R = S.render(ss=2)
    R.cleanup()
    # the inner curl of each ear
    for (x, y, rot) in ears:
        # the curl of each ear: a dark C opening to one side
        a = np.radians(rot)
        for t in np.linspace(-1.9, 1.9, 7):
            ex = int(round(x + 1.6 * np.cos(t) * np.cos(a) - 2.6 * np.sin(t) * np.sin(a) * 0.4))
            ey = int(round(y + 2.6 * np.sin(t) * np.cos(a) + 1.6 * np.cos(t) * np.sin(a)))
            if R.on(ex, ey, m.ear):
                R.px(ex, ey, "#3e2e32")
        if R.on(x, y, m.ear):
            R.px(x, y, "#6a5054")
    # cracks in the white bark
    for pts in [[(46, 98), (44, 90), (46, 84)], [(52, 60), (50, 52)], [(30, 34), (24, 26)]]:
        strand(R, pts, "#56524e", only=(m.barkw,))
    return R


# ==============================================================================================
# C - The One Who Waits: impossibly tall, a seam for a face, a palm held out
# ==============================================================================================

def one_who_waits():
    S = sc.Scene(80, 118)
    hush_light(S)
    m = materials(S)
    S.group()
    # long thin legs under a grey robe that hangs in long folds
    for sx in (-1, 1):
        S.cone((40 + 4 * sx, 74, 0), (40 + 7 * sx, 114, 1), 2.6, 2.0, m.ash, k=1.0)
        S.ell((40 + 8 * sx, 116, 3), (3, 1.4, 4), m.ash, k=0.8)
    S.cone((40, 30, -2), (40, 86, 0), 7, 13, m.robe, k=0)
    for dx in (-8, -3, 3, 8):
        S.cone((40 + dx * 0.4, 40, 4), (40 + dx, 88, 6), 1.6, 2.4, m.robe, k=1.5)
    # shoulders hunched, the neck long and bent so the head hangs forward and down at you
    S.ell((40, 30, -2), (10, 5, 7), m.robe, k=3.0)
    S.cone((42, 28, 0), (52, 16, 8), 2.6, 2.2, m.ash, k=1.5)
    S.ell((55, 15, 12), (6.5, 9.5, 6.5), m.ash, k=1.5, rot=(0, 0, 18))
    # one arm hanging to the ground, too long; the other held out, the palm open, waiting
    S.cone((32, 32, 0), (24, 70, 2), 3, 2.4, m.robe, k=1.5)
    S.cone((24, 70, 2), (22, 106, 4), 2.2, 1.8, m.ash, k=1.0)
    fingers(S, m.ash, [((22, 106, 4), (19, 114, 5)), ((22, 106, 4), (22, 115, 5)), ((22, 106, 4), (25, 114, 5))], 0.8, 0.6)
    S.cone((48, 32, 0), (58, 50, 10), 3, 2.4, m.robe, k=1.5)
    S.cone((58, 50, 10), (64, 62, 18), 2.2, 1.8, m.ash, k=1.0)
    S.ell((65, 64, 20), (4, 1.4, 3.2), m.ash, k=0.8)
    fingers(S, m.ash, [((63, 64, 21), (60, 63, 24)), ((65, 64, 22), (64, 62, 26)), ((67, 64, 21), (69, 62, 24))], 0.7, 0.55)
    # cold blue light pooled in its open palm
    S.group(k=0.6)
    S.sphere((65, 62, 22), 2.4, m.cold)
    R = S.render(ss=2)
    R.cleanup()
    # the face: no eyes, no nose - one vertical seam, stitched shut
    for y in range(9, 22):
        R.px(55 + (y - 15) // 6, y, THREAD)
    for y in range(10, 21, 3):
        R.pxs([(54 + (y - 15) // 6, y), (56 + (y - 15) // 6, y)], "#4e4c52")
    # a glow on the palm and the fingers round it
    R.px(65, 61, "#e0f2ff")
    return R


CONCEPTS = {"a": hushed_brother, "b": ear_tree, "c": one_who_waits}
LABELS = {"a": ("A  -  The Hushed Brother", "sewn mouth, whispering belly; it seals your skills"),
          "b": ("B  -  The Ear Tree", "crusted with ears; it hears your loud moves"),
          "c": ("C  -  The One Who Waits", "silence is consent; strike it or it takes")}


def compose(img, bg):
    h, w = img.shape[:2]
    canvas = bg.copy()
    canvas.alpha_composite(Image.fromarray(img, "RGBA"), (160 - w // 2, 122 - h))
    return canvas


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "art/concepts"
    which = args[1:] or list(CONCEPTS)
    os.makedirs(out, exist_ok=True)
    bg = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_bg.png")).convert("RGBA")
    scenes = []
    for k in which:
        img = CONCEPTS[k]().to_rgba()
        sc.save(img, os.path.join(out, f"hush_{k}_x6.png"), 6)
        scenes.append(compose(img, bg))
        print("rendered", k)
    sheet(scenes, [LABELS[k] for k in which], os.path.join(out, "hush_options.png"))
    print("sheet:", os.path.join(out, "hush_options.png"))
