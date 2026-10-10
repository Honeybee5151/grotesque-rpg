extends RefCounted
## Tile atlases and the small autotiler maps use. A map is an ASCII grid; each character names a
## terrain. Masked terrains take their atlas column from their four neighbours (bit 1 up, 2 right,
## 4 down, 8 left), set when that neighbour is the other kind: land beside water, water beside land.
## Keep the atlas layouts in sync with art/world/src/*.py.

const TILE := 16

## The Sallow Fen (art/world/src/fen.py). Characters not listed draw as peat.
const FEN := {
	"texture": "res://art/world/fen_tiles.png",
	"water": "~|=",
	"blocked": "~",
	"terrain": {
		"~": {"rows": [0, 1], "masked": true},
		".": {"rows": [2, 3, 4], "masked": true},
		",": {"rows": [5, 6], "masked": true},
		"o": {"rows": [7], "variants": 4},
		"|": {"rows": [8], "masked": true},
		"=": {"rows": [9], "masked": true},
	},
}


static func make_tileset(atlas: Dictionary) -> TileSet:
	var tex: Texture2D = load(atlas["texture"])
	var ts := TileSet.new()
	ts.tile_size = Vector2i(TILE, TILE)
	var src := TileSetAtlasSource.new()
	src.texture = tex
	src.texture_region_size = Vector2i(TILE, TILE)
	for y in tex.get_height() / TILE:
		for x in tex.get_width() / TILE:
			src.create_tile(Vector2i(x, y))
	ts.add_source(src, 0)
	return ts


static func variant(c: Vector2i, n: int) -> int:
	return absi((c.x * 73856093) ^ (c.y * 19349663)) % n


static func coords(atlas: Dictionary, rows: PackedStringArray, c: Vector2i) -> Vector2i:
	var terrain: Dictionary = atlas["terrain"]
	var ch := rows[c.y][c.x]
	var spec: Dictionary = terrain.get(ch, terrain["."])
	var spec_rows: Array = spec["rows"]
	if not spec.get("masked", false):
		return Vector2i(variant(c, int(spec.get("variants", 1))), spec_rows[0])
	var water: String = atlas["water"]
	var wet := water.contains(ch)
	var mask := 0
	var bit := 1
	for d: Vector2i in [Vector2i.UP, Vector2i.RIGHT, Vector2i.DOWN, Vector2i.LEFT]:
		var n := c + d
		var nch := ch
		if n.y >= 0 and n.y < rows.size() and n.x >= 0 and n.x < rows[n.y].length():
			nch = rows[n.y][n.x]
		if water.contains(nch) != wet:
			mask |= bit
		bit <<= 1
	return Vector2i(mask, spec_rows[variant(c, spec_rows.size())])
