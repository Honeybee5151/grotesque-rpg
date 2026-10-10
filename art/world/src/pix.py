"""Small pixel-art helpers for the world art (numpy + pillow). Everything is drawn at 1x.

Colours are '#rrggbb' strings or RGBA tuples. A Canvas is an RGBA numpy array with binary alpha.
"""
import numpy as np
from PIL import Image


def rgba(c, a=255):
    if isinstance(c, tuple):
        return c if len(c) == 4 else c + (a,)
    h = c.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), np.uint8)

    @staticmethod
    def from_ascii(rows, pal):
        """rows: list of equal-length strings; pal: char -> colour. '.' and ' ' are transparent."""
        c = Canvas(len(rows[0]), len(rows))
        c.ascii(rows, pal)
        return c

    def copy(self):
        c = Canvas(self.w, self.h)
        c.a = self.a.copy()
        return c

    # --- pixels -------------------------------------------------------------------------------
    def px(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = rgba(col)

    def pxs(self, pts, col):
        for x, y in pts:
            self.px(x, y, col)

    def solid(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h and self.a[y, x, 3] > 0

    def get(self, x, y):
        return tuple(int(v) for v in self.a[y, x])

    def rect(self, x, y, w, h, col):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, col)

    def hline(self, x0, x1, y, col):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            self.px(x, y, col)

    def vline(self, x, y0, y1, col):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            self.px(x, y, col)

    def line(self, x0, y0, x1, y1, col):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(n + 1):
            t = i / max(n, 1)
            self.px(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), col)

    def ellipse(self, cx, cy, rx, ry, col):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                    self.px(x, y, col)

    def ascii(self, rows, pal, x=0, y=0):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in ".  " or ch not in pal:
                    continue
                self.px(x + i, y + j, pal[ch])

    def blit(self, other, x, y):
        """Paste `other` at (x, y); transparent pixels of `other` are skipped."""
        for j in range(other.h):
            for i in range(other.w):
                if other.a[j, i, 3] > 0:
                    self.px(x + i, y + j, tuple(int(v) for v in other.a[j, i]))

    def flip(self):
        c = Canvas(self.w, self.h)
        c.a = self.a[:, ::-1].copy()
        return c

    def shifted(self, dx, dy):
        c = Canvas(self.w, self.h)
        c.blit(self, dx, dy)
        return c

    # --- finishing ----------------------------------------------------------------------------
    def outlined(self, col, rim=None):
        """1px outline around the silhouette (4-neighbourhood). `rim`: cold edge colour painted on
        the outermost right-facing pixels inside the silhouette, so dark sprites separate from
        dark ground (see docs/art.md)."""
        out = self.copy()
        for y in range(self.h):
            for x in range(self.w):
                if self.solid(x, y):
                    continue
                if any(self.solid(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    out.px(x, y, col)
        if rim:
            for y in range(self.h):
                for x in range(self.w):
                    if self.solid(x, y) and not self.solid(x + 1, y) and self.solid(x - 1, y):
                        out.px(x, y, rim)
        return out

    def image(self):
        return Image.fromarray(self.a, "RGBA")

    def save(self, path, scale=1):
        im = self.image()
        if scale != 1:
            im = im.resize((self.w * scale, self.h * scale), Image.NEAREST)
        im.save(path)


def sheet(frames, cols):
    """Pack equal-size canvases into a grid, row-major."""
    fw, fh = frames[0].w, frames[0].h
    rows = (len(frames) + cols - 1) // cols
    s = Canvas(fw * cols, fh * rows)
    for i, f in enumerate(frames):
        s.blit(f, (i % cols) * fw, (i // cols) * fh)
    return s
