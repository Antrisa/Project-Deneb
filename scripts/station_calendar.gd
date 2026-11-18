extends CanvasLayer
# Attached community-board calendar. Uses actual weekday and visitor schedule data.
const MapData = preload("res://scripts/map_data.gd")
const WEEK := ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
var open := false
var today := 1
var selected_day := 1
var cycle_start := 1
var _panel: Panel
var _heading: Label
var _detail: Label
var _days: Array[Button] = []

func _ready() -> void:
	layer = 15
	scale = Vector2(2, 2)   # the interface is laid out for 320x180; the screen is 640x360
	_panel = Panel.new()
	_panel.position = Vector2(10, 6)
	_panel.size = Vector2(300, 168)
	var style := StyleBoxFlat.new()
	style.bg_color = Color("192c3b")
	style.border_color = Color("6ebcc2")
	style.set_border_width_all(2)
	_panel.add_theme_stylebox_override("panel", style)
	add_child(_panel)
	_heading = _label(Vector2(10, 5), Vector2(245, 12), 10)
	_button("X", Vector2(274, 4), Vector2(20, 16), close)
	_button("<", Vector2(8, 21), Vector2(22, 15), func(): _cycle(-1))
	_button("Today", Vector2(123, 21), Vector2(54, 15), func(): show_day(today))
	_button(">", Vector2(270, 21), Vector2(22, 15), func(): _cycle(1))
	for i in 7:
		var label := _label(Vector2(10 + i * 40, 39), Vector2(40, 10), 8)
		label.text = WEEK[i]
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	for i in 28:
		var index: int = i
		var button := _button("", Vector2(10 + (i % 7) * 40, 51 + (i / 7) * 19), Vector2(38, 17), func(): select_day(cycle_start + index))
		_days.append(button)
	_detail = _label(Vector2(10, 129), Vector2(280, 35), 8)
	_detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	visible = false

func _label(pos: Vector2, extent: Vector2, size: int) -> Label:
	var l := Label.new()
	l.position = pos
	l.size = extent
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", Color("e4eee9"))
	_panel.add_child(l)
	return l

func _button(text: String, pos: Vector2, extent: Vector2, action: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.position = pos
	b.size = extent
	b.add_theme_font_size_override("font_size", 8)
	b.pressed.connect(action)
	_panel.add_child(b)
	return b

func show_day(day: int) -> void:
	today = maxi(day, 1)
	selected_day = today
	cycle_start = ((today - 1) / 28) * 28 + 1
	open = true
	visible = true
	_refresh()

func close() -> void:
	open = false
	visible = false

func _cycle(offset: int) -> void:
	cycle_start = maxi(1, cycle_start + 28 * offset)
	selected_day = cycle_start
	_refresh()

func select_day(day: int) -> void:
	selected_day = day
	_refresh()

static func events_for(day: int) -> Array[String]:
	var events: Array[String] = ["18:00 - community dinner, mess hall"]
	var weekday: int = (day - 1) % 7
	for who in MapData.VISITOR_DAYS:
		if weekday in MapData.VISITOR_DAYS[who]:
			events.append("%s visiting market" % who)
	return events

func _refresh() -> void:
	_heading.text = "STATION CALENDAR - Cycle %d" % ((cycle_start - 1) / 28 + 1)
	for i in 28:
		var day: int = cycle_start + i
		var visitor: bool = events_for(day).size() > 1
		_days[i].text = ("[%d]" if day == today else "%d") % day + ("*" if visitor else "")
		_days[i].modulate = Color("f7ca7c") if day == selected_day else Color.WHITE
	_detail.text = "%s, day %d%s\n%s" % [WEEK[(selected_day - 1) % 7], selected_day, " (today)" if selected_day == today else "", " | ".join(events_for(selected_day))]

func handle_input(event: InputEvent) -> void:
	if event.is_action_pressed("cancel") or event.is_action_pressed("interact"):
		close()
	elif event.is_action_pressed("move_left"):
		_cycle(-1)
	elif event.is_action_pressed("move_right"):
		_cycle(1)
