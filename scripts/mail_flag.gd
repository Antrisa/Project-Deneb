extends Node2D
# The envelope that bobs over your mailbox (the message pad on your front porch) while a letter waits in it, as in
# Stardew Valley. Drawn here in code on the world's 16-unit tile grid, just above the top of the pad.
# main.gd makes one for the prop titled "Message pad" (_spawn_prop) and shows it only on that map.

var world                      # main.gd: mail_waiting
var _t := 0.0

const EDGE := Color("4a3a32")
const PAPER := Color("fbf3dc")
const SHADE := Color("e2d2ac")
const SEAL := Color("c4463a")


func _process(delta: float) -> void:
	if not visible:
		return
	_t += delta
	queue_redraw()


func _draw() -> void:
	if world == null or world.mail_waiting.is_empty():
		return
	var y: float = -16.0 + roundf(sin(_t * 3.2) * 2.0)
	# a soft shadow on the mailbox lid, then the envelope: 12 x 8, its flap folded down to a red seal
	draw_rect(Rect2(-5, -3, 10, 2), Color(0, 0, 0, 0.18))
	draw_rect(Rect2(-6, y, 12, 8), EDGE)
	draw_rect(Rect2(-5, y + 1, 10, 6), PAPER)
	draw_rect(Rect2(-5, y + 5, 10, 2), SHADE)
	for i in 5:                                     # the flap: a V of one-unit steps down to the middle
		draw_rect(Rect2(-5 + i, y + 1 + i * 0.8, 1, 1), EDGE)
		draw_rect(Rect2(4 - i, y + 1 + i * 0.8, 1, 1), EDGE)
	draw_rect(Rect2(-1, y + 4, 2, 2), SEAL)
