extends SubViewport
# The title screen's moving picture, drawn live from the pack's lossless art (title/scene/*.png) instead of
# played as video, so every pixel is as sharp as the art and nothing has to switch between clips. A port of
# the pack's source/scene.cpp (Echo_Landing_Title_Screen.zip): the timing is worked out here each frame, the
# per-pixel work is in shaders/title/. It draws on the pack's 960x540 canvas; title_screen.gd shows the result
# full screen through shaders/sharp_scale.gdshader (exactly 2x at 1080p). The shaders were checked offline
# against frames of the pack's .mp4 (run on a software OpenGL); not yet run in Godot.
# show_time(t): t is seconds since the opening started. The approach runs from 0 to 26 s; from then on the
# station loop repeats every 120 s, with everything (clouds, orbit, sun, stars) closing on the loop.
# Layers, back to front: sky with stars and cloud light; lightning and shooting stars; sun; planet; moon base;
# its lamps and the drifting rocks; the knocked-off wing; fighter; sparks.
# Easter egg (Zachary, 21 Nov): click the fighter and it sparks where you touched it and jolts; the third click
# breaks its intact wing off at the orange stripe, and the outer panel tumbles away while the new cut sparks.
# title_screen.gd calls poke(); title/scene/fighter_wing.png marks the panel and the cut
# (tools/dev/title_wing_mask.py).

const CANVAS := Vector2i(960, 540)
const INTRO := 26.0
const LOOP := 120.0
const ART := "res://title/scene/"
const SHADERS := "res://shaders/title/"
const MAX_PRIMS := 64

