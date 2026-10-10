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


def _walk(body, facing, phase, legs):
    """Step frames: lift one leg a pixel and swing the hands a little."""
    b = body.copy()
    y0, y1 = legs
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


def figure(rows_by_facing, pal, neck=9, legs=LEG_ROWS):
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
        walk_a, walk_b = _walk(b, f, 0, legs), _walk(b, f, 1, legs)
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


def finish(frames, poses=9):
    out = []
    for f in ("down", "up", "left", "right"):
        for c in frames[f][:poses]:
            out.append(c.outlined(OUTLINE, RIM))
    return out


def hero():
    return finish(figure({"down": HERO_DOWN, "up": HERO_UP, "left": HERO_LEFT}, HERO))


# Odo, the well-keeper. The same man the Host is drawn from (docs/bestiary.md): lanky, long arms,
# balding crown with lank dark strands past the ears, grey-brown shirt, dark trousers, barefoot.
# Village skin, warm in lantern light. He carries his lantern everywhere.
ODO = {
    "1": "#e2bc9e", "2": "#b88a74", "3": "#7a5652",      # skin
    "e": "#140c10",                                      # eyes, open mouth
    "h": "#0f0a12",                                      # lank hair
    "S": "#7a6e64", "s": "#5b524f", "t": "#3e363d",      # shirt light / mid / shade
    "P": "#3a3140", "p": "#241d29",                      # trousers
    "L": "#ffe9a8", "Y": "#e8a83a", "y": "#8e5418", "k": "#1c1418",   # lantern: glow, glass, brass, frame
}

ODO_DOWN = [
    "......1111......",  # 0  bald crown
    ".....111112.....",  # 1
    "....h111112h....",  # 2
    "....h1e11e2h....",  # 3
    "....h111122h....",  # 4
    "....h11ee22h....",  # 5  mouth open: he's always mid-sentence
    "....h.1222.h....",  # 6
    "....hSSSsstt....",  # 7
    "...SSSSSsssttt..",  # 8  shoulders
    "...SSSSssssttt..",  # 9
    "...SSStSssstst..",  # 10
    "...SSStSsssttt..",  # 11
    "...SS.tSssstt.t.",  # 12 long arms hang free
    "...S2.tSssstt.t.",  # 13
    "...12.tSsssst.3.",  # 14
    "..k1k.tPPppp..3.",  # 15 the lantern hangs from his hand
    "..kYk..PPppp....",  # 16
    "..YLY..PPp.pp...",  # 17
    "..kYk..PPp.pp...",  # 18
    "...y...PPp.pp...",  # 19
    ".......PPp.pp...",  # 20
    ".......PPp.pp...",  # 21
    "......122..122..",  # 22 bare feet
    "................",  # 23
]

ODO_UP = [
    "......1111......",  # 0
    ".....111112.....",  # 1
    "....h111112h....",  # 2
    "....hh1112hh....",  # 3
    "....hhhhhhhh....",  # 4  the strands hang down the back of his head
    "....hhhhhhhh....",  # 5
    "....hhh22hhh....",  # 6
    "....hSSSsstt....",  # 7
    "...SSSSSsssttt..",  # 8
    "...SSSSssssttt..",  # 9
    "...SSSSssssttt..",  # 10
    "...SSSSsssstt...",  # 11
    "...SS.Ssssst.t..",  # 12
    "...S1.Ssssst.t..",  # 13
    "...12.Ssssst.3..",  # 14
    "..k1k..PPppp..3.",  # 15
    "..kYk..PPppp....",  # 16
    "..YLY..PPp.pp...",  # 17
    "..kYk..PPp.pp...",  # 18
    "...y...PPp.pp...",  # 19
    ".......PPp.pp...",  # 20
    ".......PPp.pp...",  # 21
    "......122..122..",  # 22
    "................",  # 23
]

ODO_LEFT = [
    "......1111......",  # 0
    ".....111112.....",  # 1
    "....1111112h....",  # 2
    "....1e1112hh....",  # 3
    "...11111hhhh....",  # 4
    "....1ee12hhh....",  # 5
    ".....1222.hh....",  # 6
    ".....SSsth.h....",  # 7
    "....SSSssth.....",  # 8
    "....SSSsstt.....",  # 9
    "....SSSsstt.....",  # 10
    "....SS1sstt.....",  # 11 near arm, hand forward with the lantern
    "...k12ssstt.....",  # 12
    "...kYkssstt.....",  # 13
    "...YLYsssst.....",  # 14
    "...kYkPPppt.....",  # 15
    "....y.PPpp......",  # 16
    "......PPpp......",  # 17
    "......PPpp......",  # 18
    "......PPpp......",  # 19
    "......PPpp......",  # 20
    "......PPpp......",  # 21
    ".....1122.......",  # 22
    "................",  # 23
]

