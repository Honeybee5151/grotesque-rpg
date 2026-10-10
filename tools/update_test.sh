#!/usr/bin/env bash
# End-to-end test of the in-game updater against a fake local GitHub release.
# Usage: GODOT=/path/to/godot tools/update_test.sh   (Windows: tools\check.ps1 -Updater, or this from Git Bash)
# Exits 1 if any step doesn't end the way it should.
set -euo pipefail
GODOT="${GODOT:-godot}"
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
PORT=8765
SERVER_PID=""
FAILS=0
trap 'kill $SERVER_PID 2>/dev/null || true; rm -rf "$WORK"' EXIT
run() { GRP_FORCE_UPDATES=1 GRP_TEST_API="${API:-}" "$GODOT" --headless --path "$PROJ" --script res://tools/update_test.gd -- "$@" 2>&1 | grep -vE "^Godot Engine|ObjectDB|at: cleanup|leaked"; }
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
PY=""
for c in python3 python py; do if "$c" -c "" >/dev/null 2>&1; then PY="$c"; break; fi; done
[ -n "$PY" ] || { echo "update_test: needs Python 3 for the fake release server" >&2; exit 1; }

echo "== build a fake v0.2.0 update pack"
mkdir -p "$WORK/proj" "$WORK/srv"
(cd "$PROJ" && tar --exclude=./build --exclude=./.git -cf - .) | (cd "$WORK/proj" && tar -xf -)
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
run clean >/dev/null
echo "== already up to date";             API="http://127.0.0.1:$PORT/same.json" expect "Up to date." download
echo "== corrupted download is rejected"; API="http://127.0.0.1:$PORT/bad.json" expect "corrupted - not applied" download
echo "== good download";                  API="http://127.0.0.1:$PORT/good.json" expect "RESULT staged=[0.2.0] ready=[0.2.0]" download
echo "== next launch mounts it";          expect "applied=true after: 0.2.0" apply
run clean >/dev/null
if [ "$FAILS" -gt 0 ]; then echo "== updater: $FAILS check(s) FAILED"; exit 1; fi
echo "== updater: all checks passed"
