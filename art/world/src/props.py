"""Props for Hollowell: the well, stilt-houses, a lamp post, reeds, plus small UI pixels
(speech bubble, item icons). Drawn at 1x; the bottom row of every prop is its ground line.
"""
import math

import numpy as np

from pix import Canvas
from fen import PEAT, GRASS, WOOD, STONE

OUTLINE = "#0a0710"
AMBER = ["#4a2208", "#8a4a12", "#d08a2a", "#f2bc4a", "#fff0b4"]
THATCH = ["#110c0b", "#1f1813", "#2d2419", "#3e3322", "#53452d"]
MOSS = ["#232a1f", "#323c2a"]
ROPE = ["#3a2c22", "#6b543c", "#9a8060"]


def _r(seed):
    return np.random.default_rng(seed)


# --------------------------------------------------------------------------------------------
# the well
# --------------------------------------------------------------------------------------------

def well(lamp=True, boarded=False):
    """Round stone well in 3/4 view with a wooden frame, roller and rope. 40x48, footprint 2x2.
    `boarded`: the morning after - planks nailed across the mouth, a stone on top, no rope."""
    W, H = 40, 48
    c = Canvas(W, H)
    cx, top, wall, rx, ry = 20, 29, 11, 16, 7       # rim centre y, wall height, radii
    r = _r(11)

    def front(y_c, x):
        t = (x + 0.5 - cx) / rx
        return y_c + ry * math.sqrt(max(0.0, 1 - t * t))

    # stone wall: brick courses that follow the curve, lit on the left
    for x in range(cx - rx, cx + rx):
        y0, y1 = front(top, x), front(top + wall, x)
        side = (x + 0.5 - cx) / rx                 # -1 left .. 1 right
        for y in range(int(y0), int(round(y1)) + 1):
            course = int((y - y0) // 3)
            shade = 2 if side < -0.35 else (1 if side < 0.45 else 0)
            col = STONE[shade + 1]
            # mortar between courses and staggered joints
            if (y - int(y0)) % 3 == 0:
                col = STONE[0]
            elif (x + course * 3) % 6 == 0:
                col = STONE[0]
            elif (y - int(y0)) % 3 == 1 and shade == 2:
                col = STONE[4] if (x + course * 3) % 6 == 1 else STONE[3]
            c.px(x, y, col)
    # rim: a ring of cap stones, the top surface catching the light
    for y in range(top - ry - 1, top + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 1):
            o = ((x + 0.5 - cx) / (rx + 0.5)) ** 2 + ((y + 0.5 - top) / (ry + 0.5)) ** 2
            i = ((x + 0.5 - cx) / (rx - 3.5)) ** 2 + ((y + 0.5 - top) / (ry - 2.0)) ** 2
            if o <= 1.0 and i > 1.0:
                lit = (x - cx) * 0.6 + (y - top) * 1.4
                c.px(x, y, STONE[4] if lit < -6 else (STONE[3] if lit < 4 else STONE[2]))
            elif i <= 1.0:
                # the shaft: black, with a sliver of the far inner wall at the back
                c.px(x, y, "#040306" if y > top - 2 else STONE[0])
    for k in range(-rx, rx, 5):                    # joints between cap stones
        x = cx + k
        c.px(x, int(front(top, x)) - 1, STONE[1])

    # frame: two posts, a roller with rope wound on it, a crank on the right
    for px_ in (cx - rx + 2, cx + rx - 3):
        c.rect(px_, 4, 2, top - 4, WOOD[2])
        c.vline(px_, 4, top - 1, WOOD[3])
        c.px(px_ + 1, top - 1, WOOD[0])
    c.rect(cx - rx + 1, 6, 2 * rx - 2, 3, WOOD[2])
    c.hline(cx - rx + 1, cx + rx - 2, 6, WOOD[3])
    c.hline(cx - rx + 1, cx + rx - 2, 8, WOOD[1])
    for x in range(cx - 5, cx + 5):                # wound rope
        c.px(x, 7, ROPE[1] if x % 2 else ROPE[2])
    c.rect(cx + rx - 1, 5, 3, 2, WOOD[1])          # crank
    c.vline(cx + rx + 1, 6, 10, WOOD[2])
    # the rope drops into the dark
    if not boarded:
        for y in range(9, top + 1):
            c.px(cx, y, ROPE[1] if y % 3 else ROPE[2])
    else:
        for k, py in enumerate((top - 4, top - 1, top + 2)):   # planks across the mouth
            x0 = cx - rx + 3 + (k % 2)
            x1 = cx + rx - 4 - (k == 1)
            c.rect(x0, py, x1 - x0, 2, WOOD[2])
            c.hline(x0, x1 - 1, py, WOOD[3])
            c.hline(x0, x1 - 1, py + 2, "#040306")
            c.pxs([(x0 + 1, py), (x1 - 2, py)], STONE[4])    # nail heads
        c.ellipse(cx + 3, top - 3, 3.5, 2.5, STONE[3])        # a stone to hold them down
        c.hline(cx + 1, cx + 4, top - 5, STONE[4])
        c.hline(cx + 1, cx + 5, top - 1, STONE[1])
    # a bucket on the rim
    c.rect(cx - rx + 4, top - 4, 5, 5, WOOD[2])
    c.hline(cx - rx + 4, cx - rx + 8, top - 4, WOOD[3])
    c.hline(cx - rx + 4, cx - rx + 8, top - 2, STONE[1])
    c.px(cx - rx + 4, top - 4, WOOD[4])
    if lamp:                                       # a lantern on a hook on the left post
        lx = cx - rx + 1
        c.px(lx - 1, 10, WOOD[1])
        c.rect(lx - 3, 11, 3, 1, "#1c1418")
        c.rect(lx - 3, 12, 3, 3, AMBER[3])
        c.px(lx - 2, 13, AMBER[4])
        c.hline(lx - 3, lx - 1, 15, "#1c1418")
    return c.outlined(OUTLINE)


# --------------------------------------------------------------------------------------------
# stilt-houses
# --------------------------------------------------------------------------------------------

def house(kind="odo"):
    """A plank shack on short stilts with a sagging reed roof. 64x64, footprint 4x2.
    kind: "odo" (door ajar, lamp in the window), "shut" (window shuttered, a crack of light),
    "dark" (nobody home)."""
    W, H = 64, 64
    c = Canvas(W, H)
    r = _r({"odo": 1, "shut": 2, "dark": 3}[kind])
    wall_top, wall_bot = 30, 54
    x0, x1 = 6, 57
    # stilts and the shadow under the floor
    c.rect(x0 + 1, wall_bot, x1 - x0 - 1, 6, "#0d080c")
    for px_ in (x0 + 2, x0 + 16, x1 - 17, x1 - 3):
        c.rect(px_, wall_bot, 2, 9, WOOD[1])
        c.px(px_, wall_bot, WOOD[2])
    # plank wall, vertical boards, lit from the left
    for x in range(x0, x1 + 1):
        board = (x - x0) // 4
        edge = (x - x0) % 4 == 0
        base = WOOD[3] if x < x0 + 12 else WOOD[2]
        for y in range(wall_top, wall_bot):
            c.px(x, y, WOOD[1] if edge else base)
        if not edge and r.random() < 0.3:          # knots, rot
            c.px(x, int(r.integers(wall_top + 2, wall_bot - 1)), WOOD[0])
    c.hline(x0, x1, wall_bot - 1, WOOD[0])         # floor beam
    c.hline(x0, x1, wall_bot, WOOD[1])
    # door with a ladder down to the ground
    dx = 25
    c.rect(dx, 36, 10, wall_bot - 36, "#0b0709")
    c.rect(dx - 1, 35, 12, 1, WOOD[1])
    if kind == "odo":                              # ajar: warm light spills through the gap
        c.rect(dx + 1, 37, 6, wall_bot - 38, WOOD[1])
        c.vline(dx + 7, 37, wall_bot - 2, AMBER[3])
        c.vline(dx + 8, 37, wall_bot - 2, AMBER[2])
    else:
        c.rect(dx + 1, 37, 8, wall_bot - 38, WOOD[1])
        c.vline(dx + 5, 37, wall_bot - 2, WOOD[0])
        c.px(dx + 7, 45, WOOD[3])
    for y in range(wall_bot, H):                    # ladder
        c.px(dx + 1, y, WOOD[2])
        c.px(dx + 8, y, WOOD[1])
        if (y - wall_bot) % 3 == 1:
            c.hline(dx + 1, dx + 8, y, WOOD[2])
    # window
    wx, wy = 42, 37
    if kind == "dark":
        c.rect(wx, wy, 9, 7, "#08060a")
    elif kind == "shut":
        c.rect(wx, wy, 9, 7, WOOD[1])
        for y in range(wy, wy + 7, 2):
            c.hline(wx, wx + 8, y, WOOD[0])
        c.vline(wx + 4, wy, wy + 6, AMBER[2])       # a crack of light between the shutters
    else:
        c.rect(wx, wy, 9, 7, AMBER[3])
        c.rect(wx + 1, wy + 1, 3, 2, AMBER[4])
        c.vline(wx + 4, wy, wy + 6, WOOD[0])
        c.hline(wx, wx + 8, wy + 3, WOOD[0])
    c.rect(wx - 1, wy - 1, 11, 1, WOOD[1])
    c.rect(wx - 1, wy + 7, 11, 1, WOOD[0])
    # roof: thatched reed, front slope seen from above, sagging in the middle, ragged eaves
    ry0, ry1 = 4, wall_top + 2
    for x in range(1, W - 1):
        sag = int(round(2.5 * math.sin(math.pi * (x - 1) / (W - 3))))
        y_top = ry0 + sag
        y_eave = ry1 + (1 if r.random() < 0.35 else 0) + (sag // 2)
        for y in range(y_top, y_eave):
            t = (y - y_top) / max(1, (y_eave - y_top))
            col = THATCH[3] if t < 0.18 else (THATCH[2] if t < 0.75 else THATCH[1])
            if x < 10 and t < 0.75:
                col = THATCH[min(4, THATCH.index(col) + 1)]
            if (x * 7 + y * 3) % 11 == 0 or (x % 3 == 0 and r.random() < 0.25):
                col = THATCH[max(0, THATCH.index(col) - 1)]   # reed strands
            c.px(x, y, col)
        c.px(x, y_top, THATCH[4] if x < W // 2 else THATCH[3])
        c.px(x, y_eave, THATCH[0])
    for _ in range(5):                               # damp moss on the thatch
        mx, my = int(r.integers(4, W - 10)), int(r.integers(ry0 + 6, ry1 - 4))
        for k in range(int(r.integers(4, 9))):
            c.px(mx + k, my + (k % 3 == 0), MOSS[k % 2])
    for x in range(W // 2 - 6, W // 2 + 6):          # ridge cap
        c.px(x, ry0 + int(round(2.5 * math.sin(math.pi * (x - 1) / (W - 3)))) + 1, THATCH[3])
    for _ in range(14):                              # loose reeds hanging off the eave
        x = int(r.integers(2, W - 3))
        y = ry1 + 1
        c.vline(x, y, y + int(r.integers(1, 3)), THATCH[1])
    if kind == "dark":                               # a hole in the roof
        c.ellipse(46, 14, 5, 3, "#0b0709")
        c.hline(42, 50, 12, THATCH[0])
    return c.outlined(OUTLINE)


# --------------------------------------------------------------------------------------------
# small things
# --------------------------------------------------------------------------------------------

def lamp_post():
    """A crooked pole with a hanging lantern. 12x34, footprint 1x1."""
    c = Canvas(12, 34)
    c.rect(4, 4, 2, 30, WOOD[2])
    c.vline(4, 4, 33, WOOD[3])
    c.hline(4, 9, 4, WOOD[2])                       # arm
    c.hline(4, 9, 3, WOOD[3])
    c.vline(9, 5, 6, "#1c1418")                     # chain
    c.rect(8, 7, 3, 1, "#1c1418")
    c.rect(8, 8, 3, 4, AMBER[3])
    c.px(9, 9, AMBER[4])
    c.hline(8, 10, 12, "#1c1418")
    c.rect(3, 31, 4, 3, WOOD[1])                    # the foot, sunk in peat
    return c.outlined(OUTLINE)


def reeds(seed=0):
    """A clump of fen reeds with a couple of cattails. 16x22, decoration."""
    r = _r(100 + seed)
    c = Canvas(16, 22)
    for i in range(7):
        x = 3 + i * 1.6 + float(r.uniform(-0.6, 0.6))
        h = int(r.integers(10, 20))
        lean = float(r.uniform(-0.25, 0.25))
        for k in range(h):
            y = 21 - k
            xx = int(round(x + lean * k))
            c.px(xx, y, GRASS[2] if k < h - 3 else GRASS[3])
        if r.random() < 0.35:                        # cattail
            xx = int(round(x + lean * h))
            c.rect(xx, 21 - h, 2, 3, "#3a2618")
            c.px(xx, 21 - h, "#5a3c26")
    return c.outlined(OUTLINE)


def bubble():
    """Speech bubble with three dots - shown when the hero says nothing. 13x10."""
    c = Canvas(13, 10)
    c.rect(1, 0, 11, 7, "#d6d0e6")
    c.rect(0, 1, 13, 5, "#d6d0e6")
    c.pxs([(4, 7), (5, 7), (4, 8)], "#d6d0e6")
    for x in (3, 6, 9):
        c.px(x, 3, "#1a1424")
    out = c.outlined(OUTLINE)
    return out


def lantern_icon():
    """Odo's lantern, held up when the hero shows it. 7x10."""
    c = Canvas(7, 10)
    c.hline(2, 4, 0, "#1c1418")
    c.px(3, 1, "#1c1418")
    c.rect(1, 2, 5, 1, "#1c1418")
    c.rect(1, 3, 5, 5, AMBER[3])
    c.rect(2, 4, 3, 3, AMBER[4])
    c.vline(1, 3, 7, AMBER[1])
    c.rect(1, 8, 5, 1, "#1c1418")
    return c.outlined(OUTLINE)
