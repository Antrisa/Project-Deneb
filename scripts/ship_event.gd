extends CanvasLayer
# Arriving at a stop, and the event window (21 Nov 2026). Like FTL: your ship jumps to the stop, the scene changes,
# and a window comes up with the event's text and choices (Zachary, 21 Nov). Pick a choice; the outcome and what
# you gained or lost show in the same window; Continue closes it. Drawn on the Terran field datapad
# (ui/ship_screen.gd): the stop in the scope at the top, the event in the panel under it. Mock-up:
# datapad_event_x2.png in the Drive folder.
#
# main.gd calls show_backdrop(stop) on arrival, then open_event(event, cb). Events are in scripts/space_events.gd;
# main.gd checks needs (space_need_met) and applies effects (apply_space_effects). cb.call(fight_id) when the
# player continues: fight_id is an enemy ship id if the outcome started a fight, otherwise "".
# Until backdrops and ships are drawn, what's at the stop is drawn here as plain shapes.

const ShipData = preload("res://scripts/ship_data.gd")
const SpaceEvents = preload("res://scripts/space_events.gd")
const ShipScreen = preload("res://ui/ship_screen.gd")

const INK := Color("373b36")          # as ui/ship_screen.gd
const MUTED := Color("595e55")          # as ui/ship_screen.gd
const OCHRE := Color("a45736")          # as ui/ship_screen.gd
const ORANGE := Color("ac5c36")          # as ui/ship_screen.gd
const LINE := 16.0                 # body text line height
const ROW := 28.0                  # one choice

var world                          # main.gd
var open := false                  # the scene is up (and maybe the window)
var showing_window := false
var event: Dictionary = {}
var outcome: Dictionary = {}       # after a choice: {"text", "gains": [[text, colour]], "fight"}
var stop: Dictionary = {}
var on_done: Callable = Callable()
var screen: ShipScreen
var ship_tex: Texture2D


func _ready() -> void:
	layer = 9
	visible = false
	screen = ShipScreen.new()
	add_child(screen)
	screen.fill = true                  # the whole window, like the battle (Zachary, 22 Nov)
	screen.paint = Callable(self, "_paint")
	screen.on_click = Callable(self, "_click")
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
	screen.redraw()


func open_event(new_event: Dictionary, cb: Callable) -> void:
	event = new_event
	outcome = {}
	on_done = cb
	showing_window = true
	open = true
	visible = true
	screen.redraw()


# A window that only reports something (the salvage after a won fight): the text and gains, then Continue.
func show_result(title: String, text: String, gains: Array, cb: Callable) -> void:
	event = {"title": title, "text": text, "choices": []}
	outcome = {"text": text, "gains": gains, "fight": ""}
	on_done = cb
	showing_window = true
	open = true
	visible = true
	screen.redraw()


func close() -> void:
	open = false
	visible = false
	showing_window = false
	on_done = Callable()


func _process(_delta: float) -> void:
	if open and visible:
		screen.redraw()


# ---------------------------------------------------------------- input

func handle_input(ev: InputEvent) -> void:
	if not showing_window:
		return
	var key := ev as InputEventKey
	if key != null and key.pressed and not key.echo and key.physical_keycode >= KEY_1 and key.physical_keycode <= KEY_4:
		_choose(key.physical_keycode - KEY_1)
	elif ev.is_action_pressed("interact") or ev.is_action_pressed("use"):
		_continue()


func _click(id: String, _p: Vector2, button: int) -> void:
	if button != MOUSE_BUTTON_LEFT:
		return
	if world.dialogue.active:
		world.dialogue.advance()
		return
	if id.begins_with("choice/"):
		_choose(int(id.get_slice("/", 1)))
	elif id == "continue":
		_continue()


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

func _zone() -> Dictionary:
	if stop.is_empty() or int(stop.get("ring", 0)) <= 1:
		return {}
	return ShipData.ZONES[ShipData.stop_zone_index(stop)]       # the zone the stop sits in on the map


func _tag() -> String:
	var kind: String = str(stop.get("kind", ""))
	if ShipData.STOP_KINDS.has(kind):
		return str(ShipData.STOP_KINDS[kind]["label"])
	return "Arrived"


