extends CanvasLayer
# The store window (21 Nov 2026), like FTL's (Zachary, 21 Nov): tabs for weapons, systems, crew, drones and
# augments; buy or sell; fuel, missiles and drone parts; hull repair one point at a time or all at once.
# Weapons go into an empty weapon slot on your ship (main.gd ship_weapons) and sell back for half.
# Systems, crew, drones and augments have nothing in them yet: the starter ship has no room for them.
#
# main.gd calls open_store(stock, cb); cb.call() when you leave. Stock is a ShipData.STORES entry.
# Drawn on the Terran field datapad (ui/ship_screen.gd); mock-up: datapad_store_x2.png in the Drive folder.
# Store pictures, when drawn, go in art/ships/store/<weapon id>.png (48 x 48).
# Trade goods (23 Nov): each store sells some salvage and resources and buys what's in your bag, at its own prices
# (ShipData.STORES "goods", "buys", TRADE_VALUE). Shown as a list instead of cards.

const ShipData = preload("res://scripts/ship_data.gd")
const ShipScreen = preload("res://ui/ship_screen.gd")

const TABS := ["Weapons", "Trade goods", "Systems", "Crew", "Drones & parts", "Augments"]
const ItemData = preload("res://scripts/item_data.gd")
const SLOTS_SHOWN := 4
const INK := Color("373b36")          # as ui/ship_screen.gd
const MUTED := Color("595e55")          # as ui/ship_screen.gd
const OCHRE := Color("a45736")          # as ui/ship_screen.gd
const ORANGE := Color("ac5c36")          # as ui/ship_screen.gd

var world                          # main.gd
var open := false
var stock: Dictionary = {}
var on_leave: Callable = Callable()
var tab := 0
var selling := false
var picked := -1                   # index into the current slot list
var status := ""
var screen: ShipScreen


func _ready() -> void:
	layer = 9                      # added after the event layer, so it draws over the stop's scene
	visible = false
	screen = ShipScreen.new()
	add_child(screen)
	screen.fill = true                  # the whole window, like the battle (Zachary, 22 Nov)
	screen.paint = Callable(self, "_paint")
	screen.on_click = Callable(self, "_click")


func open_store(new_stock: Dictionary, cb: Callable) -> void:
	stock = new_stock
	on_leave = cb
	tab = 0
	selling = false
	picked = -1
	status = "Welcome! Have a look around."
	open = true
	visible = true
	screen.redraw()


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
	if open and visible:
		screen.redraw()


func handle_input(ev: InputEvent) -> void:
	if ev.is_action_pressed("cancel"):
		_leave()


func _click(id: String, _p: Vector2, button: int) -> void:
	if button != MOUSE_BUTTON_LEFT:
		return
	if world.dialogue.active:
		world.dialogue.advance()
		return
	if id == "":
		return
	var action: String = id.get_slice("/", 0)
	var arg: int = int(id.get_slice("/", 1)) if id.contains("/") else 0
	_act(action, arg)


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
			out.append([str(wid), int(round(int(ShipData.WEAPONS[wid].get("price", 0)) * float(stock.get("markup", 1.0))))])
	return out


# Trade goods on show: [[item id, price, how many you have]]. Buying: what the store sells. Selling: what it buys
# that you have.
func _goods() -> Array:
	var out: Array = []
	if selling:
		var buys: Dictionary = stock.get("buys", {})
		for item in ShipData.TRADE_VALUE:
			var have: int = int(world._count(item))
			if have <= 0:
				continue
			var mult: float = float(buys.get(item, buys.get("*", 0.0)))
			if mult > 0.0:
				out.append([item, maxi(1, int(round(int(ShipData.TRADE_VALUE[item]) * mult))), have])
	else:
		for item in stock.get("goods", []):
			out.append([str(item), int(round(int(ShipData.TRADE_VALUE[item]) * float(stock.get("sells_at", 2.0)))), int(world._count(item))])
	return out


func _empty_text() -> String:
	match TABS[tab]:
		"Trade goods": return "Nothing they want in your bag." if selling else "No goods today."
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
				status = "One missile. You have %d. Missile launchers use one a shot." % int(world.missiles)
		"parts":
			price = int(stock.get("drone_parts", 10))
			if _pay(price, "Store"):
				world.drone_parts += 1
				status = "One drone part. You have %d. (Drones come later.)" % int(world.drone_parts)
		"good", "goodall":
			_trade(int(arg), action == "goodall")
		"repair1", "repairall":
			_repair(action == "repairall")
		"leave":
			_leave()


