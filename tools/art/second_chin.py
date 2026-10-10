"""The Second Chin (enemy `second_chin`): a Plenty alderman whose double chin grew its own face and took
charge.

A pear-shaped alderman in roast-red velvet with a gold chain of office and lace at his throat; his
own little face, frightened, under a powdered wig - and under it a double chin grown into a face of
its own, beady and sneering, that does the talking now. Carnival. Focal accent: the chin's mouth.

Poses (88x118, one canvas and ground line):
  normal     stiff, frightened face up top, the chin sneering.
  telegraph  the knowing look: the chin juts forward, eyes narrowed to slits, a smug lopsided smirk;
             the man's little hand flies to his mouth. (It has read what he did last round.)
  hurt       the chin grimaces, the body jiggles back.

    python tools/art/second_chin.py [OUTDIR] [poses...] [--zoom]

Writes <pose>.png at 1x to OUTDIR (default art/monsters/second_chin) and a sheet to
art/concepts/second_chin_poses.png.
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import sculpt as sc
from host_concepts import strand, sheet
from plenty_concepts import PAL, materials, carnival_light, compose

W, H = 88, 118

# jut: how far the chin pushes forward/down; lean: body tilt (deg); hand: where his free hand is;
# chin_eyes / chin_mouth / face: expression states
POSES = {
    "normal": dict(jut=0, lean=0, hand="goblet", chin_eyes="beady", chin_mouth="sneer", face="afraid"),
    "telegraph": dict(jut=4, lean=-4, hand="mouth", chin_eyes="slits", chin_mouth="smirk", face="horror"),
    "hurt": dict(jut=-2, lean=7, hand="goblet", chin_eyes="shut", chin_mouth="grimace", face="afraid"),
}
LABELS = {"normal": ("normal", "his face afraid; the chin in charge"),
          "telegraph": ("telegraph", "the knowing look: it read your last move"),
          "hurt": ("hurt", "the chin grimaces")}


def rot(p, deg, c=(44, 112)):
    a = np.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * np.cos(a) - y * np.sin(a), c[1] + x * np.sin(a) + y * np.cos(a), p[2])


def build(pose):
    P = POSES[pose]
    S = sc.Scene(W, H)
    carnival_light(S)
    m = materials(S)
    lean, jut = P["lean"], P["jut"]
    T = lambda p: rot(p, lean)

    S.group()
    # buckled shoes, white stockings, short legs under a pear of a body
    for sx in (-1, 1):
        S.ell((44 + 8 * sx, 114, 3), (5, 2.5, 6), m.wood, k=1.0)
        S.cone(T((44 + 7 * sx, 98, 0)), (44 + 8 * sx, 112, 1), 5, 4, m.wig, k=1.5)
    S.ell(T((44, 82, 0)), (26, 24, 20), m.velvet, k=0, rot=(0, 0, lean))
    S.ell(T((44, 58, 2)), (19, 15, 15), m.velvet, k=4.0, rot=(0, 0, lean))
    # arms: his right holds the goblet; his left hangs - or flies up to his little mouth
    S.cone(T((26, 56, 4)), T((20, 76, 10)), 5, 4, m.velvet, k=2.0)
    S.sphere(T((19, 79, 11)), 3.4, m.gorge, k=1.0)
    if P["hand"] == "mouth":
        S.cone(T((62, 56, 4)), T((64, 42, 14)), 5, 4, m.velvet, k=2.0)
        S.cone(T((64, 42, 14)), T((53, 32, 14)), 3.6, 3.0, m.velvet, k=1.5)
        S.sphere(T((51, 31, 15)), 3.0, m.gorge, k=1.0)
    else:
        S.cone(T((62, 56, 4)), T((68, 76, 10)), 5, 4, m.velvet, k=2.0)
        S.sphere(T((69, 79, 11)), 3.4, m.gorge, k=1.0)
        S.cone(T((70, 76, 13)), T((71, 68, 13)), 1.2, 3.0, m.gold, k=0.5)
    # his own head on top, small and frightened, in a powdered wig
    S.ell(T((44, 27, 6)), (8, 9, 8), m.gorge, k=0)
    for (x, y, r) in [(35, 25, 3.8), (53, 25, 3.8), (37, 18, 3.6), (51, 18, 3.6), (44, 16, 4.2), (34, 32, 3.0), (54, 32, 3.0)]:
        S.sphere(T((x, y, 4)), r, m.wig, k=1.0)
    # the chin: bigger than the head, a face of its own; it juts out when it knows something
    chin = T((44, 45 + jut * 0.5, 11 + jut))
    S.ell(chin, (15, 10.5, 11), m.gorge, k=3.0, rot=(0, 0, lean))
    mouth_rot = {"sneer": -6, "smirk": -14, "grimace": 4}[P["chin_mouth"]]
    mh = {"sneer": 2.6, "smirk": 1.8, "grimace": 3.2}[P["chin_mouth"]]
    S.carve_ell((chin[0] + 1 + (2 if P["chin_mouth"] == "smirk" else 0), chin[1] + 5, chin[2] + 10),
                (8.5, mh, 4), k=0.8, mat=m.throat, rot=(0, 0, lean + mouth_rot))
    # lace at the throat, half swallowed; the chain of office and its medal
    S.group(k=0.6)
    for x in (36, 40, 44, 48, 52):
        S.sphere(T((x, 57, 15)), 2.6, m.wig)
    S.torus(T((44, 64, 13)), (0, -0.35, 1), 11, 1.1, m.gold)
    S.ell(T((44, 75, 15)), (3.6, 3.6, 1.4), m.gold)
    R = S.render(ss=2)
    R.cleanup()
    details(R, m, P, T, chin)
    return R


def details(R, m, P, T, chin):
    def px(p, col):
        x, y, _ = T((p[0], p[1], 0))
        R.px(int(round(x)), int(round(y)), col)

    # his eyes: wide with fright, or wider still with horror (and no mouth to see behind his hand)
    for sx in (-1, 1):
        cx = 44 + 3 * sx
        px((cx - 1, 25), "#fff8f0")
        px((cx, 25), "#fff8f0")
        px((cx - 1, 26), "#fff8f0")
        px((cx, 26), "#fff8f0")
        px((cx - (0 if sx < 0 else 1), 26 if P["face"] == "afraid" else 25), "#1a0a10")
    if P["face"] == "afraid":
        px((44, 31), "#5a1e2e")
        px((43, 31), "#5a1e2e")
    # the chin's eyes: beady, narrowed to smug slits, or squeezed shut
    ccx, ccy = chin[0], chin[1]
    for sx in (-1, 1):
        ex, ey = int(ccx + 5 * sx), int(ccy - 2)
        if P["chin_eyes"] == "beady":
            R.pxs([(ex - 1, ey), (ex, ey), (ex + 1, ey)], "#5a1e2e")
            R.px(ex, ey + 1, "#1a0a10")
        elif P["chin_eyes"] == "slits":
            R.pxs([(ex - 2, ey + 1), (ex - 1, ey), (ex, ey), (ex + 1, ey), (ex + 2, ey - (1 if sx > 0 else 0))], "#1a0a10")
            R.px(ex + sx * 2, ey - 2, "#5a1e2e")          # a brow cocked
        else:
            R.pxs([(ex - 1, ey + 1), (ex, ey), (ex + 1, ey + 1)], "#5a1e2e")
    # teeth in the chin's mouth
    for x in range(int(ccx) - 7, int(ccx) + 9, 2):
        for y in range(int(ccy) + 2, int(ccy) + 9):
            if R.on(x, y, m.throat):
                R.px(x, y, "#fff8e8")
                break
    # gold buttons down the coat
    for y in range(74, 104, 6):
        x, yy, _ = T((44, y, 0))
        if R.on(int(x), int(yy), m.velvet):
            R.px(int(x), int(yy), "#f8e080")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "art/monsters/second_chin"
    extra = out if args else "art/concepts"
    which = args[1:] or list(POSES)
    os.makedirs(out, exist_ok=True)
    bg = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_bg.png")).convert("RGBA")
    scenes = []
    for k in which:
        img = build(k).to_rgba()
        sc.save(img, os.path.join(out, f"{k}.png"))
        if "--zoom" in sys.argv:
            sc.save(img, os.path.join(extra, f"second_chin_{k}_x6.png"), 6)
        scenes.append(compose(img, bg))
        print("wrote", os.path.join(out, f"{k}.png"))
    path = os.path.join(extra, "second_chin_poses.png")
    sheet(scenes, [LABELS[k] for k in which], path)
    print("sheet:", path)
