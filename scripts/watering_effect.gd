extends Node2D
var phase:=0.0
func _process(delta: float) -> void:
	phase+=delta;queue_redraw()
func _draw() -> void:
	for i in range(18):
		var t:=fmod(phase+i*.07,1.0)
		var pos:=Vector2((i%6-3)*4+t*4,-22+t*25)
		draw_rect(Rect2(pos,Vector2(1,2)),Color("96e6e3"))
