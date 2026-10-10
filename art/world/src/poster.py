"""The Salt Guild's poster, found folded in the drowned man's coat - seen over his own hands. 320x180.

Body text is set in the game's pixel font (the glyph table in tools/art/font.py); the headline uses
bold 9px capitals drawn here. Two inks (black-brown and the Guild's red) on fen-soaked paper:
quarter folds, tide-marks, and an applicant's name the water has washed away.
"""
import math
import os
import sys

import numpy as np

from pix import Canvas
from people import HERO

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools", "art"))
import font as grotesk  # noqa: E402  (the game's font: read-only use of its glyph table)

PAPER = ["#2b221d", "#6b5b4a", "#988670", "#bcab8b", "#d6c8a6"]
INK = "#231814"
RED = "#8a2c23"
RED_HI = "#a8443a"
NAME_INK = "#2a2f45"
BG = ["#07050d", "#0d0a15", "#141020"]

# Bold 9px capitals for the headline (2px stems).
HEAD = {
    "A": ["..##..", ".####.", "##..##", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    "D": ["#####.", "##..##", "##..##", "##..##", "##..##", "##..##", "##..##", "##..##", "#####."],
    "E": ["######", "##....", "##....", "##....", "#####.", "##....", "##....", "##....", "######"],
    "G": [".####.", "##..##", "##....", "##....", "##.###", "##..##", "##..##", "##..##", ".####."],
    "H": ["##..##", "##..##", "##..##", "##..##", "######", "##..##", "##..##", "##..##", "##..##"],
    "I": ["####", ".##.", ".##.", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    "K": ["##..##", "##..##", "##.##.", "####..", "###...", "####..", "##.##.", "##..##", "##..##"],
    "L": ["##....", "##....", "##....", "##....", "##....", "##....", "##....", "##....", "######"],
    "N": ["##..##", "###.##", "###.##", "######", "##.###", "##.###", "##..##", "##..##", "##..##"],
    "R": ["#####.", "##..##", "##..##", "##..##", "#####.", "####..", "##.##.", "##..##", "##..##"],
    "S": [".####.", "##..##", "##....", "##....", ".####.", "....##", "....##", "##..##", ".####."],
    "T": ["######", "..##..", "..##..", "..##..", "..##..", "..##..", "..##..", "..##..", "..##.."],
    "U": ["##..##", "##..##", "##..##", "##..##", "##..##", "##..##", "##..##", "##..##", ".####."],
}


def _r(seed):
    return np.random.default_rng(seed)


# --------------------------------------------------------------------------------------------
# lettering
# --------------------------------------------------------------------------------------------

def measure(s, glyphs, space):
    w = 0
    for ch in s:
        w += space if ch == " " else len(glyphs[ch][0]) + 1
    return w - 1


def letter(c, s, x, y, col, glyphs, space, wobble=None):
    """Draws `s` with its top-left at (x, y). `wobble`: rng to drop the odd pixel (worn print)."""
    for ch in s:
        if ch == " ":
            x += space
            continue
        rows = glyphs[ch]
        for j, row in enumerate(rows):
            for i, v in enumerate(row):
                if v == "#" and not (wobble is not None and wobble.random() < 0.04):
                    c.px(x + i, y + j, col)
        x += len(rows[0]) + 1


def centred(c, s, cx, y, col, head=False, wobble=None):
    glyphs, space = (HEAD, 4) if head else (grotesk.G, 3)
    letter(c, s, cx - measure(s, glyphs, space) // 2, y, col, glyphs, space, wobble)


# --------------------------------------------------------------------------------------------
# the poster
# --------------------------------------------------------------------------------------------

def background():
    c = Canvas(320, 180)
    c.rect(0, 0, 320, 180, BG[0])
    bayer = [[0, 2], [3, 1]]
    for y in range(180):
        for x in range(320):
            d = ((x - 160) / 150) ** 2 + ((y - 95) / 110) ** 2
            if d < 1.0 and (1.0 - d) * 4 > bayer[y & 1][x & 1] + 1:
                c.px(x, y, BG[1] if d > 0.45 else BG[2])
    return c


def paper(c, x0, y0, w, h):
    r = _r(5)
    x1, y1 = x0 + w - 1, y0 + h - 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            # deckled edges, a torn bottom-right corner
            edge = min(x - x0, x1 - x, y - y0, y1 - y)
            if edge == 0 and r.random() < 0.35:
                continue
            if (x1 - x) + (y1 - y) < 9 + int(r.integers(0, 3)):
                continue
            col = PAPER[3]
            if edge <= 1:
                col = PAPER[2]
            elif r.random() < 0.06:
                col = PAPER[2] if r.random() < 0.6 else PAPER[4]
            c.px(x, y, col)
    # quarter folds: a crease is a lit ridge beside its shadow
    mx, my = x0 + w // 2, y0 + h // 2
    for y in range(y0 + 1, y1):
        if c.solid(mx, y):
            c.px(mx, y, PAPER[4])
            c.px(mx + 1, y, PAPER[2])
    for x in range(x0 + 1, x1):
        if c.solid(x, my):
            c.px(x, my, PAPER[4])
            c.px(x, my + 1, PAPER[2])


def stain(c, cx, cy, rx, ry, seed, region):
    """A tide-mark: water dried into a darker ring, the paper inside a shade darker and blotchy."""
    r = _r(seed)
    x0, y0, x1, y1 = region
    for y in range(int(cy - ry) - 2, int(cy + ry) + 3):
        for x in range(int(cx - rx) - 2, int(cx + rx) + 3):
            if not (x0 <= x <= x1 and y0 <= y <= y1) or not c.solid(x, y):
                continue
            a = math.atan2(y - cy, x - cx)
            k = 1.0 + 0.18 * math.sin(a * 3 + seed) + 0.1 * math.sin(a * 7 + seed * 2)
            d = math.hypot((x - cx) / rx, (y - cy) / ry) / k
            if 0.9 < d <= 1.0:
                c.px(x, y, PAPER[1] if r.random() < 0.7 else PAPER[2])
            elif d <= 0.9 and (x + y) % 2 == 0 and r.random() < 0.55:
                c.px(x, y, PAPER[2])


def woodcut(c, x0, y0):
    """The Guild's picture: a hunter with a lantern on a pole faces a ridden man on his knuckles.
    About 140x46, black ink cut with paper-coloured highlights."""
    gy = y0 + 44
    # ground, cut with hatching
    c.hline(x0 + 4, x0 + 136, gy, INK)
    for x in range(x0 + 6, x0 + 134, 3):
        c.px(x, gy + 1, INK)
        if x % 2:
            c.px(x + 1, gy + 2, INK)
    # reeds in clumps at either side, leaning
    r = _r(77)
    for base in (x0 + 4, x0 + 12, x0 + 64, x0 + 126, x0 + 133):
        for k in range(int(r.integers(2, 4))):
            x = base + k * 2
            h = int(r.integers(7, 16))
            lean = float(r.uniform(-0.3, 0.3))
            for j in range(h):
                c.px(round(x + lean * j), gy - 1 - j, INK)
            if r.random() < 0.4:
                c.rect(round(x + lean * h), gy - h - 3, 2, 3, INK)
    # the hunter: long coat, hood, a pole with the lantern held out
    hx = x0 + 40
    for k in range(26):                               # coat, widening to the hem
        y = gy - 1 - k
        half = 5 + (k < 10) * (10 - k) // 3
        c.hline(hx - half, hx + half - 1, y, INK)
    c.ellipse(hx + 1, gy - 30, 4, 4.5, INK)           # hood
    c.px(hx + 4, gy - 30, PAPER[3])                   # a glint of face under the hood
    for k in range(3, 24, 4):                         # light catching the coat's folds
        c.px(hx + 3, gy - k, PAPER[3])
    c.line(hx + 3, gy - 20, hx + 22, gy - 34, INK)    # the pole
    c.line(hx + 3, gy - 21, hx + 22, gy - 35, INK)
    lx, ly = hx + 24, gy - 32                         # the lantern, its rays cut in red
    c.rect(lx - 2, ly - 2, 5, 6, INK)
    c.rect(lx - 1, ly - 1, 3, 4, RED_HI)
    for a in range(0, 360, 30):
        t = math.radians(a)
        for k in range(6, 12, 2):
            c.px(round(lx + math.cos(t) * k), round(ly + 1 + math.sin(t) * k * 0.8), RED)
    # the ridden man, on his knuckles; the frog on his back; the cord into his crown
    rx_ = x0 + 102
    for k in range(18):                               # a back bent like a bridge
        y = gy - 16 - round(5 * math.sin(math.pi * k / 17))
        c.vline(rx_ - 8 + k, y, y + 5, INK)
    c.line(rx_ - 8, gy - 13, rx_ - 13, gy - 1, INK)   # a long arm reaching down
    c.line(rx_ - 7, gy - 13, rx_ - 12, gy - 1, INK)
    c.line(rx_ - 5, gy - 12, rx_ - 6, gy - 1, INK)    # the other, buckled
    c.line(rx_ + 8, gy - 12, rx_ + 12, gy - 1, INK)   # legs behind
    c.line(rx_ + 6, gy - 12, rx_ + 8, gy - 1, INK)
    c.ellipse(rx_ - 9, gy - 9, 3, 3.5, INK)           # the head hanging between the arms
    c.px(rx_ - 9, gy - 7, PAPER[3])                   # the pale crown, opened
    c.ellipse(rx_ + 2, gy - 26, 7, 4, INK)            # the frog on his back
    c.ellipse(rx_ - 2, gy - 30, 2, 2, INK)            # its eyes, bulging
    c.ellipse(rx_ + 5, gy - 30, 2, 2, INK)
    c.pxs([(rx_ - 2, gy - 30), (rx_ + 5, gy - 30)], PAPER[4])
    c.line(rx_ - 3, gy - 23, rx_ - 8, gy - 9, RED)    # the cord into his crown
    c.line(rx_ - 2, gy - 23, rx_ - 7, gy - 9, RED)
    for k in range(-6, 9, 3):                         # light along his back
        c.px(rx_ + k, gy - 20 - round(5 * math.sin(math.pi * (k + 8) / 17)), PAPER[3])


def crystal(c, cx, cy):
    """The Guild's mark: a cube of salt, three faces."""
    pts_top = [(cx, cy - 4), (cx + 4, cy - 2), (cx, cy), (cx - 4, cy - 2)]
    for y in range(cy - 5, cy + 6):
        for x in range(cx - 5, cx + 6):
            top = abs(x - cx) * 0.5 + abs(y - (cy - 2)) <= 2.5
            left = x <= cx and cx - 4 <= x and cy - 2 + (cx - x) * 0.5 - 0.5 <= y <= cy + 3 + (cx - x) * 0.5 - (cx - x)
            right = x >= cx and x <= cx + 4 and cy - 2 + (x - cx) * 0.5 - 0.5 <= y <= cy + 3 + (x - cx) * 0.5 - (x - cx)
            if top:
                c.px(x, y, PAPER[4])
            elif left:
                c.px(x, y, PAPER[2])
            elif right:
                c.px(x, y, PAPER[1])
    for x, y in pts_top:
        c.px(x, y, INK)


def name_smear(c, x0, y, w, seed):
    """Someone wrote a name here. The fen took it: a loop of run ink, dripping down the paper."""
    r = _r(seed)
    x = x0
    py = y + 3
    while x < x0 + w:
        ny = y + 3 + int(round(2.5 * math.sin(x * 0.7 + r.random())))
        c.line(x, py, x + 1, ny, NAME_INK)
        if r.random() < 0.18:                         # a loop
            c.ellipse(x + 1, y + 2, 1.5, 2.5, NAME_INK)
        if r.random() < 0.3:                          # the ink ran
            for k in range(int(r.integers(2, 7))):
                if r.random() < 0.8:
                    c.px(x, ny + 2 + k, NAME_INK)
        py = ny
        x += 2
    stain(c, x0 + w // 2, y + 5, w * 0.62, 5, seed + 3, (0, 0, 319, 179))


def seal(c, cx, cy):
    """The Guild's red seal, stamped a little crooked and faded."""
    r = _r(41)
    for y in range(cy - 7, cy + 8):
        for x in range(cx - 7, cx + 8):
            d = math.hypot(x - cx, y - cy)
            ring = 5.5 <= d <= 7.0
            core = d <= 3.2 and abs(x - cx) + abs(y - cy) <= 3
            if (ring or core) and c.solid(x, y) and r.random() < 0.78:
                c.px(x, y, RED)


def hands(c):
    """His hands at the bottom corners, holding the poster up: thumbs over the front, coat sleeves."""
    skin = [HERO["3"], HERO["2"], HERO["1"]]
    coat = [HERO["k"], HERO["c"], HERO["C"]]
    for side in (-1, 1):
        cx = 160 + side * 82
        # sleeve coming in from the bottom corner
        for y in range(160, 180):
            half = 6 + (y - 160) // 3
            for x in range(cx - half, cx + half + 1):
                c.px(x + side * 6, y + 0, coat[1] if (x - cx) * side < half - 3 else coat[0])
            c.px(cx - side * (half - 1) + side * 6, y, coat[2])
        # the back of the hand round the paper's edge, four fingers curled behind it
        ex = 160 + side * 80                          # the paper's edge
        for k in range(4):                            # fingertips peeking past the edge
            fy = 140 + k * 4
            for j in range(4):
                c.px(ex + side * (1 + j), fy, skin[1] if j < 3 else skin[0])
                c.px(ex + side * (1 + j), fy + 1, skin[1])
                c.px(ex + side * (1 + j), fy + 2, skin[0])
        for y in range(150, 166):                     # the hand
            w_ = 9 + (y - 150) // 4
            for j in range(w_):
                x = ex + side * (j - 2)
                c.px(x, y, skin[2] if j < 3 else (skin[1] if j < w_ - 2 else skin[0]))
        # the thumb on the front of the paper, its nail catching the light
        tx = ex - side * 4
        for y in range(136, 152):
            c.px(tx, y, skin[2])
            c.px(tx - side, y, skin[1])
            c.px(tx + side, y, skin[1] if y > 140 else skin[2])
        c.pxs([(tx, 136), (tx - side, 137)], HERO["2"])
        c.px(tx, 137, "#e8d4c4")                      # the nail
        c.px(tx - side * 2, 145, skin[0])             # its shadow on the paper


def poster():
    c = background()
    x0, y0, w, h = 80, 3, 160, 174
    paper(c, x0, y0, w, h)
    region = (x0 + 1, y0 + 1, x0 + w - 2, y0 + h - 2)
    stain(c, x0 + 130, y0 + 18, 22, 16, 11, region)
    stain(c, x0 + 24, y0 + 120, 16, 22, 12, region)
    wob = _r(9)
    cx = x0 + w // 2
    centred(c, "THE SALT GUILD", cx, y0 + 5, RED, head=True, wobble=wob)
    centred(c, "SEEKS HUNTERS", cx, y0 + 16, INK, head=True, wobble=wob)
    c.hline(x0 + 14, cx - 8, y0 + 29, INK)
    c.hline(cx + 8, x0 + w - 15, y0 + 29, INK)
    crystal(c, cx, y0 + 29)
    woodcut(c, x0 + 10, y0 + 32)
    centred(c, "THE EXAMINATION", cx, y0 + 82, RED, wobble=wob)
    lines = ["is held at the end of the rains,", "where the hungry are fed", "and never full.",
             "Come as you are.", "Who cannot find us", "has their answer."]
    for i, s in enumerate(lines):
        centred(c, s, cx, y0 + 93 + i * 10 + (3 if i >= 3 else 0), INK, wobble=wob)
    letter(c, "Applicant:", x0 + 14, y0 + 158, INK, grotesk.G, 3, wob)
    c.hline(x0 + 60, x0 + 140, y0 + 166, PAPER[1])
    name_smear(c, x0 + 64, y0 + 157, 62, 21)
    seal(c, x0 + 134, y0 + 146)
    # ink that ran when the fen soaked it
    r = _r(31)
    for _ in range(14):
        x = int(r.integers(x0 + 10, x0 + w - 10))
        y = int(r.integers(y0 + 40, y0 + 150))
        if c.get(x, y)[:3] in ((0x23, 0x18, 0x14), (0x8a, 0x2c, 0x23)):
            col = c.get(x, y)
            for k in range(1, int(r.integers(2, 5))):
                if c.solid(x, y + k):
                    c.px(x, y + k, col)
    hands(c)
    return c
