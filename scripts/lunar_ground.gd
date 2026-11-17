extends RefCounted
# Separate tiled floor, structure, wall faces, shadows. All units are world pixels.
var floor_art: Texture2D
var materials: Array[Texture2D] = []
func _init() -> void:
	for i in range(8): materials.append(load("res://art/lunar/material_%d.png" % i))
var portals_above := {}
var lights: Array = []
# The floor picture is baked ahead of time by tools/bake_floor.py (run by tools/build.py). Working it out
# here, pixel by pixel, took a very long time, so that is only a fallback for when the picture is missing.
func prepare(rows: Array) -> void:
	if floor_art != null: return
	if ResourceLoader.exists("res://art/lunar/floor_main.png"):
		floor_art = load("res://art/lunar/floor_main.png")
	else:
		push_warning("art/lunar/floor_main.png is missing: baking the promenade floor now (slow). Run tools/build.py.")
		floor_art = ImageTexture.create_from_image(bake_floor(rows))
	for e in preload("res://scripts/map_data.gd").ENTRANCES:
		if e[0] == "main" and e[6] == "S":
			for dx in [-1,0,1]: portals_above[Vector2i(e[1]+dx,e[2]-1)] = true
	lights = preload("res://scripts/map_data.gd").ROOF_LIGHTS
# Whole level in one go (kept for tools that want it). The game draws it in chunks with paint_region,
# so Godot only draws the part on screen.
func paint(n: Node2D, data: Dictionary) -> void:
	var rows: Array = data.floor
	paint_region(n,rows,Rect2i(0,0,rows[0].length(),rows.size()))
# Moon surface round the station: a ring round the main circle and round the four corner pods.
func moon_at(x: int,y: int) -> bool:
	if Vector2(x-115,y-95).length() < 68: return true
	for sx in [-1,1]:
		for sy in [-1,1]:
			if Vector2(x-115-sx*39.6,y-95-sy*39.6).length() < 25.0: return true
	return false
func paint_region(n: Node2D, rows: Array, r: Rect2i) -> void:
	prepare(rows)
	var x1: int = mini(r.end.x,rows[0].length())
	var y1: int = mini(r.end.y,rows.size())
	var area_px := Rect2(Vector2(r.position*16),Vector2((Vector2i(x1,y1)-r.position)*16))
	n.draw_texture_rect_region(floor_art,area_px,area_px)
	for y in range(r.position.y,y1):
		for x in range(r.position.x,x1):
			var ch: String = rows[y][x]
			if ch == "~":
				if moon_at(x,y):
					tile(n,3,x,y)
				continue
			if ch not in "#Wz":
				continue
			roof_tile(n,rows,x,y,0)
	# Wall bodies meet the same structural footprint, then their raised roof lip.
	for y in range(r.position.y,y1):
		for x in range(r.position.x,x1):
			if rows[y][x] not in "#Wz": continue
			var bottom: bool = y+1<rows.size() and rows[y+1][x] not in "#Wz~"
			if bottom and not portals_above.has(Vector2i(x,y)):
				n.draw_rect(Rect2(x*16,y*16+16,16,4),Color(0.1,0.12,0.18,0.22))
				n.draw_texture_rect_region(materials[2],Rect2(x*16,y*16-16,16,32),Rect2((x%2)*32,0,32,64),wall_tint(x,y))
				wall_detail(n,x,y)
			else:
				roof_tile(n,rows,x,y,-16)
			if not bottom and y>0 and rows[y-1][x] in "#Wz":
				roof_detail(n,x,y)
				# A seam where one roof plate meets the next, so the roof reads as separate buildings.
				if x+1<rows[y].length() and rows[y][x+1] in "#Wz" and roof_zone(x+1,y)!=roof_zone(x,y):
					n.draw_rect(Rect2(x*16+15,y*16-16,1,16),Color("36434f"))
					n.draw_rect(Rect2(x*16+16,y*16-16,1,16),Color("a9b6c2"))
				if y+1<rows.size() and rows[y+1][x] in "#Wz" and roof_zone(x,y+1)!=roof_zone(x,y):
					n.draw_rect(Rect2(x*16,y*16-1,16,1),Color("36434f"))
					n.draw_rect(Rect2(x*16,y*16,16,1),Color("a9b6c2"))
			if x>0 and rows[y][x-1] not in "#Wz~":
				n.draw_rect(Rect2(x*16,y*16-16,2,32),Color("394756"))
			if x+1<rows[y].length() and rows[y][x+1] not in "#Wz~":
				n.draw_rect(Rect2(x*16+14,y*16-16,2,32),Color("7c828a"))
	for l in lights:
		if r.has_point(Vector2i(int(l[0]),int(l[1]))):
			skylight(n,int(l[0]),int(l[1]))
# The roofs are split into plates: eight over the shop band (one between each pair of spokes) and sixteen
# round the outer shell. Each plate has its own tone.
func roof_zone(x: int,y: int) -> int:
	var d:=Vector2(x+0.5-115.5,y+0.5-95.5)
	# Each corner pod is one plate of its own.
	for sx in [-1,1]:
		for sy in [-1,1]:
			if Vector2(x-115-sx*39.6,y-95-sy*39.6).length() <= 14.0: return 24
	var a: float=fposmod(rad_to_deg(d.angle()),360.0)
	if d.length()<45.0:
		return int(a/45.0)%8
	return 8+int(fposmod(a+11.25,360.0)/22.5)%16