func _trade(i: int, all: bool) -> void:
	var goods: Array = _goods()
	if i < 0 or i >= goods.size():
		return
	var item: String = goods[i][0]
	var price: int = goods[i][1]
	var item_name: String = str(ItemData.ITEMS[item]["name"]) if ItemData.ITEMS.has(item) else item
	if selling:
		var n: int = int(goods[i][2]) if all else 1
		world._give(item, -n)
		world._money(price * n, "Sold at a store")
		world.sfx("coin")
		status = "Sold %d %s for %d Scrip." % [n, item_name.to_lower(), price * n]
	elif _pay(price, "Store"):
		world._give(item, 1)
		status = "Bought 1 %s. You have %d." % [item_name.to_lower(), int(world._count(item))]


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

func _paint() -> void:
	var s := screen
	s.case_fill(str(stock.get("name", "Store")))
	s.shift(((s.page - ShipScreen.DESIGN) / 2.0).floor() + Vector2(0, -16))
	for i in range(TABS.size()):
		s.button("tab/%d" % i, Rect2(56 + i * 90, 54, 88, 24), str(TABS[i]), tab == i, "micro")
	s.button("mode", Rect2(600, 54, 112, 24), "Selling" if selling else "Buying", selling)
	var slots: Array = _slots()
	if TABS[tab] == "Trade goods":
		_paint_goods()
	for k in range(SLOTS_SHOWN if TABS[tab] != "Trade goods" else 0):
		var r := Rect2(56 + k * 104, 84, 98, 112)
		if k >= slots.size():
			s.frame(r, Color("ece9e0"), Color("d0c9bb"), Color("f4f2ec"), Color("dcd7cc"))
			continue
		_paint_slot(k, slots[k], r)
	if slots.is_empty() and (TABS[tab] != "Trade goods" or _goods().is_empty()):
		var y: float = 128.0
		for ln in s.wrap_lines(_empty_text(), 380, "label"):
			s.text_center(262, y, ln, "label", MUTED)
			y += 16.0
	_paint_details(slots)
	_paint_supplies()
	_paint_repair()
	s.shift(s.bottom_left())
	s.status(status)
	s.shift(s.bottom_right())
	s.solid_button("leave", Rect2(625, 388, 82, 22), "Leave")
	s.shift(Vector2.ZERO)


func _paint_slot(k: int, slot: Array, r: Rect2) -> void:
	var s := screen
	var wid: String = slot[0]
	var mine: bool = k == picked
	s.frame(r, Color("f8f6ef") if mine else Color("f0ede4"), ORANGE if mine else Color("bdb4a5"))
	if mine:
		s.outline(r, ORANGE, 2.0)
	var pic := Rect2(r.position + Vector2(25, 10), Vector2(48, 48))
	var pic_path := "res://art/ships/store/%s.png" % wid
	if ResourceLoader.exists(pic_path):
		s.texture(load(pic_path), pic)
	else:
		s.rect(Rect2(pic.position + Vector2(2, 18), Vector2(32, 12)), Color("8a8e9c"))
		s.outline(Rect2(pic.position + Vector2(2, 18), Vector2(32, 12)), Color("3a3e48"))
		s.rect(Rect2(pic.position + Vector2(34, 21), Vector2(12, 6)), ShipData.WEAPONS[wid]["color"])
	s.text_fit(r.position.x + 6, r.position.y + 74, r.size.x - 12, str(ShipData.WEAPONS[wid]["name"]), "label", INK)
	s.text(r.position.x + 6, r.position.y + 90, "%s%d SCRIP" % ["+" if selling else "", int(slot[1])], "micro", OCHRE)
	var cost: int = int(ShipData.WEAPONS[wid]["power"])
	var px0: float = r.end.x - 6 - cost * 7.0 + 2
	s.img("i_bolt", Rect2(px0 - 12, r.position.y + 94, 9, 9), OCHRE)
	s.pips(px0, r.position.y + 94, cost, cost, 5.0, 9.0, 2.0)
	if s.hovering(r) and not mine:
		s.outline(r, ORANGE)
	s.hit("slot/%d" % k, r)


# The trade goods, two columns of six rows: icon, name, price, and Buy (or Sell 1 and Sell all).
func _paint_goods() -> void:
	var s := screen
	var goods: Array = _goods()
	var tex: Texture2D = world.items_tex
	for i in range(mini(12, goods.size())):
		var g: Array = goods[i]
		var r := Rect2(56 + (i / 6) * 208, 84 + (i % 6) * 19, 204, 17)
		s.frame(r, Color("f0ede4"), Color("d0c9bb"))
		if tex != null and ItemData.ITEMS.has(g[0]):
			var cell: int = tex.get_height()
			s.texture(tex, Rect2(r.position + Vector2(2, 1), Vector2(15, 15)), Rect2(int(ItemData.ITEMS[g[0]]["icon"]) * cell, 0, cell, cell))
		var item_name: String = str(ItemData.ITEMS[g[0]]["name"]) if ItemData.ITEMS.has(g[0]) else str(g[0])
		s.text_fit(r.position.x + 20, r.position.y + 4, 74, "%s (%d)" % [item_name, int(g[2])], "micro", INK)
		s.text(r.position.x + 98, r.position.y + 4, "%s%d" % ["+" if selling else "", int(g[1])], "micro", OCHRE)
		if selling:
			s.button("good/%d" % i, Rect2(r.end.x - 74, r.position.y + 1, 34, 15), "Sell", false, "micro")
			s.button("goodall/%d" % i, Rect2(r.end.x - 38, r.position.y + 1, 36, 15), "All", false, "micro")
		else:
			s.button("good/%d" % i, Rect2(r.end.x - 44, r.position.y + 1, 42, 15), "Buy", false, "micro", int(world.credits) >= int(g[1]))


