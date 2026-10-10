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
1. **Command phase.** The player picks Attack / Guard / Item / Run. Run only works when the caller
   allows it. With several enemies standing, Attack opens a target menu; cancelling backs out.
2. **Enemies decide.** Each enemy picks its move from its behaviour (`scripts/battle/enemy_ai.gd`)
   before anyone acts. An enemy never reacts to what the hero chose this round: everything it does
   can be read from what it did before.
3. **Everyone acts in turn order.** Priority moves (Guard, Run) go first. Then the higher AGI goes
   first. Ties go hero first, then enemies left to right. There's no random speed roll: order is
   readable.
4. **End of round.** States tick (Drained bleeds), and a stun that ate a turn this round wears off.

The battle ends when every enemy has fallen (won), the hero falls (lost), or he runs (fled).

## Damage
- **Attack-based skills** (`power`): ATK × state modifiers × power × a roll of 0.85-1.15, rounded,
  minus the target's DEF.
- **Flat skills** (`dmg: [min, max]`): a roll in that range, minus DEF.
- **Crit** (skills marked `crit`): 10% chance, ×1.5.
- **Stunned target:** ×2 after the crit, and the stun's line replaces the skill's own in the log.
  A crit on a stunned enemy is ×3.
- At least 1 damage. A **guarded** hit deals half, rounded up.
- **Mercy** (the tutorial): the hero can't drop below 1 HP.
- The log and popups show the full hit on an enemy, and the HP actually lost on the hero.
- Big hits (crits, hits on a stunned enemy) get the louder sound and the yellow popup.

## Guard, telegraphs and stuns
- **Telegraph:** the warning move before a big one. It gets its own pose (`telegraph.png`) and
  text, and the enemy holds the pose until its next move.
- **Guard:** priority, so it's up before anyone else acts. It lasts the round and covers every hit
  in it. A normal hit deals half. A `guard_blocks` move (the Host's Latch) is stopped entirely,
  and the attacker is stunned.
- **Stunned:** loses its next action. Until the end of the round in which it lost that action, it
  takes double damage and shows its `stunned` pose. A pattern ("cycle") enemy then starts its
  pattern over.

## States
| state | stacks | effect | ends |
|---|---|---|---|
| Drained | up to 3 | per stack: -10% ATK; end of round -3 HP and -1 MP | Salve cures it; ends with the battle |
| Stunned | 1 | skips its next action; takes ×2 damage | end of the round it lost; ends with the battle |

An enemy can say a state's lines its own way (`state_text`). The Host's stun says "For a moment,
the man's eyes clear."

## Hero and items
- **Wanderer** (placeholder name): HP 60, MP 10, ATK 10, DEF 0, AGI 10. Nothing spends MP yet. Hero
  skills come next, and they will make Drained's MP drain matter.
- **Salve** (2 per fight in the tutorial): heals 15 HP and cures Drained. It can only be used when
  it would help.

## Enemies
### The Host (`host`): the tutorial
A possessed man with the Sucker Frog on his back, its cord sunk into his skull (art and lore:
`docs/bestiary.md`). HP 80, DEF 0, AGI 6. Mercy is on.

Pattern, repeating: **Lash** (5-8) → **Coil** (telegraph: the frog rears, his head snaps up with the
jaw unhinged, "the sucker flexes on its brain, hungry") → **Latch** (4-6 and Drained +1).
- Guard the Latch and the sucker slaps off his raised arms: the Host is stunned and the man's eyes
  clear for a moment. The next hit lands on the frog's bare belly for double. Then the frog crawls
  back onto his skull and the pattern restarts at Lash.
- **The lesson:** read the coil, guard the latch, punish the stun.

Balance (`tools/smoke_test.gd`, seeds 1-100):

| play | wins | turns (min/avg/max) | HP left | notes |
|---|---|---|---|---|
| smart: guard after the coil | 100/100 | 6 / 8.2 / 9 | 44 / 46.9 / 50 | never Drained, no Salves |
| attack only | 100/100 | 8 / 8.9 / 10 | 1 / 4.3 / 13 | Drained ×2-3; mercy catches it in 25/100 |

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
  - `hero`: `{hp, mp, items, states}` carried in from outside, otherwise fresh.
- `result`: `{outcome: "won" | "lost" | "fled", hero: {hp, mp, items, states}, turns}`. States that
  end with the battle (Drained, Stunned) aren't carried out.
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
- `godot --headless --path . --script res://tools/smoke_test.gd -- smart` (or `attack`) plays one
  fight and prints every line.
  - `seed=N` replays a fight exactly.
  - `runs=N` prints a balance summary.
  - `troop=host,host` fights a group.
- The same seed gives the same log, so a refactor must reproduce the previous version's logs line
  for line. The battle-core split was checked that way on seeds 1-40 under both policies.
- Every enemy gets an autoplay of its telegraph, plus a smart-vs-careless balance line in this file.

## Open questions
- **Run** always succeeds. No fight allows it yet; decide odds and cost when the world needs it.
- **Three wide enemies:** the floating command window covers most of the left one. Fine for two;
  revisit with the first three-enemy fight (smaller monsters, or move the window).
- **Hero skills** that spend MP are the next step.
- **Big-hit digits:** crits and stun hits are yellow but the same size as other numbers, because
  bitmap fonts don't scale. Monster will draw a taller digits set.
