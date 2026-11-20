extends CanvasLayer
# The title screen: the painted title art with the Play / Co-op / Settings / Quit buttons from the 20 Nov UI
# pack (title/menu_buttons.tscn, Echo_Landing_Complete_UI.zip). The buttons lay themselves out in screen
# pixels like the datapad (2x at 1080p, 3x at 1440p), five percent in from the left (ui/pixel_grid.gd).
#
# Settings switches fullscreen and sets the master volume (kept in user://title_settings.cfg, as in the pack's
# own title scene); Quit asks first. The main game has no multiplayer yet, so Co-op only says so.
# main.gd keeps the game paused while `open` is true and starts play when `play_requested` fires.

signal play_requested

const PixelGrid = preload("res://ui/pixel_grid.gd")
const PREFS_PATH := "user://title_settings.cfg"

var open := true
var world                      # main.gd: its fullscreen switch keeps the window a whole multiple of 640x360
var _root: Control
var _menu                      # title/menu_buttons.gd
var _dialog: PanelContainer
var _fields: VBoxContainer
var _page := ""
var _prefs := ConfigFile.new()


func _ready() -> void:
	layer = 90
	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_STOP
	_root.theme = load("res://title/menu_panel_theme.tres")
	add_child(_root)

	# The painted backdrop, trimmed to 16:9 the way the pack's own title scene trims it.
	var art := AtlasTexture.new()
	art.atlas = load("res://art/ui/title_art.png")
	art.region = Rect2(16, 12, 1332, 749)
	art.filter_clip = true
	var back := TextureRect.new()
	back.texture = art
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	back.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	back.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(back)

	_menu = load("res://title/menu_buttons.tscn").instantiate()
	_root.add_child(_menu)
	_menu.play_requested.connect(_play)
	_menu.coop_requested.connect(_open_coop)
	_menu.settings_requested.connect(_open_settings)
	_menu.quit_requested.connect(_open_quit)

	_dialog = PanelContainer.new()
	_dialog.visible = false
	_dialog.custom_minimum_size = Vector2(200, 0)
	_root.add_child(_dialog)
	_fields = VBoxContainer.new()
	_fields.add_theme_constant_override("separation", 7)
	_dialog.add_child(_fields)
	_root.resized.connect(_place_dialog)
	get_viewport().size_changed.connect(_place_dialog)
	_dialog.resized.connect(_place_dialog)

	if _prefs.load(PREFS_PATH) == OK:
		_set_volume(float(_prefs.get_value("audio", "master", 1.0)))
		if _prefs.has_section_key("display", "fullscreen"):
			_set_fullscreen(bool(_prefs.get_value("display", "fullscreen")))


# Keys that are not the interface's own (arrows, Tab and Enter already move and press): W and S move,
# E presses. main.gd passes them here while the title is open.
func handle_input(event: InputEvent) -> void:
	if _page != "":
		return
	var buttons: Array = _menu.actions
	var at := 0
	for i in buttons.size():
		if buttons[i].has_focus():
			at = i
	if event.is_action_pressed("move_up", true):
		buttons[posmod(at - 1, buttons.size())].grab_focus()
	elif event.is_action_pressed("move_down", true):
		buttons[(at + 1) % buttons.size()].grab_focus()
	elif event.is_action_pressed("interact"):
		buttons[at].pressed.emit()


# Escape (or the controller's east button) closes a Settings, Co-op or Quit panel.
func _input(event: InputEvent) -> void:
	if open and _page != "" and event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_back()


func _play() -> void:
	open = false
	visible = false
	play_requested.emit()
	queue_free()


func _place_dialog() -> void:
	PixelGrid.place_left(_root, _dialog)


func _begin(button_name: String, heading: String) -> void:
	_page = button_name
	_menu.hide()
	for child in _fields.get_children():
		_fields.remove_child(child)
		child.queue_free()
	_dialog.show()
	_dialog.reset_size.call_deferred()
	_place_dialog.call_deferred()
	var title := _label(heading)
	title.add_theme_font_size_override("font_size", 16)


func _label(value: String) -> Label:
	var label := Label.new()
	label.text = value
	_fields.add_child(label)
	return label


func _button(caption: String, action: Callable) -> Button:
	var button := Button.new()
	button.text = caption
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	button.pressed.connect(action)
	_fields.add_child(button)
	return button


func _back() -> void:
	_dialog.hide()
	_menu.show()
	_menu.restore_focus(_page)
	_page = ""


func _open_settings() -> void:
	_begin("Settings", "Settings")
	var display := _button(_window_label(), _toggle_display)
	display.name = "DisplayMode"
	_label("Master volume")
	var volume := HSlider.new()
	volume.max_value = 1.0
	volume.step = 0.05
	volume.value = float(_prefs.get_value("audio", "master", 1.0))
	volume.value_changed.connect(_volume_changed)
	_fields.add_child(volume)
	_label("In game, Alt+Enter also switches fullscreen and M turns the music on or off.").autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_button("Back", _back)
	display.grab_focus()


func _open_coop() -> void:
	_begin("Coop", "Co-op")
	_label("Co-op isn't in this build yet.").autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_button("Back", _back).grab_focus()


func _open_quit() -> void:
	_begin("Quit", "Quit Echo Landing?")
	_button("Cancel", _back).grab_focus()
	_button("Quit game", get_tree().quit)


func _is_fullscreen() -> bool:
	return DisplayServer.window_get_mode() in [DisplayServer.WINDOW_MODE_FULLSCREEN, DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN]


func _window_label() -> String:
	return "Display: fullscreen" if _is_fullscreen() else "Display: windowed"


func _toggle_display() -> void:
	_set_fullscreen(not _is_fullscreen())
	_prefs.set_value("display", "fullscreen", _is_fullscreen())
	_prefs.save(PREFS_PATH)
	var display := _fields.get_node_or_null("DisplayMode") as Button
	if display != null:
		display.text = _window_label()


func _set_fullscreen(enabled: bool) -> void:
	if enabled == _is_fullscreen():
		return
	if world != null and world.has_method("_toggle_fullscreen"):
		world._toggle_fullscreen()
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if enabled else DisplayServer.WINDOW_MODE_WINDOWED)


func _set_volume(volume: float) -> void:
	var master := AudioServer.get_bus_index("Master")
	AudioServer.set_bus_mute(master, volume <= 0.0)
	AudioServer.set_bus_volume_db(master, linear_to_db(maxf(volume, 0.001)))


func _volume_changed(amount: float) -> void:
	_set_volume(amount)
	_prefs.set_value("audio", "master", amount)
	_prefs.save(PREFS_PATH)
