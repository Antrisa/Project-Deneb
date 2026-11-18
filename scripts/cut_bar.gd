extends Node2D
# The little bar over a vein or rock while the mining laser is held on it (main.gd _update_cut).
# Its fill (0..1) is kept in the "f" meta value.


func _draw() -> void:
	var f: float = float(get_meta("f", 0.0))
	draw_rect(Rect2(-1, -1, 18, 5), Color(0.05, 0.05, 0.08, 0.85))
	draw_rect(Rect2(0, 0, 16.0 * f, 3), Color(1.0, 0.82, 0.35).lerp(Color(0.5, 1.0, 0.55), f))
