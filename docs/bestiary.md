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

## The Mouther (`mouther`) - the drowned boardwalk north of Hollowell

**Look.** A bog body, peat-tanned to leather and pressed crooked by the bog: knock-kneed, one
shoulder hiked, the skull flattened on one side, in a rotted coat. Its jaw hangs far below where a
jaw should be and works with no sound. A rotted scarf has slipped down off the mouth it once covered.
Focal accent: the wet pink inside of that mouth.

**Lore.** Hollowell says the fen keeps what it's owed: it kept this one's voice, and they think it
kept the hero's. (It didn't - but a drowned man who lost his voice the same way is a hint for later.)
Moth: "Drowned men don't talk. Everybody knows that."

**Hook: the inhale.** It sucks in a long silent breath (telegraph), and next round drinks the breath
out of the hero: it takes his MP and heals by that much, or drinks HP when he has none. Guard doesn't
help - it isn't damage. **Crush it mid-inhale** and it chokes on its own breath: the drink is
cancelled and it loses the action. Teaches **Crush**, and spending MP before it's taken. Rule:
`"break": {"by": ["crush"]}` (`@fights`).

**Flavour.** Dread.

**Sprites.** `art/monsters/mouther/`, all 96x118 on one ground line: `normal` (crooked, slack, the
jaw working), `telegraph` (head tipped back, jaw dropped further, arms spread, the air and its own
scarf streaming into its mouth), `stunned` (choking: knees buckled, both hands at its throat, fen
water dribbling from its jaw), `hurt` (a flinch). Source: `tools/art/mouther.py`; sheet:
`art/concepts/mouther_poses.png`.

## The Brood (`brood`) and spawnlings (`spawnling`) - the Sallow Fen's boss

**Look.** The spawn-mother under Hollowell's well: a bloated dark toad squatting in black water,
dead milky eyes half-lidded on top of her head, her back a heaped dome of glossy black spawn with
riders curled in the eggs and jelly hanging off it. Under her chin a pale sac of more; in the seam
of her mouth a toothed pink sucker. Focal accent: the sac. Her spawnlings are hatched riders, baby
Sucker Frogs: glossy black tadpole-frogs on budding pale legs, one big embryo eye, a tiny pink sucker.

**Lore.** The black spawn in Odo's bucket was hers, and the Sucker Frog that rode him is one of her
brood. The flooded caves under the well are her nursery.

**Hook: the hatch.** Her sac swells (telegraph) and next round a spawnling drops into the fight; a
spawnling still alive a round later climbs onto the hero (Drained) and leaves the formation without
dying. Kill the spawnling or hit the mother: a clean **priority** call. One spawnling per swell
(`@fights`).

**Flavour.** Dread.

**Sprites.** `art/monsters/brood/` (104x96): `normal` (squatting, the sac slack), `telegraph` (she
rears and the sac swells into a stretched pale balloon, eggs showing through), `hurt` (eyes squeezed
shut, she sinks). `art/monsters/spawnling/` (40x44): `normal` (sitting on its curled tail),
`telegraph` (coiled to leap, the sucker flared - the climb), `hurt` (squashed flat). A boss and two
spawnlings fit 320 easily (192px). Source: `tools/art/brood.py`; sheet: `art/concepts/brood_poses.png`.

## Sallow Fen (region 1) - how it was planned

world's region 1: a mouth that **sucks**, dread, night and fog, lantern amber the only warm colour.
Every fen monster's big move is answered differently: the Host teaches **Guard**, the Mouther
**Crush**, the Penny Leeches **thinning a pack**, the Brood **priority**. The concept sheet the set
came from: `art/concepts/fen_options.png` (source `tools/art/fen_concepts.py`). All four are built.
