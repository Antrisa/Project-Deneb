extends CanvasLayer
# The jump map (21 Nov 2026): a big circle round Echo Landing, five rings out into the neutral zone, split into
# four zones of control (Terran, Zaa'sh, Collective, and the Rabble's Reach). Drawn on the Terran field datapad
# (ui/ship_screen.gd): the map in the scope on the left, the next stop and your ship's stores on the right.
# Mock-up: datapad_map_x2.png in the Drive folder.
#
# This first version shows a locked route (the first flight, ShipData.FIRST_FLIGHT): only the next stop can be
# jumped to. The other stops on the rings are drawn greyed out; free ship runs with daily stops come in slice 2.
# main.gd opens it with open_route() and gets on_jump.call(index) when the ship arrives at a stop; main.gd runs
# that stop (dialogue, a fight) and the map waits.

const ShipData = preload("res://scripts/ship_data.gd")
const ShipScreen = preload("res://ui/ship_screen.gd")

# The page fills the window (Zachary, 22 Nov), so the map's scope, its middle and its scale are worked out each
# frame (_layout): the circle grows with the scope. RING radii are at zoom 1, the 420 x 330 scope of the old page.
var MAP_WIN := Rect2(53, 52, 420, 330)
var CENTER := Vector2(263, 217)
var zoom := 1.0
const RING := [0.0, 30.0, 60.0, 90.0, 120.0, 150.0]   # radius of each ring; ring 0 is the Landing
const MOVE_TIME := 0.9
const INK := Color("373b36")          # as ui/ship_screen.gd
const MUTED := Color("595e55")          # as ui/ship_screen.gd
const GOLD := Color("fadc5a")
const NAME_ON_MAP := Color("f0e6d0")
const KEY_KINDS := ["beacon", "distress", "store", "special"]

var world                          # main.gd
var open := false
var route: Array = []
var at := -1                       # the stop the ship is at; -1 is the Landing
var show_route := true             # false while S.A.R.A. is still asking for help
var title := ""
var on_jump: Callable = Callable()
var moving := 0.0                  # 0..1 while the ship travels to the next stop
var move_index := -1
var screen: ShipScreen
var dots: Array = []               # the other stops on the rings: [position, kind]
var pulse := 0.0


func _ready() -> void:
	layer = 9
	visible = false
	screen = ShipScreen.new()
	add_child(screen)
	screen.fill = true
	screen.paint = Callable(self, "_paint")
	screen.on_click = Callable(self, "_click")
	# The rest of the rings, for show (greyed out on the first flight).
	var rng := RandomNumberGenerator.new()
	rng.seed = 21
	# Mostly ordinary beacons, some distress signals, a few stores, and the odd special sector.
	var mix: Array = ["beacon", "beacon", "beacon", "beacon", "beacon", "beacon", "distress", "distress", "store", "special"]
	for ring in range(1, RING.size()):
		var n: int = ShipData.RING_STOPS[ring]
		var turn: float = rng.randf() * 360.0 / n
		for k in range(n):
			var ang: float = turn + k * 360.0 / n + rng.randf_range(-6.0, 6.0)
			var r: float = RING[ring] + rng.randf_range(-4.0, 4.0)
			dots.append([Vector2(cos(deg_to_rad(ang)), sin(deg_to_rad(ang))) * r, mix[rng.randi() % mix.size()]])


func _zone_index(ang: float) -> int:
	var a: float = fposmod(ang, 360.0)
	if a >= 225.0 and a < 315.0: return 0
	if a >= 315.0 or a < 45.0: return 1
	if a < 135.0: return 2
	return 3


# Show the map with a route. index: the stop the ship is at (-1 = just left the Landing).
func open_route(new_route: Array, index: int, cb: Callable, reveal: bool = true, heading: String = "") -> void:
	route = new_route
	at = index
	on_jump = cb
	show_route = reveal
	title = heading
	moving = 0.0
	open = true
	visible = true
	screen.redraw()


func close() -> void:
	open = false
	visible = false
	on_jump = Callable()


func stop_pos(i: int) -> Vector2:
	if i < 0 or i >= route.size():
		return CENTER
	var s: Dictionary = route[i]
	var a: float = deg_to_rad(float(s["angle"]))
	return CENTER + Vector2(cos(a), sin(a)) * float(RING[int(s["ring"])]) * zoom


func next_index() -> int:
	return at + 1 if at + 1 < route.size() else -1


func can_jump() -> bool:
	return open and visible and show_route and moving == 0.0 and next_index() >= 0 and not world.dialogue.active


