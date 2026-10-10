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

## Sallow Fen (region 1) - concepts, not final

world's region 1: a mouth that **sucks**, dread, night and fog, lantern amber the only warm colour.
Every fen monster's big move is answered differently: the Host teaches **Guard**. Concepts on
`art/concepts/fen_options.png` (source `tools/art/fen_concepts.py`); hooks are proposals for
`@fights`, placements from `@world`.

- **The Mouther** (`mouther`, solo/pair). A peat-tanned bog body, pressed crooked by the bog, a
  rotted scarf slipped down off the mouth it once covered; its jaw hangs far too low and works with
  no sound. Lore: the fen kept its voice - what Hollowell thinks happened to the hero (it didn't).
  *Hook - the inhale:* it gapes and sucks in a long silent breath (telegraph), then drinks the breath
  out of the hero (MP). Crush it mid-inhale and it chokes (stun). Teaches **Crush** and spending MP
  before it's taken. Placement: the drowned boardwalk north of Hollowell ("Drowned men don't talk").
- **Penny Leeches** (`penny_leech`, pack of 3, 44x66 each). Fat glossy leeches rearing off a coil,
  round pink suckers, and the coins wished into Hollowell's well grown into their skin - why the water
  tastes of pennies. *Hook - the chorus:* they sway in unison (telegraph), then all latch at once
  (Drained each). Kill one in the sway round to break it. Teaches **thinning a pack**. Placement: the
  first ordinary fight, the black pool in the well cave or the fen shallows.
- **The Brood** (`brood`, region boss, 104x92). The spawn-mother under the well: a bloated dark toad
  with dead milky eyes, her back a heaped dome of black spawn with riders curled in the eggs, a pale
  sac of more under her chin. The Sucker Frog is one of hers. *Hook - the hatch:* her sac swells
  (telegraph), then spawnlings drop into the formation and climb onto the hero if left. Teaches
  **priority**. Placement: deep in the flooded caves under the well.
