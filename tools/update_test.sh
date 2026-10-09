#!/usr/bin/env bash
# End-to-end test of the in-game updater against a fake local GitHub release.
# Usage: GODOT=/path/to/godot tools/update_test.sh
set -euo pipefail
GODOT="${GODOT:-godot}"
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
PORT=8765
SERVER_PID=""
trap 'kill $SERVER_PID 2>/dev/null || true; rm -rf "$WORK"' EXIT
run() { GRP_FORCE_UPDATES=1 GRP_TEST_API="${API:-}" "$GODOT" --headless --path "$PROJ" --script res://tools/update_test.gd -- "$@" 2>&1 | grep -vE "^Godot Engine|ObjectDB|at: cleanup|leaked"; }

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
python3 -m http.server $PORT --directory "$WORK/srv" >/dev/null 2>&1 & SERVER_PID=$!
sleep 1

echo "== semver"; run semver
run clean >/dev/null
echo "== already up to date";   API="http://127.0.0.1:$PORT/same.json" run download
echo "== corrupted download is rejected"; API="http://127.0.0.1:$PORT/bad.json" run download
echo "== good download";        API="http://127.0.0.1:$PORT/good.json" run download
echo "== next launch mounts it"; run apply
run clean >/dev/null