# Moth, Odo's daughter (about ten). A pale shift, bare feet, big dark eyes: the palest thing in
# the fen, like her name. She follows his lamp everywhere.
MOTH = {
    "1": "#e6c6b0", "2": "#bc9686", "3": "#80616a",      # skin
    "e": "#0d080e",                                      # eyes
    "h": "#1a1219", "H": "#33262f",                      # hair
    "W": "#cbc4cf", "w": "#9a92a6", "v": "#625a74",      # shift: light / mid / shade
}

MOTH_DOWN = [
    "................",  # 0
    "................",  # 1
    "................",  # 2
    "................",  # 3
    "................",  # 4
    "......hhhh......",  # 5
    ".....hHHhhh.....",  # 6
    ".....h1111h.....",  # 7
    ".....1e11e2.....",  # 8  big dark eyes
    ".....1e11e2.....",  # 9
    ".....h1112h.....",  # 10
    "......h22h......",  # 11
    ".....WWwwwv.....",  # 12
    "....WWWwwwvv....",  # 13
    "....1WWwwwv3....",  # 14
    "....1WWwwwv3....",  # 15
    "....WWWwwwvv....",  # 16
    "...WWWwwwwvvv...",  # 17
    "...WWwwwwwwvv...",  # 18
    "...Wwwwwwwwwv...",  # 19
    "......1..2......",  # 20
    "......1..2......",  # 21
    ".....11..22.....",  # 22
    "................",  # 23
]

MOTH_UP = [
    "................",  # 0
    "................",  # 1
    "................",  # 2
    "................",  # 3
    "................",  # 4
    "......hhhh......",  # 5
    ".....hHHhhh.....",  # 6
    ".....hHhhhh.....",  # 7
    ".....hhhhhh.....",  # 8
    ".....hhhhhh.....",  # 9
    ".....hhhhhh.....",  # 10
    "......hhhh......",  # 11
    ".....WWwwwv.....",  # 12
    "....WWWwwwvv....",  # 13
    "....1WWwwwv3....",  # 14
    "....1WWwwwv3....",  # 15
    "....WWWwwwvv....",  # 16
    "...WWWwwwwvvv...",  # 17
    "...WWwwwwwwvv...",  # 18
    "...Wwwwwwwwwv...",  # 19
    "......1..2......",  # 20
    "......1..2......",  # 21
    ".....11..22.....",  # 22
    "................",  # 23
]

MOTH_LEFT = [
    "................",  # 0
    "................",  # 1
    "................",  # 2
    "................",  # 3
    "................",  # 4
    "......hhhh......",  # 5
    ".....hHHhhh.....",  # 6
    ".....11hhhh.....",  # 7
    "....1e11hhh.....",  # 8
    "....1e11hhh.....",  # 9
    ".....112hhh.....",  # 10
    "......22hh......",  # 11
    "......WWwv......",  # 12
    ".....WWwwvv.....",  # 13
    ".....W1wwvv.....",  # 14
    ".....W1wwvv.....",  # 15
    ".....WWwwvv.....",  # 16
    "....WWwwwwvv....",  # 17
    "....WWwwwwvv....",  # 18
    "....Wwwwwwwv....",  # 19
    "......1.2.......",  # 20
    "......1.2.......",  # 21
    ".....11.2.......",  # 22
    "................",  # 23
]


def odo():
    return finish(figure({"down": ODO_DOWN, "up": ODO_UP, "left": ODO_LEFT}, ODO, neck=7), 3)


def moth():
    return finish(figure({"down": MOTH_DOWN, "up": MOTH_UP, "left": MOTH_LEFT}, MOTH, neck=12, legs=(20, 24)), 3)


