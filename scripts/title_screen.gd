extends CanvasLayer
# The title screen: the animated opening from Echo_Landing_Title_Screen.zip (20 Nov) with the Play / Co-op /
# Settings / Quit buttons from the UI pack (title/menu_buttons.tscn, Echo_Landing_Complete_UI.zip).
# The opening (26 s) plays once, then the station loop (120 s) repeats; the theme starts on the first frame
# and loops on its own. The ECHO LANDING title fades in from 20.5 to 24.7 s with its three echo bars pulsing,
# as in the pack's index.html. The buttons fade in with it. Any key or click during the opening skips to the
# loop; M mutes the theme. Godot plays only Ogg Theora, so the pack's .mp4 clips were converted to .ogv. The buttons lay themselves out in screen
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

const INTRO := "res://title/intro/"
const DESIGN := Vector2(960, 540)          # the clips' canvas; the title sits at (557, 41) on it
const TITLE_AT := Vector2(557, 41)
const OPENING_SECONDS := 26.0
var _scene: Control
var _opening: VideoStreamPlayer
var _loop: VideoStreamPlayer
var _theme: AudioStreamPlayer
var _title_layers: Array[TextureRect] = []
var _time := 0.0                           # seconds since the opening started (the loop counts on from 26)
var _skipped := false


func _ready() -> void:
	layer = 90
	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_STOP
	_root.theme = load("res://title/menu_panel_theme.tres")
	add_child(_root)

	_build_intro()

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


func _build_intro() -> void:
	var black := ColorRect.new()
	black.color = Color("070717")
	black.set_anchors_preset(Control.PRESET_FULL_RECT)
	black.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(black)
	_scene = Control.new()
	_scene.set_anchors_preset(Control.PRESET_FULL_RECT)
	_scene.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_scene.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_root.add_child(_scene)
	_opening = _video("opening.ogv", false)
	_loop = _video("station_loop.ogv", true)
	_loop.visible = false
	for layer_name in ["title", "echo_bar_1", "echo_bar_2", "echo_bar_3"]:
		var path: String = INTRO + layer_name + ".png"
		if not ResourceLoader.exists(path):
			continue
		var layer := TextureRect.new()
		layer.texture = load(path)
		layer.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		layer.stretch_mode = TextureRect.STRETCH_SCALE
		layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
		layer.modulate.a = 0.0
		_scene.add_child(layer)
		_title_layers.append(layer)
	_scene.resized.connect(_place_intro)
	_place_intro.call_deferred()
	_theme = AudioStreamPlayer.new()
	if ResourceLoader.exists(INTRO + "theme.mp3"):
		var song: AudioStream = load(INTRO + "theme.mp3")
		if song is AudioStreamMP3:
			song.loop = true
		_theme.stream = song
	add_child(_theme)
	if _opening != null:
		_opening.finished.connect(_to_loop)
		_opening.play()
	else:
		_to_loop()
	_theme.play()


func _video(file: String, looping: bool) -> VideoStreamPlayer:
	if not ResourceLoader.exists(INTRO + file):
		return null
	var player := VideoStreamPlayer.new()
	player.stream = load(INTRO + file)
	player.expand = true
	player.loop = looping
	player.set_anchors_preset(Control.PRESET_FULL_RECT)
	player.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_scene.add_child(player)
	return player


# The title and echo bars keep their place on the 960x540 canvas the clips were made on.
func _place_intro() -> void:
	var k: float = _scene.size.x / DESIGN.x
	for layer in _title_layers:
		layer.position = TITLE_AT * k
		layer.size = layer.texture.get_size() * k


func _to_loop() -> void:
	if _opening != null:
		_opening.stop()
		_opening.visible = false
	if _time < OPENING_SECONDS:
		_time = OPENING_SECONDS
	if _loop != null:
		_loop.visible = true
		_loop.play()


func _process(delta: float) -> void:
	if not open:
		return
	_time += delta
	# The station's own music waits until play starts.
	if world != null and world.music != null:
		world.music.stream_paused = true
	var k: float = clampf((_time - 20.5) / 4.2, 0.0, 1.0)
	var alpha: float = k * k * k * (10.0 + k * (-15.0 + 6.0 * k))
	var phase: float = fposmod(_time - 20.5, 4.0)
	for i in _title_layers.size():
		if i == 0:
			_title_layers[i].modulate.a = alpha
		else:
			var v: float = clampf((phase - 0.05 - (i - 1) * 0.87) / 1.48, 0.0, 1.0)
			_title_layers[i].modulate.a = alpha * (0.22 + 0.78 * pow(sin(PI * v), 2.0))
	if _menu != null:
		_menu.modulate.a = alpha if _page == "" else 1.0


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
	if not open:
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_M:
		_theme.stream_paused = not _theme.stream_paused
		get_viewport().set_input_as_handled()
		return
	# Until the title has faded in, a key or click skips the opening instead of pressing a button.
	if _time < 24.7 and ((event is InputEventKey and event.pressed and not event.echo) or (event is InputEventMouseButton and event.pressed)):
		get_viewport().set_input_as_handled()
		_skip()
		return
	if _page != "" and event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_back()


func _skip() -> void:
	if _skipped:
		return
	_skipped = true
	_time = maxf(_time, 24.7)
	if _opening != null and _opening.is_playing():
		_to_loop()


func _play() -> void:
	open = false
	visible = false
	_theme.stop()
	if world != null and world.music != null:
		world.music.stream_paused = false
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
	_button("New game...", _open_new_game)
	_button("Back", _back)
	display.grab_focus()


# Settings > New game: erase the save and start over on the character screen (21 Nov, for testing the creator).
func _open_new_game() -> void:
	_begin("Settings", "Start a new game?")
	_label("This erases your save: the day, your items and credits, friendships, the farm and your look. You'll make a new character.").autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_button("Cancel", _open_settings).grab_focus()
	_button("Erase and start over", _erase_and_restart)


func _erase_and_restart() -> void:
	if world != null and world.has_method("_new_game"):
		world._new_game()


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
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN if enabled else DisplayServer.WINDOW_MODE_WINDOWED)


func _set_volume(volume: float) -> void:
	var master := AudioServer.get_bus_index("Master")
	AudioServer.set_bus_mute(master, volume <= 0.0)
	AudioServer.set_bus_volume_db(master, linear_to_db(maxf(volume, 0.001)))


func _volume_changed(amount: float) -> void:
	_set_volume(amount)
	_prefs.set_value("audio", "master", amount)
	_prefs.save(PREFS_PATH)
