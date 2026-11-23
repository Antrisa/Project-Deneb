extends CanvasLayer
# Station repairs (Zachary, 23 Nov): parts of the Agri Complex stay broken and sealed until you pay S.A.R.A. to
# repair them. "the fishponds circle should be broken and closed off until you do the harbinger quest and then pay
# sara to fix it", and the storage dome is "also broken until you pay sara with scrip and materials to reopen".
# Drawn in the Terran datapad style like the other new screens. Opened from a sealed door, or when S.A.R.A. brings it
# up:
#   - the repairs she can do down the left, with how each stands;
#   - the one you picked on the right: what she says about it, what it needs and what you have, and a look at it
#     through the station's cameras;
#   - Pay S.A.R.A. Her drones work overnight, and the doors open in the morning (main.gd _next_day).
# Esc, E, a right-click or Close puts the page away; Up / Down pick another repair.
# main.gd owns the state (station_fixed, station_due, repair_state(), pay_station_repair()); this file holds the
# list of repairs and draws the page. The map side: tools/spaceport.py (the sealed doors are INNER_DOORS with owner
# "repair:<id>", and the wreckage inside is cleared from the SEALED_ROOMS boxes).

const ShipScreen = preload("res://ui/ship_screen.gd")
const ItemData = preload("res://scripts/item_data.gd")
const MapData = preload("res://scripts/map_data.gd")

# id -> its name, where it is, what S.A.R.A. says about it, the price in Scrip and the materials (item id -> how
# many), and "mention", what she says when she brings it up (once a day, when you talk to her and it can start). A
# repair that has to wait has "after" (a flag on main.gd that must be true) and "wait" (what she says until then). The prices are first guesses, to settle with the price sheet. The wording is Claude's draft.
const REPAIRS := {
	"storage": {
		"name": "Storage dome",
		"where": "Agri Complex: west of your field",
		"about": "The agri dome's old stores. A pressure seal failed years ago and I closed the doors on it. The frame is sound; the glass and the seals are not.",
		"cost": 500, "needs": {"hull_plate": 4, "coil_wire": 2, "stone": 40},
		"mention": "The storage dome by your field is still sealed. My drones can repair it whenever you can spare what it needs.",
	},
	"ponds": {
		"name": "Hot springs & fish ponds",
		"where": "Agri Complex: east of your front porch",
		"about": "The springs draw warm water up from the ocean under the caverns, and the ponds were stocked from them. Something down there kept cracking the pipes, so I sealed the dome.",
		"cost": 2000, "needs": {},
		"after": "harbinger_slain",
		"wait": "Not while the Harbinger lives. Whatever cracks the pipes is down in that water, and I will not send my drones into it.",
		"mention": "The springs have been quiet since the Harbinger went down. I can repair the hot springs and the fish ponds now, if you can spare the Scrip.",
	},
}
const ORDER := ["storage", "ponds"]

const BAD := Color("a43a2a")
const ROW := 40.0
const LIST_W := 214.0
const STATE_TEXT := {"ready": "BROKEN", "locked": "BROKEN  -  NOT YET", "due": "OPENS TOMORROW", "open": "REPAIRED"}

var world                                # main.gd
var open := false
var showing := "storage"
var message := ""                        # what happened when you last pressed Pay
var screen: ShipScreen


func _ready() -> void:
	layer = 14
	screen = ShipScreen.new()
	add_child(screen)
	screen.fill = true
	screen.paint = Callable(self, "_paint")
	screen.on_click = Callable(self, "_click")
	visible = false


func open_at(id: String) -> void:
	showing = id if REPAIRS.has(id) else str(ORDER[0])
	message = ""
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


func _step(by: int) -> void:
	var at: int = clampi(ORDER.find(showing) + by, 0, ORDER.size() - 1)
	_pick(str(ORDER[at]))


func _pick(id: String) -> void:
	if id == showing:
		return
	showing = id
	message = ""
	world.sfx("click")


func _click(id: String, _p: Vector2, button: int) -> void:
	if button == MOUSE_BUTTON_RIGHT:
		close()
		return
	if button != MOUSE_BUTTON_LEFT:
		return
	if id == "close":
		close()
	elif id == "pay":
		message = world.pay_station_repair(showing)
	elif id.begins_with("pick/"):
		_pick(id.substr(5))


func _paint() -> void:
	var s := screen
	s.case_fill("Station repairs")
	var top := 34.0
	var bottom: float = s.page.y - 44.0
	# the repairs S.A.R.A. can do
	var box := Rect2(12, top, LIST_W, bottom - top)
	s.panel(box, "map", "S.A.R.A.'s repairs")
	var y: float = top + 29.0
	for id in ORDER:
		var r: Dictionary = REPAIRS[id]
		var state: String = world.repair_state(id)
		var row := Rect2(box.position.x + 6, y, box.size.x - 12, ROW - 4)
		if id == showing:
			s.frame(row, Color("f0d4b9"), Color("c3b8a5"), Color("f9e8d2"), Color("bd8b67"))
		else:
			s.frame(row, Color("f0eee7"), Color("c3b8a5"), Color("fffdf6"), Color("d5cfc1"))
		s.text_fit(row.position.x + 8, row.position.y + 4, row.size.x - 14, str(r["name"]), "label", ShipScreen.INK)
		s.text_fit(row.position.x + 8, row.position.y + 21, row.size.x - 14, str(STATE_TEXT.get(state, "")), "micro",
				ShipScreen.PIP_ON if state == "open" else (ShipScreen.OCHRE if state != "locked" else ShipScreen.MUTED))
		if s.hovering(row):
			s.outline(row, ShipScreen.ORANGE)
		s.hit("pick/" + str(id), row)
		y += ROW
	# the one you picked
	var d := Rect2(box.end.x + 10, top, s.page.x - box.end.x - 22, bottom - top)
	_paint_repair(d, showing)
	# the bottom row
	s.shift(s.bottom_left())
	s.status(message if message != "" else "Pick a repair. S.A.R.A.'s drones do the work overnight. Esc or E puts this away.")
	s.shift(s.bottom_right())
	s.solid_button("close", Rect2(625, 388, 82, 22), "Close")
	s.shift(Vector2.ZERO)


