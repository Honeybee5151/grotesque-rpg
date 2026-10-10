"""Compose a map from an ASCII layout with the same autotiling the game uses (scripts/world/tiles.gd),
for judging tiles and props outside the engine.

    python art/world/src/preview.py OUT.png [scale]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pix import Canvas  # noqa: E402
import fen  # noqa: E402

WATERISH = "~|="
SPEC = {"~": ([0, 1], True), ".": ([2, 3, 4], True), ",": ([5, 6], True), "o": ([7], False),
        "|": ([8], True), "=": ([9], True)}


def variant(x, y, n):
    return ((x * 73856093) ^ (y * 19349663)) % n


def compose(rows, atlas):
    h, w = len(rows), len(rows[0])
    out = Canvas(w * 16, h * 16)
    for y in range(h):
        for x in range(w):
            ch = rows[y][x]
            spec_rows, masked = SPEC.get(ch, SPEC["."])
            if masked:
                mask = 0
                for bit, (dx, dy) in ((1, (0, -1)), (2, (1, 0)), (4, (0, 1)), (8, (-1, 0))):
                    nx, ny = x + dx, y + dy
                    n = rows[ny][nx] if 0 <= nx < w and 0 <= ny < h else ch
                    if (ch in WATERISH) != (n in WATERISH):
                        mask |= bit
                col, row = mask, spec_rows[variant(x, y, len(spec_rows))]
            else:
                col, row = variant(x, y, 4), spec_rows[0]
            tile = Canvas(16, 16)
            tile.a = atlas.a[row * 16:(row + 1) * 16, col * 16:(col + 1) * 16].copy()
            out.blit(tile, x * 16, y * 16)
    return out


SAMPLE = [
    "~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~",
    "~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~",
    "~~~~~~~~~~,,,,,.,,,~~~~~~~~~~~",
    "~~~~~~,,,,.......,,,,,~~~~~~~~",
    "~~~~~,,.............,,,,~~~~~~",
    "~~~~,,...............,,,,~~~~~",
    "~~~~,.................,,,~~~~~",
    "~~~,,..................,,~~~~~",
    "~~~,......oooooooooo...,~~~~~~",
    "~~~,......oooooooooo....~~~~~~",
    "~~~~,.....oooooooooo...,~~~~~~",
    "~~~~,,....oooooooooo..,,~~~~~~",
    "~~~~~,.................,~~~~~~",
    "~~~~~~,,..............,,~~~~~~",
    "~~~~~~~~,,,.......,,,,~~~~~~~~",
    "~~~~~~~~~~~~,,.,,~~~~~~~~~~~~~",
    "~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~",
    "~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~",
    "~~~~~~~~~~~====|~~~~~~~~~~~~~~",
    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
]

if __name__ == "__main__":
    out = sys.argv[1]
    scale = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    a = fen.atlas()
    compose(SAMPLE, a).save(out, scale)
    a.save(out.replace(".png", "_atlas.png"), scale)
    print("wrote", out)
