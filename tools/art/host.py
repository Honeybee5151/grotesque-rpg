"""The Host (enemy `host`): final battle sprites, from concept C "The Hunched" (Miles' pick).

A man bent forward on his knuckles, head hanging so his opened crown faces you. The Sucker Frog
rides his back; a cord runs from its mouth down into his skull. The cord is the focal accent.
His head is drained paler than the rest of him: the sucker feeds there first.

Poses (all on one 104x118 canvas and ground line, so swapping never moves him):
  normal     hunched, head hanging, face in shadow; the cord sags across him.
  telegraph  the coil: the frog rears, the cord snaps taut and yanks his head up - jaw unhinged -
             and flings his buckling arm out like a jerked marionette.
  stunned    after a guarded latch: the sucker is torn out of his skull and hangs slack, the frog
             slides off dazed, and for one turn the man looks up with clear eyes and reaches out.
  hurt       a flinch when hit: the frog squeezes its eyes shut, the cord jolts, his head jerks.

    python tools/art/host.py [OUTDIR] [normal telegraph stunned hurt] [--zoom] [--verbose]

Writes the game sprites, <pose>.png at 1x, to OUTDIR (default art/monsters/host), and a labelled
sheet of the poses on the cave background to art/concepts/host_poses.png (--zoom: also x6 zooms
there). With an explicit OUTDIR, everything goes to OUTDIR instead (for scratch iterations).
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import sculpt as sc
from host_concepts import (W, H, PAL, horror_light, M, warts, strand, edge_line,
                           VEIN, HAIR, compose, sheet)

PAL = dict(PAL)
# bloodless head skin: a step lighter and colder than his arms
PAL["pale"] = dict(ramp=["#2a2231", "#4a4352", "#6f6a76", "#99969a", "#c6c2b8"], outline="#120c18")
# inside his mouth: dark, so the cord stays the only saturated pink on him
PAL["throat"] = dict(ramp=["#10060c", "#1c0a13", "#2b0e1b", "#3f1424", "#5a1c30"], outline="#0a0408")


def materials(S):
    m = M()
    for name in ["skin", "pale", "throat", "frog", "belly", "flesh", "brain", "shirt", "pants", "eye", "bone"]:
        setattr(m, name, S.mat(name, **PAL[name]))
    return m


class Frame:
    """A posable local frame (x right, y down, z out of the face) for placing a part's features once."""

    def __init__(self, origin, rot=(0, 0, 0)):
        self.o = np.array(origin, float)
        self.R = sc.rotm(*rot)

    def p(self, v):
        return tuple(self.o + self.R @ np.array(v, float))

    def d(self, v):
        return tuple(self.R @ np.array(v, float))

    def xy(self, v):
        x, y, _ = self.p(v)
        return int(np.floor(x)), int(np.floor(y))


def fell(S, F, c, r, mat, k=0.0, rot=(0, 0, 0), carve=False):
    e = sc.Ellipsoid(F.p(c), r)
    e.R = F.R @ sc.rotm(*rot)
    S._add(e, mat, k, "sub" if carve else "add")


def fingers(S, mat, pairs, ra=1.1, rb=0.9):
    for a, b in pairs:
        S.cone(a, b, ra, rb, mat, k=0.6)


def up(p, lift):
    return (p[0], p[1] - lift, p[2])


def lerp(a, b, t):
    return tuple(np.array(a, float) + (np.array(b, float) - np.array(a, float)) * t)


def add(a, b):
    return tuple(np.array(a, float) + np.array(b, float))


# ----------------------------------------------------------------------------------------------
# poses
# ----------------------------------------------------------------------------------------------

