extends Node2D
## The Agri dome's ground: your field (farmed a tile at a time), the herb patches, and the animated ponds and
## spring. Drawn below the planters, the player and other props.
##
## The field (21 Nov). One tile is one character wide, as in Stardew. Each dug tile is drawn on its own:
##  - with the farm art, when it exists (see the farm art instructions, docs/FARM_ART.md):
##      art/farm/field.png       untilled field dirt, 3 variants of 24 x 24 side by side
##      art/farm/tilled.png      16 dug tiles, 24 x 24, in a 4 x 4 grid. Tile i joins its dug neighbours:
##                               i = 1 (north dug) + 2 (east) + 4 (south) + 8 (west); tile i is at column i % 4, row i / 4
##      art/farm/tilled_wet.png  the same 16, watered
##      art/farm/crops/<crop>.png  one 24 x 48 picture per growth stage, side by side, the last one ripe
##      art/farm/field_border.png  a grass edge drawn over the field's own edge tiles, in the same 16-tile layout
##                               as tilled.png, numbered by which neighbours are inside the field (21 Nov)
##  - until then, cut from the old 48-pixel soil art: a quarter of the furrowed (or watered) texture per tile, with a
##    raised lip drawn where it meets undug ground, and simple drawn crops.
const EDGES := preload("res://art/lunar/agri/crop_edges.png")
const SOIL := preload("res://art/lunar/agri/soil.png")
const WATERED := preload("res://art/lunar/agri/watered.png")
const PONDS := preload("res://art/lunar/agri/ponds.png")
const MapData = preload("res://scripts/map_data.gd")
const SPRING_TINT := Color(0.90, 1.04, 1.04)
const FPS := 6.25
const ART_CELL := 48
const WORLD_CELL := 32
const TILE := 16
const ART := 2.0 / 3.0                     # one art pixel, in world units
# Atlas rows of crop_edges.png run clockwise from the north edge, followed by grass on all four edges (8) and
# a tilled interior (9). Units here are two map tiles.
const HERB_PATCHES := [Vector2i(20, 16), Vector2i(21, 16), Vector2i(22, 16)]
const LIP := Color("a7764c")               # the raised edge of a dug tile, where it meets undug ground
const LIP_SHADOW := Color("3e2617")

var station: Node
var pond_cells: Array[Vector2i] = []
var spring_cells: Array[Vector2i] = []
var elapsed := 0.0
var frame := -1
var cursor := Vector2i(-1, -1)
var field := Rect2i()
var art_field: Texture2D
var art_tilled: Texture2D
var art_wet: Texture2D
var art_border: Texture2D
var crop_art := {}
var crop_sprites := {}                     # tile -> Sprite2D in the game's depth-sorted layer (station.actors)

func setup(game: Node, rows: Array) -> void:
	station = game
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	for y in rows.size():
		for x in rows[y].length():
			match rows[y][x]:
				"Y": pond_cells.append(Vector2i(x, y))
				"O": spring_cells.append(Vector2i(x, y))
	var f: Array = MapData.FARM_FIELDS.get("agri", [])
	if f.size() == 4:
		field = Rect2i(int(f[0]), int(f[1]), int(f[2]), int(f[3]))
	art_field = _load("res://art/farm/field.png")
	art_tilled = _load("res://art/farm/tilled.png")
	art_wet = _load("res://art/farm/tilled_wet.png")
	art_border = _load("res://art/farm/field_border.png")
	visibility_changed.connect(_sync_visibility)

func _load(path: String) -> Texture2D:
	return load(path) if ResourceLoader.exists(path) else null

func _sync_visibility() -> void:
	set_process(is_visible_in_tree())
	if is_processing():
		_process(0.0)

func _process(delta: float) -> void:
	elapsed = fmod(elapsed + delta, 8.0 / FPS)
	var next := floori(elapsed * FPS)
	var c: Vector2i = station.farm_cursor() if station.current_area == "agri" else Vector2i(-1, -1)
	if next != frame or c != cursor:
		frame = next
		cursor = c
		queue_redraw()

