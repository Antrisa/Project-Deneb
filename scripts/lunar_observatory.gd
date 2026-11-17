extends Node2D
# A wall-mounted, multi-pane window. Lunar terrain behind glass is separate from frame.
var phase := 0.0
func _process(delta: float) -> void:
	if is_visible_in_tree():phase+=delta;queue_redraw()
func _draw() -> void:
	var r:=Rect2(0,-52,160,52)
	draw_rect(r.grow(4),Color("3e485c"))
	draw_rect(r,Color("182638"))
	for i in range(28):
		var x:=float((i*53+17)%158);var y:=float((i*17+7)%24)-50
		draw_rect(Rect2(x,y,1,1),Color("d0e0df"))
	var terrain:=PackedVector2Array([Vector2(0,-18),Vector2(18,-29),Vector2(35,-21),Vector2(61,-33),Vector2(93,-17),Vector2(119,-28),Vector2(160,-18),Vector2(160,0),Vector2(0,0)])
	draw_colored_polygon(terrain,Color("8d8993"))
	for i in range(9):
		draw_set_transform(Vector2(10+i*17,-8-(i%3)*5),0,Vector2(1,.36))
		draw_circle(Vector2.ZERO,7,Color("666879"))
		draw_arc(Vector2.ZERO,7,0,PI,14,Color("beb7b6"),1)
	draw_set_transform(Vector2.ZERO)
	for x in [0,40,80,120,160]:
		draw_rect(Rect2(x-2,-53,4,56),Color("637687"))
		draw_line(Vector2(x+2,-48),Vector2(x+2,-4),Color("add6d4"),1)
	for x in [6,46,86,126]:draw_line(Vector2(x,-48),Vector2(x+17,-30),Color(0.6,0.9,1,0.22),2)
	draw_rect(Rect2(-3,0,166,5),Color("c3b49d"))
	for x in [12,52,92,132]:draw_rect(Rect2(x,2,16,1),Color("74dfd3"))
