# Combat bible (v0)

How battles work. This file is the source of truth for the rules. The numbers themselves live in
`scripts/data.gd`, and the code in `scripts/battle/`. Change a rule here first, then in code, then
prove it with `tools/smoke_test.gd`.

## The idea
- Classic front-view, turn-based combat in the RPG Maker tradition, written from scratch. A mute hero
  against 1-3 enemies.
- **Every enemy teaches or tests one idea, and its big move is telegraphed a round ahead.** Reading
  the telegraph and answering it is the core skill. Answering it pays off in HP and in speed: the
  answered enemy is stunned and takes double damage.
- The hero is mute. His actions and the battle text lean on gestures ("He nods, once"), and his
  speech bubble only ever shows "...".

## A round
1. **Command phase.** The player picks Attack / Skill / Guard / Item / Run. Skill lists the hero's
   skills with their MP cost. Run only works when the caller allows it. With several enemies
   standing, an attack opens a target menu. Cancelling backs out of any submenu.
2. **Enemies decide.** Each enemy picks its move from its behaviour (`scripts/battle/enemy_ai.gd`)
   before anyone acts. An enemy never reacts to what the hero chose this round: everything it does
   can be read from what it did before.
3. **Everyone acts in turn order.** Priority moves (Guard, Run) go first. Then the higher AGI goes
   first. Ties go hero first, then enemies left to right. There's no random speed roll: order is
   readable.
4. **End of round.** States tick (Drained bleeds), and a stun that ate a turn this round wears off.

The battle ends when every enemy has fallen (won), the hero falls (lost), or he runs (fled).

## Damage
- **Attack-based skills** (`power`): ATK × state modifiers × power × a roll of 0.85-1.15 (a skill
  can set its own `variance`; Crush has none), rounded, minus the target's DEF.
- **Flat skills** (`dmg: [min, max]`): a roll in that range, minus DEF.
- **Crit** (skills marked `crit`): 10% chance, ×1.5.
- **Stunned target:** ×2 after the crit, and the stun's line replaces the skill's own in the log.
  A crit on a stunned enemy is ×3.
- At least 1 damage. A **guarded** hit deals half, rounded up.
- **Mercy** (the tutorial): the hero can't drop below 1 HP.
- The log and popups show the full hit on an enemy, and the HP actually lost on the hero.
- Big hits (crits, hits on a stunned enemy) get the louder sound and taller yellow digits.

## Guard, telegraphs and stuns
- **Telegraph:** the warning move before a big one. It gets its own pose (`telegraph.png`) and
  text, and the enemy holds the pose until its next move.
