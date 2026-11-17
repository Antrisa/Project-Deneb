extends Node2D
var resident
var phase:=0.0
func _process(delta: float) -> void:
	phase+=delta
	if resident==null:return
	visible=resident._settled and resident._act in ["garden","chess","hologame","observe","read","browse","restock"]
	queue_redraw()
func _draw() -> void:
	if not visible:return
	var act: String=resident._act
	var direction: int=resident._facing
	var side: float=-1 if direction==2 else 1
	if act in ["chess","hologame"]:
		var tex: Texture2D=resident._walk_tex
		var fw: float=tex.get_width()/4.0
		var fh: float=tex.get_height()/3.0
		# Preserve each alien's head and upper-body art; bend the lower legs at the seat.
		draw_texture_rect_region(tex,Rect2(-8,-29,16,21),Rect2(direction*fw,0,fw,fh*21/32))
		draw_texture_rect_region(tex,Rect2(-5,-9,10,7),Rect2(direction*fw+fw*.2,fh*.66,fw*.6,fh*.22))
		if direction in [0,1]:
			for leg in [-4,2]:
				draw_rect(Rect2(leg,-7,4,6),Color("343d48"))
				draw_rect(Rect2(leg,-2,4,3),Color("212b37"))
		else:
			draw_rect(Rect2(side*5-3,-6,6,5),Color("343d48"))
			draw_rect(Rect2(side*7-3,-2,6,3),Color("212b37"))
		var reach:=maxf(0.0,sin(phase*1.7))*4
		draw_rect(Rect2(side*(6+reach)-2,-14,4,3),Color("c6aa88"))
		return
	if act=="garden":
		var at:=Vector2(side*9,-12+sin(phase*2))
		draw_rect(Rect2(at,Vector2(6,5)),Color("678d91"))
		draw_line(at+Vector2(5,1),at+Vector2(10,0),Color("c5d6ce"),2)
		for i in range(5):
			var t:=fmod(phase*1.2+i*.2,1.0)
			draw_rect(Rect2(at+Vector2(10+t*6,t*t*12),Vector2(1,2)),Color("93e6ea"))
	elif act=="read":
		draw_rect(Rect2(-7,-14,14,8),Color("b79266"))
		draw_rect(Rect2(-6,-13,5,6),Color("e6d7b3"));draw_rect(Rect2(1,-13,5,6),Color("e6d7b3"))
	elif act=="restock":
		var lift:=floorf((sin(phase*2)+1)*2)
		draw_rect(Rect2(-5,-13-lift,10,8),Color("b38d59"))
		draw_rect(Rect2(-2,-13-lift,3,8),Color("dfc18e"))
	elif act=="browse":
		draw_rect(Rect2(side*(7+sin(phase*2)*2)-2,-14,5,4),Color("deba87"))
	elif act=="observe":
		draw_rect(Rect2(side*7-3,-22,6,3),Color("a1b5bc"))
