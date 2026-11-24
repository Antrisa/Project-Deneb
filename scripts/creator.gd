extends CanvasLayer
# The "who are you?" screen (24 Nov: redrawn in the Terran datapad style of the other screens, ui/ship_screen.gd,
# and the clothes are back). Pick a gender, a top and a bottom, and the hair, eye, skin and clothes colours.
# Each gender keeps one hairstyle (scripts/player_maker.gd STARTER_LOOKS).
# Shown at the start of a new game, and again from the wardrobe in your apartment.
#   - Left: you, walking on the spot from the front, back and both sides; under that, for a colour line, the
#     preset swatches and hue / saturation / lightness sliders (click or drag).
#   - Right: the choices. Click a line's arrows (or Up / Down then Left / Right) to change it.
#   - Shuffle (R) picks random clothes and colours; Starter look (Home) puts the gender's own back; Start / Done
#     (E or Enter) keeps it. Esc leaves the wardrobe without changing anything.
# main.gd passes key presses here while it is open; clicks come straight to the screen.

const WalkCycle = preload("res://scripts/walk_cycle.gd")
const MakerScript = preload("res://scripts/player_maker.gd")
const ShipScreen = preload("res://ui/ship_screen.gd")

# What each line of the screen changes: [key in the look, label]
const ROWS := [
	["body", "Gender"], ["tops", "Top"], ["bottoms", "Bottom"],
	["hairColor", "Hair colour"], ["eyeColor", "Eyes"], ["skinColor", "Skin"],
	["topColor", "Top colour"], ["bottomColor", "Bottom colour"],
]
const ROW_H := 28.0
const SLIDER_STEPS := 32
const AXES := ["HUE", "SATURATION", "LIGHTNESS"]

var world                    # main.gd
var maker                    # scripts/player_maker.gd
var open := false
var look := {}
var row := 0
var first_time := false
var screen: ShipScreen

var _before := {}            # the look the wardrobe opened with (Esc puts it back)
var _sheet: Texture2D
var _time := 0.0
var _drag := -1              # the slider being dragged (0 hue, 1 saturation, 2 lightness), -1 none
var _sliders: Array = []     # [axis, Rect2] of each slider bar as last drawn


func _ready() -> void:
	layer = 14
	screen = ShipScreen.new()
	add_child(screen)
	screen.fill = true
	screen.paint = Callable(self, "_paint")
	screen.on_click = Callable(self, "_click")
	visible = false


func show_for(start_look: Dictionary, is_first_time: bool) -> void:
	look = maker.tidy(start_look)
	_before = look.duplicate()
	first_time = is_first_time
	row = 0
	_drag = -1
	open = true
	visible = true
	_refresh()
	screen.redraw()


func _refresh() -> void:
	_sheet = maker.sheet(look)


func _process(delta: float) -> void:
	_time += delta
	if not open:
		visible = false
		return
	visible = true
	if _drag >= 0:
		if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
			_slide_to(_drag, screen.mouse.x)
		else:
			_drag = -1
	screen.redraw()


# ---------------------------------------------------------------- changing things

func _change(index: int, by: int) -> void:
	var key: String = ROWS[index][0]
	if key == "body":
		# the other gender's hair and starter clothes, keeping any colours already picked
		var n: int = maker.option_count(key)
		var next: int = (int(look[key]) + by + n) % n
		var colours := {}
		for k in MakerScript.PALETTES:
			colours[k] = look[k]
		look = maker.defaults(next)
		if not (first_time and _starter_colours(colours, 1 - next)):
			look.merge(colours, true)
	elif MakerScript.NAMES.has(key):
		look[key] = (int(look[key]) + by + MakerScript.CHOICES) % MakerScript.CHOICES
	else:
		var colours: Array = MakerScript.PALETTES[key]
		var at: int = colours.find(look[key])
		look[key] = colours[(maxi(at, 0) + by + colours.size()) % colours.size()]
	world.sfx("click", 1.2, -6.0)
	_refresh()


