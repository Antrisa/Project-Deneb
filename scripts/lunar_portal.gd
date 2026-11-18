extends Node2D
# A reusable portal component: separate frame, sliding leaves, light and approach marker.
const NORTH_CANOPY = preload("res://art/lunar/portal_n_canopy.png")
const NORTH_LEAF = preload("res://art/lunar/portal_n_leaf.png")
const ACCESS_READY = preload("res://art/lunar/door_access_ready.png")
const ACCESS_LOCKED = preload("res://art/lunar/door_access_locked.png")

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
# Painted doors (Art Pack 5): a frame, and leaves that slide into the frame's jambs. Drawn at half size.
var art := {}
func _art(name: String) -> Texture2D:
	if not art.has(name):
		art[name] = load("res://art/lunar/%s.png" % name) if ResourceLoader.exists("res://art/lunar/%s.png" % name) else null
	return art[name]
# Opening of each painted frame, in the frame picture's own pixels: x from, x to, y from (to the bottom).
const APERTURE := {"door_s_frame": [26, 66, 40], "lift_frame": [34, 88, 36]}
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
		draw_texture_rect(NORTH_CANOPY, Rect2(-24, -45, 48, 48), false)
		var shown := roundf(17.0 * (1.0 - opening))
		if shown > 0.0:
			var source := Rect2(34.0 - shown * 2, 0, shown * 2, 32)
			draw_texture_rect_region(NORTH_LEAF, Rect2(-17, -21, shown, 16), source)
			draw_set_transform(Vector2.ZERO, 0.0, Vector2(-1, 1))
			draw_texture_rect_region(NORTH_LEAF, Rect2(-17, -21, shown, 16), source)
			draw_set_transform(Vector2.ZERO)
		draw_rect(Rect2(-7, -25, 14, 1), accent)
		draw_texture_rect(ACCESS_LOCKED if locked else ACCESS_READY, Rect2(-2, -30, 4, 2), false)
		return
	if facing in ["E","W"]:
		var side := -1.0 if facing == "W" else 1.0
		var jamb := _art("door_side_frame")
		var slide := _art("door_side_leaf")
		if jamb != null and slide != null:
			# The picture faces right (an east-facing door); mirrored for a west-facing one.
			draw_set_transform(Vector2.ZERO,0.0,Vector2(side,1.0))
			draw_texture_rect(jamb,Rect2(-8,-46,16,48),false)
			var h := 32.0*(1.0-opening)
			if h>0.5:
				draw_texture_rect_region(slide,Rect2(-4,-38,8,h),Rect2(0,0,16,h*2.0))
			draw_rect(Rect2(7,-36,1,30),accent)
			draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)
			return
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
	var frame_name := "lift_frame" if kind == "lift" else "door_s_frame"
	var frame := _art(frame_name)
	var leaf_art := _art("lift_leaf" if kind == "lift" else "door_s_leaf")
	if frame != null and leaf_art != null:
		_painted_door(frame,frame_name,leaf_art,accent)
		return
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
# A painted doorway: dark opening, two leaves sliding apart into the jambs, then the frame over them.
# The frame stands on the door tile's bottom edge, centred on it, at half size.
func _painted_door(frame: Texture2D,frame_name: String,leaf_art: Texture2D,accent: Color) -> void:
	var fw := frame.get_width()*0.5
	var fh := frame.get_height()*0.5
	var top_left := Vector2(-fw*0.5,2.0-fh)
	var ap: Array = APERTURE[frame_name]
	var ax0: float = top_left.x+ap[0]*0.5
	var ax1: float = top_left.x+ap[1]*0.5
	var ay0: float = top_left.y+ap[2]*0.5
	var ay1 := 2.0
	draw_rect(Rect2(ax0,ay0,ax1-ax0,ay1-ay0),Color("263440"))
	draw_rect(Rect2(ax0+1,ay1-3,ax1-ax0-2,2),Color("d7ba8a"))
	var half := (ax1-ax0)*0.5
	var shown := floorf(half*(1.0-opening))
	if shown>0.5:
		var src_w := shown*2.0*leaf_art.get_width()/(half*2.0)
		var src := Rect2(leaf_art.get_width()-src_w,0,src_w,leaf_art.get_height())
		draw_texture_rect_region(leaf_art,Rect2(ax0,ay0,shown,ay1-ay0),src)
		draw_set_transform(Vector2.ZERO,0.0,Vector2(-1,1))
		draw_texture_rect_region(leaf_art,Rect2(-ax1,ay0,shown,ay1-ay0),src)
		draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)
	draw_texture_rect(frame,Rect2(top_left,Vector2(fw,fh)),false)
	draw_rect(Rect2(ax0+2,ay0-3,ax1-ax0-4,1),accent.lightened(0.08*sin(pulse*2)))
	icon(Vector2(0,top_left.y-8),accent)