# The glints scene.cpp pins to bright points of the starfield, one per 83x80 cell (12 x 7 cells): x, y on
# the starfield, phase, twinkles per loop; -1 for an empty cell. Worked out by tools/dev/title_stars.py.
const STARS := [
	255, 80, 8.16, 11,  331, 23, 3.36, 17,  390, 86, 7.44, 12,  -1, -1, 0, 0,  608, 81, 6.72, 13,  664, 80, 1.92, 19,  720, 68, 6.00, 14,  -1, -1, 0, 0,  -1, -1, 0, 0,  -1, -1, 0, 0,  -1, -1, 0, 0,  1150, 59, 8.64, 11,
	-1, -1, 0, 0,  320, 161, 1.92, 15,  -1, -1, 0, 0,  534, 112, 1.20, 16,  583, 125, 5.28, 11,  -1, -1, 0, 0,  752, 111, 4.56, 12,  852, 149, 8.64, 18,  -1, -1, 0, 0,  1038, 157, 7.92, 19,  -1, -1, 0, 0,  1149, 112, 7.20, 20,
	231, 216, 5.28, 18,  355, 185, 0.48, 13,  -1, -1, 0, 0,  479, 230, 8.64, 14,  599, 229, 3.84, 20,  639, 230, 7.92, 15,  785, 198, 3.12, 10,  -1, -1, 0, 0,  931, 181, 2.40, 11,  1028, 248, 6.48, 17,  1065, 220, 1.68, 12,  1187, 187, 5.76, 18,
	271, 312, 3.84, 16,  377, 324, 7.92, 11,  453, 308, 3.12, 17,  532, 276, 7.20, 12,  -1, -1, 0, 0,  676, 322, 6.48, 13,  780, 277, 1.68, 19,  842, 288, 5.76, 14,  891, 298, 0.96, 20,  -1, -1, 0, 0,  1083, 301, 0.24, 10,  1181, 273, 4.32, 16,
	268, 381, 2.40, 14,  -1, -1, 0, 0,  412, 408, 1.68, 15,  475, 383, 5.76, 10,  623, 364, 0.96, 16,  672, 379, 5.04, 11,  -1, -1, 0, 0,  805, 346, 4.32, 12,  920, 378, 8.40, 18,  1004, 351, 3.60, 13,  1077, 349, 7.68, 19,  -1, -1, 0, 0,
	243, 427, 0.96, 12,  350, 447, 5.04, 18,  433, 420, 0.24, 13,  -1, -1, 0, 0,  616, 476, 8.40, 14,  654, 426, 3.60, 20,  764, 485, 7.68, 15,  868, 459, 2.88, 10,  -1, -1, 0, 0,  989, 447, 2.16, 11,  1096, 464, 6.24, 17,  1187, 429, 1.44, 12,
	-1, -1, 0, 0,  326, 538, 3.60, 16,  401, 527, 7.68, 11,  541, 570, 2.88, 17,  -1, -1, 0, 0,  -1, -1, 0, 0,  736, 530, 6.24, 13,  859, 547, 1.44, 19,  -1, -1, 0, 0,  1008, 523, 0.72, 20,  -1, -1, 0, 0,  1143, 547, 0.00, 10,
]
# Lightning inside the green cloud: start (loop seconds), x, y on the starfield, shape.
const DISCHARGES := [[8.6, 1092.0, 217.0, 0], [33.2, 1000.0, 262.0, 1], [55.1, 917.0, 302.0, 2], [82.3, 1093.0, 216.0, 2], [103.0, 1002.0, 261.0, 0], [113.4, 916.0, 301.0, 1]]
const SPINE := [Vector2(-20, 9), Vector2(-15, 6), Vector2(-13, 7), Vector2(-8, 3), Vector2(-5, 4), Vector2(-1, 0), Vector2(3, -1), Vector2(7, -1), Vector2(11, -5), Vector2(16, -5), Vector2(19, -8)]
# Shooting stars: start (negative during the approach), seconds, from x, y, travel x, y, tail, brightness.
const METEORS := [
	[-11.2, 0.85, 793.0, 91.0, -112.0, 34.0, 18.0, 0.92], [-3.7, 0.81, 481.0, 153.0, 74.0, 31.0, 13.0, 0.76],
	[5.2, 0.96, 495.0, 79.0, -86.0, 38.0, 17.0, 0.92], [18.2, 0.91, 734.0, 133.0, -103.0, 28.0, 15.0, 0.86],
	[33.6, 0.79, 443.0, 174.0, 85.0, 28.0, 13.0, 0.70], [48.1, 1.08, 927.0, 38.0, -118.0, 37.0, 20.0, 0.94],
	[62.7, 0.91, 671.0, 129.0, -103.0, 28.0, 15.0, 0.86], [78.4, 0.92, 555.0, 184.0, -101.0, 43.0, 17.0, 0.83],
	[91.6, 0.88, 417.0, 110.0, 90.0, 28.0, 15.0, 0.82], [102.4, 0.91, 877.0, 137.0, -103.0, 28.0, 15.0, 0.90],
	[115.0, 1.12, 539.0, 28.0, -123.0, 50.0, 21.0, 0.99],
]
# The five pairs of approach lights on the runway, in moon_base.png pixels.
const RUNWAY := [[Vector2(31, 212.5), Vector2(114.5, 212.5)], [Vector2(65, 198), Vector2(132.5, 200)], [Vector2(92, 188), Vector2(152.5, 189.5)], [Vector2(111.5, 180.5), Vector2(166.5, 181.5)], [Vector2(128, 174.5), Vector2(177, 175.5)]]
# Drifting rocks: y, seconds to cross, phase, size, turns per loop.
const ROCKS := [[103.0, 120.0, 4.0, 2.2, 3.0], [463.0, 60.0, 22.0, 2.6, 4.0], [227.0, 120.0, 82.0, 1.55, 7.0], [330.0, 60.0, 14.0, 1.0, 5.0], [173.0, 120.0, 29.0, 3.7, 3.0], [407.0, 120.0, 71.0, 2.4, 4.0], [371.0, 120.0, 7.0, 1.4, 5.0]]
const ENGINE_PULSES := [-25.5, -22.9, -18.0, -12.1, -8.7, -4.2, 3.1, 11.0, 20.4, 31.7, 44.2, 53.8, 67.4, 81.3, 91.8, 106.8, 116.1]
const SPARK_BURSTS := [-24.2, -21.0, -16.1, -9.7, -3.8, 4.8, 14.6, 27.2, 43.7, 60.1, 77.0, 89.6, 105.0, 114.3]
const CLOUD_STARTS := [5.0, 27.0, 51.0, 77.0, 98.0, 109.0]
# The easter egg. Points on the fighter are in fighter.png pixels; SPRITE_TO_MODEL turns them into scene.cpp's
# 260x174 fighter space. Middle of the panel that breaks off and of the cut, from tools/dev/title_wing_mask.py.
const SPRITE_TO_MODEL := Vector2(260.0 / 72.0, 174.0 / 49.0)
const DAMAGED_TIP := Vector2(50.01, 35.36)
const WING_MIDDLE := Vector2(11.27, 11.17)
const WING_ROOT := Vector2(16.77, 14.27)
const POKES_TO_BREAK := 3
const CUT_BURSTS := [1.9, 9.3, 17.0, 24.6, 33.1, 41.0, 50.2, 58.7, 66.3, 75.8, 84.0, 93.5, 101.2, 110.6]

