"""The flooded cave under Hollowell's well. Palette follows the battle backdrop's violets so the walk
into the Host and the fight feel like one place.

Atlas layout - keep in sync with CAVE in scripts/world/tiles.gd. 16 columns; masked rows have one
tile per neighbour mask (bit 1 up, 2 right, 4 down, 8 left).
    rows 0-1  .  floor, 2 variants; bit set where the neighbour is rock (#)
    rows 2-3  #  rock, 2 variants; bit set where the neighbour is NOT rock (a face shows below it)
    row  4    ~  black water; bit set where the neighbour is not water
    row  5    ,  floor crusted with frogspawn, 4 variants (columns 0-3), no mask
"""
import numpy as np

from pix import Canvas
from fen import WATER

FLOOR = ["#0b0811", "#130e1a", "#1b1524", "#251c30", "#33283f"]
ROCK = ["#06040a", "#0d0a13", "#151020", "#1f182c", "#2c233b"]
FACE = ["#100b16", "#1a1323", "#251c31", "#332842", "#463756"]
SPAWN = ["#05040a", "#2c2c3a", "#4a4a5e", "#8c8ca6"]       # egg, jelly dark, jelly, glint
ROWS = 6


def _r(seed):
    return np.random.default_rng(seed)


def floor(seed):
    r = _r(7000 + seed)
    t = Canvas(16, 16)
    t.rect(0, 0, 16, 16, FLOOR[2])
    for _ in range(6):
        x, y = int(r.integers(0, 15)), int(r.integers(1, 15))
        n = int(r.integers(2, 4))
        t.hline(x, x + n - 1, y, FLOOR[1])
        t.hline(x, x + n - 2, y - 1, FLOOR[3])
    for _ in range(4):
        t.px(int(r.integers(0, 16)), int(r.integers(0, 16)), FLOOR[0])
    if r.random() < 0.5:                       # a wet sheen
        x, y = int(r.integers(2, 11)), int(r.integers(3, 13))
        t.hline(x, x + 3, y, FLOOR[3])
        t.px(x + 1, y, FLOOR[4])
    return t


def floor_edges(t, mask):
    if mask & 1:                               # rock above: its face shades the floor
        t.rect(0, 0, 16, 3, FLOOR[0])
        for x in range(0, 16, 2):
            t.px(x, 3, FLOOR[1])
    if mask & 8:
        t.vline(0, 0, 15, FLOOR[1])
    if mask & 2:
        t.vline(15, 0, 15, FLOOR[1])
    if mask & 4:
        t.hline(0, 15, 15, FLOOR[1])


