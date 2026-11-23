extends Node2D
# Little effects drawn in code for heart-event scenes (scripts/cutscene.gd "fx", 23 Nov 2026), so what the
# narration says can be seen: bees buzzing round a spot, fireflies drifting and blinking over a wide one, steam
# curling up from a pot or a mug, and the station's heartbeats as little lights rising round S.A.R.A.'s dais.
# Zaas's scenes add water: spray from a burst pipe, and bubbles rising where something is under the water.
# Stand-ins until there's art for them (Art Fix List, "Heart events").

var kind := "bees"
var center := Vector2.ZERO      # where the effect is heading (world pixels)
var spread := 14.0              # how far the motes wander from it
var _here := Vector2.ZERO       # where it is now: it drifts to center when moved
var _motes: Array = []          # [phase, speed, reach (0..1), angle]
var _t := 0.0


func setup(what: String, at: Vector2, radius: float) -> void:
	kind = what
	center = at
	_here = at
	spread = radius
	z_index = 40                # over the people standing in the scene
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(what)
	var count: int = {"bees": 22, "fireflies": 28, "steam": 7, "heartbeats": 26, "spray": 30, "bubbles": 14}.get(what, 12)
	for _i in count:
		var speed: float = rng.randf_range(2.0, 4.5) if what == "bees" else rng.randf_range(0.3, 0.9)
		_motes.append([rng.randf() * TAU, speed, rng.randf_range(0.3, 1.0), rng.randf() * TAU])


# Head somewhere else (bees settling on a hand), wandering this far from it.
func move_to(at: Vector2, radius: float) -> void:
	center = at
	spread = radius


func _process(delta: float) -> void:
	_t += delta
	_here = _here.move_toward(center, delta * 28.0)
	queue_redraw()


func _draw() -> void:
	for m in _motes:
		var ph: float = m[0]
		var sp: float = m[1]
		var reach: float = spread * float(m[2])
		match kind:
			"bees":
				# loops round the spot, with a quick jitter for the buzz; yellow and dark body, a pale wing
				var a: float = float(m[3]) + _t * sp
				var p: Vector2 = _here + Vector2(cos(a), sin(a * 1.7) * 0.6) * reach
				p += Vector2(sin(_t * 23.0 + ph), cos(_t * 19.0 + ph)) * 0.8
				p = p.round()
				draw_rect(Rect2(p, Vector2(2, 1)), Color("f2c230"))
				draw_rect(Rect2(p + Vector2(1, 0), Vector2(1, 1)), Color("3a2414"))
				draw_rect(Rect2(p + Vector2(0, -1), Vector2(1, 1)), Color(1, 1, 1, 0.65))
			"fireflies":
				# slow drifting, each blinking on its own beat, with a faint halo
				var p: Vector2 = _here + Vector2(sin(_t * sp + ph) * reach, cos(_t * sp * 0.7 + float(m[3])) * reach * 0.5)
				var glow: float = 0.5 + 0.5 * sin(_t * 2.0 + ph * 3.0)
				if glow >= 0.15:
					p = p.round()
					draw_rect(Rect2(p - Vector2(1, 1), Vector2(3, 3)), Color(0.85, 1.0, 0.5, 0.18 * glow))
					draw_rect(Rect2(p, Vector2(1, 1)), Color(0.95, 1.0, 0.6, glow))
			"heartbeats":
				# a ring of small lights round the spot, each beating twice and resting, on its own slow rhythm
				var a: float = float(m[3]) + _t * 0.08
				var p: Vector2 = _here + Vector2(cos(a), sin(a) * 0.45) * reach - Vector2(0, 6.0 + float(m[2]) * 10.0)
				var beat: float = fmod(_t * (0.9 + sp * 0.3) + ph, 1.0)
				var pulse: float = 1.0 if beat < 0.08 or (beat > 0.18 and beat < 0.26) else 0.35
				p = p.round()
				draw_rect(Rect2(p - Vector2(1, 1), Vector2(3, 3)), Color(0.55, 0.85, 1.0, 0.2 * pulse))
				draw_rect(Rect2(p, Vector2(1, 1)), Color(0.75, 0.95, 1.0, pulse))
			"spray":
				# drops thrown up and out from the spot, falling back in arcs, over and over
				var life: float = fmod(_t * (0.9 + sp) + ph, 1.0)
				var side: float = cos(float(m[3]))
				var p: Vector2 = _here + Vector2(side * reach * life, -14.0 * float(m[2]) * life + 26.0 * life * life)
				draw_rect(Rect2(p.round(), Vector2(1, 2)), Color(0.62, 0.85, 1.0, 0.85 * (1.0 - life * 0.6)))
			"bubbles":
				# little rings wobbling upward and popping, over a spot under the water
				var life: float = fmod(_t * sp * 0.45 + ph, 1.0)
				var p: Vector2 = _here + Vector2((float(m[2]) - 0.65) * spread + sin(_t * 3.0 + ph) * 1.5, -life * 22.0)
				var r: float = 1.0 if float(m[2]) < 0.7 else 2.0
				p = p.round()
				draw_rect(Rect2(p - Vector2(r, 0), Vector2(1, 1)), Color(0.8, 0.95, 1.0, 0.8 * (1.0 - life)))
				draw_rect(Rect2(p + Vector2(r, 0), Vector2(1, 1)), Color(0.8, 0.95, 1.0, 0.8 * (1.0 - life)))
				draw_rect(Rect2(p - Vector2(0, r), Vector2(1, 1)), Color(0.9, 1.0, 1.0, 0.9 * (1.0 - life)))
				draw_rect(Rect2(p + Vector2(0, r), Vector2(1, 1)), Color(0.6, 0.85, 1.0, 0.6 * (1.0 - life)))
			"steam":
				# puffs rise, sway and fade, then start again at the bottom
				var life: float = fmod(_t * sp * 0.35 + ph, 1.0)
				var p: Vector2 = _here + Vector2(sin(life * 6.0 + ph) * 2.0 + (float(m[2]) - 0.65) * spread, -life * 18.0)
				draw_rect(Rect2(p.round(), Vector2(2, 2)), Color(0.92, 0.92, 0.96, 0.45 * (1.0 - life)))
