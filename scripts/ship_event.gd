extends CanvasLayer
# Arriving at a stop, and the event window (21 Nov 2026). Like FTL: your ship jumps to the stop, the backdrop
# changes, and a window comes up with the event's text and choices (Zachary, 21 Nov). Pick a choice; the
# outcome and what you gained or lost show in the same window; Continue closes it.
#
# main.gd calls show_backdrop(stop) on arrival, then open_event(event, cb). Events are in scripts/space_events.gd;
# main.gd checks needs (space_need_met) and applies effects (apply_space_effects). cb.call(fight_id) when the
# player continues: fight_id is an enemy ship id if the outcome started a fight, otherwise "".
# Laid out on the 640 x 360 screen at 1:1 (templates/ui_event_window_x2.png in the ship art pack). Until the
# UI kit and backdrops exist, everything here is drawn as plain shapes.

const ShipData = preload("res://scripts/ship_data.gd")
const SpaceEvents = preload("res://scripts/space_events.gd")

const W := 640.0
const H := 360.0
const WIN := Rect2(120, 54, 400, 248)
const WHITE := Color("ececf0")
const DIM := Color("969cb0")
const GOLD := Color("fadc5a")
const BLUE := Color("5ab4ff")
const GOOD := Color("5adc6e")
const BAD := Color("e6463c")

var world                          # main.gd
var open := false                  # the backdrop is up (and maybe the window)
var showing_window := false
var event: Dictionary = {}
var outcome: Dictionary = {}       # after a choice: {"text", "gains": [[text, colour]], "fight"}
var stop: Dictionary = {}
var on_done: Callable = Callable()
var view: Control
var font: Font
var stars: Array = []
var ship_tex: Texture2D
var hover := Vector2(-99, -99)
var _hits: Array = []              # [Rect2, action, index], rebuilt each time the window is drawn


func _ready() -> void:
	layer = 9
	visible = false
	view = Control.new()
	view.size = Vector2(W, H)
	view.mouse_filter = Control.MOUSE_FILTER_STOP
	view.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(view)
	view.draw.connect(_draw_view)
	view.gui_input.connect(_on_gui_input)
	font = view.get_theme_default_font()
	if font == null:
		font = ThemeDB.fallback_font
	var rng := RandomNumberGenerator.new()
	rng.seed = 11
	for i in range(220):
		stars.append([Vector2(rng.randf() * W, rng.randf() * H), rng.randf_range(0.25, 0.9)])
	if ResourceLoader.exists(ShipData.STARTER["art"]):
		ship_tex = load(ShipData.STARTER["art"])


# The ship has arrived: show the stop behind whatever happens next.
func show_backdrop(new_stop: Dictionary) -> void:
	stop = new_stop
	event = {}
	outcome = {}
	showing_window = false
	open = true
	visible = true


func open_event(new_event: Dictionary, cb: Callable) -> void:
	event = new_event
	outcome = {}
	on_done = cb
	showing_window = true
	open = true
	visible = true


func close() -> void:
	open = false
	visible = false
	showing_window = false
	on_done = Callable()


func _process(_delta: float) -> void:
	if open:
		view.queue_redraw()


# ---------------------------------------------------------------- input

func handle_input(ev: InputEvent) -> void:
	if not showing_window:
		return
	var key := ev as InputEventKey
	if key != null and key.pressed and not key.echo and key.physical_keycode >= KEY_1 and key.physical_keycode <= KEY_4:
		_choose(key.physical_keycode - KEY_1)
	elif ev.is_action_pressed("interact") or ev.is_action_pressed("use"):
		_continue()


func _on_gui_input(ev: InputEvent) -> void:
	var motion := ev as InputEventMouseMotion
	if motion != null:
		hover = motion.position
		return
	var click := ev as InputEventMouseButton
	if click == null or not click.pressed or click.button_index != MOUSE_BUTTON_LEFT:
		return
	view.accept_event()
	if world.dialogue.active:
		world.dialogue.advance()
		return
	for h in _hits:
		if (h[0] as Rect2).has_point(click.position):
			if str(h[1]) == "choice":
				_choose(int(h[2]))
			elif str(h[1]) == "continue":
				_continue()
			return


func _choose(i: int) -> void:
	if not outcome.is_empty() or event.is_empty():
		return
	var choices: Array = event["choices"]
	if i < 0 or i >= choices.size():
		return
	var ch: Dictionary = choices[i]
	if not world.space_need_met(str(ch.get("needs", ""))):
		world.sfx("deny")
		return
	var o: Dictionary = SpaceEvents.roll(ch)
	outcome = world.apply_space_effects(o.get("effects", []))
	outcome["text"] = str(o.get("text", ""))
	world.sfx("click")


func _continue() -> void:
	if outcome.is_empty():
		return
	var cb: Callable = on_done
	var fight: String = str(outcome.get("fight", ""))
	showing_window = false
	event = {}
	outcome = {}
	on_done = Callable()
	if cb.is_valid():
		cb.call(fight)


# ---------------------------------------------------------------- drawing

func _text(pos: Vector2, s: String, color: Color = WHITE, size: int = 12) -> void:
	view.draw_string(font, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)


