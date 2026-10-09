extends Node
## First scene on every launch. If the updater staged a newer game.pck in user://, mount it
## *before* anything else loads, then open the title screen.
##
## Keep this file tiny and self-contained: it runs before an update is mounted, so it is the one
## piece of the game that an update can't change. Don't preload other game scripts here -- they'd be
## cached from the old build and shadow the updated ones.

const PACK := "user://update.pck"
const META := "user://update.json"


func _ready() -> void:
	apply_pending_update()
	get_tree().change_scene_to_file.call_deferred("res://title.tscn")


func apply_pending_update() -> bool:
	# The editor always runs the project folder itself; GRP_FORCE_UPDATES=1 is for tests.
	if OS.has_feature("editor") and OS.get_environment("GRP_FORCE_UPDATES") != "1":
		return false
	if not FileAccess.file_exists(PACK) or not FileAccess.file_exists(META):
		return false
	var meta: Variant = JSON.parse_string(FileAccess.get_file_as_string(META))
	if typeof(meta) != TYPE_DICTIONARY:
		_discard()
		return false
	var staged := str(meta.get("version", ""))
	# A fresh full download can be newer than an old staged pack; never downgrade.
	if not _is_newer(staged, _base_version()):
		_discard()
		return false
	if FileAccess.get_sha256(PACK) != str(meta.get("sha256", "")):
		_discard()
		return false
	if not ProjectSettings.load_resource_pack(PACK):
		_discard()
		return false
	return true


func _base_version() -> String:
	var cfg := ConfigFile.new()
	if cfg.load("res://release.cfg") != OK:
		return "0.0.0"
	return str(cfg.get_value("release", "version", "0.0.0"))


func _discard() -> void:
	for p in [PACK, META]:
		if FileAccess.file_exists(p):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(p))


func _is_newer(a: String, b: String) -> bool:
	var pa := _parts(a)
	var pb := _parts(b)
	for i in 3:
		if pa[i] != pb[i]:
			return pa[i] > pb[i]
	return false


func _parts(v: String) -> Array[int]:
	var out: Array[int] = [0, 0, 0]
	var core := v.trim_prefix("v").split("-")[0].split("+")[0]
	var bits := core.split(".")
	for i in mini(3, bits.size()):
		out[i] = int(bits[i])
	return out
