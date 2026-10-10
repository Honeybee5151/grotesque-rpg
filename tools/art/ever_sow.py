"""The Ever-Sow (enemy `ever_sow`): Plenty's holy pig and its boss - she regrows whatever is carved off.

A vast sow, three-quarter on, dressed like a shrine: candles and ribbons, a velvet cloth, a gold ring
through her snout, a butcher's cleaver left in her back; her flanks carved to raw meat, budding back.
Carnival. Focal accent: the raw red of the cuts.

Poses (104x96, one canvas and ground line):
  normal     standing, serene, the cuts raw.
  telegraph  knitting: she arches and lifts her snout, and new flesh swells out of the cuts like
             rising dough - next round she regrows unless the wound is salted.
  stunned    salted: the cuts crusted white, she slumps onto her belly, eyes squeezed, a candle down.
  hurt       her head jerks back.

    python tools/art/ever_sow.py [OUTDIR] [poses...] [--zoom]

Writes <pose>.png at 1x to OUTDIR (default art/monsters/ever_sow) and a sheet to
art/concepts/ever_sow_poses.png.
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import sculpt as sc
from host_concepts import strand, sheet
from plenty_concepts import PAL, materials, carnival_light, compose

W, H = 104, 96
SALT, SALT_DK = "#f4f2ee", "#c8c4bc"

# arch: back/head lift; slump: lying down; wounds: raw / swelling / salted; eyes: serene/shut/open
POSES = {
    "normal": dict(arch=0, slump=0, head=0, wounds="raw", eyes="serene", candles="lit"),
    "telegraph": dict(arch=6, slump=0, head=-11, wounds="swelling", eyes="open", candles="flare"),
    "stunned": dict(arch=-2, slump=9, head=6, wounds="salted", eyes="shut", candles="down"),
    "hurt": dict(arch=-1, slump=1, head=4, wounds="raw", eyes="shut", candles="lit"),
}
LABELS = {"normal": ("normal", "serene, carved, budding back"),
          "telegraph": ("telegraph", "knitting: the flesh swells back"),
          "stunned": ("stunned", "salted: the cuts can't close"),
          "hurt": ("hurt", "a flinch")}
CUTS = [(54, 50, 10, 6), (72, 54, 8, 8), (62, 66, 8, 4)]      # x, y, half-width, half-height


def build(pose):
    P = POSES[pose]
    S = sc.Scene(W, H)
    carnival_light(S)
    m = materials(S)
    sl, ar, hd = P["slump"], P["arch"], P["head"]
    S.group()
    # a vast sow, three-quarter on, facing left; she sinks onto her belly when salted
    body_y = 58 + sl
    S.ell((60, body_y - ar, -4), (40, 24, 22), m.sow, k=0)
    S.ell((58, body_y + 12, 4), (30, 13 - sl * 0.4, 14), m.sow, k=4.0)
    for (x, z) in [(30, 8), (38, -12), (82, 6), (88, -12)]:
        if sl > 4:              # legs splayed out under her
            S.cone((x, 74 + sl * 0.6, z), (x - 6 if x < 60 else x + 6, 91, z + 2), 5.5, 4.4, m.sow, k=2.0)
            S.ell((x - 7 if x < 60 else x + 7, 92, z + 3), (4.5, 2.4, 5), m.wood, k=0.8)
        else:
            S.cone((x, 72 + sl, z), (x - 2, 90, z), 5.5, 4.4, m.sow, k=2.0)
            S.ell((x - 2.5, 92, z + 1), (4.5, 2.4, 5), m.wood, k=0.8)
    hy = 52 + sl + hd
    S.ell((22, hy, 6), (16, 14, 14), m.sow, k=5.0)
    S.ell((8, hy + 5 - hd * 0.3, 10), (5, 5.5, 5), m.sow, k=2.0)
    for sz in (1, -1):
        S.ell((24, hy - 13, 6 + 7 * sz), (7, 3, 9), m.sow, k=1.5, rot=(0, 0, -30 - hd * 2))
    # carved flanks: slabs cut away to raw meat
    for (x, y, w, h) in CUTS:
        S.carve_ell((x, y + sl - ar * 0.6, 20), (w, h, 6), k=0.6, mat=m.raw)
    # budding back: small lumps in the cuts, or swelling out of them like dough, or salted shut
    S.group(k=0.8)
    for (x, y, w, h) in CUTS:
        cy = y + sl - ar * 0.6
        if P["wounds"] == "swelling":
            for dx, dy, r in [(-w * 0.4, -h * 0.2, 4.2), (w * 0.35, h * 0.1, 3.8), (0, h * 0.35, 3.4), (-w * 0.1, -h * 0.5, 3.0)]:
                S.sphere((x + dx, cy + dy, 20), r, m.raw)
        elif P["wounds"] == "raw":
            for dx, dy in [(-w * 0.4, -h * 0.2), (w * 0.3, h * 0.2)]:
                S.sphere((x + dx, cy + dy, 16), 2.0, m.raw)
    if P["wounds"] == "swelling":
        for (x, y, r) in [(44, 36, 4.0), (49, 33, 3.4), (80, 37, 3.8), (86, 42, 3.0), (50, 80, 4.2), (66, 82, 3.6), (76, 79, 3.2)]:
            S.sphere((x, y - ar * 0.8, 6), r, m.raw)
    # dressed like a shrine: the velvet cloth, candles, the gold snout ring, the cleaver
    S.group(k=1.0)
    S.ell((64, 37 + sl - ar, -2), (22, 6, 18), m.velvet)
    S.group(k=0.0)
    cand = [(52, 4, 9), (60, -6, 11), (68, 4, 8), (76, -4, 10)]
    for i, (x, z, h) in enumerate(cand):
        top = 33 + sl - ar
        if P["candles"] == "down" and i == 1:
            S.cone((x, top, z), (x + h, top + 2, z), 1.6, 1.4, m.wax)        # knocked over
        else:
            S.cone((x, top, z), (x, top - h, z), 1.6, 1.4, m.wax)
    S.torus((4, hy + 8 - hd * 0.3, 12), (1, 0, 0.3), 3.0, 0.9, m.gold)
    S.cone((84, 40 + sl - ar, 2), (90, 30 + sl - ar, 2), 1.2, 1.0, m.wood)
    S.ell((83, 44 + sl - ar, 2), (5, 6, 1.0), m.steel, rot=(0, 0, 30))
    R = S.render(ss=2)
    R.cleanup()
    details(R, m, P, sl, ar, hy, cand)
    return R


def details(R, m, P, sl, ar, hy, cand):
    # candle flames (flaring when she knits; none on the fallen one)
    for i, (x, z, h) in enumerate(cand):
        top = 33 + sl - ar
        if P["candles"] == "down" and i == 1:
            continue
        flame = 3 if P["candles"] == "flare" else 2
        for j in range(flame):
            R.px(x, int(top - h - 1 - j), "#fff09a" if j == 0 else "#f0c840")
    # the eye: serenely shut, open and bright as she knits, squeezed when salted
    ex, ey = 19, int(hy - 4)
    if P["eyes"] == "serene":
        R.pxs([(ex - 1, ey), (ex, ey + 1), (ex + 1, ey + 1), (ex + 2, ey)], "#4e1e28")
    elif P["eyes"] == "open":
        R.pxs([(ex, ey), (ex + 1, ey)], "#fff8f0")
        R.px(ex, ey, "#1a0a10")
        R.px(ex + 1, ey - 1, "#f8bcc0")
    else:
        R.pxs([(ex - 1, ey + 1), (ex, ey), (ex + 1, ey), (ex + 2, ey + 1)], "#260c12")
    # nostrils
    R.pxs([(6, int(hy + 4)), (9, int(hy + 4))], "#260c12")
    # the butcher's straight cut lines round each slab; salt crusted over them when salted
    for (x, y, w, h) in CUTS:
        cy = y + sl - ar * 0.6
        for xx in range(int(x - w), int(x + w) + 1):
            for yy in (int(cy - h), int(cy + h)):
                if R.on(xx, yy, m.sow):
                    R.px(xx, yy, "#8a3a48")
        if P["wounds"] == "salted":
            for xx in range(int(x - w + 1), int(x + w)):
                for yy in range(int(cy - h + 1), int(cy + h)):
                    if R.on(xx, yy, m.raw) and (xx * 3 + yy * 7) % 4 != 0:
                        R.px(xx, yy, SALT if (xx + yy) % 3 else SALT_DK)
    # ribbons round her middle
    for x in range(40, 90, 3):
        y = int(44 + sl - ar + 0.004 * (x - 64) ** 2)
        if R.on(x, y, m.sow):
            R.px(x, y, "#f0c840")
    if P["wounds"] == "salted":
        # salt spilled on the ground by her
        for x, y in [(44, 93), (47, 92), (51, 93), (66, 92), (70, 93)]:
            R.px(x, y, SALT)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "art/monsters/ever_sow"
    extra = out if args else "art/concepts"
    which = args[1:] or list(POSES)
    os.makedirs(out, exist_ok=True)
    bg = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_bg.png")).convert("RGBA")
    scenes = []
    for k in which:
        img = build(k).to_rgba()
        sc.save(img, os.path.join(out, f"{k}.png"))
        if "--zoom" in sys.argv:
            sc.save(img, os.path.join(extra, f"ever_sow_{k}_x6.png"), 6)
        scenes.append(compose(img, bg))
        print("wrote", os.path.join(out, f"{k}.png"))
    path = os.path.join(extra, "ever_sow_poses.png")
    sheet(scenes, [LABELS[k] for k in which], path)
    print("sheet:", path)
