# Art bible (v0)

Lessons from redrawing the Host. Read before drawing anything.

## The look
- **Native 1x pixels.** Everything shares the 320x180 pixel grid. Never upscale a sprite in-engine.
- **Silhouette first.** A monster must read as a black shape. Posture and asymmetry carry the horror:
  a lolled head, a dropped shoulder, knees that bend wrong, a limb too long.
- **Grotesque is anatomy, not gore.** The wrongness is in how the body is put together: a mouth where
  no mouth belongs, a body being worn by something else.
- **One focal accent.** The most saturated, brightest thing on the sprite is the point of the monster
  (for the Host: the sucker in the brain). Everything else stays dark and desaturated. Competing
  accents (bright eyes + white teeth + cyan drool + pink flesh) turn into noise.
- **Light:** a harsh, mostly-overhead key light from the upper left, deep shadows, plus a 1px cold
  rim on right-facing edges so dark sprites separate from the dark cave.
- **Palettes:** 5-step hue-shifted ramps per material (`PAL` in `tools/art/host_concepts.py`):
  shadows lean purple so they sit in the cave, highlights lean warm. No smooth gradients,
  no anti-aliasing against the background, no pillow shading.
- **Detail size:** below 2px a detail becomes noise. Single pixels only where placed on purpose
  (an eye glint, a tooth), with coordinates read from `tools/art/grid.py`.
- **Two flavours of grotesque** - pick one per monster/region and say which:
  carnival (bodies overflowing, almost funny, saturated) or dread (alien, still, restrained palette).
- **Text is pixel art too.** All text sits on the 320x180 grid in our own pixel fonts, at their own size,
  never smooth, never scaled (decided 2026-10-10; Miles left the call to monster).

## Text and logo
- `art/fonts/grotesk.fnt`: the body font. Proportional, 7px caps, 2px descenders, 10px line,
  `info size=10`. `art/fonts/grotesk_digits.fnt`: chunky outlined digits for damage popups
  (0-9 + - ! ? . /); the dark outline is baked in and the white fill takes `font_color`.
- `art/fonts/grotesk_crit.fnt`: the same digits 2px taller (`info size=12`) for crits and stun hits.
- Use a font only at its own size, with `scaling_mode=0` in its tracked `.import`: Godot's stock
  import scales bitmap fonts fractionally to any requested `font_size` (the default 16 drew 1.6x).
  Bitmap fonts ignore `outline_size`, so outlines must be drawn into the glyphs.
- After editing a font's `.import`, delete its `.godot/imported/<name>.fnt-*` and import again:
  Godot can keep the first import's settings (the crit font stayed scaled until its cache was
  cleared). Atlases are `importer="skip"` (the font importer reads them itself).
- `art/ui/logo.png` (96x26): the title logo. The O is the Sucker Frog's eye, the Q's tail is its
  tongue. Sources: `tools/art/font.py` (glyphs as text, `--specimen` to judge them on a battle
  window) and `tools/art/logo.py` (`--preview` on the title scene).

## Pipeline (`tools/art/sculpt.py`)
1. Sculpt the form in 3D from spheres, ellipsoids, tapered cones and tori that blend like clay; carve
   mouths, sockets and wounds with subtraction. Front view, z toward the viewer.
2. Render: the raymarcher quantizes lighting onto the ramps, adds cast shadows, ambient occlusion,
   wet specular, depth-edge lines, coloured outlines and orphan-pixel cleanup.
3. Hand-paint details on top (eyes, teeth, veins, tears, drool, warts) at exact coordinates.
4. Judge it on the cave background at battle scale, never only zoomed in. Once it's wired in, look at
   it in the running scene: `godot --path . --script res://tools/art/capture.gd -- res://title.tscn
   out.png` saves exactly what the window shows.

