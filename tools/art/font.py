"""Grotesk: the game's pixel font (a "grotesk" is a sans-serif - fitting, for Grotesque RPG).

Proportional, 7px caps, 5px x-height, 2px descenders, 10px line, 1px letter spacing. Drawn on the
320x180 grid and never scaled. Exported as a BMFont (.fnt + .png), which Godot imports as a
FontFile. Use it at its own size (the .fnt's `info size=`), with scaling off in its .import:
Godot's stock import scales bitmap fonts fractionally to whatever font_size is asked for.

A second face, grotesk_digits, is chunky outlined digits for damage popups: bitmap fonts can't
take Godot's outline_size, so the 1px dark outline is baked in; the fill is white so font_color
tints it while the outline stays dark.

    python tools/art/font.py [OUTDIR]        # default art/fonts -> grotesk + grotesk_digits (.fnt, .png)
    python tools/art/font.py --specimen PNG  # all glyphs, real game lines and popups, 4x

Glyphs: rows top to bottom; rows 0-6 sit on the baseline (caps, ascenders), rows 7-8 are descenders.
'#' is ink. Glyphs shorter than 9 rows are padded at the bottom.
"""
import os
import sys
import numpy as np
from PIL import Image

LINE_HEIGHT = 10
BASE = 7          # baseline: rows above it
ROWS = 9          # 7 + 2 descender rows
SPACE_ADVANCE = 3

G = {}


def glyph(chars, *rows):
    for c in chars:
        G[c] = rows


# --- digits -------------------------------------------------------------------------------------
glyph("0", ".##.", "#..#", "#..#", "#..#", "#..#", "#..#", ".##.")
glyph("1", ".#.", "##.", ".#.", ".#.", ".#.", ".#.", "###")
glyph("2", ".##.", "#..#", "...#", "..#.", ".#..", "#...", "####")
glyph("3", ".##.", "#..#", "...#", ".##.", "...#", "#..#", ".##.")
glyph("4", "..#.", ".##.", "#.#.", "#.#.", "####", "..#.", "..#.")
glyph("5", "####", "#...", "###.", "...#", "...#", "#..#", ".##.")
glyph("6", ".##.", "#...", "#...", "###.", "#..#", "#..#", ".##.")
glyph("7", "####", "...#", "..#.", "..#.", ".#..", ".#..", ".#..")
glyph("8", ".##.", "#..#", "#..#", ".##.", "#..#", "#..#", ".##.")
glyph("9", ".##.", "#..#", "#..#", ".###", "...#", "...#", ".##.")

# --- capitals -----------------------------------------------------------------------------------
glyph("A", ".##.", "#..#", "#..#", "####", "#..#", "#..#", "#..#")
glyph("B", "###.", "#..#", "#..#", "###.", "#..#", "#..#", "###.")
glyph("C", ".##.", "#..#", "#...", "#...", "#...", "#..#", ".##.")
glyph("D", "###.", "#..#", "#..#", "#..#", "#..#", "#..#", "###.")
glyph("E", "####", "#...", "#...", "###.", "#...", "#...", "####")
glyph("F", "####", "#...", "#...", "###.", "#...", "#...", "#...")
glyph("G", ".##.", "#..#", "#...", "#.##", "#..#", "#..#", ".###")
glyph("H", "#..#", "#..#", "#..#", "####", "#..#", "#..#", "#..#")
glyph("I", "###", ".#.", ".#.", ".#.", ".#.", ".#.", "###")
glyph("J", "..##", "...#", "...#", "...#", "...#", "#..#", ".##.")
glyph("K", "#..#", "#..#", "#.#.", "##..", "#.#.", "#..#", "#..#")
glyph("L", "#...", "#...", "#...", "#...", "#...", "#...", "####")
glyph("M", "#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#")
glyph("N", "#..#", "##.#", "##.#", "#.##", "#.##", "#..#", "#..#")
glyph("O", ".##.", "#..#", "#..#", "#..#", "#..#", "#..#", ".##.")
glyph("P", "###.", "#..#", "#..#", "###.", "#...", "#...", "#...")
glyph("Q", ".##.", "#..#", "#..#", "#..#", "#..#", "#.#.", ".#.#")
glyph("R", "###.", "#..#", "#..#", "###.", "#.#.", "#..#", "#..#")
glyph("S", ".##.", "#..#", "#...", ".##.", "...#", "#..#", ".##.")
glyph("T", "#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..")
glyph("U", "#..#", "#..#", "#..#", "#..#", "#..#", "#..#", ".##.")
glyph("V", "#...#", "#...#", "#...#", ".#.#.", ".#.#.", ".#.#.", "..#..")
glyph("W", "#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#.")
glyph("X", "#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#")
glyph("Y", "#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..")
glyph("Z", "####", "...#", "...#", "..#.", ".#..", "#...", "####")

