"""Penny Leeches (enemy `penny_leech`): a pack of three, the fen's first ordinary fight.

Fat glossy leeches rearing off a coiled tail, a round pink sucker for a head, and the coins wished
into Hollowell's well grown into their skin (why the water tastes of pennies). The coins are the
focal accent.

Poses (50x76, one canvas and ground line; designed at 44x66 and sculpted 1.15x):
  normal, normal_2, normal_3   three individuals, each its own S-curve (a pack member picks one)
  telegraph                    the chorus: all three rear up into the SAME pose, suckers flared -
                               identical bodies in a row read as unison at a glance
  hurt                         a leech's reflex: it contracts into a fat knot, sucker clenched

    python tools/art/penny_leech.py [OUTDIR] [poses...]

Writes <pose>.png at 1x to OUTDIR (default art/monsters/penny_leech) and a sheet of the formation
(normal trio, telegraph trio, hurt) to art/concepts/penny_leech_poses.png.
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import sculpt as sc
from host_concepts import PAL as HOST_PAL, horror_light, M, sheet

W, H = 50, 76
SC = 1.15          # the poses below are laid out on a 44x66 grid, ground at y=66, centre x=22


def sp(p):
    """Design grid -> canvas: scale about the bottom centre."""
    return (W / 2 + (p[0] - 22) * SC, H - (66 - p[1]) * SC, p[2] * SC)

PAL = dict(HOST_PAL)
PAL.update({
    "leech":  dict(ramp=["#0c0c0a", "#1a1914", "#2b2920", "#433f30", "#625b44"], outline="#060605",
                   spec="#c8c2a0", shin=26.0, spec_thr=0.45),
    "under":  dict(ramp=["#18160e", "#2c291a", "#433e26", "#5d5634", "#7c7246"], outline="#0a0906",
                   spec="#cfc69a", shin=22.0, spec_thr=0.5),
    "copper": dict(ramp=["#2a1307", "#5c2e0e", "#91531c", "#c27e30", "#e8b05c"], outline="#140902",
                   spec="#fff0c0", shin=30.0, spec_thr=0.5),
    "throat": dict(ramp=["#10060c", "#1c0a13", "#2b0e1b", "#3f1424", "#5a1c30"], outline="#0a0408"),
})


def materials(S):
    m = M()
    for name in ["leech", "under", "copper", "flesh", "throat"]:
        setattr(m, name, S.mat(name, **PAL[name]))
    return m


# spine (base to neck), radii along it, head centre, which way the sucker faces, coins (t, sideways)
POSES = {
    "normal": dict(spine=[(22, 59, 0), (17, 50, 3), (19, 40, 5), (25, 30, 5), (24, 20, 6.5)],
                   radii=[8.5, 8.0, 7.0, 6.0, 5.2], head=(23.5, 14, 8), face=(0, -0.5, 0.86),
                   mouth=(3.2, 1.5, 1.0), coins=[(0.18, 3), (0.42, -3), (0.6, 2), (0.8, -1)]),
    "normal_2": dict(spine=[(24, 59, 0), (29, 51, 3), (28, 43, 5), (22, 37, 6), (16, 32, 6.5)],
                     radii=[8.5, 8.0, 7.0, 6.0, 5.2], head=(13.5, 27.5, 8), face=(-0.45, -0.3, 0.84),
                     mouth=(3.2, 1.5, 1.0), coins=[(0.2, -3), (0.45, 2), (0.7, 1)]),
    "normal_3": dict(spine=[(20, 59, 0), (15, 51, 3), (17, 42, 5), (23, 35, 5.5), (28, 27, 6.5)],
                     radii=[8.5, 8.0, 7.0, 6.0, 5.2], head=(30.5, 21.5, 8), face=(0.4, -0.4, 0.82),
                     mouth=(3.2, 1.5, 1.0), coins=[(0.15, 2), (0.38, -2), (0.62, 3), (0.8, -1)]),
    # the chorus: reared straight up, stretched thin, the sucker flared wide and aimed at you
    "telegraph": dict(spine=[(22, 59, 0), (21, 48, 2), (22, 36, 4), (22, 24, 5), (22, 14, 6.5)],
                      radii=[8.0, 6.8, 5.8, 5.0, 4.6], head=(22, 8.5, 8), face=(0, -0.25, 0.97),
                      mouth=(4.2, 1.7, 1.25), coins=[(0.18, 2.5), (0.4, -2.5), (0.6, 2), (0.82, -1.5)]),
    # hurt: contracted into a fat knot, the sucker clenched small
    "hurt": dict(spine=[(22, 59, 0), (20, 53, 3), (22, 46, 5), (25, 40, 5.5), (24, 35, 6.5)],
                 radii=[10.5, 10.0, 9.0, 7.5, 6.2], head=(23.5, 30, 8), face=(0.1, -0.6, 0.8),
                 mouth=(2.0, 1.4, 0.6), coins=[(0.25, 4), (0.5, -4), (0.75, 2)]),
}
LABELS = {"normal": ("normal", "three individuals, each its own curve"),
          "telegraph": ("telegraph", "the chorus: all three rise as one"),
          "hurt": ("hurt", "contracts into a knot")}


def along(spine, radii, t):
    n = len(spine) - 1
    i = min(int(t * n), n - 1)
    f = t * n - i
    a, b = np.array(spine[i], float), np.array(spine[i + 1], float)
    return a + (b - a) * f, radii[i] + (radii[i + 1] - radii[i]) * f


def basis(face):
    face = np.array(face, float)
    face /= np.linalg.norm(face)
    side = np.cross(face, [0.0, 0.0, 1.0])
    side = side / np.linalg.norm(side) if np.linalg.norm(side) > 1e-6 else np.array([1.0, 0, 0])
    if side[0] < 0:
        side = -side
    up = np.cross(side, face)
    return face, side, up


def build(pose):
    P = POSES[pose]
    S = sc.Scene(W, H)
    horror_light(S)
    m = materials(S)
    spine = [sp(q) for q in P["spine"]]
    radii = [r * SC for r in P["radii"]]
    head = sp(P["head"])
    S.group()
    # the tail coiled on the ground, its tip curling out in front
    S.ell(sp((22, 61, 0)), (13 * SC, 4.2 * SC, 9 * SC), m.leech)
    S.cone(sp((29, 62, 6)), sp((35, 63.5, 9)), 2.6 * SC, 1.2 * SC, m.leech, k=1.0)
    S.chain(spine, radii, m.leech, k=1.5)
    S.ell(head, (radii[-1] + 0.6, radii[-1] - 0.2, radii[-1] + 0.2), m.leech, k=2.0)
    # a paler underside down the inside of the curve
    S.group(k=1.2)
    for t in (0.1, 0.3, 0.5, 0.7):
        p, r = along(spine, radii, t)
        S.ell((p[0], p[1], p[2] + r * 0.62), (r * 0.42, r * 0.75, r * 0.35), m.under)
    # swallowed pennies, grown into the skin
    S.group(k=0.4)
    coins = []
    for t, dx in P["coins"]:
        p, r = along(spine, radii, t)
        dx *= SC
        c = (p[0] + dx, p[1], p[2] + np.sqrt(max(r * r - dx * dx, 1.0)) - 0.1)
        S.ell(c, (3.2, 3.2, 1.2), m.copper, rot=(dx * 4, 0, dx * 8))
        coins.append(c)
    # the sucker: a ring of pink lip, dark inside
    face, side, up = basis(P["face"])
    R0, r0, gape = P["mouth"]
    R0, r0 = R0 * SC, r0 * SC
    mouth = np.array(head, float) + face * (radii[-1] - 0.6)
    S.group(k=1.0)
    S.torus(tuple(mouth), tuple(face), R0, r0, m.flesh)
    S.carve_sphere(tuple(mouth + face * 1.2), (R0 - 0.9) * gape, k=0.6, mat=m.throat)

    R = S.render(ss=2)
    R.cleanup()
    # annuli: faint rings across the lit body
    for y in range(4, H - 10, 4):
        for x in range(1, W - 1):
            if R.on(x, y, m.leech) and R.code[y, x] % 8 in (2, 3):
                R.px(x, y, PAL["leech"]["ramp"][1])
    # each coin catches the light: a bright glint up and left of its middle
    for c in coins:
        x, y = int(np.floor(c[0] - 1)), int(np.floor(c[1] - 1))
        if R.on(x, y, m.copper):
            R.px(x, y, "#fff0c0")
    # a ring of pale teeth inside the sucker (more of them when it flares)
    n = 10 if gape > 1 else 8
    for a in np.linspace(0, 2 * np.pi, n, endpoint=False):
        p = mouth + face * 0.8 + (side * np.cos(a) + up * np.sin(a)) * (R0 - 1.1)
        x, y = int(np.floor(p[0])), int(np.floor(p[1]))
        if R.on(x, y, m.throat):
            R.px(x, y, "#d8cfb4")
    return R


def formation(imgs, bg):
    """Stand a formation as the battle does: 4px apart, centred on x=160, bottoms on y=122."""
    total = sum(i.shape[1] for i in imgs) + 4 * (len(imgs) - 1)
    x = 160 - total // 2
    canvas = bg.copy()
    for i in imgs:
        canvas.alpha_composite(Image.fromarray(i, "RGBA"), (x, 122 - i.shape[0]))
        x += i.shape[1] + 4
    return canvas


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "art/monsters/penny_leech"
    extra = out if args else "art/concepts"
    which = args[1:] or list(POSES)
    os.makedirs(out, exist_ok=True)
    imgs = {}
    for k in which:
        imgs[k] = build(k).to_rgba()
        sc.save(imgs[k], os.path.join(out, f"{k}.png"))
        if "--zoom" in sys.argv:
            sc.save(imgs[k], os.path.join(extra, f"penny_leech_{k}_x6.png"), 6)
        print("wrote", os.path.join(out, f"{k}.png"))
    if all(k in imgs for k in POSES):
        bg = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_bg.png")).convert("RGBA")
        scenes = [formation([imgs["normal"], imgs["normal_2"], imgs["normal_3"]], bg),
                  formation([imgs["telegraph"]] * 3, bg),
                  formation([imgs["normal"], imgs["hurt"], imgs["normal_3"]], bg)]
        path = os.path.join(extra, "penny_leech_poses.png")
        sheet(scenes, [LABELS["normal"], LABELS["telegraph"], LABELS["hurt"]], path)
        print("sheet:", path)