func _body() -> String:
	return str(outcome.get("text", "")) if not outcome.is_empty() else str(event.get("text", ""))


func _paint() -> void:
	var s := screen
	s.case_fill(_tag())
	var left: float = 12.0
	var wide: float = s.page.x - 24.0
	var bottom: float = s.page.y - 50.0
	if not showing_window:
		_paint_scene(Rect2(left, 46, wide, bottom - 46.0))
		_status("Arrived: %s." % str(stop.get("name", "a quiet patch of space")))
		return
	# The panel grows to fit the event; the scene takes what's left above it.
	var body: Array = s.wrap_lines(_body(), wide - 22.0, "label")
	var below: float
	if outcome.is_empty():
		below = mini(4, (event.get("choices", []) as Array).size()) * ROW
	else:
		below = _gain_rows() * LINE + 4.0
	var height: float = 30.0 + body.size() * LINE + 8.0 + below + 4.0
	var top: float = clampf(bottom - height, bottom - 262.0, bottom - 122.0)
	_paint_scene(Rect2(left, 46, wide, top - 50.0))
	var box := Rect2(left, top, wide, bottom - top)
	s.panel(box, "mark", str(event.get("title", "")))
	var y: float = top + 30.0
	for ln in body:
		s.text(left + 11.0, y, ln, "label", INK)
		y += LINE
	y += 8.0
	if outcome.is_empty():
		var choices: Array = event.get("choices", [])
		y = maxf(y, bottom - 4.0 - mini(4, choices.size()) * ROW)
		for i in range(mini(4, choices.size())):
			_paint_choice(i, choices[i], Rect2(left + 9.0, y + i * ROW, wide - 18.0, 24))
		_status("Choose with a click, or keys 1 to %d." % mini(4, choices.size()))
	else:
		# More than six lines (a big salvage) go in two columns.
		var gains: Array = outcome.get("gains", [])
		var rows: int = _gain_rows()
		for gi in gains.size():
			var g: Array = gains[gi]
			var gx: float = left + 11.0 + (wide * 0.5 if gi >= rows else 0.0)
			s.text_fit(gx, y + (gi % rows) * LINE, wide * 0.5 - 16.0 if gains.size() > 6 else wide - 22.0, str(g[0]), "label", Color(g[1]).darkened(0.35))
		_status("Click Continue.")
		s.shift(s.bottom_right())
		s.solid_button("continue", Rect2(625, 388, 82, 22), "Continue")
		s.shift(Vector2.ZERO)


func _gain_rows() -> int:
	var n: int = (outcome.get("gains", []) as Array).size()
	return n if n <= 6 else int(ceil(n / 2.0))


func _status(line: String) -> void:
	screen.shift(screen.bottom_left())
	screen.status(line)
	screen.shift(Vector2.ZERO)


# A choice row. A choice that needs something you have (a weapon, the drone) is blue, as in FTL; one that needs
# something you don't have is greyed out.
func _paint_choice(i: int, ch: Dictionary, r: Rect2) -> void:
	var s := screen
	var needs: String = str(ch.get("needs", ""))
	var ok: bool = world.space_need_met(needs)
	var words := "%d  %s" % [i + 1, str(ch["text"])]
	var tag: String = needs.to_upper()
	var tag_w: float = s.width(tag, "micro") + 12.0 if needs != "" else 0.0
	if not ok:
		s.frame(r, Color("e6e4de"), Color("d0c9bb"), Color("f2f0ea"), Color("dcd7cc"))
		s.text_fit(r.position.x + 8, r.position.y + 4, r.size.x - 16 - tag_w, words, "label", Color("a8a69e"))
		s.text_right(r.end.x - 8, r.position.y + 6, tag, "micro", Color("a8a69e"))
		return
	if needs != "":
		s.frame(r, Color("d6e6ee"), Color("6f9fb4"), Color("eef7fb"), Color("9cc2d2"))
		s.text_fit(r.position.x + 8, r.position.y + 4, r.size.x - 16 - tag_w, words, "label", Color("2a4a5a"))
		s.text_right(r.end.x - 8, r.position.y + 6, tag, "micro", Color("2a6a8a"))
	else:
		s.frame(r, Color("f0eee7"), Color("c3b8a5"), Color("fffdf6"), Color("d5cfc1"))
		s.text_fit(r.position.x + 8, r.position.y + 4, r.size.x - 16, words, "label", INK)
	if s.hovering(r):
		s.outline(r, ORANGE)
	s.hit("choice/%d" % i, r)