var _sky: ShaderMaterial
var _fx_sky: ShaderMaterial
var _sun: ShaderMaterial
var _planet: ShaderMaterial
var _moon: ShaderMaterial
var _fx_moon: ShaderMaterial
var _fighter: ShaderMaterial
var _fx_sparks: ShaderMaterial
var _wing_piece: ShaderMaterial
var _wing_layer: ColorRect
var _last_layer: ColorRect
var _ship_image: Image
var _wing_image: Image
var _now := 0.0                          # the time last shown
var _pose_centre := Vector2.ZERO         # the fighter as last drawn, for clicks
var _pose_scale := 1.0
var _pose_rot := Vector2(1.0, 0.0)       # cos, sin
var _poked := 0
var _pokes: Array = []                   # recent clicks: time, point (fighter space), push direction, push
var _wing_off := -1.0                    # when the wing came off; -1 while it's on
var _wing_start := Vector2.ZERO
var _wing_dir := Vector2.ZERO
var _wing_angle := 0.0
var _wing_scale := 0.535
var _radius := 369.0                     # half the planet's width
# Soft dots, lines and glows for one prims layer, filled each frame (see shaders/title/prims.gdshader).
var _shape := PackedColorArray()
var _extra := PackedColorArray()
var _tint := PackedColorArray()


func _init() -> void:
	size = CANVAS
	disable_3d = true
	transparent_bg = false
	render_target_update_mode = SubViewport.UPDATE_ALWAYS
	canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST


func _ready() -> void:
	_sky = _layer("sky", {"sky_tex": "starfield", "mask_tex": "nebula_light"})
	var stars := PackedColorArray()
	for i in range(0, STARS.size(), 4):
		stars.append(Color(float(STARS[i]), float(STARS[i + 1]), float(STARS[i + 2]), float(STARS[i + 3])))
	_sky.set_shader_parameter("stars", stars)
	_fx_sky = _layer("prims", {})
	_sun = _layer("sun", {})
	_planet = _layer("planet", {"world_tex": "planet"})
	var world: Texture2D = _planet.get_shader_parameter("world_tex")
	if world != null:
		_radius = world.get_width() * 0.5
	_moon = _layer("moon", {"moon_tex": "moon_base"})
	_fx_moon = _layer("prims", {})
	_wing_piece = _layer("fighter", {"ship_tex": "fighter", "wing_tex": "fighter_wing"})
	_wing_piece.set_shader_parameter("part", 2)
	_wing_layer = _last_layer
	_wing_layer.visible = false
	_fighter = _layer("fighter", {"ship_tex": "fighter", "wing_tex": "fighter_wing"})
	_fighter.set_shader_parameter("part", 0)
	_fx_sparks = _layer("prims", {})
	var ship: Texture2D = _fighter.get_shader_parameter("ship_tex")
	var wing: Texture2D = _fighter.get_shader_parameter("wing_tex")
	if ship != null:
		_ship_image = ship.get_image()
	if wing != null:
		_wing_image = wing.get_image()
	show_time(0.0)


func _layer(shader_name: String, textures: Dictionary) -> ShaderMaterial:
	var rect := ColorRect.new()
	rect.position = Vector2.ZERO
	rect.size = Vector2(CANVAS)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var material := ShaderMaterial.new()
	material.shader = load(SHADERS + shader_name + ".gdshader")
	for uniform_name: String in textures:
		var path := ART + str(textures[uniform_name]) + ".png"
		if ResourceLoader.exists(path):
			material.set_shader_parameter(uniform_name, load(path))
	rect.material = material
	add_child(rect)
	_last_layer = rect
	return material