func _paint_details(slots: Array) -> void:
	var s := screen
	var r := Rect2(476, 84, 239, 200)
	if TABS[tab] == "Trade goods":
		s.panel(r, "blaster", "Trade goods")
		var hint: String = "Sell salvage from your bag. This store pays %s." % _pay_words() if selling \
				else "Goods for the station: parts for ship repairs and machines. Switch to Selling to sell your salvage here."
		s.wrap_text(486, 114, 219, hint, "label", MUTED)
		return
	if picked < 0 or picked >= slots.size():
		s.panel(r, "blaster", "Details")
		s.wrap_text(486, 114, 219, "Pick something to see it here.", "label", MUTED)
		return
	var wid: String = slots[picked][0]
	var w: Dictionary = ShipData.WEAPONS[wid]
	s.panel(r, "blaster", str(w["name"]))
	var lines := [
		"%s, NEEDS %d POWER" % [str(w.get("type", "weapon")).to_upper(), int(w["power"])],
		"%d SHOT%s OF %d DAMAGE" % [int(w["shots"]), "S" if int(w["shots"]) > 1 else "", int(w["damage"])],
		"CHARGES IN %.0f SECONDS" % float(w["charge"]),
	]
	for i in range(lines.size()):
		s.text(486, 112 + i * 14, str(lines[i]), "micro", INK)
	var about: Array = s.wrap_lines(str(w.get("about", "")), 219, "label")
	for i in range(mini(4, about.size())):
		s.text(486, 160 + i * 16, about[i], "label", MUTED)
	s.solid_button("deal", Rect2(486, 250, 219, 24), ("Sell for %d" if selling else "Buy for %d") % int(slots[picked][1]))


func _pay_words() -> String:
	var all: float = float((stock.get("buys", {}) as Dictionary).get("*", 1.0))
	if all >= 1.4:
		return "well over what Bram does, and asks no questions"
	if all > 1.05:
		return "more than Bram does"
	if all < 0.95:
		return "a little less than Bram"
	return "about what Bram does, more for some things" if (stock.get("buys", {}) as Dictionary).size() > 1 else "about what Bram does"


func _paint_supplies() -> void:
	var s := screen
	s.panel(Rect2(56, 202, 412, 82), "bolt", "Supplies")
	var rows := [["Fuel cell", "fuel", int(stock.get("fuel", 6)), int(world.fuel)],
		["Missile", "missiles", int(stock.get("missiles", 12)), int(world.missiles)],
		["Drone part", "parts", int(stock.get("drone_parts", 10)), int(world.drone_parts)]]
	for i in range(rows.size()):
		var y: float = 228.0 + i * 18.0
		s.text(66, y, str(rows[i][0]), "label", INK)
		s.text(170, y + 2, "YOU HAVE %d" % int(rows[i][3]), "micro", MUTED)
		s.button(str(rows[i][1]), Rect2(360, y - 1, 100, 17), "Buy 1: %d" % int(rows[i][2]), false, "micro")


func _paint_repair() -> void:
	var s := screen
	s.panel(Rect2(56, 290, 659, 92), "power", "Hull repair")
	var full: int = int(ShipData.STARTER["hull"])
	var hull: int = int(world.ship_hull)
	var each: int = int(stock.get("repair", 8))
	s.text(66, 320, "HULL %d / %d" % [hull, full], "micro", INK if hull >= full else Color("a43a2a"))
	s.pips(150, 319, full, hull, 5.0, 9.0, 2.0, ShipScreen.PIP_RED if hull * 3 <= full else ShipScreen.PIP_ON)
	var missing: int = maxi(0, full - hull)
	s.button("repair1", Rect2(66, 340, 150, 24), "Repair 1: %d" % each, false, "label", missing > 0)
	s.button("repairall", Rect2(224, 340, 150, 24), "Repair all: %d" % (each * missing), false, "label", missing > 0)
	s.text(400, 320, "SCRIP %d   FUEL %d   MISSILES %d   PARTS %d" % [int(world.credits), int(world.fuel), int(world.missiles), int(world.drone_parts)], "micro", INK)