POSES = {
    "normal": dict(
        lift=0, arm="buckled",
        head=(45, 74, 10), head_rot=(-38, 0, -18), jaw=0.0, mouth=1.0, eyes="rolled",
        frog=(59, 34, -8), frog_rot=(0, 0, 0), frog_eyes="lidded", grip=(True, True),
        cord="slack", sucker=(4.4, 1.6),
    ),
    "telegraph": dict(
        lift=6, arm="spasm",
        head=(47, 61, 16), head_rot=(24, 0, -10), jaw=8.0, mouth=1.3, eyes="white",
        frog=(59, 27, -9), frog_rot=(22, 0, 4), frog_eyes="wide", grip=(True, True),
        cord="taut", sucker=(3.4, 2.3),
    ),
    "stunned": dict(
        lift=4, arm="reaching",
        head=(46, 63, 15), head_rot=(-4, 0, 9), jaw=0.0, mouth=0.55, eyes="clear",
        frog=(64, 36, -8), frog_rot=(25, 0, 28), frog_eyes="dazed", grip=(False, True),
        cord="torn", sucker=(2.6, 1.2),
    ),
    "hurt": dict(
        lift=-3, arm="buckled",
        head=(43, 77, 9), head_rot=(-46, 12, -34), jaw=2.0, mouth=1.0, eyes="shut",
        frog=(59, 37, -8), frog_rot=(-10, 0, -5), frog_eyes="shut", grip=(True, True),
        cord="slack", sag=2.2, sucker=(4.0, 1.9),
    ),
}


# ----------------------------------------------------------------------------------------------
# the man
# ----------------------------------------------------------------------------------------------

def man(S, m, P):
    L = P["lift"]
    S.group()
    # legs: his right knee up, his left dragged behind on the knee, foot twisted out
    S.cone((43, 70, -16), (36, 94, -3), 6, 4.6, m.pants)
    S.cone((36, 94, -3), (33, 111, -2), 4.6, 3.4, m.pants, k=1.0)
    S.ell((32, 114, 0), (4.5, 2.3, 5.5), m.skin, k=1.0)
    S.cone((61, 70, -16), (67, 108, -1), 6, 4.4, m.pants, k=1.5)
    S.cone((67, 108, -1), (70, 112, -18), 4.4, 3.4, m.pants, k=1.0)
    S.ell((74.5, 113.5, -22), (5, 2.2, 3), m.skin, k=1.0, rot=(0, 0, -15))

    # back, shoulders (his right dropped), chest
    shR, shL = up((31, 63, 0), L), up((73, 55.5, 0), L)
    S.ell(up((52, 54, -6), L), (20, 12.5, 14), m.shirt, k=2.0, rot=(0, 0, -6))
    S.sphere(shR, 7, m.shirt, k=3.0)
    S.sphere(shL, 7, m.shirt, k=3.0)
    S.ell(up((52, 66, -2), L), (16, 10, 12), m.shirt, k=3.0, rot=(0, 0, -6))
    for i, (y, z) in enumerate([(44, 6.5), (48.5, 7.6), (53, 8.2), (57.5, 8.0)]):
        S.sphere(up((52 - i * 0.4, y + i * 0.5, z - 2.0), L), 2.4 - i * 0.15, m.shirt, k=1.6)

    # his left arm: too long, planted far out, fingers splayed
    S.cone(shL, up((84, 79, 3), L * 0.5), 5, 4, m.shirt, k=2.0)
    S.cone(up((84, 79, 3), L * 0.5), (85, 103, 6), 3.4, 2.6, m.skin, k=1.0)
    S.ell((85.5, 107.5, 7), (4.2, 3.6, 3.6), m.skin, k=1.0)
    fingers(S, m.skin, [((82.5, 109, 8), (80, 115, 9.5)), ((85, 110, 9), (84.5, 115.5, 10.5)),
                        ((87.5, 109.5, 8.5), (89, 115, 10)), ((89.5, 108, 8), (92.5, 113.5, 9)),
                        ((82, 106, 8), (78.5, 109.5, 9))])

    # his right arm
    if P["arm"] == "buckled":
        # buckling, the elbow kicked out sideways as it gives under him
        S.cone(shR, (15, 81, 2), 5, 4, m.shirt, k=2.0)
        S.cone((15, 81, 2), (25, 101, 7), 3.4, 2.6, m.skin, k=1.0)
        S.ell((26, 106, 8), (4.2, 3.6, 3.6), m.skin, k=1.0, rot=(0, 0, 15))
        fingers(S, m.skin, [((24, 108, 9), (22, 114, 10)), ((26.5, 109, 9.5), (26.5, 114.5, 11)),
                            ((29, 108, 9), (30.5, 113.5, 10.5)), ((30, 105, 9), (33.5, 108, 10))])
    elif P["arm"] == "spasm":
        # jerked off the ground and flung out, fingers clawed
        S.cone(shR, (15, 70, 4), 5, 4, m.shirt, k=2.0)
        S.cone((15, 70, 4), (9, 85, 7), 3.4, 2.6, m.skin, k=1.0)
        S.ell((8.5, 89.5, 8), (3.6, 3.4, 3.2), m.skin, k=1.0, rot=(0, 0, 20))
        fingers(S, m.skin, [((6, 91, 9), (3.5, 95.5, 10)), ((8, 92.5, 9.5), (6.5, 97.5, 10.5)),
                            ((10, 92.5, 9), (11, 97.5, 10)), ((11.5, 90.5, 9), (14.5, 93.5, 10)),
                            ((10.5, 87, 9), (13.5, 84.5, 10))])
    else:
        # reaching toward you, palm open: the only thing he can say
        S.cone(shR, (25, 78, 7), 5, 4, m.shirt, k=2.0)
        S.cone((25, 78, 7), (25, 86, 16), 3.4, 2.8, m.skin, k=1.0)
        S.ell((25.5, 84.5, 18), (3.6, 4.0, 1.8), m.skin, k=1.0)
        fingers(S, m.skin, [((22.5, 81.5, 19), (20.5, 76.5, 20)), ((24.5, 81, 19.5), (24, 75.5, 20.5)),
                            ((26.5, 81, 19.5), (27, 75.5, 20.5)), ((28.5, 82, 19), (30.5, 77.5, 20)),
                            ((28.5, 86, 18.5), (31.5, 84.5, 19.5))])

    # neck, down and forward into the head
    F = Frame(P["head"], P["head_rot"])
    S.cone(up((50, 57, 3), L), F.p((0, 3, -7)), 5, 4.4, m.pale, k=2.0)
    head(S, m, F, P)
    return F