func show_time(time: float) -> void:
	_now = time
	var t := time
	if t >= INTRO + LOOP:
		t = INTRO + fposmod(t - INTRO, LOOP)
	var u := t - INTRO
	if u >= 0.0:
		u = fposmod(u, LOOP)
	# The camera accelerates for four seconds, crosses at a steady speed and brakes to a stop at 26 s.
	var travel := clampf(t - 8.0, 0.0, 18.0)
	var p: float
	if travel < 4.0:
		p = 4.0 * _ramp(travel / 4.0) / 14.0
	elif travel <= 14.0:
		p = (travel - 2.0) / 14.0
	else:
		p = 1.0 - 4.0 * _ramp((18.0 - travel) / 4.0) / 14.0
	var cx := lerpf(215.0, -34.0, p)
	var cy := lerpf(237.0, 202.0, p)
	var settled := t >= INTRO
	var show := smoothstep(5.0, 14.0, t)
	var sky_at := Vector2(lerpf(105.0, 205.0, p), lerpf(23.0, 31.0, p))
	var power := _cloud_activity(u)

	_sky.set_shader_parameter("offset", sky_at)
	_sky.set_shader_parameter("settled", settled)
	_sky.set_shader_parameter("vis", 0.035 + 0.965 * smoothstep(4.1, 13.6, t))
	_sky.set_shader_parameter("power", power)
	_sky.set_shader_parameter("u", u)
	_sky.set_shader_parameter("show", show)

	_prims_begin()
	if show > 0.0:
		_add_lightning(u, show, sky_at)
		_add_meteors(u, show)
	_prims_end(_fx_sky)

	_set_sun(u, t, cx, cy)

	_planet.set_shader_parameter("corner", Vector2(cx - _radius, cy - _radius))
	_planet.set_shader_parameter("turn", Vector3(0.66 * sin(TAU * u / 60.0 + 0.3), -0.71 * sin(TAU * u / 60.0 - 1.1), 0.77 * sin(TAU * u / 40.0 + 0.46)))
	_planet.set_shader_parameter("zon", 10.4 * sin(TAU * u / 120.0 + 0.2))
	_planet.set_shader_parameter("lat", 2.3 * sin(TAU * u / 60.0 + 1.5))
	_planet.set_shader_parameter("t", t)
	_planet.set_shader_parameter("threshold", lerpf(1.4, -1.55, _ease((t - 4.5) / 9.1)))
	_planet.set_shader_parameter("day", t >= 13.6)

	var sx0 := lerpf(1018.0, 310.0, p)
	var my := lerpf(225.0, 108.0, p)
	_moon.set_shader_parameter("corner", Vector2(sx0 - 320.0, my))
	_moon.set_shader_parameter("settled", settled)
	_moon.set_shader_parameter("daylight", smoothstep(15.5, 23.8, t))

	_prims_begin()
	_add_lamps(u, t, sx0, my)
	_add_rocks(u, t, p)
	_prims_end(_fx_moon)

	_set_fighter(u, t, p)


func _ramp(v: float) -> float:
	return v * v * v * (1.0 - 0.5 * v)


func _ease(x: float) -> float:
	var k := clampf(x, 0.0, 1.0)
	return k * k * k * (k * (6.0 * k - 15.0) + 10.0)


# Light passes from one gas knot of the green cloud to the next; closes on the 120 s loop.
func _cloud_activity(u: float) -> Vector3:
	var phase := TAU * u / 120.0
	var power := [0.0, 0.0, 0.0]
	for i in 3:
		var slow := 0.5 + 0.5 * sin(phase * (i + 2) + i * 2.1)
		var amount := 0.06 + 0.13 * slow
		for j in 6:
			var rank: int = i if j % 2 == 0 else 2 - i
			var age := fposmod(u - float(CLOUD_STARTS[j]) - rank * 1.55, 120.0)
			var width := 6.4 + float(j % 3) * 0.85
			if age < width:
				var rise := smoothstep(0.0, 1.8, age)
				var fall := 1.0 - smoothstep(2.1, width, age)
				amount += (0.58 + 0.16 * float((i + j) % 3)) * rise * fall
		power[i] = amount
	return Vector3(power[0], power[1], power[2])


func _engine_light(u: float) -> float:
	var pulse := 0.0
	for i in ENGINE_PULSES.size():
		var life := 2.15 if i % 3 == 0 else 1.38
		var q := (u - float(ENGINE_PULSES[i])) / life
		if q >= 0.0 and q < 1.0:
			var envelope := smoothstep(0.0, 0.24, q) * (1.0 - smoothstep(0.39, 1.0, q))
			var tremble := 0.89 + 0.085 * sin(11.0 * q + 0.5) + 0.035 * sin(24.0 * q)
			pulse = maxf(pulse, envelope * tremble * (0.7 + 0.12 * float(i % 3)))
	return 0.065 + 0.025 * sin(TAU * u / 8.0) + pulse


