extends Control
# The "who are you?" screen: pick hair, face, clothes and colours.
# Shown at the start of a new game, and again from the locker in your quarters.
# main.gd passes key presses and clicks here while it is open.

const MakerScript = preload("res://scripts/player_maker.gd")

# What each line of the screen changes: [key in the look, label]
const ROWS := [
	["hair", "Hair"], ["hairColor", "Hair colour"], ["faces", "Face"], ["eyeColor", "Eyes"], ["skinColor", "Skin"],
	["tops", "Top"], ["topColor", "Top colour"], ["bottoms", "Bottom"], ["bottomColor", "Bottom colour"],
]
const PANEL := Rect2(4, 4, 312, 172)
const ROW_X := 156.0
const ROW_Y := 34.0
const ROW_H := 13.0
const SHUFFLE := Rect2(16, 112, 64, 15)
const START := Rect2(84, 112, 64, 15)
const DIM := Color(0.6, 0.7, 0.85)
const GOLD := Color(1.0, 0.824, 0.498)

var world                    # main.gd
var maker                    # scripts/player_maker.gd
var open := false
var look := {}
var row := 0
var first_time := false

var _font: Font
var _panel_tex: Texture2D
var _tab_tex: Texture2D
var _sheet: Texture2D
var _time := 0.0
var _last_mouse := Vector2(-1, -1)


func _ready() -> void:
	_font = ThemeDB.fallback_font
	_panel_tex = load("res://art/ui_panel.png")
	_tab_tex = load("res://art/ui_tab.png")
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size = Vector2(320, 180)


func show_for(start_look: Dictionary, is_first_time: bool) -> void:
	look = maker.tidy(start_look)
	first_time = is_first_time
	row = 0
	open = true
	_refresh()


func _refresh() -> void:
	_sheet = maker.sheet(look)


func _process(delta: float) -> void:
	_time += delta
	if open:
		var at: Vector2 = get_local_mouse_position()
		if at != _last_mouse:
			_last_mouse = at
			var hit: int = _row_at(at)
			if hit != -1:
				row = hit
	queue_redraw()


# ---------------------------------------------------------------- changing things

func _change(index: int, by: int) -> void:
	var entry: Array = ROWS[index]
	var key: String = entry[0]
	if MakerScript.NAMES.has(key):
		look[key] = (int(look[key]) + by + 10) % 10
	else:
		var colours: Array = MakerScript.PALETTES[key]
		var at: int = colours.find(look[key])
		look[key] = colours[(maxi(at, 0) + by + colours.size()) % colours.size()]
	world.sfx("click", 1.2, -6.0)
	_refresh()


func _shuffle() -> void:
	look = maker.random_look()
	world.sfx("click", 0.9)
	_refresh()


func _finish() -> void:
	open = false
	world.sfx("quest", 1.2)
	world.set_appearance(look)


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
		_finish()
	else:
		var key_event := event as InputEventKey
		if key_event != null and key_event.pressed and not key_event.echo and key_event.physical_keycode == KEY_R:
			_shuffle()


func _row_at(at: Vector2) -> int:
	for i in ROWS.size():
		if Rect2(ROW_X - 2, ROW_Y + i * ROW_H - 9, 158, ROW_H).has_point(at):
			return i
	return -1


func handle_click(button: int) -> void:
	if button != MOUSE_BUTTON_LEFT:
		return
	var at: Vector2 = get_local_mouse_position()
	if SHUFFLE.has_point(at):
		_shuffle()
	elif START.has_point(at):
		_finish()
	else:
		var hit: int = _row_at(at)
		if hit != -1:
			row = hit
			# The left half of the value steps back, the right half steps forward.
			_change(hit, -1 if at.x < ROW_X + 106 else 1)


# ---------------------------------------------------------------- drawing

func _txt(pos: Vector2, s: String, color: Color = Color.WHITE, font_size: int = 8) -> void:
	draw_string(_font, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, color)


