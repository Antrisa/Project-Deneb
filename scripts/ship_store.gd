extends CanvasLayer
# The store window (21 Nov 2026), like FTL's (Zachary, 21 Nov): tabs for weapons, systems, crew, drones and
# augments; buy or sell; fuel, missiles and drone parts; hull repair one point at a time or all at once.
# Weapons go into an empty weapon slot on your ship (main.gd ship_weapons) and sell back for half.
# Systems, crew, drones and augments have nothing in them yet: the starter ship has no room for them.
#
# main.gd calls open_store(stock, cb); cb.call() when you leave. Stock is a ShipData.STORES entry.
# Laid out on the 640 x 360 screen at 1:1 (templates/ui_store_window_x2.png in the ship art pack). It draws
# over the stop's backdrop (scripts/ship_event.gd). Plain shapes until the UI kit and store pictures exist.

const ShipData = preload("res://scripts/ship_data.gd")

const W := 640.0
const H := 360.0
const WIN := Rect2(80, 40, 480, 280)
const TABS := ["Weapons", "Systems", "Crew", "Drones & parts", "Augments"]
const WHITE := Color("ececf0")
const DIM := Color("969cb0")
const GOLD := Color("fadc5a")
const LILAC := Color("c8a0ff")
const GOOD := Color("5adc6e")
const BAD := Color("e6463c")

var world                          # main.gd
var open := false
var stock: Dictionary = {}
var on_leave: Callable = Callable()
var tab := 0
var selling := false
var picked := -1                   # index into the current slot list
var status := ""
var view: Control
var font: Font
var hover := Vector2(-99, -99)
var _hits: Array = []


func _ready() -> void:
	layer = 9                      # added after the event layer, so it draws over the stop's backdrop
	visible = false
	view = Control.new()
	view.size = Vector2(W, H)
	view.mouse_filter = Control.MOUSE_FILTER_STOP
	view.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(view)
	view.draw.connect(_draw_view)
	view.gui_input.connect(_on_gui_input)
	font = view.get_theme_default_font()
	if font == null:
		font = ThemeDB.fallback_font


func open_store(new_stock: Dictionary, cb: Callable) -> void:
	stock = new_stock
	on_leave = cb
	tab = 0
	selling = false
	picked = -1
	status = "Welcome! Have a look around."
	open = true
	visible = true


func close() -> void:
	open = false
	visible = false
	on_leave = Callable()


func _leave() -> void:
	var cb: Callable = on_leave
	close()
	if cb.is_valid():
		cb.call()


func _process(_delta: float) -> void:
	if open:
		view.queue_redraw()


func handle_input(ev: InputEvent) -> void:
	if ev.is_action_pressed("cancel"):
		_leave()


func _on_gui_input(ev: InputEvent) -> void:
	var motion := ev as InputEventMouseMotion
	if motion != null:
		hover = motion.position
		return
	var click := ev as InputEventMouseButton
	if click == null or not click.pressed or click.button_index != MOUSE_BUTTON_LEFT:
		return
	view.accept_event()
	if world.dialogue.active:
		world.dialogue.advance()
		return
	for h in _hits:
		if (h[0] as Rect2).has_point(click.position):
			_act(str(h[1]), h[2])
			return


# ---------------------------------------------------------------- what's for sale

# The slots on the current tab: [[weapon id, price], ...].
func _slots() -> Array:
	var out: Array = []
	if TABS[tab] != "Weapons":
		return out
	if selling:
		for wid in world.ship_weapons:
			if str(wid) != "":
				out.append([str(wid), int(ShipData.WEAPONS[wid].get("price", 0)) / 2])
	else:
		for wid in stock.get("weapons", []):
			out.append([str(wid), int(ShipData.WEAPONS[wid].get("price", 0))])
	return out


func _empty_text() -> String:
	match TABS[tab]:
		"Systems": return "Your ship has no room for more systems."
		"Crew": return "Your ship has no crew deck. Bigger ships can take crew."
		"Drones & parts": return "No drones for sale. Drone parts are below, with fuel and missiles."
		"Augments": return "Nothing in stock today."
	return "Nothing to sell." if selling else "Sold out."


