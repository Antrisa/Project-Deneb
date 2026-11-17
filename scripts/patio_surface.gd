extends Node2D
# A continuous rounded terrace over the walkable grid, with a curved plaza approach.
var outline := PackedVector2Array()
var route := PackedVector2Array()
func _ready() -> void:
	outline.append(Vector2(133,73)*16)
	outline.append(Vector2(152,73)*16)
	for i in range(1,33):
		var angle := PI*float(i)/32.0
		outline.append((Vector2(142.5,73)+Vector2(9.5*cos(angle),10*sin(angle)))*16)
	for p in [Vector2(142,81),Vector2(139,84),Vector2(135,86),Vector2(131,88),Vector2(126,90),Vector2(121,91)]:route.append(p*16)
	queue_redraw()
func _draw() -> void:
	# Quiet composite flooring, not heavy repeating plank outlines.
	draw_polyline(route,Color("665f58"),45.0)
	draw_polyline(route,Color("ab9b83"),41.0)
	draw_colored_polygon(outline,Color("ab9b83"))
	var closed := outline.duplicate()
	closed.append(outline[0])
	draw_polyline(closed,Color("776e61"),2.0)
	for y in range(73*16+16,83*16,24):
		for x in range(132*16,153*16,32):
			var start := Vector2(x+2,y)
			var end := start+Vector2(28,0)
			if Geometry2D.is_point_in_polygon(start,outline) and Geometry2D.is_point_in_polygon(end,outline):
				draw_line(start,end,Color("9e907c"),1.0)
	# Embedded guide lights steer the player toward the entrance.
	for p in [Vector2(140,83),Vector2(136,86),Vector2(131,89)]:
		draw_rect(Rect2(p*16,Vector2(6,2)),Color("d8ba7c"))
