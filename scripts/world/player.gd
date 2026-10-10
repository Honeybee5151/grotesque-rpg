extends "res://scripts/world/actor.gd"
## The hero on the map. Arrows / WASD walk; Z (Enter, Space, left click) faces whoever or whatever is
## in front of him. The most recently pressed direction wins, so diagonals feel right.

const KEYS := {
	Vector2i.UP: [KEY_UP, KEY_W],
	Vector2i.DOWN: [KEY_DOWN, KEY_S],
	Vector2i.LEFT: [KEY_LEFT, KEY_A],
	Vector2i.RIGHT: [KEY_RIGHT, KEY_D],
}

var world: Node
var _held: Array[Vector2i] = []


func _ready() -> void:
	arrived.connect(func() -> void: map.hero_stepped(cell))


func _physics_process(delta: float) -> void:
	_track_keys()
	super(delta)
	if moving or world.busy > 0 or _held.is_empty():
		return
	step(_held.back())


func _track_keys() -> void:
	for d: Vector2i in KEYS:
		var down := false
		for k: Key in KEYS[d]:
			down = down or Input.is_key_pressed(k)
		if down and not _held.has(d):
			_held.append(d)
		elif not down and _held.has(d):
			_held.erase(d)


func _unhandled_input(event: InputEvent) -> void:
	var ok := false
	if event is InputEventKey and event.pressed and not event.echo:
		ok = event.keycode in [KEY_Z, KEY_ENTER, KEY_KP_ENTER, KEY_SPACE]
	elif event is InputEventMouseButton and event.pressed:
		ok = event.button_index == MOUSE_BUTTON_LEFT
	if ok and world.busy == 0 and not moving:
		get_viewport().set_input_as_handled()
		map.interact(cell + facing)