func _draw() -> void:
	if frame < 0:
		return
	_draw_field()
	# The herb patches: the farm's field dirt and grass border when that art exists, else the old soil art.
	if art_field != null:
		_draw_undug(Rect2i(HERB_PATCHES[0] * 2, Vector2i(HERB_PATCHES.size() * 2, 2)))
	else:
		for patch in HERB_PATCHES:
			_draw_cell(patch, 8)
	_draw_water(pond_cells, Color.WHITE)
	_draw_water(spring_cells, SPRING_TINT)

# ---------------------------------------------------------------- the field

func _draw_field() -> void:
	if field.size == Vector2i.ZERO:
		return
	# Undug ground: the new field art per tile, or the old 2 x 2-tile soil pieces with their grass border.
	if art_field != null:
		_draw_undug(field)
	else:
		var c0: Vector2i = field.position / 2
		var cells: Vector2i = field.size / 2
		for cy in cells.y:
			for cx in cells.x:
				var row := _frame_row(cx, cy, cells)
				var cell := c0 + Vector2i(cx, cy)
				if row < 0:
					var v := _variant(cell.x, cell.y)
					draw_texture_rect_region(SOIL, Rect2(cell * WORLD_CELL, Vector2.ONE * WORLD_CELL), Rect2(v * ART_CELL, 0, ART_CELL, ART_CELL))
				else:
					_draw_cell(cell, row)
	var day: int = station.day
	for tile in station.farm:
		var t: Dictionary = station.farm[tile]
		_draw_dug(tile, int(t["watered"]) == day)
	for tile in station.farm:
		var stage: int = station.crop_stage(station.farm[tile])
		if stage >= 0 and not crop_sprites.has(tile):          # stand-ins only: painted crops are sprites
			_draw_crop(tile, str(station.farm[tile]["crop"]), stage)
	if cursor.x >= 0:
		draw_rect(Rect2(cursor * TILE, Vector2.ONE * TILE).grow(-ART * 0.5), Color(1, 1, 1, 0.75), false, ART)

# Undug dirt over a rectangle of tiles, with the grass border round its edge (art/farm/field_border.png).
func _draw_undug(r: Rect2i) -> void:
	for y in range(r.position.y, r.end.y):
		for x in range(r.position.x, r.end.x):
			var v := _variant(x, y)
			draw_texture_rect_region(art_field, Rect2(x * TILE, y * TILE, TILE, TILE), Rect2(v * 24, 0, 24, 24))
			var inside := (1 if y > r.position.y else 0) + (2 if x < r.end.x - 1 else 0) \
				+ (4 if y < r.end.y - 1 else 0) + (8 if x > r.position.x else 0)
			if art_border != null and inside != 15:
				draw_texture_rect_region(art_border, Rect2(x * TILE, y * TILE, TILE, TILE), Rect2((inside % 4) * 24, (inside / 4) * 24, 24, 24))

# Which piece of the old soil art a 2 x 2-tile cell of the field takes: its grass frame round the edge, plain
# dirt inside (-1).
func _frame_row(cx: int, cy: int, cells: Vector2i) -> int:
	var n := cy == 0
	var s := cy == cells.y - 1
	var w := cx == 0
	var e := cx == cells.x - 1
	if n and w: return 7
	if n and e: return 1
	if s and e: return 3
	if s and w: return 5
	if n: return 0
	if e: return 2
	if s: return 4
	if w: return 6
	return -1

func _variant(x: int, y: int) -> int:
	return ((x * 17) ^ (y * 29)) % 3

func _dug(tile: Vector2i) -> bool:
	return station.farm.has(tile)

