extends Node2D
# Draws one area of the station (a level, the mine, the outer walkways).
# The data comes from scripts/map_data.gd.

const TILE := 16
const MapData = preload("res://scripts/map_data.gd")

var data: Dictionary
var tiles_tex: Texture2D
var overhead := false      # true for the layer drawn in front of characters (tops of tall objects)
var hidden_objects := {}
var lunar = preload("res://scripts/lunar_ground.gd").new()
var cell := 16             # size of one tile in tiles.png (16, or 32 for double-detail art)


func setup(area_data: Dictionary, tex: Texture2D, is_overhead: bool = false) -> void:
	data = area_data
	lunar.key = MapData.LUNAR_AREAS.get(data["title"], "main")
	if data["title"] == "Community Concourse":
		for tile in MapData.CONCOURSE_HIDDEN:
			hidden_objects[Vector2i(int(tile[0]), int(tile[1]))] = true
	tiles_tex = tex
	overhead = is_overhead
	cell = tex.get_width() / int(MapData.TILE_COLUMNS)
	if MapData.LUNAR_AREAS.has(data["title"]) and not overhead:
		_make_chunks()


# Levels in the promenade style are far bigger than the screen. Drawn as one item, Godot had to handle every tile of it
# every frame. Split into chunks 16 tiles square, it only draws the few chunks on screen.
const CHUNK := 16
func _make_chunks() -> void:
	var rows: Array = data["floor"]
	for cy in range(0, rows.size(), CHUNK):
		for cx in range(0, rows[0].length(), CHUNK):
			var chunk := Node2D.new()
			chunk.draw.connect(_draw_chunk.bind(chunk, Rect2i(cx, cy, CHUNK, CHUNK)))
			add_child(chunk)


func _draw_chunk(chunk: Node2D, r: Rect2i) -> void:
	lunar.paint_region(chunk, data["floor"], r)
	var obj_rows: Array = data["obj"]
	for y in range(r.position.y, mini(r.end.y, obj_rows.size())):
		var orow: String = obj_rows[y]
		for x in range(r.position.x, mini(r.end.x, orow.length())):
			var ch: String = orow[x]
			if ch != "x" and MapData.TILE_OBJ.has(ch):
				chunk.draw_texture_rect_region(tiles_tex, Rect2(x * TILE, y * TILE, TILE, TILE), Rect2(int(MapData.TILE_OBJ[ch]) * cell, cell, cell, cell))


func _draw() -> void:
	if MapData.LUNAR_AREAS.has(data["title"]):
		if not overhead:
			pass                 # drawn by the chunks (see _make_chunks)
		else:
			# Tops of the tall store-front objects (sign boards, racks, shelves), drawn in front of characters.
			for y in range(1, data.obj.size()):
				for x in data.obj[y].length():
					var top_ch: String = data.obj[y][x]
					if top_ch != "x" and MapData.TALL.contains(top_ch) and MapData.TILE_OBJ.has(top_ch):
						_top(int(MapData.TILE_OBJ[top_ch]), x, y - 1)
		return
	var floor_rows: Array = data["floor"]
	var obj_rows: Array = data["obj"]
	if overhead:
		# Tops of tall objects go over the tile above them, so you can walk behind.
		for y in range(1, floor_rows.size()):
			var frow_top: String = floor_rows[y]
			var orow_top: String = obj_rows[y]
			for x in frow_top.length():
				var fch_top: String = frow_top[x]
				if MapData.TALL.contains(fch_top) and MapData.TILE_FLOOR.has(fch_top):
					_top(int(MapData.TILE_FLOOR[fch_top]), x, y - 1)
				var och_top: String = orow_top[x]
				if MapData.TALL.contains(och_top) and MapData.TILE_OBJ.has(och_top):
					_top(int(MapData.TILE_OBJ[och_top]), x, y - 1)
		return
	for y in floor_rows.size():
		var frow: String = floor_rows[y]
		var orow: String = obj_rows[y]
		for x in frow.length():
			var fch: String = frow[x]
			if MapData.TILE_FLOOR.has(fch):
				# Floors have variations. The first is the common one; the others turn up now and then.
				var index: int = MapData.TILE_FLOOR[fch]
				var n: int = MapData.TILE_VARIANTS.get(fch, 1)
				if n > 1:
					var pick: int = absi((x * 73856093) ^ (y * 19349663)) % (n * 6)
					if pick < n:
						index += pick
				_tile(index, x, y)
			# Soft shadow on the floor just below a wall's front face.
			if y > 0 and not MapData.SOLID_FLOOR.contains(fch):
				var above: String = floor_rows[y - 1]
				var ach: String = above[x]
				if MapData.WALL_FACES.contains(ach):
					draw_rect(Rect2(x * TILE, y * TILE, TILE, 4), Color(0, 0, 0, 0.18))
			var och: String = orow[x]
			if MapData.TILE_OBJ.has(och) and not hidden_objects.has(Vector2i(x, y)):
				_tile(int(MapData.TILE_OBJ[och]), x, y)
	# Painted outlines on the floor (loading pad, landing pad). Values are in tiles.
	var outlines: Array = data["outlines"]   # (base layer only)
	for o in outlines:
		var r: Rect2 = Rect2(int(o[0]) * TILE, int(o[1]) * TILE, int(o[2]) * TILE, int(o[3]) * TILE)
		draw_rect(r.grow(-1.0), Color("e6be3c"), false, 1.0)


# Each column of tiles.png is one cell wide and two cells tall: the tile is the lower half,
# the top of a tall object the upper half. Whatever size the art is, a tile is drawn 16x16 in the world.
func _tile(index: int, x: int, y: int) -> void:
	draw_texture_rect_region(tiles_tex, Rect2(x * TILE, y * TILE, TILE, TILE), Rect2(index * cell, cell, cell, cell))


func _top(index: int, x: int, y: int) -> void:
	draw_texture_rect_region(tiles_tex, Rect2(x * TILE, y * TILE, TILE, TILE), Rect2(index * cell, 0, cell, cell))
