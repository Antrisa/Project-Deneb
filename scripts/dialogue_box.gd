extends CanvasLayer
# The talk box: who's speaking, their portrait, the line typing out, and any choices, listed inside the box.
# main.gd calls start(), advance() and cancel(); cutscenes (scripts/cutscene.gd) also start_choice().
# start() can be given a portrait texture to show beside the text.
# If start() is given on_yes, the last line becomes a question with two answers listed under it, yes_text and
# no_text: advancing takes the highlighted one (yes to begin with), cancel() says no.
#
# Since 24 Nov (Zachary: the chat windows were "in the old code generated blue style not the creme orange UI color
# scheme", the options "should be in the text window where the NPCs talk like stardew", and people in cutscenes
# walked behind the box) the box is drawn by a datapad of its own (datapad/datapad.gd _talk), in the datapad's
# cream and orange, and sits at the foot of the screen, or at the top when the people in the scene are down there.
# Choices are picked with up and down (or the mouse wheel), 1 to 4, or the mouse, and taken with a click or E.
# If the datapad can't be loaded, the old blue box below still works.

# A line may start with one of these in square brackets to pick the speaker's expression,
# for example "[happy] Good morning!". The order matches the pictures in each portrait file.
# The 20 Nov portraits have a seventh picture, "shocked"; older six-picture files show neutral for it.
# "bashful" is another name for the fifth picture (the new art draws it as bashful rather than love).
const EMOTES := ["neutral", "happy", "sad", "surprised", "love", "angry", "shocked"]
const EMOTE_ALIASES := {"bashful": 4}

const NineFrame = preload("res://scripts/nine_frame.gd")
const PAD_SCENE := "res://datapad/datapad.tscn"

var active := false
var voice_pitch := 1.0        # set by main.gd before start(): each resident talks at their own pitch
var on_done: Callable = Callable()   # optional: called when the lines run out (set after start(); main.gd _say_then)
var world = null              # main.gd, to keep the box off the people in a scene

var _lines: Array = []
var _index := 0
var _shown := 0.0
var _on_yes: Callable = Callable()
var _on_no: Callable = Callable()
var _on_pick: Callable = Callable()    # start_choice(): called with the number of the choice taken
var _options: Array = []      # the choices listed on the last line ([yes_text, no_text] for a yes/no question)
var _option_at := 0
var _top := false             # the box is at the top of the screen for this line
var _blip: AudioStreamPlayer
var _blipped := 0
var _current := ""            # the line being shown, without its expression tag
var _speaker_name := ""
var _emote := 0
var _portrait_tex: Texture2D = null
var _pad = null               # the datapad that draws the box
var _pushed := {}

# the old box, used only without the datapad
var _panel: Control
var _speaker: Label
var _text: Label
var _choice: Label
var _portrait: Sprite2D        # the speaker's face; the art file holds six or seven square expressions side by side
var _portrait_back: ColorRect
var _portrait_frame: Control


func _ready() -> void:
	layer = 10
	_blip = AudioStreamPlayer.new()
	# One soft note per text box (Zachary, 23 Nov: the per-letter blips were "a bit annoying"). A real sound saved
	# as audio/talk.ogg replaces the made-up one.
	_blip.stream = load("res://audio/talk.ogg") if ResourceLoader.exists("res://audio/talk.ogg") else load("res://audio/talk.wav")
	_blip.volume_db = -10.0
	add_child(_blip)
	if ResourceLoader.exists(PAD_SCENE):
		_pad = load(PAD_SCENE).instantiate()
		_pad.hud_hidden = true            # this one draws the talk box and nothing else
		_pad.catalog = {}
		_pad.extra_textures = {}
		add_child(_pad)
		_pad.set_process_input(false)
		_pad.set_process_unhandled_input(false)
		_pad.mouse_filter = Control.MOUSE_FILTER_IGNORE
		visible = true
		return
	_build_old_box()
	visible = false


# ---------------------------------------------------------------- starting and moving on

