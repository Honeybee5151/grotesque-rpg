extends ColorRect
## Fog over a map: drifting patches of pale haze with ordered-dither edges, moving a whole pixel
## at a time so nothing shimmers. Lies over the people and under the lighting, which tints it.

const SHADER := """
shader_type canvas_item;

uniform vec2 area = vec2(320.0, 180.0);
uniform vec2 drift = vec2(0.0);
uniform float density = 0.5;
uniform vec4 fog_color : source_color = vec4(0.70, 0.69, 0.78, 1.0);
uniform float thick = 0.2;

const float BAYER[16] = float[](0.0, 8.0, 2.0, 10.0, 12.0, 4.0, 14.0, 6.0,
                                 3.0, 11.0, 1.0, 9.0, 15.0, 7.0, 13.0, 5.0);

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
	           mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void fragment() {
	vec2 cell = floor(UV * area);
	vec2 p = cell + drift;
	float n = noise(p / 80.0) * 0.7 + noise(p / 26.0) * 0.3;
	float v = n - (1.0 - density);
	int bi = int(mod(cell.y, 4.0)) * 4 + int(mod(cell.x, 4.0));
	float t = (BAYER[bi] + 0.5) / 16.0;
	float a = 0.0;
	// wisps: a thin core, and a checkered fringe that thins out toward the edge
	if (v > 0.1) {
		a = thick;
	} else if (v > 0.0 && t < v / 0.1 * 0.5) {
		a = thick;
	}
	COLOR = vec4(fog_color.rgb, a);
}
"""

var speed := Vector2(4.0, 1.5)      # pixels a second
var _t := 0.0
var _mat: ShaderMaterial


func setup(area: Vector2, density: float) -> void:
	size = area
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	z_index = 90
	var sh := Shader.new()
	sh.code = SHADER
	_mat = ShaderMaterial.new()
	_mat.shader = sh
	material = _mat
	_mat.set_shader_parameter("area", area)
	_mat.set_shader_parameter("density", density)


func _process(delta: float) -> void:
	_t += delta
	_mat.set_shader_parameter("drift", (speed * _t).floor())
