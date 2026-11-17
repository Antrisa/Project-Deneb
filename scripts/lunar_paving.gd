extends RefCounted
# Native pixel paving, baked once. Visual borders never change collision or navigation.
const COLORS = [Color("718899"),Color("ded4bc"),Color("b8c3b5"),Color("c6a587"),Color("adb990"),Color("a8bfc0")]
static var painted: Image
static var stone: Image
static func texture_color(kind: int,x: int,y: int,base: Color,seed: int) -> Color:
	if painted==null:painted=load("res://art/lunar/paving_painted.png").get_image()
	var origins: Array[Vector2i]=[Vector2i(38,76),Vector2i(260,4),Vector2i(526,20),Vector2i(50,263),Vector2i(263,263),Vector2i(535,280)]
	var spans: Array[Vector2i]=[Vector2i(20,20),Vector2i(18,18),Vector2i(50,50),Vector2i(70,12),Vector2i(18,18),Vector2i(50,50)]
	var at: Vector2i=origins[kind]+Vector2i(posmod(x+seed*7,spans[kind].x),posmod(y+seed*3,spans[kind].y))
	var ink: Color=painted.get_pixelv(at)
	return base.lerp(ink,0.48)
static func noise_at(x: int,y: int) -> int:
	return absi((x*374761+y*668265) ^ (x*y*31))%101
static func swatch(kind: int,x: int,y: int,preview_variant: int=-1) -> Color:
	if kind==0:return hex_paver(x,y,preview_variant)
	if kind==4:return stone_paver(x,y,preview_variant)
	var width: int = [8,11,11,13,7,11][kind]
	var height: int = [7,6,8,4,7,8][kind]
	var row: int = floori(float(y)/height)
	var shifted: int = x+(width/2 if row%2 else 0)
	var col: int = floori(float(shifted)/width)
	var seed: int = noise_at(col,row)
	var variant: int=preview_variant if preview_variant>=0 else noise_at(col+37,row-19)%3
	var base: Color = COLORS[kind].lightened((seed%7)*0.009).darkened((seed%5)*0.008)
	if variant==1:base=base.lerp(Color("a9b7b4"),0.07)
	elif variant==2:base=base.lerp(Color("bda482"),0.07)
	base=texture_color(kind,x,y,base,seed)
	var xx: int = posmod(shifted,width)
	var yy: int = posmod(y,height)
	# Offset bond, a fine bevel and occasional inset stones replace the graph-paper grid.
	if xx==0 or yy==0:return base.darkened(0.24)
	if yy==1:return base.lightened(0.18)
	if xx==width-1 and seed%3==0:return base.darkened(0.04)
	# B: recessed inset edging with a restrained brass / ceramic detail.
	if variant==1:
		if (yy==2 or yy==height-2) and xx>2 and xx<width-2:return base.darkened(0.055)
		if xx==width-3 and yy==height-3:return base.lerp(Color("b9aa83"),0.4)
	# C: offset scuffs and a small bevel chip, never a damaged or impassable tile.
	if variant==2:
		if yy==2+seed%maxi(1,height-4) and xx>=3+seed%3 and xx<=6+seed%3:return base.darkened(0.085)
		if xx==1 and yy==height-2:return base.darkened(0.24)
	if kind==0 and seed%17==0:return base.lerp(Color("b7bda6"),0.22)
	if noise_at(x,y)>97:return base.lightened(0.035)
	return base
static func stone_paver(x: int,y: int,preview_variant: int=-1) -> Color:
	if stone==null:stone=load("res://art/lunar/garden_stone.png").get_image()
	var cx:=floori(float(x)/32.0);var cy:=floori(float(y)/32.0)
	var variant: int=preview_variant if preview_variant>=0 else noise_at(cx,cy)%3
	var color:=stone.get_pixel(posmod(x,stone.get_width()),posmod(y,stone.get_height()))
	if variant==1:color=color.lightened(0.025)
	elif variant==2:color=color.darkened(0.025)
	return color
