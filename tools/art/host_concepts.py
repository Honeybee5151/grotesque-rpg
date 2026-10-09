"""The Host: three concepts for the tutorial monster (a possessed man ridden by the Sucker Frog).

    python3 tools/art/host_concepts.py OUTDIR [a b c]
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import sculpt as sc

W, H = 104, 118

PAL = {
    "skin":  dict(ramp=["#1d1524", "#352c3c", "#544c58", "#78727a", "#a29c94"], outline="#100a16"),
    "frog":  dict(ramp=["#141a14", "#232f1e", "#3a4626", "#5a6530", "#848a40"], outline="#090d08",
                  spec="#d8e2a8", shin=24.0, spec_thr=0.5),
    "belly": dict(ramp=["#2e241c", "#4f4030", "#7a6646", "#a48e60", "#c8b684"], outline="#140e0a",
                  spec="#f2e8c0", shin=24.0, spec_thr=0.55),
    "flesh": dict(ramp=["#3a0a1e", "#681430", "#9c2646", "#cc4862", "#ee8696"], outline="#1a0510",
                  spec="#ffd6dc", shin=20.0, spec_thr=0.45),
    "brain": dict(ramp=["#3e1428", "#6e2a44", "#9c4a64", "#c47486", "#e6a6b0"], outline="#1c0812",
                  spec="#ffe0e6", shin=18.0, spec_thr=0.5),
    "shirt": dict(ramp=["#1a161e", "#2b252e", "#403840", "#59504f", "#766a60"], outline="#0e0b11"),
    "pants": dict(ramp=["#0e0b12", "#18131c", "#241d29", "#322a37", "#433946"], outline="#07050a"),
    "eye":   dict(ramp=["#3a1e04", "#6e3a0a", "#a85e12", "#d88a1c", "#f4c040"], outline="#140a02",
                  spec="#fff2c0", shin=30.0, spec_thr=0.5),
    "redeye": dict(ramp=["#3a0606", "#771010", "#b82020", "#e04a3a", "#fb8a76"], outline="#140202",
                   spec="#ffffff", shin=30.0, spec_thr=0.5),
    "bone":  dict(ramp=["#3e352e", "#6c614f", "#9b8f74", "#c7bc9c", "#ebe3c6"], outline="#16110c"),
}


def horror_light(S):
    """Harsh, mostly-overhead light; cold rim from behind-right."""
    S.L = unit((-0.4, -0.78, 0.52))
    S.ambient = 0.18
    S.thresholds = [0.2, 0.36, 0.56, 0.8]
    S.rim_col = sc.hexc("#3e5a62")


class M:
    pass


def materials(S, coiled=False):
    m = M()
    for name in ["skin", "frog", "belly", "flesh", "brain", "shirt", "pants", "eye", "bone"]:
        key = "redeye" if (name == "eye" and coiled) else name
        setattr(m, name, S.mat(name, **PAL[key]))
    return m


def unit(v):
    v = np.array(v, float)
    return v / np.linalg.norm(v)


# ----------------------------------------------------------------------------------------------
# hand-painting helpers
# ----------------------------------------------------------------------------------------------

def warts(R, mat_idx, n, seed, hi, lo, box=None):
    rng = np.random.default_rng(seed)
    placed = 0
    tries = 0
    while placed < n and tries < n * 60:
        tries += 1
        x = int(rng.integers(1, R.w - 2))
        y = int(rng.integers(1, R.h - 2))
        if box and not (box[0] <= x <= box[2] and box[1] <= y <= box[3]):
            continue
        c = R.code[y, x]
        if c < 0 or c // 8 != mat_idx or c % 8 not in (1, 2, 3):
            continue
        if R.code[y + 1, x] // 8 != mat_idx or (x, y) in R.over:
            continue
        R.px(x, y, hi)
        R.px(x, y + 1, lo)
        placed += 1


def strand(R, pts, col, only=None):
    """Polyline that only paints over pixels of the given materials (None = anywhere)."""
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = int(max(abs(x1 - x0), abs(y1 - y0)))
        for j in range(n + 1):
            t = j / max(n, 1)
            x, y = round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t)
            if only is None or (0 <= x < R.w and 0 <= y < R.h and R.mat[y, x] in only):
                R.px(x, y, col)


def edge_line(R, inner, outer, col, only_dirs=((0, -1), (0, 1), (-1, 0), (1, 0))):
    """Paint pixels of material `outer` that touch material `inner` (e.g. a bone rim on cut skin)."""
    mat = R.mat
    for y in range(1, R.h - 1):
        for x in range(1, R.w - 1):
            if mat[y, x] != outer:
                continue
            for dx, dy in only_dirs:
                if mat[y + dy, x + dx] == inner:
                    R.px(x, y, col)
                    break


SLIME, SLIME_HI = "#6f8c90", "#cfe6e4"
VEIN, VEIN_HI = "#3a1226", "#8a2a48"
HAIR = "#0f0a12"


# ==============================================================================================
# A - The Rider: full body, limp like a marionette; frog crouched on his shoulders
# ==============================================================================================

def concept_a(coiled=False):
    S = sc.Scene(W, H)
    horror_light(S)
    m = materials(S, coiled)

    # --- the man ---------------------------------------------------------------------------
    S.group()
    S.ell((51.5, 76, 0), (11, 6.5, 7), m.pants)
    S.cone((46, 78, 0), (45.5, 95, 1), 6.2, 4.3, m.pants, k=1.5)
    S.cone((45.5, 95, 1), (41, 111, 0), 4.3, 3.2, m.pants, k=1.0)
    S.cone((57, 78, 0), (57.5, 95, 1), 6.2, 4.3, m.pants, k=1.5)
    S.cone((57.5, 95, 1), (63, 111, 0), 4.3, 3.2, m.pants, k=1.0)
    S.ell((40, 113.5, 2.5), (4.5, 2.3, 5), m.skin, k=1.0)
    S.ell((64, 113.5, 2.5), (4.5, 2.3, 5), m.skin, k=1.0, rot=(0, 0, 10))

    S.cone((51.5, 73, 0), (51, 55, 1.5), 9.5, 11, m.shirt, k=2.0)
    S.ell((51, 51, 2), (13, 8.5, 8.5), m.shirt, k=2.5)
    S.sphere((39, 50.5, 0), 5.5, m.shirt, k=2.0)
    S.sphere((63.5, 47, 0), 5.5, m.shirt, k=2.0)
    S.cone((39, 50.5, 0), (35, 66, 1.5), 4.4, 3.6, m.shirt, k=1.5)
    S.cone((63.5, 47, 0), (68.5, 62, 1.5), 4.4, 3.6, m.shirt, k=1.5)
    S.cone((35, 66, 1.5), (34.5, 84, 2.5), 3.2, 2.4, m.skin, k=1.0)
    S.cone((68.5, 62, 1.5), (67.5, 79, 2.5), 3.2, 2.4, m.skin, k=1.0)
    S.ell((34.5, 87, 2.5), (2.8, 3.6, 1.8), m.skin, k=1.0)
    S.ell((67.5, 82, 2.5), (2.8, 3.6, 1.8), m.skin, k=1.0)
    for a, b in [((33, 89, 2.5), (31, 98, 2.5)), ((35, 90, 3), (34.5, 100, 3)),
                 ((36.5, 89, 2.5), (38, 97, 2.5)), ((33, 86, 3.5), (30.5, 91, 3.5)),
                 ((66, 84, 2.5), (64.5, 92, 2.5)), ((67.5, 85, 3), (67.5, 94, 3)),
                 ((69, 84, 2.5), (70.5, 91, 2.5)), ((66, 81, 3.5), (63.5, 85, 3.5))]:
        S.cone(a, b, 1.0, 0.75, m.skin, k=0.6)

    S.cone((50, 46, 1.5), (46.5, 40, 2.5), 3.8, 3.4, m.skin, k=1.5)
    S.ell((44, 31, 3), (8.5, 10.5, 9), m.skin, k=1.5, rot=(0, 0, -18))
    S.ell((42.5, 40, 4.5), (6, 3.8, 6), m.skin, k=1.5, rot=(0, 0, -18))
    S.carve_ell((42.6, 39.6, 11), (3.2, 2.8, 5), k=0.8, mat=m.flesh, rot=(0, 0, -18))
    S.carve_sphere((40.2, 29.5, 10.5), 2.8, k=1.0)
    S.carve_sphere((47.6, 28.0, 10.2), 2.7, k=1.0)
    S.cone((44.7, 30.5, 11.2), (45.3, 34.5, 12.0), 1.2, 1.5, m.skin, k=0.8)
    S.carve_sphere((41.2, 21.0, 5.5), 5.4, k=1.0, mat=m.brain)

    # --- the frog ----------------------------------------------------------------------------
    S.group(k=0.0)
    S.ell((59, 28, -5), (15, 12, 12), m.frog, rot=(0, 0, 8))
    S.ell((57.5, 34, 1), (10, 6.5, 7), m.belly, k=2.0)
    S.ell((56, 17.5, 0), (11.5, 8, 9), m.frog, k=3.0, rot=(0, 0, -14))
    # hind legs over the shoulders, toes splayed on his chest
    S.ell((41.5, 42, -1), (7, 5.5, 6), m.frog, k=2.0, rot=(0, 0, -20))
    S.ell((68, 40, -1), (7, 5.5, 6), m.frog, k=2.0, rot=(0, 0, 25))
    S.cone((41, 45, 2), (43.5, 55, 5), 3.2, 2.4, m.frog, k=1.2)
    S.cone((68, 43, 2), (65, 54, 5), 3.2, 2.4, m.frog, k=1.2)
    for base, tips in [((43.5, 55, 5), [(41, 59, 6), (43.5, 60, 6.5), (46, 58.5, 6)]),
                       ((65, 54, 5), [(62.5, 58, 6), (65, 59.5, 6.5), (67.5, 58, 6)])]:
        for tip in tips:
            S.cone(base, tip, 1.0, 0.8, m.frog, k=0.6)
            S.sphere(tip, 1.25, m.frog, k=0.5)
    # forelimbs: one clamped over his eye, one around his throat
    S.chain([(46, 26, 0), (38, 24, 6), (36, 30, 11)], [3.0, 2.4, 2.0], m.frog, k=1.2)
    for tip in [(33.5, 34, 12), (36.5, 35.5, 12.5), (39.5, 34, 12)]:
        S.cone((36, 30, 11), tip, 0.95, 0.8, m.frog, k=0.6)
        S.sphere(tip, 1.25, m.frog, k=0.5)
    S.chain([(66, 32, -1), (63, 40, 4), (56, 42, 7)], [3.0, 2.4, 2.0], m.frog, k=1.2)
    for tip in [(52.5, 43, 8), (53.5, 45.5, 8), (56, 46.5, 8)]:
        S.cone((56, 42, 7), tip, 0.95, 0.8, m.frog, k=0.6)
        S.sphere(tip, 1.25, m.frog, k=0.5)

    # eyes: small, sunk into the skull, heavy lids
    S.group(k=0.6)
    S.sphere((49, 12.6, 4.6), 2.9, m.eye)
    S.sphere((61.2, 10.4, 3.6), 2.9, m.eye)
    S.group(k=0.8)
    S.ell((49, 11.0, 4.4), (3.8, 2.2, 3.4), m.frog, rot=(0, 0, -14))
    S.ell((61.2, 8.8, 3.4), (3.8, 2.2, 3.4), m.frog, rot=(0, 0, 10))

    # the sucker: stalk from its chin, lips clamped on the open crown (fuses into both)
    S.group(k=1.6)
    S.chain([(52, 22.5, 4), (48, 19.5, 6.5), (44, 20, 7)], [2.6, 2.4, 3.6], m.flesh, k=1.0)
    S.sphere((48.6, 19.6, 6.8), 2.9, m.flesh, k=1.2)
    S.torus((41.4, 21.4, 5.8), unit((-0.3, -0.8, 0.5)), 4.6, 1.7, m.flesh, k=1.0)
    S.group(k=1.0)
    S.sphere((41.4, 22.4, 4.4), 4.3, m.brain)

    R = S.render(ss=2)
    R.cleanup()
    detail_a(R, m, coiled)
    return R


def detail_a(R, m, coiled):
    # frog: slit pupils, warts, a long frowning mouth that the stalk comes out of
    R.pxs([(46, 12), (46, 13), (61, 10), (61, 11)], "#0a0604")
    warts(R, m.frog, 18, 5, "#848a40", "#141a14", box=(34, 6, 76, 58))
    strand(R, [(53, 22), (56, 23), (60, 23), (64, 22), (66, 21)], "#090d08", only=(m.frog,))
    # the cut skull: a bone rim where scalp meets brain, veins running down the face
    edge_line(R, m.brain, m.skin, "#9b8f74")
    edge_line(R, m.flesh, m.skin, "#6c614f")
    for pts in [[(39, 25), (38, 28), (38, 31)], [(43, 25), (44, 28)], [(49, 25), (50, 28), (50, 31)]]:
        strand(R, pts, VEIN, only=(m.skin,))
    for pts in [[(37, 21), (39, 22), (41, 21)], [(39, 18), (41, 19), (43, 18)], [(42, 23), (44, 24)], [(44, 20), (46, 21)]]:
        strand(R, pts, "#6e2a44", only=(m.brain, m.flesh))
    # his face: one pale rolled eye, a glint in the other socket, teeth, drool
    R.pxs([(47, 29), (48, 29), (48, 30)], "#c9c0a8")
    R.px(47, 30, "#a01818")
    R.px(40, 30, "#8e887c")
    for x in range(40, 46):
        R.px(x, 37, "#c7bc9c" if x % 2 == 0 else "#6c614f")
    strand(R, [(44, 42), (45, 46), (45, 50), (46, 54)], SLIME)
    R.pxs([(45, 47), (46, 53)], SLIME_HI)
    # shirt: open collar, a slime stain, rips, a ragged hem over the trousers
    R.poly([(44, 46), (47, 49), (48, 50), (49, 49), (52, 46)], "#0e0b11")
    R.pxs([(47, 47), (48, 47), (48, 48), (49, 47)], "#544c58")
    strand(R, [(46, 55), (46, 60), (47, 64)], "#2b252e", only=(m.shirt,))
    R.poly([(35, 60), (37, 62), (35, 64)], "#0e0b11")
    R.px(36, 62, "#78727a")
    R.poly([(69, 57), (67, 59), (69, 61)], "#0e0b11")
    for x in range(41, 63):
        dy = (0, 1, 2, 1, 0, 2, 1)[x % 7]
        R.px(x, 74 + dy, "#403840")
        R.px(x, 75 + dy, "#0e0b11")
    # nails, toe pads
    R.pxs([(31, 98), (34, 100), (38, 97), (64, 92), (67, 94), (70, 91), (30, 91), (63, 85)], "#6c614f")


# ==============================================================================================
# B - The Crown: close bust; the frog fused into the top of his skull, face in focus
# ==============================================================================================

def concept_b(coiled=False):
    S = sc.Scene(W, H)
    horror_light(S)
    m = materials(S, coiled)

    # --- the man (bust), head wrenched to one side ----------------------------------------------
    S.group()
    S.ell((52, 117, -2), (34, 14, 14), m.shirt)
    S.cone((52, 99, 0), (22, 109, 0), 8, 9, m.shirt, k=3.0)
    S.cone((52, 99, 0), (82, 108, 0), 8, 9, m.shirt, k=3.0)
    S.ell((52, 115, 5), (22, 11, 10), m.shirt, k=3.0)
    S.cone((52, 104, 2), (50, 84, 3), 8, 7, m.skin, k=2.0)
    S.ell((49, 62, 4), (16.5, 20, 15.5), m.skin, k=2.0, rot=(0, 0, -14))
    S.ell((51, 86, 6.5), (10.5, 7.5, 10.5), m.skin, k=3.5, rot=(0, 0, -4))
    S.sphere((39.5, 64.5, 13), 4.0, m.skin, k=3.0)
    S.sphere((58, 61, 13), 4.0, m.skin, k=3.0)
    S.ell((33, 65, 2), (2.6, 5, 3.2), m.skin, k=1.5, rot=(0, 0, -14))
    S.ell((65, 59, 2), (2.6, 5, 3.2), m.skin, k=1.5, rot=(0, 0, -14))
    S.carve_sphere((39.5, 72, 16), 3.6, k=2.0)
    S.carve_sphere((59.5, 69.5, 16), 3.6, k=2.0)
    S.carve_ell((50.5, 81, 16.5), (5.0, 8.4, 8), k=1.2, mat=m.flesh, rot=(0, 0, 5))
    S.carve_sphere((41, 61, 17.5), 4.6, k=1.5)
    S.carve_sphere((57, 58, 17.5), 4.6, k=1.5)
    S.cone((49, 61, 18.5), (50, 68, 20.5), 1.8, 2.5, m.skin, k=1.2)
    S.carve_ell((47.5, 45, 6), (15, 7, 14), k=2.0, mat=m.brain, rot=(0, 0, -14))
    S.group(k=0.6)
    S.sphere((41, 62, 13.2), 2.7, m.bone)
    S.sphere((57, 58.5, 15.0), 3.3, m.bone)
    S.group(k=1.6)
    S.ell((47.5, 45.5, 5), (13, 5.5, 12), m.brain, rot=(0, 0, -14))
    S.sphere((41.5, 45, 9), 4.2, m.brain, k=1.5)
    S.sphere((49.5, 42, 10), 4.6, m.brain, k=1.5)
    S.sphere((56, 40.5, 8.5), 3.8, m.brain, k=1.5)

    # --- the frog, leaning over the open skull, feeding -----------------------------------------
    S.group(k=0.0)
    S.ell((54, 20, -2), (19, 11.5, 12.5), m.frog, rot=(0, 0, 10))
    S.ell((52, 26, 6), (12, 5, 6), m.belly, k=2.0, rot=(0, 0, 10))
    S.ell((50, 13, 5), (13.5, 7.5, 10), m.frog, k=3.0, rot=(0, 0, 6))
    S.ell((31, 32, 0), (8, 7, 7), m.frog, k=2.0, rot=(0, 0, -20))
    S.ell((73, 28, 0), (8, 7, 7), m.frog, k=2.0, rot=(0, 0, 20))
    S.cone((29.5, 37, 3), (31.5, 58, 8), 4.0, 3.0, m.frog, k=1.2)
    S.cone((74, 33, 3), (68.5, 54, 8), 4.0, 3.0, m.frog, k=1.2)
    for base, tips in [((31.5, 58, 8), [(33, 64.5, 12), (35.5, 62.5, 13), (36.5, 59, 13)]),
                       ((68.5, 54, 8), [(66.5, 60.5, 12), (64, 58.5, 13), (63, 55, 13)])]:
        for tip in tips:
            S.cone(base, tip, 1.2, 0.9, m.frog, k=0.6)
            S.sphere(tip, 1.4, m.frog, k=0.5)
    for base, mid, tips in [((42, 27, 7), (40, 36, 11), [(37, 41.5, 12), (40, 43, 12.5), (43, 42, 12)]),
                            ((61, 26, 7), (61.5, 35, 11), [(58.5, 40.5, 12), (61.5, 41.5, 12.5), (64.5, 40, 12)])]:
        S.chain([base, mid], [3.2, 2.4], m.frog, k=1.2)
        for tip in tips:
            S.cone(mid, tip, 1.1, 0.9, m.frog, k=0.6)
            S.sphere(tip, 1.3, m.frog, k=0.5)
    S.group(k=0.6)
    S.sphere((41, 9.5, 9.2), 3.1, m.eye)
    S.sphere((58.5, 8, 9.2), 3.1, m.eye)
    S.group(k=0.8)
    S.ell((41, 7.8, 8.9), (4.1, 2.4, 3.7), m.frog, rot=(0, 0, -6))
    S.ell((58.5, 6.3, 8.9), (4.1, 2.4, 3.7), m.frog, rot=(0, 0, 14))

    # the sucker tube and tendrils, down into the brain
    S.group(k=1.4)
    S.chain([(51, 28, 9), (50, 33, 12), (49, 38, 13)], [2.6, 2.3, 3.0], m.flesh, k=1.0)
    S.torus((49, 39.5, 12.5), unit((0, -0.6, 0.8)), 3.0, 1.2, m.flesh, k=1.0)
    for pts, rr in [([(44, 28, 8), (42.5, 33, 10), (43.5, 39, 11)], [1.0, 0.8, 1.1]),
                    ([(46.5, 29, 9), (46, 34, 12), (45.5, 39, 13)], [0.9, 0.8, 1.0]),
                    ([(55, 29, 9), (56, 34, 12), (54.5, 39, 12.5)], [1.0, 0.85, 1.1]),
                    ([(58.5, 27.5, 8), (60, 33, 10), (58.5, 39, 10.5)], [0.85, 0.75, 1.0])]:
        S.chain(pts, rr, m.flesh, k=0.8)

    R = S.render(ss=2)
    R.cleanup()
    detail_b(R, m, coiled)
    return R


def detail_b(R, m, coiled):
    # frog: slit pupils, warts, mouth line
    R.pxs([(41, 9), (41, 10), (58, 8), (58, 9)], "#0a0604")
    warts(R, m.frog, 24, 7, "#848a40", "#141a14")
    strand(R, [(35, 20), (41, 21), (47, 22), (53, 21), (59, 19), (63, 17)], "#090d08", only=(m.frog,))
    # the cut skull rim, folds in the brain, veins down the forehead
    edge_line(R, m.brain, m.skin, "#9b8f74")
    for pts in [[(40, 44), (42, 45), (44, 44)], [(47, 45), (49, 46), (51, 45)], [(53, 42), (55, 43)], [(44, 47), (46, 48)]]:
        strand(R, pts, "#6e2a44", only=(m.brain,))
    for pts in [[(38, 51), (37, 54), (38, 57)], [(44, 52), (45, 55)], [(51, 51), (50, 54), (51, 57)], [(58, 49), (60, 52)]]:
        strand(R, pts, VEIN, only=(m.skin,))
    # eyes: left rolled up white and veined; right bulging, pupil looking somewhere else
    R.pxs([(39, 60), (41, 61)], "#a01818")
    R.pxs([(58, 54), (59, 54), (58, 55)], "#5a2010")
    R.px(59, 55, "#0a0604")
    R.pxs([(55, 56), (56, 57)], "#a01818")
    # tears of blood
    strand(R, [(56, 59), (56, 63), (57, 67), (57, 70)], "#7d1d3e", only=(m.skin, m.bone))
    R.px(57, 71, "#9c2646")
    strand(R, [(40, 64), (40, 68), (39, 72)], "#7d1d3e", only=(m.skin, m.bone))
    # teeth on the upper gum, a few on the dropped jaw, drool
    for x in range(45, 53):
        R.px(x, 72, "#c7bc9c" if x % 2 == 1 else "#6c614f")
    R.pxs([(47, 86), (49, 87), (51, 86)], "#9b8f74")
    strand(R, [(50, 91), (50, 95), (51, 99)], SLIME)
    R.px(50, 94, SLIME_HI)
    # collar
    R.poly([(42, 98), (47, 103), (52, 106), (57, 103), (62, 98)], "#0e0b11")


# ==============================================================================================
# C - The Hunched: bent forward on long arms, head hanging so the crown faces you;
#     the frog rides his back with a cord down into his skull
# ==============================================================================================

def concept_c(coiled=False):
    S = sc.Scene(W, H)
    horror_light(S)
    m = materials(S, coiled)

    # --- the man ------------------------------------------------------------------------------
    S.group()
    # legs, bent, mostly behind the arms
    S.cone((44, 70, -16), (39, 96, -4), 6, 4.6, m.pants)
    S.cone((39, 96, -4), (37, 112, -2), 4.6, 3.4, m.pants, k=1.0)
    S.cone((60, 70, -16), (65, 96, -4), 6, 4.6, m.pants, k=1.5)
    S.cone((65, 96, -4), (67, 112, -2), 4.6, 3.4, m.pants, k=1.0)
    S.ell((36, 114, 0), (4.5, 2.3, 5.5), m.skin, k=1.0)
    S.ell((68, 114, 0), (4.5, 2.3, 5.5), m.skin, k=1.0)
    # back, shoulders, chest
    S.ell((52, 54, -6), (20, 12.5, 14), m.shirt, k=2.0)
    S.sphere((31.5, 60, 0), 7, m.shirt, k=3.0)
    S.sphere((72.5, 58.5, 0), 7, m.shirt, k=3.0)
    S.ell((52, 66, -2), (16, 10, 12), m.shirt, k=3.0)
    for i, (y, z) in enumerate([(44, 6.5), (48.5, 7.6), (53, 8.2), (57.5, 8.0)]):
        S.sphere((52, y, z - 2.0), 2.4 - i * 0.15, m.shirt, k=1.6)
    # long arms to the floor
    S.cone((31.5, 60, 0), (23.5, 81, 4), 5, 4, m.shirt, k=2.0)
    S.cone((23.5, 81, 4), (27.5, 103, 6), 3.4, 2.7, m.skin, k=1.0)
    S.ell((27.5, 107.5, 7), (4.2, 3.6, 3.6), m.skin, k=1.0)
    S.cone((72.5, 58.5, 0), (81.5, 79, 3), 5, 4, m.shirt, k=2.0)
    S.cone((81.5, 79, 3), (77.5, 102, 6), 3.4, 2.7, m.skin, k=1.0)
    S.ell((77.5, 106.5, 7), (4.2, 3.6, 3.6), m.skin, k=1.0)
    for a, b in [((25, 109, 8), (23, 113.5, 9.5)), ((27.5, 110, 9), (27, 114.5, 10.5)), ((30, 109.5, 8.5), (31, 114, 10)),
                 ((75, 108, 8), (73.5, 113.5, 9.5)), ((77.5, 109, 9), (77.5, 114.5, 10.5)), ((80, 108.5, 8.5), (81.5, 113.5, 9.5))]:
        S.cone(a, b, 1.2, 0.95, m.skin, k=0.6)
    # neck forward-down, head hanging with the crown toward us
    S.cone((52, 57, 4), (52, 65, 10), 5, 4.5, m.skin, k=2.0)
    S.ell((52, 72, 12), (9.5, 10.5, 11), m.skin, k=1.5)
    S.ell((52, 83.5, 8), (6.5, 3.8, 6.5), m.skin, k=2.0)
    S.carve_sphere((52, 69.5, 23), 5.6, k=1.0, mat=m.brain)
    S.group(k=1.0)
    S.sphere((52, 69.5, 19.8), 4.6, m.brain)

    # --- the frog on his back -------------------------------------------------------------------
    S.group(k=0.0)
    S.ell((56, 34, -8), (14, 12, 11), m.frog)
    S.ell((55, 40, -1), (9, 7, 6), m.belly, k=2.0)
    S.ell((55, 23, -4), (11, 8, 9), m.frog, k=3.0)
    S.carve_ell((55, 27, 4.2), (7.5, 0.9, 3), k=0.4, mat=m.flesh)
    S.ell((43.5, 42, -8), (6, 5, 6), m.frog, k=2.0, rot=(0, 0, -25))
    S.ell((68.5, 42, -8), (6, 5, 6), m.frog, k=2.0, rot=(0, 0, 25))
    for base, tip0, tips in [((47, 41, -3), (44, 51, 2), [(41.5, 54, 3), (44, 55, 3.5), (46.5, 54, 3)]),
                             ((64, 41, -3), (66.5, 51, 1), [(64, 54, 2), (66.5, 55, 2.5), (69, 54, 2)])]:
        S.cone(base, tip0, 2.8, 2.1, m.frog, k=1.2)
        for tip in tips:
            S.cone(tip0, tip, 1.0, 0.8, m.frog, k=0.6)
            S.sphere(tip, 1.2, m.frog, k=0.5)
    S.group(k=0.6)
    S.sphere((49, 18.5, 0.5), 2.9, m.eye)
    S.sphere((61, 17.5, -0.5), 2.9, m.eye)
    S.group(k=0.8)
    S.ell((49, 17, 0.3), (3.8, 2.2, 3.4), m.frog, rot=(0, 0, -12))
    S.ell((61, 16, -0.7), (3.8, 2.2, 3.4), m.frog, rot=(0, 0, 12))

    # the cord: from its mouth, over his back, down into the crown
    S.group(k=1.4)
    S.chain([(54, 28, 2), (50.5, 36, 10), (52.5, 46, 16.5), (49.5, 56, 21), (52, 65.5, 23.5)],
            [2.4, 2.0, 2.0, 1.9, 2.8], m.flesh, k=1.0)
    S.sphere((51.6, 43.5, 15.6), 3.3, m.flesh, k=1.6)
    S.torus((52, 69.5, 22.8), unit((0, -0.25, 1)), 4.4, 1.6, m.flesh, k=1.0)

    R = S.render(ss=2)
    R.cleanup()
    detail_c(R, m, coiled)
    return R


def detail_c(R, m, coiled):
    # frog: slit pupils, warts, a long frowning mouth clamped around the cord
    for x, y in [(49, 18), (49, 19), (61, 17), (61, 18)]:
        R.px(x, y, "#0a0604")
    warts(R, m.frog, 16, 3, "#848a40", "#141a14", box=(40, 12, 72, 52))
    R.poly([(44, 28), (47, 27), (50, 26)], "#090d08")
    R.poly([(57, 26), (61, 27), (65, 28)], "#090d08")
    R.pxs([(51, 27), (56, 27)], SLIME_HI)
    # hair hanging from the dropped head
    for pts in [[(45, 62), (44, 70), (43, 78), (44, 86)], [(47, 65), (46, 74), (46, 84), (45, 88)],
                [(58, 64), (59, 72), (60, 80), (59, 87)], [(60, 61), (61, 69), (62, 78), (63, 84)],
                [(56, 67), (56, 76), (57, 85)], [(49, 73), (48, 80), (48, 86)]]:
        strand(R, pts, HAIR)
    # what's left of the face, in the shadow under the crown
    R.pxs([(49, 77), (55, 77)], "#c9c0a8")
    for x in range(48, 57):
        R.px(x, 82, "#c7bc9c" if x % 2 == 0 else "#6c614f")
    R.pxs([(49, 83), (51, 83), (53, 83), (55, 83)], "#9b8f74")
    strand(R, [(54, 84), (54, 92), (55, 99), (55, 104)], SLIME)
    R.pxs([(54, 88), (55, 101)], SLIME_HI)
    # veins crawling out from the sucker over the scalp, folds in the exposed brain
    for pts in [[(47, 66), (45, 64), (44, 61)], [(57, 67), (59, 65), (60, 62)], [(48, 72), (46, 74)], [(57, 72), (59, 74)]]:
        strand(R, pts, VEIN, only=(m.skin,))
    R.poly([(50, 68), (52, 69), (54, 68)], "#6e2a44")
    R.poly([(50, 71), (53, 71)], "#6e2a44")
    # torn shirt: a rip on the left shoulder showing skin, a stain trailing from the ring
    R.poly([(30, 56), (33, 58), (31, 60), (34, 62)], "#0e0b11")
    R.pxs([(32, 59), (33, 61)], "#78727a")
    R.poly([(70, 62), (72, 65), (70, 67)], "#0e0b11")
    R.pxs([(71, 64)], "#78727a")
    # yellowed nails on the floor
    R.pxs([(23, 113), (27, 114), (31, 113), (73, 113), (77, 114), (81, 113)], "#9b8f74")


CONCEPTS = {"a": concept_a, "b": concept_b, "c": concept_c}


def compose(img, bg, pos=(108, 4)):
    canvas = bg.copy()
    canvas.alpha_composite(Image.fromarray(img, "RGBA"), pos)
    return canvas


if __name__ == "__main__":
    out = sys.argv[1]
    which = sys.argv[2:] or list(CONCEPTS)
    bg = Image.open(os.path.join(out, "bg.png")).convert("RGBA")
    for k in which:
        for coiled in (False,):
            R = CONCEPTS[k](coiled)
            img = R.to_rgba()
            tag = f"{k}{'_coil' if coiled else ''}"
            sc.save(img, os.path.join(out, f"host_{tag}.png"))
            sc.save(img, os.path.join(out, f"host_{tag}_x6.png"), 6)
            scene = compose(img, bg).crop((60, 0, 260, 124))
            scene.resize((scene.width * 4, scene.height * 4), Image.NEAREST).save(os.path.join(out, f"scene_{tag}.png"))
            print("wrote", tag)
