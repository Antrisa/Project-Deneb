extends CanvasLayer
# The jump map (21 Nov 2026): a big circle round Echo Landing, five rings out into the neutral zone, split into
# four zones of control (Terran, Zaa'sh, Collective, and the Rabble's Reach). Mock-up: ftl_zones_map_mockup.png.
#
# This first version shows a locked route (the first flight, ShipData.FIRST_FLIGHT): only the next stop can be
# jumped to. The other stops on the rings are drawn greyed out; free ship runs with daily stops come in slice 2.
# main.gd opens it with open_route() and gets on_jump.call(index) when the ship arrives at a stop; main.gd runs
# that stop (dialogue, a fight) and the map waits. Laid out for 320x180, drawn at 2x.

const ShipData = preload("res://scripts/ship_data.gd")

const W := 320.0
const H := 180.0
const CENTER := Vector2(100, 92)
const RING := [0.0, 18.0, 34.0, 50.0, 66.0, 82.0]   # radius of each ring; ring 0 is the Landing
const MOVE_TIME := 0.9
const WHITE := Color("ececf0")
const DIM := Color("969cb0")
const GOLD := Color("fadc5a")
const PANEL := Color(0.08, 0.09, 0.16, 0.94)

var world                          # main.gd
var open := false
var route: Array = []
var at := -1                       # the stop the ship is at; -1 is the Landing
var show_route := true             # false while S.A.R.A. is still asking for help
var title := ""
var on_jump: Callable = Callable()
var moving := 0.0                  # 0..1 while the ship travels to the next stop
var move_index := -1
var view: Control
var font: Font
var dots: Array = []               # the other stops on the rings: [position, kind]
var hover := Vector2(-99, -99)
var pulse := 0.0


func _ready() -> void:
	layer = 9
	scale = Vector2(2, 2)
	visible = false
	view = Control.new()
	view.size = Vector2(W, H)
	view.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(view)
	view.draw.connect(_draw_view)
	view.gui_input.connect(_on_gui_input)
	font = view.get_theme_default_font()
	if font == null:
		font = ThemeDB.fallback_font
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
			var r: float = RING[ring] + rng.randf_range(-2.5, 2.5)
			dots.append([CENTER + Vector2(cos(deg_to_rad(ang)), sin(deg_to_rad(ang))) * r, mix[rng.randi() % mix.size()]])


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


func close() -> void:
	open = false
	visible = false
	on_jump = Callable()


func stop_pos(i: int) -> Vector2:
	if i < 0 or i >= route.size():
		return CENTER
	var s: Dictionary = route[i]
	var a: float = deg_to_rad(float(s["angle"]))
	return CENTER + Vector2(cos(a), sin(a)) * float(RING[int(s["ring"])])


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
	view.queue_redraw()
	if moving > 0.0:
		moving += delta / MOVE_TIME
		if moving >= 1.0:
			moving = 0.0
			at = move_index
			var cb: Callable = on_jump
			if cb.is_valid():
				cb.call(at)


func handle_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact") or event.is_action_pressed("use"):
		jump()


func _jump_rect() -> Rect2: return Rect2(202, 146, 112, 13)


func _on_gui_input(event: InputEvent) -> void:
	var motion := event as InputEventMouseMotion
	if motion != null:
		hover = motion.position
		return
	var click := event as InputEventMouseButton
	if click == null or not click.pressed or click.button_index != MOUSE_BUTTON_LEFT:
		return
	view.accept_event()
	if world.dialogue.active:
		world.dialogue.advance()
		return
	var n: int = next_index()
	if _jump_rect().has_point(click.position) or (n >= 0 and stop_pos(n).distance_to(click.position) <= 7.0):
		jump()


# ---------------------------------------------------------------- drawing

func _text(pos: Vector2, s: String, color: Color = WHITE, size: int = 8) -> void:
	view.draw_string(font, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)


func _text_c(x: float, y: float, s: String, color: Color = WHITE, size: int = 8) -> void:
	var w: float = font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	_text(Vector2(x - w / 2.0, y), s, color, size)


func _wedge(from_deg: float, to_deg: float, radius: float, color: Color) -> void:
	var pts := PackedVector2Array([CENTER])
	var steps := 24
	for i in range(steps + 1):
		var a: float = deg_to_rad(lerpf(from_deg, to_deg, float(i) / steps))
		pts.append(CENTER + Vector2(cos(a), sin(a)) * radius)
	view.draw_colored_polygon(pts, color)


