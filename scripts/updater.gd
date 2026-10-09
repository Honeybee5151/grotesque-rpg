extends Node
## In-game updater. Asks GitHub for the latest release of the repo stamped into release.cfg;
## if it's newer, downloads that release's `game.pck`, checks it, and stages it in user://.
## boot.gd mounts it on the next launch. Needs the repo to be public (no login is used).

signal status(text: String)
signal update_ready(version: String)

const PACK_ASSET := "game.pck"
const PACK := "user://update.pck"
const PART := "user://update.pck.part"
const META := "user://update.json"

var enabled := true            # the title screen turns this off inside the editor
var api_url_override := ""     # tests point this at a local fake release
var current_version := "0.0.0"
var repo := ""
var ready_version := ""

var _dl_http: HTTPRequest
var _dl_total := 0
var _dl_label := ""
var _timer: Timer


func _ready() -> void:
	var cfg := ConfigFile.new()
	if cfg.load("res://release.cfg") == OK:
		current_version = str(cfg.get_value("release", "version", "0.0.0"))
		repo = str(cfg.get_value("release", "repo", ""))
	_timer = Timer.new()
	_timer.wait_time = 0.25
	_timer.timeout.connect(_progress_tick)
	add_child(_timer)


func check() -> void:
	if not enabled:
		status.emit("Dev build - updates are off.")
		return
	var url := api_url_override
	if url == "":
		if repo == "" or repo.begins_with("OWNER/"):
			status.emit("Updates aren't set up in this build.")
			return
		url = "https://api.github.com/repos/%s/releases/latest" % repo
	status.emit("Checking for updates...")

	var headers := PackedStringArray(["Accept: application/vnd.github+json", "User-Agent: grotesque-rpg-updater"])
	var res := await _fetch(url, headers, "", 15.0)
	if res[0] != HTTPRequest.RESULT_SUCCESS:
		status.emit("Couldn't reach GitHub - skipping update check.")
		return
	var code: int = res[1]
	if code == 404:
		status.emit("No releases published yet. (v%s)" % current_version)
		return
	if code != 200:
		status.emit("Update check failed (HTTP %d)." % code)
		return
	var parsed: Variant = JSON.parse_string((res[2] as PackedByteArray).get_string_from_utf8())
	if typeof(parsed) != TYPE_DICTIONARY:
		status.emit("Update check failed (bad response).")
		return
	var rel: Dictionary = parsed
	var tag := str(rel.get("tag_name", "")).trim_prefix("v")
	if tag == "" or not is_newer(tag, current_version):
		status.emit("Up to date. (v%s)" % current_version)
		return

	if staged_version() == tag:
		_mark_ready(tag)
		return

	var asset: Dictionary = {}
	for a in rel.get("assets", []):
		if str(a.get("name", "")) == PACK_ASSET:
			asset = a
	if asset.is_empty():
		status.emit("v%s is out, but it has no update pack - download it from GitHub." % tag)
		return

	_dl_total = int(asset.get("size", 0))
	_dl_label = tag
	_timer.start()
	status.emit("Downloading v%s..." % tag)
	var dl := await _fetch(str(asset["browser_download_url"]), PackedStringArray(["User-Agent: grotesque-rpg-updater"]), PART, 0.0)
	_timer.stop()
	if dl[0] != HTTPRequest.RESULT_SUCCESS or int(dl[1]) != 200:
		_remove(PART)
		status.emit("Update download failed.")
		return

	# verify: size and (when GitHub provides it) SHA-256
	var sha := FileAccess.get_sha256(PART)
	var digest := str(asset.get("digest", ""))
	var bad := false
	if _dl_total > 0:
		var f := FileAccess.open(PART, FileAccess.READ)
		bad = f == null or f.get_length() != _dl_total
	if digest.begins_with("sha256:") and digest.trim_prefix("sha256:") != sha:
		bad = true
	if bad or sha == "":
		_remove(PART)
		status.emit("Update download was corrupted - not applied.")
		return

	_remove(PACK)
	DirAccess.rename_absolute(ProjectSettings.globalize_path(PART), ProjectSettings.globalize_path(PACK))
	var mf := FileAccess.open(META, FileAccess.WRITE)
	mf.store_string(JSON.stringify({"version": tag, "sha256": sha}))
	mf.close()
	_mark_ready(tag)


func staged_version() -> String:
	if not FileAccess.file_exists(PACK) or not FileAccess.file_exists(META):
		return ""
	var meta: Variant = JSON.parse_string(FileAccess.get_file_as_string(META))
	if typeof(meta) != TYPE_DICTIONARY:
		return ""
	return str(meta.get("version", ""))


func restart_game() -> void:
	OS.create_process(OS.get_executable_path(), OS.get_cmdline_args())
	get_tree().quit()


func _mark_ready(tag: String) -> void:
	ready_version = tag
	status.emit("Update v%s ready - restart to apply." % tag)
	update_ready.emit(tag)


func _fetch(url: String, headers: PackedStringArray, file: String, timeout: float) -> Array:
	var http := HTTPRequest.new()
	http.timeout = timeout
	if file != "":
		http.download_file = file
	add_child(http)
	_dl_http = http
	if http.request(url, headers) != OK:
		http.queue_free()
		return [HTTPRequest.RESULT_CANT_CONNECT, 0, PackedByteArray()]
	var r: Array = await http.request_completed
	http.queue_free()
	return [r[0], r[1], r[3]]


func _progress_tick() -> void:
	if not is_instance_valid(_dl_http) or _dl_total <= 0:
		return
	var pct := int(100.0 * _dl_http.get_downloaded_bytes() / _dl_total)
	status.emit("Downloading v%s... %d%%" % [_dl_label, clampi(pct, 0, 100)])


func _remove(p: String) -> void:
	if FileAccess.file_exists(p):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(p))


static func is_newer(a: String, b: String) -> bool:
	var pa := _parts(a)
	var pb := _parts(b)
	for i in 3:
		if pa[i] != pb[i]:
			return pa[i] > pb[i]
	return false


static func _parts(v: String) -> Array[int]:
	var out: Array[int] = [0, 0, 0]
	var core := v.trim_prefix("v").split("-")[0].split("+")[0]
	var bits := core.split(".")
	for i in mini(3, bits.size()):
		out[i] = int(bits[i])
	return out
