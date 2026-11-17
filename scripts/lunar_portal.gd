extends Node2D
# A reusable portal component: separate frame, sliding leaves, light and approach marker.
var facing := "S"
var kind := "shop"
var destination := ""
var title := ""
var facade_width := 0.0
var opening := 0.0
var locked := false
var pulse := 0.0
var window: Texture2D = preload("res://art/lunar/home.png")
var panel: Texture2D = preload("res://art/lunar/material_2.png")
var metal: Texture2D = preload("res://art/lunar/material_6.png")
func setup(e: Array, facade: Array = []) -> void:
	position = Vector2(float(e[1])*16+8,float(e[2])*16+16)
	facing = e[6]; title = e[7];destination = e[3];locked = e[8]
	kind = "lift" if destination in ["top","eng"] or "lift" in title.to_lower() else "shop"
	if not facade.is_empty():
		kind = facade[6]
		facade_width = float(facade[4])*16 if facing in ["N","S"] else 0.0
func _process(delta: float) -> void:
	if not visible: return
	pulse += delta
	queue_redraw()
func _draw() -> void:
	var accent := Color("e9b65f")
	if destination == "medbay": accent = Color("91d8bc")
	elif destination == "fab": accent = Color("e5a56b")
	elif kind == "lift": accent = Color("78d6d0")
	if locked: accent = Color("d47972")
	# Inward-facing north entrances are under the near-side roof; do not paint a
	# south-facing storefront onto the back. Their lit threshold is readable from above.
	if facing == "N":
		draw_rect(Rect2(-20,-25,40,17),Color("424d60"))
		draw_rect(Rect2(-17,-24,34,4),accent)
		draw_rect(Rect2(-14,-19,28,9),Color("202b39"))
		var remain := 14.0*(1.0-opening)
		draw_rect(Rect2(-14,-18,remain,8),Color("8a9b9e"))
		draw_rect(Rect2(14-remain,-18,remain,8),Color("8a9b9e"))
		return
	if facing in ["E","W"]:
		var side := -1.0 if facing == "W" else 1.0
		draw_rect(Rect2(-8,-40,16,40),Color("333e50"))
		draw_rect(Rect2(-5,-36,10,34*(1.0-opening)),Color("a69d8d"))
		draw_rect(Rect2(side*8-1,-36,2,30),accent)
		return
	# Follow the curved wall's actual boundary, rather than drawing a straight
	# facade across the public walkway. Each bay is anchored to a solid cell.
	if facade_width>0:
		var rows: Array=preload("res://scripts/map_data.gd").AREAS.main.floor
		var origin:=Vector2i(floori(position.x/16.0),floori(position.y/16.0)-1)
		for dx in range(-int(facade_width/32),int(facade_width/32)+1):
			var xx:=origin.x+dx
			var best:=999
			for yy in range(maxi(1,origin.y-10),mini(rows.size()-1,origin.y+8)):
				if rows[yy][xx] in "#Wz" and rows[yy+1][xx] not in "#Wz~" and absi(yy-origin.y)<absi(best-origin.y):best=yy
			if best==999:continue
			var at:=Vector2(dx*16-8,(best-origin.y)*16)
			draw_texture_rect_region(panel,Rect2(at+Vector2(0,-30),Vector2(16,30)),Rect2(0,0,32,64))
			draw_rect(Rect2(at+Vector2(0,-34),Vector2(16,4)),Color("59667b"))
			draw_line(at+Vector2(0,-30),at+Vector2(16,-30),Color("dcc1a1"),1)
			if absi(dx)>1 and dx%2==0 and kind!="lift":
				draw_texture_rect_region(window,Rect2(at+Vector2(2,-25),Vector2(12,20)),Rect2(57,42,44,50))
	var half := 16.0 if kind in ["major","lift"] else 12.0
	draw_style_box(frame_style(),Rect2(-half-5,-42,half*2+10,44))
	draw_rect(Rect2(-half,-36,half*2,36),Color("263440"))
	# Shallow lit vestibule is visible through independently moving leaves.
	draw_rect(Rect2(-half+2,-32,half*2-4,30),Color("686b62"))
	draw_rect(Rect2(-half+2,-3,half*2-4,3),Color("d7ba8a"))
	var leaf := floorf(half*(1.0-opening))
	if leaf>0:
		draw_texture_rect_region(metal,Rect2(-half,-35,leaf,34),Rect2(0,0,leaf*2,64))
		draw_texture_rect_region(metal,Rect2(half-leaf,-35,leaf,34),Rect2(32,0,leaf*2,64))
		draw_rect(Rect2(-half+leaf-2,-24,1,12),accent)
		draw_rect(Rect2(half-leaf+1,-24,1,12),accent)
	draw_rect(Rect2(-half+1,-39,half*2-2,2),accent.lightened(0.08*sin(pulse*2)))
	draw_rect(Rect2(-half-2,1,half*2+4,3),Color("a29b8a"))
	icon(Vector2(0,-51),accent)
func frame_style() -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color=Color("c0ad99");s.border_color=Color("474958");s.set_border_width_all(2);s.set_corner_radius_all(4)
	return s
func icon(at: Vector2, color: Color) -> void:
	draw_rect(Rect2(at-Vector2(10,7),Vector2(20,14)),Color("394557"))
	if destination == "medbay":
		draw_rect(Rect2(at-Vector2(2,5),Vector2(4,10)),color);draw_rect(Rect2(at-Vector2(5,2),Vector2(10,4)),color)
	elif destination in ["mess","bar"]:
		draw_arc(at+Vector2(0,-1),6,0,PI,8,color,2);draw_line(at+Vector2(-6,-1),at+Vector2(6,-1),color,1)
		draw_line(at+Vector2(-2,-5),at+Vector2(-1,-3),color,1)
	elif kind=="lift":
		draw_polyline(PackedVector2Array([at+Vector2(-6,1),at+Vector2(-3,-3),at+Vector2(0,1)]),color,1)
		draw_polyline(PackedVector2Array([at+Vector2(1,-1),at+Vector2(4,3),at+Vector2(7,-1)]),color,1)
	elif destination=="fab":
		draw_arc(at,5,0,TAU,8,color,2);draw_line(at+Vector2(-7,0),at+Vector2(7,0),color,1)
	else:
		draw_rect(Rect2(at-Vector2(5,4),Vector2(10,8)),color,false,1);draw_line(at+Vector2(0,-4),at+Vector2(0,4),color,1)
