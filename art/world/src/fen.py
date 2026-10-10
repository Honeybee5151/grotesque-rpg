"""Sallow Fen tiles (Hollowell): peat, dead grass, cobbles, black water and boardwalks.

Atlas layout - keep in sync with FEN in scripts/world/tiles.gd. 16 columns; a "masked" row has one
tile per neighbour mask (bit 1 = up, 2 = right, 4 = down, 8 = left; a set bit means that neighbour
is the other kind: land for water tiles, water for land tiles).
    rows 0-1  ~  water, 2 variants, masked
    rows 2-4  .  peat, 3 variants, masked
    rows 5-6  ,  dead grass, 2 variants, masked
    row  7    o  cobbles, 4 variants (columns 0-3)
    row  8    |  boardwalk running up/down, masked
    row  9    =  boardwalk running left/right, masked
"""
import numpy as np

from pix import Canvas

# Dread palette: the battle cave's violets, peat browns, reed grey-greens. Authored as if lit by a
# lantern; the in-game darkness overlay does the rest. 5 steps, dark -> light, shadows lean purple.
PEAT = ["#130d12", "#21171c", "#2f2228", "#413035", "#584346"]
GRASS = ["#161b16", "#232c20", "#33402c", "#48573a", "#66734c"]
WATER = ["#06050b", "#0c0b17", "#141428", "#1f2240", "#323a5c"]
WOOD = ["#140c0f", "#23171b", "#35252a", "#4a3437", "#644a49"]
STONE = ["#141219", "#221e29", "#332e3b", "#48424f", "#655e69"]

ROWS = 10


def _rng(*key):
    return np.random.default_rng(abs(hash(("fen",) + key)) % (2 ** 32))


def _seeded(seed):
    return np.random.default_rng(seed)


# --------------------------------------------------------------------------------------------
# bases
# --------------------------------------------------------------------------------------------

def peat(seed):
    r = _seeded(1000 + seed)
    t = Canvas(16, 16)
    t.rect(0, 0, 16, 16, PEAT[2])
    for _ in range(7):                      # clods: a dark lump with a lit top edge
        x, y = int(r.integers(0, 15)), int(r.integers(1, 15))
        w = int(r.integers(2, 4))
        t.hline(x, x + w - 1, y, PEAT[1])
        if r.random() < 0.5:
            t.hline(x + 1, x + w - 1, y + 1, PEAT[1])
        t.hline(x, x + w - 2, y - 1, PEAT[3])
    for _ in range(3):                      # pits
        t.px(int(r.integers(0, 16)), int(r.integers(0, 16)), PEAT[0])
    if r.random() < 0.6:                    # a root
        x, y = int(r.integers(2, 11)), int(r.integers(3, 13))
        t.line(x, y, x + 3, y + int(r.integers(-1, 2)), WOOD[1])
    return t


def tuft(t, x, y, r):
    h = int(r.integers(2, 4))
    t.vline(x, y - h, y, GRASS[2])
    t.px(x, y - h, GRASS[4])
    t.line(x - 1, y, x - 2, y - h + 1, GRASS[1])
    t.px(x - 2, y - h + 1, GRASS[3])
    t.line(x + 1, y, x + 2, y - h + 2, GRASS[1])
    t.px(x, y + 1, PEAT[0])
    t.px(x - 1, y + 1, PEAT[1])


def grass(seed):
    r = _seeded(2000 + seed)
    t = peat(seed + 7)
    for _ in range(4):
        tuft(t, int(r.integers(2, 14)), int(r.integers(4, 14)), r)
    return t


