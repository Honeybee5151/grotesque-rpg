"""The drowned road north of Hollowell: Old Gristle, the Mouther on the map, the salt circle, a
signpost, a mile-stone, dead trees, and item icons (the poster, wishing pennies).
"""
import math

import numpy as np

from pix import Canvas
from fen import PEAT, GRASS, WOOD, STONE, WATER
from people import OUTLINE, RIM, FW

SALT = ["#5a6670", "#8a98a4", "#c2ccd4", "#eef3f6"]
PAPER = ["#6b5b4a", "#988670", "#bcab8b", "#d6c8a6"]


def _r(seed):
    return np.random.default_rng(seed)


# --------------------------------------------------------------------------------------------
# Old Gristle: thirty Examinations failed, friendly, and every offer a trap. An oilskin coat that
# gapes at the belly - and the belly has a mouth of its own, that laughs a beat after he does.
# --------------------------------------------------------------------------------------------

GRISTLE = {
    "T": "#2e2618", "t": "#4e4228",                      # oilskin rain-hat
    "1": "#dcae92", "2": "#ac7e66", "3": "#70504a",      # ruddy skin
    "e": "#120a0e", "b": "#7a6458",                      # eyes, stubble
    "O": "#8a7a3e", "o": "#5e5228", "q": "#3a3219",      # greasy oilskin coat
    "m": "#1a0a0e", "w": "#e4d8bc", "r": "#8a2c3c",      # the belly-mouth: throat, teeth, lip
    "p": "#3a3036", "B": "#211a1e", "j": "#6a5a7a",      # trousers, boots, his jug
}

GRISTLE_DOWN = [
    "................",  # 0
    "................",  # 1
    "......TTTTT.....",  # 2  hat crown
    "...tTTTTTTTTTt..",  # 3  wide brim
    "....b1111112b...",  # 4
    "....1e111e12....",  # 5
    "....1111111b....",  # 6
    "....bb11122bb...",  # 7  jowls, stubble
    "...OOOooooooqq..",  # 8  shoulders
    "..OOOOoooooooqq.",  # 9
    ".1OOOrwwwwwrqqq3",  # 10 the coat gapes: lips, teeth
    ".1OOOmmmmmmmqqq3",  # 11 the belly-mouth
    ".jOOOrwwwwwrqqq3",  # 12 a jug in his hand
    ".jjOOOoooooqqqq.",  # 13
    "..OOOOoooooqqqq.",  # 14
    "...OOOooooqqqq..",  # 15
    "...OOoooooooqq..",  # 16
    "....OOooooqq....",  # 17
    "....pppp.ppp....",  # 18
    "....ppp..ppp....",  # 19
    "....ppp..ppp....",  # 20
    "...BBBB..BBBB...",  # 21
    "...BBBB..BBBB...",  # 22
    "................",  # 23
]


def gristle():
    """Two frames: smiling, and the belly-mouth laughing open."""
    a = Canvas.from_ascii(GRISTLE_DOWN, GRISTLE)
    laugh = [list(r) for r in GRISTLE_DOWN]
    laugh[10] = list(".1OOOmwmwmwmqqq3")
    laugh[11] = list(".1OOOmmmmmmmqqq3")
    laugh[12] = list(".jOOOmwmwmwmqqq3")
    laugh[13] = list(".jjOOOrrrrrqqqq.")
    b = Canvas.from_ascii(["".join(r) for r in laugh], GRISTLE)
    return [a.outlined(OUTLINE, RIM), b.outlined(OUTLINE, RIM)]


# --------------------------------------------------------------------------------------------
# The Mouther on the map (the battler is monster's: art/monsters/mouther). A bog body, tanned to
# leather, pressed crooked; the jaw hanging far too low, its scarf slipped off the mouth.
# --------------------------------------------------------------------------------------------

MOUTHER = {
    "1": "#9a6a42", "2": "#704a2c", "3": "#46291a",      # peat-tanned skin
    "e": "#120a08",
    "m": "#c04a62", "M": "#5a1424",                      # the wet pink inside of the mouth
    "G": "#4e5e46", "g": "#36422f", "h": "#232a1f",      # the rotted coat
    "s": "#5e4c3a", "S": "#3e3226",                      # the rotted scarf
}

MOUTHER_UP = [
    ".......11.......",  # 0  the skull, flattened on one side
    "......1112......",  # 1
    ".....1e12e......",  # 2
    ".....11112......",  # 3
    ".....1mmM2......",  # 4  the jaw drops
    "......mmM2......",  # 5
    "......MmM.......",  # 6
    "......2M2.......",  # 7  far below where a jaw should be
    "....GssSsshh....",  # 8  the scarf slipped down round the neck
    "...GGg1222hh....",  # 9  one shoulder hiked
    "..GGGg1232ghh...",  # 10
    "..GG.g1222g.h...",  # 11
    "..G1.g2232g.h...",  # 12
    "..G1.gg22gg.h1..",  # 13
    "...1..g22g...1..",  # 14 arms hanging past the hips
    "...1..1..2...2..",  # 15
    "......1..2......",  # 16
    ".......1.2......",  # 17 knock-kneed
    ".......12.......",  # 18
    "......1..2......",  # 19
    "......1...2.....",  # 20
    ".....11...22....",  # 21
    "................",  # 22
    "................",  # 23
]

MOUTHER_DOWN_IN_PEAT = [
    "............................",  # 0
    "......SSSSS.................",  # 1
    "....1111sss2GGgg............",  # 2  lying face up in the peat
    "...1e1e12mmMGGGgggghh.......",  # 3  the jaw open to the sky
    "...111112mMMGGGggggghhh2222.",  # 4
    "....11122MM.GGgggghhh..1112.",  # 5
    ".....222.....hhhh.......22..",  # 6
    "............................",  # 7
]