func _draw_dug(tile: Vector2i, wet: bool) -> void:
	var dst := Rect2(tile * TILE, Vector2.ONE * TILE)
	var joins := (1 if _dug(tile + Vector2i.UP) else 0) + (2 if _dug(tile + Vector2i.RIGHT) else 0) \
		+ (4 if _dug(tile + Vector2i.DOWN) else 0) + (8 if _dug(tile + Vector2i.LEFT) else 0)
	var sheet: Texture2D = art_wet if wet and art_wet != null else art_tilled
	if sheet != null:
		draw_texture_rect_region(sheet, dst, Rect2((joins % 4) * 24, (joins / 4) * 24, 24, 24))
		return
	# The old art: the quarter of a 48-pixel furrow (or watered) cell that falls on this tile, so neighbours
	# join up into one texture, and a lip on every side that meets undug ground.
	var cell: Vector2i = tile / 2
	var v := _variant(cell.x, cell.y)
	var quarter := Vector2((tile.x % 2) * 24, (tile.y % 2) * 24)
	if wet:
		draw_texture_rect_region(WATERED, dst, Rect2(Vector2(frame * ART_CELL, v * ART_CELL) + quarter, Vector2(24, 24)))
	else:
		draw_texture_rect_region(EDGES, dst, Rect2(Vector2(v * ART_CELL, 9 * ART_CELL) + quarter, Vector2(24, 24)))
	var o: Vector2 = dst.position
	if joins & 1 == 0:
		draw_rect(Rect2(o, Vector2(TILE, ART)), LIP); draw_rect(Rect2(o + Vector2(0, ART), Vector2(TILE, ART)), LIP_SHADOW)
	if joins & 4 == 0:
		draw_rect(Rect2(o + Vector2(0, TILE - 2 * ART), Vector2(TILE, ART)), LIP_SHADOW); draw_rect(Rect2(o + Vector2(0, TILE - ART), Vector2(TILE, ART)), LIP)
	if joins & 8 == 0:
		draw_rect(Rect2(o, Vector2(ART, TILE)), LIP); draw_rect(Rect2(o + Vector2(ART, 0), Vector2(ART, TILE)), LIP_SHADOW)
	if joins & 2 == 0:
		draw_rect(Rect2(o + Vector2(TILE - 2 * ART, 0), Vector2(ART, TILE)), LIP_SHADOW); draw_rect(Rect2(o + Vector2(TILE - ART, 0), Vector2(ART, TILE)), LIP)

# ---------------------------------------------------------------- crops

# Painted crops stand in the same depth-sorted layer as people and props, so a tall crop in the row above
# the player covers their feet and one in the row below stays behind them (21 Nov). Their sort point is the
# planted tile's foot line, as for a person standing on it. Call after anything changes on the field.
func sync_crops() -> void:
	queue_redraw()
	if station == null or station.actors == null:
		return
	var keep := {}
	for tile in station.farm:
		var t: Dictionary = station.farm[tile]
		var stage: int = station.crop_stage(t)
		if stage < 0:
			continue
		var crop: String = str(t["crop"])
		if not crop_art.has(crop):
			crop_art[crop] = _load("res://art/farm/crops/%s.png" % crop)
		var tex: Texture2D = crop_art[crop]
		if tex == null:
			continue                                   # no art: the stand-in is drawn on the ground
		var sp: Sprite2D = crop_sprites.get(tile)
		if sp == null:
			sp = Sprite2D.new()
			sp.centered = false
			sp.region_enabled = true
			sp.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			sp.scale = Vector2.ONE * ART
			sp.offset = Vector2(-12, -42)              # bottom of the picture on the tile's bottom edge
			sp.position = Vector2(tile.x * TILE + 8, tile.y * TILE + 12)
			station.actors.add_child(sp)
			station.area_sprites.append([sp, "agri"])
			crop_sprites[tile] = sp
		sp.texture = tex
		var frames: int = maxi(1, tex.get_width() / 24)
		sp.region_rect = Rect2(mini(stage, frames - 1) * 24, 0, 24, 48)
		sp.visible = station.current_area == "agri"
		keep[tile] = true
	for tile in crop_sprites.keys():
		if keep.has(tile):
			continue
		var gone: Sprite2D = crop_sprites[tile]
		crop_sprites.erase(tile)
		for i in range(station.area_sprites.size() - 1, -1, -1):
			if station.area_sprites[i][0] == gone:
				station.area_sprites.remove_at(i)
		gone.queue_free()