# A two-by-two skylight set into the roof (x,y is its top-left roof tile).
func skylight(n: Node2D,x: int,y: int) -> void:
	var r:=Rect2(x*16+2,y*16-16+2,28,28)
	n.draw_rect(r.grow(1),Color("2f3b4a"))
	n.draw_rect(r,Color("86bfc4"))
	n.draw_rect(Rect2(r.position,Vector2(28,8)),Color("a9d8d6"))
	n.draw_rect(Rect2(r.position+Vector2(4,18),Vector2(20,6)),Color("e9c98a"))
	n.draw_rect(Rect2(r.position+Vector2(13,0),Vector2(2,28)),Color("4a596b"))
	n.draw_rect(Rect2(r.position+Vector2(0,13),Vector2(28,2)),Color("4a596b"))
	n.draw_rect(r,Color("5b6b7e"),false,1.0)
func tile(n: Node2D, material: int,x: int,y: int) -> void:
	n.draw_texture_rect_region(materials[material],Rect2(x*16,y*16,16,16),Rect2((x%4)*16,(y%4)*16,16,16))

func bake_floor(rows: Array) -> Image:
	return preload("res://scripts/lunar_paving.gd").bake(rows)

func hash_cell(x: int,y: int) -> int:
	return absi(x*73856093 ^ y*19349663)
func wall_tint(x: int,y: int) -> Color:
	return [Color("ffffff"),Color("e1e7ec"),Color("ede2d5")][hash_cell(x/3,y)%3]
func wall_detail(n: Node2D,x: int,y: int) -> void:
	var at:=Vector2(x*16,y*16)
	var v:=hash_cell(x,y)%7
	if v==1:
		n.draw_style_box(panel_style(Color("4d5b6b")),Rect2(at+Vector2(3,-7),Vector2(10,8)))
		for k in range(3):n.draw_line(at+Vector2(5,-5+k*2),at+Vector2(11,-5+k*2),Color("8c999e"),1)
	elif v==3:
		n.draw_rect(Rect2(at+Vector2(4,-9),Vector2(8,12)),Color("717e8b"),false,1)
		n.draw_line(at+Vector2(6,0),at+Vector2(9,0),Color("d2bf9b"),1)
	elif v==5:
		n.draw_rect(Rect2(at+Vector2(5,-6),Vector2(6,3)),Color("354657"))
		n.draw_line(at+Vector2(6,-5),at+Vector2(9,-5),Color("7ac0bd"),1)
func panel_style(c: Color) -> StyleBoxFlat:
	var s:=StyleBoxFlat.new();s.bg_color=c;s.border_color=Color("394653")
	s.set_border_width_all(1);s.set_corner_radius_all(2);return s
func roof_detail(n: Node2D,x: int,y: int) -> void:
	var at:=Vector2(x*16,y*16-16)
	var v:=hash_cell(x,y)%19
	if v==2:
		n.draw_style_box(panel_style(Color("526477")),Rect2(at+Vector2(3,3),Vector2(10,9)))
		for k in range(3):n.draw_line(at+Vector2(5,5+k*2),at+Vector2(11,5+k*2),Color("8b9ba6"),1)
	elif v==7:
		n.draw_style_box(panel_style(Color("607184")),Rect2(at+Vector2(2,2),Vector2(12,12)))
		n.draw_line(at+Vector2(4,4),at+Vector2(12,4),Color("91a0ad"),1)
		n.draw_line(at+Vector2(9,11),at+Vector2(11,11),Color("c9b992"),1)
	elif v==12:
		n.draw_line(at+Vector2(3,4),at+Vector2(3,12),Color("8296a2"),1)
		n.draw_line(at+Vector2(4,12),at+Vector2(11,12),Color("394c61"),1)
func roof_tile(n: Node2D,rows: Array,x: int,y: int,lift: int) -> void:
	# Round convex exterior corners inside the collision footprint, never into a path.
	var open_l: bool=x>0 and rows[y][x-1] not in "#Wz"
	var open_r: bool=x+1<rows[y].length() and rows[y][x+1] not in "#Wz"
	var open_u: bool=y>0 and rows[y-1][x] not in "#Wz"
	var open_d: bool=y+1<rows.size() and rows[y+1][x] not in "#Wz"
	var rounded: Array[bool]=[open_l and open_u,open_r and open_u,open_r and open_d,open_l and open_d]
	var tint: Color=[Color("ffffff"),Color("dbe4ee"),Color("f0e9df"),Color("c6d3e2")][roof_zone(x,y)%4]
	if not (rounded[0] or rounded[1] or rounded[2] or rounded[3]):
		# Most roof tiles: one plain textured square, which Godot draws far faster than a polygon.
		n.draw_texture_rect_region(materials[1],Rect2(x*16,y*16+lift,16,16),Rect2((x%4)*16,(y%4)*16,16,16),tint)
		return
	var centers: Array[Vector2]=[Vector2(5,5),Vector2(11,5),Vector2(11,11),Vector2(5,11)]
	var corners: Array[Vector2]=[Vector2(0,0),Vector2(16,0),Vector2(16,16),Vector2(0,16)]
	var points:=PackedVector2Array();var uv:=PackedVector2Array()
	for i in range(4):
		if rounded[i]:
			for j in range(5):points.append(centers[i]+Vector2.from_angle(PI+i*PI/2+j*PI/8)*5)
		else:points.append(corners[i])
	for i in points.size():
		uv.append((points[i]+Vector2((x%4)*16,(y%4)*16))/64.0)
		points[i]+=Vector2(x*16,y*16+lift)
	n.draw_polygon(points,PackedColorArray([tint]),uv,materials[1])