## Battlers
- Canvas up to 104x118, bottom-centred; shown centred at (160, 63); the battle windows cover y >= 124.
- Files: `art/monsters/<id>/normal.png` + `telegraph.png` (required), `stunned.png` / `hurt.png`
  (optional). The battle draws them at scale 1 with the bottom-centre at (160, 122); a missing pose
  falls back to `normal`. Every pose uses the same canvas and ground line, so swapping never jumps.
- **Formations:** the battle stands enemies canvas by canvas, 4px apart, the group centred on x=160,
  every bottom row on y=122. Canvas widths plus gaps must fit in 320. Budgets: solo up to 104 wide
  (x 108-212), pairs up to 96 (x 62-258), trios up to 80 (x 36-284); mixed groups are fine (one 104
  + two 60s). A pack monster is drawn small from the start, not shrunk. Don't draw around the battle
  windows; the command window over a trio's left member is a battle-UI problem (`@fights`).
- Each monster gets a `normal` pose and a `telegraph` pose (the warning before its big move), and
  optionally `hurt`. Telegraphs must read in one glance: change the silhouette, not just a colour.
- **Packs:** identical clones in a row look cheap. Give pack members variants (`normal_2.png`,
  `normal_3.png`; a member takes the one for its formation slot, else `normal.png`), and keep a shared
  move's telegraph identical on purpose: a pack snapping into one pose reads as unison (Penny Leeches).
- Commit each sprite's `.import` with it: every `.import` is tracked, so UIDs match across checkouts.

## Battle backdrops
- `art/battle/<bg>.png`, 320x180 at 1x; a battle with `bg` other than `"cave"` loads it. The windows
  cover y >= 124 and enemies stand on y = 122, so that's the ground (or the waterline).
- Restrained like the cave: dark, dithered (ordered 4x4), low contrast, a vignette, the centre calm
  where the monster stands. At most one warm accent (the Mere's lantern). The monster carries the
  picture; the backdrop only says where you are.
- A monster that lives in a place can lean on its backdrop: Old Iron has no water of its own any more,
  just foam where it breaks the Mere's surface.
- Backdrops so far (`tools/art/<name>_bg.py`, each with `--preview`): `mere` (the Black Mere, night on
  the barge - Old Iron), `swallow` (the Long Swallow, inside the Ever-Sow's gullet, lit by candles
  applicants left in the ribs - Gorger packs), `tasting` (the Tasting hall: a one-point feast hall,
  bunting and sausages, tables down both sides, the gourmet's empty throne - the Ever-Sow).
- Make poses parameters of one sculpt (head/limb frames, a lift, named arm variants), not separate
  drawings - see `tools/art/host.py`. The design and the light stay consistent across poses.
- Show Miles 2-3 options as one labelled sheet before polishing one. Concepts and sheets go in
  `art/concepts/` (it has a `.gdignore`, so they never ship in the game).

## Lessons from finishing the Host
- **A face aimed at the floor under an overhead key is a hood.** Physically right, unreadable. Give the
  part that must read its own lighter ramp *with a story reason* (his head is drained by the sucker),
  then hand-paint just enough to say "human": dim eyes, teeth, a few hairs.
- **Hide, then reveal.** Normal hides the face; the telegraph reveals it horribly; the stunned pose
  reveals it humanly. The pose sequence tells the story.
- **Place painted details from the part's posed frame** (`Frame.xy`), never as screen offsets: when the
  head rotated, screen-placed scalp veins slid down into his eye.
- **Mouths: carve above the lip, and make the inside dark.** A carve through the jaw shows pink and
  reads as a stuck-out tongue (a cartoon laugh). A dark throat ramp keeps the mouth a hole and the
  focal accent the only saturated colour.
- **A ring seen edge-on is a hat band.** When a sucker or mouth turns away from you, make it short and
  fat, or hide it behind the head.
- **Bends must break the silhouette outward.** An elbow folded inward vanishes behind the body.
- **Eyes at 1x:** 1px = a glint, 2px sliver = rolled back, 3px white-pupil-white = looking at you.
