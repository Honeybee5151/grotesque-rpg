extends ColorRect
## Night for a map. Darkness in four flat bands with ordered dithering only where one band meets the
## next (no smooth gradients), lifted around lights. It multiplies the scene, so shadows lean violet
## and lantern light leans warm. Light positions are in map pixels.

const SHADER := """
shader_type canvas_item;
render_mode blend_mul, unshaded;

uniform vec2 area = vec2(320.0, 180.0);
uniform int count = 0;
uniform vec4 lights[16];
uniform float ambient = 0.3;
uniform vec3 band0 : source_color = vec3(0.13, 0.10, 0.24);
uniform vec3 band1 : source_color = vec3(0.36, 0.30, 0.52);
uniform vec3 band2 : source_color = vec3(0.68, 0.62, 0.80);
uniform vec3 band3 : source_color = vec3(1.0, 0.93, 0.80);

const float BAYER[16] = float[](0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0,
                                 3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0);

void fragment() {
	vec2 p = floor(UV * area);
	float l = ambient;
	for (int i = 0; i < 16; i++) {
		if (i >= count) {
			break;
		}
		float d = length(p + 0.5 - lights[i].xy) / lights[i].z;
		l = max(l, lights[i].w * (1.0 - d));
	}
	float q = clamp(l, 0.0, 0.999) * 4.0;
	float band = floor(q);
	float f = q - band;
	int bi = int(mod(p.y, 4.0)) * 4 + int(mod(p.x, 4.0));
	float t = (BAYER[bi] + 0.5) / 16.0;
	if (f > 0.7 && t < (f - 0.7) / 0.3) {
		band += 1.0;
	}
	vec3 c = band < 0.5 ? band0 : (band < 1.5 ? band1 : (band < 2.5 ? band2 : band3));
	COLOR = vec4(c, 1.0);
}
"""

var ambient := 0.3
var _lights: Array[Dictionary] = []
var _mat: ShaderMaterial
var _tick := 0.0


func setup(area: Vector2, ambient_level: float) -> void:
	size = area
	ambient = ambient_level
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	z_index = 100
	var sh := Shader.new()
	sh.code = SHADER
	_mat = ShaderMaterial.new()
	_mat.shader = sh
	material = _mat
	_mat.set_shader_parameter("area", area)
	_push()


## Adds a light at `pos` (map pixels) and returns its index. Flickering lights wobble a pixel or two.
func add(pos: Vector2, radius: float, strength := 1.0, flicker := false) -> int:
	_lights.append({"pos": pos, "radius": radius, "strength": strength, "flicker": flicker, "r": radius})
	_push()
	return _lights.size() - 1


func move(i: int, pos: Vector2) -> void:
	_lights[i]["pos"] = pos
	_push()


func set_strength(i: int, strength: float) -> void:
	_lights[i]["strength"] = strength
	_push()


func _process(delta: float) -> void:
	_tick += delta
	if _tick < 0.12:
		return
	_tick = 0.0
	var changed := false
	for l in _lights:
		if l["flicker"]:
			l["r"] = float(l["radius"]) + float(randi_range(-1, 1)) * 1.5
			changed = true
	if changed:
		_push()


func _push() -> void:
	if _mat == null:
		return
	var arr := PackedVector4Array()
	for l in _lights:
		var p: Vector2 = l["pos"]
		arr.append(Vector4(p.x, p.y, float(l["r"]), float(l["strength"])))
	_mat.set_shader_parameter("count", arr.size())
	_mat.set_shader_parameter("lights", arr)
	_mat.set_shader_parameter("ambient", ambient)
