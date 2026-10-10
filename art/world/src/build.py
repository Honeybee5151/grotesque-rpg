"""Build every world PNG into art/world/.

    python art/world/src/build.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import fen  # noqa: E402
import people  # noqa: E402
from pix import sheet  # noqa: E402

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def save(canvas, name):
    path = os.path.join(OUT, name)
    canvas.save(path)
    print("wrote", os.path.relpath(path, os.path.join(OUT, "..", "..")), f"{canvas.w}x{canvas.h}")


if __name__ == "__main__":
    save(fen.atlas(), "fen_tiles.png")
    save(sheet(people.hero(), 9), "hero.png")
