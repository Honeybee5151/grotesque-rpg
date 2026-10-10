# Bestiary

One entry per monster: the look, two lines of lore, the behaviour hook the fight is built on, and
its flavour (carnival or dread - see `docs/art.md`). Sprites live in `art/monsters/<id>/`.

## The Host (`host`) - tutorial fight

**Look.** A man bent forward on his knuckles, head hanging so his opened crown faces you. The Sucker
Frog rides his back, and a fleshy pink cord runs from its mouth down into his skull. The cord is
the only saturated thing on him. His head is drained paler than the rest of him, and veins crawl
out from under the sucker. One arm is too long, the other buckles under him, and one leg drags.

**Lore.** The Sucker Frog can't go far on its own legs, so it borrows a man's: it opens the crown,
sinks its sucker into the brain and steers him by the cord. It is always looking for a better host.

**Hook: the cord.** Lash -> Coil -> Latch (`scripts/data.gd`).
- *Coil* (telegraph pose): the frog rears, the cord snaps taut and yanks his head up - face
  revealed, jaw unhinged - and flings his buckling arm out like a jerked marionette.
- *Latch*: the frog tears its sucker out of him and lunges for the hero's head - it wants a new host.
- *Guarded* (stunned pose): the sucker slips off and hangs slack, the frog slides off his back
  dazed, belly exposed, and for one turn the man looks up with clear eyes and reaches out to you.
  Stunned enemies take double damage: that's the moment to hit the frog.
- The tutorial's lesson in pictures: read the telegraph, guard, punish.

**Flavour.** Dread: grey, drained, still, one pink accent. The frog is the only hint of carnival.

**Sprites.** `art/monsters/host/` - `normal`, `telegraph`, `stunned`, `hurt` (all 104x118, same
ground line). Source: `tools/art/host.py` (concept C "The Hunched", picked by Miles 2026-10-10 from
`art/concepts/host_sheet.png`); pose sheet: `art/concepts/host_poses.png`.

## Penny Leeches (`penny_leech`) - the fen's first ordinary fight, a pack of three

**Look.** Fat, glossy black leeches rearing off a coiled tail, each with a round pink sucker for a
head and a ring of pale teeth inside it. Set into their skin are the coins Hollowell wished down its
well, copper catching the light: the focal accent.

**Lore.** For as long as anyone remembers, Hollowell dropped a penny down the well for a wish. The
leeches ate every one, and now the water tastes of them.

**Hook: the chorus.** Each leech nips on its own. Then all three rear up into the *same* pose, suckers
flared (telegraph), and next round they all latch at once, each its own hit plus Drained. Guard only
halves it. Kill one during the sway and the chorus is a voice short. A Crush kills a leech outright
(about 20 HP), so the lesson is **thinning a pack**, and Mend/Salve after. Numbers: `@fights`.

**Flavour.** Dread, with a sickly glint of copper.

**Sprites.** `art/monsters/penny_leech/`, all 50x76 on one ground line: `normal`, `normal_2`,
`normal_3` (three individuals; a pack member takes the variant for its slot), `telegraph` (identical
for all three: the unison is the warning), `hurt` (it contracts into a knot). Source:
`tools/art/penny_leech.py`; sheet: `art/concepts/penny_leech_poses.png`. Placement (`@world`): the
black pool in the well cave or the fen shallows, right after the Host.

## Sallow Fen (region 1) - concepts, not final

world's region 1: a mouth that **sucks**, dread, night and fog, lantern amber the only warm colour.
Every fen monster's big move is answered differently: the Host teaches **Guard**. Concepts on
`art/concepts/fen_options.png` (source `tools/art/fen_concepts.py`); hooks are proposals for
`@fights`, placements from `@world`. Built so far: Penny Leeches (above).

- **The Mouther** (`mouther`, solo/pair). A peat-tanned bog body, pressed crooked by the bog, a
  rotted scarf slipped down off the mouth it once covered; its jaw hangs far too low and works with
  no sound. Lore: the fen kept its voice - what Hollowell thinks happened to the hero (it didn't).
  *Hook - the inhale:* it gapes and sucks in a long silent breath (telegraph), then drinks the breath
  out of the hero (MP). Crush it mid-inhale and it chokes (stun). Teaches **Crush** and spending MP
  before it's taken. Placement: the drowned boardwalk north of Hollowell ("Drowned men don't talk").
- **The Brood** (`brood`, region boss, 104x92). The spawn-mother under the well: a bloated dark toad
  with dead milky eyes, her back a heaped dome of black spawn with riders curled in the eggs, a pale
  sac of more under her chin. The Sucker Frog is one of hers. *Hook - the hatch:* her sac swells
  (telegraph), then spawnlings drop into the formation and climb onto the hero if left. Teaches
  **priority**. Placement: deep in the flooded caves under the well.