func jump() -> void:
	if not can_jump():
		return
	if int(world.fuel) <= 0:
		world.sfx("deny")
		world._toast("Out of fuel")
		return
	move_index = next_index()
	moving = 0.001
	world.sfx("warp", 1.2, -4.0)


func _process(delta: float) -> void:
	if not open:
		return
	pulse += delta
	if moving > 0.0:
		moving += delta / MOVE_TIME
		if moving >= 1.0:
			moving = 0.0
			at = move_index
			var cb: Callable = on_jump
			if cb.is_valid():
				cb.call(at)
	if open and visible:
		screen.redraw()


func handle_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact") or event.is_action_pressed("use"):
		jump()


func _click(id: String, _p: Vector2, button: int) -> void:
	if button != MOUSE_BUTTON_LEFT:
		return
	if world.dialogue.active:
		world.dialogue.advance()
		return
	if id == "jump" or id == "stop":
		jump()


# ---------------------------------------------------------------- drawing

func _wedge(from_deg: float, to_deg: float, radius: float, color: Color) -> void:
	var pts := PackedVector2Array([CENTER])
	var steps := 24
	for i in range(steps + 1):
		var a: float = deg_to_rad(lerpf(from_deg, to_deg, float(i) / steps))
		pts.append(CENTER + Vector2(cos(a), sin(a)) * radius)
	screen.polygon(pts, color)


func _layout() -> void:
	var pg: Vector2 = screen.page
	MAP_WIN = Rect2(12, 46, pg.x - 24.0 - 241.0, pg.y - 96.0)
	CENTER = MAP_WIN.get_center().round()
	zoom = minf(MAP_WIN.size.x / 420.0, MAP_WIN.size.y / 330.0)


func _paint() -> void:
	var s := screen
	_layout()
	s.case_fill("Jump map")
	s.scope(MAP_WIN, 3)
	var outer: float = (RING[RING.size() - 1] + 7.0) * zoom
	for z in ShipData.ZONES:
		_wedge(float(z["from"]), float(z["to"]), outer, Color(z["color"], 0.72))
	s.circle(CENTER, (RING[1] + 7.0) * zoom, Color("3d4946"))
	for r in RING:
		if r > 0.0:
			s.ring(CENTER, r * zoom, Color(0.54, 0.6, 0.55, 0.55))
	for z in ShipData.ZONES:
		var mid: float = deg_to_rad((float(z["from"]) + float(z["to"])) / 2.0)
		var rim: Vector2 = CENTER + Vector2(cos(mid), sin(mid)) * (outer - 12.0)
		var label: String = str(z["name"]).to_upper()
		var half: float = s.width(label, "micro") / 2.0
		var x: float = clampf(rim.x, MAP_WIN.position.x + 10.0 + half, MAP_WIN.end.x - 10.0 - half)
		s.text_center(x, rim.y - 6.0, label, "micro", z["text"])
	# the other stops: not on this route
	for d in dots:
		var p: Vector2 = CENTER + (d[0] as Vector2) * zoom
		var near := false
		for i in range(route.size()):
			if stop_pos(i).distance_to(p) < 12.0:
				near = true
		if not near:
			s.circle(p, 2.5, Color(0.42, 0.46, 0.45))
	# the Landing
	s.circle(CENTER, 8.0, Color("64b4ff"))
	s.ring(CENTER, 8.0, Color("f0f0f0"))
	s.text_center(CENTER.x, CENTER.y - 8.0, "EL", "micro", Color("14203c"))
	var n: int = next_index()
	if show_route:
		var prev: Vector2 = CENTER
		for i in range(route.size()):
			var here: Vector2 = stop_pos(i)
			var done: bool = i <= at
			s.line(prev, here, GOLD if done else Color(0.98, 0.86, 0.35, 0.45), 2.0 if done else 1.0)
			prev = here
		for i in range(route.size()):
			var stop: Dictionary = route[i]
			var kind: Dictionary = ShipData.STOP_KINDS[stop["kind"]]
			var here: Vector2 = stop_pos(i)
			var rad: float = 6.0 if str(stop["kind"]) == "special" else 5.0
			s.circle(here, rad, kind["color"] if i > at else Color(kind["color"]).darkened(0.4))
			s.ring(here, rad, Color("20262a"))
			if i == n and moving == 0.0:
				s.ring(here, rad + 3.0 + sin(pulse * 5.0), GOLD, 1.5)
				s.hit("stop", Rect2(here - Vector2(10, 10), Vector2(20, 20)))
				if s.hovering(Rect2(here - Vector2(10, 10), Vector2(20, 20))) and can_jump():
					s.ring(here, rad + 6.0, Color("fff6ea"))
			s.text_center(here.x, here.y - rad - 13.0, str(stop["name"]).to_upper(), "micro", NAME_ON_MAP if i > at else Color("8f9c8a"))
	# your ship
	var ship: Vector2 = stop_pos(at)
	if moving > 0.0:
		ship = stop_pos(at).lerp(stop_pos(move_index), clampf(moving, 0.0, 1.0))
	var facing: Vector2 = (stop_pos(n) - ship).normalized() if n >= 0 else Vector2.RIGHT
	if facing == Vector2.ZERO:
		facing = Vector2.RIGHT
	var side := Vector2(-facing.y, facing.x)
	s.polygon(PackedVector2Array([ship + facing * 8.0, ship - facing * 5.0 + side * 5.0, ship - facing * 5.0 - side * 5.0]), Color("ff8c28"))
	_paint_side(n)