def water(seed):
    r = _seeded(3000 + seed)
    t = Canvas(16, 16)
    t.rect(0, 0, 16, 16, WATER[1])
    for _ in range(3):                      # slow ripples
        x, y, n = int(r.integers(0, 13)), int(r.integers(1, 15)), int(r.integers(2, 5))
        t.hline(x, x + n - 1, y, WATER[2])
        if r.random() < 0.45:
            t.px(x + n // 2, y, WATER[3])
    for _ in range(2):                      # muck
        t.px(int(r.integers(0, 16)), int(r.integers(0, 16)), WATER[0])
    return t


def cobble(seed):
    """Worn flagstones bedded in mud: irregular slabs, lit top-left, mud showing between."""
    r = _seeded(4000 + seed)
    t = peat(seed + 20)
    slabs = [
        [(0, 0, 7, 5), (8, 0, 8, 4), (0, 6, 5, 5), (6, 5, 6, 6), (13, 5, 3, 5), (0, 12, 8, 4), (9, 12, 7, 4)],
        [(0, 0, 5, 6), (6, 0, 6, 4), (12, 1, 4, 6), (0, 7, 9, 4), (10, 7, 6, 5), (1, 12, 5, 4), (7, 12, 9, 4)],
        [(1, 0, 9, 4), (11, 0, 5, 7), (0, 5, 4, 6), (5, 5, 6, 5), (0, 12, 6, 4), (7, 11, 4, 5), (12, 8, 4, 8)],
        [(0, 1, 4, 5), (5, 0, 7, 5), (13, 0, 3, 4), (0, 7, 7, 4), (8, 6, 8, 5), (0, 12, 10, 4), (11, 12, 5, 4)],
    ][seed % 4]
    for x, y, w, h in slabs:
        x += int(r.integers(0, 2))
        y += int(r.integers(0, 2))
        w -= int(r.integers(1, 3))
        h -= int(r.integers(0, 2))
        if w < 2 or h < 2:
            continue
        t.rect(x, y, w, h, STONE[2])
        t.hline(x, x + w - 1, y, STONE[3])
        t.px(x, y, STONE[4])
        t.vline(x, y + 1, y + h - 1, STONE[3])
        t.hline(x + 1, x + w - 1, y + h - 1, STONE[1])
        # knock the corners off so they read as worn slabs, not bricks
        for cx, cy in ((x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
            if r.random() < 0.7:
                t.px(cx, cy, PEAT[1])
        if r.random() < 0.5:
            t.px(x + int(r.integers(1, max(2, w - 1))), y + int(r.integers(1, max(2, h - 1))), STONE[1])
    return t


# --------------------------------------------------------------------------------------------
# edges
# --------------------------------------------------------------------------------------------

def water_edges(t, mask, seed):
    r = _seeded(5000 + seed * 16 + mask)
    if mask & 8:                            # land to the left
        t.vline(0, 0, 15, PEAT[1])
        t.vline(1, 0, 15, WATER[0])
    if mask & 2:                            # land to the right
        t.vline(15, 0, 15, PEAT[1])
        t.vline(14, 0, 15, WATER[0])
    if mask & 4:                            # land below: the wet shoreline
        for x in range(16):
            if r.random() < 0.7:
                t.px(x, 15, WATER[3])
        t.hline(0, 15, 14, WATER[2])
    if mask & 1:                            # land above: its bank face drops into the water
        t.rect(0, 0, 16, 3, PEAT[1])
        t.hline(0, 15, 0, PEAT[2])
        for x in range(16):
            if r.random() < 0.3:
                t.vline(x, 1, 2, PEAT[0])
        t.hline(0, 15, 3, WATER[0])
        for _ in range(3):                  # roots trailing into the water
            x = int(r.integers(0, 16))
            t.vline(x, 3, 3 + int(r.integers(1, 3)), PEAT[0])
        for x in range(16):
            if r.random() < 0.35:
                t.px(x, 4, WATER[2])


def _cut_corner(t, corner, rad=4):
    """Round a convex land corner: pixels outside a quarter circle become water, with a dark rim."""
    cx = rad if corner in ("tl", "bl") else 16 - rad
    cy = rad if corner in ("tl", "tr") else 16 - rad
    xs = range(0, rad) if corner in ("tl", "bl") else range(16 - rad, 16)
    ys = range(0, rad) if corner in ("tl", "tr") else range(16 - rad, 16)
    cut = set()
    for y in ys:
        for x in xs:
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 > rad * rad:
                t.px(x, y, WATER[1])
                cut.add((x, y))
    for y in ys:
        for x in xs:
            if (x, y) in cut:
                continue
            if any((x + dx, y + dy) in cut for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                t.px(x, y, PEAT[4] if corner in ("bl", "br") else PEAT[0])


def land_edges(t, mask, seed):
    r = _seeded(6000 + seed * 16 + mask)
    if mask & 8:                            # water to the left
        t.vline(0, 0, 15, PEAT[0])
    if mask & 2:                            # water to the right
        t.vline(15, 0, 15, PEAT[0])
    if mask & 1:                            # water above: wet rim with reeds
        t.hline(0, 15, 0, PEAT[0])
        t.hline(0, 15, 1, PEAT[1])
        for _ in range(2):
            x = int(r.integers(3, 13))
            t.vline(x, 0, 2, GRASS[2])
            t.px(x, 0, GRASS[3])
    if mask & 4:                            # water below: the lip of the bank catches the light
        t.hline(0, 15, 15, PEAT[4])
        t.hline(0, 15, 14, PEAT[3])
    # round the top corners; bottom corners stay square, where the bank face reads as a drop
    if mask & 1 and mask & 8:
        _cut_corner(t, "tl", 9)
    if mask & 1 and mask & 2:
        _cut_corner(t, "tr", 9)


# --------------------------------------------------------------------------------------------
# boardwalks (drawn over masked water)
# --------------------------------------------------------------------------------------------

def walk_v(t):
    t.vline(1, 0, 15, WOOD[1])
    t.vline(14, 0, 15, WOOD[0])
    for y in range(0, 16, 4):
        t.rect(2, y, 12, 3, WOOD[2])
        t.hline(2, 13, y, WOOD[3])
        t.px(2, y, WOOD[4])
        t.hline(2, 13, y + 3, WOOD[0])
        t.px(4 + (y * 3) % 8, y + 1, WOOD[1])   # nail / knot
    t.rect(0, 12, 1, 4, WOOD[1])             # posts
    t.rect(15, 12, 1, 4, WOOD[0])


def walk_h(t):
    t.hline(0, 15, 1, WOOD[1])
    for x in range(0, 16, 4):
        t.rect(x, 2, 3, 10, WOOD[2])
        t.vline(x, 2, 11, WOOD[3])
        t.px(x, 2, WOOD[4])
        t.vline(x + 3, 2, 11, WOOD[0])
        t.px(x + 1, 4 + (x * 5) % 6, WOOD[1])
    t.hline(0, 15, 12, WOOD[1])              # front edge, then its shadow on the water
    t.hline(0, 15, 13, WOOD[0])
    for px_ in (3, 11):                       # posts into the water, with a reflection
        t.rect(px_, 14, 2, 2, WOOD[1])
        t.px(px_ + 1, 14, WOOD[0])


# --------------------------------------------------------------------------------------------
# atlas
# --------------------------------------------------------------------------------------------

def atlas():
    a = Canvas(16 * 16, 16 * ROWS)

    def put(tile, col, row):
        a.blit(tile, col * 16, row * 16)

    for v in range(2):
        for m in range(16):
            t = water(v)
            water_edges(t, m, v)
            put(t, m, 0 + v)
    for v in range(3):
        for m in range(16):
            t = peat(v)
            land_edges(t, m, v)
            put(t, m, 2 + v)
    for v in range(2):
        for m in range(16):
            t = grass(v)
            land_edges(t, m, v + 3)
            put(t, m, 5 + v)
    for v in range(4):
        put(cobble(v), v, 7)
    for m in range(16):
        t = water(2)
        water_edges(t, m, 9)
        walk_v(t)
        put(t, m, 8)
        t = water(3)
        water_edges(t, m, 10)
        walk_h(t)
        put(t, m, 9)
    return a