func _nine(tex: Texture2D, r: Rect2, corner: float) -> void:
	var cw: float = tex.get_width() / 3.0
	var ch: float = tex.get_height() / 3.0
	var xs: Array = [r.position.x, r.position.x + corner, r.end.x - corner, r.end.x]
	var ys: Array = [r.position.y, r.position.y + corner, r.end.y - corner, r.end.y]
	for j in 3:
		for i in 3:
			var x0: float = xs[i]
			var x1: float = xs[i + 1]
			var y0: float = ys[j]
			var y1: float = ys[j + 1]
			draw_texture_rect_region(tex, Rect2(x0, y0, x1 - x0, y1 - y0), Rect2(i * cw, j * ch, cw, ch))


func _button(r: Rect2, label: String, chosen: int) -> void:
	var fw: float = _tab_tex.get_width() / 2.0
	var third: float = fw / 3.0
	var xs: Array = [r.position.x, r.position.x + 4.0, r.end.x - 4.0, r.end.x]
	for i in 3:
		var x0: float = xs[i]
		var x1: float = xs[i + 1]
		draw_texture_rect_region(_tab_tex, Rect2(x0, r.position.y, x1 - x0, r.size.y), Rect2(chosen * fw + i * third, 0, third, _tab_tex.get_height()))
	_txt(r.position + Vector2(8, 10), label, Color.WHITE)


func _draw() -> void:
	if not open:
		return
	draw_rect(Rect2(0, 0, 320, 180), Color(0.02, 0.03, 0.08, 0.9))
	_nine(_panel_tex, PANEL, 8.0)
	_txt(Vector2(16, 20), "Who are you?" if first_time else "A change of look", GOLD, 10)

	# Four views, walking on the spot.
	if _sheet != null:
		var cycle: Array = [1, 0, 2, 0]
		var step: int = cycle[int(_time * 5.0) % 4]
		for d in 4:
			draw_texture_rect_region(_sheet, Rect2(18 + d * 33, 38, 32, 64), Rect2(d * 32, step * 64, 32, 64))
	_txt(Vector2(22, 34), "Front       Back        Left        Right", DIM, 6)

	_button(SHUFFLE, "Shuffle  R", 0)
	_button(START, "Start" if first_time else "Done", 1)

	for i in ROWS.size():
		var entry: Array = ROWS[i]
		var key: String = entry[0]
		var label: String = entry[1]
		var y: float = ROW_Y + i * ROW_H
		var chosen: bool = i == row
		if chosen:
			draw_rect(Rect2(ROW_X - 2, y - 9, 158, ROW_H), Color(0.16, 0.3, 0.45, 0.8))
		_txt(Vector2(ROW_X, y), label, Color.WHITE if chosen else DIM)
		_txt(Vector2(ROW_X + 62, y), "<", GOLD if chosen else DIM)
		_txt(Vector2(ROW_X + 148, y), ">", GOLD if chosen else DIM)
		if MakerScript.NAMES.has(key):
			var names: Array = MakerScript.NAMES[key]
			var chosen_name: String = names[int(look[key])]
			_txt(Vector2(ROW_X + 70, y), chosen_name, Color.WHITE, 7)
		else:
			var colours: Array = MakerScript.PALETTES[key]
			var at: int = maxi(0, colours.find(look[key]))
			draw_rect(Rect2(ROW_X + 70, y - 7, 30, 8), Color.html(look[key]))
			draw_rect(Rect2(ROW_X + 69.5, y - 7.5, 31, 9), Color(0, 0, 0, 0.6), false, 1.0)
			_txt(Vector2(ROW_X + 106, y), "%d of %d" % [at + 1, colours.size()], DIM, 6)

	_txt(Vector2(16, 144), "Up / Down: choose a line     Left / Right: change it", DIM, 6)
	_txt(Vector2(16, 153), "Or click the left or right half of a value.", DIM, 6)
	if first_time:
		_txt(Vector2(16, 166), "You can change this later at the locker in your quarters.", DIM, 6)
	else:
		_txt(Vector2(16, 166), "Enter or Esc when you're done.", DIM, 6)
