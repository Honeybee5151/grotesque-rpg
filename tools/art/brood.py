"""The Brood (enemy `brood`) and her spawnlings (`spawnling`): the Sallow Fen's boss, deep in the
flooded caves under Hollowell's well. The Sucker Frog that took Odo is one of hers.

A bloated dark toad squatting in black water, dead milky eyes half-lidded, her back a heaped dome of
glossy black spawn with riders curled in the eggs. Under her chin hangs a pale sac of more. Focal
accent: that sac, and the pink sucker in the seam of her mouth.

Brood poses (104x96):
  normal     squatting, the sac slack under her chin.
  telegraph  the hatch: she rears her head and the sac swells into a stretched pale balloon, the
             eggs inside showing through - next round they drop into the fight.
  hurt       a flinch: eyes squeezed shut, she sinks, the sac slack.
Spawnling poses (40x44), a hatched rider - a baby Sucker Frog:
  normal     a glossy black tadpole-frog sitting on its curled tail, one pale embryo eye.
  telegraph  coiled to leap at the hero, the tiny sucker flared.
  hurt       squashed flat.

    python tools/art/brood.py [OUTDIR] [--zoom]

Writes art/monsters/brood/<pose>.png and art/monsters/spawnling/<pose>.png at 1x (OUTDIR replaces
art/monsters), and a sheet of the formation to art/concepts/brood_poses.png.
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import sculpt as sc
from host_concepts import PAL as HOST_PAL, horror_light, M, warts, strand, sheet

PAL = dict(HOST_PAL)
PAL.update({
    "brood":  dict(ramp=["#0e120e", "#1a2118", "#2a3424", "#3f4a30", "#5b6440"], outline="#070906",
                   spec="#b8c08c", shin=22.0, spec_thr=0.55),
    "pale":   dict(ramp=["#2a2618", "#46402a", "#665e40", "#8a8058", "#aca274"], outline="#14120a"),
    "milk":   dict(ramp=["#2e2e2a", "#4e4c46", "#74726a", "#9e9a8e", "#c8c4b4"], outline="#121210",
                   spec="#f0eee4", shin=30.0, spec_thr=0.5),
    "sac":    dict(ramp=["#3a1c26", "#5e3040", "#86505e", "#ae7882", "#d0a4a8"], outline="#1a0c10",
                   spec="#f4dcdc", shin=24.0, spec_thr=0.5),
    "spawn":  dict(ramp=["#050608", "#0c0e12", "#151a20", "#232a32", "#36404a"], outline="#020203",
                   spec="#e4eef4", shin=36.0, spec_thr=0.42),
    "water":  dict(ramp=["#05060a", "#0a0c12", "#10141c", "#1a2232", "#2a3650"], outline="#030305",
                   spec="#9ab4cc", shin=40.0, spec_thr=0.35),
    "throat": dict(ramp=["#10060c", "#1c0a13", "#2b0e1b", "#3f1424", "#5a1c30"], outline="#0a0408"),
})
JELLY = "#5a6670"
EMBRYO = "#b9c4b0"


def materials(S):
    m = M()
    for name in ["brood", "pale", "milk", "sac", "spawn", "water", "throat", "flesh"]:
        setattr(m, name, S.mat(name, **PAL[name]))
    return m


# ==============================================================================================
# the Brood
# ==============================================================================================

BW, BH = 104, 96
BROOD = {
    "normal": dict(rear=0, sink=0, sac=(10, 6, 6.5), sac_y=73, lid=0.0, eyes="dead"),
    "telegraph": dict(rear=5, sink=0, sac=(16, 11.5, 11), sac_y=78, lid=-1.6, eyes="dead"),
    "hurt": dict(rear=-1, sink=3, sac=(8.5, 5, 5.5), sac_y=74, lid=2.2, eyes="shut"),
}


def brood(pose):
    P = BROOD[pose]
    rr, sk = P["rear"], P["sink"]
    S = sc.Scene(BW, BH)
    horror_light(S)
    m = materials(S)
    S.group()
    S.ell((52, 93, 0), (49, 1.8, 16), m.water)

    S.group()
    # a bloated body squatting in the pool, haunches folded at her sides
    S.ell((52, 70 + sk, -6), (36, 20 - sk * 0.5, 24), m.brood, k=0)
    S.ell((52, 79 + sk, 9), (26, 10, 11), m.pale, k=2.0)
    S.ell((16, 77 + sk, -6), (10, 12, 10), m.brood, k=2.0, rot=(0, 0, -12))
    S.ell((88, 77 + sk, -6), (10, 12, 10), m.brood, k=2.0, rot=(0, 0, 12))
    for sx in (-1, 1):
        a, b = (52 + 20 * sx, 76 + sk, 10), (52 + 27 * sx, 90, 14)
        S.cone(a, b, 6, 4.5, m.brood, k=1.5)
        for dx in (-3.5, 0, 3.5):
            S.cone(b, (b[0] + dx * 1.4 + 2 * sx, 93, 17), 1.6, 1.2, m.brood, k=0.6)
    # a wide flat head, raised when she rears; the mouth a long seam
    hy = 59 + sk - rr
    S.ell((52, hy, 10 + rr * 0.4), (25, 10.5, 13), m.brood, k=3.0, rot=(-rr * 2.5, 0, 0))
    S.carve_ell((52, hy + 5, 22.5 + rr * 0.3), (21, 0.9, 4), k=0.4, mat=m.throat)
    S.group(k=0.6)
    eyes = [(52 + 15 * sx, hy - 10, 15.5) for sx in (-1, 1)]
    for e in eyes:
        S.sphere(e, 4.4, m.milk)
    S.group(k=0.8)
    for e, sx in zip(eyes, (-1, 1)):
        if P["eyes"] == "shut":
            S.ell((e[0], e[1], e[2] + 0.4), (5.0, 4.6, 4.8), m.brood)
        else:
            S.ell((e[0], e[1] - 2.4 + P["lid"], e[2] - 0.2), (5.4, 2.8, 4.8), m.brood, rot=(0, 0, -8 * sx))
    # the sac under her chin; the sucker, a toothed disc in the seam
    S.group(k=1.0)
    sw, sh, sd = P["sac"]
    S.ell((52, P["sac_y"] + sk - rr * 0.4, 16 + sd * 0.3), (sw, sh, sd), m.sac)
    S.torus((52, hy + 6, 22.5 + rr * 0.3), (0, -0.15, 1), 3.4, 1.5, m.flesh)
    S.carve_sphere((52, hy + 6, 23.8 + rr * 0.3), 2.3, k=0.6, mat=m.throat)
    # the spawn: a heaped dome of glossy black eggs on her back, riders curled inside
    rng = np.random.default_rng(11)
    eggs = []
    S.group(k=0.3)
    while len(eggs) < 80:
        u, h = rng.uniform(-1, 1), rng.uniform(0, 1)
        top = 51 + sk - 25 * np.sqrt(max(0.0, 1 - u * u))
        x, y = 52 + u * 33, top + h * (51 + sk - top) * 0.85
        z = -4 - 10 * h + rng.uniform(-3, 3)
        r = rng.uniform(2.4, 4.0)
        S.sphere((x, y, z), r, m.spawn, k=0.3)
        eggs.append((x, y, z, r))

    R = S.render(ss=2)
    R.cleanup()
    warts(R, m.brood, 30, 9, "#5b6440", "#0e120e", box=(6, 54, 98, 90))
    # a faint film over the dead eyes, or the creases of shut ones
    for e, sx in zip(eyes, (-1, 1)):
        ex, ey = int(e[0]) - sx, int(e[1]) + 1
        if P["eyes"] == "shut":
            R.pxs([(ex - 2, ey), (ex - 1, ey + 1), (ex, ey + 1), (ex + 1, ey + 1), (ex + 2, ey)], "#070906")
        else:
            R.px(ex, ey, "#e8e4d4")
    # veins over the pale belly; eggs dark through the sac (more of them, larger, when it swells)
    for pts in [[(36, 82), (40, 85), (44, 84)], [(62, 84), (66, 86), (70, 83)], [(49, 87), (52, 89)]]:
        strand(R, [(x, y + sk) for x, y in pts], "#2a2618", only=(m.pale,))
    rng2 = np.random.default_rng(5)
    cy = P["sac_y"] + sk - rr * 0.4
    for _ in range(int(sw * 1.4)):
        x = int(52 + rng2.uniform(-0.75, 0.75) * sw)
        y = int(cy + rng2.uniform(-0.5, 0.65) * sh)
        if R.on(x, y, m.sac):
            R.px(x, y, "#2a1820")
            if pose == "telegraph" and R.on(x + 1, y, m.sac):
                R.px(x + 1, y, "#2a1820")
    hx = int(hy + 6)
    for x, y in [(50, hx - 1), (54, hx - 1), (51, hx + 1), (53, hx + 1), (50, hx), (54, hx)]:
        if R.on(x, y, m.throat):
            R.px(x, y, "#d8cfb4")
    # pale embryo eyes in the eggs facing you; jelly strings hanging off the mound
    for x, y, z, r in eggs:
        if z > -6 and R.on(int(x), int(y), m.spawn) and (int(x) + int(y)) % 3 == 0:
            R.px(int(x), int(y), EMBRYO)
    for pts in [[(20, 48), (19, 55), (20, 60)], [(84, 47), (86, 53), (85, 58)], [(36, 44), (35, 50)],
                [(70, 43), (71, 49)]]:
        strand(R, [(x, y + sk) for x, y in pts], JELLY)
    return R


# ==============================================================================================
# a spawnling: a hatched rider, a baby Sucker Frog
# ==============================================================================================

SW, SH = 40, 44
SPAWN = {
    "normal": dict(body=(20, 30, 0), rot=(0, 0, -8), squash=1.0, legs="tucked", gape=0.8, tail="curled"),
    "telegraph": dict(body=(20, 25, 2), rot=(-25, 0, 6), squash=1.0, legs="coiled", gape=1.3, tail="up"),
    "hurt": dict(body=(20, 35, 0), rot=(0, 0, 0), squash=0.62, legs="splayed", gape=0.5, tail="flat"),
}


def spawnling(pose):
    P = SPAWN[pose]
    S = sc.Scene(SW, SH)
    horror_light(S)
    m = materials(S)
    bx, by, bz = P["body"]
    q = P["squash"]
    S.group()
    S.ell((20, 42.5, 0), (14, 1.2, 7), m.water)
    S.group()
    # a glossy black bulb of a body, egg-jelly still clinging
    S.ell((bx, by, bz), (9.5 / q ** 0.4, 8.5 * q, 8), m.spawn, rot=P["rot"])
    # the tail: curled round in front, lifted behind it, or flattened out
    if P["tail"] == "curled":
        S.chain([(bx + 6, by + 6, 2), (bx + 11, by + 9, 4), (bx + 9, by + 12, 7), (bx + 4, by + 11, 8)],
                [3.0, 2.2, 1.6, 1.0], m.spawn, k=1.0)
    elif P["tail"] == "up":
        S.chain([(bx + 5, by + 2, -3), (bx + 11, by - 4, -5), (bx + 14, by - 11, -6)],
                [3.0, 2.0, 1.0], m.spawn, k=1.0)
    else:
        S.chain([(bx + 7, by + 3, 0), (bx + 14, by + 5, 1), (bx + 18, by + 5, 2)], [2.6, 1.8, 1.0], m.spawn, k=1.0)
    # budding frog legs, pale and new
    if P["legs"] == "coiled":
        legs = [((bx - 6, by + 5, 3), (bx - 9, by + 12, 6), (bx - 6, by + 15, 9)),
                ((bx + 4, by + 6, 3), (bx + 8, by + 12, 6), (bx + 6, by + 15, 9))]
    elif P["legs"] == "splayed":
        legs = [((bx - 7, by + 2, 2), (bx - 13, by + 5, 4), (bx - 16, by + 7, 5)),
                ((bx + 6, by + 2, 2), (bx + 12, by + 5, 4), (bx + 15, by + 7, 5))]
    else:
        legs = [((bx - 5, by + 6, 3), (bx - 8, by + 10, 5), (bx - 5, by + 12, 7)),
                ((bx + 3, by + 7, 3), (bx + 6, by + 11, 5), (bx + 3, by + 12.5, 7))]
    for a, b, c in legs:
        S.chain([a, b, c], [1.8, 1.4, 1.1], m.pale, k=0.8)
    # one big pale embryo eye on top, and a tiny pink sucker at the front
    face = np.array([0.0, -0.25 if P["tail"] != "up" else -0.45, 1.0])
    face /= np.linalg.norm(face)
    eye = (bx - 1.5, by - 6.5 * q, bz + 4.5)
    S.group(k=0.5)
    S.sphere(eye, 2.7, m.milk)
    S.group(k=0.8)
    mouth = np.array([bx, by + 1.5 * q, bz]) + face * 8.2
    S.torus(tuple(mouth), tuple(face), 2.2 * P["gape"], 1.1, m.flesh)
    S.carve_sphere(tuple(mouth + face * 0.9), 1.5 * P["gape"], k=0.4, mat=m.throat)
    R = S.render(ss=2)
    R.cleanup()
    ex, ey = int(np.floor(eye[0])), int(np.floor(eye[1]))
    R.px(ex, ey, "#0a0604")
    R.px(ex - 1, ey - 1, "#f0eee4")
    for pts in [[(bx - 8, by - 2), (bx - 9, by + 3)], [(bx + 7, by - 4), (bx + 9, by)]]:
        strand(R, [(int(x), int(y)) for x, y in pts], JELLY)
    return R


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
    root = args[0] if args else "art/monsters"
    extra = root if args else "art/concepts"
    out = {}
    for name, fn, poses in [("brood", brood, BROOD), ("spawnling", spawnling, SPAWN)]:
        os.makedirs(os.path.join(root, name), exist_ok=True)
        for k in poses:
            img = fn(k).to_rgba()
            out[(name, k)] = img
            sc.save(img, os.path.join(root, name, f"{k}.png"))
            if "--zoom" in sys.argv:
                sc.save(img, os.path.join(extra, f"{name}_{k}_x6.png"), 6)
            print("wrote", os.path.join(root, name, f"{k}.png"))
    bg = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_bg.png")).convert("RGBA")
    scenes = [formation([out[("brood", "normal")]], bg),
              formation([out[("brood", "telegraph")]], bg),
              formation([out[("spawnling", "telegraph")], out[("brood", "normal")], out[("spawnling", "normal")]], bg)]
    labels = [("normal", "squatting, the sac slack"), ("telegraph", "the hatch: the sac swells"),
              ("with spawnlings", "boss 104 + two 40s: one coiled to climb")]
    path = os.path.join(extra, "brood_poses.png")
    sheet(scenes, labels, path)
    print("sheet:", path)
