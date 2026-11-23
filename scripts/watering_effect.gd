extends Node2D
# Each droplet keeps the position where it left the tilting can.
const Player = preload("res://scripts/player.gd")
const PIXEL := 2.0 / 3.0
const FALL_TIME := 0.19
const LANDINGS: Array[Vector2] = [
	Vector2(-2, 0), Vector2(1, -1), Vector2(-1, 2),
	Vector2(3, 1), Vector2(0, -2), Vector2(-3, 1),
]
var spout: Callable
var elapsed := 0.0
var origins: Array[Vector2] = []


func release_time(i: int) -> float:
	return (0.54 + 0.036 * i) * Player.HELD_LEN


func _process(delta: float) -> void:
	elapsed += delta
	while origins.size() < LANDINGS.size() and elapsed >= release_time(origins.size()):
		var origin := Vector2(0, -14)  # Generic hand tool if the equipped tier has no held art.
		if spout.is_valid():
			var world_point: Vector2 = spout.call()
			origin = to_local(world_point) if world_point.is_finite() else Vector2.INF
		origins.append(origin)
	queue_redraw()
	if elapsed >= release_time(LANDINGS.size() - 1) + FALL_TIME:
		queue_free()


func drop_position(i: int) -> Vector2:
	var t := (elapsed - release_time(i)) / FALL_TIME
	if t < 0.0 or t >= 1.0 or not origins[i].is_finite():
		return Vector2.INF
	var at := origins[i].lerp(LANDINGS[i], t)
	at.y = lerpf(origins[i].y, LANDINGS[i].y, t*t) - 1.5 * sin(PI*t)
	return at.snapped(Vector2.ONE * PIXEL)


func _draw() -> void:
	for i in origins.size():
		var at := drop_position(i)
		if at.is_finite():
			draw_rect(Rect2(at, Vector2(PIXEL, 2*PIXEL)), Color("78becb"))
			draw_rect(Rect2(at, Vector2(PIXEL, PIXEL)), Color("c0ebe6"))