def mouther():
    up = Canvas.from_ascii(MOUTHER_UP, MOUTHER).outlined(OUTLINE, RIM)
    lying = Canvas.from_ascii(MOUTHER_DOWN_IN_PEAT, MOUTHER)
    # sunk in the bog: peat laps over its edges
    r = _r(3)
    for x in range(lying.w):
        for y in (5, 6, 7):
            if r.random() < 0.55:
                lying.px(x, y, PEAT[1] if r.random() < 0.6 else PEAT[0])
    return up, lying.outlined(OUTLINE)


# --------------------------------------------------------------------------------------------
# props
# --------------------------------------------------------------------------------------------

def salt_circle():
    """A Salt Guild waystation: a ring of salt kept white, and a post with a salt-glass lamp.
    48x30; the ring is decoration, the post is what you face to rest."""
    W, H = 48, 30
    c = Canvas(W, H)
    cx, cy, rx, ry = 24, 21, 21, 7.5
    r = _r(9)
    for a in range(0, 360, 4):                     # the ring: crystals heaped in a line
        t = math.radians(a)
        x = cx + math.cos(t) * rx
        y = cy + math.sin(t) * ry
        c.px(round(x), round(y), SALT[2])
        c.px(round(x) + 1, round(y), SALT[1] if math.sin(t) < 0 else SALT[2])
        if r.random() < 0.35:
            c.px(round(x), round(y) - 1, SALT[3])
    # the post and its lamp
    c.rect(23, 6, 2, 16, WOOD[2])
    c.vline(23, 6, 21, WOOD[3])
    c.hline(22, 26, 5, WOOD[1])
    c.rect(22, 0, 5, 5, SALT[1])                   # a cage of salt-glass, cold light inside
    c.rect(23, 1, 3, 3, SALT[3])
    c.px(24, 2, "#ffffff")
    c.rect(22, 21, 4, 2, PEAT[1])
    return c.outlined(OUTLINE)


def signpost():
    """A crooked post with two boards: HOLLOWELL south, TALLOWMOUTH north, and something
    scratched underneath. 20x28."""
    c = Canvas(20, 28)
    c.rect(9, 6, 2, 22, WOOD[2])
    c.vline(9, 6, 27, WOOD[3])
    for y, x0, x1, tip in ((4, 2, 17, 18), (11, 3, 16, 1)):
        c.rect(x0, y, x1 - x0 + 1, 4, WOOD[2])
        c.hline(x0, x1, y, WOOD[3])
        c.hline(x0, x1, y + 3, WOOD[0])
        c.px(tip, y + 1, WOOD[2])
        c.px(tip, y + 2, WOOD[1])
        for x in range(x0 + 2, x1 - 1, 2):         # lettering, too small to read
            c.px(x, y + 1 + (x % 3 == 0), WOOD[0])
    for x in range(5, 15, 2):                      # the scratched warning on the post
        c.px(x if x != 9 else 11, 18 + (x % 4 == 1), "#d6c8a6")
    return c.outlined(OUTLINE)


def milestone():
    c = Canvas(14, 16)
    c.rect(2, 3, 10, 13, STONE[2])
    c.hline(3, 10, 2, STONE[3])
    c.rect(4, 1, 6, 2, STONE[3])
    c.vline(2, 3, 15, STONE[3])
    c.vline(11, 3, 15, STONE[1])
    for y in (6, 9):                               # notches for the miles
        c.hline(5, 8, y, STONE[0])
    c.pxs([(4, 12), (9, 13), (6, 4)], GRASS[2])    # lichen
    return c.outlined(OUTLINE)


def dead_tree(seed=0):
    """A drowned tree, black and bare, leaning. 28x34."""
    r = _r(500 + seed)
    c = Canvas(28, 34)

    def branch(x, y, ang, length, w):
        if length < 3:
            return
        for k in range(int(length)):
            xx = x + math.cos(ang) * k
            yy = y - math.sin(ang) * k
            for d in range(w):
                c.px(round(xx) + d, round(yy), WOOD[1] if d == 0 else WOOD[0])
        nx = x + math.cos(ang) * length
        ny = y - math.sin(ang) * length
        for da in (-0.55, 0.45):
            if r.random() < 0.85:
                branch(nx, ny, ang + da + float(r.uniform(-0.2, 0.2)), length * 0.62, max(1, w - 1))

    branch(13, 33, math.pi / 2 + float(r.uniform(-0.15, 0.15)), 13, 3)
    return c.outlined(OUTLINE)


def poster_icon():
    """The poster, folded small: a soaked square of paper with a red mark. 9x10."""
    c = Canvas(9, 10)
    c.rect(0, 1, 9, 8, PAPER[2])
    c.hline(0, 8, 1, PAPER[3])
    c.vline(4, 1, 8, PAPER[1])                     # the fold
    c.rect(1, 3, 2, 2, "#8a2c23")                  # the Guild's red
    c.hline(5, 7, 3, PAPER[0])
    c.hline(5, 7, 5, PAPER[0])
    c.hline(1, 3, 6, PAPER[0])
    return c.outlined(OUTLINE)


def pennies_icon():
    """Wishing pennies, green with the fen. 10x7."""
    c = Canvas(10, 7)
    for x, y in ((1, 2), (5, 1), (3, 4)):
        c.ellipse(x + 1.5, y + 1.5, 2, 1.5, "#b87a3a")
        c.px(x + 1, y + 1, "#e8b46a")
        c.px(x + 2, y + 2, "#5a7a4a")
    return c.outlined(OUTLINE)
