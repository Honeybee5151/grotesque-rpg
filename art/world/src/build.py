"""Build every world PNG into art/world/.

    python art/world/src/build.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import cave  # noqa: E402
import fen  # noqa: E402
import people  # noqa: E402
import props  # noqa: E402
from pix import sheet  # noqa: E402

OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def save(canvas, name):
    path = os.path.join(OUT, name)
    canvas.save(path)
    print("wrote", os.path.relpath(path, os.path.join(OUT, "..", "..")), f"{canvas.w}x{canvas.h}")


if __name__ == "__main__":
    save(fen.atlas(), "fen_tiles.png")
    save(sheet(people.hero(), 10), "hero.png")
    save(sheet(people.odo(), 3), "odo.png")
    save(sheet(people.moth(), 3), "moth.png")
    save(sheet(people.odo_freed(), 3), "odo_freed.png")
    save(sheet(people.host(), 2), "host_walk.png")
    save(people.odo_dead(), "odo_dead.png")
    save(people.frog_spent(), "frog_spent.png")
    save(props.well(), "well.png")
    for kind in ("odo", "shut", "dark"):
        save(props.house(kind), f"house_{kind}.png")
    save(props.lamp_post(), "lamp_post.png")
    for i in range(3):
        save(props.reeds(i), f"reeds_{i}.png")
    save(props.bubble(), "bubble.png")
    save(props.lantern_icon(), "item_lantern.png")
    save(cave.atlas(), "cave_tiles.png")
    save(cave.rungs(), "rungs.png")
    save(cave.lantern_rock(), "lantern_rock.png")
    save(cave.lantern_rock(False), "rock.png")
    for i in range(3):
        save(cave.stalagmite(i), f"stalagmite_{i}.png")