# --- lowercase ----------------------------------------------------------------------------------
glyph("a", "....", "....", ".##.", "...#", ".###", "#..#", ".###")
glyph("b", "#...", "#...", "###.", "#..#", "#..#", "#..#", "###.")
glyph("c", "...", "...", ".##", "#..", "#..", "#..", ".##")
glyph("d", "...#", "...#", ".###", "#..#", "#..#", "#..#", ".###")
glyph("e", "....", "....", ".##.", "#..#", "####", "#...", ".##.")
glyph("f", ".##", "#..", "###", "#..", "#..", "#..", "#..")
glyph("g", "....", "....", ".###", "#..#", "#..#", "#..#", ".###", "...#", ".##.")
glyph("h", "#...", "#...", "###.", "#..#", "#..#", "#..#", "#..#")
glyph("i", "#", ".", "#", "#", "#", "#", "#")
glyph("j", ".#", "..", ".#", ".#", ".#", ".#", ".#", ".#", "#.")
glyph("k", "#...", "#...", "#..#", "#.#.", "##..", "#.#.", "#..#")
glyph("l", "#", "#", "#", "#", "#", "#", "#")
glyph("m", ".....", ".....", "####.", "#.#.#", "#.#.#", "#.#.#", "#.#.#")
glyph("n", "....", "....", "###.", "#..#", "#..#", "#..#", "#..#")
glyph("o", "....", "....", ".##.", "#..#", "#..#", "#..#", ".##.")
glyph("p", "....", "....", "###.", "#..#", "#..#", "#..#", "###.", "#...", "#...")
glyph("q", "....", "....", ".###", "#..#", "#..#", "#..#", ".###", "...#", "...#")
glyph("r", "...", "...", "#.#", "##.", "#..", "#..", "#..")
glyph("s", "....", "....", ".###", "#...", ".##.", "...#", "###.")
glyph("t", "...", ".#.", "###", ".#.", ".#.", ".#.", "..#")
glyph("u", "....", "....", "#..#", "#..#", "#..#", "#..#", ".###")
glyph("v", "...", "...", "#.#", "#.#", "#.#", "#.#", ".#.")
glyph("w", ".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#.")
glyph("x", "...", "...", "#.#", "#.#", ".#.", "#.#", "#.#")
glyph("y", "....", "....", "#..#", "#..#", "#..#", "#..#", ".###", "...#", ".##.")
glyph("z", "....", "....", "####", "...#", ".##.", "#...", "####")

