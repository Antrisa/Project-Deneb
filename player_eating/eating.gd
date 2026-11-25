extends Node2D

signal eating_started
## Fired once, just as the held item disappears and the player's hand reaches the mouth.
signal bite
signal eating_finished

const DIRECTIONS := [&"south", &"north", &"west", &"east"]
const LAYERS := [&"bottoms", &"faces", &"tops", &"hair", &"arm"]
const SHADER := preload("res://player_eating/tint.gdshader")
const EXAMPLE_FOOD := preload("res://player_eating/ration_6.png")
const FRAMES := [0.10, 0.24, 0.12, 0.12]
const FOOD_CENTERS := [
	[Vector2i(-12, -36), Vector2i(-6, -48)],
	[Vector2i(11, -36), Vector2i(5, -48)],
	[Vector2i(-13, -35), Vector2i(-7, -48)],
	[Vector2i(12, -35), Vector2i(6, -48)],
]
const ATLAS := [
	[
		[preload("res://player_eating/body_1/bottoms.png"), preload("res://player_eating/body_1/bottoms_mask.png")],
		[preload("res://player_eating/body_1/faces.png"), preload("res://player_eating/body_1/faces_mask.png")],
		[preload("res://player_eating/body_1/tops.png"), preload("res://player_eating/body_1/tops_mask.png")],
		[preload("res://player_eating/body_1/hair.png"), preload("res://player_eating/body_1/hair_mask.png")],
		[preload("res://player_eating/body_1/arm.png"), preload("res://player_eating/body_1/arm_mask.png")]
	]
]   # one body since 24 Nov (body_2 retired)

@export_range(1, 1, 1) var body_type := 1
@export_range(0, 9, 1) var hair_style := 0
@export_range(0, 9, 1) var face_style := 0
@export_range(0, 9, 1) var top_style := 2
@export_range(0, 9, 1) var bottom_style := 1
@export var hair_color := Color8(130, 72, 46)
@export var skin_color := Color8(245, 184, 138)
@export var eye_color := Color8(66, 97, 58)
@export var top_color := Color8(88, 104, 106)
@export var bottom_color := Color8(81, 69, 75)

var is_eating := false
var _facing := 0
var _frame := 0
var _time_in_frame := 0.0
var _layers: Array[Sprite2D] = []
@onready var food: Sprite2D = $Food

func _ready() -> void:
	for layer_name in LAYERS:
		var part := Sprite2D.new()
		part.name = layer_name
		part.centered = false
		part.position = Vector2(-24, -63)
		var mat := ShaderMaterial.new()
		mat.shader = SHADER
		part.material = mat
		add_child(part)
		_layers.append(part)
	hide()
	set_process(false)

## Assign the selected character's style indices and colours before playing.
## Pass any food icon with a tightly cropped transparent background.
func play_eating(direction: StringName, item_icon: Texture2D = EXAMPLE_FOOD) -> bool:
	var facing := DIRECTIONS.find(direction)
	if is_eating or facing < 0 or item_icon == null or not is_node_ready():
		return false
	if body_type < 1 or body_type > ATLAS.size():
		return false
	var styles := [bottom_style, face_style, top_style, hair_style, top_style]
	for style in styles:
		if style < 0 or style > 9:
			return false
	_facing = facing
	var fabrics := [bottom_color, skin_color, top_color, hair_color, top_color]
	for i in _layers.size():
		var part := _layers[i]
		var pair: Array = ATLAS[body_type - 1][i]
		part.texture = pair[0]
		part.hframes = 4
		part.vframes = int(part.texture.get_height() / 68)
		var mat := part.material as ShaderMaterial
		mat.set_shader_parameter("tint_mask",pair[1])
		mat.set_shader_parameter("fabric",fabrics[i])
		mat.set_shader_parameter("skin",skin_color)
		mat.set_shader_parameter("eyes",eye_color)
		var style: int = styles[i] if part.vframes > 4 else 0
		part.frame_coords = Vector2i(_facing, style * 4)
	# Echo Landing: the layers are stacked by drawing order instead of z_index (the pack used 0, 2, 4, 6, 8 and
	# 10 for the food), because a z_index lifts the animation above the y-sorted residents and the roof edges
	# that should cover the player. Bottoms, face, top, hair, arm, food; from behind, the arm goes under the hair.
	for part in _layers:
		move_child(part, -1)
	if _facing == 1:
		move_child(_layers[4], _layers[3].get_index())
	food.z_index = 0
	move_child(food, -1)
	food.texture = item_icon
	var size_px := item_icon.get_size()
	var ratio := minf(1.0, minf(13.0 / maxf(size_px.x, 1.0), 14.0 / maxf(size_px.y, 1.0)))
	food.scale = Vector2(ratio, ratio)
	_frame = 0
	_time_in_frame = 0.0
	is_eating = true
	_show_frame()
	show()
	set_process(true)
	eating_started.emit()
	return true

func _show_frame() -> void:
	for layer in _layers:
		var row := layer.frame_coords.y
		layer.frame_coords = Vector2i(_facing, row - row % 4 + _frame)
	food.visible = _frame < 2
	if food.visible:
		var center: Vector2i = FOOD_CENTERS[_facing][_frame]
		var half_size := (food.texture.get_size() * food.scale * 0.5).floor()
		food.position = Vector2(center) - half_size

func _process(delta: float) -> void:
	if not is_eating:
		return
	_time_in_frame += delta
	while is_eating and _time_in_frame >= float(FRAMES[_frame]):
		_time_in_frame -= float(FRAMES[_frame])
		_frame += 1
		if _frame == FRAMES.size():
			is_eating = false
			hide()
			set_process(false)
			eating_finished.emit()
			return
		_show_frame()
		if _frame == 2:
			bite.emit()