# New arrays each time: a material keeps a reference to the array it was given, not a copy.
func _prims_begin() -> void:
	_shape = PackedColorArray()
	_extra = PackedColorArray()
	_tint = PackedColorArray()


func _prims_end(material: ShaderMaterial) -> void:
	var count := mini(_shape.size(), MAX_PRIMS)
	_shape.resize(MAX_PRIMS)
	_extra.resize(MAX_PRIMS)
	_tint.resize(MAX_PRIMS)
	material.set_shader_parameter("count", count)
	material.set_shader_parameter("shape", _shape)
	material.set_shader_parameter("extra", _extra)
	material.set_shader_parameter("tint", _tint)


func _dot(at: Vector2, radius: float, colour: Color, alpha: float) -> void:
	if alpha > 0.0:
		_shape.append(Color(0.0, at.x, at.y, 0.0))
		_extra.append(Color(0.0, radius, 0.0, alpha))
		_tint.append(colour)


func _line(p0: Vector2, p1: Vector2, radius: float, colour: Color, alpha: float) -> void:
	if alpha > 0.0:
		_shape.append(Color(1.0, p0.x, p0.y, p1.x))
		_extra.append(Color(p1.y, radius, 0.0, alpha))
		_tint.append(colour)


func _glow(at: Vector2, radii: Vector2, colour: Color, alpha: float) -> void:
	if alpha >= 0.002:
		_shape.append(Color(2.0, at.x, at.y, 0.0))
		_extra.append(Color(0.0, radii.x, radii.y, alpha))
		_tint.append(colour)


func _add_lightning(u: float, show: float, sky_at: Vector2) -> void:
	for arc: Array in DISCHARGES:
		var age := fposmod(u - float(arc[0]), 120.0)
		if age >= 2.85:
			continue
		var power := smoothstep(0.0, 0.66, age) * (1.0 - smoothstep(0.81, 2.85, age)) * show
		var at := Vector2(float(arc[1]), float(arc[2])) - sky_at
		var off := float(arc[3]) * 2.03
		var previous: Vector2 = at + SPINE[0] + Vector2(0.0, 1.2 * sin(off))
		for i in range(1, 11):
			var point: Vector2 = at + SPINE[i] + Vector2(0.0, 1.2 * sin(1.1 * i + off))
			var lit := power * smoothstep(0.04, 0.94, age + 0.46 - 0.052 * i)
			_line(previous, point, 1.5, Color8(72, 174, 125), lit * 0.15)
			_line(previous, point, 0.46, Color8(161, 225, 181), lit * 0.76)
			previous = point
		_line(at + Vector2(-5.0, 4.0), at + Vector2(-1.0, 7.0), 0.44, Color8(111, 202, 149), power * 0.59)
		_line(at + Vector2(-1.0, 7.0), at + Vector2(5.0, 6.5), 0.40, Color8(111, 202, 149), power * 0.46)


func _add_meteors(u: float, show: float) -> void:
	for m: Array in METEORS:
		var q := (u - float(m[0])) / float(m[1])
		if q <= 0.0 or q >= 1.0:
			continue
		var travel := Vector2(float(m[4]), float(m[5]))
		var head := Vector2(float(m[2]), float(m[3])) + q * travel
		var tail := float(m[6]) * (0.55 + 0.45 * smoothstep(0.0, 0.25, q))
		var back := -travel * tail / travel.length()
		var light := show * float(m[7]) * smoothstep(0.0, 0.22, q) * (1.0 - smoothstep(0.6, 1.0, q))
		for i in range(5, -1, -1):
			var a := i / 6.0
			var b := (i + 1) / 6.0
			_line(head + a * back, head + b * back, 0.49 - 0.22 * a, Color8(157, 190, 215), light * (1.0 - a) * (1.0 - a))
		_dot(head, 0.66, Color8(224, 235, 240), light)


