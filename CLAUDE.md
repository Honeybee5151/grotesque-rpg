# Grotesque RPG

A turn-based pixel-art RPG in **Godot 4.4.1** (GDScript). A mute hero who talks only in gestures, in a
world of wonderfully grotesque monsters. **Miles** is the director: big creative calls are his.

## Layout
- `boot.tscn` -> `title.tscn` -> `main.tscn` (battle). Entry is `scripts/boot.gd` (mounts update packs).
- `scripts/` - `battle/` (the battle), `main.gd` (the tutorial fight), `data.gd` hero/items/enemies,
  `title.gd`, `updater.gd`, `boot.gd`, `sprite_factory.gd` (procedural cave background).
- `tools/` - `smoke_test.gd` (headless battle autoplay), `update_test.*` (updater end-to-end),
  `art/` (`sculpt.py` 3D-sculpt -> pixel-art renderer, `host_concepts.py`, `grid.py` coordinate viewer).
- `art/` - PNG assets (`art/monsters/<id>/`, `art/world/`, `art/concepts/`).
- `docs/` - design bibles: `art.md` (read before drawing anything), plus world/combat/bestiary docs as
  they're written. They are how the team remembers decisions - keep yours current.
- `team/` - `roles/*.md` (one per agent), `Start-Team.ps1` (opens the four agent terminals).

## Hard rules
- **Never edit `VERSION` or `.github/workflows/`** unless Miles explicitly says to release / change CI.
  A `VERSION` change on `main` publishes a public release that auto-updates every player.
- Never force-push, never rewrite `main`'s history, never delete other roles' branches or worktrees.
- 320x180 base resolution, integer scaling, nearest filtering. **All pixel art at 1x** - never scale a
  sprite up in-engine (mixed pixel sizes look cheap). Battlers are at most 104x118.
- Run the relevant checks before saying something works, and look at rendered art before showing it.
- Small, coherent commits with clear messages. Push your own branch as a backup.
- Team sessions run in **auto mode**: no permission prompts, and Claude Code's safety classifier blocks
  risky actions. If something is blocked, don't look for a way around it - say what you were trying
  to do and ask Miles. monster/world/fights are hard-blocked from pushing `main` and editing
  `VERSION` or CI (`team/settings/creative.json`); that work goes through `@misc`.

## Running things (Windows, from your checkout)
- `godot` is on PATH in team terminals (a shim for the Godot 4.4.1 console exe in `$env:GODOT`).
  - Import: `godot --headless --path . --import`
  - Battle autoplay: `godot --headless --path . --script res://tools/smoke_test.gd -- smart` (and `-- attack`)
  - Play: `godot --path .`
- All the merge checks in one go: `tools\check.ps1` (import, every script parses, boot to the title,
  both autoplays; `-Updater` adds the updater test). Exits 1 on any failure.
- Art: `python tools/art/host_concepts.py <outdir> a b c` (numpy + pillow);
  `python tools/art/grid.py in.png out.png x0 y0 x1 y1 scale` to read exact pixel coordinates.
- To show Miles an image, save it and open it: `Start-Process <path.png>`.

## The team: four Claude sessions, one per terminal
| name      | role                                                  | checkout     | branch         |
|-----------|-------------------------------------------------------|--------------|----------------|
| `monster` | monster designer and pixel artist                     | `..\monster` | `team/monster` |
| `world`   | world builder: maps, towns, NPCs, story, lore         | `..\world`   | `team/world`   |
| `fights`  | combat designer and battle programmer                 | `..\fights`  | `team/fights`  |
| `misc`    | integrator + everything else: tooling, UI, bugs, merges, releases | `..\main` | `main` |

- **Message each other** with cross-session messages: `@monster`, `@world`, `@fights`, `@misc`. Message
  when you change something another role builds on, or need something from them. Short and concrete.
- **Ownership** keeps merges painless - edit outside your area only in small, announced steps:
  - monster: `art/monsters/**`, `art/concepts/**`, `tools/art/**`, `docs/art.md`, `docs/bestiary.md`
  - world: `scenes/world/**`, `scripts/world/**`, `art/world/**`, `docs/world.md`, `docs/story.md`
  - fights: `scripts/main.gd`, `scripts/battle/**`, `scripts/data.gd`, `tools/smoke_test.gd`, `docs/combat.md`
  - misc: everything else (`project.godot`, title/menus, updater, `tools/` tests, CI, README, `team/`)
- **Shipping work**: commit on your branch, run `tools\check.ps1`, push, then message `@misc`
  "ready to merge: <summary>".
  misc merges into `main` after the checks pass and tells everyone. All checkouts share one repository,
  so pick up others' work any time with `git merge main` in your own checkout.
- Anything that changes the game's direction goes to Miles first.
