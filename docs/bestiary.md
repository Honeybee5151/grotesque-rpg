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
