extends "res://scripts/lunar_portal.gd"
# Painted wayfinding belongs below the actors, not in the door's foreground layer.
func _draw() -> void:
	var color := Color("e9b65f")
	if destination == "medbay": color=Color("91d8bc")
	elif kind == "lift":color=Color("78d6d0")
	icon(Vector2.ZERO,color)
