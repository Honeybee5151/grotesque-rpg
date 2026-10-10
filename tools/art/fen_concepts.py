"""The Sallow Fen bestiary: three concepts for Miles to pick from (world's region 1 - a mouth that
sucks, dread). Each teaches a different answer to its telegraph:

  A  The Mouther     a bog body whose jaw works with no sound; it inhales, then drinks your breath (MP).
                     Answer: Crush it mid-inhale and it chokes. (The Host teaches Guard.)
  B  Penny Leeches   a pack of three with wished-for coins grown into their skin; they sway in unison,
                     then all latch at once. Answer: thin the pack before the chorus.
  C  The Brood       the spawn-mother of the flooded caves, her back a raft of rider spawn; her back
                     heaves, then spawnlings drop in. Answer: priority.

    python tools/art/fen_concepts.py [OUTDIR] [a b c]     # default art/concepts -> fen_options.png
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import sculpt as sc
from host_concepts import PAL as HOST_PAL, horror_light, M, warts, strand, sheet
from host import Frame, fell, fingers, add

PAL = dict(HOST_PAL)
PAL.update({
    "peat":   dict(ramp=["#180e08", "#2e1c10", "#4c321c", "#6e4c2a", "#957044"], outline="#0c0604",
                   spec="#d8bc88", shin=18.0, spec_thr=0.62),
    "coat":   dict(ramp=["#0c0e0c", "#171b16", "#232922", "#323a30", "#465042"], outline="#060706"),
    "reed":   dict(ramp=["#26200e", "#463c1c", "#6a5e2e", "#918244", "#b4a460"], outline="#120e06"),
    "throat": dict(ramp=["#10060c", "#1c0a13", "#2b0e1b", "#3f1424", "#5a1c30"], outline="#0a0408"),
    "water":  dict(ramp=["#05060a", "#0a0c12", "#10141c", "#1a2232", "#2a3650"], outline="#030305",
                   spec="#9ab4cc", shin=40.0, spec_thr=0.35),
    "leech":  dict(ramp=["#0c0c0a", "#1a1914", "#2b2920", "#433f30", "#625b44"], outline="#060605",
                   spec="#c8c2a0", shin=26.0, spec_thr=0.45),
    "copper": dict(ramp=["#2a1307", "#5c2e0e", "#91531c", "#c27e30", "#e8b05c"], outline="#140902",
                   spec="#fff0c0", shin=30.0, spec_thr=0.5),
    "scarf":  dict(ramp=["#1c0c08", "#36180f", "#542818", "#723c24", "#8e5434"], outline="#0e0604"),
    "brood":  dict(ramp=["#0e120e", "#1a2118", "#2a3424", "#3f4a30", "#5b6440"], outline="#070906",
                   spec="#b8c08c", shin=22.0, spec_thr=0.55),
    "milk":   dict(ramp=["#2e2e2a", "#4e4c46", "#74726a", "#9e9a8e", "#c8c4b4"], outline="#121210",
                   spec="#f0eee4", shin=30.0, spec_thr=0.5),
    "sac":    dict(ramp=["#3a1c26", "#5e3040", "#86505e", "#ae7882", "#d0a4a8"], outline="#1a0c10",
                   spec="#f4dcdc", shin=24.0, spec_thr=0.5),
    "spawn":  dict(ramp=["#050608", "#0c0e12", "#151a20", "#232a32", "#36404a"], outline="#020203",
                   spec="#e4eef4", shin=36.0, spec_thr=0.42),
})
NAMES = ["peat", "coat", "reed", "throat", "water", "leech", "copper", "spawn", "scarf", "brood", "milk", "sac",
         "frog", "belly", "flesh", "eye", "bone"]


def materials(S):
    m = M()
    for name in NAMES:
        setattr(m, name, S.mat(name, **PAL[name]))
    return m


# ==============================================================================================
# A - The Mouther: a bog body, jaw working with no sound
# ==============================================================================================

def mouther():
    S = sc.Scene(96, 118)
    horror_light(S)
    m = materials(S)

    # standing in its own puddle of fen water
    S.group()
    S.ell((48, 115.5, 0), (26, 1.4, 11), m.water)

    S.group()
    # the coat's back hangs behind everything: a ragged dark shape around the thin body
    S.ell((48, 62, -6), (15, 27, 4), m.coat, k=2.0, rot=(0, 0, -4))
    # legs: pressed crooked by the peat - knock-kneed, one foot turned in, knobs for knees
    S.cone((44, 72, 0), (41, 92, 2), 3.0, 2.5, m.peat, k=1.0)
    S.sphere((41, 92, 3), 3.0, m.peat, k=1.0)
    S.cone((41, 92, 3), (42, 112, 1), 2.5, 2.0, m.peat, k=0.8)
    S.ell((41, 114, 3), (3.6, 1.8, 4.6), m.peat, k=0.8, rot=(0, 0, 12))
    S.cone((53, 72, 0), (51.5, 91, 4), 3.0, 2.5, m.peat, k=1.0)
    S.sphere((51.5, 91, 5), 3.0, m.peat, k=1.0)
    S.cone((51.5, 91, 5), (58, 112, 1), 2.5, 2.0, m.peat, k=0.8)
    S.ell((59.5, 114, 3), (3.6, 1.8, 4.6), m.peat, k=0.8, rot=(0, 0, -30))
    # a starved torso, twisted: ribs under leather, belly sucked in under them
    S.ell((48, 71, 0), (6.5, 3.5, 5), m.peat, k=1.5)
    S.ell((47, 51, 0), (8, 12, 6), m.peat, k=2.0, rot=(0, 0, -7))
    S.carve_ell((48, 64, 6.8), (6, 5, 3.4), k=2.0)
    for i in range(5):
        S.carve_ell((47.5 - i * 0.3, 44 + i * 3.2, 6.6), (7.5, 0.7, 1.6), k=0.4, rot=(0, 0, -7))
    # shoulders: his right hiked up, his left dropped
    S.sphere((37, 38.5, 0), 4.8, m.coat, k=2.0)
    S.sphere((59, 43, 0), 4.8, m.coat, k=2.0)
    S.ell((36.5, 63, 2.5), (4, 23, 5), m.coat, k=2.0, rot=(0, 0, 3))
    S.ell((60, 66, 2.5), (4, 21, 5), m.coat, k=2.0, rot=(0, 0, -5))
    # his right arm hangs straight, far too long; his left is bent, the hand dangling off the wrist
    S.cone((36, 39.5, 0), (31, 63, 2), 3.0, 2.5, m.coat, k=1.5)
    S.cone((31, 63, 2), (28.5, 86, 4), 2.2, 1.8, m.peat, k=0.8)
    S.ell((28, 90, 4.5), (2.5, 3.4, 1.8), m.peat, k=0.8)
    fingers(S, m.peat, [((27, 92, 4.5), (26, 99.5, 5)), ((28.5, 93, 5), (28.5, 101, 5.5)),
                        ((30, 92, 4.5), (31, 99, 5))], 0.8, 0.6)
    S.cone((60, 44, 0), (65, 60, 4), 3.0, 2.5, m.coat, k=1.5)
    S.cone((65, 60, 4), (58, 70, 11), 2.2, 1.8, m.peat, k=0.8)
    S.ell((56.5, 73, 11.5), (2.4, 3.2, 1.8), m.peat, k=0.8, rot=(0, 0, 25))
    fingers(S, m.peat, [((55.5, 75, 11.5), (53.5, 81, 12)), ((57, 75.5, 12), (56, 82.5, 12.5)),
                        ((58.5, 75, 11.5), (58.5, 81, 12))], 0.8, 0.6)
    # neck: a cord of tendons jutting forward
    S.cone((48, 38, 1), (47, 28, 4), 2.8, 3.0, m.peat, k=1.2)

    # the head, lolled and pressed flat on one side; the jaw hangs far below where a jaw should be
    F = Frame((46.5, 17, 5), (10, 0, 13))
    fell(S, F, (0, 0, 0), (9, 10.4, 9), m.peat, k=1.2)
    S.carve_sphere(F.p((-9.5, -5.5, 0)), 4.2, k=1.5)
    fell(S, F, (0, 19, 2.5), (5, 2.8, 4.8), m.peat, k=1.5)
    for sx in (-1, 1):
        S.cone(F.p((6.0 * sx, 3.5, 1.5)), F.p((4.4 * sx, 18.5, 2.5)), 1.6, 1.4, m.peat, k=1.2)
        S.carve_sphere(F.p((3.2 * sx, -1.0, 8.0)), 2.4, k=0.8)
    fell(S, F, (0, 10.2, 7.2), (3.6, 9.2, 5.0), m.throat, k=0.8, carve=True)
    # a rotted scarf, slipped down off the mouth it once covered
    S.group(k=0.6)
    S.torus((47.6, 36.5, 2.5), (0, 1, 0.2), 4.6, 1.5, m.scarf, k=0.5)
    S.cone((43.5, 37.5, 6.5), (41.5, 49, 8), 2.0, 1.4, m.scarf, k=0.8)

    R = S.render(ss=2)
    R.cleanup()
    # milky eyes in the sockets, a collapsed nose
    for sx in (-1, 1):
        ex, ey = F.xy((3.2 * sx, -0.7, 9.9))
        R.px(ex, ey, "#8d8a7c")
    R.pxs([F.xy((-0.4, 3.0, 9.9)), F.xy((0.6, 3.0, 9.9))], "#0c0604")
    # the inside of the mouth: wet pink gums at the rim, a tongue far down in the dark
    for t in np.linspace(0, 2 * np.pi, 22, endpoint=False):
        x, y = F.xy((3.5 * np.sin(t), 10.2 + 9.3 * np.cos(t), 7.4))
        if R.on(x, y, m.throat):
            R.px(x, y, "#9c2646" if np.cos(t) > -0.2 else "#681430")
    tx, ty = F.xy((0.3, 16.5, 6.0))
    R.pxs([(tx, ty), (tx + 1, ty)], "#cc4862")
    # ribs under the leather, creases in it; reeds tangled in the scarf; hair plastered to the skull
    for pts in [[(41, 92), (43, 94)], [(51, 90), (53, 92)], [(43, 100), (42, 104)], [(55, 101), (57, 105)]]:
        strand(R, pts, "#2e1c10", only=(m.peat,))
    strand(R, [(51, 37), (53, 43), (52, 49)], "#918244")
    strand(R, [(45, 39), (44, 45)], "#6a5e2e")
    for v, length, sway in [((-6.5, -4, 2), 9, -1), ((5.5, -6, 2.5), 12, 1), ((-2.5, -8, 4), 6, 0)]:
        hx, hy = F.xy(v)
        strand(R, [(hx, hy), (hx + sway, hy + length)], "#0c0806")
    # a ragged coat hem; fen water dripping off its fingers into the puddle
    for x in range(33, 64):
        if R.on(x, 86, m.coat) and (x * 7) % 5 < 2:
            R.px(x, 86, "#060706")
    R.pxs([(26, 103), (26, 107), (55, 85), (55, 89)], "#2a3650")
    return R


# ==============================================================================================
# B - Penny Leeches: a pack of three, the wished-for coins grown into their skin
# ==============================================================================================

LEECHES = [
    # spine points (base to head), sucker facing, coin positions (t along the spine, sideways offset)
    dict(spine=[(22, 59, 0), (17, 50, 3), (19, 40, 5), (25, 30, 5), (24, 20, 6.5)],
         head=(23.5, 14, 8), face=(0, -0.5, 0.86), coins=[(0.18, 3), (0.42, -3), (0.6, 2), (0.78, -1)]),
    dict(spine=[(24, 59, 0), (29, 51, 3), (28, 43, 5), (22, 37, 6), (16, 32, 6.5)],
         head=(13.5, 27.5, 8), face=(-0.45, -0.3, 0.84), coins=[(0.2, -3), (0.45, 2), (0.7, 1)]),
    dict(spine=[(20, 59, 0), (15, 51, 3), (17, 42, 5), (23, 35, 5.5), (28, 27, 6.5)],
         head=(30.5, 21.5, 8), face=(0.4, -0.4, 0.82), coins=[(0.15, 2), (0.38, -2), (0.62, 3), (0.8, -1)]),
]


def lerp3(pts, t):
    """Point and segment index at t (0..1) along a polyline."""
    n = len(pts) - 1
    i = min(int(t * n), n - 1)
    f = t * n - i
    a, b = np.array(pts[i], float), np.array(pts[i + 1], float)
    return a + (b - a) * f, i


def leech(spec):
    S = sc.Scene(44, 66)
    horror_light(S)
    m = materials(S)
    radii = [8.5, 8.0, 7.0, 6.0, 5.2]
    S.group()
    S.ell((22, 61, 0), (13, 4.2, 9), m.leech)
    S.chain(spec["spine"], radii, m.leech, k=1.5)
    S.ell(spec["head"], (5.8, 5.0, 5.4), m.leech, k=2.0)
    # swallowed pennies, grown into the skin
    S.group(k=0.4)
    for t, dx in spec["coins"]:
        p, i = lerp3(spec["spine"], t)
        r = radii[i] + (radii[i + 1] - radii[i]) * (t * 4 - i)
        S.ell((p[0] + dx, p[1], p[2] + r * 0.98), (2.9, 2.9, 1.1), m.copper, rot=(dx * 4, 0, dx * 8))
    # the sucker: a ring of pink lip, dark inside
    face = np.array(spec["face"], float)
    face /= np.linalg.norm(face)
    mouth = np.array(spec["head"], float) + face * 4.6
    S.group(k=1.0)
    S.torus(tuple(mouth), tuple(face), 3.2, 1.5, m.flesh)
    S.carve_sphere(tuple(mouth + face * 1.2), 2.3, k=0.6, mat=m.throat)
    R = S.render(ss=2)
    R.cleanup()
    # annuli: dark rings across the body; tiny pale teeth around the sucker's rim
    for y in range(4, 57):
        if y % 4:
            continue
        for x in range(1, 43):
            if R.on(x, y, m.leech) and R.code[y, x] % 8 in (2, 3):
                R.px(x, y, PAL["leech"]["ramp"][1])
    for a in np.linspace(0, 2 * np.pi, 8, endpoint=False):
        side = np.cross(face, [0, 0, 1.0])
        side = side / (np.linalg.norm(side) or 1) if np.linalg.norm(side) > 1e-6 else np.array([1.0, 0, 0])
        up = np.cross(side, face)
        p = mouth + face * 0.8 + (side * np.cos(a) + up * np.sin(a)) * 2.0
        x, y = int(np.floor(p[0])), int(np.floor(p[1]))
        if R.on(x, y, m.throat):
            R.px(x, y, "#d8cfb4")
    return R


def penny_leeches():
    return [leech(s) for s in LEECHES]


# ==============================================================================================
# C - The Brood: the spawn-mother under the well, her back a raft of rider spawn
# ==============================================================================================

def brood():
    S = sc.Scene(104, 92)
    horror_light(S)
    m = materials(S)
    S.group()
    S.ell((52, 89, 0), (49, 1.8, 16), m.water)

    S.group()
    # a bloated body squatting in the pool, haunches folded at her sides
    S.ell((52, 66, -6), (36, 20, 24), m.brood, k=0)
    S.ell((52, 75, 9), (26, 10, 11), m.belly, k=2.0)
    S.ell((16, 73, -6), (10, 12, 10), m.brood, k=2.0, rot=(0, 0, -12))
    S.ell((88, 73, -6), (10, 12, 10), m.brood, k=2.0, rot=(0, 0, 12))
    for sx in (-1, 1):
        a, b = (52 + 20 * sx, 72, 10), (52 + 27 * sx, 86, 14)
        S.cone(a, b, 6, 4.5, m.brood, k=1.5)
        for dx in (-3.5, 0, 3.5):
            S.cone(b, (b[0] + dx * 1.4 + 2 * sx, 89, 17), 1.6, 1.2, m.brood, k=0.6)
    # a wide flat head, mouth a long seam; dead milky eyes
    S.ell((52, 55, 10), (25, 10.5, 13), m.brood, k=3.0)
    S.carve_ell((52, 60, 22.5), (21, 0.9, 4), k=0.4, mat=m.throat)
    S.group(k=0.6)
    for sx in (-1, 1):
        S.sphere((52 + 15 * sx, 45, 15.5), 4.4, m.milk)
    S.group(k=0.8)
    for sx in (-1, 1):
        S.ell((52 + 15 * sx, 42.6, 15.3), (5.4, 2.8, 4.8), m.brood, rot=(0, 0, -8 * sx))
    # under the chin a pale sac, full of more of them; the sucker a toothed disc in the seam
    S.group(k=1.0)
    S.ell((52, 69, 18), (10, 6, 6.5), m.sac)
    S.torus((52, 61, 22.5), (0, -0.15, 1), 3.4, 1.5, m.flesh)
    S.carve_sphere((52, 61, 23.8), 2.3, k=0.6, mat=m.throat)
    # the spawn: a heaped dome of glossy black eggs on her back, riders curled inside
    rng = np.random.default_rng(11)
    eggs = []
    S.group(k=0.3)
    while len(eggs) < 80:
        u, h = rng.uniform(-1, 1), rng.uniform(0, 1)
        top = 47 - 25 * np.sqrt(max(0.0, 1 - u * u))
        x, y = 52 + u * 33, top + h * (47 - top) * 0.85
        z = -4 - 10 * h + rng.uniform(-3, 3)
        r = rng.uniform(2.4, 4.0)
        S.sphere((x, y, z), r, m.spawn, k=0.3)
        eggs.append((x, y, z, r))

    R = S.render(ss=2)
    R.cleanup()
    warts(R, m.brood, 30, 9, "#5b6440", "#0e120e", box=(6, 50, 98, 86))
    # a faint pupil-less film over the eyes; eggs seen through the sac; teeth in the sucker
    for sx in (-1, 1):
        R.px(52 + 15 * sx - sx, 46, "#e8e4d4")
    for x, y in [(47, 68), (50, 70), (54, 68), (57, 70), (52, 72), (45, 71), (59, 72)]:
        if R.on(x, y, m.sac):
            R.px(x, y, "#2a1820")
    for x, y in [(50, 60), (54, 60), (51, 62), (53, 62), (50, 61), (54, 61)]:
        if R.on(x, y, m.throat):
            R.px(x, y, "#d8cfb4")
    # pale embryo eyes in the eggs facing you; jelly strings hanging off the mound
    for x, y, z, r in eggs:
        if z > -6 and R.on(int(x), int(y), m.spawn) and (int(x) + int(y)) % 3 == 0:
            R.px(int(x), int(y), "#b9c4b0")
    for pts in [[(20, 44), (19, 51), (20, 56)], [(84, 43), (86, 49), (85, 54)], [(36, 40), (35, 46)],
                [(70, 39), (71, 45)]]:
        strand(R, pts, "#5a6670")
    return R


CONCEPTS = {"a": mouther, "b": penny_leeches, "c": brood}
LABELS = {"a": ("A  -  The Mouther", "a bog body; inhales, then drinks your breath"),
          "b": ("B  -  Penny Leeches", "a pack; they sway in unison, then all latch"),
          "c": ("C  -  The Brood", "the boss under the well; her spawn drop in")}


def compose(img, bg, pos):
    canvas = bg.copy()
    canvas.alpha_composite(Image.fromarray(img, "RGBA"), pos)
    return canvas


def place(imgs, bg):
    """Stand a formation the way the battle does: canvases 4px apart, centred on x=160, bottoms on y=122."""
    total = sum(i.shape[1] for i in imgs) + 4 * (len(imgs) - 1)
    x = 160 - total // 2
    canvas = bg.copy()
    for i in imgs:
        canvas.alpha_composite(Image.fromarray(i, "RGBA"), (x, 122 - i.shape[0]))
        x += i.shape[1] + 4
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
            sc.save(img, os.path.join(out, f"fen_{k}{j if len(imgs) > 1 else ''}_x6.png"), 6)
        scenes.append(place(imgs, bg))
        print("rendered", k)
    sheet(scenes, [LABELS[k] for k in which], os.path.join(out, "fen_options.png"))
    print("sheet:", os.path.join(out, "fen_options.png"))