static func hex_paver(x: int,y: int,preview_variant: int=-1) -> Color:
	# Flat-top axial hexes in shared world coordinates: no repeating square stamp.
	const R: float=6.0
	var q: float=(2.0/3.0*x)/R
	var r: float=(-x/3.0+sqrt(3.0)*y/3.0)/R
	var s: float=-q-r
	var iq:=roundi(q);var ir:=roundi(r);var iz:=roundi(s)
	var dq:=absf(iq-q);var dr:=absf(ir-r);var dz:=absf(iz-s)
	if dq>dr and dq>dz:iq=-ir-iz
	elif dr>dz:ir=-iq-iz
	var local:=Vector2(x-R*1.5*iq,y-R*sqrt(3.0)*(ir+iq*0.5))
	var edge: float=R*0.8660254-maxf(absf(local.y),absf(local.x)*0.8660254+absf(local.y)*0.5)
	var seed: int=noise_at(iq,ir)
	var variant: int=preview_variant if preview_variant>=0 else noise_at(iq+37,ir-19)%3
	var palette: Array[Color]=[Color("718899"),Color("7c92a2"),Color("667e90"),Color("8599a8"),Color("6f8397"),Color("788e9b")]
	var base: Color=palette[seed%palette.size()]
	base=texture_color(0,x,y,base,seed)
	if edge<0.65:return Color("364957")
	if edge<1.35:return base.lightened(0.23) if local.y<0 else base.darkened(0.18)
	# Occasional recessed service hexes, with a small brass or muted teal indicator.
	if variant==1:
		if edge>2.1 and edge<2.8:return base.darkened(0.13)
		if absf(local.x)<1.6 and local.y>3.0 and local.y<4.5:
			return Color("9aaea5") if seed%2 else Color("b9a475")
	# Sparse offset scuffs; most tiles remain quiet so characters read clearly.
	var mark_x: float=float(seed%7-3)
	var mark_y: float=float((seed/7)%7-3)
	if variant==2 and absf(local.x-mark_x)<2.0 and absf(local.y-mark_y)<0.55:return base.darkened(0.085)
	if noise_at(x,y)>98:return base.lightened(0.025)
	return base
static func weights(rows: Array,px: float,py: float) -> Vector3:
	var gx: float=px/16.0-0.5
	var gy: float=py/16.0-0.5
	var tx:=floori(gx);var ty:=floori(gy)
	var fx: float=smoothstep(0.0,1.0,gx-tx)
	var fy: float=smoothstep(0.0,1.0,gy-ty)
	var result:=Vector3.ZERO
	for dy in range(2):
		for dx in range(2):
			if ty+dy<0 or ty+dy>=rows.size() or tx+dx<0 or tx+dx>=rows[ty+dy].length():continue
			var c: String=rows[ty+dy][tx+dx]
			var w: float=(fx if dx else 1-fx)*(fy if dy else 1-fy)
			if c=="p":result.x+=w
			elif c=="h":result.y+=w
			elif c=="u":result.z+=w
	return result
static func sample(rows: Array,x: int,y: int,ch: String) -> Color:
	var delta:=Vector2(x+1-1848,y+1-1528)
	var radius: float=delta.length()
	var spoke: float=minf(minf(absf(delta.x),absf(delta.y)),minf(absf(delta.x-delta.y),absf(delta.x+delta.y))*0.70710678)
	var route: float=minf(spoke,absf(radius-152)+20) if radius<480 else spoke
	var kind:=2 if ch=="a" or radius>490 else 0
	var w:=weights(rows,x+1,y+1)
	# Social floors follow their furnished court footprints rather than floating ovals.
	var point:=Vector2(x+1,y+1)/16.0
	w.y=1.0 if Geometry2D.is_point_in_polygon(point,PackedVector2Array([Vector2(99,72),Vector2(101,70),Vector2(110,70),Vector2(110,81),Vector2(108,83),Vector2(105,80),Vector2(99,74)])) else 0.0
	if point.x>115 and point.y>100:
		w.z=1.0 if Geometry2D.is_point_in_polygon(point,PackedVector2Array([Vector2(118,112),Vector2(120,110),Vector2(125,110),Vector2(130,115),Vector2(130,119),Vector2(120,119),Vector2(118,117)])) else 0.0
	var pocket: float=maxf(w.x,maxf(w.y,w.z))
	if pocket>0.5:kind=3 if w.x==pocket else 4 if w.y==pocket else 5
	# Continuous eight-spoke layout and a round fountain circuit, clipped to walkable ground.
	var on_route: bool=radius<174 or (route<40 and (radius<480 or ch in [".","a"]))
	if on_route:kind=1
	var color:=swatch(kind,x,y)
	if on_route and route>36 and radius>=170:
		color=Color("a99579") if route>38 else Color("f1dfbc")
	# A softly rounded border on garden / recreation / patio blends. Paths cut clear openings.
	if w.x>0.39 and w.x<0.61 and route>44:
		color=Color("928d7a") if pocket<0.49 else Color("e6d6b6")
	# Brass direction studs are spaced far apart; no repeated stripes across the route.
	if on_route and route<3 and int(radius)%96<4 and radius>175:
		color=Color("c7ad70")
	return color
static func bake(rows: Array) -> Image:
	var img:=Image.create(rows[0].length()*16,rows.size()*16,false,Image.FORMAT_RGBA8)
	img.fill(Color.TRANSPARENT)
	for ty in rows.size():
		for tx in rows[ty].length():
			var ch: String=rows[ty][tx]
			if ch in "#Wz~":continue
			for yy in range(16):
				for xx in range(16):img.set_pixel(tx*16+xx,ty*16+yy,sample(rows,tx*16+xx,ty*16+yy,ch))
	return img
