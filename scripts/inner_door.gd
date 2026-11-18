extends Node2D
# A door between two rooms of the same map (homes first). It slides open when the player or a resident
# comes near and shuts behind them. A bedroom door stays shut to the player until they are friends enough
# with its owner (main.gd decides that and sets `locked`).
# entry: [map, x, y, w, h, facing, owner, room]. facing "S" is a door in a wall running east-west (you walk
# through it north-south); "E" is a door in a wall running north-south.

var area := ""
var tiles: Array[Vector2i] = []
var facing := "S"
var owner := ""
var room := ""
var locked := false
var opening := 0.0           # 0 shut, 1 open
var size_px := Vector2.ZERO

func setup(e: Array) -> void:
	area = e[0]; facing = e[5]; owner = e[6]; room = e[7]
	var x: int = int(e[1]); var y: int = int(e[2]); var w: int = int(e[3]); var h: int = int(e[4])
	for yy in range(y, y + h):
		for xx in range(x, x + w):
			tiles.append(Vector2i(xx, yy))
	position = Vector2(x * 16, y * 16)
	size_px = Vector2(w * 16, h * 16)
	z_index = 0

func center() -> Vector2:
	return position + size_px * 0.5

func blocks() -> bool:
	return opening < 0.95

func _draw() -> void:
	var frame := Color("4a5568")
	var leaf := Color("b9b2a3")
	var edge := Color("7d7668")
	var light := Color("d47972") if locked else Color("91d8bc")
	if facing == "S":
		# Seen from the front: two leaves sliding apart inside a frame that stands on the doorway.
		var w := size_px.x
		var top := -18.0
		var h := 16.0 - top
		draw_rect(Rect2(-2, top - 3, w + 4, 3), frame)
		draw_rect(Rect2(-2, top, 2, h), frame)
		draw_rect(Rect2(w, top, 2, h), frame)
		var half := w * 0.5 * (1.0 - opening)
		if half > 0.5:
			draw_rect(Rect2(0, top, half, h), leaf)
			draw_rect(Rect2(w - half, top, half, h), leaf)
			draw_rect(Rect2(half - 1, top, 1, h), edge)
			draw_rect(Rect2(w - half, top, 1, h), edge)
		draw_rect(Rect2(w * 0.5 - 2, top - 2, 4, 1), light)
	else:
		# Seen side-on: a thin door in a north-south wall, sliding up into the wall above.
		var hgt := size_px.y
		var x0 := 6.0
		draw_rect(Rect2(x0 - 1, -14, 6, 2), frame)
		var shown := (hgt + 12.0) * (1.0 - opening)
		if shown > 0.5:
			draw_rect(Rect2(x0, hgt - shown, 4, shown), leaf)
			draw_rect(Rect2(x0 + 3, hgt - shown, 1, shown), edge)
		draw_rect(Rect2(x0 + 1, -12, 2, 2), light)