# --- punctuation and symbols --------------------------------------------------------------------
glyph(".", ".", ".", ".", ".", ".", ".", "#")
glyph(",", "..", "..", "..", "..", "..", "..", ".#", "#.")
glyph("!", "#", "#", "#", "#", "#", ".", "#")
glyph("?", ".##.", "#..#", "...#", "..#.", ".#..", "....", ".#..")
glyph("'", "#", "#")
glyph('"', "#.#", "#.#")
glyph(":", ".", ".", ".", "#", ".", ".", "#")
glyph(";", "..", "..", "..", ".#", "..", "..", ".#", "#.")
glyph("-", "...", "...", "...", "...", "###")
glyph("+", "...", "...", "...", ".#.", "###", ".#.")
glyph("=", "...", "...", "...", "###", "...", "###")
glyph("(", ".#", "#.", "#.", "#.", "#.", "#.", ".#")
glyph(")", "#.", ".#", ".#", ".#", ".#", ".#", "#.")
glyph("[", "##", "#.", "#.", "#.", "#.", "#.", "##")
glyph("]", "##", ".#", ".#", ".#", ".#", ".#", "##")
glyph("{", "..#", ".#.", ".#.", "#..", ".#.", ".#.", "..#")
glyph("}", "#..", ".#.", ".#.", "..#", ".#.", ".#.", "#..")
glyph("/", "..#", "..#", ".#.", ".#.", ".#.", "#..", "#..")
glyph("\\", "#..", "#..", ".#.", ".#.", ".#.", "..#", "..#")
glyph("|", "#", "#", "#", "#", "#", "#", "#", "#", "#")
glyph("_", "....", "....", "....", "....", "....", "....", "....", "....", "####")
glyph("*", "...", "#.#", ".#.", "#.#")
glyph("#", ".....", ".#.#.", "#####", ".#.#.", "#####", ".#.#.")
glyph("%", "##..", "##.#", "..#.", ".#..", "#.##", "..##")
glyph("&", ".##..", "#..#.", ".##..", ".#.#.", "#..##", "#..#.", ".##.#")
glyph("$", "..#.", ".###", "#.#.", ".##.", "..##", "###.", ".#..")
glyph("@", ".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###.")
glyph("<", "...", "...", "..#", ".#.", "#..", ".#.", "..#")
glyph(">", "...", "...", "#..", ".#.", "..#", ".#.", "#..")
glyph("^", ".#.", "#.#")
glyph("`", "#.", ".#")
glyph("~", "....", "....", "....", ".#.#", "#.#.")


# --- grotesk_digits: damage popups (2px strokes, 8 rows, outline baked in) -----------------------
D = {}


def digit(chars, *rows):
    for c in chars:
        D[c] = rows


digit("0", ".###.", "##.##", "##.##", "##.##", "##.##", "##.##", "##.##", ".###.")
digit("1", ".##.", "###.", ".##.", ".##.", ".##.", ".##.", ".##.", "####")
digit("2", ".###.", "##.##", "...##", "..##.", ".##..", "##...", "##...", "#####")
digit("3", "####.", "...##", "...##", ".###.", "...##", "...##", "...##", "####.")
digit("4", "...##", "..###", ".#.##", "##.##", "#####", "...##", "...##", "...##")
digit("5", "#####", "##...", "##...", "####.", "...##", "...##", "...##", "####.")
digit("6", ".###.", "##...", "##...", "####.", "##.##", "##.##", "##.##", ".###.")
digit("7", "#####", "...##", "...##", "..##.", "..##.", ".##..", ".##..", ".##..")
digit("8", ".###.", "##.##", "##.##", ".###.", "##.##", "##.##", "##.##", ".###.")
digit("9", ".###.", "##.##", "##.##", "##.##", ".####", "...##", "...##", ".###.")
digit("+", "......", "..##..", "..##..", "######", "######", "..##..", "..##..")
digit("-", "....", "....", "....", "####", "####")
digit("!", "##", "##", "##", "##", "##", "##", "..", "##")
digit("?", ".###.", "##.##", "...##", "..##.", ".##..", ".##..", ".....", ".##..")
digit(".", "..", "..", "..", "..", "..", "..", "##", "##")
digit("/", "...#", "...#", "..#.", "..#.", ".#..", ".#..", "#...", "#...")


