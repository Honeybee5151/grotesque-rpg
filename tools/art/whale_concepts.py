"""The whale that hunts the hunters (Miles: "a whale that hunts humans with a harpoon-like attack,
revenge"). Three concepts for him to pick from:

  A  The Harpooner  a sperm whale standing on its flukes like a man, two pale human arms grown out of
                    its flanks, gripping a whaler's harpoon. It learned the hunt from the men who
                    hunted it. Hook: throw and reel - the hero is hooked, then hauled in.
  B  Old Iron       a vast scarred whale head breaching out of black water, bristling with the rusted
                    harpoons of every whaler who ever struck it, ropes trailing, one huge old eye.
                    Hook: it wrenches a harpoon out of its own hide and gives it back.
  C  The Flensed    a whale stripped of its blubber, crawling on its own ribs, a jaw of bare bone.
                    Hook: it fires its toothed jaw on a sinew line and reels the hero in.

    python tools/art/whale_concepts.py [OUTDIR] [a b c]   # default art/concepts -> whale_options.png
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import sculpt as sc
from host_concepts import PAL as HOST_PAL, horror_light, M, strand, sheet, compose

W, H = 104, 118

PAL = dict(HOST_PAL)
PAL.update({
    "whale": dict(ramp=["#0c1016", "#18202a", "#28323e", "#3c4856", "#566474"], outline="#06080c",
                  spec="#a8b8c8", shin=30.0, spec_thr=0.6),
    "wbelly": dict(ramp=["#1e2228", "#343a42", "#4e5660", "#6e7680", "#929aa2"], outline="#0e1014"),
    "iron":  dict(ramp=["#1a0e08", "#3a1e10", "#5e321a", "#844a26", "#a8663a"], outline="#0c0604",
                  spec="#d89a6a", shin=24.0, spec_thr=0.6),
    "wood":  dict(ramp=["#1c140c", "#34261a", "#504028", "#6e5a3a", "#8e7a52"], outline="#0e0a06"),
    "milk":  dict(ramp=["#2e2e2a", "#4e4c46", "#74726a", "#9e9a8e", "#c8c4b4"], outline="#121210",
                  spec="#f0eee4", shin=30.0, spec_thr=0.5),
    "water": dict(ramp=["#05060a", "#0a0c12", "#10141c", "#1a2232", "#2a3650"], outline="#030305",
                  spec="#9ab4cc", shin=40.0, spec_thr=0.35),
    "pale":  dict(ramp=["#2a2231", "#4a4352", "#6f6a76", "#99969a", "#c6c2b8"], outline="#120c18"),
    "meat":  dict(ramp=["#2a0810", "#4a1018", "#6e1c24", "#922e30", "#b44a44"], outline="#14040a",
                  spec="#e89a90", shin=20.0, spec_thr=0.55),
    "fat":   dict(ramp=["#3a3020", "#5e5034", "#86764c", "#ae9e6a", "#d2c690"], outline="#1c160e"),
    "oilskin": dict(ramp=["#2a2008", "#4e3c0c", "#7a6214", "#a88a1e", "#d0b030"], outline="#141004",
                    spec="#f4e08a", shin=24.0, spec_thr=0.6),
})
ROPE, ROPE_DK = "#8a8460", "#46402a"
FOAM, FOAM_DK = "#9ab4cc", "#4a5a70"


def materials(S):
    m = M()
    for name in ["whale", "wbelly", "iron", "wood", "milk", "water", "pale", "meat", "fat", "bone", "oilskin"]:
        setattr(m, name, S.mat(name, **PAL[name]))
    return m


def unit(v):
    v = np.array(v, float)
    return v / np.linalg.norm(v)


def on_ellipsoid(c, r, d):
    """The point on an axis-aligned ellipsoid's surface in direction d from its centre, and its normal."""
    d = unit(d)
    t = 1.0 / np.sqrt(((d / np.array(r, float)) ** 2).sum())
    p = np.array(c, float) + d * t
    n = unit((p - np.array(c, float)) / (np.array(r, float) ** 2))
    return p, n


# ==============================================================================================
# B - Old Iron: a breaching head bristling with every harpoon ever thrown at it
# ==============================================================================================