def head(S, m, F, P):
    jaw, mo = P["jaw"], P["mouth"]
    skew = -jaw * 1.4                     # an unhinged jaw hangs crooked
    fell(S, F, (0, 0, 0), (9, 11, 10.5), m.pale, k=1.5)
    fell(S, F, (-jaw * 0.15, 8.5 + jaw, 4.5), (6.4, 3.6, 6.2), m.pale, k=2.0, rot=(0, 0, skew))
    if jaw > 0:
        for sx in (-1, 1):
            S.cone(F.p((5.8 * sx, 4, 2)), F.p((5.2 * sx - jaw * 0.15, 8.5 + jaw * (1 - 0.12 * sx), 3.5)),
                   2.0, 1.8, m.pale, k=1.5)
    for sx in (-1, 1):
        S.sphere(F.p((5.5 * sx, 1.5, 7)), 2.6, m.pale, k=2.0)
        fell(S, F, (9.6 * sx, 1, -0.5), (1.8, 3.2, 2.8), m.pale, k=1.2)
        S.carve_sphere(F.p((3.4 * sx, 0, 9.3)), 2.4, k=1.0)
    S.cone(F.p((0, 0.5, 10.2)), F.p((0, 4.6, 11.4)), 1.2, 1.6, m.pale, k=0.8)
    fell(S, F, (-jaw * 0.1, 7.55 + jaw * 0.5, 8.8), (3.4 * mo, (2.15 + jaw * 0.5) * min(mo, 1.0), 4),
         m.throat, k=0.8, rot=(0, 0, skew), carve=True)
    # the opened crown
    S.carve_sphere(F.p((0, -10, 1.5)), 5.2, k=1.0, mat=m.brain)
    S.group(k=1.0)
    S.sphere(F.p((0, -8.6, 1.2)), 4.4, m.brain)


# ----------------------------------------------------------------------------------------------
# the frog (parts in its own frame, so it can rear or slide; its feet grip his shoulders)
# ----------------------------------------------------------------------------------------------

