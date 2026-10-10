"""People of the world, drawn as ASCII at 1x and assembled into sprite sheets.

Sheet layout (keep in sync with scripts/world/actor.gd): one row per facing - down, up, left, right -
and one column per pose. Every frame is FW x FH with the feet on the bottom row.
    0 stand, 1 walk A, 2 walk B, 3 nod, 4 shake (head one way), 5 shake (the other way),
    6 shrug, 7 point, 8 show (both hands raised)
"""
from pix import Canvas

FW, FH = 16, 24
OUTLINE = "#0a0710"
RIM = "#26363f"

# The hero: fen-soaked dark coat, plastered black hair, a rust scarf over his mouth (his one accent).
HERO = {
    "h": "#110c16", "H": "#2b2433",                      # hair
    "1": "#d6b8a6", "2": "#a88378", "3": "#6f505a",      # skin light / mid / shade
    "e": "#0b0710",                                      # eyes
    "R": "#c25a3c", "r": "#8f3628", "q": "#5a1d1f",      # scarf
    "C": "#4d4b68", "c": "#302e46", "k": "#1b1929",      # coat
    "w": "#151018",                                      # shirt in the coat's opening
    "P": "#3b3039", "p": "#261d27",                      # trousers
    "B": "#2c2128", "b": "#130c11",                      # boots
}

# ruler     0123456789ABCDEF
HERO_DOWN = [
    "................",  # 0
    "......hhhh......",  # 1
    ".....hHHhhh.....",  # 2
    "....hHHhhhhh....",  # 3
    "....hH1111hh....",  # 4
    "....h111112h....",  # 5
    "....h1e11e2h....",  # 6
    "....hh1122hh....",  # 7
    "....hRRRRrqh....",  # 8  scarf over the mouth
    ".....RRRrrq.....",  # 9
    "...CcRRrrqqck...",  # 10 shoulders
    "..CCccqrrqccck..",  # 11
    "..CCcccwwcrqck..",  # 12 coat opening, scarf tail
    "..CCcccwwcrqck..",  # 13
    "..Ccccwwcccqkk..",  # 14
    "..Ccccwwcccckk..",  # 15
    "..1cccccccckk3..",  # 16 hands
    "..1Ccccccccck3..",  # 17
    "...Cccccccckk...",  # 18
    "....PPpp.Ppp....",  # 19 legs
    "....PPp..Ppp....",  # 20
    "....PPp..Ppp....",  # 21
    "...BBbb..Bbbb...",  # 22 boots
    "...bbbb..bbbb...",  # 23
]

HERO_UP = [
    "................",  # 0
    "......hhhh......",  # 1
    ".....hHHhhh.....",  # 2
    "....hHHhhhhh....",  # 3
    "....hHhhhhhh....",  # 4
    "....hHhhhhhh....",  # 5
    "....hhhhhhhh....",  # 6
    "....hhhhhhhh....",  # 7
    ".....hhhhhh.....",  # 8
    ".....RRRrrq.....",  # 9  scarf knot at the back of the neck
    "...CcRRrrqqck...",  # 10
    "..CCccqrrqccck..",  # 11
    "..CCcccrqcccck..",  # 12
    "..CCcccrqcccck..",  # 13
    "..Ccccccqcccck..",  # 14
    "..Ccccccccccck..",  # 15
    "..1cccccccccc3..",  # 16
    "..1Ccccccccck3..",  # 17
    "...Cccccccckk...",  # 18
    "....PPpp.Ppp....",  # 19
    "....PPp..Ppp....",  # 20
    "....PPp..Ppp....",  # 21
    "...BBbb..Bbbb...",  # 22
    "...bbbb..bbbb...",  # 23
]

