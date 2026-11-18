extends Node2D
# Separate architectural modules on a shared hull. World units remain pixels.
var player: Node2D
var elapsed := 0.0
var door_open := 0.0
var door: Node2D
var fan: Node2D
var lamp_material: ShaderMaterial
var door_material: ShaderMaterial
var door_world := Vector2.ZERO
func piece(key: String, point: Vector2) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = load("res://art/mess_hall/%s.png" % key)
	s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	s.centered = false
	s.scale = Vector2.ONE * (2.0 / 3.0)   # 24-pixel-grid art
	s.position = point
	add_child(s)
	return s
func setup(data: Array) -> void:
	position = Vector2(float(data[1])*16.0,(float(data[2])+float(data[4]))*16.0)
	door_world = position + Vector2(152,-8)
	# Wall modules meet at pilasters; utility panels occupy the solid rear deck.
	for x in [0.0,100.0,200.0]:
		var panel := piece("service",Vector2.ZERO)
		panel.position = Vector2(x,-64.0-panel.texture.get_height()*0.5)
	for x in [16.0,188.0]:
		var window := piece("window",Vector2.ZERO)
		window.position = Vector2(x,-window.texture.get_height()*0.5)
	for x in [0.0,288.0]:piece("pillar",Vector2(x,-64))
	door = preload("res://scripts/mess_door.gd").new()
	door.position = Vector2(120,-door.tex.get_height()*0.5)
	add_child(door)
	lamp_material = ShaderMaterial.new()
	lamp_material.shader = load("res://shaders/mess_lights.gdshader")
	for child in get_children():
		if child != door:child.material = lamp_material
	queue_redraw()
func _process(delta: float) -> void:
	if not visible:return
	elapsed += delta
	var near := is_instance_valid(player) and player.global_position.distance_to(door_world)<58.0
	door_open = move_toward(door_open,1.0 if near else 0.0,delta*2.5)
	door.opening = door_open
	door.queue_redraw()
	queue_redraw()
func _draw() -> void:
	draw_rect(Rect2(0,-64,304,64),Color("b7a394"))
	draw_rect(Rect2(0,-66,304,2),Color("d9c4ad"))
	# Floor-level shadow grounds the facade; little moving fans are separate geometry.
	draw_rect(Rect2(0,0,304,3),Color(0.05,0.08,0.12,0.3))
	for x in [80.0,180.0,280.0]:
		var c := Vector2(x,-94)
		for a in [0.0,PI/2.0]:
			var d := Vector2(cos(elapsed*1.6+a),sin(elapsed*1.6+a))*4.0
			draw_line(c-d,c+d,Color("899198"),1.0)