func _starter_colours(colours: Dictionary, body: int) -> bool:
	var starter: Dictionary = maker.defaults(body)
	for k in colours:
		if colours[k] != starter[k]:
			return false
	return true


func _shuffle() -> void:
	# Shuffle changes the clothes and colours; gender (and so the hairstyle) stays as chosen.
	var keep_body: int = int(look.get("body", 0))
	look = maker.random_look()
	look["body"] = keep_body
	look = maker.tidy(look)
	world.sfx("click", 0.9)
	_refresh()


func _use_starter() -> void:
	look = maker.defaults(int(look.body))
	world.sfx("click", 1.2, -6.0)
	_refresh()


func _finish() -> void:
	open = false
	visible = false
	_drag = -1
	world.sfx("quest", 1.2)
	world.set_appearance(look)


func _leave() -> void:
	look = _before
	open = false
	visible = false
	_drag = -1
	world.sfx("click", 0.9)


func handle_input(event: InputEvent) -> void:
	if event.is_action_pressed("move_up", true):
		row = (row + ROWS.size() - 1) % ROWS.size()
	elif event.is_action_pressed("move_down", true):
		row = (row + 1) % ROWS.size()
	elif event.is_action_pressed("move_left", true):
		_change(row, -1)
	elif event.is_action_pressed("move_right", true):
		_change(row, 1)
	elif event.is_action_pressed("interact"):
		_finish()
	elif event.is_action_pressed("cancel") and not first_time:
		_leave()
	else:
		var key_event := event as InputEventKey
		if key_event != null and key_event.pressed and not key_event.echo:
			match key_event.physical_keycode:
				KEY_R:
					_shuffle()
				KEY_HOME:
					_use_starter()
				KEY_ENTER, KEY_KP_ENTER:
					_finish()


# Clicks reach the screen directly (ui/ship_screen.gd); main.gd's own click handling leaves them be.
func handle_click(_button: int) -> void:
	pass


func _click(id: String, at: Vector2, button: int) -> void:
	if button == MOUSE_BUTTON_RIGHT and not first_time:
		_leave()
		return
	if button != MOUSE_BUTTON_LEFT:
		return
	var parts := id.split("/")
	match parts[0]:
		"row":
			row = parts[1].to_int()
		"prev":
			row = parts[1].to_int()
			_change(row, -1)
		"next":
			row = parts[1].to_int()
			_change(row, 1)
		"swatch":
			var key := _color_key()
			if key != "":
				look[key] = str(MakerScript.PALETTES[key][parts[1].to_int()])
				world.sfx("click", 1.2, -6.0)
				_refresh()
		"slider":
			_drag = parts[1].to_int()
			_slide_to(_drag, at.x)
		"shuffle":
			_shuffle()
		"starter":
			_use_starter()
		"start":
			_finish()
		"cancel":
			_leave()


func _color_key() -> String:
	var key: String = ROWS[row][0]
	return key if MakerScript.PALETTES.has(key) else ""


func _slide_to(axis: int, x: float) -> void:
	for s in _sliders:
		if int(s[0]) == axis:
			var r: Rect2 = s[1]
			_set_color_axis(axis, clampf((x - r.position.x) / r.size.x, 0.0, 1.0))
			return


func _set_color_axis(axis: int, value: float) -> void:
	var key: String = _color_key()
	if key.is_empty():
		return
	var color: Color = Color.html(look[key])
	var hsv := Vector3(color.h, color.s, color.v)
	hsv[axis] = clampf(value, 0.0, 1.0)
	var result: String = "#" + Color.from_hsv(hsv.x, hsv.y, hsv.z).to_html(false)
	if result != look[key]:
		look[key] = result
		_refresh()


# ---------------------------------------------------------------- drawing

