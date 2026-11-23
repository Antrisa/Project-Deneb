extends Sprite2D
var title := ""
var phase := 0.0
var mail_world = null          # main.gd, for the message pad by your front door: its screen lights up when mail waits
func _process(delta: float) -> void:
	if visible:
		phase += delta
		queue_redraw()
func _draw() -> void:
	if texture == null: return
	var y: float = -texture.get_height()+7
	var ink := Color("79dfd0")
	draw_rect(Rect2(5,y,22,29),Color("163742"))
	var mid := Vector2(16,y+8)
	if "Medbay" in title:
		draw_rect(Rect2(mid-Vector2(2,5),Vector2(4,10)),ink)
		draw_rect(Rect2(mid-Vector2(5,2),Vector2(10,4)),ink)
	elif "Manufacturing" in title:
		draw_arc(mid,5,0,TAU,8,ink,2)
		draw_line(mid-Vector2(7,0),mid+Vector2(7,0),ink,1)
	elif "Message" in title:
		# your mailbox (23 Nov): an envelope on the screen, blinking amber while a letter waits
		if mail_world != null and not mail_world.mail_waiting.is_empty() and fmod(phase, 1.0) < 0.6:
			ink = Color("f2c94c")
		draw_rect(Rect2(mid - Vector2(7, 4), Vector2(14, 9)), ink, false, 1)
		draw_line(mid - Vector2(7, 4), mid + Vector2(0, 1), ink, 1)
		draw_line(mid + Vector2(7, -4), mid + Vector2(0, 1), ink, 1)
	elif "Community" in title:
		draw_rect(Rect2(mid-Vector2(6,5),Vector2(12,10)),ink,false,1)
		draw_line(mid-Vector2(0,5),mid+Vector2(0,5),ink,1)
	else:
		draw_arc(mid,6,0,PI,8,ink,2)
		draw_line(mid-Vector2(6,0),mid+Vector2(6,0),ink,1)
	for i in range(3):draw_rect(Rect2(8,y+17+i*4,16-i*3,2),ink.darkened(0.2))
	draw_line(Vector2(6,y+fmod(phase*10,28)),Vector2(26,y+fmod(phase*10,28)),Color(0.7,1,1,0.15),1)