func start(speaker: String, lines: Array, on_yes: Callable = Callable(), yes_text: String = "", portrait: Texture2D = null,
		on_no: Callable = Callable(), no_text: String = "Not now") -> void:
	_begin(speaker, lines, portrait)
	_on_yes = on_yes
	_on_no = on_no
	_options = [yes_text if yes_text != "" else "Yes", no_text] if on_yes.is_valid() else []
	_show_line()


# A question with any number of answers (a cutscene's choices): on_pick gets the number of the one taken. With no
# lines, the last line shown is asked again.
func start_choice(speaker: String, lines: Array, options: Array, on_pick: Callable, portrait: Texture2D = null) -> void:
	if lines.is_empty():
		lines = [("[%s] " % EMOTES[_emote] if _emote > 0 else "") + _current]
		speaker = _speaker_name
		portrait = _portrait_tex
	_begin(speaker, lines, portrait)
	_on_pick = on_pick
	_options = options.duplicate()
	_show_line()


func _begin(speaker: String, lines: Array, portrait: Texture2D) -> void:
	on_done = Callable()
	_on_yes = Callable()
	_on_no = Callable()
	_on_pick = Callable()
	_options = []
	_option_at = 0
	_lines = lines
	_index = 0
	_speaker_name = speaker
	_portrait_tex = portrait
	active = true
	if _pad == null:
		_old_start(speaker, portrait)


# For scenes that turn lines over by themselves (cutscene.gd "say_timed").
func line_index() -> int:
	return _index


func turn_line() -> void:
	_shown = float(_current.length())
	advance()


func advance() -> void:
	if int(_shown) < _current.length():
		_shown = float(_current.length())   # finish typing first
		_push()
		return
	if _choosing():
		_pick(_option_at)
		return
	_index += 1
	if _index >= _lines.size():
		_close()
		if on_done.is_valid():
			var done: Callable = on_done
			on_done = Callable()
			done.call()
	else:
		_show_line()


func cancel() -> void:
	if not active:
		return
	if _on_yes.is_valid() and not _options.is_empty() and _index == _lines.size() - 1:
		_pick(1)                         # a yes/no question: cancel says no, even while the line is typing


func _pick(i: int) -> void:
	if i < 0 or i >= _options.size():
		return
	if world != null:
		world.sfx("click")
	var yes: Callable = _on_yes
	var no: Callable = _on_no
	var pick: Callable = _on_pick
	_on_yes = Callable()
	_on_no = Callable()
	_on_pick = Callable()
	_close()
	if pick.is_valid():
		pick.call(i)
	elif i == 0 and yes.is_valid():
		yes.call()
	elif i == 1 and no.is_valid():
		no.call()


func _close() -> void:
	active = false
	_options = []
	if _pad != null:
		_pad.talk = {}
		_pushed = {}
		_pad.refresh()
	else:
		visible = false


func _choosing() -> bool:
	return active and not _options.is_empty() and _index == _lines.size() - 1 and int(_shown) >= _current.length()


func _show_line() -> void:
	var line: String = str(_lines[_index])
	# An expression tag at the start picks the portrait picture and is not shown.
	_emote = 0
	if line.begins_with("["):
		var close: int = line.find("]")
		if close > 0:
			var tag: String = line.substr(1, close - 1)
			_emote = int(EMOTE_ALIASES.get(tag, maxi(0, EMOTES.find(tag))))
			line = line.substr(close + 1).strip_edges()
	_current = line
	_shown = 0.0
	_blipped = 0
	if line != "":
		_blip.pitch_scale = voice_pitch          # each resident's note at their own pitch
		_blip.play()
	_top = _box_on_top()
	if _pad != null:
		_push()
	else:
		_old_show_line()


