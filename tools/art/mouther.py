"""The Mouther (enemy `mouther`): a bog body from the drowned boardwalk north of Hollowell.

Peat-tanned and pressed crooked by the bog, a rotted scarf slipped down off the mouth it once
covered; its jaw hangs far too low and works with no sound. The fen kept its voice - what Hollowell
thinks happened to the hero. Focal accent: the wet pink inside of the mouth.

Poses (96x118, one canvas and ground line):
  normal     crooked, slack, the jaw working.
  telegraph  the inhale: head tipped back, jaw dropped further, arms spread to take the air in, the
             scarf's loose end streaming up toward the mouth along the draught.
  stunned    choking (a Crush broke the inhale): knees buckled, head pitched forward, both hands at
             its throat, fen water dribbling from its jaw.
  hurt       a flinch: the head snapped aside, an arm jerked up.

    python tools/art/mouther.py [OUTDIR] [poses...] [--zoom]

Writes <pose>.png at 1x to OUTDIR (default art/monsters/mouther) and a labelled sheet to
art/concepts/mouther_poses.png.
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import sculpt as sc
from host_concepts import PAL as HOST_PAL, horror_light, M, strand, sheet, compose
from host import Frame, fell, fingers, add

W, H = 96, 118

PAL = dict(HOST_PAL)
PAL.update({
    "peat":   dict(ramp=["#180e08", "#2e1c10", "#4c321c", "#6e4c2a", "#957044"], outline="#0c0604",
                   spec="#d8bc88", shin=18.0, spec_thr=0.78),
    "coat":   dict(ramp=["#0c0e0c", "#171b16", "#232922", "#323a30", "#465042"], outline="#060706"),
    "throat": dict(ramp=["#10060c", "#1c0a13", "#2b0e1b", "#3f1424", "#5a1c30"], outline="#0a0408"),
    "water":  dict(ramp=["#05060a", "#0a0c12", "#10141c", "#1a2232", "#2a3650"], outline="#030305",
                   spec="#9ab4cc", shin=40.0, spec_thr=0.35),
    "scarf":  dict(ramp=["#1c0c08", "#36180f", "#542818", "#723c24", "#8e5434"], outline="#0e0604"),
})


def materials(S):
    m = M()
    for name in ["peat", "coat", "throat", "water", "scarf"]:
        setattr(m, name, S.mat(name, **PAL[name]))
    return m


def up(p, d):
    return (p[0], p[1] - d, p[2])


# lift: whole upper body up (+) or down (-); chest: ribcage scale; head: frame; jaw/mouth: how far
# the jaw hangs and how wide the hole is; arms/legs/scarf: named variants
POSES = {
    "normal": dict(lift=0, chest=1.0, head=((46.5, 17, 5), (10, 0, 13)), jaw=19, mouth=(3.6, 9.2),
                   arms="slack", legs="crooked", scarf="hang"),
    "telegraph": dict(lift=3, chest=1.18, head=((47, 14, 3), (34, 0, 4)), jaw=23, mouth=(4.6, 11.4),
                      arms="spread", legs="crooked", scarf="sucked"),
    "stunned": dict(lift=-7, chest=0.92, head=((45, 30, 9), (-34, 0, -12)), jaw=14, mouth=(2.6, 5.5),
                    arms="throat", legs="buckled", scarf="hang"),
    "hurt": dict(lift=-1, chest=1.0, head=((44.5, 18, 4), (6, 0, -26)), jaw=17, mouth=(3.2, 8.0),
                 arms="jerk", legs="crooked", scarf="hang"),
}
LABELS = {"normal": ("normal", "crooked, slack, the jaw working"),
          "telegraph": ("telegraph", "the inhale: it draws the air in"),
          "stunned": ("stunned", "choking on its own breath"),
          "hurt": ("hurt", "a flinch")}


def build(pose):
    P = POSES[pose]
    L = P["lift"]
    S = sc.Scene(W, H)
    horror_light(S)
    m = materials(S)

    S.group()
    S.ell((48, 115.5, 0), (26, 1.4, 11), m.water)

    S.group()
    # the coat's back, a ragged dark shape behind the thin body
    S.ell(up((48, 62, -6), L), (15, 27 - max(0, -L) * 0.6, 4), m.coat, k=2.0, rot=(0, 0, -4))
    # legs: pressed crooked by the peat (knock-kneed, a foot turned in), or buckled
    hipL, hipR = up((44, 72, 0), L), up((53, 72, 0), L)
    if P["legs"] == "buckled":
        kneeL, kneeR = (39, 97, 8), (54, 98, 9)
    else:
        kneeL, kneeR = up((41, 92, 3), L * 0.5), up((51.5, 91, 5), L * 0.5)
    for hip, knee, ankle, foot, rz in [(hipL, kneeL, (42, 112, 1), (41, 114, 3), 12),
                                       (hipR, kneeR, (58, 112, 1), (59.5, 114, 3), -30)]:
        S.cone(hip, knee, 3.0, 2.5, m.peat, k=1.0)
        S.sphere(knee, 3.0, m.peat, k=1.0)
        S.cone(knee, ankle, 2.5, 2.0, m.peat, k=0.8)
        S.ell(foot, (3.6, 1.8, 4.6), m.peat, k=0.8, rot=(0, 0, rz))
    # a starved torso, twisted: a narrow carved cage over a belly sucked in under it
    c = P["chest"]
    S.ell(up((48, 71, 0), L), (6.5, 3.5, 5), m.peat, k=1.5)
    S.ell(up((47, 51, 0), L), (8 * c, 12 * (0.5 + c * 0.5), 6 * c), m.peat, k=2.0, rot=(0, 0, -7))
    S.carve_ell(up((48, 64, 6.8 * c), L), (6, 5, 3.4), k=2.0)
    for i in range(5):
        S.carve_ell(up((47.5 - i * 0.3, 44 + i * 3.2, 6.6 * c), L), (7.5 * c, 0.7, 1.6), k=0.4, rot=(0, 0, -7))
    # shoulders: his right hiked up, his left dropped
    shR, shL = up((37, 38.5, 0), L + (3 if P["arms"] == "spread" else 0)), up((59, 43, 0), L)
    S.sphere(shR, 4.8, m.coat, k=2.0)
    S.sphere(shL, 4.8, m.coat, k=2.0)
    S.ell(up((36.5, 63, 2.5), L), (4, 23 + min(L, 0) * 0.5, 5), m.coat, k=2.0, rot=(0, 0, 3))
    S.ell(up((60, 66, 2.5), L), (4, 21 + min(L, 0) * 0.5, 5), m.coat, k=2.0, rot=(0, 0, -5))

    F = Frame(*P["head"])
    arms(S, m, P["arms"], shR, shL, F)
    # neck: a cord of tendons into the head
    S.cone(up((48, 38, 1), L), F.p((0, 6, -5)), 2.8, 3.0, m.peat, k=1.2)
    # the head, pressed flat on one side; the jaw hangs far below where a jaw should be
    jaw, (mw, mh) = P["jaw"], P["mouth"]
    fell(S, F, (0, 0, 0), (9, 10.4, 9), m.peat, k=1.2)
    S.carve_sphere(F.p((-9.5, -5.5, 0)), 4.2, k=1.5)
    fell(S, F, (0, jaw, 2.5), (5, 2.8, 4.8), m.peat, k=1.5)
    for sx in (-1, 1):
        S.cone(F.p((6.0 * sx, 3.5, 1.5)), F.p((4.4 * sx, jaw - 0.5, 2.5)), 1.6, 1.4, m.peat, k=1.2)
        S.carve_sphere(F.p((3.2 * sx, -1.0, 8.0)), 2.4, k=0.8)
    mid = 1.0 + (jaw - 1.0) * 0.5
    fell(S, F, (0, mid, 7.2), (mw, mh, 5.0), m.throat, k=0.8, carve=True)
    # the rotted scarf: around the neck, its loose end hanging - or drawn up toward the mouth
    S.group(k=0.6)
    neck = up((47.6, 36.5, 2.5), L)
    S.torus(neck, (0, 1, 0.2), 4.6, 1.5, m.scarf, k=0.5)
    end0 = add(neck, (-4, 1, 4))
    if P["scarf"] == "sucked":
        tip = F.p((-mw * 0.6, mid + mh * 0.2, 10.0))
        S.chain([end0, add(end0, (-9, -3, 6)), add(end0, (-8, -12, 9)), tip], [2.0, 1.8, 1.5, 1.1], m.scarf, k=0.8)
    else:
        S.cone(end0, add(end0, (-2, 11.5, 1.5)), 2.0, 1.4, m.scarf, k=0.8)

    R = S.render(ss=2)
    R.cleanup()
    details(R, m, P, F, L, pose)
    return R


def arms(S, m, kind, shR, shL, F):
    """His right arm hangs from shR (screen left), his left from shL."""
    def hand(at, rot, tips):
        S.ell(at, (2.5, 3.4, 1.8), m.peat, k=0.8, rot=rot)
        fingers(S, m.peat, [(add(at, a), add(at, b)) for a, b in tips], 0.8, 0.6)

    down = [((-1, 2, 0), (-2, 9.5, 0.5)), ((0.5, 3, 0.5), (0.5, 11, 1)), ((2, 2, 0), (3, 9, 0.5))]
    if kind == "slack":
        S.cone(shR, (31, 63, 2), 3.0, 2.5, m.coat, k=1.5)
        S.cone((31, 63, 2), (28.5, 86, 4), 2.2, 1.8, m.peat, k=0.8)
        hand((28, 90, 4.5), (0, 0, 0), down)
        S.cone(shL, (65, 60, 4), 3.0, 2.5, m.coat, k=1.5)
        S.cone((65, 60, 4), (58, 70, 11), 2.2, 1.8, m.peat, k=0.8)
        hand((56.5, 73, 11.5), (0, 0, 25), [((-1, 2, 0), (-3, 8, 0.5)), ((0.5, 2.5, 0.5), (-0.5, 9.5, 1)),
                                            ((2, 2, 0), (2, 8, 0.5))])
    elif kind == "spread":
        # arms lifted away from the body, hands open, taking the air in
        S.cone(shR, (24, 48, 3), 3.0, 2.5, m.coat, k=1.5)
        S.cone((24, 48, 3), (13, 58, 6), 2.2, 1.8, m.peat, k=0.8)
        hand((10.5, 60, 6.5), (0, 0, 55), [((-2, 1, 0), (-7, 3, 0.5)), ((-1.5, 2.5, 0.5), (-6.5, 7, 1)),
                                           ((0, 3, 0), (-3, 9, 0.5))])
        S.cone(shL, (71, 52, 3), 3.0, 2.5, m.coat, k=1.5)
        S.cone((71, 52, 3), (82, 62, 6), 2.2, 1.8, m.peat, k=0.8)
        hand((84.5, 64, 6.5), (0, 0, -55), [((2, 1, 0), (7, 3, 0.5)), ((1.5, 2.5, 0.5), (6.5, 7, 1)),
                                            ((0, 3, 0), (3, 9, 0.5))])
    elif kind == "throat":
        # both hands clutching its throat, elbows out
        throat = F.p((0, 8, -4))
        for sh, elbow, side in [(shR, (30, 50, 6), -1), (shL, (66, 52, 6), 1)]:
            S.cone(sh, elbow, 3.0, 2.5, m.coat, k=1.5)
            wrist = add(throat, (7 * side, 3, 6))
            S.cone(elbow, wrist, 2.2, 1.8, m.peat, k=0.8)
            S.ell(add(wrist, (-2.5 * side, -1, 1)), (2.6, 2.4, 1.8), m.peat, k=0.8)
            fingers(S, m.peat, [(add(wrist, (-2 * side, -2 + j * 1.6, 1.5)), add(wrist, (-6 * side, -3 + j * 1.8, 2)))
                                for j in range(3)], 0.75, 0.6)
    else:
        # hurt: his right arm jerked up and out, the left flung back
        S.cone(shR, (24, 32, 4), 3.0, 2.5, m.coat, k=1.5)
        S.cone((24, 32, 4), (18, 18, 6), 2.2, 1.8, m.peat, k=0.8)
        hand((16.5, 14.5, 6.5), (0, 0, 160), [((-1, -2, 0), (-2, -8, 0.5)), ((0.5, -3, 0.5), (0.5, -9.5, 1)),
                                              ((2, -2, 0), (3, -8, 0.5))])
        S.cone(shL, (67, 62, -1), 3.0, 2.5, m.coat, k=1.5)
        S.cone((67, 62, -1), (72, 82, 1), 2.2, 1.8, m.peat, k=0.8)
        hand((73, 86, 1.5), (0, 0, -10), down)


def details(R, m, P, F, L, pose):
    jaw, (mw, mh) = P["jaw"], P["mouth"]
    mid = 1.0 + (jaw - 1.0) * 0.5
    # milky eyes in the sockets (squeezed shut when it chokes), a collapsed nose
    for sx in (-1, 1):
        ex, ey = F.xy((3.2 * sx, -0.7, 9.9))
        if pose == "stunned":
            R.pxs([(ex - 1, ey), (ex, ey + 1), (ex + 1, ey)], "#180e08")
        else:
            R.px(ex, ey, "#8d8a7c")
    R.pxs([F.xy((-0.4, 3.0, 9.9)), F.xy((0.6, 3.0, 9.9))], "#0c0604")
    # the inside of the mouth: wet pink gums at the rim, a tongue far down in the dark
    for t in np.linspace(0, 2 * np.pi, 26, endpoint=False):
        x, y = F.xy(((mw - 0.1) * np.sin(t), mid + (mh + 0.1) * np.cos(t), 7.4))
        if R.on(x, y, m.throat):
            R.px(x, y, "#9c2646" if np.cos(t) > -0.2 else "#681430")
    tx, ty = F.xy((0.3, mid + mh * 0.68, 6.0))
    R.pxs([(tx, ty), (tx + 1, ty)], "#cc4862")
    if pose == "telegraph":
        # the cheeks split at the corners; the draught curling into the mouth from both sides
        for sx in (-1, 1):
            strand(R, [F.xy((mw * sx, mid - mh * 0.2, 6.6)), F.xy(((mw + 2.2) * sx, mid - mh * 0.45, 5.6))],
                   "#180e08", only=(m.peat,))
        # wisps of fen air rising from below and streaming into the open mouth
        mx, my = F.xy((0, mid - mh * 0.3, 9))
        for sx in (-1, 1):
            for (x0, y0, bend) in [(30, 44, 10), (22, 30, 7), (14, 18, 5)]:
                pts = []
                for j in range(12):
                    a = j / 11.0
                    x = mx + sx * x0 * (1 - a) ** 1.3
                    y = my + y0 * (1 - a) - bend * np.sin(np.pi * a)
                    pts.append((x, y))
                for j, ((xa, ya), (xb, yb)) in enumerate(zip(pts[:-1], pts[1:])):
                    if j % 3 != 2:
                        strand(R, [(round(xa), round(ya)), (round(xb), round(yb))],
                               "#6a7a90" if j >= 7 else "#3b4658")
    if pose == "stunned":
        # choking: fen water dribbling from its jaw down onto its hands
        jx, jy = F.xy((0.5, jaw + 2.0, 4))
        strand(R, [(jx, jy), (jx, jy + 5), (jx + 1, jy + 10)], "#1a2232")
        R.px(jx + 1, jy + 12, "#2a3650")
    # creases in the leather of the legs; reeds tangled in the scarf; hair plastered to the skull
    for pts in [[(43, 100), (42, 104)], [(55, 101), (57, 105)]]:
        strand(R, pts, "#2e1c10", only=(m.peat,))
    sx0, sy0 = 51, int(37 - L)
    strand(R, [(sx0, sy0), (sx0 + 2, sy0 + 6), (sx0 + 1, sy0 + 12)], "#918244")
    for v, length, sway in [((-6.5, -4, 2), 9, -1), ((5.5, -6, 2.5), 12, 1), ((-2.5, -8, 4), 6, 0)]:
        hx, hy = F.xy(v)
        if pose == "telegraph":       # hair drawn forward on the draught
            strand(R, [(hx, hy), (hx - sway * 2, hy + length // 2)], "#0c0806")
        else:
            strand(R, [(hx, hy), (hx + sway, hy + length)], "#0c0806")
    # a ragged coat hem; fen water dripping into the puddle
    hem = int(86 - L * 0.6)
    for x in range(30, 66):
        if R.on(x, hem, m.coat) and (x * 7) % 5 < 2:
            R.px(x, hem, "#060706")
    if pose == "normal":
        R.pxs([(26, 103), (26, 107), (55, 85), (55, 89)], "#2a3650")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "art/monsters/mouther"
    extra = out if args else "art/concepts"
    which = args[1:] or list(POSES)
    os.makedirs(out, exist_ok=True)
    bg = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_bg.png")).convert("RGBA")
    scenes = []
    for k in which:
        img = build(k).to_rgba()
        sc.save(img, os.path.join(out, f"{k}.png"))
        if "--zoom" in sys.argv:
            sc.save(img, os.path.join(extra, f"mouther_{k}_x6.png"), 6)
        scenes.append(compose(img, bg))
        print("wrote", os.path.join(out, f"{k}.png"))
    path = os.path.join(extra, "mouther_poses.png")
    sheet(scenes, [LABELS[k] for k in which], path)
    print("sheet:", path)