FROG_EYES = [(-7, -15.5, 8.5), (5, -17, 7.5)]
FROG_MOUTH = (-3, -6, 10)


def frog(S, m, P):
    G = Frame(P["frog"], P["frog_rot"])
    L = P["lift"]
    S.group(k=0.0)
    fell(S, G, (0, 0, 0), (14, 12, 11), m.frog, rot=(0, 0, 6))
    fell(S, G, (-1, 6, 7), (9, 7, 6), m.belly, k=2.0)
    fell(S, G, (-1, -11, 4), (11, 8, 9), m.frog, k=3.0, rot=(0, 0, 8))
    fell(S, G, (-1.5, -7, 12.2), (7.5, 0.9, 3), m.flesh, k=0.4, rot=(0, 0, 8), carve=True)
    fell(S, G, (-13, 9, 0), (6, 5, 6), m.frog, k=2.0, rot=(0, 0, -25))
    fell(S, G, (12.5, 7, 0), (6, 5, 6), m.frog, k=2.0, rot=(0, 0, 25))
    # feet: one gripping his dropped shoulder, one clamped on the high one (or dangling, let go)
    feet = [((-11, 8, 5), (38, 53, 4), [(34.5, 56.5, 5), (37.5, 58, 5.5), (40.5, 57, 5)]),
            ((8, 6, 5), (70, 50, 2), [(67.5, 53, 3), (70, 54.5, 3.5), (72.5, 53, 3)])]
    for (base, tip0, tips), grip in zip(feet, P["grip"]):
        b = G.p(base)
        if grip:
            tip0, tips = up(tip0, L), [up(t, L) for t in tips]
        else:
            tip0 = add(b, (-3, 10, 3))
            tips = [add(tip0, d) for d in [(-2.5, 3.5, 1), (0, 4.5, 1.5), (2.5, 3.5, 1)]]
        S.cone(b, tip0, 2.8, 2.1, m.frog, k=1.2)
        for tip in tips:
            S.cone(tip0, tip, 1.0, 0.8, m.frog, k=0.6)
            S.sphere(tip, 1.2, m.frog, k=0.5)
    S.group(k=0.6)
    for e in FROG_EYES:
        S.sphere(G.p(e), 2.9, m.eye)
    # lids: heavy (normal), raised (rearing), drooping (dazed), squeezed over the whole eye (flinch)
    lid = {"lidded": 0.0, "wide": -1.4, "dazed": 1.1}.get(P["frog_eyes"], 0.0)
    S.group(k=0.8)
    for e, rz in zip(FROG_EYES, (-12, 12)):
        if P["frog_eyes"] == "shut":
            fell(S, G, add(e, (0, 0, 0.4)), (3.5, 3.2, 3.3), m.frog, rot=(0, 0, rz))
        else:
            fell(S, G, add(e, (0, -1.5 + lid, -0.2)), (3.8, 2.2, 3.4), m.frog, rot=(0, 0, rz))
    return G


# ----------------------------------------------------------------------------------------------
# the cord: from the frog's mouth into the crown - sagging, taut, or torn out and hanging
# ----------------------------------------------------------------------------------------------

def cord(S, m, P, F, G):
    S.group(k=1.4)
    mouth = G.p(FROG_MOUTH)
    crown = F.p((0, -10.8, 1.5))
    end = crown
    s = P["sucker"]
    if P["cord"] == "slack":
        g = P.get("sag", 1.0)
        pts = [mouth, add(lerp(mouth, crown, 0.22), (-1 * g, 0, 6)), add(lerp(mouth, crown, 0.47), (2.5 * g, 0, 6)),
               add(lerp(mouth, crown, 0.73), (1.5 * (1 - g), 0, 4)), crown]
        S.chain(pts, [2.4, 2.0, 2.1, 1.9, 2.6], m.flesh, k=1.0)
        S.sphere(add(lerp(mouth, crown, 0.42), (0, 0, 6)), 3.0, m.flesh, k=1.6)   # a swallowed lump
    elif P["cord"] == "taut":
        pts = [lerp(mouth, crown, t) for t in (0, 0.33, 0.66, 1)]
        S.chain(pts, [2.0, 1.6, 1.6, 2.4], m.flesh, k=0.8)
    if P["cord"] in ("slack", "taut"):
        S.torus(F.p((0, -10, 1.5)), F.d((0, -1, 0.25)), s[0], s[1], m.flesh, k=1.0)
    else:
        # torn out: hangs from its mouth, the sucker's open ring dangling by his face
        end = add(mouth, (2, 38, 13))
        pts = [mouth, add(mouth, (1, 10, 5)), add(mouth, (2, 20, 9)), add(mouth, (2.5, 30, 12)), end]
        S.chain(pts, [2.2, 1.8, 1.8, 1.9, 2.2], m.flesh, k=1.0)
        S.torus(add(end, (0, 2.4, 1)), (0, 0.35, 1), s[0], s[1], m.flesh, k=0.8)
    return end


