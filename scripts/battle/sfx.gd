extends RefCounted
## Tiny synthesized battle sounds, no sound files. Built once, shared by every battle.
## Press M in battle to mute (it stays muted for the session).

static var muted := false
static var _lib: Dictionary = {}


static func play(sound: String, parent: Node) -> void:
	if muted:
		return
	if _lib.is_empty():
		_build()
	if not _lib.has(sound):
		return
	var pl := AudioStreamPlayer.new()
	pl.stream = _lib[sound]
	pl.finished.connect(pl.queue_free)
	parent.add_child(pl)
	pl.play()


static func _build() -> void:
	_lib["ok"] = _synth([{"f0": 500, "f1": 500, "dur": 0.04, "k": "square", "v": 0.12}])
	_lib["hit"] = _synth([{"f0": 220, "f1": 60, "dur": 0.12, "k": "square", "v": 0.3}])
	_lib["crit"] = _synth([
		{"f0": 330, "f1": 80, "dur": 0.14, "k": "square", "v": 0.3},
		{"f0": 660, "f1": 120, "dur": 0.10, "k": "square", "v": 0.2, "delay": 0.05},
	])
	_lib["hurt"] = _synth([{"f0": 140, "f1": 40, "dur": 0.22, "k": "saw", "v": 0.3}])
	_lib["guard"] = _synth([{"f0": 300, "f1": 500, "dur": 0.08, "k": "tri", "v": 0.35}])
	_lib["coil"] = _synth([{"f0": 90, "f1": 160, "dur": 0.35, "k": "saw", "v": 0.22}])
	_lib["drain"] = _synth([
		{"f0": 400, "f1": 100, "dur": 0.4, "k": "sine", "v": 0.35},
		{"f0": 300, "f1": 70, "dur": 0.4, "k": "sine", "v": 0.25, "delay": 0.1},
	])
	_lib["heal"] = _synth([
		{"f0": 440, "f1": 440, "dur": 0.08, "k": "tri", "v": 0.3},
		{"f0": 660, "f1": 660, "dur": 0.12, "k": "tri", "v": 0.3, "delay": 0.09},
	])
	_lib["die"] = _synth([{"f0": 160, "f1": 30, "dur": 1.0, "k": "saw", "v": 0.3}])


static func _synth(parts: Array) -> AudioStreamWAV:
	var rate := 22050
	var total := 0.0
	for p in parts:
		total = maxf(total, float(p.get("delay", 0.0)) + float(p["dur"]))
	var n := int(total * rate)
	var buf := PackedFloat32Array()
	buf.resize(n)
	for p in parts:
		var f0: float = p["f0"]
		var f1: float = p["f1"]
		var dur: float = p["dur"]
		var kind: String = p["k"]
		var vol: float = p.get("v", 0.25)
		var start := int(float(p.get("delay", 0.0)) * rate)
		var phase := 0.0
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