def old_iron():
    S = sc.Scene(W, H)
    horror_light(S)
    m = materials(S)
    S.group()
    S.ell((52, 113, 0), (52, 2.6, 22), m.water)

    S.group()
    # spyhopping: the head stood straight up out of the water to watch you, leaning a little
    body_c, body_r = (56, 64, -8), (24, 54, 21)
    S.ell(body_c, body_r, m.whale, rot=(0, 0, 7))
    S.ell((52, 38, 4), (21, 30, 15), m.whale, k=6.0, rot=(0, 0, 7))       # the blunt spermaceti brow
    S.ell((51, 17, -2), (24, 9, 19), m.whale, k=7.0, rot=(0, 0, 7))       # squared off at the top
    S.ell((26, 106, 6), (11, 3, 5), m.whale, k=2.0, rot=(0, 0, -22))      # a flipper at the waterline
    # the mouth: a dark seam down the front where the jaw has dropped away from it
    S.carve_ell((37, 74, 14), (3.0, 30, 6), k=1.0, rot=(0, 0, 12))
    # the narrow underslung jaw, hanging open down its front, a row of pegs along it
    S.group(k=1.5)
    S.cone((44, 104, 12), (28, 44, 18), 5.4, 3.0, m.wbelly, k=1.0)
    S.ell((44, 103, 12), (6.5, 5, 6), m.wbelly, k=2.0)
    # its eye, small and old, by the hinge of the jaw
    S.group(k=1.2)
    S.ell((48, 93, 15), (5, 4, 4), m.whale)
    S.group(k=0.6)
    S.sphere((49.5, 93, 18), 2.7, m.milk)
    # the harpoons: iron collars sunk in the hide, shafts standing out of its back and brow
    rng = np.random.default_rng(7)
    shafts = []
    S.group(k=0.0)
    dirs = [(0.95, -0.3, 0.1), (0.9, 0.1, 0.15), (0.85, 0.4, 0.2), (0.6, -0.75, 0.15), (0.2, -1.0, 0.2),
            (-0.35, -0.9, 0.3), (0.7, -0.2, 0.7), (0.5, 0.25, 0.8), (0.95, 0.65, 0.2), (0.3, -0.55, 0.8),
            (-0.7, -0.4, 0.4)]
    for d in dirs:
        p, n = on_ellipsoid(body_c, body_r, d)
        n = unit(n + rng.normal(0, 0.15, 3) + np.array([0.0, -0.25, 0.0]))
        tip = p + n * rng.uniform(13, 21)
        S.sphere(tuple(p + n * 0.8), 1.7, m.iron)
        S.cone(tuple(p + n * 0.5), tuple(tip), 1.1, 0.8, m.wood)
        shafts.append((p, tip))

    R = S.render(ss=2)
    R.cleanup()
    # prune-wrinkled hide: wavy creases across the head and body
    for y0 in range(16, 104, 6):
        for x in range(6, 100):
            y = y0 + int(1.5 * np.sin(x * 0.35 + y0))
            if R.on(x, y, m.whale) and R.code[y, x] % 8 in (2, 3):
                R.px(x, y, PAL["whale"]["ramp"][1])
    # pegs of teeth along the open jaw, facing the mouth
    for t in np.linspace(0.1, 0.92, 11):
        x = int(44 + (28 - 44) * t + 3)
        y = int(104 + (44 - 104) * t)
        if R.on(x - 1, y, m.wbelly):
            R.px(x - 1, y, "#9c2646")
        if R.on(x, y, m.wbelly) or R.on(x + 1, y, m.whale):
            R.pxs([(x, y), (x + 1, y)], "#ebe3c6")
    # ropes hanging off the shafts' ends, slack and rotten
    for p, tip in shafts:
        x, y = int(tip[0]), int(tip[1])
        drop, sway = int(rng.uniform(4, 9)), int(rng.choice([-4, -3, 3, 4]))
        strand(R, [(x, y), (x + sway // 2, y + drop // 2), (x + sway, y + drop)], ROPE)
        R.px(x + sway, y + drop, ROPE_DK)
    # the eye: a pale iris, a dark pupil, wrinkles round it
    R.pxs([(50, 92), (50, 93)], "#0a0806")
    R.px(49, 91, "#f0eee4")
    for pts in [[(42, 89), (46, 87), (52, 88)], [(43, 98), (48, 99), (53, 97)]]:
        strand(R, pts, "#0c1016", only=(m.whale,))
    # old wounds where harpoons came out; barnacles on the brow; squid-sucker scars
    for x, y in [(70, 48), (62, 72), (78, 86), (58, 26), (82, 62)]:
        if R.on(x, y, m.whale):
            R.pxs([(x, y), (x + 1, y)], "#06080c")
            R.pxs([(x - 1, y), (x + 2, y), (x, y - 1), (x + 1, y + 1)], "#566474")
    for x, y in [(40, 20), (42, 22), (39, 23), (46, 17), (48, 19)]:
        if R.on(x, y, m.whale):
            R.px(x, y, "#929aa2")
    for cx, cy in [(66, 36), (74, 74)]:
        for a in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            x, y = int(cx + 3 * np.cos(a)), int(cy + 3 * np.sin(a))
            if R.on(x, y, m.whale):
                R.px(x, y, "#3c4856")
    # foam where it breaks the water
    for x in range(4, 100):
        if (x * 13) % 7 < 3:
            R.px(x, 110 + (x % 3 == 0), FOAM if (x * 5) % 4 else FOAM_DK)
    return R


# ==============================================================================================
# A - The Harpooner: a sperm whale stood up on its flukes, with a whaler's arms and harpoon
# ==============================================================================================

def harpooner():
    S = sc.Scene(W, H)
    horror_light(S)
    m = materials(S)
    S.group()
    # standing on its tail: the flukes spread on the ground like feet
    S.ell((33, 112, 4), (17, 3.4, 8), m.whale, rot=(0, 0, -10))
    S.ell((71, 112, 4), (17, 3.4, 8), m.whale, rot=(0, 0, 10))
    S.cone((52, 110, 0), (52, 86, 0), 6, 14, m.whale, k=3.0)
    body_c, body_r = (53, 58, -4), (22, 46, 19)
    S.ell(body_c, body_r, m.whale, k=4.0, rot=(0, 0, 4))
    S.ell((51, 16, -2), (21, 8.5, 17), m.whale, k=7.0, rot=(0, 0, 4))
    S.ell((48, 70, 12), (12, 22, 8), m.wbelly, k=4.0)
    S.carve_ell((38, 66, 13), (2.6, 22, 5), k=1.0, rot=(0, 0, 10))
    S.group(k=1.4)
    S.cone((42, 90, 11), (30, 44, 16), 4.4, 2.6, m.wbelly, k=1.0)
    S.group(k=1.2)
    S.ell((47, 83, 14), (4.4, 3.6, 4), m.whale)
    S.group(k=0.6)
    S.sphere((48.5, 83, 17), 2.4, m.milk)
    # a whaler's arms grown out of its flanks, still in their torn yellow oilskin sleeves
    S.group(k=1.5)
    for sh, el, wr in [((32, 66, 4), (20, 82, 10), (30, 92, 19)), ((74, 60, 4), (87, 70, 10), (77, 55, 19))]:
        S.cone(sh, el, 4.0, 3.4, m.oilskin, k=1.5)
        S.cone(el, wr, 3.0, 2.3, m.pale, k=1.0)
        S.ell(wr, (2.8, 2.6, 2.4), m.pale, k=0.8)
    # the harpoon held across its body: a long shaft, a barbed iron head, the line coiled on the ground
    S.group(k=0.6)
    S.cone((16, 104, 20), (90, 28, 18), 1.3, 1.1, m.wood)
    S.cone((90, 28, 18), (98, 18, 18), 2.0, 0.4, m.iron)
    for d in ((-5, 3), (2, 6)):
        S.cone((95, 22, 18), (95 + d[0], 22 + d[1], 18), 1.0, 0.3, m.iron)
    R = S.render(ss=2)
    R.cleanup()
    for y0 in range(16, 100, 6):
        for x in range(6, 100):
            y = y0 + int(1.5 * np.sin(x * 0.35 + y0))
            if R.on(x, y, m.whale) and R.code[y, x] % 8 in (2, 3):
                R.px(x, y, PAL["whale"]["ramp"][1])
    for t in np.linspace(0.1, 0.92, 10):
        x, y = int(42 + (30 - 42) * t + 3), int(90 + (44 - 90) * t)
        if R.on(x, y, m.wbelly) or R.on(x + 1, y, m.whale):
            R.pxs([(x, y), (x + 1, y)], "#ebe3c6")
    R.pxs([(49, 82), (49, 83)], "#0a0806")
    # fingers wrapped round the shaft; the line from the harpoon's butt coiled on the ground
    for wx, wy in [(30, 92), (77, 55)]:
        R.pxs([(wx - 1, wy + 2), (wx + 1, wy + 2), (wx + 2, wy + 1)], "#99969a")
    strand(R, [(16, 104), (10, 110), (16, 113), (26, 112), (20, 108)], ROPE)
    strand(R, [(20, 108), (13, 111)], ROPE_DK)
    return R


# ==============================================================================================
# C - The Flensed: stripped of its blubber, crawling on its own ribs, a jaw of bare bone
# ==============================================================================================

def flensed():
    S = sc.Scene(W, H)
    horror_light(S)
    m = materials(S)
    S.group()
    # the stripped body, raw muscle, side-on, the tail raised behind it
    S.ell((62, 60, -4), (30, 17, 16), m.meat, rot=(0, 0, -6))
    S.cone((88, 56, -4), (100, 34, -2), 9, 4, m.meat, k=3.0)
    S.ell((96, 27, -2), (6, 2.2, 8), m.bone, k=1.0, rot=(0, 0, -70))
    S.ell((101, 33, -2), (6, 2.2, 8), m.bone, k=1.0, rot=(0, 0, -10))
    # the skull, bare bone, and the long jaw hanging open beneath it
    S.ell((26, 58, 4), (23, 11, 12), m.bone, k=4.0, rot=(0, 0, 8))
    S.ell((40, 54, 2), (12, 13, 12), m.bone, k=4.0)
    S.carve_sphere((38, 53, 14), 3.8, k=1.0, mat=m.meat)
    S.cone((40, 70, 8), (4, 80, 10), 3.6, 1.8, m.bone, k=1.5)
    # strips of blubber left hanging off the flensed back
    for x, y, l in [(52, 44, 10), (64, 42, 13), (76, 45, 9)]:
        S.ell((x, y + l * 0.5, 10), (2.2, l * 0.6, 1.6), m.fat, k=1.5)
    # the ribs, crawling: bare white arcs down to the ground on both sides
    S.group(k=0.8)
    for i, x in enumerate((44, 56, 68, 80)):
        for side, z, dx in ((1, 12, -6), (-1, -14, 6)):
            top = (x, 64, z * 0.6)
            knee = (x + dx * 1.9, 84, z * 1.2)
            foot = (x + dx * 0.9, 112, z * 0.8)
            mat = m.bone
            S.chain([top, knee, foot], [2.0, 1.6, 1.1], mat, k=0.8)
    R = S.render(ss=2)
    R.cleanup()
    # muscle striations, the eye in the skull, teeth along the jaw
    for x0 in range(40, 92, 5):
        strand(R, [(x0, 48), (x0 - 2, 70)], "#4a1018", only=(m.meat,))
    R.pxs([(38, 53), (39, 53)], "#f4e6c8")
    R.px(38, 54, "#0a0806")
    for t in np.linspace(0.1, 0.9, 8):
        x, y = int(40 + (4 - 40) * t), int(70 + (80 - 70) * t) - 2
        if R.on(x, y + 1, m.bone):
            R.px(x, y, "#ebe3c6")
    # the flensing hook still in its back, and its chain
    strand(R, [(70, 40), (72, 34), (76, 30), (79, 33)], "#5e321a")
    strand(R, [(76, 30), (76, 18)], "#3a1e10")
    return R


CONCEPTS = {"a": harpooner, "b": old_iron, "c": flensed}
LABELS = {"a": ("A  -  The Harpooner", "a whaler's arms and harpoon; throw and reel"),
          "b": ("B  -  Old Iron", "bristling with every harpoon; it gives them back"),
          "c": ("C  -  The Flensed", "cut up alive; its jaw is the harpoon")}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "art/concepts"
    which = args[1:] or list(CONCEPTS)
    os.makedirs(out, exist_ok=True)
    bg = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_bg.png")).convert("RGBA")
    scenes = []
    for k in which:
        img = CONCEPTS[k]().to_rgba()
        sc.save(img, os.path.join(out, f"whale_{k}_x6.png"), 6)
        scenes.append(compose(img, bg))
        print("rendered", k)
    sheet(scenes, [LABELS[k] for k in which], os.path.join(out, "whale_options.png"))
    print("sheet:", os.path.join(out, "whale_options.png"))
