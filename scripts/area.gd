extends Node2D
# Draws one area of the station (a level, the mine, the outer walkways).
# The data comes from scripts/map_data.gd.

const TILE := 16
const MapData = preload("res://scripts/map_data.gd")

var data: Dictionary
var tiles_tex: Texture2D
var overhead := false      # true for the layer drawn in front of characters (tops of tall objects)


func setup(area_data: Dictionary, tex: Texture2D, is_overhead: bool = false) -> void:
	data = area_data
	tiles_tex = tex
	overhead = is_overhead


func _draw() -> void:
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
					var pick: int = absi((x * 73856093) ^ (y * 19349663)) % (n * 3)
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
			if MapData.TILE_OBJ.has(och):
				_tile(int(MapData.TILE_OBJ[och]), x, y)
	# Painted outlines on the floor (loading pad, landing pad). Values are in tiles.
	var outlines: Array = data["outlines"]   # (base layer only)
	for o in outlines:
		var r: Rect2 = Rect2(int(o[0]) * TILE, int(o[1]) * TILE, int(o[2]) * TILE, int(o[3]) * TILE)
		draw_rect(r.grow(-1.0), Color("e6be3c"), false, 1.0)


# tiles.png columns are 16 wide and 32 tall: the tile is the lower half, the top of a tall object the upper half.
func _tile(index: int, x: int, y: int) -> void:
	draw_texture_rect_region(tiles_tex, Rect2(x * TILE, y * TILE, TILE, TILE), Rect2(index * TILE, TILE, TILE, TILE))


func _top(index: int, x: int, y: int) -> void:
	draw_texture_rect_region(tiles_tex, Rect2(x * TILE, y * TILE, TILE, TILE), Rect2(index * TILE, 0, TILE, TILE))
