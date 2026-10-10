# World bible (v0)

Owner: `world`. Story and plot spine live in `docs/story.md`. Approved by Miles 2026-10-10 ("you decide").

## The core idea: a world of mouths
Every region is a mouth gone wrong: one that **sucks**, one that **gorges**, one **sewn shut**, one that
**never shuts up**. The hero is the one person in it who can't use his. The grotesque is oral and
anatomical (see `docs/art.md`): suckers, gullets, sewn lips, walls that talk.

Regions alternate flavour so the journey breathes:

| # | Region | Flavour | The mouth | How silence reads there | They call him |
|---|--------|---------|-----------|-------------------------|---------------|
| 1 | **Hollowell, in the Sallow Fen** (start) | dread | sucks | bad luck: a drowned man the fen sent back | the drowned man |
| 2 | **Plenty** | carnival | gorges | a verdict: critics and saints don't eat | the Critic |
| 3 | **The Hush** | dread | sewn shut | holiness, and consent | Brother Hush |
| 4 | **Clamour** | carnival | never shuts up | menace: the scariest thing in a loud city | the Silent Man |

## The hero
- Mute. Nobody knows his name, so every region gives him one (table above). In battle he is still
  `Data.HERO.name` ("Wanderer", a placeholder owned by `@fights`).
- Look: gaunt young man, fen-soaked dark coat, hair plastered flat, a **rust-red scarf wound over his
  mouth** - his one warm accent in cold places. Running rumour: there's no mouth under it at all.
- Why he's mute stays a mystery in play. Every region has a theory (the fen kept his voice; it's a vow;
  he's a spy; he's simple; he's listening to God). The truth exists - see `docs/story.md`.

## Talking with gestures
When someone waits for an answer, a small menu opens beside the text box:

**Nod - Shake - Shrug - Point - Show - Say nothing**

- **Point** opens the things worth pointing at in that moment (a person, the well, himself).
  **Show** opens his items. **Say nothing** is always there - silence is an answer.
- The hero's sprite acts it out, then the NPC **puts words in his mouth**: "So you're lost." Never
  "you nodded".
- **Misreads are by character, not random.** The hopeful hear yes. The guilty hear an accusation.
  Bullies hear fear. Some monsters read silence as menace, wisdom or consent (the Hush runs on this).
- **NPCs override him.** A chatterbox decides for him ("That was a yes. I've decided."). That is
  comedy, and later it is horror.
- **New gestures are found like items**, one or so per region, each opening new replies: Bow, Beckon,
  Mime (eat / sleep / dead), Cover ears, Take a hand, and a rude one learned from a kid.
- Writing rules: every question answers every gesture on offer (a per-character default is fine);
  keep lines short (the text box shows 3 lines of about 52 characters); a reaction is better than an
  explanation.

## Regions

### 1. Hollowell, in the Sallow Fen (dread) - the start
Stilt-houses on a peat island around one deep stone well. Black water on every side, fog, reeds.
Night palette: the battle cave's indigo and violet, peat browns, reed grey-greens; **lantern amber is
the only warm colour**. The well drops into flooded caves where things breed in the dark water.
- People: few, damp, superstitious, quiet themselves. They pulled the hero out of the fen at dusk
  with no voice, and they say the fen kept it ("the fen keeps what it's owed").
- **Odo**, the well-keeper: a chatterbox who talks enough for both of them, a widower, warm and scared.
- **Moth**, his daughter (about ten): blunt, pale, follows his lamp everywhere - hence the name.
- What lives here: the **Sucker Frog** and other riders that come up out of the water and wear people;
  leeches; bog bodies that mouth words with no sound.
- The Host lands because the player knows the man: Odo teaches the hero rope signals, goes down the
  well, and comes back as the Host (`docs/story.md`, Prologue).

### 2. Plenty (carnival)
A fair town fed by the **Ever-Sow**, a holy pig that regrows whatever is carved off it. Everyone eats,
everyone grows: chins with opinions, a butcher-priest, aldermen carried on litters, mouths budding where
mouths shouldn't. Saturated pinks, yolk yellows, roast reds. His silence after a bite is a critic's
verdict and the cooks panic; refusing food is a scandal; some think he's a fasting saint.
Seeds for `@monster`: gorgers, a second chin that talks back, the Ever-Sow itself.

### 3. The Hush (dread)
A pale abbey and its wood, where a vow of silence outlived its monks and something moved into the quiet.
Bone white, ash grey, one cold blue. The last brothers think he keeps the Vow perfectly - a living
saint. The things in the wood take **silence as consent**: if he doesn't shake his head, it's a yes.
Seeds: sewn-mouthed monks whose bellies whisper; trees grown full of ears; the tall pale thing that only
waits for you not to say no.

### 4. Clamour (carnival)
A city where everyone talks at once, walls and signs included; gossip grows on people like mould and
the market sells words by weight. A man who says nothing is the most frightening thing they have ever
seen: they pay him to leave rooms, and children dare each other to make him speak. Loud, crowded,
saturated. Seeds: the Gossip (a mould made of whispers), wall-mouths, the Herald (see story).

## Building it (tech)
- Godot 4.4.1, 320x180, 16x16 tiles on `TileMapLayer`, nearest filtering, everything at 1x, every
  position on whole pixels. Art in `art/world/`, drawn by `art/world/src/*.py` (numpy + pillow).
- `scenes/world/world.tscn` is the root that stays loaded: it owns story flags, the hero's carried
  battle state, the text box, transitions, and swaps maps in and out (`scripts/world/maps/*.gd`).
- Maps are ASCII grids turned into `TileMapLayer` cells; characters step one tile at a time.
- **Battle hand-off** (agreed with `@fights`):
  ```gdscript
  var battle = preload("res://scripts/battle/battle.gd").new()
  add_child(battle)        # own CanvasLayer 10, process_mode ALWAYS
  var result: Dictionary = await battle.run(["host"], context)
  battle.queue_free()
  ```
  `context` (all optional): `intro: Array[String]` (lines of 44 characters or fewer, replacing the
  default opening), `bg` (backdrop id, default `"cave"`), `can_run` (default false), `mercy` (default
  from enemy data), `hero: {hp, mp, items: {id: count}, states: {id: stacks}}` (missing = full HP/MP,
  starting items). `result`: `{outcome: "won"|"lost"|"fled", hero: {...same shape}, turns: int}`.
  The world disables itself under the battle and resumes when `run()` returns.
