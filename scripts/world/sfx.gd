extends Node
## Tiny synthesized sounds for the overworld, the same no-files approach as the battle. M mutes.

const SOUNDS := {
	"blip": [{"f0": 230, "f1": 230, "dur": 0.035, "k": "square", "v": 0.045}],
	"ok": [{"f0": 500, "f1": 500, "dur": 0.04, "k": "square", "v": 0.10}],
	"move": [{"f0": 700, "f1": 700, "dur": 0.025, "k": "square", "v": 0.05}],
	"back": [{"f0": 320, "f1": 200, "dur": 0.05, "k": "square", "v": 0.07}],
	"gesture": [{"f0": 180, "f1": 150, "dur": 0.06, "k": "tri", "v": 0.18}],
	"tug": [{"f0": 120, "f1": 60, "dur": 0.2, "k": "saw", "v": 0.25}],
	"creak": [
		{"f0": 300, "f1": 420, "dur": 0.25, "k": "saw", "v": 0.06},
		{"f0": 410, "f1": 330, "dur": 0.2, "k": "saw", "v": 0.05, "delay": 0.2},
	],
	"splash": [{"f0": 900, "f1": 200, "dur": 0.35, "k": "noise", "v": 0.25}],
	"drip": [{"f0": 900, "f1": 1400, "dur": 0.05, "k": "sine", "v": 0.12}],
	"swallow": [
		{"f0": 220, "f1": 40, "dur": 0.7, "k": "saw", "v": 0.25},
		{"f0": 110, "f1": 30, "dur": 0.7, "k": "square", "v": 0.12, "delay": 0.1},
	],
	"thud": [{"f0": 90, "f1": 40, "dur": 0.25, "k": "square", "v": 0.25}],
}

var muted := false
var _streams := {}


func play(id: String, pitch := 1.0) -> void:
	if muted or not SOUNDS.has(id):
		return
	if not _streams.has(id):
		_streams[id] = _synth(SOUNDS[id])
	var p := AudioStreamPlayer.new()
	p.stream = _streams[id]
	p.pitch_scale = pitch
	p.finished.connect(p.queue_free)
	add_child(p)
	p.play()


func _synth(parts: Array) -> AudioStreamWAV:
	var rate := 22050
	var total := 0.0
	for p: Dictionary in parts:
		total = maxf(total, float(p.get("delay", 0.0)) + float(p["dur"]))
	var n := int(total * rate)
	var buf := PackedFloat32Array()
	buf.resize(n)
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	for p: Dictionary in parts:
		var f0: float = p["f0"]
		var f1: float = p["f1"]
		var dur: float = p["dur"]
		var kind: String = p["k"]
		var vol: float = p.get("v", 0.25)
		var start := int(float(p.get("delay", 0.0)) * rate)
		var phase := 0.0
		var hold := 0.0
		for i in int(dur * rate):
			var t := float(i) / rate
			phase += f0 * pow(f1 / f0, t / dur) / rate
			var ph := fmod(phase, 1.0)
			var w := 0.0
			match kind:
				"sine": w = sin(TAU * ph)
				"square": w = 1.0 if ph < 0.5 else -1.0
				"saw": w = 2.0 * ph - 1.0
				"tri": w = 4.0 * absf(ph - 0.5) - 1.0
				"noise":
					if ph < hold:
						w = rng.randf_range(-1.0, 1.0)
					hold = ph
					w = w if w != 0.0 else rng.randf_range(-1.0, 1.0) * 0.5
			if start + i < n:
				buf[start + i] += w * vol * exp(-5.0 * t / dur)
	var bytes := PackedByteArray()
	bytes.resize(n * 2)
	for i in n:
		bytes.encode_s16(i * 2, int(clampf(buf[i], -1.0, 1.0) * 32767.0))
	var s := AudioStreamWAV.new()
	s.format = AudioStreamWAV.FORMAT_16_BITS
	s.mix_rate = rate
	s.stereo = false
	s.data = bytes
	return s