func _act(action: String, arg) -> void:
	var price: int
	match action:
		"tab":
			tab = int(arg)
			picked = -1
			world.sfx("click")
		"mode":
			selling = not selling
			picked = -1
			world.sfx("click")
		"slot":
			picked = int(arg)
			world.sfx("click", 1.3, -6.0)
		"deal":
			_deal()
		"fuel":
			price = int(stock.get("fuel", 6))
			if _pay(price, "Fuel"):
				world.fuel += 1
				status = "One fuel cell. You have %d." % int(world.fuel)
		"missiles":
			price = int(stock.get("missiles", 12))
			if _pay(price, "Store"):
				world.missiles += 1
				status = "One missile. You have %d. (Missile weapons come later.)" % int(world.missiles)
		"parts":
			price = int(stock.get("drone_parts", 10))
			if _pay(price, "Store"):
				world.drone_parts += 1
				status = "One drone part. You have %d. (Drones come later.)" % int(world.drone_parts)
		"repair1", "repairall":
			_repair(action == "repairall")
		"leave":
			_leave()


func _pay(price: int, ledger: String) -> bool:
	if int(world.credits) < price:
		status = "You need %d Scrip for that." % price
		world.sfx("deny")
		return false
	world._money(-price, ledger)
	world.sfx("coin")
	return true


func _deal() -> void:
	var slots: Array = _slots()
	if picked < 0 or picked >= slots.size():
		return
	var wid: String = slots[picked][0]
	var price: int = slots[picked][1]
	var mine: Array = world.ship_weapons
	if selling:
		var count := 0
		for w in mine:
			if str(w) != "":
				count += 1
		if count <= 1:
			status = "Keep at least one weapon."
			world.sfx("deny")
			return
		mine[mine.find(wid)] = ""
		world._money(price, "Sold at a store")
		world.sfx("coin")
		status = "Sold the %s for %d Scrip." % [str(ShipData.WEAPONS[wid]["name"]), price]
		picked = -1
	else:
		var free: int = mine.find("")
		if free < 0:
			status = "No free weapon slot. Sell one first."
			world.sfx("deny")
			return
		if not _pay(price, "Store"):
			return
		mine[free] = wid
		status = "The %s is fitted in weapon slot %d." % [str(ShipData.WEAPONS[wid]["name"]), free + 1]


func _repair(all: bool) -> void:
	var full: int = int(ShipData.STARTER["hull"])
	var missing: int = full - int(world.ship_hull)
	if missing <= 0:
		status = "Your hull is fine."
		return
	var each: int = int(stock.get("repair", 8))
	var n: int = missing if all else 1
	n = mini(n, int(world.credits) / each)
	if n <= 0:
		status = "You need %d Scrip a hull point." % each
		world.sfx("deny")
		return
	world._money(-(n * each), "Ship repairs")
	world.ship_hull = int(world.ship_hull) + n
	world.sfx("coin")
	status = "Patched %d hull. Hull %d of %d." % [n, int(world.ship_hull), full]


# ---------------------------------------------------------------- drawing

func _text(pos: Vector2, s: String, color: Color = WHITE, size: int = 11) -> void:
	view.draw_string(font, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)


func _text_c(r: Rect2, s: String, color: Color = WHITE, size: int = 11) -> void:
	var w: float = font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	_text(Vector2(r.get_center().x - w / 2.0, r.position.y + r.size.y / 2.0 + size / 2.0 - 1.0), s, color, size)


func _button(r: Rect2, label: String, action: String, arg = 0, lit: bool = false, size: int = 10) -> void:
	var fill := Color("3a3060") if lit else Color("262c46")
	if r.has_point(hover):
		fill = fill.lightened(0.15)
	view.draw_rect(r, fill)
	view.draw_rect(r, LILAC if lit else Color("5a6080"), false, 1.0)
	_text_c(r, label, WHITE, size)
	_hits.append([r, action, arg])