func _draw_crop(tile: Vector2i, crop: String, stage: int) -> void:
	if not crop_art.has(crop):
		crop_art[crop] = _load("res://art/farm/crops/%s.png" % crop)
	var tex: Texture2D = crop_art[crop]
	if tex != null:
		# One 24 x 48 picture per stage, standing on the bottom of the tile.
		var n: int = maxi(1, tex.get_width() / 24)
		var k: int = mini(stage, n - 1)
		draw_texture_rect_region(tex, Rect2(tile.x * TILE, tile.y * TILE - TILE, TILE, 2 * TILE), Rect2(k * 24, 0, 24, 48))
		return
	# Stand-ins until the crop art arrives, drawn in art pixels (24 to a tile; negative y reaches up).
	var ripe: bool = stage >= int(station.CROPS[crop]["stages"])
	var leaf := Color("5f9a3e")
	var leaf_dark := Color("3d6a2a")
	if stage == 0:
		_px(tile, 9, 14, 2, 2, Color("4a2c18")); _px(tile, 13, 16, 2, 2, Color("4a2c18")); _px(tile, 11, 11, 2, 2, Color("4a2c18"))
		return
	if not ripe:
		var h: int = 3 + stage * 4
		_px(tile, 11, 20 - h, 2, h, leaf_dark)
		_px(tile, 7, 20 - h, 4, 3, leaf); _px(tile, 13, 22 - h, 4, 3, leaf)
		if stage >= 2:
			_px(tile, 6, 23 - h, 4, 3, leaf_dark); _px(tile, 14, 18 - h + 6, 4, 3, leaf)
		return
	match crop:
		"crater_potato":
			_px(tile, 5, 8, 14, 10, leaf); _px(tile, 7, 6, 10, 3, leaf); _px(tile, 6, 14, 12, 4, leaf_dark)
			_px(tile, 6, 18, 5, 4, Color("8c6096")); _px(tile, 13, 19, 5, 3, Color("8c6096")); _px(tile, 7, 18, 2, 1, Color("b48cc0"))
		"moon_wheat":
			for x in [6, 11, 16]:
				_px(tile, x, -2, 2, 22, Color("b79c5a"))
				_px(tile, x - 1, -8, 4, 7, Color("e6d48c")); _px(tile, x, -9, 2, 1, Color("f4e8b4"))
		"star_tomato":
			_px(tile, 5, 2, 14, 18, leaf); _px(tile, 7, 0, 10, 3, leaf_dark); _px(tile, 11, 2, 2, 18, leaf_dark)
			for p in [Vector2i(6, 6), Vector2i(14, 4), Vector2i(9, 12), Vector2i(15, 13), Vector2i(7, 17)]:
				_px(tile, p.x, p.y, 3, 3, Color("d6403c")); _px(tile, p.x, p.y, 1, 1, Color("f08070"))
		_:
			_px(tile, 7, 6, 10, 14, leaf)

func _px(tile: Vector2i, ax: int, ay: int, w: int, h: int, color: Color) -> void:
	draw_rect(Rect2(Vector2(tile * TILE) + Vector2(ax, ay) * ART, Vector2(w, h) * ART), color)

# ---------------------------------------------------------------- herb patches and water

func _draw_cell(cell: Vector2i, row: int) -> void:
	var v := _variant(cell.x, cell.y)
	draw_texture_rect_region(EDGES, Rect2(cell * WORLD_CELL, Vector2i.ONE * WORLD_CELL), Rect2(v * ART_CELL, row * ART_CELL, ART_CELL, ART_CELL))

func _draw_water(cells: Array[Vector2i], tint: Color) -> void:
	for tile in cells:
		var cell := tile / 2
		var variant := ((cell.x * 17) ^ (cell.y * 29)) % 3
		var offset := (tile % 2) * 24
		var src := Rect2(Vector2i(frame, variant) * ART_CELL + offset, Vector2i(24, 24))
		draw_texture_rect_region(PONDS, Rect2(tile * 16, Vector2i(16, 16)), src, tint)
