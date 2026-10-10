extends Node2D
## Base for maps. A map lays its ground from an ASCII grid onto a TileMapLayer, stands props and
## people on a y-sorted layer, darkens itself (lighting.gd) and scripts its story as coroutines that
## call the world's say() / ask() / caption(). Subclasses override build() and arrive().
## Every map is a script in scripts/world/maps/, loaded by World.go().

const TILE := 16
const Tiles := preload("res://scripts/world/tiles.gd")
const Actor := preload("res://scripts/world/actor.gd")
const Player := preload("res://scripts/world/player.gd")
const Lighting := preload("res://scripts/world/lighting.gd")
const HERO_SHEET := "res://art/world/hero.png"

var world: Node               # the World root
var player: Player
var ground: TileMapLayer
var things: Node2D            # props and people, drawn in y order
var light: Lighting
var rows: PackedStringArray
var walls := {}               # Vector2i -> true: cells nobody can enter
var people := {}              # Vector2i -> actor standing on (or stepping into) that cell
var examine := {}             # Vector2i -> Callable: things the hero can face and press Z on
var triggers := {}            # Vector2i -> Callable: fires when the hero finishes a step there
var spawns := {}              # name -> [cell, facing]
var landmarks := {}           # point-at id -> Node2D or Vector2 (map pixels): the hero turns to it
var camera: Camera2D
var hero_glow := 0.0          # > 0: a faint light around the hero (dark maps)
var _glow := -1


func _ready() -> void:
	ground = TileMapLayer.new()
	add_child(ground)
	things = Node2D.new()
	things.y_sort_enabled = true
	add_child(things)
	build()


## Lay the ground and add props, people, lights and spawns here.
func build() -> void:
	pass


## Called once the hero stands on `spawn`. Reveal the map (and start any arrival scene).
func arrive(_spawn: String) -> void:
	await world.reveal()


func size_px() -> Vector2i:
	return Vector2i(rows[0].length(), rows.size()) * TILE


# --------------------------------------------------------------------------------------------
# building
# --------------------------------------------------------------------------------------------

## Lays the ground from `layout` (one string per row) with an atlas from tiles.gd.
func lay(layout: PackedStringArray, atlas: Dictionary) -> void:
	rows = layout
	ground.tile_set = Tiles.make_tileset(atlas)
	var blocked: String = atlas["blocked"]
	for y in rows.size():
		for x in rows[y].length():
			var c := Vector2i(x, y)
			ground.set_cell(c, 0, Tiles.coords(atlas, rows, c))
			if blocked.contains(rows[y][x]):
				walls[c] = true


## Darkness over the whole map; `ambient` is the light level away from any lamp (0 = black).
func darken(ambient: float) -> void:
	light = Lighting.new()
	add_child(light)
	light.setup(Vector2(size_px()), ambient)


## Stands a sprite on a footprint of cells whose top-left is `c`, its bottom edge on the bottom of
## the footprint and centred across it. Blocks the footprint unless `solid` is false.
func prop(tex: Texture2D, c: Vector2i, footprint := Vector2i.ONE, solid := true, nudge := Vector2i.ZERO) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = tex
	s.centered = false
	s.position = Vector2(c.x * TILE + footprint.x * TILE / 2, (c.y + footprint.y) * TILE - 1) + Vector2(nudge)
	s.offset = Vector2(-tex.get_width() / 2, -tex.get_height() + 1)
	things.add_child(s)
	if solid:
		for y in footprint.y:
			for x in footprint.x:
				walls[c + Vector2i(x, y)] = true
	return s


## Puts a person on cell `c`. `columns`: poses in the sheet (see actor.gd).
func person(sheet: String, c: Vector2i, facing := Vector2i.DOWN, columns := 3, frame := Vector2i(16, 24)) -> Actor:
	var a := Actor.new()
	a.map = self
	a.setup(load(sheet), columns, frame)
	things.add_child(a)
	a.place(c)
	a.face(facing)
	return a


func spawn_player(spawn: String) -> void:
	player = Player.new()
	player.map = self
	player.world = world
	player.setup(load(HERO_SHEET), 10)
	things.add_child(player)
	var sp: Array = spawns.get(spawn, [Vector2i.ZERO, Vector2i.DOWN])
	player.place(sp[0])
	player.face(sp[1])
	var cam := Camera2D.new()
	cam.offset = Vector2(0, -8)
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = size_px().x
	cam.limit_bottom = size_px().y
	player.add_child(cam)
	cam.make_current()
	camera = cam
	if hero_glow > 0.0 and light != null:
		_glow = light.add(player.position, 26.0, hero_glow)


# --------------------------------------------------------------------------------------------
# the grid
# --------------------------------------------------------------------------------------------

func blocked(c: Vector2i, who: Node = null) -> bool:
	if c.x < 0 or c.y < 0 or c.y >= rows.size() or c.x >= rows[0].length():
		return true
	if walls.has(c):
		return true
	var p: Node = people.get(c)
	return p != null and p != who


func occupy(c: Vector2i, who: Node) -> void:
	people[c] = who


func vacate(c: Vector2i, who: Node) -> void:
	if people.get(c) == who:
		people.erase(c)


## The hero pressed Z facing cell `c`.
func interact(c: Vector2i) -> void:
	var p: Actor = people.get(c)
	if p != null and p.talk.is_valid():
		if p.turns_to_talk:
			p.face_toward(player)
		world.run(p.talk)
	elif examine.has(c):
		world.run(examine[c])


## The hero finished a step onto `c`.
func hero_stepped(c: Vector2i) -> void:
	if triggers.has(c):
		world.run(triggers[c])


func _physics_process(_delta: float) -> void:
	if _glow >= 0 and player != null:
		light.move(_glow, player.position + Vector2(0, -8))


## Shakes the view by up to `px` whole pixels for `sec` seconds.
func shake(px: float, sec: float) -> void:
	if camera == null:
		return
	var tw := create_tween()
	for i in maxi(1, int(sec / 0.04)):
		tw.tween_property(camera, "offset", Vector2(randf_range(-px, px), -8.0 + randf_range(-px, px)).round(), 0.04)
	tw.tween_property(camera, "offset", Vector2(0, -8), 0.04)
	await tw.finished


## Where a point-at target is, or null if it has no place on this map.
func landmark(id: String) -> Variant:
	var l: Variant = landmarks.get(id)
	if l is Node2D:
		return l.position if is_instance_valid(l) else null
	return l


## Pixel centre of a cell, for lights.
func at(c: Vector2i, dy := 0) -> Vector2:
	return Vector2(c.x * TILE + TILE / 2, c.y * TILE + TILE / 2 + dy)