def rock(seed, mask):
    """Rock seen from above; where open ground is below it, its face shows in the lower part."""
    r = _r(8000 + seed * 16 + mask)
    t = Canvas(16, 16)
    t.rect(0, 0, 16, 16, ROCK[1])
    for _ in range(5):
        x, y = int(r.integers(0, 15)), int(r.integers(0, 15))
        t.hline(x, x + int(r.integers(1, 3)), y, ROCK[2])
    face_top = 5 if mask & 4 else 16
    if mask & 1:                               # an open edge above: a lit lip
        t.hline(0, 15, 0, ROCK[3])
        t.hline(0, 15, 1, ROCK[2])
    if mask & 8:
        t.vline(0, 0, face_top - 1, ROCK[3])
    if mask & 2:
        t.vline(15, 0, face_top - 1, ROCK[0])
    if mask & 4:                               # the face: striated, lit from the upper left
        t.hline(0, 15, face_top - 1, ROCK[4])
        for y in range(face_top, 16):
            for x in range(16):
                k = (x * 5 + (y // 3) * 7 + seed * 3) % 9
                col = FACE[2] if k > 2 else FACE[1]
                if y == face_top:
                    col = FACE[4] if x % 5 else FACE[3]
                elif k == 0:
                    col = FACE[3]
                elif y > 13:
                    col = FACE[1] if k > 3 else FACE[0]
                t.px(x, y, col)
        for _ in range(3):                     # cracks running down the face
            x = int(r.integers(1, 15))
            t.vline(x, face_top + 1, int(r.integers(face_top + 3, 16)), FACE[0])
        if mask & 8:
            t.vline(0, face_top, 15, FACE[3])
        if mask & 2:
            t.vline(15, face_top, 15, FACE[0])
    return t


def water(mask, seed):
    r = _r(9000 + seed * 16 + mask)
    t = Canvas(16, 16)
    t.rect(0, 0, 16, 16, WATER[0])
    for _ in range(2):
        x, y = int(r.integers(0, 13)), int(r.integers(2, 14))
        t.hline(x, x + int(r.integers(1, 4)), y, WATER[2])
    if mask & 1:
        t.rect(0, 0, 16, 2, FACE[2])
        t.hline(0, 15, 0, FACE[3])
        t.hline(0, 15, 2, WATER[0])
        for x in range(16):
            if r.random() < 0.4:
                t.px(x, 3, WATER[2])
    if mask & 4:
        for x in range(16):
            if r.random() < 0.6:
                t.px(x, 15, WATER[3])
    if mask & 8:
        t.vline(0, 0, 15, FLOOR[1])
    if mask & 2:
        t.vline(15, 0, 15, FLOOR[1])
    return t


def spawn_floor(seed):
    """Floor crusted with frogspawn: clumps of black eggs in grey jelly."""
    r = _r(9500 + seed)
    t = floor(seed + 30)
    for _ in range(3 + seed % 2):
        cx, cy = int(r.integers(3, 13)), int(r.integers(3, 13))
        for _ in range(9):
            x, y = cx + int(r.integers(-3, 3)), cy + int(r.integers(-2, 2))
            t.rect(x, y, 2, 2, SPAWN[2])
            t.px(x, y, SPAWN[3] if r.random() < 0.3 else SPAWN[2])
            t.px(x + 1, y + 1, SPAWN[0])
        t.hline(cx - 3, cx + 2, cy + 2, SPAWN[1])
    return t


def atlas():
    a = Canvas(16 * 16, 16 * ROWS)

    def put(tile, col, row):
        a.blit(tile, col * 16, row * 16)

    for v in range(2):
        for m in range(16):
            t = floor(v)
            floor_edges(t, m)
            put(t, m, 0 + v)
            put(rock(v, m), m, 2 + v)
    for m in range(16):
        put(water(m, 0), m, 4)
    for v in range(4):
        put(spawn_floor(v), v, 5)
    return a


# --------------------------------------------------------------------------------------------
# props
# --------------------------------------------------------------------------------------------

OUTLINE = "#05030a"
AMBER = ["#4a2208", "#8a4a12", "#d08a2a", "#f2bc4a", "#fff0b4"]


def rungs():
    """Iron rungs up the shaft wall, the way back to the well. 16x20, drawn over a rock face."""
    c = Canvas(16, 20)
    for y in range(1, 20, 4):
        c.hline(4, 11, y, "#3c3640")
        c.hline(4, 11, y + 1, "#1a161e")
        c.px(4, y, "#6a6270")
        c.vline(3, y - 1, y + 1, "#1a161e")
        c.vline(12, y - 1, y + 1, "#1a161e")
    return c


def lantern_rock(lit=True):
    """Odo's lantern, set down on a rock. 16x14."""
    c = Canvas(16, 14)
    c.ellipse(8, 10.5, 7, 3.5, FACE[2])
    c.hline(2, 13, 8, FACE[4])
    c.hline(3, 12, 13, FACE[0])
    c.px(3, 9, FACE[4])
    if lit:
        c.hline(6, 9, 1, "#1c1418")
        c.px(7, 0, "#1c1418")
        c.rect(5, 2, 5, 1, "#1c1418")
        c.rect(5, 3, 5, 4, AMBER[3])
        c.rect(6, 4, 3, 2, AMBER[4])
        c.rect(5, 7, 5, 1, "#1c1418")
    return c.outlined(OUTLINE)


def stalagmite(seed=0):
    r = _r(9900 + seed)
    h = int(r.integers(10, 16))
    c = Canvas(10, 16)
    for k in range(h):
        y = 15 - k
        half = max(0, int(round((1 - k / h) * 3.5)))
        for x in range(5 - half, 5 + half + 1):
            c.px(x, y, FACE[3] if x < 5 else FACE[1])
        c.px(5 - half, y, FACE[4] if k % 3 else FACE[3])
    return c.outlined(OUTLINE)
