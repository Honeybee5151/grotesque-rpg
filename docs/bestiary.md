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
flared (telegraph), and next round they all latch at once, each its own hit; Drained lands once per
drink round (once per leech was too harsh for a first fight). Guard only halves it. Kill one during the sway and the chorus is a voice short. A Crush kills a leech outright
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

## Old Iron (`old_iron`) - the whale that hunts the hunters

Miles' brief: a whale that hunts humans with a harpoon, out of revenge. Picked from three concepts
(`art/concepts/whale_options.png`, source `tools/art/whale_concepts.py`).

**Look.** A vast sperm whale spyhopping out of black water - its head stood straight up to watch
you - prune-wrinkled, scarred and barnacled, its hide bristling with the rusted harpoons of every
whaler who ever struck it, rotten ropes trailing. A narrow toothed jaw hangs open down its front.
Its old eye is amber, the colour of lamplight: lamps burn whale oil. That eye is the focal accent.

**Lore.** It never died. It kept every harpoon ever thrown at it, and now it gives them back.
Hollowell's lanterns burn whale oil rendered at Tallowmouth, a dying whaling hamlet on the Mere's
shore: the fen's one warm colour is bought with its blood, so it hunts whoever carries a lamp.

**Hook: it gives them back** (as `@fights` built it: Wrench opens a Wounded stack on itself,
+25% damage taken each, up to 5; a guarded throw glances off and it overbalances, stunned; after five
harpoons it gapes and bites). It wrenches a harpoon out of its own hide and
clamps it in its jaw (telegraph), then flings it: a heavy hit, and the harpoon stays in the hero,
bleeding him the way it has bled for years. Guard: it glances off. Every harpoon it gives back
leaves a wound open in its hide, so the more it throws, the softer it gets: bait the throws, brace,
strike the wounds. Its hide holds only so many.

**Flavour.** Dread.

**Sprites.** `art/monsters/old_iron/`, 104x118: `normal` (spyhopping, watching), `telegraph` (it
rears back, a harpoon pulled from its own hide clamped across its jaw, the wound bleeding), `hurt`
(it rolls away, eye shut), `stunned` (overbalanced after a guarded throw: tipped over, wallowing,
eye rolled), and for the empty-hide phase `spent` (resting: no harpoons left, a wound where each
was) and `gape` (the bite telegraph: jaw swung wide, the mouth carved open and pink). It stands in its own patch of water. Source: `tools/art/old_iron.py`;
sheet: `art/concepts/old_iron_poses.png`.

**Placement** (`@world`). The Black Mere, the open black water between the Sallow Fen and Plenty,
crossed by night on the ferrywoman's barge: the Mere's boss, after the Mouther and the leeches. She
tells the hero to put Odo's lantern out - douse it and cross blind, or keep it lit and Old Iron
comes. The battle is on the barge's deck at night: black water, fog, the barge's lantern swinging.

## The Gorger (`gorger`) - Plenty's common pack monster

**Look.** A walking stomach on stubby legs: a tiny head in a paper festival crown, cheeks stuffed,
a napkin tucked in its collar spattered with sauce, and a second mouth grinning and chewing right
across its belly - mouths budding where mouths shouldn't. Pink and greasy, almost funny. Focal
accent: the belly-mouth.

**Lore.** It ate the holy pig's meat and grew back fatter every time; now it can't stop.

**Hook: it eats until it can't move.** Its telegraph is a feast: it shovels food into both mouths
and heals. Then it puts itself out - bloated, it loses its next action and takes double, so a Crush
that turn hits for four. A telegraph that is an **opening**, not a threat. In a pack they feast on
their own clocks, not together: most rounds one is bloated, so the lesson is picking the open one.
The feast heals less than the bloated punish deals (`@fights`).

**Flavour.** Carnival.

**Sprites.** `art/monsters/gorger/`, 72x80: `normal`, `normal_2`, `normal_3` (three individuals:
fork and drumstick, a pie hugged to its belly, a string of sausages), `telegraph` (the feast: arms up
shovelling, cheeks bulging, the belly-mouth gaping on food), `stunned` (bloated: swollen rounder,
tipped back, legs splayed, eyes rolled, napkin popped, a puff of steam), `hurt`. Source:
`tools/art/gorger.py`; sheet: `art/concepts/gorger_poses.png`.

## The Second Chin (`second_chin`) - a Plenty alderman

**Look.** A pear-shaped alderman in roast-red velvet, a gold chain of office and lace at his throat.
His own little face, frightened, under a powdered wig - and under it a double chin grown into a face
of its own, beady and sneering, that does the talking now. Focal accent: the chin's mouth.

**Lore.** He ate at the holy pig's table every feast day, and what grew back grew a mind of its own.
He hasn't finished a sentence in years; it finishes them for him.

**Hook: the critic.** It remembers what the hero did last round, and says so - "It eyes your raised
arms, bored." (telegraph: the knowing look). If he does the same thing again that round, it says
"Predictable." and counter-hits; if he changes his answer, it scowls and whiffs. Decided before he
picks and reading only last round, so it's fair and readable. Teaches **varying your answers**
(Attack and Crush count as different; `@fights`).

**Flavour.** Carnival.

**Sprites.** `art/monsters/second_chin/`, 88x118: `normal` (stiff, his face afraid, the chin
sneering), `telegraph` (the knowing look: the chin juts, eyes narrowed to slits, a smug lopsided
smirk; his little hand flies to his mouth), `hurt` (the chin grimaces, the body jiggles back).
Source: `tools/art/second_chin.py`; sheet: `art/concepts/second_chin_poses.png`.

## The Ever-Sow (`ever_sow`) - Plenty's holy pig, its boss

**Look.** A vast sow, three-quarter on, dressed like a shrine: candles and ribbons, a velvet cloth, a
gold ring through her snout, a butcher's cleaver left in her back. Her flanks are carved in clean
butcher's slabs down to raw meat, budding back. Focal accent: the raw red of the cuts.

**Lore.** Plenty is fed by her: carve what you like, it grows back by morning. Whatever ate of her
grows back too - which is why salt, and the Salt Guild, matter here.

**Hook: it grows back.** Her wounds knit (telegraph: she arches, snout up, new flesh swelling out of
the cuts like dough), and next round she regrows a great heal. Throw Salt on her while she knits and
the wound salts shut: the heal is lost and she's stunned. Salt any other time is a small sting, and
it's scarce (2-3 a fight, from the Salt Guild). Teaches **the right item at the right time**
(Salt becomes a thrown item; `"break": {"by": ["salt"]}`, `@fights`).

**Flavour.** Carnival.

**Sprites.** `art/monsters/ever_sow/`, 104x96: `normal` (serene, carved, budding), `telegraph`
(knitting), `stunned` (salted: the cuts crusted white, slumped onto her belly, eyes squeezed, a candle
down, salt spilled), `hurt`. Source: `tools/art/ever_sow.py`; sheet: `art/concepts/ever_sow_poses.png`.

## Plenty (region 2) - how it was planned

world's region 2: the mouth that **gorges**, carnival - bodies overflowing, almost funny, saturated
(roast reds, yolk yellows, pinks), lit warmer and fuller than the fen (`carnival_light`). The
regional idea: whatever ate the Ever-Sow's meat grows back, and **salt** stops it. Each monster
teaches a new answer: a telegraph that is an opening (the Gorger), varying your answers (the Second
Chin), the right item at the right time (the Ever-Sow). The concept sheet the set came from:
`art/concepts/plenty_options.png` (source `tools/art/plenty_concepts.py`). All three are built.