func _draw_view() -> void:
	view.draw_rect(Rect2(0, 0, W, H), Color("0a0c1a"))
	var outer: float = RING[RING.size() - 1] + 7.0
	for z in ShipData.ZONES:
		_wedge(float(z["from"]), float(z["to"]), outer, z["color"])
	view.draw_circle(CENTER, RING[1] + 7.0, Color("1e2236"))
	for r in RING:
		if r > 0.0:
			view.draw_arc(CENTER, r, 0.0, TAU, 64, Color(0.45, 0.5, 0.7, 0.35), 1.0)
	for z in ShipData.ZONES:
		var mid: float = deg_to_rad((float(z["from"]) + float(z["to"])) / 2.0)
		var at_rim: Vector2 = CENTER + Vector2(cos(mid), sin(mid)) * (outer - 2.0)
		var y: float = clampf(at_rim.y + (6.0 if sin(mid) > 0.5 else -1.0), 7.0, H - 2.0)
		_text_c(clampf(at_rim.x, 30.0, 170.0), y, str(z["name"]), z["text"], 6)
	# the other stops: not on this route
	for d in dots:
		var p: Vector2 = d[0]
		var near := false
		for i in range(route.size()):
			if stop_pos(i).distance_to(p) < 8.0:
				near = true
		if near:
			continue
		view.draw_circle(p, 2.5, Color(0.32, 0.33, 0.4))
	# the Landing
	view.draw_circle(CENTER, 6.0, Color("64b4ff"))
	view.draw_arc(CENTER, 6.0, 0.0, TAU, 20, WHITE, 1.0)
	_text_c(CENTER.x, CENTER.y + 3, "EL", Color("14203c"), 6)
	if show_route:
		var prev: Vector2 = CENTER
		for i in range(route.size()):
			var here: Vector2 = stop_pos(i)
			var done: bool = i <= at
			view.draw_line(prev, here, GOLD if done else Color(0.98, 0.86, 0.35, 0.45), 1.0 if not done else 2.0)
			prev = here
		for i in range(route.size()):
			var s: Dictionary = route[i]
			var kind: Dictionary = ShipData.STOP_KINDS[s["kind"]]
			var here: Vector2 = stop_pos(i)
			var rad: float = 5.0 if str(s["kind"]) == "special" else 4.0
			view.draw_circle(here, rad, kind["color"] if i > at else Color(kind["color"]).darkened(0.4))
			view.draw_arc(here, rad, 0.0, TAU, 16, WHITE, 1.0)
			if i == next_index() and moving == 0.0:
				view.draw_arc(here, rad + 2.0 + sin(pulse * 5.0) * 1.0, 0.0, TAU, 20, GOLD, 1.0)
			_text_c(here.x, here.y - rad - 2.0, str(s["name"]), WHITE if i > at else DIM, 6)
	# your ship
	var ship: Vector2 = stop_pos(at)
	if moving > 0.0:
		ship = stop_pos(at).lerp(stop_pos(move_index), clampf(moving, 0.0, 1.0))
	var facing: Vector2 = (stop_pos(next_index()) - ship).normalized() if next_index() >= 0 else Vector2.RIGHT
	if facing == Vector2.ZERO:
		facing = Vector2.RIGHT
	var side := Vector2(-facing.y, facing.x)
	view.draw_colored_polygon(PackedVector2Array([ship + facing * 5.0, ship - facing * 3.0 + side * 3.0, ship - facing * 3.0 - side * 3.0]), Color("ff8c28"))
	_draw_panel()


func _draw_panel() -> void:
	view.draw_rect(Rect2(198, 4, 118, 172), PANEL)
	_text(Vector2(202, 13), "JUMP MAP", Color("78f0ff"), 8)
	if title != "":
		_text(Vector2(202, 23), title, GOLD, 6)
	_text(Vector2(202, 34), "Fuel %d   Hull %d/%d" % [int(world.fuel), int(world.ship_hull), int(ShipData.STARTER["hull"])], WHITE, 7)
	_text(Vector2(202, 43), "Credits %d" % int(world.credits), WHITE, 7)
	var n: int = next_index()
	if show_route and n >= 0:
		var s: Dictionary = route[n]
		var kind: Dictionary = ShipData.STOP_KINDS[s["kind"]]
		_text(Vector2(202, 57), "Next stop", DIM, 6)
		_text(Vector2(202, 67), str(s["name"]), WHITE, 8)
		_text(Vector2(202, 76), str(kind["label"]), kind["color"], 6)
		view.draw_multiline_string(font, Vector2(202, 86), str(s["about"]), HORIZONTAL_ALIGNMENT_LEFT, 110, 6, 5, DIM)
	# the key
	var keys: Array = ["beacon", "distress", "store", "special"]
	for k in range(keys.size()):
		var kind2: Dictionary = ShipData.STOP_KINDS[keys[k]]
		var pos := Vector2(204 + (k % 2) * 56, 124 + floori(k / 2.0) * 8)
		view.draw_circle(pos, 2.0, kind2["color"])
		_text(pos + Vector2(4, 2), str(kind2["label"]), DIM, 6)
	var jr := _jump_rect()
	var ready: bool = can_jump()
	view.draw_rect(jr, Color("4664a0") if ready else Color("323646"))
	if jr.has_point(hover) and ready:
		view.draw_rect(jr, GOLD, false, 1.0)
	_text_c(jr.get_center().x, jr.position.y + 9, "Jump  [E]   1 fuel" if n >= 0 else "Journey's end", WHITE if ready else DIM, 7)
	_text_c(258, 170, "Fold home: not on this flight", DIM, 6)
