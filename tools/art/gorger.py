"""The Gorger (enemy `gorger`): Plenty's common pack monster.

A walking stomach on stubby legs: a tiny head in a paper festival crown, cheeks stuffed, a napkin
tucked in its collar, and a second mouth grinning and chewing right across its belly - mouths
budding where mouths shouldn't. Carnival: pink, greasy, almost funny. Focal accent: the belly-mouth.

Poses (72x80, one canvas and ground line):
  normal, normal_2, normal_3   three individuals: fork and drumstick / hugging a pie / sausages
  telegraph                    the feast: arms up shovelling, cheeks bulging, the belly-mouth gaping
  stunned                      bloated: swollen rounder, tipped back, legs splayed, eyes rolled,
                               the napkin popped loose - its helpless turn, the opening
  hurt                         a jiggling flinch

    python tools/art/gorger.py [OUTDIR] [poses...] [--zoom]

Writes <pose>.png at 1x to OUTDIR (default art/monsters/gorger) and a sheet of a pack to
art/concepts/gorger_poses.png.
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import sculpt as sc
from host_concepts import strand, sheet
from plenty_concepts import PAL, materials, carnival_light

W, H = 72, 80

# belly: scale of the stomach; tip: lean back (px the top moves back/up); arms: variant;
# held: what's in its hands; eyes: bliss / wide / rolled / shut; gape: how wide the belly-mouth opens
POSES = {
    "normal": dict(belly=1.0, sink=0, arms="hold", held="fork", eyes="bliss", gape=1.0, napkin="tucked"),
    "normal_2": dict(belly=1.0, sink=0, arms="hug", held="pie", eyes="bliss", gape=0.8, napkin="tucked"),
    "normal_3": dict(belly=1.0, sink=0, arms="hold", held="sausage", eyes="wide", gape=1.0, napkin="tucked"),
    "telegraph": dict(belly=1.04, sink=-1, arms="shovel", held="feast", eyes="wide", gape=1.6, napkin="tucked"),
    "stunned": dict(belly=1.16, sink=3, arms="flop", held=None, eyes="rolled", gape=0.6, napkin="popped"),
    "hurt": dict(belly=0.96, sink=2, arms="flinch", held="fork", eyes="shut", gape=0.7, napkin="tucked"),
}
LABELS = {"normal": ("normal", "a pack of three, each its own"),
          "telegraph": ("telegraph", "the feast: it shovels it in"),
          "stunned": ("stunned", "bloated: it can't move"),
          "hurt": ("hurt", "a flinch")}


def build(pose):
    P = POSES[pose]
    S = sc.Scene(W, H)
    carnival_light(S)
    m = materials(S)
    b, sk = P["belly"], P["sink"]
    cy = 50 + sk                       # the belly's centre
    S.group()
    # stubby legs (splayed when bloated)
    spread = 4 if pose == "stunned" else 0
    for sx in (-1, 1):
        S.cone((36 + 9 * sx, 64 + sk, 0), (36 + (11 + spread) * sx, 75, 2 + spread), 5, 4.2, m.gorge, k=1.5)
        S.ell((36 + (12 + spread) * sx, 77, 4 + spread), (5, 2.2, 5.5), m.gorge, k=1.0)
    S.ell((36, cy, 0), (27 * b, 25 * b, 22 * b), m.gorge, k=0)
    # the little head on top (tipped back when bloated); cheeks stuffed
    hy = cy - 28 * b + (2 if pose == "stunned" else 0)
    hz = 6 - (5 if pose == "stunned" else 0)
    S.ell((36, hy, hz), (9, 8, 8), m.gorge, k=3.0)
    cheek = 5.4 if pose == "telegraph" else 4.4
    for sx in (-1, 1):
        S.sphere((36 + 6 * sx, hy + 3, hz + 4), cheek, m.gorge, k=2.0)
    S.carve_ell((36, hy + 6, hz + 7), (3, 1.2 + (0.8 if pose == "telegraph" else 0), 3), k=0.5, mat=m.throat)
    # the belly-mouth across the stomach
    mz = 21 * b
    S.carve_ell((36, cy + 4, mz), (15 * b, 5.5 * P["gape"], 8), k=1.5, mat=m.throat)
    S.group(k=1.2)
    S.ell((36, cy + 4 + 5.5 * P["gape"] - 1, mz - 4), (8, 3, 4), m.raw)

    # arms: holding, hugging, shovelling (up), flopped, flinching
    S.group(k=2.0)
    arms = {
        "hold": [((14, cy - 10, 6), (10, cy, 12)), ((58, cy - 10, 6), (62, cy, 12))],
        "hug": [((14, cy - 10, 6), (24, cy - 2, 20)), ((58, cy - 10, 6), (48, cy - 2, 20))],
        "shovel": [((14, cy - 10, 6), (14, cy - 26, 14)), ((58, cy - 10, 6), (56, cy - 24, 16))],
        "flop": [((12, cy - 8, 4), (6, cy + 6, 4)), ((60, cy - 8, 4), (66, cy + 6, 4))],
        "flinch": [((14, cy - 10, 6), (11, cy - 20, 10)), ((58, cy - 10, 6), (63, cy - 4, 8))],
    }[P["arms"]]
    for a, hnd in arms:
        S.cone(a, hnd, 4, 3.2, m.gorge, k=2.0)
        S.sphere(hnd, 3.4, m.gorge, k=1.0)

    # a paper festival crown (knocked askew when bloated); the napkin tucked in, or popped loose
    S.group(k=0.5)
    tilt = -18 if pose == "stunned" else (8 if pose == "hurt" else 0)
    crown_y = hy - 6.5
    for i, x in enumerate((29, 33, 37, 41)):
        S.cone((x + 1, crown_y, hz), (x + 1 + (i - 1.5) * 0.6 + tilt * 0.08, crown_y - 5.5, hz - 1), 1.8, 0.4, m.yolk)
    S.ell((36 + tilt * 0.1, crown_y, hz), (7.5, 2.0, 6.5), m.yolk, rot=(0, 0, tilt))
    if P["napkin"] == "tucked":
        S.ell((36, cy - 13 * b, 17 * b), (11, 8, 2.4), m.wig, rot=(38, 0, 0))
        for sx in (-1, 1):
            S.sphere((36 + 3.5 * sx, cy - 19.5 * b, 13), 1.8, m.wig)
    else:
        S.ell((52, cy - 22, 10), (9, 6, 2.0), m.wig, rot=(20, 0, 35))     # flapping loose off one shoulder

    # what it holds
    S.group(k=0.0)
    held = P["held"]
    if held == "fork":
        hx, hy2 = arms[1][1][0], arms[1][1][1]
        S.cone((hx - 1, hy2 - 2, 14), (hx + 3, hy2 - 10, 14), 0.9, 0.6, m.steel)
        for d in (-1.5, 0, 1.5):
            S.cone((hx + 3 + d * 0.3, hy2 - 10, 14), (hx + 3 + d, hy2 - 15, 14), 0.5, 0.4, m.steel)
        dx, dy = arms[0][1][0], arms[0][1][1]
        S.cone((dx, dy - 1, 14), (dx - 2, dy - 7, 14), 1.2, 1.0, m.bone)
        S.sphere((dx - 2.5, dy - 9.5, 14), 3.2, m.velvet)
    elif held == "pie":
        S.ell((36, cy - 3, 24), (10, 3.5, 6), m.wax, rot=(-15, 0, 0))     # a pie, hugged to the belly
        S.ell((36, cy - 5, 24), (9, 1.4, 5.5), m.velvet, rot=(-15, 0, 0))
    elif held == "sausage":
        pts = [(56, cy - 22, 8), (60, cy - 26, 6), (63, cy - 20, 4), (64, cy - 11, 6), (62, cy - 2, 10), (59, cy + 6, 12)]
        for p in pts:
            S.ell(p, (2.6, 3.4, 2.6), m.velvet, rot=(0, 0, 20))
        S.cone(arms[0][1], (arms[0][1][0] - 2, arms[0][1][1] - 7, 14), 1.2, 1.0, m.bone)
    elif held == "feast":
        for (x, y, z, r, mat) in [(14, cy - 30, 16, 3.4, m.velvet), (56, cy - 28, 18, 3.0, m.yolk),
                                  (30, cy + 2, 24, 2.6, m.velvet), (40, cy + 3, 24, 2.4, m.wax)]:
            S.sphere((x, y, z), r, mat)                               # food going in, both ends

    R = S.render(ss=2)
    R.cleanup()
    details(R, m, P, pose, cy, hy, b)
    return R


def details(R, m, P, pose, cy, hy, b):
    # teeth along the belly-mouth: top row and bottom row
    top = cy + 4 - 5.5 * P["gape"] + 1
    bot = cy + 4 + 5.5 * P["gape"] - 1
    for x in range(24, 49, 2):
        y = int(top + 0.02 * (x - 36) ** 2)
        if R.on(x, y, m.throat) or R.on(x, y + 1, m.throat):
            R.px(x, y, "#fff8e8")
    for x in range(26, 47, 3):
        y = int(bot - 0.015 * (x - 36) ** 2)
        if R.on(x, y, m.throat):
            R.px(x, y, "#ece0c8")
    # the eyes: shut in bliss, wide and greedy, rolled up full, or squeezed shut
    ey = int(hy - 1)
    for sx in (-1, 1):
        ex = 36 + 3 * sx
        if P["eyes"] == "bliss":
            R.pxs([(ex - 1, ey), (ex, ey + 1), (ex + 1, ey)], "#5a1e2e")
        elif P["eyes"] == "wide":
            R.pxs([(ex - 1, ey), (ex, ey)], "#fff8f0")
            R.px(ex - (1 if sx > 0 else 0), ey, "#1a0a10")
        elif P["eyes"] == "rolled":
            R.pxs([(ex - 1, ey + 1), (ex, ey + 1)], "#fff8f0")
            R.px(ex, ey, "#1a0a10")
        else:
            R.pxs([(ex - 1, ey + 1), (ex, ey), (ex + 1, ey + 1)], "#5a1e2e")
    # sauce on the napkin; drool down the belly
    if P["napkin"] == "tucked":
        for x, y in [(32, -13), (33, -13), (39, -11), (35, -9), (41, -14), (30, -10)]:
            yy = int(cy + y * b)
            if R.on(x, yy, m.wig):
                R.px(x, yy, "#c03a2c")
    strand(R, [(30, int(cy + 10)), (29, int(cy + 14)), (30, int(cy + 17))], "#ffc2c8", only=(m.gorge,))
    if pose == "stunned":
        # stretched shiny skin, a burp of steam off the little head
        for x, y in [(20, cy - 12), (52, cy - 10), (24, cy + 12)]:
            if R.on(int(x), int(y), m.gorge):
                R.px(int(x), int(y), "#fff0f0")
        for i, (x, y) in enumerate([(42, hy - 10), (44, hy - 13), (41, hy - 16), (44, hy - 19)]):
            if 0 <= y < H and not R.on(int(x), int(y), m.gorge):
                R.px(int(x), int(y), "#f0eeea" if i % 2 else "#a8a4a4")
    if P["held"] == "pie":
        for x in range(28, 45, 3):
            if R.on(x, int(cy - 2), m.wax):
                R.px(x, int(cy - 2), "#8e2420")


def formation(imgs, bg):
    total = sum(i.shape[1] for i in imgs) + 4 * (len(imgs) - 1)
    x = 160 - total // 2
    canvas = bg.copy()
    for i in imgs:
        canvas.alpha_composite(Image.fromarray(i, "RGBA"), (x, 122 - i.shape[0]))
        x += i.shape[1] + 4
    return canvas


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "art/monsters/gorger"
    extra = out if args else "art/concepts"
    which = args[1:] or list(POSES)
    os.makedirs(out, exist_ok=True)
    imgs = {}
    for k in which:
        imgs[k] = build(k).to_rgba()
        sc.save(imgs[k], os.path.join(out, f"{k}.png"))
        if "--zoom" in sys.argv:
            sc.save(imgs[k], os.path.join(extra, f"gorger_{k}_x6.png"), 6)
        print("wrote", os.path.join(out, f"{k}.png"))
    if all(k in imgs for k in POSES):
        bg = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_bg.png")).convert("RGBA")
        scenes = [formation([imgs["normal"], imgs["normal_2"], imgs["normal_3"]], bg),
                  formation([imgs["normal"], imgs["telegraph"], imgs["normal_3"]], bg),
                  formation([imgs["normal"], imgs["stunned"], imgs["hurt"]], bg)]
        labels = [LABELS["normal"], LABELS["telegraph"], ("stunned / hurt", "bloated: it can't move / a flinch")]
        path = os.path.join(extra, "gorger_poses.png")
        sheet(scenes, labels, path)
        print("sheet:", path)
