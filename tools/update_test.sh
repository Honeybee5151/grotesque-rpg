#!/usr/bin/env bash
# End-to-end test of the in-game updater.
#   GODOT=/path/to/godot tools/update_test.sh          against a fake local release
#   GODOT=/path/to/godot tools/update_test.sh --real   against the real latest GitHub release
# (Windows: tools\check.ps1 -Updater, or this from Git Bash.) Exits 1 if any step doesn't end the way
# it should. Runs in a copy of the project named "Grotesque RPG (update test)", so it never touches
# the user folder of an installed game (same name = same folder, and its staged update).
set -euo pipefail
GODOT="${GODOT:-godot}"
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
CLIENT="$WORK/client"
PORT=8765
SERVER_PID=""
FAILS=0
trap 'kill $SERVER_PID 2>/dev/null || true; rm -rf "$WORK"' EXIT
copy_project() { mkdir -p "$1"; (cd "$PROJ" && tar --exclude=./build --exclude=./.git -cf - .) | (cd "$1" && tar -xf -); }
run() { GRP_FORCE_UPDATES=1 GRP_TEST_API="${API:-}" "$GODOT" --headless --path "$CLIENT" --script res://tools/update_test.gd -- "$@" 2>&1 | grep -vE "^Godot Engine|ObjectDB|at: cleanup|leaked"; }
# expect <text the output must contain> <update_test.gd args...>
expect() {
  local want="$1"; shift
  local out; out="$(run "$@" || true)"
  printf '%s\n' "$out"
  if grep -qF -- "$want" <<<"$out" && ! grep -q "SCRIPT ERROR" <<<"$out"; then
    echo "  ok"
  else
    echo "  FAILED: expected \"$want\" and no script errors"; FAILS=$((FAILS + 1))
  fi
}
finish() {
  run clean >/dev/null
  if [ "$FAILS" -gt 0 ]; then echo "== updater: $FAILS check(s) FAILED"; exit 1; fi
  echo "== updater: all checks passed"; exit 0
}

copy_project "$CLIENT"
sed -i 's/^config\/name=.*/config\/name="Grotesque RPG (update test)"/' "$CLIENT/project.godot"
"$GODOT" --headless --path "$CLIENT" --import >/dev/null 2>&1 || true
run clean >/dev/null

if [ "${1:-}" = "--real" ]; then
  REPO="$(git -C "$PROJ" remote get-url origin | sed -E 's#^(git@github\.com:|https://github\.com/)##; s#\.git$##')"
  API="https://api.github.com/repos/$REPO/releases/latest"
  TAG="$(curl -sf "$API" | grep -o '"tag_name": *"[^"]*"' | head -1 | sed -E 's/.*"v?([^"]*)"$/\1/')"
  # GitHub caches releases/latest for about a minute, so just after a release the game can still be
  # told the previous version: retry for a couple of minutes before calling it a failure.
  for _ in 1 2 3 4 5 6; do
    API="$API" run download | grep -qF "Update v$TAG ready" && break
    run clean >/dev/null; echo "  (GitHub still serves an older latest release; retrying in 20 s)"; sleep 20
  done
  echo "== download the latest real release of $REPO (v$TAG)"; API="$API" expect "Update v$TAG ready" download
  echo "== next launch mounts it";                                 expect "applied=true after: $TAG" apply
  finish
fi

PY=""
for c in python3 python py; do if "$c" -c "" >/dev/null 2>&1; then PY="$c"; break; fi; done
[ -n "$PY" ] || { echo "update_test: needs Python 3 for the fake release server" >&2; exit 1; }

echo "== build a fake v0.2.0 update pack"
copy_project "$WORK/proj"
mkdir -p "$WORK/srv"
sed -i 's/^version=.*/version="0.2.0"/' "$WORK/proj/release.cfg"
"$GODOT" --headless --path "$WORK/proj" --import >/dev/null 2>&1 || true
"$GODOT" --headless --path "$WORK/proj" --export-pack "Windows Desktop" "$WORK/srv/game.pck" >/dev/null 2>&1
SHA=$(sha256sum "$WORK/srv/game.pck" | cut -d' ' -f1); SIZE=$(stat -c%s "$WORK/srv/game.pck")
mk() { # tag digest outfile
  cat > "$WORK/srv/$3" <<EOF
{"tag_name":"$1","assets":[{"name":"game.pck","size":$SIZE,"digest":"$2","browser_download_url":"http://127.0.0.1:$PORT/game.pck"}]}
EOF
}
mk v0.2.0 "sha256:$SHA" good.json
mk v0.2.0 "sha256:0000000000000000000000000000000000000000000000000000000000000000" bad.json
mk v0.1.0 "sha256:$SHA" same.json
# loopback only: binding every interface makes Windows Firewall pop up a prompt
"$PY" -m http.server "$PORT" --bind 127.0.0.1 --directory "$WORK/srv" >/dev/null 2>&1 & SERVER_PID=$!
for _ in $(seq 50); do curl -sf -o /dev/null "http://127.0.0.1:$PORT/good.json" && break; sleep 0.2; done

echo "== semver"; expect "semver: all ok" semver
echo "== already up to date";             API="http://127.0.0.1:$PORT/same.json" expect "Up to date." download
echo "== corrupted download is rejected"; API="http://127.0.0.1:$PORT/bad.json" expect "corrupted - not applied" download
echo "== good download";                  API="http://127.0.0.1:$PORT/good.json" expect "RESULT staged=[0.2.0] ready=[0.2.0]" download
echo "== next launch mounts it";          expect "applied=true after: 0.2.0" apply
finish
