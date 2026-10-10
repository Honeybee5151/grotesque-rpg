"""Old Iron (enemy `old_iron`): the whale that hunts the hunters (Miles' pick, concept B).

A vast sperm whale spyhopping out of black water - head stood straight up to watch you - its hide
bristling with the rusted harpoons of every whaler who ever struck it, rotten ropes trailing. It
never died; it kept every harpoon, and now it gives them back. Its old eye is amber, the colour of
lamplight: lamps burn whale oil. That eye is the focal accent.

Poses (104x118, one canvas and ground line):
  normal     spyhopping, watching, jaw hanging open, the harpoons standing out of its back.
  telegraph  it wrenches a harpoon out of its own hide and clamps it crosswise in its jaw, rearing
             back to fling it; the wound it came out of runs dark.
  hurt       it rolls away from the blow, the eye squeezed shut.

    python tools/art/old_iron.py [OUTDIR] [poses...] [--zoom]

Writes <pose>.png at 1x to OUTDIR (default art/monsters/old_iron) and a sheet to
art/concepts/old_iron_poses.png.
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import sculpt as sc
from host_concepts import horror_light, strand, sheet, compose
from whale_concepts import PAL, materials, unit, on_ellipsoid, ROPE, ROPE_DK, FOAM, FOAM_DK

W, H = 104, 118
PAL = dict(PAL)
PAL["amber"] = dict(ramp=["#3a1e04", "#6e3a0a", "#a85e12", "#d88a1c", "#f4c040"], outline="#140a02",
                    spec="#fff2c0", shin=30.0, spec_thr=0.5)
BLOOD, BLOOD_DK = "#681430", "#3a0a1e"

# lean: how far the column tips (degrees, + clockwise); jaw: "open" or "bite" (on a harpoon);
# eye: "open" / "shut"; torn: index of the harpoon it pulled out (None if all still in)
POSES = {
    "normal": dict(lean=7, dy=0, jaw="open", eye="open", torn=None),
    "telegraph": dict(lean=-11, dy=-3, dx=8, jaw="bite", eye="open", torn=3),
    "hurt": dict(lean=16, dy=3, jaw="open", eye="shut", torn=None),
}
LABELS = {"normal": ("normal", "watching you out of the black water"),
          "telegraph": ("telegraph", "it pulls a harpoon out to give it back"),
          "hurt": ("hurt", "it rolls away from the blow")}
DIRS = [(0.95, -0.3, 0.1), (0.9, 0.1, 0.15), (0.85, 0.4, 0.2), (0.6, -0.75, 0.15), (0.2, -1.0, 0.2),
        (-0.35, -0.9, 0.3), (0.7, -0.2, 0.7), (0.5, 0.25, 0.8), (0.95, 0.65, 0.2), (0.3, -0.55, 0.8),
        (-0.7, -0.4, 0.4)]


def rot_about(p, c, deg):
    """Rotate point p about c in the screen plane (+deg clockwise, y down)."""
    a = np.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * np.cos(a) - y * np.sin(a), c[1] + x * np.sin(a) + y * np.cos(a), p[2])


def build(pose):
    P = POSES[pose]
    S = sc.Scene(W, H)
    horror_light(S)
    m = materials(S)
    m.amber = S.mat("amber", **PAL["amber"])
    pivot = (54, 112, 0)                       # it tips about where it breaks the water
    lean = P["lean"] - 7                       # the design below is drawn at lean 7

    def T(p):
        q = rot_about(p, pivot, lean)
        return (q[0] + P.get("dx", 0), q[1] + P["dy"], q[2])

    S.group()
    S.ell((52, 113, 0), (52, 2.6, 22), m.water)

    S.group()
    body_c, body_r = (56, 64, -8), (24, 54, 21)
    S.ell(T(body_c), body_r, m.whale, rot=(0, 0, P["lean"]))
    S.ell(T((52, 38, 4)), (21, 30, 15), m.whale, k=6.0, rot=(0, 0, P["lean"]))
    S.ell(T((51, 17, -2)), (24, 9, 19), m.whale, k=7.0, rot=(0, 0, P["lean"]))
    S.ell((26, 106, 6), (11, 3, 5), m.whale, k=2.0, rot=(0, 0, -22))
    S.carve_ell(T((37, 74, 14)), (3.0, 30, 6), k=1.0, rot=(0, 0, P["lean"] + 5))
    # the narrow jaw: hanging open down its front, or swung up to bite on a harpoon
    S.group(k=1.5)
    hinge = T((44, 104, 12))
    tip = T((28, 44, 18)) if P["jaw"] == "open" else T((36, 46, 17))
    S.cone(hinge, tip, 5.4, 3.0, m.wbelly, k=1.0)
    S.ell(hinge, (6.5, 5, 6), m.wbelly, k=2.0)
    # its old eye, by the hinge: amber, the colour of lamplight
    eye_c = T((49.5, 93, 18))
    S.group(k=1.2)
    S.ell(T((48, 93, 15)), (5, 4.2 if P["eye"] == "open" else 3.4, 4), m.whale)
    if P["eye"] == "open":
        S.group(k=0.6)
        S.sphere(eye_c, 2.9, m.amber)
    # the harpoons still in its hide (one pulled when it means to throw)
    rng = np.random.default_rng(7)
    shafts = []
    S.group(k=0.0)
    for i, d in enumerate(DIRS):
        p, n = on_ellipsoid(body_c, body_r, d)
        n = unit(n + rng.normal(0, 0.15, 3) + np.array([0.0, -0.25, 0.0]))
        length = rng.uniform(13, 21)
        if i == P["torn"]:
            shafts.append((T(tuple(p)), None))
            continue
        tip_h = p + n * length
        while length > 6:            # keep every shaft (and its rope) inside the canvas, whatever the lean
            tx, ty, _ = T(tuple(tip_h))
            if 3 <= tx <= W - 6 and ty >= 3:
                break
            length -= 1.0
            tip_h = p + n * length
        S.sphere(T(tuple(p + n * 0.8)), 1.7, m.iron)
        S.cone(T(tuple(p + n * 0.5)), T(tuple(tip_h)), 1.1, 0.8, m.wood)
        shafts.append((T(tuple(p)), T(tuple(tip_h))))
    held = None
    if P["jaw"] == "bite":
        # the pulled harpoon, clamped crosswise in its teeth, its barbed head toward you
        mid = np.array(T((42, 60, 20)))
        a, b = mid + np.array([17, -11, 2]), mid + np.array([-15, 8, 8])
        S.group(k=0.0)
        S.cone(tuple(a), tuple(b), 1.6, 1.3, m.wood)
        head = b + np.array([-6.5, 3.6, 1.5])
        S.cone(tuple(b), tuple(head), 2.8, 0.5, m.iron)
        for d in ((0, -6, 0), (2, 5, 0)):
            base = b + np.array([-3.5, 2, 0.6])
            S.cone(tuple(base), tuple(base + np.array(d)), 1.3, 0.3, m.iron)
        held = (a, b)

    R = S.render(ss=2)
    R.cleanup()
    # prune-wrinkled hide: wavy creases across it
    for y0 in range(14, 106, 6):
        for x in range(4, 102):
            y = y0 + int(1.5 * np.sin(x * 0.35 + y0))
            if 0 <= y < H and R.on(x, y, m.whale) and R.code[y, x] % 8 in (2, 3):
                R.px(x, y, PAL["whale"]["ramp"][1])
    # pegs of teeth along the jaw, a pink gum
    for t in np.linspace(0.1, 0.92, 11):
        x = int(hinge[0] + (tip[0] - hinge[0]) * t + 3)
        y = int(hinge[1] + (tip[1] - hinge[1]) * t)
        if R.on(x - 1, y, m.wbelly):
            R.px(x - 1, y, "#9c2646")
        if R.on(x, y, m.wbelly) or R.on(x + 1, y, m.whale):
            R.pxs([(x, y), (x + 1, y)], "#ebe3c6")
    # ropes trailing off the shafts; the torn wound running dark
    for p, tip_h in shafts:
        if tip_h is None:
            x, y = int(p[0]), int(p[1])
            for dx in range(-2, 3):
                for dy in range(-1, 3):
                    if abs(dx) + abs(dy) <= 3 and R.on(x + dx, y + dy, m.whale):
                        R.px(x + dx, y + dy, BLOOD_DK if abs(dx) + abs(dy) <= 1 else BLOOD)
            strand(R, [(x, y + 3), (x + 1, y + 10), (x, y + 18)], BLOOD, only=(m.whale,))
            strand(R, [(x - 2, y + 3), (x - 2, y + 9)], BLOOD, only=(m.whale,))
            continue
        x, y = int(tip_h[0]), int(tip_h[1])
        drop, sway = int(rng.uniform(4, 9)), int(rng.choice([-4, -3, 3, 4]))
        strand(R, [(x, y), (x + sway // 2, y + drop // 2), (x + sway, y + drop)], ROPE)
        R.px(x + sway, y + drop, ROPE_DK)
    if held is not None:
        a, b = held
        strand(R, [(int(a[0]), int(a[1])), (int(a[0]) + 6, int(a[1]) + 6), (int(a[0]) + 4, int(a[1]) + 14)], ROPE)
    # the eye: a slit of a pupil and a glint - or the crease of a shut eye
    ex, ey = int(eye_c[0]), int(eye_c[1])
    if P["eye"] == "open":
        R.pxs([(ex, ey - 1), (ex, ey), (ex, ey + 1)], "#140a02")
        R.px(ex - 1, ey - 1, "#fff2c0")
    else:
        R.pxs([(ex - 2, ey), (ex - 1, ey + 1), (ex, ey + 1), (ex + 1, ey + 1), (ex + 2, ey)], "#06080c")
    for dx, dy in [(-7, -4), (-6, 5)]:
        strand(R, [(ex + dx, ey + dy), (ex + dx + 5, ey + dy - 1), (ex + dx + 10, ey + dy)], "#0c1016", only=(m.whale,))
    # old wounds, barnacles on the brow, squid-sucker scars - placed in the body's frame
    for x, y in [(70, 48), (62, 72), (78, 86), (58, 26), (82, 62)]:
        qx, qy, _ = T((x, y, 0))
        qx, qy = int(qx), int(qy)
        if R.on(qx, qy, m.whale):
            R.pxs([(qx, qy), (qx + 1, qy)], "#06080c")
            R.pxs([(qx - 1, qy), (qx + 2, qy), (qx, qy - 1), (qx + 1, qy + 1)], "#566474")
    for x, y in [(40, 20), (42, 22), (39, 23), (46, 17), (48, 19)]:
        qx, qy, _ = T((x, y, 0))
        if R.on(int(qx), int(qy), m.whale):
            R.px(int(qx), int(qy), "#929aa2")
    for cx, cy in [(66, 36), (74, 74)]:
        qx, qy, _ = T((cx, cy, 0))
        for a in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            x, y = int(qx + 3 * np.cos(a)), int(qy + 3 * np.sin(a))
            if R.on(x, y, m.whale):
                R.px(x, y, "#3c4856")
    # foam where it breaks the water
    for x in range(4, 100):
        if (x * 13) % 7 < 3:
            R.px(x, 110 + (x % 3 == 0), FOAM if (x * 5) % 4 else FOAM_DK)
    return R


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "art/monsters/old_iron"
    extra = out if args else "art/concepts"
    which = args[1:] or list(POSES)
    os.makedirs(out, exist_ok=True)
    bg = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_bg.png")).convert("RGBA")
    scenes = []
    for k in which:
        img = build(k).to_rgba()
        sc.save(img, os.path.join(out, f"{k}.png"))
        if "--zoom" in sys.argv:
            sc.save(img, os.path.join(extra, f"old_iron_{k}_x6.png"), 6)
        scenes.append(compose(img, bg))
        print("wrote", os.path.join(out, f"{k}.png"))
    path = os.path.join(extra, "old_iron_poses.png")
    sheet(scenes, [LABELS[k] for k in which], path)
    print("sheet:", path)
