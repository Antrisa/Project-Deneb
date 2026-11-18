extends Node2D
# Each solid component has its own depth anchor. The basin water is animated separately.
var phase := 0.0
var water: Node2D
func _ready() -> void:
	y_sort_enabled = true
	_add_part("fountain_rear",Vector2(0,-28),Vector2(-56,-17))
	water = preload("res://scripts/lunar_water.gd").new()
	add_child(water)
	_add_part("fountain_column",Vector2(0,0),Vector2(-22,-82))
	var front := Node2D.new()
	front.name="FrontRimAndPanels"
	front.position=Vector2(0,44)
	add_child(front)
	_sprite(front,"fountain_front",Vector2(-56,-68))
	_sprite(front,"fountain_board",Vector2(-43,-31))
	_sprite(front,"fountain_calendar",Vector2(11,-31))
func _add_part(asset: String,anchor: Vector2,draw_at: Vector2) -> void:
	var part := Node2D.new()
	part.name=asset
	part.position=anchor
	add_child(part)
	_sprite(part,asset,draw_at)
func _sprite(parent: Node2D,asset: String,at: Vector2) -> void:
	var s := Sprite2D.new()
	s.texture=load("res://art/lunar/%s.png"%asset)
	s.centered=false
	s.scale=Vector2.ONE*(2.0/3.0)   # 24-pixel-grid art, like everything else
	s.offset=at*1.5
	s.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
	parent.add_child(s)