func _set_sun(u: float, t: float, cx: float, cy: float) -> void:
	var lift := lerpf(-31.0, 36.0, _ease((t - 3.6) / 8.4))
	var at := Vector2(cx + (_radius + lift) * 0.9156, cy + (_radius + lift) * -0.4020)
	var vis := smoothstep(3.2, 8.0, t)
	var phase := TAU * u / 120.0
	var prom := PackedColorArray()
	var prom_tint := PackedColorArray()
	for j in 2:
		var base := (-1.1 if j == 0 else 0.40) + 0.12 * sin(phase * (2 + j) + j)
		var previous := Vector2.ZERO
		for i in 18:
			var v := i / 17.0
			var bow := sin(PI * v)
			var angle := base + v * (0.55 + 0.09 * sin(phase * 3.0 + j))
			var activity := 0.5 + 0.5 * sin(phase * 4.0 + j * 2.6)
			var height := (4.0 if j == 1 else 6.7) * (0.22 + 0.78 * activity)
			var r := 15.6 - 0.65 + height * bow * (0.83 + 0.17 * sin(TAU * v + phase * 3.0))
			var point := at + r * Vector2(cos(angle), sin(angle))
			if i > 0:
				prom.append(Color(previous.x, previous.y, point.x, point.y))
				prom_tint.append(Color(1.0, (168.0 + 35.0 * bow) / 255.0, 93.0 / 255.0, vis * (0.33 + 0.47 * activity)))
			previous = point
	_sun.set_shader_parameter("centre", at)
	_sun.set_shader_parameter("vis", vis)
	_sun.set_shader_parameter("phase", phase)
	_sun.set_shader_parameter("prom", prom)
	_sun.set_shader_parameter("prom_tint", prom_tint)


func _add_lamps(u: float, t: float, sx0: float, my: float) -> void:
	var lamp := pow(maxf(0.0, cos(TAU * u / 6.0)), 4.0) * smoothstep(16.0, 23.0, t)
	var beacon := Vector2(sx0 + 532.0, my + 50.0)
	_glow(beacon, Vector2(5.5, 5.5), Color8(252, 115, 68), lamp * 0.45)
	_dot(beacon, 1.25, Color8(255, 218, 144), lamp * 0.86)
	var visibility := smoothstep(14.0, 22.0, t)
	for i in 5:
		var elapsed := fposmod(u + 0.4 - 0.54 * i, 5.0)
		var light := pow(sin(PI * clampf(elapsed / 1.55, 0.0, 1.0)), 2.0) * visibility
		for spot: Vector2 in RUNWAY[i]:
			var at := Vector2(sx0 + 2.0 * (spot.x + 0.5), my + 2.0 * (spot.y + 0.5))
			_glow(at, Vector2(10.0 - i * 0.8, 4.5), Color8(255, 164, 66), light * 0.51)
			_line(at + Vector2(-3.7 + i * 0.45, 0.0), at + Vector2(3.7 - i * 0.45, -0.3), 0.86, Color8(255, 243, 178), light * 0.91)


func _add_rocks(u: float, t: float, p: float) -> void:
	var vis := 0.12 + 0.88 * smoothstep(4.0, 14.0, t)
	for rock: Array in ROCKS:
		var crossing := float(rock[1])
		var phase := float(rock[2])
		var r := float(rock[3])
		var q := fposmod(u + phase, crossing) / crossing
		var x := CANVAS.x + 60.0 - (CANVAS.x + 120.0) * q + (1.0 - p) * 45.0
		var y := float(rock[0]) + 11.0 * (q - 0.5) + sin(TAU * u / 40.0 + phase) * 3.0
		var angle := TAU * float(rock[4]) * u / 120.0 + phase
		var d := r * Vector2(cos(angle), sin(angle))
		var at := Vector2(x, y)
		_line(at - d * 0.78, at + d, r * 0.42, Color8(55, 60, 80), vis)
		_line(at - d * 0.78 - Vector2(0.0, r * 0.35), at + d * 0.28 - Vector2(0.0, r * 0.35), 0.65, Color8(130, 129, 142), vis * 0.8)