func _paint_repair(d: Rect2, id: String) -> void:
	var s := screen
	var r: Dictionary = REPAIRS[id]
	var state: String = world.repair_state(id)
	s.panel(d, "power", str(r["name"]))
	var half: float = floorf((d.size.x - 30.0) / 2.0)
	var x: float = d.position.x + 12.0
	var y: float = d.position.y + 32.0
	s.text_fit(x, y, half, str(r["where"]).to_upper(), "micro", ShipScreen.MUTED)
	y += 18.0
	y = s.wrap_text(x, y, half, "S.A.R.A.: \"%s\"" % str(r["about"]), "label", ShipScreen.INK, 16.0)
	if state == "locked":
		y += 6.0
		y = s.wrap_text(x, y, half, str(r.get("wait", "Not yet.")), "label", BAD, 16.0)
	# what it needs, against what you have
	y += 12.0
	s.rect(Rect2(x, y, half, 1), ShipScreen.RULE)
	y += 8.0
	s.text(x, y, "WHAT THE REPAIR NEEDS", "micro", ShipScreen.MUTED)
	y += 16.0
	var live: bool = state == "ready"
	var needs: Dictionary = r["needs"]
	for item in needs:
		_item_icon(str(item), Rect2(x, y - 2, 12, 12))
		var have: int = int(world._count(str(item)))
		var col: Color = (ShipScreen.INK if have >= int(needs[item]) else BAD) if live else Color("a8a69e")
		s.text_fit(x + 16, y, half - 16, "%d %s   YOU HAVE %d" % [int(needs[item]), _item_name(str(item)).to_upper(), have], "micro", col)
		y += 14.0
	var scrip_col: Color = (ShipScreen.OCHRE if int(world.credits) >= int(r["cost"]) else BAD) if live else Color("a8a69e")
	s.text_fit(x, y, half, "%d SCRIP   YOU HAVE %d" % [int(r["cost"]), int(world.credits)], "micro", scrip_col)
	# the dome through the station's cameras
	var cam := Rect2(d.position.x + 18.0 + half, d.position.y + 30.0, half, minf(196.0, d.size.y - 80.0))
	_paint_camera(cam, id, state)
	# pay
	var pay := Rect2(d.end.x - 12.0 - half, d.end.y - 36.0, half, 26.0)
	match state:
		"open":
			s.button("", pay, "Repaired", false, "label", false)
		"due":
			s.button("", pay, "Opens in the morning", false, "label", false)
		"locked":
			s.button("", pay, "Not yet", false, "label", false)
		_:
			if world.can_pay_repair(id):
				s.solid_button("pay", pay, "Pay S.A.R.A. (%d)" % int(r["cost"]))
			else:
				s.button("", pay, "Not enough yet", false, "label", false)


# The dome as the station's cameras see it: its part of the baked map, dimmed while it's broken.
func _paint_camera(r: Rect2, id: String, state: String) -> void:
	var s := screen
	s.scope(r, 1, state != "open")
	var at: Array = MapData.SEALED_ROOMS.get(id, [])
	if at.size() == 5:
		var src := Rect2(float(at[1]) * 24.0, float(at[2]) * 24.0, float(int(at[3]) - int(at[1]) + 1) * 24.0, float(int(at[4]) - int(at[2]) + 1) * 24.0)
		var area := Rect2(r.position + Vector2(8, 20), r.size - Vector2(16, 28))
		var k: float = minf(area.size.x / src.size.x, area.size.y / src.size.y)
		var dest := Rect2((area.position + (area.size - src.size * k) * 0.5).round(), (src.size * k).round())
		var tint := Color.WHITE if state == "open" else Color(0.55, 0.6, 0.66)
		for pattern in ["floor_%s", "walls_%s", "walls_%s_top"]:      # the baked floor, walls and wall tops
			var path: String = "res://art/lunar/" + (str(pattern) % str(at[0])) + ".png"
			if ResourceLoader.exists(path):
				s.texture(load(path), dest, src, tint)
	s.text(r.position.x + 8, r.position.y + 6, "CAMERA  " + str(REPAIRS[id]["name"]).to_upper(), "micro", ShipScreen.SCOPE_TEXT)
	s.text_right(r.end.x - 8, r.position.y + 6, "SEALED" if state != "open" else "OPEN", "micro",
			ShipScreen.HOSTILE_TEXT if state != "open" else ShipScreen.SCOPE_TEXT)


func _item_name(item: String) -> String:
	return str(ItemData.ITEMS[item]["name"]) if ItemData.ITEMS.has(item) else item


func _item_icon(item: String, r: Rect2) -> void:
	var tex: Texture2D = world.items_tex
	if tex == null or not ItemData.ITEMS.has(item):
		return
	var cell: int = tex.get_height()
	screen.texture(tex, r, Rect2(int(ItemData.ITEMS[item]["icon"]) * cell, 0, cell, cell))