func _paint() -> void:
	var s := screen
	s.case_fill("New crew" if first_time else "Wardrobe")
	var top := 34.0
	var bottom: float = s.page.y - 44.0
	var right_w := 300.0
	var left := Rect2(12, top, s.page.x - right_w - 34.0, bottom - top)
	var choices := Rect2(left.end.x + 10.0, top, s.page.x - left.end.x - 22.0, bottom - top)
	s.panel(left, "crew", "Who are you?" if first_time else "A change of look")
	_paint_preview(Rect2(left.position.x + 8, left.position.y + 30, left.size.x - 16, 180))
	var under := Rect2(left.position.x + 8, left.position.y + 218, left.size.x - 16, left.end.y - left.position.y - 226)
	if _color_key() != "":
		_paint_colour(under)
	else:
		_paint_tips(under)
	s.panel(choices, "skills", "Your look")
	_paint_rows(choices)
	# the bottom row
	s.shift(s.bottom_left())
	s.text_fit(61, ShipScreen.STATUS_Y, 360, "Up / Down choose a line, Left / Right change it. R shuffles.", "label", ShipScreen.INK)
	s.shift(s.bottom_right())
	s.button("shuffle", Rect2(355, 388, 84, 22), "Shuffle")
	s.button("starter", Rect2(445, 388, 104, 22), "Starter look")
	if not first_time:
		s.button("cancel", Rect2(555, 388, 64, 22), "Cancel")
	s.solid_button("start", Rect2(625, 388, 82, 22), "Start" if first_time else "Done")
	s.shift(Vector2.ZERO)


# You, from four sides, walking on the spot in the dark readout window.
func _paint_preview(r: Rect2) -> void:
	var s := screen
	s.scope(r, 1)
	if _sheet == null:
		return
	var rows := WalkCycle.rows(_sheet)
	var step := WalkCycle.pose(int(_time * 8.0), rows)
	var fw: float = _sheet.get_width() / 4.0
	var fh: float = _sheet.get_height() / float(rows)
	var cell_w: float = r.size.x / 4.0
	var k: float = s.fit_scale(Vector2(fw, fh), Vector2(cell_w - 8.0, r.size.y - 30.0), 4.0)
	var names := ["FRONT", "BACK", "LEFT", "RIGHT"]
	for d in 4:
		var cx: float = r.position.x + cell_w * (d + 0.5)
		var size := Vector2(fw, fh) * k
		var at: Vector2 = s.snap(Vector2(cx - size.x * 0.5, r.end.y - 20.0 - size.y))
		s.texture(_sheet, Rect2(at, size), Rect2(d * fw, step * fh, fw, fh))
		s.text_center(cx, r.end.y - 15.0, names[d], "micro", ShipScreen.SCOPE_TEXT)


func _paint_tips(r: Rect2) -> void:
	var s := screen
	var y: float = r.position.y + 4.0
	s.text(r.position.x, y, "CLOTHES AND COLOURS", "micro", ShipScreen.MUTED)
	y += 16.0
	y = s.wrap_text(r.position.x, y, r.size.x, "Pick a top and a bottom, then their colours. Choose a colour line to mix your own shade.", "body", ShipScreen.INK, 17.0)
	y += 6.0
	s.wrap_text(r.position.x, y, r.size.x, "You can change your look any time at the wardrobe in your apartment.", "label", ShipScreen.MUTED, 15.0)


