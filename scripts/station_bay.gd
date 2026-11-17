extends Node2D
# Tile-sized, layered cutaway architecture; no stretched facade textures.
var kind := ""
var w := 176.0
var h := 96.0
var phase := 0.0
var tick := 0.0
var lamp := Color("75d9d2")
var door_x := 80.0
var open_market := false
func setup(data: Array) -> void:
	kind = str(data[0])
	w = float(data[3]) * 16.0
	h = float(data[4]) * 16.0
	position = Vector2(float(data[1])*16.0,(float(data[2])+float(data[4]))*16.0)
	open_market = kind in ["bram","weaver","furn","fab"]
	door_x = 32.0 if open_market else w/2.0-8.0
	if kind in ["bar","armoury"]: door_x -= 16.0
	if kind == "medbay": lamp = Color("8ed9b4")
	if kind == "weaver": lamp = Color("c4a1e4")
	if kind in ["mess","bar","common"]: lamp = Color("f0bf74")
	phase = float(kind.hash()%100)*0.1
func _process(delta: float) -> void:
	if not visible: return
	tick += delta
	if tick > 0.12:
		phase += tick
		tick = 0.0
		queue_redraw()
func box(x: float,y: float,a: float,b: float,c: String) -> void:
	draw_rect(Rect2(x,y,a,b),Color(c))
func _draw() -> void:
	# Cutaway: a deep service deck, thick shared bulkhead and a recessed room.
	box(0,-h,w,h,"26333f")
	box(4,-h+4,w-8,32,"52646f")
	for x in range(8,int(w)-8,16):
		box(x,-h+5,14,26,"617581")
		box(x,-h+5,14,1,"87949b")
	# Horizontal utility pipes run through the bay into adjoining station walls.
	box(0,-h+15,w,5,"263b46")
	box(0,-h+15,w,1,"afbab8")
	for x in [12.0,w-28.0]:
		box(x,-h+8,17,17,"26343f")
		for j in range(4):box(x+2,-h+10+j*3,13,1,"87959b")
		# Slow fan in its own housing.
		var center := Vector2(x+8,-h+16)
		var spin := Vector2(cos(phase),sin(phase))*5.0
		draw_line(center-spin,center+spin,Color("a9b5b7"),1)
	# Recessed interior floor, back wall and side-wall thickness.
	box(7,-h+38,w-14,h-43,"151f2c")
	box(10,-h+39,w-20,12,"6b7679")
	box(10,-h+51,w-20,h-56,"444c50")
	for y in range(int(-h+53),-5,8):box(10,y,w-20,1,"586064")
	box(0,-h+35,7,h-35,"a4acaa")
	box(w-7,-h+35,7,h-35,"747f83")
	box(7,-h+35,3,h-35,"394851")
	box(w-10,-h+35,3,h-35,"263640")
	# Furniture is built independently inside each bay.
	if open_market:
		for x in range(67,int(w)-14,22):
			box(x,-42,19,26,"283740")
			for row in range(3):
				box(x+1,-40+row*7,17,2,"a1a59b")
				for col in range(3):
					draw_rect(Rect2(x+2+col*5,-44+row*7,3,4), lamp.darkened(float(col)*0.12))
		box(62,-17,w-77,12,"687e82")
		box(60,-19,w-73,4,"b5b8a8")
		box(64,-5,w-81,3,"172732")
	else:
		for x in [15.0,w-47.0]:
			box(x,-39,30,20,"223743")
			box(x+2,-37,26,12,"437783")
			if kind in ["library","common","mess","bar"]:
				box(x+2,-25,26,6,"ac8663")
				box(x+4,-30,9,5,"cfaa75")
				box(x+17,-30,9,5,"769a94")
			else:
				box(x+3,-35,24,1,"73c2bd")
				box(x+3,-32,11,1,"73c2bd")
	# Narrow standard door, independent of total bay width, matches warp tiles.
	box(door_x-3,-40,22,40,"162b36")
	box(door_x,-36,16,34,"347079")
	box(door_x+1,-35,6,31,"4b9094")
	box(door_x+9,-35,6,31,"40848b")
	box(door_x+7,-36,2,35,"182e3c")
	box(door_x+5,-18,1,5,"b6e7d5")
	box(door_x+10,-18,1,5,"b6e7d5")
	box(door_x-3,-2,22,2,"99a8a4")
	# Header and screen are separate animated components.
	box(4,-h+32,w-8,6,"bdbea8")
	box(door_x-5,-45,26,4,"20383f")
	draw_rect(Rect2(door_x-3,-44,22,2),lamp*(0.86+0.08*sin(phase)))
	box(w-21,-18,8,12,"172a36")
	draw_rect(Rect2(w-20,-16,6,7),lamp.darkened(0.45))
	box(w-20,-15+int(phase*2.0)%5,5,1,"bde5d2")
	for x in [5.0,w-7.0]:
		draw_rect(Rect2(x,-29,2,8),Color("e8bc7d")*(0.92+0.04*sin(phase)))
