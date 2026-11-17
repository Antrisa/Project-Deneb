extends Node2D
var phase := 0.0
func _process(delta: float) -> void:
	if is_visible_in_tree():
		phase+=delta
		queue_redraw()
func _draw() -> void:
	draw_set_transform(Vector2(0,-12),0,Vector2(1,0.56))
	draw_circle(Vector2.ZERO,47,Color("237a8c"))
	draw_circle(Vector2.ZERO,43,Color("35b5bb"))
	for i in range(3):
		var r := 14+fmod(phase*10+i*12,28)
		draw_arc(Vector2.ZERO,r,0,TAU,48,Color(0.65,1,0.96,0.5*(1-(r-14)/28)),1)
	draw_set_transform(Vector2.ZERO)
	# Six individually animated water streams land inside the collision basin.
	for side in [-1,1]:
		for i in range(3):
			var points := PackedVector2Array()
			for k in range(13):
				var t:=float(k)/12
				points.append(Vector2(side*(10+t*(19+i*5)),-40+t*(36+i*5)-sin(t*PI)*12))
			draw_polyline(points,Color("9cfaf1"),1.0)
			var t:=fmod(phase*0.9+i*0.3,1.0)
			draw_circle(Vector2(side*(10+t*(19+i*5)),-40+t*(36+i*5)-sin(t*PI)*12),1,Color("e9ffff"))