# ----------------------------------------------------------------------------------------------
# hand-painted details
# ----------------------------------------------------------------------------------------------

EYE_DIM, EYE_LID = "#a39a86", "#4a4352"
DROOL, DROOL_HI = "#46525a", "#8fa4a6"
PUPIL = "#0a0604"


def hang(R, x0, y0, length, col, only=None, sway=0):
    """A strand hanging straight down (hair, drool), with an optional sideways drift."""
    pts = [(x0, y0), (x0 + sway * 0.5, y0 + length * 0.5), (x0 + sway, y0 + length)]
    strand(R, pts, col, only)


def details(R, m, P, F, G, end):
    # frog: slit pupils (crossed when dazed), warts
    for i, e in enumerate(FROG_EYES):
        x, y = G.xy(add(e, (0, 0, 2.9)))
        if P["frog_eyes"] == "dazed":
            R.px(x + (1 if i == 0 else -1), y + 1, PUPIL)
        elif P["frog_eyes"] == "shut":
            R.pxs([(x - 1, y), (x, y + 1), (x + 1, y + 1), (x + 2, y)], "#090d08")
        elif P["frog_eyes"] == "wide":
            R.pxs([(x, y), (x + 1, y), (x, y - 1), (x + 1, y - 1)], PUPIL)
        else:
            R.pxs([(x, y), (x + 1, y)], PUPIL)
    gx, gy = G.xy((0, 0, 0))
    warts(R, m.frog, 16, 3, "#848a40", "#141a14", box=(gx - 19, gy - 24, gx + 17, gy + 18))

    # the cut scalp: a bone rim around the brain, veins crawling out from where the sucker feeds
    edge_line(R, m.brain, m.pale, "#9b8f74")
    for a, r2 in [(-105, 8.4), (-50, 7.6), (20, 8.0), (75, 8.6), (150, 7.4)]:
        t = np.radians(a)
        p0 = F.xy((5.6 * np.sin(t), -8.6, 1.5 + 5.6 * np.cos(t)))
        p1 = F.xy((r2 * np.sin(t), -5.6, 1.5 + r2 * np.cos(t)))
        strand(R, [p0, p1], VEIN, only=(m.pale,))

    eyes = P["eyes"]
    for sx in (-1, 1):
        ex, ey = F.xy((3.4 * sx, -0.4, 10.4))
        if eyes == "rolled":        # dim, rolled up toward you from the shadow
            R.px(ex, ey, EYE_DIM)
            R.px(ex + (1 if sx < 0 else -1), ey, EYE_LID)
        elif eyes == "shut":        # squeezed shut
            R.pxs([(ex - 1, ey), (ex, ey + 1), (ex + 1, ey)], "#2a2231")
        elif eyes == "white":       # rolled all the way back: a sliver of white under the lid
            R.pxs([(ex, ey + 1), (ex + 1, ey + 1)], EYE_DIM)
        else:                       # clear: his own eyes, looking right at you
            R.pxs([(ex - 1, ey), (ex, ey), (ex + 1, ey)], "#c6c2b8")
            R.px(ex, ey, PUPIL)
    if eyes == "clear":
        ex, ey = F.xy((3.4, -0.4, 10.4))
        strand(R, [(ex, ey + 2), (ex, ey + 5), (ex + 1, ey + 8)], "#4a4352", only=(m.pale,))
    if P["cord"] == "torn":
        # the sucker's open throat, still dripping; a fresh run from the hole in his crown
        ox, oy = int(np.floor(end[0])), int(np.floor(end[1] + 2.4))
        R.pxs([(ox, oy), (ox - 1, oy), (ox, oy - 1), (ox - 1, oy - 1)], "#1a0510")
        R.pxs([(ox, oy + 5), (ox, oy + 7)], "#681430")
        cx, cy = F.xy((6, -6.5, 6.5))
        strand(R, [(cx, cy), (cx, cy + 4), (cx + 1, cy + 7)], "#681430", only=(m.pale,))

    # teeth on the upper gum; drool when his mouth hangs open
    if P["mouth"] >= 1.0:
        for i, x in enumerate(np.linspace(-2.6, 2.6, 5)):
            R.px(*F.xy((x, 6.6, 9.8)), "#9b8f74" if i % 2 == 0 else "#4f4030")
    if P["jaw"] > 2:
        for x in (-2.2, 0.4, 2.4):
            R.px(*F.xy((x - P["jaw"] * 0.1, 8.0 + P["jaw"], 9.0 - x * 0.2)), "#6c614f")
    if P["jaw"] > 0.5 or eyes == "rolled":
        mx, my = F.xy((0, 9.6 + P["jaw"], 8.6))
        hang(R, mx, my, 13 - int(P["jaw"]), DROOL, sway=1)
        R.px(mx + 1, my + 8, DROOL_HI)

    # a few hairs left on the drained scalp, hanging past his ears
    for v, length, sway in [((-8.5, -5, 3), 12, -1), ((-9.5, -1, 1), 9, 0), ((8, -6.5, 3), 10, 1), ((9.5, -2, 1), 7, 0)]:
        hx, hy = F.xy(v)
        hang(R, hx, hy, length, HAIR, sway=sway)


