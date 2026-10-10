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
- Each monster gets a `normal` pose and a `telegraph` pose (the warning before its big move), and
  optionally `hurt`. Telegraphs must read in one glance: change the silhouette, not just a colour.
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