# The stop, in the scope: your ship on the left, whatever is there on the right. Everything stays inside the
# scope (the page has no clipping).
func _paint_scene(r: Rect2) -> void:
	var s := screen
	s.scope(r, 7)
	var zone: Dictionary = _zone()
	if not zone.is_empty():
		s.rect(r.grow(-2.0), Color(zone["color"], 0.35))
		s.text(r.position.x + 11, r.position.y + 7, str(zone["name"]).to_upper(), "micro", zone["text"])
	else:
		s.text(r.position.x + 11, r.position.y + 7, "NEAR ECHO LANDING", "micro", ShipScreen.SCOPE_TEXT)
	if not stop.is_empty():
		s.text_right(r.end.x - 11, r.position.y + 7, str(stop.get("name", "")).to_upper(), "micro", ShipScreen.SCOPE_TEXT)
	var me: Dictionary = ShipData.STARTER
	var size: Vector2 = me["size"]
	var area := Rect2(r.position + Vector2(16, 18), Vector2(240, r.size.y - 30))
	# fitted on the picture's own pixels (double-resolution art has "art_scale" 2), so it stays crisp
	var a: float = float(me.get("art_scale", 1))
	var xf: Transform2D = s.fit_into(size * a, area)
	if ship_tex != null:
		var fw: float = ship_tex.get_width() / float(me["frames"])
		s.texture(ship_tex, Rect2(xf.origin, size * a * xf.get_scale().x), Rect2(fw * int(me["frame"]), 0, fw, ship_tex.get_height()))
	_paint_prop(Rect2(r.position.x + 280, r.position.y + 18, r.size.x - 296, r.size.y - 30))


func _paint_prop(r: Rect2) -> void:
	var s := screen
	var what: String = str(stop.get("event", ""))
	var kind: String = str(stop.get("kind", ""))
	var c: Vector2 = r.get_center()
	var u: float = clampf(r.size.y / 100.0, 0.4, 2.0)
	if what == "ice_field":
		var rng := RandomNumberGenerator.new()
		rng.seed = 4
		for i in range(14):
			var rad: float = rng.randf_range(5, 13) * u
			var at := Vector2(rng.randf_range(r.position.x + rad, r.end.x - rad), rng.randf_range(r.position.y + rad, r.end.y - rad))
			var pts := PackedVector2Array()
			for k in range(6):
				var a: float = k * TAU / 6.0 + rng.randf_range(-0.3, 0.3)
				pts.append(at + Vector2(cos(a), sin(a)) * rad * rng.randf_range(0.7, 1.0))
			s.polygon(pts, Color(0.7, 0.8, 0.9, 0.85))
	elif kind == "distress":
		var base: Vector2 = c - Vector2(75, 25) * u
		s.rect(Rect2(base, Vector2(150, 50) * u), Color("4a5a4e"))
		s.rect(Rect2(base + Vector2(20, -18) * u, Vector2(60, 18) * u), Color("5a6a5c"))
		s.rect(Rect2(base + Vector2(150, 12) * u, Vector2(26, 26) * u), Color("3a463e"))
		for i in range(3):
			s.circle(base + Vector2(30 + i * 40, 25) * u, 6.0 * u, Color("2a2420"))
	elif kind == "store":
		s.circle(c, 40.0 * u, Color("6a4a8a"))
		s.circle(c, 26.0 * u, Color("8a6ab0"))
		for i in range(4):
			s.rect(Rect2(c + Vector2(-58 + i * 30, 44) * u, Vector2(22, 12) * u), Color("c8a050"))