func _set_fighter(u: float, t: float, p: float) -> void:
	var a := TAU * u / 120.0
	var centre := Vector2(lerpf(535.0, 310.0, p) + 5.8 * sin(2.0 * a + 0.5) + (1.0 - p) * 4.9 * sin(t * 0.47),
			lerpf(267.0, 328.0, p) + 6.2 * sin(3.0 * a - 0.85) + (1.0 - p) * 2.6 * sin(t * 0.4 + 0.6))
	var scale := lerpf(1.0, 0.535, p)
	var angle := (lerpf(-7.0, 6.0, p) + 4.9 * sin(a * 2.0 + 0.1) + (1.0 - p) * 3.1 * sin(t * 0.36)) * 0.0174532925
	# A click shoves the ship: a quick wobble away from where it was touched.
	for poke_entry: Array in _pokes:
		var since := _now - float(poke_entry[0])
		if since >= 0.0 and since < 1.5:
			var wobble := exp(-4.5 * since) * sin(16.0 * since)
			var push: Vector2 = poke_entry[2]
			centre += push * float(poke_entry[3]) * wobble
			angle += 0.018 * float(poke_entry[3]) * wobble
	var c := cos(angle)
	var s := sin(angle)
	_pose_centre = centre
	_pose_scale = scale
	_pose_rot = Vector2(c, s)
	var f := _engine_light(u)
	var ambient := lerpf(0.49, 1.0, smoothstep(4.4, 11.8, t))
	_fighter.set_shader_parameter("centre", centre)
	_fighter.set_shader_parameter("scale", scale)
	_fighter.set_shader_parameter("rot", Vector2(c, s))
	_fighter.set_shader_parameter("engines", Vector2(f, _engine_light(u - 0.23) * (0.83 + 0.09 * sin(a * 3.0 + 1.6))))
	_fighter.set_shader_parameter("ambient", ambient)
	_fighter.set_shader_parameter("plume_len", 12.0 + 28.0 * f)
	_fighter.set_shader_parameter("sway", sin(TAU * u / 6.0) * 1.15 + sin(TAU * u / 2.5) * 0.48)
	_fighter.set_shader_parameter("part", 1 if _wing_off >= 0.0 else 0)
	_set_wing_piece(ambient)
	_prims_begin()
	# Sparks from the cut edge of the damaged wing.
	var tip := _to_canvas(DAMAGED_TIP * SPRITE_TO_MODEL)
	for i in SPARK_BURSTS.size():
		_burst(tip, u - float(SPARK_BURSTS[i]), i, scale)
	# The easter egg's sparks: a spray where each click landed, and the damaged wing shaken loose a little.
	for poke_entry: Array in _pokes:
		var since := _now - float(poke_entry[0])
		var pick := int(poke_entry[4])
		_spray(_to_canvas(poke_entry[1]), since, pick, 9, 1.0)
		_burst(tip, since, 20 + pick, scale)
	if _wing_off >= 0.0:
		var root := _to_canvas(WING_ROOT * SPRITE_TO_MODEL)
		_spray(root, _now - _wing_off, 3, 16, 1.4)
		for i in CUT_BURSTS.size():
			_burst(root, u - float(CUT_BURSTS[i]), i + 7, scale)
	_prims_end(_fx_sparks)


# One burst of sparks from a cut edge (scene.cpp's wing sparks); `since` is the time since it started.
func _burst(tip: Vector2, since: float, i: int, scale: float) -> void:
	if since < 0.0 or since > 1.6:
		return
	for n in 5:
		var age := since - n * 0.049
		var life := 0.58 + 0.12 * float((i + n) % 5)
		if age <= 0.0 or age >= life:
			continue
		var dx := -15.0 + float((i * 5 + n * 11) % 32)
		var dy := 11.0 + float((n * 7 + i * 3) % 22)
		var k := age / life
		var at := tip + Vector2(dx * age * scale, (dy * age + 1.5 * age * age) * scale)
		_line(at, at - Vector2(dx, dy) * 0.039 * scale, 0.52 + 0.34 * scale, Color8(252, int(lerpf(205.0, 111.0, k)), int(lerpf(139.0, 66.0, k))), sin(PI * pow(k, 0.68)) * 0.94)


# A flash and hot sparks flying out all round from a point, for the easter egg.
func _spray(origin: Vector2, since: float, pick: int, count: int, reach: float) -> void:
	if since < 0.0 or since > 1.3:
		return
	if since < 0.2:
		var fade := 1.0 - since / 0.2
		_glow(origin, Vector2(9.0, 9.0) * reach, Color8(255, 226, 160), 0.85 * fade)
		_glow(origin, Vector2(4.0, 4.0) * reach, Color8(255, 250, 230), fade)
	for n: int in count:
		var age := since - n * 0.01
		var life := 0.45 + 0.08 * float((n + pick) % 4)
		if age <= 0.0 or age >= life:
			continue
		var heading := TAU * (float(n) + 0.37 * float(pick % 7)) / float(count)
		var speed := (38.0 + 8.0 * float((n * 7 + pick) % 5)) * reach
		var dir := Vector2(cos(heading), sin(heading))
		var k := age / life
		var at := origin + dir * speed * age + Vector2(0.0, 12.0 * age * age)
		_line(at, at - dir * speed * 0.06, 0.8, Color8(255, int(lerpf(245.0, 140.0, k)), int(lerpf(205.0, 60.0, k))), sin(PI * pow(k, 0.5)) * 0.97)


