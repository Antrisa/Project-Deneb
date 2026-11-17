extends Node2D
# Door frame and two independently clipped leaves, with a lit interior behind.
var opening := 0.0
var tex: Texture2D = preload("res://art/mess_hall/door.png")
var room: Texture2D = preload("res://art/mess_hall/window.png")
func region(src: Rect2, dest: Vector2) -> void:
	draw_texture_rect_region(tex,Rect2(dest,src.size*0.5),src)
func _draw() -> void:
	var s := tex.get_size()
	var left := floorf(s.x*0.24)
	var right := floorf(s.x*0.78)
	var top := floorf(s.y*0.40)
	var bottom := floorf(s.y*0.94)
	var mid := floorf((left+right)/2.0)
	var aperture := Rect2(left*0.5,top*0.5,(right-left)*0.5,(bottom-top)*0.5)
	# Deep amber inner room and a threshold, rather than an opaque placeholder.
	draw_rect(aperture,Color("554d40"))
	var rs := room.get_size()
	draw_texture_rect_region(room,aperture,Rect2(rs.x*0.24,rs.y*0.24,aperture.size.x*2,aperture.size.y*2))
	draw_rect(Rect2(aperture.position+Vector2(0,aperture.size.y-4),Vector2(aperture.size.x,4)),Color("86776b"))
	region(Rect2(0,0,s.x,top),Vector2.ZERO)
	region(Rect2(0,bottom,s.x,s.y-bottom),Vector2(0,bottom*0.5))
	region(Rect2(0,top,left,bottom-top),Vector2(0,top*0.5))
	region(Rect2(right,top,s.x-right,bottom-top),Vector2(right*0.5,top*0.5))
	var shift := floorf((mid-left)*opening)
	if mid-left-shift>0:
		region(Rect2(left+shift,top,mid-left-shift,bottom-top),Vector2(left*0.5,top*0.5))
	if right-mid-shift>0:
		region(Rect2(mid,top,right-mid-shift,bottom-top),Vector2((mid+shift)*0.5,top*0.5))
