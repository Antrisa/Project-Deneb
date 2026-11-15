extends Control
# A stretchy frame drawn from a picture laid out as a 3x3 grid:
# the four corners keep their size, the edges and the middle stretch to fit.
# Used for the dialogue box and the portrait border. The picture can be any size.

var tex: Texture2D
var corner := 8.0          # how big the corners are drawn, in screen units


func _draw() -> void:
	if tex == null:
		return
	var cw: float = tex.get_width() / 3.0
	var ch: float = tex.get_height() / 3.0
	var xs: Array = [0.0, corner, size.x - corner, size.x]
	var ys: Array = [0.0, corner, size.y - corner, size.y]
	for j in 3:
		for i in 3:
			var x0: float = xs[i]
			var x1: float = xs[i + 1]
			var y0: float = ys[j]
			var y1: float = ys[j + 1]
			draw_texture_rect_region(tex, Rect2(x0, y0, x1 - x0, y1 - y0), Rect2(i * cw, j * ch, cw, ch))