# For a colour line: its preset swatches, then hue, saturation and lightness sliders.
func _paint_colour(r: Rect2) -> void:
	var s := screen
	var key := _color_key()
	var current := Color.html(look[key])
	s.text(r.position.x, r.position.y + 2.0, str(ROWS[row][1]).to_upper(), "micro", ShipScreen.MUTED)
	s.text_right(r.end.x, r.position.y + 2.0, str(look[key]).to_upper(), "micro", ShipScreen.MUTED)
	var colours: Array = MakerScript.PALETTES[key]
	var x: float = r.position.x
	var y: float = r.position.y + 16.0
	for i in colours.size():
		var sw := Rect2(x, y, 18, 18)
		var chosen: bool = str(colours[i]) == str(look[key])
		s.rect(sw, Color.html(colours[i]))
		s.outline(sw, ShipScreen.ORANGE if chosen else Color("8f877a"), 2.0 if chosen else 1.0)
		if s.hovering(sw) and not chosen:
			s.outline(sw.grow(1.0), ShipScreen.ORANGE)
		s.hit("swatch/%d" % i, sw)
		x += 22.0
		if x + 18.0 > r.end.x:
			x = r.position.x
			y += 22.0
	y += 30.0
	var values := [current.h, current.s, current.v]
	_sliders.clear()
	for axis in 3:
		s.text(r.position.x, y, AXES[axis], "micro", ShipScreen.MUTED)
		var bar := Rect2(r.position.x + 78.0, y + 1.0, r.size.x - 82.0, 9.0)
		var seg: float = bar.size.x / SLIDER_STEPS
		for i in SLIDER_STEPS:
			var t: float = (i + 0.5) / SLIDER_STEPS
			var shade: Color
			if axis == 0:
				shade = Color.from_hsv(t, 0.8, 0.9)
			elif axis == 1:
				shade = Color.from_hsv(current.h, t, maxf(current.v, 0.3))
			else:
				shade = Color.from_hsv(current.h, current.s, t)
			s.rect(Rect2(bar.position.x + i * seg, bar.position.y, ceilf(seg), bar.size.y), shade)
		s.outline(bar, Color("8f877a"))
		var knob: float = bar.position.x + float(values[axis]) * bar.size.x
		s.rect(Rect2(knob - 2.0, bar.position.y - 3.0, 4.0, bar.size.y + 6.0), ShipScreen.INK)
		s.rect(Rect2(knob - 1.0, bar.position.y - 2.0, 2.0, bar.size.y + 4.0), ShipScreen.IVORY)
		var grab := bar.grow_individual(4.0, 5.0, 4.0, 5.0)
		_sliders.append([axis, grab])
		s.hit("slider/%d" % axis, grab)
		y += 22.0


# The choices, one line each: the name, and the choice between arrows.
func _paint_rows(r: Rect2) -> void:
	var s := screen
	var y: float = r.position.y + 30.0
	for i in ROWS.size():
		var key: String = ROWS[i][0]
		var line := Rect2(r.position.x + 6.0, y, r.size.x - 12.0, ROW_H - 4.0)
		if i == row:
			s.frame(line, Color("f0d4b9"), Color("c3b8a5"), Color("f9e8d2"), Color("bd8b67"))
		elif s.hovering(line):
			s.frame(line, Color("f7f3ea"), Color("d5cfc1"), Color("fffdf6"), Color("e3ddd0"))
		s.hit("row/%d" % i, line)
		s.text(line.position.x + 8.0, line.position.y + 5.0, str(ROWS[i][1]), "label", ShipScreen.INK if i == row else ShipScreen.MUTED)
		var value_x: float = line.position.x + 104.0
		var value_w: float = line.end.x - value_x - 30.0
		s.button("prev/%d" % i, Rect2(value_x - 2.0, line.position.y + 2.0, 20.0, line.size.y - 4.0), "<")
		s.button("next/%d" % i, Rect2(line.end.x - 24.0, line.position.y + 2.0, 20.0, line.size.y - 4.0), ">")
		var mid := Rect2(value_x + 22.0, line.position.y, value_w - 22.0, line.size.y)
		if key == "body":
			s.text_center(mid.get_center().x, line.position.y + 5.0, str(MakerScript.OPTIONS["body"][int(look["body"])]), "label", ShipScreen.INK)
		elif MakerScript.NAMES.has(key):
			var label: String = str(MakerScript.NAMES[key][int(look[key])])
			s.text_center(mid.get_center().x, line.position.y + 5.0, label, "label", ShipScreen.INK)
		else:
			var sw := Rect2(mid.get_center().x - 22.0, line.position.y + 5.0, 44.0, line.size.y - 10.0)
			s.rect(sw, Color.html(look[key]))
			s.outline(sw, Color("6f675c"))
		y += ROW_H