HERO_LEFT = [
    "................",  # 0
    "......hhhh......",  # 1
    ".....hHHhhhh....",  # 2
    "....hHHhhhhhh...",  # 3
    "....h11hhhhhh...",  # 4
    "...1111hhhhhh...",  # 5
    "...1e11hhhhh....",  # 6
    "....1122hhhh....",  # 7
    "....RRRrqhh.....",  # 8  scarf over the mouth
    ".....RRrrq......",  # 9
    ".....CRrrqk.....",  # 10
    "....CCcrqcck....",  # 11
    "....CCccqcck....",  # 12
    "....CCcccqck....",  # 13 his near arm hangs in front of the coat
    "....CCcccqck....",  # 14
    "....CcCccqck....",  # 15
    "....Cc1cccck....",  # 16
    "....Cc3ccckk....",  # 17
    "....Ccccckk.....",  # 18
    ".....PPpPp......",  # 19
    ".....PPpPp......",  # 20
    ".....PPpPp......",  # 21
    "....BBbBbb......",  # 22
    "....bbbbbb......",  # 23
]

LEG_ROWS = (19, 24)


def _check(rows):
    assert len(rows) == FH, len(rows)
    for i, r in enumerate(rows):
        assert len(r) == FW, (i, r, len(r))


def _art(rows, pal):
    _check(rows)
    return Canvas.from_ascii(rows, pal)


def _split(c, at):
    """Split a figure into head (rows < at) and body (rows >= at)."""
    head, body = Canvas(FW, FH), Canvas(FW, FH)
    head.a[:at] = c.a[:at]
    body.a[at:] = c.a[at:]
    return head, body


def _walk(body, facing, phase):
    """Step frames: lift one leg a pixel and swing the hands a little."""
    b = body.copy()
    y0, y1 = LEG_ROWS
    legs = Canvas(FW, FH)
    legs.a[y0:y1] = b.a[y0:y1]
    b.a[y0:y1] = 0
    if facing in ("down", "up"):
        left, right = Canvas(FW, FH), Canvas(FW, FH)
        left.a[:, :8] = legs.a[:, :8]
        right.a[:, 8:] = legs.a[:, 8:]
        lift, stay = (left, right) if phase == 0 else (right, left)
        b.blit(stay, 0, 0)
        b.blit(lift, 0, -1)
    else:
        # side view: legs scissor - shift the front leg forward, the back leg back
        front, back = Canvas(FW, FH), Canvas(FW, FH)
        front.a[:, :8] = legs.a[:, :8]
        back.a[:, 8:] = legs.a[:, 8:]
        d = -1 if phase == 0 else 1
        b.blit(back, -d, 0)
        b.blit(front, d, 0)
    return b


def figure(rows_by_facing, pal, neck=9):
    """All poses for one character: dict facing -> list of canvases (columns of the sheet)."""
    art = {f: _art(rows_by_facing[f], pal) for f in ("down", "up", "left")}
    art["right"] = art["left"].flip()
    heads, bodies = {}, {}
    for f, c in art.items():
        heads[f], bodies[f] = _split(c, neck)

    def compose(body, head, hx=0, hy=0):
        out = body.copy()
        out.blit(head, hx, hy)
        return out

    frames = {}
    for f in ("down", "up", "left", "right"):
        h, b = heads[f], bodies[f]
        walk_a, walk_b = _walk(b, f, 0), _walk(b, f, 1)
        shake = {"down": (heads["left"], heads["right"]), "up": (h.shifted(-1, 0), h.shifted(1, 0)),
                 "left": (h.shifted(-1, 0), h.shifted(1, 0)), "right": (h.shifted(1, 0), h.shifted(-1, 0))}[f]
        frames[f] = [
            compose(b, h),                 # 0 stand
            compose(walk_a, h, 0, 1),      # 1 walk A (head bobs down a pixel)
            compose(walk_b, h, 0, 1),      # 2 walk B
            compose(b, h, 0, 1),           # 3 nod
            compose(b, shake[0]),          # 4 shake one way
            compose(b, shake[1]),          # 5 shake the other way
            compose(b, h),                 # 6 shrug (arms drawn below)
            compose(b, h),                 # 7 point
            compose(b, h),                 # 8 show
        ]
    return frames


def finish(frames):
    out = []
    for f in ("down", "up", "left", "right"):
        for c in frames[f]:
            out.append(c.outlined(OUTLINE, RIM))
    return out


def hero():
    return finish(figure({"down": HERO_DOWN, "up": HERO_UP, "left": HERO_LEFT}, HERO))