# The Host on the map: Odo bent onto his knuckles, the frog riding his back, the pink cord from its
# mouth down into his opened crown (docs/bestiary.md). Faces down, toward whoever it lurches at.
# Two frames of a lurch. 24x26.
HOST = {
    "G": "#848a40", "g": "#5a6530", "f": "#3a4626", "F": "#232f1e",   # frog
    "b": "#a48e60", "B": "#7a6646",                                  # frog belly
    "o": "#f4c040",                                                  # frog eyes
    "C": "#ee8696", "c": "#cc4862", "k": "#681430",                  # cord and sucker
    "1": "#c2bab4", "2": "#8a8490", "3": "#5a5260",                  # drained skin
    "S": "#59504f", "s": "#403840", "t": "#2b252e",                  # shirt
    "p": "#241d29", "e": "#0b0710",
}

HOST_A = [
    "........................",  # 0
    "........gGGGGg..........",  # 1
    ".......gGoGGoGg.........",  # 2  the frog, eyes heavy-lidded
    "......fgGGGGGGgf........",  # 3
    "......fggGGkGGggf.......",  # 4
    ".....FfgbbbkbbbgfF......",  # 5
    ".....FfgbbbcbbbgfF......",  # 6
    "......FfgBbcbBgfF.......",  # 7
    ".......FfffcfffF........",  # 8
    ".....sSSSSSCSSSsst......",  # 9  his back, the cord running down it
    "....sSSSSSScSSSssst.....",  # 10
    "...2sSSSSSScSSsssst2....",  # 11
    "...2ssSSS1kck1ssstt2....",  # 12 the crown hanging toward you, sucker seated in it
    "..22.ssS11cCc11stt.22...",  # 13
    "..2...t111kck111t...2...",  # 14
    "..2....2111c1112....2...",  # 15
    ".22.....2111112.....22..",  # 16
    ".2.......22322......2...",  # 17
    ".2........e.e.......22..",  # 18
    "22..................2...",  # 19
    "2...................22..",  # 20
    "22..................2...",  # 21
    "12..................21..",  # 22
    "122................2221.",  # 23
    "1222...............2.11.",  # 24
    "........................",  # 25
]


def host():
    a = Canvas.from_ascii(HOST_A, HOST)
    b = a.copy()
    # the lurch: the left arm reaches a pixel further, the right drags back up
    left, right = Canvas(24, 26), Canvas(24, 26)
    left.a[16:, :10] = a.a[16:, :10]
    right.a[16:, 14:] = a.a[16:, 14:]
    b.a[16:, :10] = 0
    b.a[16:, 14:] = 0
    b.blit(left, 0, 1)
    b.blit(right, 0, -1)
    body = Canvas(24, 26)
    body.a[:16] = b.a[:16]
    b.a[:16] = 0
    b.blit(body, 0, 1)
    return [a.outlined(OUTLINE, RIM), b.outlined(OUTLINE, RIM)]


# Odo after the fight: face down on the cave floor, one long arm out, the open crown toward you.
# 28x12.
ODO_DOWN_DEAD = [
    "............................",  # 0
    "....hh......................",  # 1
    "..h1kch.....................",  # 2  the ring the sucker left
    ".h11c11h.SSSSSSSsss.........",  # 3
    ".h1kck1hSSSSSSSsssstt.......",  # 4
    "..h111hsSSSSSSsssssttpppp...",  # 5
    "...h1h.sSSSSSssssstttpppp...",  # 6
    "222222222SSSssssttt..pppp.12",  # 7  the arm flung out past his head
    "12.........ssstt.....ppppp22",  # 8
    "............................",  # 9
    "............................",  # 10
    "............................",  # 11
]

DEAD = dict(ODO)
DEAD.update({"1": "#b4aaa6", "2": "#8a807e", "h": "#0f0a12", "c": "#cc4862", "k": "#681430",
             "S": "#6a605a", "s": "#4e4648", "t": "#352e35"})


def odo_dead():
    return Canvas.from_ascii(ODO_DOWN_DEAD, DEAD).outlined(OUTLINE, RIM)


# The frog after it peels away: spent, flat, a deflated sucker trailing. 14x8.
FROG_SPENT = [
    "..............",
    "...gGGGg......",
    "..gGoGGGg.....",
    ".fgGGGGGgf....",
    ".FfgbbbgfFkc..",
    "..FfffffF..kcC",
    "..............",
    "..............",
]


def frog_spent():
    return Canvas.from_ascii(FROG_SPENT, HOST).outlined(OUTLINE)
