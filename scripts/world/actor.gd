extends Node2D
## Someone standing on the tile grid. Steps one tile at a time at one pixel per physics tick, so it
## is always on whole pixels. Sheets have one row per facing (down, up, left, right) and one column
## per pose (see art/world/src/people.py); a sheet may have fewer columns than there are poses.

signal arrived

const TILE := 16
const ROW := {Vector2i.DOWN: 0, Vector2i.UP: 1, Vector2i.LEFT: 2, Vector2i.RIGHT: 3}
enum Pose { STAND, WALK_A, WALK_B, NOD, SHAKE_A, SHAKE_B, SHRUG, POINT, SHOW, POINT_SELF }

var map: Node                 # the map this actor stands on
var cell := Vector2i.ZERO
var facing := Vector2i.DOWN
var pose := Pose.STAND
var moving := false
var talk := Callable()        # run when the hero faces this actor and presses Z
var turns_to_talk := true     # face the hero when he talks to us
var sprite: Sprite2D

var _dir := Vector2i.ZERO
var _left := 0
var _foot := false
var _cols := 1


func setup(tex: Texture2D, columns: int, frame_size := Vector2i(16, 24)) -> void:
	_cols = columns
	sprite = Sprite2D.new()
	sprite.texture = tex
	sprite.hframes = columns
	sprite.vframes = maxi(1, tex.get_height() / frame_size.y)
	sprite.centered = false
	sprite.offset = Vector2(-frame_size.x / 2, -frame_size.y + 1)
	add_child(sprite)
	_refresh()


## Puts the actor on a cell at once. Its origin is the bottom-centre pixel of the cell.
func place(c: Vector2i) -> void:
	if map:
		map.vacate(cell, self)
	cell = c
	position = Vector2(c.x * TILE + TILE / 2, c.y * TILE + TILE - 1)
	if map:
		map.occupy(c, self)


func face(d: Vector2i) -> void:
	if d != Vector2i.ZERO:
		facing = d
	_refresh()


func face_toward(other: Node2D) -> void:
	face_toward_pos(other.position)


func face_toward_pos(p: Vector2) -> void:
	var d: Vector2 = p - position
	if absf(d.x) > absf(d.y):
		face(Vector2i.RIGHT if d.x > 0 else Vector2i.LEFT)
	else:
		face(Vector2i.DOWN if d.y > 0 else Vector2i.UP)


## Starts a one-tile step. Returns false (and only turns) if the way is blocked.
func step(d: Vector2i) -> bool:
	face(d)
	if moving or map.blocked(cell + d, self):
		return false
	map.vacate(cell, self)
	cell += d
	map.occupy(cell, self)
	_dir = d
	_left = TILE
	_foot = not _foot
	moving = true
	_refresh()
	return true


## Walks a list of directions, waiting whenever the way is blocked.
func walk(path: Array) -> void:
	for d: Vector2i in path:
		while not step(d):
			await get_tree().physics_frame
		await arrived


## Acts out a gesture: "nod", "shake", "shrug", "point", "show" or "silent". Pointing at "self"
## puts a hand on his chest instead.
func gesture(g: String, at := "") -> void:
	match g:
		"nod":
			for i in 2:
				await _hold(Pose.NOD, 0.13)
				await _hold(Pose.STAND, 0.11)
		"shake":
			for i in 2:
				await _hold(Pose.SHAKE_A, 0.12)
				await _hold(Pose.SHAKE_B, 0.12)
		"shrug":
			await _hold(Pose.SHRUG, 0.55)
		"point":
			await _hold(Pose.POINT_SELF if at == "self" else Pose.POINT, 0.7)
		"show":
			await _hold(Pose.SHOW, 0.7)
		_:
			await get_tree().create_timer(0.55).timeout
	pose = Pose.STAND
	_refresh()


func _hold(p: int, sec: float) -> void:
	pose = p
	_refresh()
	await get_tree().create_timer(sec).timeout


func _physics_process(_delta: float) -> void:
	if not moving:
		return
	position += Vector2(_dir)
	_left -= 1
	if _left <= 0:
		moving = false
	_refresh()
	if not moving:
		arrived.emit()


func _refresh() -> void:
	if sprite == null:
		return
	var col := pose
	if moving and _left > TILE / 2:
		col = Pose.WALK_A if _foot else Pose.WALK_B
	var row: int = ROW[facing] if sprite.vframes > 1 else 0
	sprite.frame = row * _cols + mini(col, _cols - 1)