func _draw_view() -> void:
	_hits.clear()
	view.draw_rect(WIN, Color(0.086, 0.1, 0.17, 0.97))
	view.draw_rect(WIN, LILAC, false, 2.0)
	_text(Vector2(WIN.position.x, WIN.position.y - 4), str(stock.get("name", "Store")), LILAC, 13)
	var credits_line := "Scrip %d    Fuel %d    Missiles %d    Drone parts %d" % [int(world.credits), int(world.fuel), int(world.missiles), int(world.drone_parts)]
	var cw: float = font.get_string_size(credits_line, HORIZONTAL_ALIGNMENT_LEFT, -1, 11).x
	_text(Vector2(WIN.end.x - cw, WIN.position.y - 4), credits_line, WHITE, 11)
	for i in range(TABS.size()):
		_button(Rect2(88 + i * 74, 48, 70, 18), str(TABS[i]), "tab", i, tab == i)
	_button(Rect2(460, 48, 92, 18), "Selling" if selling else "Buying", "mode", 0, selling)
	# slots
	var slots: Array = _slots()
	if slots.is_empty():
		view.draw_multiline_string(font, Vector2(92, 96), _empty_text(), HORIZONTAL_ALIGNMENT_LEFT, 270, 11, 4, DIM)
	for k in range(mini(8, slots.size())):
		var r := Rect2(88 + (k % 4) * 70, 72 + floori(k / 4.0) * 90, 66, 86)
		var fill := Color("2a2448") if k == picked else Color("1c2036")
		if r.has_point(hover):
			fill = fill.lightened(0.1)
		view.draw_rect(r, fill)
		view.draw_rect(r, GOLD if k == picked else Color("5a6080"), false, 1.0)
		var wid: String = slots[k][0]
		var pic_path := "res://art/ships/store/%s.png" % wid
		var pic := Rect2(r.position + Vector2(9, 6), Vector2(48, 48))
		if ResourceLoader.exists(pic_path):
			view.draw_texture_rect(load(pic_path), pic, false)
		else:
			var col: Color = ShipData.WEAPONS[wid]["color"]
			view.draw_rect(Rect2(pic.position + Vector2(6, 18), Vector2(30, 12)), Color("8a8e9c"))
			view.draw_rect(Rect2(pic.position + Vector2(36, 21), Vector2(10, 6)), col)
		_text(r.position + Vector2(4, 66), str(ShipData.WEAPONS[wid]["name"]), WHITE, 9)
		_text(r.position + Vector2(4, 79), "%s%d Scrip" % ["+" if selling else "", int(slots[k][1])], GOLD, 9)
		_hits.append([r, "slot", k])
	# details
	var d := Rect2(372, 72, 180, 176)
	view.draw_rect(d, Color("141828"))
	view.draw_rect(d, Color("5a6080"), false, 1.0)
	if picked >= 0 and picked < slots.size():
		var wid2: String = slots[picked][0]
		var w: Dictionary = ShipData.WEAPONS[wid2]
		_text(d.position + Vector2(6, 16), str(w["name"]), GOLD, 13)
		var lines := [
			"%s, needs %d power" % [str(w.get("type", "")).capitalize(), int(w["power"])],
			"%d shot%s of %d damage" % [int(w["shots"]), "s" if int(w["shots"]) > 1 else "", int(w["damage"])],
			"Charges in %.0f seconds" % float(w["charge"]),
		]
		for i in range(lines.size()):
			_text(d.position + Vector2(6, 34 + i * 14), str(lines[i]), WHITE, 10)
		view.draw_multiline_string(font, d.position + Vector2(6, 84), str(w.get("about", "")), HORIZONTAL_ALIGNMENT_LEFT, 168, 10, 5, DIM)
		_button(Rect2(380, 222, 164, 20), ("Sell for %d" if selling else "Buy for %d") % int(slots[picked][1]), "deal", 0, true, 11)
	else:
		view.draw_multiline_string(font, d.position + Vector2(6, 18), "Pick something to see it here.", HORIZONTAL_ALIGNMENT_LEFT, 168, 10, 3, DIM)
	# resources
	var res := Rect2(88, 256, 274, 56)
	view.draw_rect(res, Color("141828"))
	view.draw_rect(res, Color("5a6080"), false, 1.0)
	var rows := [["Fuel cell", "fuel", int(stock.get("fuel", 6))], ["Missile", "missiles", int(stock.get("missiles", 12))],
		["Drone part", "parts", int(stock.get("drone_parts", 10))]]
	for i in range(rows.size()):
		var y: float = res.position.y + 4 + i * 17
		_text(Vector2(res.position.x + 6, y + 11), str(rows[i][0]), WHITE, 10)
		_button(Rect2(res.end.x - 90, y, 84, 14), "Buy 1: %d" % int(rows[i][2]), str(rows[i][1]), 0, false, 9)
	# hull repair
	var rep := Rect2(372, 256, 180, 56)
	view.draw_rect(rep, Color("141828"))
	view.draw_rect(rep, Color("5a6080"), false, 1.0)
	var full: int = int(ShipData.STARTER["hull"])
	var each: int = int(stock.get("repair", 8))
	_text(rep.position + Vector2(6, 15), "Hull %d of %d" % [int(world.ship_hull), full], GOOD if int(world.ship_hull) >= full else BAD, 11)
	_button(Rect2(380, 282, 78, 18), "Repair 1: %d" % each, "repair1", 0, false, 9)
	_button(Rect2(466, 282, 80, 18), "Repair all: %d" % (each * maxi(0, full - int(world.ship_hull))), "repairall", 0, false, 9)
	# status and leave
	_text(Vector2(88, 336), status, DIM, 11)
	_button(Rect2(500, 324, 60, 18), "Leave", "leave", 0, false, 11)