func _paint_side(n: int) -> void:
	var s := screen
	s.shift(Vector2(s.page.x - 12.0 - 715.0, -6.0))   # the side column, as designed, against the right edge
	# the next stop
	var box := Rect2(480, 52, 235, 120)
	s.panel(box, "map", "Next stop")
	if show_route and n >= 0:
		var stop: Dictionary = route[n]
		var kind: Dictionary = ShipData.STOP_KINDS[stop["kind"]]
		s.text_fit(488, 78, 219, str(stop["name"]), "mid", INK)
		s.circle(Vector2(491.5, 106.5), 3.5, kind["color"])
		s.ring(Vector2(491.5, 106.5), 3.5, Color("20262a"))
		var zone: Dictionary = ShipData.ZONES[_zone_index(float(stop["angle"]))]
		s.text_fit(499, 102, 208, "%s, %s, RING %d" % [str(kind["label"]).to_upper(), str(zone["name"]).to_upper(), int(stop["ring"])], "micro", MUTED)
		var lines: Array = s.wrap_lines(str(stop["about"]), 219, "label")
		for i in range(mini(3, lines.size())):
			s.text(488, 117 + i * 15, lines[i], "label", INK)
	elif not show_route:
		s.text(488, 80, "Listening...", "label", MUTED)
	else:
		s.text(488, 80, "Journey's end.", "label", MUTED)
	# your ship's stores, and the key
	var ship_box := Rect2(480, 176, 235, 110)
	s.panel(ship_box, "bolt", "Ship")
	var full: int = int(ShipData.STARTER["hull"])
	s.text(488, 203, "FUEL %d" % int(world.fuel), "micro", INK if int(world.fuel) > 0 else ShipScreen.PIP_RED)
	s.text(600, 203, "HULL %d / %d" % [int(world.ship_hull), full], "micro", INK if int(world.ship_hull) * 3 > full else ShipScreen.PIP_RED)
	s.text(488, 217, "MISSILES %d" % int(world.missiles), "micro", INK)
	s.text(600, 217, "PARTS %d" % int(world.drone_parts), "micro", INK)
	s.text(488, 231, "SCRIP %d" % int(world.credits), "micro", INK)
	for i in range(KEY_KINDS.size()):
		var kind2: Dictionary = ShipData.STOP_KINDS[KEY_KINDS[i]]
		var x: float = 488.0 + (i % 2) * 110.0
		var y: float = 252.0 + floorf(i / 2.0) * 14.0
		s.circle(Vector2(x + 3.5, y + 5.5), 3.5, kind2["color"])
		s.ring(Vector2(x + 3.5, y + 5.5), 3.5, Color("20262a"))
		s.text(x + 11, y + 1, str(kind2["label"]), "micro", MUTED)
	# the buttons
	var can: bool = can_jump()
	s.button("jump", Rect2(480, 292, 115, 26), "Jump (1 fuel)", can, "label", can)
	s.button("fold", Rect2(600, 292, 115, 26), "Fold home", false, "label", false)
	# the flight
	var flight := Rect2(480, 324, 235, 58)
	s.panel(flight, "mark", title if title != "" else "Free flight")
	if route.size() > 0:
		s.text(488, 352, "STOP %d OF %d" % [clampi(at + 1, 0, route.size()), route.size()], "micro", MUTED)
		s.pips(560, 352, route.size(), at + 1, 9.0, 7.0, 3.0)
	var hint := "Pick the stop with the gold ring, or press E, to jump to it."
	if not show_route:
		hint = "S.A.R.A. is calling."
	elif n < 0:
		hint = "The route is done."
	elif moving > 0.0:
		hint = "Jumping..."
	if title != "":
		hint += "   Fold home: not on this flight."
	s.shift(s.bottom_left())
	s.status(hint)
	s.shift(s.bottom_right())
	s.solid_button("jump", Rect2(625, 388, 82, 22), "Jump", can)
	s.shift(Vector2.ZERO)
