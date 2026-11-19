extends Node2D
## A high north wall leaves the kitchen fixtures and dining-room paths free.
const WINDOW := preload("res://art/mess_hall/window.png")
const PANEL := preload("res://art/lunar/material_2.png")
const SHUTTLE := preload("res://art/mess_hall/service_shuttle.png")
const ART := 2.0 / 3.0
const HEADROOM := 40
const WINDOW_AT := Vector2(96, -36)
const GLASS := Rect2i(6, 8, 138, 25)
const DINNER := 18 * 60
var clock: Node
var wall_width := 0
var shuttle_x := -100

func setup(game: Node, columns: int) -> void:
	clock = game
	wall_width = columns * 16
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	visibility_changed.connect(_sync_visibility)

func _sync_visibility() -> void:
	set_process(is_visible_in_tree())
	if is_processing():
		_process(0.0)

func _process(_delta: float) -> void:
	var minutes: float = clock.minutes
	var pass_time := fposmod(minutes - DINNER, 20.0)
	var x := -100
	if minutes >= DINNER and minutes < DINNER + 120 and pass_time < 5.0:
		x = GLASS.position.x - SHUTTLE.get_width() + floori(pass_time / 5.0 * (GLASS.size.x + SHUTTLE.get_width()))
	if x != shuttle_x:
		shuttle_x = x
		queue_redraw()

func _draw() -> void:
	draw_set_transform(Vector2(0, -HEADROOM), 0.0, Vector2.ONE * ART)
	var hull := Rect2(0, 0, wall_width / ART, HEADROOM / ART)
	draw_texture_rect(PANEL, hull, true)
	draw_set_transform(WINDOW_AT, 0.0, Vector2.ONE * ART)
	draw_texture(WINDOW, Vector2.ZERO)
	var ship := Rect2i(Vector2i(shuttle_x, 20), SHUTTLE.get_size())
	var visible_part := ship.intersection(GLASS)
	if visible_part.has_area():
		draw_texture_rect_region(SHUTTLE, Rect2(visible_part), Rect2(visible_part.position - ship.position, visible_part.size))