- **Guard:** priority, so it's up before anyone else acts. It lasts the round and covers every hit
  in it. A normal hit deals half. A `guard_blocks` move (the Host's Latch) is stopped entirely,
  and the attacker is stunned.
- **Stunned:** loses its next action. Until the end of the round in which it lost that action, it
  takes double damage and shows its `stunned` pose. A pattern ("cycle") enemy then starts its
  pattern over.

## Packs
- Several enemies with the same "cycle" pattern stay in step, so a pack telegraphs together.
- **Chorus** moves (`chorus`): when several pack members use the move in the same round, its lines
  are said once and its cues (pose, flash) move them all together. When only one is left, its
  `lines_alone` are used instead.
- `states_once`: the move's states land once a round, from the first hit, however many bite. A
  pack drains you a stack per round rather than a stack per member.
- Art: the n-th member with the same sprite takes `<pose>_<n>.png` when there is one (`normal_2`,
  `normal_3`), so a pack isn't three clones. A shared `telegraph.png` makes the unison the warning.

## States
| state | stacks | effect | ends |
|---|---|---|---|
| Drained | up to 3 | per stack: -10% ATK; end of round -3 HP and -1 MP | Salve cures it; ends with the battle |
| Stunned | 1 | skips its next action; takes ×2 damage | end of the round it lost; ends with the battle |

An enemy can say a state's lines its own way (`state_text`). The Host's stun says "For a moment,
the man's eyes clear."

## Hero, skills and items
- **Wanderer** (placeholder name): HP 60, MP 10, ATK 10, DEF 0, AGI 10.
- **Skills** are things he does, not words he says: he has no voice. MP is paid when the skill
  goes off. If Drained has eaten it by then, "he tries, but he's spent."

| skill | MP | effect | gesture |
|---|---|---|---|
| **Crush** | 4 | ×2 damage. A sure blow: no damage roll and no crit. On a stunned enemy that's ×4: the punish for a read telegraph. | "Wanderer throws his whole weight into it!" |
| **Mend** | 3 | heals 16 HP | "Wanderer presses a hand to his wounds." |

- Ten MP is two Crushes, or a Crush and two Mends. Drained takes 1 MP per stack every round, so a
  missed telegraph costs skills as well as HP.
- A caller can hand the hero a different skill list (`context.hero.skills`). The prologue (and the
  standalone tutorial) give him only Crush; Mend comes later in the story.
- **Salve** (2 per fight in the tutorial): heals 15 HP and cures Drained. It can only be used when
  it would help.

## Enemies
### The Host (`host`): the tutorial
A possessed man with the Sucker Frog on his back, its cord sunk into his skull (art and lore:
`docs/bestiary.md`). In world's prologue, he's Odo. HP 58, DEF 0, AGI 6. Mercy is on.

Pattern, repeating: **Lash** (5-8) → **Coil** (telegraph: the frog rears, his head snaps up with the
jaw unhinged, "the sucker flexes on its brain, hungry") → **Latch** (4-6 and Drained +1).
- Guard the Latch and the sucker slaps off his raised arms: the Host is stunned and the man's eyes
  clear for a moment. The next hit lands on the frog's bare belly for double. Then the frog crawls
  back onto his skull and the pattern restarts at Lash.
- **Freed** (agreed with world): kill the Host while it's stunned, the sucker torn out of his skull,
  and the man lives. The death lines become "The frog peels away, spent. The man falls." / "He's
  still breathing." and the result carries `flags.freed`. Any other kill: "He was already gone."
  In the story, a freed Odo lives but is mute (the frog ate his words).
- **The lesson:** read the coil, guard the latch, Crush the stun, and you save him.
- **Why 58 HP:** two attacks (at least 9 each) plus a Crush on the stun (exactly 40) always come to
  58 or more. So reading the first coil and Crushing the stun always frees him, in round 4. A
  player who misses the first read gets a second cycle: the Host survives the extra attacks, and a
  guarded second latch plus a Crush still frees him. At 80 HP, the Crush on the first stun left
  him at ~17, and the next plain hit killed him outside a stun: the player who did it right lost
  him (only 27/100 freed).

Balance (`tools/smoke_test.gd`, seeds 1-100; every policy wins, the tutorial can't kill you):

| play (autoplay policy) | turns (min/avg/max) | HP left | freed | notes |
|---|---|---|---|---|
| reads the first coil, Crushes the stun (`skills`, `save`) | 4 / 4 / 4 | 52-55 | 100/100 | never Drained |
| misses the first read, catches the second (`learner`) | 7 / 7 / 7 | 34-54 | 100/100 | Drained ×1, uses a Salve |
| guards every latch, never Crushes (`smart`) | 4 / 5.9 / 8 | 44-55 | 7/100 | never Drained |
| Crushes early, never guards (`spam`) | 4 / 4.1 / 5 | 32-48 | 0/100 | Drained ×1 |
| attack only (`attack`) | 5 / 6.2 / 7 | 18-38 | 0/100 | Drained ×1-2; mercy never needed |

Guarding is what saves him; Crush is the tool that does it. Spending Crush anywhere else is fast but
gives him up.

### Penny Leeches (`penny_leech`): the fen's first ordinary fight, a pack of three
Black leeches with Hollowell's wished-away pennies set in their skin (lore: `docs/bestiary.md`). HP
20, DEF 0, AGI 8 (the hero acts first). No mercy.

Pattern, in step: **Nip** (1-3) → **Sway** (telegraph, chorus: "The leeches rear up as one, suckers
wide.") → **Drink** (chorus: "They drop onto Wanderer together!", each bites for 2-4, and Drained +1
once a round).
- Guard only halves the bites; Drained still lands. The answer is thinning the pack. A Crush
  (exactly 20) kills a leech outright, an Attack (at most 18) never does, and the hero acts first.
  So Crush one in round 1 and another during the sway, and only one is left to drink.
- Death: "The leech A goes limp, spits out a penny."
- **The lesson:** not every telegraph is answered by Guard. Thin the pack before the chorus lands.

Balance (seeds 1-100, full HP, both Salves, Crush and Mend):

| play (autoplay policy) | wins | turns (min/avg/max) | HP left | notes |
|---|---|---|---|---|
| focus the weakest, Crush when it kills (`thin`) | 100/100 | 4 / 4.6 / 5 | 41-53 | Drained ×1 |
| attack only (`attack`) | 100/100 | 6 / 7.8 / 9 | 8-38 (avg 20) | Drained ×1-2 |
| guard the drink, the tutorial's habit (`smart`) | 99/100 | 10 / 13.7 / 16 | 0-52 (avg 35) | uses both Salves |

The first tuning (each bite drained, bites 2-4) killed 38/100 of the attack-only and guard-habit
players. A first ordinary fight should hurt the wrong answer, not end the game over it.

## Starting a battle
Agreed with world. The battle is a CanvasLayer (layer 10) that draws over the caller and keeps
running while the caller is paused or disabled.
```gdscript
var battle = preload("res://scripts/battle/battle.gd").new()
add_child(battle)
var result: Dictionary = await battle.run(["host"], context)
battle.queue_free()
```
- `context`, all optional:
  - `intro`: lines replacing the first enemy's own opening.
  - `bg`: backdrop, default `"cave"`.
  - `can_run`: default false.
  - `mercy`: default on if an enemy's data asks for it.
  - `hero`: `{hp, mp, items, states, skills}` carried in from outside, otherwise fresh.
- `result`: `{outcome: "won" | "lost" | "fled", hero: {hp, mp, items, states}, turns, flags}`.
  States that end with the battle (Drained, Stunned) aren't carried out. `flags` holds story flags
  the fight raised (an enemy's `death_when`), e.g. `{"freed": true}`.
- `scripts/main.gd` is the standalone tutorial the title screen opens. It runs the same call in a loop.

## Enemy art
`art/monsters/<sprite>/normal.png` and `telegraph.png`, plus optional `stunned.png` and `hurt.png`.
All are at 1x on one canvas of up to 104×118, standing on its bottom row, and drawn with the
bottom-centre on the ground line y=122. A formation stands canvas by canvas, 4px apart, centred as a
group on x=160; it has to fit in 320px. Monster's budgets: solo 104 wide, pairs 96, trios 80 (also
in `docs/art.md`). A missing pose falls back to `normal`. Missing art shows as a magenta square.
Hurt flashes for 0.3s on a hit.

## Battle text
Every line lives in `data.gd` and fits the log window: 214px of the Grotesk pixel font (about 42
characters). `say()` measures each line and warns when one doesn't fit; the widest today is 180px.
- A line can carry cues: a sound, a pose, a flash, a shake, or the hero's "..." bubble.
- Names read mid-sentence ("the Host"). `{User}`-style placeholders capitalise the first letter.
- The format is documented at the top of `data.gd`.

## Testing
- `godot --headless --path . --script res://tools/smoke_test.gd -- smart` plays one fight and prints
  every line. Policies: `smart`, `skills`, `learner`, `save`, `thin`, `spam`, `attack` (what each
  does is at the top of the file). The summary counts story flags too ("freed in N/100").
  - `seed=N` replays a fight exactly.
  - `runs=N` prints a balance summary.
  - `troop=host,host` fights a group.
- The same seed gives the same log, so a refactor must reproduce the previous version's logs line
  for line. The battle-core split was checked that way on seeds 1-40 under both policies.
- Every enemy gets an autoplay of its telegraph, plus a smart-vs-careless balance line in this file.

## Open questions
- **Run** always succeeds. No fight allows it yet; decide odds and cost when the world needs it.
- **Menus** hug the left edge (from x=4, as wide as their text) and grow upward from just above the
  log. They're clear of a pair. A trio (80 wide each) loses its outer 14px to the main menu, and a bit
  more to the wider skill and target submenus. Check that with the first three-enemy fight.
- **More skills:** one per region, found like the new gestures in `docs/world.md`? To decide with
  world.
- **HP between fights:** the tutorial leaves the hero with 18-55 HP, and nothing heals him after it.
  The leech numbers above assume full HP. World should put a rest (or Moth's kettle) between the
  Host and the leeches.
