extends CanvasLayer
# Dialogue box at the bottom of the screen.
# main.gd calls start(), advance() and cancel().
# start() can be given a portrait texture to show beside the text.
# If start() is given on_yes, the last line becomes a yes/no question:
# advancing accepts (and calls on_yes), cancel() declines.

# A line may start with one of these in square brackets to pick the speaker's expression,
# for example "[happy] Good morning!". The order matches the pictures in each portrait file.
const EMOTES := ["neutral", "happy", "sad", "surprised", "love", "angry"]

const NineFrame = preload("res://scripts/nine_frame.gd")

var active := false
var voice_pitch := 1.0        # set by main.gd before start(): each resident talks at their own pitch

var _lines: Array = []
var _index := 0
var _shown := 0.0
var _on_yes: Callable = Callable()
var _on_no: Callable = Callable()
var _blip: AudioStreamPlayer
var _blipped := 0
var _panel: Control
var _speaker: Label
var _text: Label
var _choice: Label
var _portrait: Sprite2D        # the speaker's face; the art file holds six expressions side by side
var _portrait_back: ColorRect
var _portrait_frame: Control
var _current := ""            # the line being shown, without its expression tag


func _ready() -> void:
	layer = 10
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
	_blip = AudioStreamPlayer.new()
	_blip.stream = load("res://audio/blip.wav")
	_blip.volume_db = -8.0
	add_child(_blip)
	visible = false


func _make_label(pos: Vector2, size: Vector2, color: Color) -> Label:
	var l := Label.new()
	l.position = pos
	l.size = size
	l.add_theme_font_size_override("font_size", 8)
	l.add_theme_color_override("font_color", color)
	_panel.add_child(l)
	return l


func start(speaker: String, lines: Array, on_yes: Callable = Callable(), yes_text: String = "", portrait: Texture2D = null,
		on_no: Callable = Callable(), no_text: String = "Not now") -> void:
	# With a portrait, the text moves right to make room for it.
	var left := 6.0
	if portrait != null:
		left = 74.0
		_portrait.texture = portrait
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
	_lines = lines
	_index = 0
	_on_yes = on_yes
	_on_no = on_no
	_speaker.text = speaker
	_choice.text = "[E] %s     [Q] %s" % [yes_text, no_text]
	active = true
	visible = true
	_show_line()


func advance() -> void:
	var line: String = _current
	if int(_shown) < line.length():
		_shown = float(line.length())   # finish typing first
		_text.visible_characters = -1
		return
	_index += 1
	if _index >= _lines.size():
		active = false
		visible = false
		if _on_yes.is_valid():
			var cb: Callable = _on_yes
			_on_yes = Callable()
			cb.call()
	else:
		_show_line()


func cancel() -> void:
	if not active:
		return
	if _on_yes.is_valid() and _index == _lines.size() - 1:
		_on_yes = Callable()
		active = false
		visible = false
		if _on_no.is_valid():
			var cb: Callable = _on_no
			_on_no = Callable()
			cb.call()


func _show_line() -> void:
	var line: String = _lines[_index]
	# An expression tag at the start picks the portrait picture and is not shown.
	var emote := 0
	if line.begins_with("["):
		var close: int = line.find("]")
		if close > 0:
			emote = maxi(0, EMOTES.find(line.substr(1, close - 1)))
			line = line.substr(close + 1).strip_edges()
	if _portrait.visible:
		_portrait.frame = emote
	_current = line
	_text.text = line
	_shown = 0.0
	_blipped = 0
	_text.visible_characters = 0
	_choice.visible = _on_yes.is_valid() and _index == _lines.size() - 1


func _process(delta: float) -> void:
	if not active:
		return
	var line: String = _current
	if int(_shown) < line.length():
		_shown += delta * 45.0
		_text.visible_characters = int(_shown)
		# A short blip every third letter, like a voice.
		if int(_shown) >= _blipped + 3:
			_blipped = int(_shown)
			_blip.pitch_scale = voice_pitch * randf_range(0.95, 1.05)
			_blip.play()
	else:
		_text.visible_characters = -1
