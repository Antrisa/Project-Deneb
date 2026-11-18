extends Node2D
# A door between two rooms of the same map (homes first). It slides open when the player or a resident
# comes near and shuts behind them. A bedroom door stays shut to the player until they are friends enough
# with its owner (main.gd decides that and sets `locked`).
# entry: [map, x, y, w, h, facing, owner, room]. facing "S" is a door in a wall running east-west (you walk
# through it north-south); "E" is a door in a wall running north-south.

const FRONT_FRAME = preload("res://art/lunar/inner_door_s_frame.png")
const FRONT_LEAF = preload("res://art/lunar/inner_door_s_leaf.png")
const SIDE_FRAME = preload("res://art/lunar/inner_door_side_frame.png")
const SIDE_LEAF = preload("res://art/lunar/inner_door_side_leaf.png")
const ACCESS_READY = preload("res://art/lunar/door_access_ready.png")
const ACCESS_LOCKED = preload("res://art/lunar/door_access_locked.png")

var area := ""
var tiles: Array[Vector2i] = []
var facing := "S"
var room_owner := ""
var room := ""
var locked := false:
	set(value):
		if locked != value:
			locked = value
			queue_redraw()
var opening := 0.0           # 0 shut, 1 open
var size_px := Vector2.ZERO

func setup(e: Array) -> void:
	area = e[0]; facing = e[5]; room_owner = e[6]; room = e[7]
	var x: int = int(e[1]); var y: int = int(e[2]); var w: int = int(e[3]); var h: int = int(e[4])
	for yy in range(y, y + h):
		for xx in range(x, x + w):
			tiles.append(Vector2i(xx, yy))
	position = Vector2(x * 16, y * 16)
	size_px = Vector2(w * 16, h * 16)
	z_index = 0
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST

func center() -> Vector2:
	return position + size_px * 0.5

func blocks() -> bool:
	return opening < 0.95

func _draw() -> void:
	var light := ACCESS_LOCKED if locked else ACCESS_READY
	if facing == "S":
		# The 16-pixel passage is centered on the 20-pixel frame.
		var shown := roundf(8.0 * (1.0 - opening))
		if shown > 0.0:
			var source := Rect2(16 - shown * 2, 0, shown * 2, 56)
			var leaf := Rect2(0, -12, shown, 28)
			draw_texture_rect_region(FRONT_LEAF, leaf, source)
			draw_set_transform(Vector2(16, 0), 0.0, Vector2(-1, 1))
			draw_texture_rect_region(FRONT_LEAF, leaf, source)
			draw_set_transform(Vector2.ZERO)
		draw_texture_rect(FRONT_FRAME, Rect2(-2, -21, 20, 37), false)
		draw_texture_rect(light, Rect2(6, -17, 4, 2), false)
	else:
		# The panel rises into the housing. Only its visible portion is drawn.
		var shown := roundf(35.0 * (1.0 - opening))
		if shown > 0.0:
			draw_texture_rect_region(SIDE_LEAF, Rect2(6, -6, 5, shown),
				Rect2(0, 70 - shown * 2, 10, shown * 2))
		draw_texture_rect(SIDE_FRAME, Rect2(4, -14, 8, 46), false)
		draw_texture_rect(light, Rect2(6, -11, 4, 2), false)