# ---------------------------------------------------------------- where the box goes
# Stardew moves the box out of the way: if the people in a scene are at the foot of the screen, where the box
# would hide them, and the top is clearer, the box goes to the top for this line.
func _box_on_top() -> bool:
	if world == null or _pad == null:
		return false
	if world.cutscene != null and world.cutscene.running and world.cutscene.board_up():
		return world.cutscene.board_box_top    # a picture panel: where the scene says (the prologue: top)
	var people: Array = []
	if world.player != null:
		people.append(world.player)
	if world.cutscene != null and world.cutscene.running:
		for r in world.cutscene._actors.values():
			if is_instance_valid(r) and r.visible:
				people.append(r)
		if world.cutscene._holo != null and is_instance_valid(world.cutscene._holo) and world.cutscene._holo.visible:
			people.append(world.cutscene._holo)
	if people.size() <= 1 and not (world.cutscene != null and world.cutscene.running):
		return false                     # an everyday chat: you and them in the middle of the screen
	_push_text_only()                    # the box's size depends on the line, so measure it with this one
	var bottom: Rect2 = _pad.talk_canvas_rect(false)
	var top: Rect2 = _pad.talk_canvas_rect(true)
	var hidden_bottom := 0
	var hidden_top := 0
	for n in people:
		var feet: Vector2 = (n as CanvasItem).get_global_transform_with_canvas().origin
		var body := Rect2(feet.x - 10.0, feet.y - 46.0, 20.0, 48.0)
		if body.intersects(bottom):
			hidden_bottom += 1
		if body.intersects(top):
			hidden_top += 1
	return hidden_bottom > hidden_top


# ---------------------------------------------------------------- drawing (the datapad)

func _talk_state() -> Dictionary:
	var d := {
		"speaker": _speaker_name,
		"text": _current,
		"shown": int(_shown),
		"top": _top,
		"done": int(_shown) >= _current.length(),
		"options": _options if _index == _lines.size() - 1 else [],
		"at": _option_at,
		"portrait": "",
	}
	if _portrait_tex != null:
		_pad.extra_textures["talk_portrait"] = _portrait_tex
		d["portrait"] = "talk_portrait"
		var frames: int = maxi(1, _portrait_tex.get_width() / maxi(1, _portrait_tex.get_height()))
		d["frames"] = frames
		d["frame"] = _emote if _emote < frames else 0
	return d


func _push() -> void:
	if _pad == null or not active:
		return
	var d := _talk_state()
	if d == _pushed:
		return
	_pushed = d
	_pad.talk = d
	_pad.refresh()


func _push_text_only() -> void:
	# what the box will hold for this line, so its size can be measured before it's shown
	_pad.talk = _talk_state()


func _process(delta: float) -> void:
	if not active:
		return
	if int(_shown) < _current.length():
		_shown = minf(_shown + delta * 45.0, float(_current.length()))
		if _pad != null:
			_push()
		else:
			_text.visible_characters = int(_shown)
	elif _pad == null:
		_text.visible_characters = -1
		_choice.visible = _choosing()


# ---------------------------------------------------------------- choosing with keys and the mouse
# The choices take up and down, the mouse wheel, 1 to 4 and the mouse pointer themselves; a click or E (which
# main.gd and cutscene.gd send to advance()) takes the highlighted one, and right-click (cancel) says no.

func _input(event: InputEvent) -> void:
	if not _choosing():
		return
	var moved := false
	if event.is_action_pressed("move_up"):
		_option_at = (_option_at + _options.size() - 1) % _options.size()
		moved = true
	elif event.is_action_pressed("move_down"):
		_option_at = (_option_at + 1) % _options.size()
		moved = true
	elif event is InputEventKey and event.pressed and not event.echo:
		var k: int = (event as InputEventKey).physical_keycode
		if k >= KEY_1 and k < KEY_1 + mini(_options.size(), 9):
			get_viewport().set_input_as_handled()
			_pick(k - KEY_1)
			return
	elif event is InputEventMouseButton and event.pressed:
		var b: int = (event as InputEventMouseButton).button_index
		if b == MOUSE_BUTTON_WHEEL_UP:
			_option_at = (_option_at + _options.size() - 1) % _options.size()
			moved = true
		elif b == MOUSE_BUTTON_WHEEL_DOWN:
			_option_at = (_option_at + 1) % _options.size()
			moved = true
		elif b == MOUSE_BUTTON_LEFT and _pad != null:
			var under: int = _pad.talk_option_at((event as InputEventMouseButton).position)
			if under >= 0:
				_option_at = under          # the click itself goes on to advance(), which takes it
				_push()
	elif event is InputEventMouseMotion and _pad != null:
		var hover: int = _pad.talk_option_at((event as InputEventMouseMotion).position)
		if hover >= 0 and hover != _option_at:
			_option_at = hover
			_push()
		return
	if moved:
		get_viewport().set_input_as_handled()
		if _pad != null:
			_push()
		else:
			_old_choice_text()