class Face:
    def __init__(self, name, glyphs, rows, line_height, base, space, outline=False, chars=None):
        self.name, self.glyphs, self.rows = name, glyphs, rows
        self.line_height, self.base, self.space, self.outline = line_height, base, space, outline
        self.chars = chars or [chr(i) for i in range(32, 127)]

    def bitmap(self, c):
        rows = list(self.glyphs[c]) + [""] * (self.rows - len(self.glyphs[c]))
        w = max(len(r) for r in rows)
        a = np.zeros((self.rows, w), bool)
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                a[y, x] = ch == "#"
        return a

    def cell(self, c):
        """RGBA glyph as drawn: white ink, plus a 1px dark outline around it for outlined faces."""
        b = self.bitmap(c)
        if not self.outline:
            out = np.zeros(b.shape + (4,), np.uint8)
            out[b] = (255, 255, 255, 255)
            return out
        h, w = b.shape
        pad = np.zeros((h + 2, w + 2), bool)
        pad[1:-1, 1:-1] = b
        ring = np.zeros_like(pad)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            ring |= np.roll(np.roll(pad, dy, 0), dx, 1)
        out = np.zeros((h + 2, w + 2, 4), np.uint8)
        out[ring & ~pad] = (16, 8, 14, 255)
        out[pad] = (255, 255, 255, 255)
        return out

    def check(self):
        for c, rows in self.glyphs.items():
            widths = {len(r) for r in rows}
            assert len(widths) == 1, f"{self.name}: glyph {c!r} has ragged rows {widths}"
            assert len(rows) <= self.rows, f"{self.name}: glyph {c!r} is too tall"
        missing = [c for c in self.chars if c != " " and c not in self.glyphs]
        assert not missing, f"{self.name}: missing glyphs {missing}"

    def advance(self, c):
        return self.space if c == " " else self.bitmap(c).shape[1] + 1

    def measure(self, text):
        return sum(self.advance(c) for c in text)

    def draw(self, canvas, text, x, y, col):
        """Draw at (x, y) = top of the line (the baseline is y + base). col tints the white ink."""
        tint = np.array(col, float) / 255.0
        o = 1 if self.outline else 0
        for c in text:
            if c != " ":
                g = self.cell(c)
                h, w = g.shape[:2]
                region = canvas[y - o:y - o + h, x - o:x - o + w]
                g = g[:region.shape[0], :region.shape[1]]
                m = g[:, :, 3] > 0
                region[m] = (g[m] * tint).astype(np.uint8)
            x += self.advance(c)
        return x

    def build(self, outdir):
        """Pack the glyphs into an atlas and write a BMFont text file Godot imports as a FontFile."""
        self.check()
        o = 1 if self.outline else 0
        atlas_w = 128
        x = y = 1
        places = {}
        for c in self.chars:
            w = 0 if c == " " else self.bitmap(c).shape[1] + 2 * o
            if x + w + 1 > atlas_w:
                x, y = 1, y + self.rows + 2 * o + 1
            places[c] = (x, y, w)
            x += w + 1
        atlas_h = y + self.rows + 2 * o + 1
        img = np.zeros((atlas_h, atlas_w, 4), np.uint8)
        for c, (gx, gy, w) in places.items():
            if w:
                g = self.cell(c)
                img[gy:gy + g.shape[0], gx:gx + g.shape[1]] = g
        os.makedirs(outdir, exist_ok=True)
        Image.fromarray(img, "RGBA").save(os.path.join(outdir, f"{self.name}.png"))
        lines = [f'info face="{self.name}" size={self.line_height} bold=0 italic=0 charset="" unicode=1 '
                 f'stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=1,1 outline={o}',
                 f"common lineHeight={self.line_height} base={self.base} scaleW={atlas_w} scaleH={atlas_h} "
                 f"pages=1 packed=0 alphaChnl=0 redChnl=0 greenChnl=0 blueChnl=0",
                 f'page id=0 file="{self.name}.png"',
                 f"chars count={len(self.chars)}"]
        for c in self.chars:
            gx, gy, w = places[c]
            h = 0 if c == " " else self.rows + 2 * o
            off = -o if w else 0
            lines.append(f"char id={ord(c)} x={gx} y={gy} width={w} height={h} xoffset={off} "
                         f"yoffset={off} xadvance={self.advance(c)} page=0 chnl=15")
        with open(os.path.join(outdir, f"{self.name}.fnt"), "w", newline="\n") as f:
            f.write("\n".join(lines) + "\n")


