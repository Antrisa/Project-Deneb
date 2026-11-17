extends RefCounted
# Separate tiled floor, structure, wall faces, shadows. All units are world pixels.
var floor_art: Texture2D
var materials: Array[Texture2D] = []
func _init() -> void:
	for i in range(8): materials.append(load("res://art/lunar/material_%d.png" % i))
func paint(n: Node2D, data: Dictionary) -> void:
	var rows: Array = data.floor
	if floor_art == null: floor_art = ImageTexture.create_from_image(bake_floor(rows))
	n.draw_texture_rect(floor_art,Rect2(0,0,rows[0].length()*16,rows.size()*16),false)
	preload("res://scripts/lunar_curbs.gd").paint(n)
	var portals_above := {}
	for e in preload("res://scripts/map_data.gd").ENTRANCES:
		if e[0] == "main" and e[6] == "S":
			for dx in [-1,0,1]: portals_above[Vector2i(e[1]+dx,e[2]-1)] = true
	for y in rows.size():
		for x in rows[y].length():
			var ch: String = rows[y][x]
			if ch == "~":
				if Vector2(x-115,y-95).length() < 68:
					tile(n,3,x,y)
				continue
			if ch not in "#Wz":
				continue
			var material := 0
			if ch == "a": material = 4
			elif ch == "p": material = 5
			elif ch in "#Wz": material = 1
			roof_tile(n,rows,x,y,0)
	# Wall bodies meet the same structural footprint, then their raised roof lip.
	for y in rows.size():
		for x in rows[y].length():
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
			if x>0 and rows[y][x-1] not in "#Wz~":
				n.draw_rect(Rect2(x*16,y*16-16,2,32),Color("394756"))
			if x+1<rows[y].length() and rows[y][x+1] not in "#Wz~":
				n.draw_rect(Rect2(x*16+14,y*16-16,2,32),Color("7c828a"))
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
	var tint: Color=[Color("ffffff"),Color("e1e8f0"),Color("cdd9e5")][hash_cell(x,y)%3]
	n.draw_polygon(points,PackedColorArray([tint]),uv,materials[1])
