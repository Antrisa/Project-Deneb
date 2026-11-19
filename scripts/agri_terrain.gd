extends Node2D
## Animated ground belongs below the planters, player and other props.
const EDGES := preload("res://art/lunar/agri/crop_edges.png")
const WATERED := preload("res://art/lunar/agri/watered.png")
const PONDS := preload("res://art/lunar/agri/ponds.png")
const SPRING_TINT := Color(0.90, 1.04, 1.04)
const FPS := 6.25
const ART_CELL := 48
const WORLD_CELL := 32
# Atlas rows run clockwise from the north edge, followed by grass on all
# four edges (8) and a tilled interior (9). Units here are two map tiles.
const BED_ORIGIN := Vector2i(21, 8)
const BED := [
	[7, 0, 0, 1],
	[6, 9, 9, 2],
	[6, 9, 9, 2],
	[6, 9, 9, 2],
	[6, 9, 9, 2],
	[5, 4, 4, 3],
]
const HERB_PATCHES := [Vector2i(20, 16), Vector2i(21, 16), Vector2i(22, 16)]

var station: Node
var pond_cells: Array[Vector2i] = []
var spring_cells: Array[Vector2i] = []
var elapsed := 0.0
var frame := -1
var watered := false

func setup(game: Node, rows: Array) -> void:
	station = game
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	for y in rows.size():
		for x in rows[y].length():
			match rows[y][x]:
				"Y": pond_cells.append(Vector2i(x, y))
				"O": spring_cells.append(Vector2i(x, y))
	visibility_changed.connect(_sync_visibility)

func _sync_visibility() -> void:
	set_process(is_visible_in_tree())
	if is_processing():
		_process(0.0)

func _process(delta: float) -> void:
	elapsed = fmod(elapsed + delta, 8.0 / FPS)
	var next := floori(elapsed * FPS)
	var wet: bool = station.garden_watered_day == station.day
	if next != frame or wet != watered:
		frame = next
		watered = wet
		queue_redraw()

func _draw() -> void:
	if frame < 0:
		return
	for y in BED.size():
		for x in BED[y].size():
			_draw_soil(BED_ORIGIN + Vector2i(x, y), BED[y][x])
	for patch in HERB_PATCHES:
		_draw_soil(patch, 8)
	_draw_water(pond_cells, Color.WHITE)
	_draw_water(spring_cells, SPRING_TINT)

func _draw_soil(cell: Vector2i, row: int) -> void:
	var variant := ((cell.x * 17) ^ (cell.y * 29)) % 3
	var dst := Rect2(cell * WORLD_CELL, Vector2i.ONE * WORLD_CELL)
	if row == 9 and watered:
		draw_texture_rect_region(WATERED, dst, Rect2(frame * ART_CELL, variant * ART_CELL, ART_CELL, ART_CELL))
	else:
		draw_texture_rect_region(EDGES, dst, Rect2(variant * ART_CELL, row * ART_CELL, ART_CELL, ART_CELL))

func _draw_water(cells: Array[Vector2i], tint: Color) -> void:
	for tile in cells:
		var cell := tile / 2
		var variant := ((cell.x * 17) ^ (cell.y * 29)) % 3
		var offset := (tile % 2) * 24
		var src := Rect2(Vector2i(frame, variant) * ART_CELL + offset, Vector2i(24, 24))
		draw_texture_rect_region(PONDS, Rect2(tile * 16, Vector2i(16, 16)), src, tint)
