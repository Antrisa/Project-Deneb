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
var n_height := 48.0       # north-facing doors: the wall's height on screen, from its top edge to the foot of its face
var pulse := 0.0
var window: Texture2D = preload("res://art/lunar/home.png")
var panel: Texture2D = preload("res://art/lunar/material_2.png")
var metal: Texture2D = preload("res://art/lunar/material_6.png")
# Painted doors: a frame, and leaves that slide into the frame's jambs. Drawn at 2/3 size (24 pixels a tile).
var art := {}
func _art(art_name: String) -> Texture2D:
	if not art.has(art_name):
		art[art_name] = load("res://art/lunar/%s.png" % art_name) if ResourceLoader.exists("res://art/lunar/%s.png" % art_name) else null
	return art[art_name]
# Opening of each painted frame, in the frame picture's own pixels: x from, x to, y from (to the bottom).
# Redrawn 22 Nov at 24 pixels a tile like the rest of the art, so frames are drawn at 2/3 size (ART_K).
# Each frame fills its wall exactly (Zachary, 22 Nov: "flush with walls and ceilings"): south-facing frames cover
# the wall face from its foot (the top of the door tile) up to its lip, side doors the gap in the wall's top.
const APERTURE := {"door_s_frame": [13, 41, 18], "lift_frame": [18, 54, 16]}
const ART_K := 2.0 / 3.0
func setup(e: Array, facade: Array = []) -> void:
	position = Vector2(float(e[1])*16+8,float(e[2])*16+16)
	facing = e[6]; title = e[7];destination = e[3];locked = e[8]
	if facing == "N":
		# Count the wall rows below the door tile: the frame covers the wall from its top to the foot of its face.
		var rows: Array = preload("res://scripts/map_data.gd").AREAS[e[0]].floor
		var x := int(e[1]); var y := int(e[2]) + 1; var below := 0
		while y < rows.size() and String(rows[y][x]) in "#WzZwMN78":
			below += 1; y += 1
		# A thin wall shows its face below its top; a thick block (the promenade's buildings) has no face near the
		# door, so the frame is the usual two tiles plus the door tile there.
		n_height = 32.0 + 16.0 * below if below <= 2 else 48.0
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
		# Seen from above as you walk down through it (Zachary, 22 Nov): the posts' tops and the passage floor
		# between them, covering the wall from its top edge to the foot of its face; the door is a slab across the
		# passage whose two halves slide into the posts. The picture is three 24-pixel bands: top, a plain middle
		# stretched to the wall's thickness, bottom.
		var top := -32.0
		var H := n_height
		draw_texture_rect_region(NORTH_CANOPY, Rect2(-24, top, 48, 16), Rect2(0, 0, 72, 24))
		draw_texture_rect_region(NORTH_CANOPY, Rect2(-24, top + 16, 48, H - 32), Rect2(0, 24, 72, 24))
		draw_texture_rect_region(NORTH_CANOPY, Rect2(-24, top + H - 16, 48, 16), Rect2(0, 48, 72, 24))
		var shown := roundf(16.0 * (1.0 - opening))
		var sy := top + 10.0
		if shown > 0.0:
			var lk: float = NORTH_LEAF.get_width() / 16.0
			var source := Rect2(NORTH_LEAF.get_width() - shown * lk, 0, shown * lk, NORTH_LEAF.get_height())
			draw_rect(Rect2(-16, sy + 8, shown, 2), Color(0, 0, 0, 0.25))      # the slab's shadow on the floor
			draw_rect(Rect2(16 - shown, sy + 8, shown, 2), Color(0, 0, 0, 0.25))
			draw_texture_rect_region(NORTH_LEAF, Rect2(-16, sy, shown, 8), source)
			draw_set_transform(Vector2.ZERO, 0.0, Vector2(-1, 1))
			draw_texture_rect_region(NORTH_LEAF, Rect2(-16, sy, shown, 8), source)
			draw_set_transform(Vector2.ZERO)
		draw_rect(Rect2(-10, top + H - 8, 20, 1), accent)
		draw_texture_rect(ACCESS_LOCKED if locked else ACCESS_READY, Rect2(-22, top + 2, 4, 2), false)
		return
	if facing in ["E","W"]:
		var side := -1.0 if facing == "W" else 1.0
		var jamb := _art("door_side_frame")
		var slide := _art("door_side_leaf")
		if jamb != null and slide != null:
			# The picture faces right (an east-facing door); mirrored for a west-facing one.
			draw_set_transform(Vector2.ZERO,0.0,Vector2(side,1.0))
			# Fills the gap in the wall's top: the tile above the door tile and the door tile's own top half.
			var h := 26.0*(1.0-opening)
			if h>0.5:
				draw_texture_rect_region(slide,Rect2(-6,-29,12,h),Rect2(0,0,slide.get_width(),h*slide.get_height()/26.0))
			draw_texture_rect(jamb,Rect2(-8,-32,16,32),false)
			draw_rect(Rect2(5,-28,1,24),accent)
			draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)
			return
		draw_rect(Rect2(-8,-40,16,40),Color("333e50"))
		draw_rect(Rect2(-5,-36,10,34*(1.0-opening)),Color("a69d8d"))
		draw_rect(Rect2(side*8-1,-36,2,30),accent)
		return
	# (The old painted facade strips that ran along the shop's wall here are gone: the baked walls are the facade.)
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
	var fw := frame.get_width()*ART_K
	var fh := frame.get_height()*ART_K
	var top_left := Vector2(-fw*0.5,-16.0-fh)      # bottom on the wall face's foot, top at its lip
	var ap: Array = APERTURE[frame_name]
	var ax0: float = top_left.x+ap[0]*ART_K
	var ax1: float = top_left.x+ap[1]*ART_K
	var ay0: float = top_left.y+ap[2]*ART_K
	var ay1 := -16.0
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
	draw_rect(Rect2(ax0+2,ay0-1,ax1-ax0-4,1),accent.lightened(0.08*sin(pulse*2)))
	if kind != "lift":
		small_icon(Vector2(0,top_left.y+6),accent)      # on the sign panel in the header, not on the roof above
# The shop's sign, small enough for the panel in the door frame's header (16 x 8).
func small_icon(at: Vector2, color: Color) -> void:
	if destination == "medbay":
		draw_rect(Rect2(at-Vector2(1,3),Vector2(2,6)),color);draw_rect(Rect2(at-Vector2(3,1),Vector2(6,2)),color)
	elif destination in ["mess","bar"]:
		draw_arc(at+Vector2(0,-1),3.5,0,PI,8,color,1);draw_line(at+Vector2(-4,-1),at+Vector2(4,-1),color,1)
	elif destination=="fab":
		draw_arc(at,2.5,0,TAU,8,color,1);draw_line(at+Vector2(-5,0),at+Vector2(5,0),color,1)
	else:
		draw_rect(Rect2(at-Vector2(3,2),Vector2(6,4)),color,false,1);draw_line(at+Vector2(0,-2),at+Vector2(0,2),color,1)