BODY = Face("grotesk", G, ROWS, LINE_HEIGHT, BASE, SPACE_ADVANCE)
DIGITS = Face("grotesk_digits", D, 8, 10, 8, 3, outline=True, chars=[" "] + sorted(D))


# the body face, for other tools (logo.py)
def measure(text):
    return BODY.measure(text)


def draw_text(canvas, text, x, y, col):
    return BODY.draw(canvas, text, x, y, col)


# ----------------------------------------------------------------------------------------------
# specimen: everything drawn with the glyph bitmaps directly - what the game should show, at 1x
# ----------------------------------------------------------------------------------------------

def specimen(path):
    BODY.check()
    DIGITS.check()
    here = os.path.dirname(os.path.abspath(__file__))
    W, H = 320, 180
    c = np.array(Image.open(os.path.join(here, "cave_bg.png")).convert("RGBA"))
    c[0:122, 0:224, :3] = (c[0:122, 0:224, :3] * 0.35).astype(np.uint8)
    white, dim, gold, pink = (255, 255, 255, 255), (154, 146, 192, 255), (232, 213, 90, 255), (255, 107, 139, 255)
    y = 4
    allchars = "".join(chr(i) for i in range(33, 127))
    for chunk in (allchars[:36], allchars[36:66], allchars[66:]):
        draw_text(c, chunk, 4, y, white)
        y += LINE_HEIGHT
    y += 3
    for line, col in [("The Host", gold), ("A tongue lashes out of the Host's mouth!", white),
                      ("The Host's head tips back, jaw unhinged.", white),
                      ("The sucker flexes on its brain, hungry.", white),
                      ("Drained x2! Something warm slips away.", pink),
                      ("For a moment, the man's eyes clear.", white),
                      ("the quick brown fox jumps over the lazy dog", dim),
                      ("THE QUICK BROWN FOX JUMPS", dim)]:
        draw_text(c, line, 4, y, col)
        y += LINE_HEIGHT
    # damage popups straight on the cave, in the battle's popup colours
    for text, col, dy in [("12", (255, 255, 255, 255), 0), ("27!", (255, 225, 74, 255), 14),
                          ("+15", (125, 255, 140, 255), 28), ("-6", (255, 107, 107, 255), 42),
                          ("-2", (255, 154, 184, 255), 56), ("...", (184, 176, 224, 255), 70)]:
        DIGITS.draw(c, text, 240, 14 + dy, col)
    # a battle window at the real size: log 224x56 at (0,124), text at (5,127), 214 wide
    c[124:180, 0:224] = (12, 10, 26, 255)
    c[124, 0:224] = (200, 192, 240, 255)
    log = ["A tongue lashes out of the Host's mouth!", "Wanderer takes 6 damage.", "The Host reels, stunned.",
           "Attack  Guard  Item  Run   HP 41/60"]
    for i, line in enumerate(log):
        draw_text(c, line, 5, 127 + i * 11, white)
    c[124:180, 224:320] = (12, 10, 26, 255)
    c[124, 224:320] = (200, 192, 240, 255)
    for i, line in enumerate(["Wanderer", "HP   41/60", "MP   10/10", "Drained x1"]):
        draw_text(c, line, 229, 126 + i * 12, pink if i == 3 else white)
    Image.fromarray(c, "RGBA").resize((W * 4, H * 4), Image.NEAREST).save(path)
    print("longest log line:", max(measure(l) for l in log), "px of 214")


if __name__ == "__main__":
    if "--specimen" in sys.argv:
        specimen(sys.argv[sys.argv.index("--specimen") + 1])
    else:
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        out = args[0] if args else "art/fonts"
        for face in (BODY, DIGITS):
            face.build(out)
            print("wrote", os.path.join(out, face.name + ".fnt"), "+ .png")
