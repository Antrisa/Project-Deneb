extends CanvasLayer
# The title screen, from Zachary's 20 Nov UI pack ("Terran_Datapad_Godot.zip", folder title/):
# the painted title art behind a Play / Co-op / Settings / Quit stack.
#
# The pack lays the stack out on a 768x432 canvas; the game's canvas is 640x360, so the buttons are placed
# here at their own size (150x33, one art pixel per screen pixel, so they stay crisp) where the pack puts them:
# five percent in from the left, the stack centred 46 percent of the way down. The painted backdrop is
# scaled to cover the screen.
#
# main.gd keeps the game paused while `open` is true and starts play when `play_requested` fires.
# The main game has no multiplayer yet, so Co-op only says so.

signal play_requested

const ART := "res://art/ui/title/"
const BUTTONS := ["play", "coop", "settings", "quit"]
const SIZE := Vector2(150, 33)
const GAP := 6.0

var open := true
var _buttons: Array[TextureButton] = []
var _note: Label
var _note_time := 0.0


func _ready() -> void:
	layer = 90
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(root)

	var back := TextureRect.new()
	back.texture = load("res://art/ui/title_art.png")
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	back.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	back.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR      # a large painting shown smaller
	back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(back)

	var stack: float = SIZE.y * BUTTONS.size() + GAP * (BUTTONS.size() - 1)
	var top: float = round(360.0 * 0.46 - stack / 2.0)
	for i in BUTTONS.size():
		var b := TextureButton.new()
		var id: String = BUTTONS[i]
		b.texture_normal = load(ART + id + "_idle.png")
		b.texture_pressed = load(ART + id + "_pressed.png")
		b.set_meta("idle", b.texture_normal)
		b.set_meta("focus", load(ART + id + "_focus.png"))
		b.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		b.position = Vector2(32, top + i * (SIZE.y + GAP))
		b.size = SIZE
		b.focus_mode = Control.FOCUS_ALL
		b.focus_entered.connect(_restyle.bind(b))
		b.focus_exited.connect(_restyle.bind(b))
		b.mouse_entered.connect(b.grab_focus)
		b.pressed.connect(_pressed.bind(id))
		root.add_child(b)
		_buttons.append(b)
	for i in _buttons.size():
		var b: TextureButton = _buttons[i]
		b.focus_neighbor_top = b.get_path_to(_buttons[posmod(i - 1, _buttons.size())])
		b.focus_neighbor_bottom = b.get_path_to(_buttons[(i + 1) % _buttons.size()])
		b.focus_previous = b.focus_neighbor_top
		b.focus_next = b.focus_neighbor_bottom

	_note = Label.new()
	_note.position = Vector2(32, top + BUTTONS.size() * (SIZE.y + GAP) + 4)
	_note.size = Vector2(400, 24)
	_note.add_theme_font_size_override("font_size", 14)      # the HUD's 8 at its 2x scale is 16 here
	_note.add_theme_color_override("font_color", Color(1.0, 0.86, 0.6))
	_note.add_theme_color_override("font_outline_color", Color(0.05, 0.05, 0.1))
	_note.add_theme_constant_override("outline_size", 3)
	_note.visible = false
	root.add_child(_note)
	_buttons[0].call_deferred("grab_focus")


# Keys that are not the interface's own (arrows and Enter already move and press): W/S move, E or Space presses.
# main.gd passes them here while the title is open.
func handle_input(event: InputEvent) -> void:
	var at: int = 0
	for i in _buttons.size():
		if _buttons[i].has_focus():
			at = i
	if event.is_action_pressed("move_up", true):
		_buttons[posmod(at - 1, _buttons.size())].grab_focus()
	elif event.is_action_pressed("move_down", true):
		_buttons[(at + 1) % _buttons.size()].grab_focus()
	elif event.is_action_pressed("interact") or event.is_action_pressed("use"):
		_pressed(BUTTONS[at])


func _restyle(b: TextureButton) -> void:
	b.texture_normal = b.get_meta("focus") if b.has_focus() else b.get_meta("idle")


func _pressed(id: String) -> void:
	match id:
		"play":
			open = false
			visible = false
			play_requested.emit()
			queue_free()
		"coop":
			_say("Co-op isn't in this build yet.")
		"settings":
			_say("Alt+Enter switches fullscreen. M turns the music on or off.")
		"quit":
			get_tree().quit()


func _say(text: String) -> void:
	_note.text = text
	_note.visible = true
	_note_time = 3.0


func _process(delta: float) -> void:
	if _note_time > 0.0:
		_note_time -= delta
		if _note_time <= 0.0:
			_note.visible = false