def build(pose="normal", verbose=False):
    P = POSES[pose]
    S = sc.Scene(W, H)
    horror_light(S)
    m = materials(S)
    F = man(S, m, P)
    G = frog(S, m, P)
    end = cord(S, m, P, F, G)
    R = S.render(ss=2)
    R.cleanup()
    details(R, m, P, F, G, end)
    if verbose:
        print(pose)
        for name, v in [("crown", (0, -10, 1.5)), ("eyeL", (-3.4, 0, 9.3)), ("eyeR", (3.4, 0, 9.3)),
                        ("nose", (0, 4.6, 11.4)), ("mouth", (0, 7.6, 8.8)), ("chin", (0, 11, 5))]:
            print(f"  {name:6s} {F.xy(v)}  z={F.p(v)[2]:.1f}")
        print(f"  frog   {G.xy((0, 0, 0))}  mouth {G.xy(FROG_MOUTH)}")
    return R


LABELS = {"normal": ("normal", "hunched, face hidden; the cord sags across him"),
          "telegraph": ("telegraph", "the coil: the frog rears, the cord yanks his head up"),
          "stunned": ("stunned", "sucker torn out, frog dazed: his eyes clear"),
          "hurt": ("hurt", "a flinch: the cord jolts, the frog shuts its eyes")}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "art/monsters/host"
    extra = out if args else "art/concepts"
    which = args[1:] or list(POSES)
    os.makedirs(out, exist_ok=True)
    os.makedirs(extra, exist_ok=True)
    bg = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_bg.png")).convert("RGBA")
    scenes = []
    for k in which:
        img = build(k, verbose="--verbose" in sys.argv).to_rgba()
        sc.save(img, os.path.join(out, f"{k}.png"))
        if "--zoom" in sys.argv:
            sc.save(img, os.path.join(extra, f"host_{k}_x6.png"), 6)
        scenes.append(compose(img, bg))
        print("wrote", os.path.join(out, f"{k}.png"))
    path = os.path.join(extra, "host_poses.png")
    sheet(scenes, [LABELS[k] for k in which], path)
    print("sheet:", path)
