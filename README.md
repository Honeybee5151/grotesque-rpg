# Grotesque RPG

Godot 4.4.1 (scripts are exported compiled, so keep the engine version pinned — see *Updates*).
Open the folder in Godot and press F5: boot → title screen (**Play** / Quit) → the Hollowell prologue in the
overworld; the Host fight is part of it, and the prologue returns to the title at its end.

**Controls:** Arrows walk and move menus · Z / Enter / Space / click confirm, talk, look · X / Esc / right-click back · M mute

**The fight:** the Host (a man ridden by the Sucker Frog) cycles Lash → Coil → Latch. Guard on the turn
*after* it coils and the Latch slips off and stuns it, and stunned enemies take double damage. Miss it
and you get Drained (stacking HP/MP drain, weaker attacks) — cure it with a Salve. The hero can't die
in the tutorial (`"mercy": true` on the Host in `scripts/data.gd`). The rules: `docs/combat.md`.

## Putting it on GitHub (once)
1. On github.com create a **public** repo (e.g. `grotesque-rpg`), empty — no README/licence. It has to be
   public because the in-game updater reads releases without logging in.
2. In this folder:
   ```
   git remote add origin https://github.com/<you>/grotesque-rpg.git
   git push -u origin main
   ```

## Releasing a version
Edit the `VERSION` file (e.g. `0.1.0` -> `0.2.0`) and push to `main`. The **Release** workflow
(`.github/workflows/release.yml`) creates the `v0.2.0` tag itself, stamps the version and repo name into
`release.cfg`, exports Windows / Linux (and macOS, best effort) builds, and publishes a GitHub Release with
`GrotesqueRPG-windows.zip`, `GrotesqueRPG-linux.zip`, `GrotesqueRPG-macos.zip` and **`game.pck`**.
Pushing other changes to `main` does nothing; only a changed `VERSION` ships. Pushing a `v*` tag by hand works too.
Players download the zip once; after that the game updates itself.

## Updates
- On the title screen the game asks GitHub for the latest release. If it's newer it downloads `game.pck`
  (checked against its SHA-256), stages it in the user folder and offers **Restart to update**.
  Otherwise the update is mounted automatically on the next launch (`scripts/boot.gd`).
- `game.pck` carries all scripts, scenes and data, so content/logic updates never need a new download.
  A **new Godot version** can't be delivered this way — that needs players to grab a fresh zip. If you
  change engine version, change it in `release.yml` too.
- Inside the editor the updater is off. `tools/update_test.sh` tests the whole pipeline against a fake
  local release (`GODOT=/path/to/godot tools/update_test.sh`; on Windows `tools\check.ps1 -Updater`
  runs it through Git Bash).

## The agent team (Windows)
Four Claude Code sessions (Opus 5.5, max effort) build the game in parallel, one PowerShell window
each, each in its own git worktree: **monster** (monsters and pixel art), **world** (maps, towns, NPCs,
story), **fights** (combat), **misc** (merges, tooling, releases, everything else). Their shared
rules are in `CLAUDE.md`, their briefs in `team/roles/`. They message each other by name.

Start them with `team\Start-Team.cmd` (first run installs/sets up what's missing), or from PowerShell:
`team\Start-Team.ps1 [-Continue] [-Layout Windows|Grid|Tabs] [-Only monster,fights] [-Bypass]`.
Sessions run in auto mode: no permission prompts, with Claude Code's safety classifier blocking risky
actions; only `misc` can push `main` or touch `VERSION`/CI. `-Bypass` switches every check off.
The launcher updates itself from GitHub before it starts.

## Where things live
- `scripts/data.gd` — hero, items, enemies (add monsters here)
- `scenes/world/world.tscn`, `scripts/world/` — the overworld: `world.gd` (story flags, text box, battles),
  maps in `scripts/world/maps/`, dev tools in `scripts/world/dev/` (`drive.gd`, `world_test.gd`)
- `scripts/battle/` — the battle: rules and flow (`battle.gd`), what it shows and plays (`battle_view.gd`),
  combatants, enemy behaviours, synthesized sound; `scripts/main.gd` runs the tutorial fight
- `scripts/title.gd`, `scripts/boot.gd`, `scripts/updater.gd` — title screen, update mounting, update download
- `scripts/sprite_factory.gd` — the procedural cave background
- `art/` — monster sprites (`art/monsters/<id>/`), pixel fonts, the logo; `theme.tres` makes the Grotesk
  pixel font the default
- `docs/` — design bibles: `art.md`, `bestiary.md`, `combat.md`, `world.md`, `story.md`
- `release.cfg` — version + repo, stamped by CI (don't hand-edit for releases; tag instead)
- `tools/` — `check.ps1` (every check in one go), `smoke_test.gd` (headless battle autoplays),
  updater tests, `art/` (the art tools)
