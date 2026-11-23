extends CanvasLayer
# Reading your letters (Zachary, 23 Nov: mail from the residents, as in Stardew Valley), drawn in the Terran
# datapad style like the other new screens. Opened from your mailbox: the message pad on the agri complex's front
# porch.
#   - Your letters down the left, newest first; a dot marks one you haven't read.
#   - The letter you picked on a sheet of paper on the right. It opens on the oldest one you haven't read.
#   - Click a letter (or press Up / Down) to read it. The pad keeps every letter, so you can read it again.
#   - Esc, E, a right-click or Close puts the letters away.
# main.gd owns the mail (mail_waiting, mail_days, read_letter()); this file only draws it and takes clicks.

const MailData = preload("res://scripts/mail_data.gd")
const ShipScreen = preload("res://ui/ship_screen.gd")
const Calendar = preload("res://scripts/datapad_bridge.gd")

const PAPER := Color("fbf6e8")
const PAPER_RIM := Color("c9bfa8")
const NEW_DOT := Color("c9932f")
const ROW := 34.0                        # one letter in the list
const LIST_W := 214.0

var world                                # main.gd
var open := false
var showing := ""                        # the id of the letter on the paper
var screen: ShipScreen


func _ready() -> void:
	layer = 14
	screen = ShipScreen.new()
	add_child(screen)
	screen.fill = true
	screen.paint = Callable(self, "_paint")
	screen.on_click = Callable(self, "_click")
	visible = false


func start() -> void:
	var list: Array = letters()
	if list.is_empty():
		return
	# the oldest letter you haven't read, or else the newest
	showing = str(list[0])
	for id in world.mail_waiting:
		if list.has(str(id)):
			showing = str(id)
			break
	world.read_letter(showing)
	open = true
	visible = true
	world.sfx("click")
	screen.redraw()


func close() -> void:
	open = false
	visible = false


func _process(_delta: float) -> void:
	if open:
		screen.redraw()


# Keys come from main.gd's _unhandled_input while this is open.
func handle_input(ev: InputEvent) -> void:
	if ev.is_action_pressed("cancel") or ev.is_action_pressed("interact"):
		close()
	elif ev.is_action_pressed("move_up"):
		_step(-1)
	elif ev.is_action_pressed("move_down"):
		_step(1)


# Every letter that has come, newest first (the order they came in, turned round).
func letters() -> Array:
	var out: Array = []
	var came: Array = world.mail_days.keys()
	for i in range(came.size() - 1, -1, -1):
		if MailData.LETTERS.has(str(came[i])):
			out.append(str(came[i]))
	return out


func _step(by: int) -> void:
	var list: Array = letters()
	if list.is_empty():
		return
	var at: int = clampi(list.find(showing) + by, 0, list.size() - 1)
	_show(str(list[at]))


func _show(id: String) -> void:
	if id == showing:
		return
	showing = id
	world.read_letter(id)
	world.sfx("click")


func _click(id: String, _p: Vector2, button: int) -> void:
	if button == MOUSE_BUTTON_RIGHT:
		close()
		return
	if button != MOUSE_BUTTON_LEFT:
		return
	if id == "close":
		close()
	elif id.begins_with("letter/"):
		_show(id.substr(7))


# "Spring 3": the day a letter came.
func _date(id: String) -> String:
	var d: Array = Calendar.season_date(int(world.mail_days.get(id, world.day)))
	return "%s %d" % [str(d[0]), int(d[1])]


func _paint() -> void:
	var s := screen
	s.case_fill("Mail")
	var top := 34.0
	var bottom: float = s.page.y - 44.0
	var list: Array = letters()
	# the letters
	var box := Rect2(12, top, LIST_W, bottom - top)
	s.panel(box, "journal", "Letters")
	var rows: int = maxi(1, int((box.size.y - 32.0) / ROW))
	var at: int = maxi(0, list.find(showing))
	var first: int = clampi(at - rows + 1, 0, maxi(0, list.size() - rows))
	var y: float = top + 29.0
	for i in range(first, mini(list.size(), first + rows)):
		var id: String = list[i]
		var letter: Dictionary = MailData.LETTERS[id]
		var r := Rect2(box.position.x + 6, y, box.size.x - 12, ROW - 4)
		if id == showing:
			s.frame(r, Color("f0d4b9"), Color("c3b8a5"), Color("f9e8d2"), Color("bd8b67"))
		else:
			s.frame(r, Color("f0eee7"), Color("c3b8a5"), Color("fffdf6"), Color("d5cfc1"))
		if world.mail_waiting.has(id):
			s.rect(Rect2(r.position.x + 6, r.position.y + 7, 5, 5), NEW_DOT)
		s.text_fit(r.position.x + 16, r.position.y + 3, r.size.x - 22, str(letter.get("title", id)), "label", ShipScreen.INK)
		s.text_fit(r.position.x + 16, r.position.y + 17, r.size.x - 22, "%s - %s" % [str(letter.get("from", "")), _date(id)], "micro", ShipScreen.MUTED)
		if s.hovering(r):
			s.outline(r, ShipScreen.ORANGE)
		s.hit("letter/" + id, r)
		y += ROW
	if list.size() > rows:
		s.text_center(box.get_center().x, box.end.y - 14, "%d of %d" % [at + 1, list.size()], "micro", ShipScreen.MUTED)
	# the letter itself, on paper
	var paper := Rect2(box.end.x + 10, top, s.page.x - box.end.x - 22, bottom - top)
	_paint_letter(paper, showing)
	# the bottom row
	s.shift(s.bottom_left())
	s.status("Click a letter to read it. Esc or right-click puts them away.")
	s.shift(s.bottom_right())
	s.solid_button("close", Rect2(625, 388, 82, 22), "Close")
	s.shift(Vector2.ZERO)


func _paint_letter(r: Rect2, id: String) -> void:
	var s := screen
	s.rect(Rect2(r.position + Vector2(2, 2), r.size), Color(0, 0, 0, 0.12))
	s.frame(r, PAPER, PAPER_RIM, Color("fffdf7"), Color("e6dcc6"))
	var letter: Dictionary = MailData.LETTERS.get(id, {})
	if letter.is_empty():
		return
	var x: float = r.position.x + 24.0
	var w: float = r.size.x - 48.0
	var y: float = r.position.y + 16.0
	s.text_fit(x, y, w - 90.0, str(letter.get("title", "")), "mid", ShipScreen.INK)
	s.text_right(r.end.x - 24.0, y + 7.0, _date(id).to_upper(), "micro", ShipScreen.MUTED)
	y += 27.0
	s.text(x, y, "From " + str(letter.get("from", "")), "label", ShipScreen.MUTED)
	y += 18.0
	s.rect(Rect2(x, y, w, 1), ShipScreen.RULE)
	y += 12.0
	for para in letter.get("body", []):
		y = s.wrap_text(x, y, w, str(para), "body", ShipScreen.INK, 17.0)
		y += 7.0
	var sign: String = str(letter.get("sign", ""))
	if sign != "":
		s.text_right(r.end.x - 30.0, y + 4.0, "- " + sign, "strong", ShipScreen.INK)
