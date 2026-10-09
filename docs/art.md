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
4. Judge it on the cave background at battle scale, never only zoomed in.

## Battlers
- Canvas up to 104x118, bottom-centred; shown centred at (160, 63); the battle windows cover y >= 124.
- Each monster gets a `normal` pose and a `telegraph` pose (the warning before its big move), and
  optionally `hurt`. Telegraphs must read in one glance: change the silhouette, not just a colour.
- Show Miles 2-3 options as one labelled sheet before polishing one.