func _zone_color() -> Color:
	if stop.is_empty() or int(stop.get("ring", 0)) <= 1:
		return Color("141a30")
	var a: float = fposmod(float(stop.get("angle", 0.0)), 360.0)
	var idx := 3                        # ShipData.ZONES: Terran, Zaa'sh, the Reach, Collective
	if a >= 225.0 and a < 315.0:
		idx = 0
	elif a >= 315.0 or a < 45.0:
		idx = 1
	elif a < 135.0:
		idx = 2
	return Color(ShipData.ZONES[idx]["color"]).darkened(0.45)


func _draw_view() -> void:
	_hits.clear()
	view.draw_rect(Rect2(0, 0, W, H), _zone_color())
	for s in stars:
		view.draw_rect(Rect2(s[0], Vector2.ONE), Color(1, 1, 1, float(s[1])))
	if stop.is_empty() or int(stop.get("ring", 0)) <= 1:
		for i in range(10):
			view.draw_circle(Vector2(560, -40), 150.0 - i * 4.0, Color(0.16 + i * 0.02, 0.3 + i * 0.03, 0.55 + i * 0.03))
	_draw_prop()
	if ship_tex != null:
		var me: Dictionary = ShipData.STARTER
		var fw: float = ship_tex.get_width() / float(me["frames"])
		view.draw_texture_rect_region(ship_tex, Rect2(Vector2(40, 150), me["size"]), Rect2(fw * int(me["frame"]), 0, fw, ship_tex.get_height()))
	if showing_window:
		_draw_window()


# What's at the stop, as plain shapes until backdrops and ships are drawn.
func _draw_prop() -> void:
	var what: String = str(stop.get("event", ""))
	var kind: String = str(stop.get("kind", ""))
	if what == "ice_field":
		var rng := RandomNumberGenerator.new()
		rng.seed = 4
		for i in range(14):
			var c := Vector2(rng.randf_range(380, 620), rng.randf_range(60, 320))
			var r: float = rng.randf_range(6, 22)
			var pts := PackedVector2Array()
			for k in range(6):
				var a: float = k * TAU / 6.0 + rng.randf_range(-0.3, 0.3)
				pts.append(c + Vector2(cos(a), sin(a)) * r * rng.randf_range(0.7, 1.1))
			view.draw_colored_polygon(pts, Color(0.7, 0.8, 0.9, 0.85))
	elif kind == "distress":
		var base := Vector2(430, 140)
		view.draw_rect(Rect2(base, Vector2(150, 50)), Color("4a5a4e"))
		view.draw_rect(Rect2(base + Vector2(20, -18), Vector2(60, 18)), Color("5a6a5c"))
		view.draw_rect(Rect2(base + Vector2(150, 12), Vector2(26, 26)), Color("3a463e"))
		for i in range(3):
			view.draw_circle(base + Vector2(30 + i * 40, 25), 6.0, Color("2a2420"))
	elif kind == "store":
		view.draw_circle(Vector2(510, 180), 46.0, Color("6a4a8a"))
		view.draw_circle(Vector2(510, 180), 30.0, Color("8a6ab0"))
		for i in range(4):
			view.draw_rect(Rect2(Vector2(452 + i * 30, 228), Vector2(22, 16)), Color("c8a050"))


func _draw_window() -> void:
	view.draw_rect(WIN, Color(0.086, 0.1, 0.17, 0.97))
	view.draw_rect(WIN, GOLD, false, 2.0)
	_text(Vector2(WIN.position.x + 8, WIN.position.y + 20), str(event.get("title", "")), GOLD, 14)
	var body: String = str(outcome.get("text", "")) if not outcome.is_empty() else str(event.get("text", ""))
	view.draw_multiline_string(font, Vector2(WIN.position.x + 8, WIN.position.y + 44), body, HORIZONTAL_ALIGNMENT_LEFT,
		WIN.size.x - 16, 12, 7, WHITE)
	if outcome.is_empty():
		var choices: Array = event.get("choices", [])
		for i in range(mini(4, choices.size())):
			var ch: Dictionary = choices[i]
			var r := Rect2(128, 190 + i * 24, 384, 20)
			var needs: String = str(ch.get("needs", ""))
			var ok: bool = world.space_need_met(needs)
			var fill := Color("262c46")
			if not ok:
				fill = Color("1c1e28")
			elif needs != "":
				fill = Color("1e3a5c")
			if ok and r.has_point(hover):
				fill = fill.lightened(0.15)
			view.draw_rect(r, fill)
			view.draw_rect(r, BLUE if (ok and needs != "") else Color("5a6080"), false, 1.0)
			_text(r.position + Vector2(6, 14), "%d.  %s" % [i + 1, str(ch["text"])], WHITE if ok else DIM, 12)
			if needs != "":
				var tag := "(%s)" % needs
				var w: float = font.get_string_size(tag, HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x
				_text(Vector2(r.end.x - w - 6, r.position.y + 14), tag, BLUE if ok else DIM, 10)
			_hits.append([r, "choice", i])
	else:
		var gains: Array = outcome.get("gains", [])
		for i in range(gains.size()):
			var g: Array = gains[i]
			_text(Vector2(136, 200 + i * 15), str(g[0]), g[1], 12)
		var r2 := Rect2(128, 274, 384, 20)
		view.draw_rect(r2, Color("2e4a7a") if r2.has_point(hover) else Color("26365a"))
		view.draw_rect(r2, GOLD, false, 1.0)
		var label := "Continue  [E]"
		var lw: float = font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, 12).x
		_text(Vector2(r2.get_center().x - lw / 2.0, r2.position.y + 14), label, WHITE, 12)
		_hits.append([r2, "continue", 0])