# ---------------------------------------------------------------- the old box (no datapad)

func _build_old_box() -> void:
	scale = Vector2(2, 2)   # the interface is laid out for 320x180; the screen is 640x360
	# The box is drawn from art/ui_dialogue.png (see scripts/nine_frame.gd).
	var box = NineFrame.new()
	box.tex = load("res://art/ui_dialogue.png")
	_panel = box
	_panel.position = Vector2(8, 104)
	_panel.size = Vector2(304, 72)
	add_child(_panel)
	# The portrait sits in a 64x64 box. Art of any size is scaled to fit it (128x128 art shows at double detail).
	_portrait_back = ColorRect.new()
	_portrait_back.color = Color(0.13, 0.18, 0.32)
	_portrait_back.position = Vector2(4, 4)
	_portrait_back.size = Vector2(64, 64)
	_portrait_back.visible = false
	_panel.add_child(_portrait_back)
	_portrait = Sprite2D.new()
	_portrait.centered = false
	_portrait.hframes = EMOTES.size()
	_portrait.position = Vector2(4, 4)
	_portrait.visible = false
	_panel.add_child(_portrait)
	var border = NineFrame.new()
	border.tex = load("res://art/ui_portrait_frame.png")
	border.corner = 4.0
	_portrait_frame = border
	_portrait_frame.position = Vector2(2, 2)
	_portrait_frame.size = Vector2(68, 68)
	_portrait_frame.visible = false
	_panel.add_child(_portrait_frame)
	_speaker = _make_label(Vector2(6, 2), Vector2(292, 11), Color("7fd4ff"))
	_text = _make_label(Vector2(6, 14), Vector2(292, 44), Color.WHITE)
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_choice = _make_label(Vector2(6, 59), Vector2(292, 11), Color("ffd27f"))
	_choice.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT


func _make_label(pos: Vector2, size: Vector2, color: Color) -> Label:
	var l := Label.new()
	l.position = pos
	l.size = size
	l.add_theme_font_size_override("font_size", 8)
	l.add_theme_color_override("font_color", color)
	_panel.add_child(l)
	return l


func _old_start(speaker: String, portrait: Texture2D) -> void:
	var left := 6.0
	if portrait != null:
		left = 74.0
		_portrait.texture = portrait
		_portrait.hframes = maxi(1, portrait.get_width() / maxi(1, portrait.get_height()))
		_portrait.frame = 0
		var fit: float = 64.0 / portrait.get_height()
		_portrait.scale = Vector2(fit, fit)
	_portrait.visible = portrait != null
	_portrait_back.visible = portrait != null
	_portrait_frame.visible = portrait != null
	_speaker.position.x = left
	_text.position.x = left
	_text.size = Vector2(298.0 - left, 44)
	_choice.position.x = left
	_choice.size.x = 298.0 - left
	_speaker.text = speaker
	visible = true


func _old_show_line() -> void:
	if _portrait.visible:
		_portrait.frame = _emote if _emote < _portrait.hframes else 0
	_text.text = _current
	_text.visible_characters = 0
	_old_choice_text()
	_choice.visible = false


func _old_choice_text() -> void:
	var parts: Array = []
	for i in _options.size():
		parts.append(("> " if i == _option_at else "") + str(_options[i]))
	_choice.text = "   ".join(PackedStringArray(parts))