# The broken-off panel drifts away from the ship, tumbling, until it leaves the picture.
func _set_wing_piece(ambient: float) -> void:
	if _wing_off < 0.0:
		_wing_layer.visible = false
		return
	var since := _now - _wing_off
	var at := _wing_start + _wing_dir * (12.0 * (1.0 - exp(-3.0 * since)) + 16.0 * since)
	var turn := _wing_angle - 0.5 * (1.0 - exp(-2.0 * since)) - 0.4 * since
	var c := cos(turn)
	var s := sin(turn)
	var d := (WING_MIDDLE * SPRITE_TO_MODEL - Vector2(130.0, 87.0)) * _wing_scale
	_wing_layer.visible = Rect2(-200.0, -200.0, CANVAS.x + 400.0, CANVAS.y + 400.0).has_point(at)
	_wing_piece.set_shader_parameter("centre", at - Vector2(c * d.x + s * d.y, -s * d.x + c * d.y))
	_wing_piece.set_shader_parameter("scale", _wing_scale)
	_wing_piece.set_shader_parameter("rot", Vector2(c, s))
	_wing_piece.set_shader_parameter("engines", Vector2.ZERO)
	_wing_piece.set_shader_parameter("ambient", ambient)
	_wing_piece.set_shader_parameter("plume_len", 0.0)
	_wing_piece.set_shader_parameter("sway", 0.0)


# A point in the fighter's 260x174 space, on the canvas, as the ship was last drawn.
func _to_canvas(point: Vector2) -> Vector2:
	var d := (point - Vector2(130.0, 87.0)) * _pose_scale
	return _pose_centre + Vector2(_pose_rot.x * d.x + _pose_rot.y * d.y, -_pose_rot.y * d.x + _pose_rot.x * d.y)


func _to_fighter(at: Vector2) -> Vector2:
	var o := (at - _pose_centre) / _pose_scale
	return Vector2(130.0 + _pose_rot.x * o.x - _pose_rot.y * o.y, 87.0 + _pose_rot.y * o.x + _pose_rot.x * o.y)


# title_screen.gd: a click at this point of the 960x540 canvas. True when it hit the ship, which then sparks;
# the third hit breaks the wing at its orange stripe.
func poke(at: Vector2) -> bool:
	if _ship_image == null or not _hits_ship(at):
		return false
	var recent: Array = []
	for poke_entry: Array in _pokes:
		if _now - float(poke_entry[0]) < 2.0:
			recent.append(poke_entry)
	_pokes = recent
	_poked += 1
	var push := (_pose_centre - at).normalized()
	var strength := 2.2
	if _poked == POKES_TO_BREAK and _wing_off < 0.0 and _wing_image != null:
		strength = 4.5
		_wing_off = _now
		_wing_scale = _pose_scale
		_wing_angle = atan2(_pose_rot.y, _pose_rot.x)
		_wing_start = _to_canvas(WING_MIDDLE * SPRITE_TO_MODEL)
		_wing_dir = (_wing_start - _to_canvas(WING_ROOT * SPRITE_TO_MODEL)).normalized()
	_pokes.append([_now, _to_fighter(at), push, strength, _poked])
	return true


# Within a pixel of the ship's own pixels (not the broken-off panel once it's gone).
func _hits_ship(at: Vector2) -> bool:
	var m := _to_fighter(at)
	var px := int(floor((m.x + 0.5) / SPRITE_TO_MODEL.x))
	var py := int(floor((m.y + 0.5) / SPRITE_TO_MODEL.y))
	for dy: int in [-1, 0, 1]:
		for dx: int in [-1, 0, 1]:
			var x := px + dx
			var y := py + dy
			if x < 0 or y < 0 or x >= _ship_image.get_width() or y >= _ship_image.get_height():
				continue
			if _ship_image.get_pixel(x, y).a < 0.5:
				continue
			if _wing_off >= 0.0 and _wing_image != null and _wing_image.get_pixel(x, y).r >= 0.5:
				continue
			return true
	return false
