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
			var lk: float = FRONT_LEAF.get_width() / 8.0          # the leaf picture's pixels per unit
			var source := Rect2(FRONT_LEAF.get_width() - shown * lk, 0, shown * lk, FRONT_LEAF.get_height())
			var leaf := Rect2(0, -11, shown, 27)
			draw_texture_rect_region(FRONT_LEAF, leaf, source)
			draw_set_transform(Vector2(16, 0), 0.0, Vector2(-1, 1))
			draw_texture_rect_region(FRONT_LEAF, leaf, source)
			draw_set_transform(Vector2.ZERO)
		# Fills the wall face exactly, from its foot (the bottom of the door tile) up to its lip.
		draw_texture_rect(FRONT_FRAME, Rect2(-2, -16, 20, 32), false)
		draw_texture_rect(light, Rect2(6, -15, 4, 2), false)
	else:
		# The panel rises into the housing. Only its visible portion is drawn.
		# Fills the gap in the wall's top exactly: the full width of the wall, down to where the next wall's
		# top starts (4 units short of the door's tiles).
		var gap := size_px.y - 4.0
		var room := gap - 4.0
		var shown := roundf(room * (1.0 - opening))
		if shown > 0.0:
			var lk: float = SIDE_LEAF.get_height() / room
			draw_texture_rect_region(SIDE_LEAF, Rect2(3, 2, 10, shown),
				Rect2(0, SIDE_LEAF.get_height() - shown * lk, SIDE_LEAF.get_width(), shown * lk))
		draw_texture_rect(SIDE_FRAME, Rect2(0, 0, 16, gap), false)
		draw_texture_rect(light, Rect2(6, 0.5, 4, 2), false)
