"""The title logo: GROTESQUE in bold bone-gold pixel letters, with anatomy instead of ornament.
The O is the Sucker Frog's eye (amber, toad's slit pupil) and the Q's tail is its pink tongue,
dripping. "RPG" sits under it in Grotesk caps. 1x, transparent; title.gd places it at (8, 6).

    python tools/art/logo.py [OUT.png]           # default art/ui/logo.png
    python tools/art/logo.py --preview PNG       # on the title scene (cave + Host), 4x
"""
import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import font as gfont

# 2px-stroke capitals, 8 wide x 11 tall ('#' ink). O and Q get their anatomy painted on afterwards.
LETTERS = {
    "G": [".######.", "########", "##....##", "##......", "##......", "##..####", "##..####",
          "##....##", "##....##", "########", ".######."],
    "R": ["#######.", "########", "##....##", "##....##", "##....##", "#######.", "######..",
          "##..##..", "##...##.", "##....##", "##....##"],
    "O": [".######.", "########", "########", "########", "########", "########", "########",
          "########", "########", "########", ".######."],
    "T": ["########", "########", "...##...", "...##...", "...##...", "...##...", "...##...",
          "...##...", "...##...", "...##...", "...##..."],
    "E": ["########", "########", "##......", "##......", "##......", "######..", "######..",
          "##......", "##......", "########", "########"],
    "S": [".######.", "########", "##......", "##......", "#######.", ".#######", "......##",
          "......##", "##....##", "########", ".######."],
    "Q": [".######.", "########", "##....##", "##....##", "##....##", "##....##", "##....##",
          "##..#.##", "##...###", "########", ".#######"],
    "U": ["##....##", "##....##", "##....##", "##....##", "##....##", "##....##", "##....##",
          "##....##", "##....##", "########", ".######."],
}
WORD = "GROTESQUE"
LIFT = [0, -1, 0, 1, 0, -1, 0, 1, 0]       # an uneasy baseline: letters sit a pixel off

BONE = ["#8c6c30", "#c9a24e", "#e8cf7a", "#f6e6a8"]     # shadow, mid, light, top edge
OUTLINE = "#1a0810"
SCLERA_HI, SCLERA, SCLERA_SH = "#f0e9d6", "#d6cdb5", "#9b917a"
IRIS, IRIS_HI, IRIS_SH, PUPIL, GLINT = "#c27a18", "#f0b040", "#8a4e0c", "#0a0604", "#fff6d8"
VEIN = "#b03050"
FLESH, FLESH_HI, FLESH_SH = "#cc4862", "#ee8696", "#681430"
RPG_COL = "#9a92c0"

W, H = 96, 26
X0, Y0 = 1, 2         # top-left of the first letter (room for the outline)
ADV = 10              # 8 wide + 2 gap


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8)


def build():
    img = np.zeros((H, W, 4), np.uint8)
    ink = np.zeros((H, W), bool)
    letter_at = {}
    for i, ch in enumerate(WORD):
        x0, y0 = X0 + i * ADV, Y0 + 1 + LIFT[i]
        letter_at[i] = (x0, y0)
        for y, row in enumerate(LETTERS[ch]):
            for x, c in enumerate(row):
                if c == "#":
                    ink[y0 + y, x0 + x] = True
                    # bone shading by row: lit from above, darker toward the bottom
                    tone = 3 if y == 0 else 2 if y < 4 else 1 if y < 9 else 0
                    img[y0 + y, x0 + x] = hexc(BONE[tone])

    def px(x, y, col):
        img[y, x] = hexc(col)
        ink[y, x] = True

    # O: the frog's eye - a shaded eyeball, an amber iris, a short horizontal slit, a glint
    ox, oy = letter_at[WORD.index("O")]
    for y in range(11):
        for x in range(8):
            if ink[oy + y, ox + x]:
                lit = x + y < 6
                dark = y >= 9 or x == 7 or (x >= 6 and y >= 7)
                img[oy + y, ox + x] = hexc(SCLERA_HI if lit else SCLERA_SH if dark else SCLERA)
    for x, y in [(3, 3), (4, 3), (2, 4), (3, 4), (4, 4), (5, 4), (2, 5), (3, 5), (4, 5), (5, 5),
                 (2, 6), (3, 6), (4, 6), (5, 6), (3, 7), (4, 7)]:
        px(ox + x, oy + y, IRIS_SH if y >= 6 else IRIS)
    px(ox + 3, oy + 5, PUPIL)
    px(ox + 4, oy + 5, PUPIL)
    px(ox + 2, oy + 4, IRIS_HI)
    px(ox + 3, oy + 3, GLINT)
    for x, y in [(1, 7), (1, 8), (6, 2)]:
        px(ox + x, oy + y, VEIN)

    # Q: the tail becomes the frog's tongue, hanging and dripping
    qx, qy = letter_at[WORD.index("Q")]
    for x, y, col in [(7, 10, FLESH), (8, 10, FLESH), (8, 11, FLESH_HI), (8, 12, FLESH), (9, 12, FLESH_SH),
                      (8, 13, FLESH), (8, 14, FLESH_SH), (8, 16, FLESH_SH)]:
        px(qx + x, qy + y, col)

    # two drips off the bottoms of letters (the first E and the U)
    for i, dx, length in [(WORD.index("E"), 2, 3), (WORD.index("U"), 6, 2)]:
        lx, ly = letter_at[i]
        for d in range(length):
            px(lx + dx, ly + 11 + d, FLESH_SH if d else FLESH)
        px(lx + dx, ly + 12 + length, FLESH_SH)

    # outline everything inked so far
    out = img.copy()
    for y in range(H):
        for x in range(W):
            if ink[y, x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < W and 0 <= yy < H and ink[yy, xx]:
                    out[y, x] = hexc(OUTLINE)
                    break
    img = out

    # RPG in Grotesk caps, letter-spaced, under the right half of the word
    canvas = img
    x = W - 1 - (gfont.measure("R P G"))
    gfont.draw_text(canvas, "R P G", x, Y0 + 16, tuple(hexc(RPG_COL)))
    return img


def preview(path, logo):
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    bg = Image.open(os.path.join(here, "cave_bg.png")).convert("RGBA")
    host = Image.open(os.path.join(root, "art", "monsters", "host", "normal.png")).convert("RGBA")
    bg.alpha_composite(host, (108, 4))
    bg.alpha_composite(Image.fromarray(logo, "RGBA"), (8, 6))
    a = np.array(bg)
    gfont.draw_text(a, "work in progress", 9, 42, (138, 130, 176, 255))
    a[126:168, 110:210] = (12, 10, 26, 255)
    a[126, 110:210] = a[167, 110:210] = (200, 192, 240, 255)
    gfont.draw_text(a, "PLAY", 124, 131, (255, 255, 255, 255))
    gfont.draw_text(a, "Quit", 124, 142, (154, 146, 192, 255))
    Image.fromarray(a, "RGBA").resize((1280, 720), Image.NEAREST).save(path)


if __name__ == "__main__":
    logo = build()
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1], logo)
    else:
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        out = args[0] if args else "art/ui/logo.png"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        Image.fromarray(logo, "RGBA").save(out)
        print("wrote", out, logo.shape[1], "x", logo.shape[0])
