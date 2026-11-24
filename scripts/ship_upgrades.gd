extends CanvasLayer
# The ship screen (23 Nov 2026; mock-up upgrades_systems_x2.png / upgrades_hull_x2.png, approved by Zachary: "I like
# the pre upgrade before you set out. Should have a ship selector menu when you get multiple ships so you can
# upgrade each"). Opens from Freya's workbench in the Shuttle Bay, from the crew board there (on the Crew tab, with
# hirelings), or from the jump map as a field refit (no switching ships or hiring out there).
#   Systems      - each system's level, bought with Scrip and salvage (ShipData.SYSTEM_UPGRADES, system_cost)
#   Hull & tank  - reactor bars, hull plating, the fuel tank (opens rings 4 and 5), the tether (crewed ships)
#   Crew         - who flies with you on a crewed ship: Freya and Ana at 6 hearts, hired crew, and the board
#   Contracts    - Eshu's bounties and captures: the ones you've taken, and (at the board) new ones
# The ship buttons along the top pick which ship you're looking at; "Fly this ship" makes it the one that launches.
# Freya's 8-heart perk (Master Mechanic) takes 20% off the Scrip.
# main.gd owns the state (ship_ups, ships_owned, crew_roster...) and its helpers (_ups, _ship_def, switch_ship).

const ShipData = preload("res://scripts/ship_data.gd")
const ShipScreen = preload("res://ui/ship_screen.gd")
const ItemData = preload("res://scripts/item_data.gd")

const TABS := ["Systems", "Hull & tank", "Crew", "Contracts"]
const SYS_ORDER := ["shields", "engines", "weapons", "life", "pilot", "drones", "pods", "medbay"]
const ICON_ORDER := ["shields", "engines", "weapons", "life", "pilot", "drones", "cannon", "medbay", "crew", "doors", "sensors", "pods"]
const INK := Color("373b36")
const MUTED := Color("595e55")
const OCHRE := Color("a45736")
const ORANGE := Color("ac5c36")
const BAD := Color("a43a2a")
const GREY := Color("a8a69e")
const ROSTER_MAX := 4

var world                          # main.gd
var open := false
var where := "bench"               # "bench" (Freya's workbench), "board" (the crew board), "field" (from the map),
                                   # "restore" (the covered fighter under its tarp: Freya's restoration, stage by stage)
var tab := 0
var view_ship := "starter"
var picked := 0
var status := ""
var on_leave: Callable = Callable()
var screen: ShipScreen
var icons: Texture2D


func _ready() -> void:
	layer = 9
	visible = false
	screen = ShipScreen.new()
	add_child(screen)
	screen.fill = true
	screen.paint = Callable(self, "_paint")
	screen.on_click = Callable(self, "_click")
	if ResourceLoader.exists("res://art/ui/ship/icons_systems.png"):
		icons = load("res://art/ui/ship/icons_systems.png")


func open_at(place: String, cb: Callable = Callable()) -> void:
	where = place
	on_leave = cb
	view_ship = world.active_ship
	tab = 2 if place == "board" else 0
	picked = 0
	status = {"bench": "Freya: \"Bring me parts and Scrip and I'll fit anything.\"",
		"board": "Eshu's notice: CREW WANTED, CREW AVAILABLE. Signing fee up front.",
		"field": "Field refit: your drone fits what you've got on board.",
		"restore": "Freya: \"She's a good hull under all that dust. Bring me the parts.\""}.get(place, "")
	open = true
	visible = true
	screen.redraw()


func close() -> void:
	open = false
	visible = false


func _leave() -> void:
	var cb: Callable = on_leave
	close()
	world._save_game()
	if cb.is_valid():
		cb.call()


func _process(_delta: float) -> void:
	if open and visible:
		screen.redraw()


func handle_input(ev: InputEvent) -> void:
	if ev.is_action_pressed("cancel"):
		_leave()


func _click(id: String, _p: Vector2, button: int) -> void:
	if button != MOUSE_BUTTON_LEFT or id == "":
		return
	if world.dialogue.active:
		world.dialogue.advance()
		return
	var action: String = id.get_slice("/", 0)
	var arg: String = id.get_slice("/", 1) if id.contains("/") else ""
	match action:
		"tab":
			tab = int(arg)
			picked = 0
			world.sfx("click")
		"ship":
			view_ship = arg
			picked = 0
			world.sfx("click")
		"row":
			picked = int(arg)
			world.sfx("click", 1.3, -6.0)
		"buy":
			_buy(int(arg))
		"fly":
			world.switch_ship(view_ship)
			status = "The %s is on the launch clamps now." % str(ShipData.SHIP_NAMES[view_ship]).to_lower()
			world.sfx("quest")
		"take":
			world.crew_taking[arg] = not bool(world.crew_taking.get(arg, false))
			status = ("%s is coming along." if bool(world.crew_taking[arg]) else "%s stays on the station.") % arg
			world.sfx("click")
		"dismiss":
			var i: int = int(arg)
			if i >= 0 and i < world.crew_roster.size():
				status = "%s collects their pay and heads for the next transport." % str(world.crew_roster[i]["name"])
				world.crew_roster.remove_at(i)
				world.sfx("click")
		"hire":
			_hire(int(arg))
		"take_c":
			var offers: Array = world.contract_offers()
			var k: int = int(arg)
			if k >= 0 and k < offers.size():
				status = world.take_contract(offers[k])
		"drop_c":
			world.drop_contract(int(arg))
			status = "Contract dropped. Eshu shrugs all four shoulders."
			world.sfx("click")
		"leave":
			_leave()
		"restore":
			status = world.restore_covered()


# ---------------------------------------------------------------- rows and costs

# The rows on the current tab for the ship being viewed: {key, kind, label, level, max, next, cost, about}.
func _rows() -> Array:
	var out: Array = []
	var d: Dictionary = world._ship_def(view_ship)
	var u: Dictionary = world._ups(view_ship)
	if TABS[tab] == "Systems":
		for key in SYS_ORDER:
			if not (d["systems"] as Dictionary).has(key):
				continue
			var lv: int = int(d["systems"][key][0])
			var mx: int = int(ShipData.SYSTEM_UPGRADES[key][0])
			out.append({"key": key, "kind": "sys", "label": str(ShipData.SYSTEM_LABELS[key]), "level": lv, "max": mx,
				"next": "+1 bar: " + str(ShipData.SYSTEM_EFFECTS[key]), "cost": ShipData.system_cost(key, lv + 1) if lv < mx else [],
				"about": str(ShipData.SYSTEM_ABOUT[key])})
	elif TABS[tab] == "Hull & tank":
		var base: Dictionary = ShipData.SHIP_DEFS[view_ship]
		var radd: int = int(u["reactor"])
		out.append({"key": "reactor", "kind": "reactor", "label": "Reactor", "level": int(d["reactor"]),
			"max": int(base["reactor"]) + ShipData.REACTOR_MAX_ADD, "next": "+1 power to share between systems",
			"cost": ShipData.reactor_cost(radd) if radd < ShipData.REACTOR_MAX_ADD else [],
			"about": "The reactor's bars are the power you move between systems in a fight."})
		var hl: int = int(u["hull"])
		out.append({"key": "hull", "kind": "hull", "label": "Hull plating", "level": hl, "max": ShipData.HULL_LEVELS,
			"next": "+%d hull (now %d)" % [ShipData.HULL_STEP, int(d["hull"])], "cost": ShipData.hull_cost(hl) if hl < ShipData.HULL_LEVELS else [],
			"about": "Thicker plating: more hull before she breaks. Freya patches it back to the new top after runs."})
		var tl: int = int(u["tank"])
		out.append({"key": "tank", "kind": "tank", "label": "Fuel tank", "level": 3 + tl, "max": 5,
			"next": "Rings 1-%d open on runs, %d fuel at launch" % [mini(5, 4 + tl), 4 + tl],
			"cost": ShipData.TANK_COSTS[tl] if tl < ShipData.TANK_LEVELS else [],
			"about": "Runs open rings one to three. A bigger tank opens ring four, then ring five, where rare salvage is likeliest. Freya tops the tank up to more fuel at launch."})
		if view_ship != "starter":
			var has_t: bool = bool(u.get("tether", false))
			out.append({"key": "tether", "kind": "tether", "label": "Emergency tether", "level": 1 if has_t else 0, "max": 1,
				"next": "Pulls boarders home when they fall", "cost": [] if has_t else ShipData.TETHER_COST,
				"about": "A line to every boarder. If one goes down over there, it hauls them back to your pod room instead of losing them."})
		out.append({"key": "mounts", "kind": "mounts", "label": "Weapon mounts", "level": (base["weapons"] as Array).size(),
			"max": (base["weapons"] as Array).size(), "next": "This hull has room for %d" % (base["weapons"] as Array).size(), "cost": [],
			"about": "Guns are bought at stores and fitted into empty mounts."})
	return out


func _discount() -> float:
	return 0.8 if world._crew_hearts("Freya") >= 8 else 1.0


func _scrip(cost: Array) -> int:
	return int(round(int(cost[0]) * _discount()))


func _can_pay(cost: Array) -> bool:
	if cost.is_empty() or int(world.credits) < _scrip(cost):
		return false
	var items: Dictionary = cost[1]
	for item in items:
		if int(world._count(item)) < int(items[item]):
			return false
	return true


func _missing(cost: Array) -> String:
	if cost.is_empty():
		return ""
	var items: Dictionary = cost[1]
	for item in items:
		var short: int = int(items[item]) - int(world._count(item))
		if short > 0:
			return "Missing %d %s" % [short, _item_name(item).to_lower()]
	if int(world.credits) < _scrip(cost):
		return "Missing %d Scrip" % (_scrip(cost) - int(world.credits))
	return ""


func _item_name(item: String) -> String:
	return str(ItemData.ITEMS[item]["name"]) if ItemData.ITEMS.has(item) else item


func _buy(i: int) -> void:
	var rows: Array = _rows()
	if i < 0 or i >= rows.size():
		return
	var r: Dictionary = rows[i]
	var cost: Array = r["cost"]
	if not _can_pay(cost):
		status = _missing(cost) if not cost.is_empty() else "That's as far as it goes."
		world.sfx("deny")
		return
	world._money(-_scrip(cost), "Ship upgrades")
	var items: Dictionary = cost[1]
	for item in items:
		world._give(item, -int(items[item]))
	var u: Dictionary = world._ups(view_ship)
	var flying: bool = view_ship == world.active_ship
	match str(r["kind"]):
		"sys":
			u["systems"][r["key"]] = int(r["level"]) + 1
		"reactor":
			u["reactor"] = int(u["reactor"]) + 1
		"hull":
			u["hull"] = int(u["hull"]) + 1
			if flying:
				world.ship_hull = int(world.ship_hull) + ShipData.HULL_STEP
			elif world.ship_hulls.has(view_ship):
				world.ship_hulls[view_ship] = int(world.ship_hulls[view_ship]) + ShipData.HULL_STEP
		"tank":
			u["tank"] = int(u["tank"]) + 1
		"tether":
			u["tether"] = true
	world.sfx("tool_upgrade")
	status = "%s upgraded." % str(r["label"])


# ---------------------------------------------------------------- crew

func _seats() -> int:
	return int(ShipData.CREW_SEATS.get(view_ship, 0))


func _hire(i: int) -> void:
	var offers: Array = world.crew_board_offers()
	if i < 0 or i >= offers.size():
		return
	var o: Dictionary = offers[i]
	if world.crew_roster.size() >= ROSTER_MAX:
		status = "You can keep %d hands on the books. Let one go first." % ROSTER_MAX
		world.sfx("deny")
		return
	if int(world.credits) < int(o["fee"]):
		status = "%s wants %d Scrip up front." % [str(o["name"]), int(o["fee"])]
		world.sfx("deny")
		return
	world._money(-int(o["fee"]), "Crew signing fee")
	world.crew_roster.append({"id": str(o["id"]), "name": str(o["name"]), "kind": str(o["kind"])})
	world.board_hired.append(str(o["name"]))
	world.sfx("coin")
	status = "%s signs on. They'll be at the launch clamps when you fly the covered fighter." % str(o["name"])


# ---------------------------------------------------------------- drawing

func _paint() -> void:
	var s := screen
	s.case_fill({"bench": "Freya's bench", "board": "Crew board", "field": "Field refit", "restore": "Covered fighter"}.get(where, "Ship"))
	s.shift(((s.page - ShipScreen.DESIGN) / 2.0).floor() + Vector2(0, -16))
	if where == "restore":
		_paint_restore()
		s.shift(s.bottom_left())
		s.status(status)
		s.shift(s.bottom_right())
		s.solid_button("leave", Rect2(625, 388, 82, 22), "Leave")
		s.shift(Vector2.ZERO)
		return
	for i in range(TABS.size()):
		s.button("tab/%d" % i, Rect2(56 + i * 100, 54, 96, 24), str(TABS[i]), tab == i)
	# the ship selector (only once you have more than one)
	var owned: Array = world.ships_owned
	if owned.size() > 1:
		var x: float = 715.0
		for k in range(owned.size() - 1, -1, -1):
			var sid: String = owned[k]
			var label: String = ("Fighter" if sid == "starter" else str(ShipData.SHIP_NAMES[sid])) + (" *" if sid == world.active_ship else "")
			var w: float = s.width(label, "micro") + 18.0
			x -= w
			s.button("ship/" + sid, Rect2(x, 54, w, 24), label, sid == view_ship, "micro")
			x -= 4.0
	if TABS[tab] == "Crew":
		_paint_crew()
	elif TABS[tab] == "Contracts":
		_paint_contracts()
	else:
		_paint_rows()
	s.shift(s.bottom_left())
	s.status(status)
	s.shift(s.bottom_right())
	s.solid_button("leave", Rect2(625, 388, 82, 22), "Leave")
	s.shift(Vector2.ZERO)


func _paint_rows() -> void:
	var s := screen
	var rows: Array = _rows()
	var d: Dictionary = world._ship_def(view_ship)
	s.panel(Rect2(56, 84, 412, 298), "power", "Systems" if TABS[tab] == "Systems" else "Hull, tank and reactor")
	if TABS[tab] == "Systems":
		s.text(300, 88, "REACTOR %d" % int(d["reactor"]), "micro", MUTED)
	var row_h: float = 44.0 if rows.size() <= 6 else 34.0
	picked = clampi(picked, 0, maxi(0, rows.size() - 1))
	for i in range(rows.size()):
		var r: Dictionary = rows[i]
		var box := Rect2(60, 112 + i * row_h, 404, row_h - 4.0)
		var mine: bool = i == picked
		s.frame(box, Color("f8f6ef") if mine else Color("f0ede4"), ORANGE if mine else Color("d0c9bb"))
		if mine:
			s.outline(box, ORANGE, 2.0)
		var tx: float = box.position.x + 8.0
		if str(r["kind"]) == "sys" and icons != null:
			var ii: int = ICON_ORDER.find(str(r["key"]))
			if ii >= 0:
				s.texture(icons, Rect2(box.position + Vector2(6, 5), Vector2(16, 16)), Rect2(ii * 32, 0, 32, 32), Color("6e9a76"))
				tx += 22.0
		s.text(tx, box.position.y + 4, str(r["label"]), "strong", INK)
		# level pips: owned green, the next one marked, the rest off
		var mx: int = int(r["max"])
		var lv: int = int(r["level"])
		for p in range(mx):
			var pr := Rect2(190 + p * 9, box.position.y + 6, 7, 10)
			if p < lv:
				s.rect(pr, ShipScreen.PIP_ON)
				s.outline(pr, Color("4d5a4e"))
			elif p == lv and not (r["cost"] as Array).is_empty():
				s.rect(pr, Color("f0d4b9"))
				s.outline(pr, ORANGE)
			else:
				s.rect(pr, ShipScreen.PIP_OFF)
				s.outline(pr, Color("bdb4a5"))
		s.text_fit(box.position.x + 8, box.end.y - 14, 300, str(r["next"]).to_upper() if not (r["cost"] as Array).is_empty() else "AS GOOD AS IT GETS", "micro", MUTED)
		var cost: Array = r["cost"]
		if not cost.is_empty():
			var cx: float = 290.0
			s.text(cx, box.position.y + 6, "%d SCRIP" % _scrip(cost), "micro", OCHRE)
			cx += 58.0
			var items: Dictionary = cost[1]
			for item in items:
				_item_icon(item, Rect2(cx, box.position.y + 4, 12, 12))
				var have_enough: bool = int(world._count(item)) >= int(items[item])
				s.text(cx + 13, box.position.y + 6, "x%d" % int(items[item]), "micro", INK if have_enough else BAD)
				cx += 34.0
			s.button("buy/%d" % i, Rect2(box.end.x - 64, box.end.y - 20, 60, 16), "Upgrade", false, "micro", _can_pay(cost))
		if s.hovering(box) and not mine:
			s.outline(box, ORANGE)
		s.hit("row/%d" % i, Rect2(box.position, Vector2(box.size.x - 70, box.size.y)))
	_paint_details(rows)


func _paint_details(rows: Array) -> void:
	var s := screen
	# the ship in a scope
	var sc := Rect2(476, 84, 239, 112)
	s.scope(sc, 2)
	var d: Dictionary = world._ship_def(view_ship)
	var hull_tex: Texture2D = load(str(d["art"])) if ResourceLoader.exists(str(d["art"])) else null
	var inside: Texture2D = load(str(d["interior"])) if ResourceLoader.exists(str(d["interior"])) else null
	if hull_tex != null:
		var xf: Transform2D = s.fit_into(Vector2(hull_tex.get_size()), Rect2(sc.position + Vector2(8, 16), sc.size - Vector2(16, 24)))
		s.texture_xf(hull_tex, xf)
		if inside != null:
			s.texture_xf(inside, xf)
	var flying: bool = view_ship == world.active_ship
	var hull_now: int = int(world.ship_hull) if flying else int(world.ship_hulls.get(view_ship, int(d["hull"])))
	s.text(sc.position.x + 8, sc.position.y + 6, str(ShipData.SHIP_NAMES[view_ship]).to_upper() + ("  (FLYING)" if flying else ""), "micro", ShipScreen.SCOPE_TEXT)
	s.text_right(sc.end.x - 8, sc.position.y + 6, "HULL %d / %d" % [hull_now, int(d["hull"])], "micro", ShipScreen.SCOPE_TEXT)
	# fitted augments (they stay with whichever ship flies)
	var aug_names: Array = []
	for a in world.augments:
		aug_names.append(str(ShipData.AUGMENTS[a]["name"]))
	s.text_fit(sc.position.x + 8, sc.end.y - 14, sc.size.x - 16,
			("AUGMENTS: " + ", ".join(aug_names)).to_upper() if not aug_names.is_empty() else "NO AUGMENTS (STORES SELL THEM)", "micro", ShipScreen.SCOPE_TEXT)
	var box := Rect2(476, 202, 239, 180)
	if rows.is_empty():
		s.panel(box, "power", "Nothing here")
		return
	var r: Dictionary = rows[picked]
	var cost: Array = r["cost"]
	var heading: String = str(r["label"]) if cost.is_empty() else "%s: %d to %d" % [str(r["label"]), int(r["level"]), int(r["level"]) + 1]
	if str(r["kind"]) == "tank" and not cost.is_empty():
		heading = "Fuel tank: ring %d" % (int(r["level"]) + 1)
	s.panel(box, "power", heading)
	var y: float = s.wrap_text(486, 230, 219, str(r["about"]), "label", MUTED, 16.0)
	if not cost.is_empty():
		y = maxf(y + 4.0, 290.0) - 4.0
		s.text(486, y, "COSTS" + ("  (FREYA: 20% OFF)" if _discount() < 1.0 else ""), "micro", INK)
		y += 14.0
		var items: Dictionary = cost[1]
		for item in items:
			_item_icon(item, Rect2(486, y - 2, 12, 12))
			var have: int = int(world._count(item))
			s.text(502, y, "%d %s   YOU HAVE %d" % [int(items[item]), _item_name(item).to_upper(), have], "micro", INK if have >= int(items[item]) else BAD)
			y += 14.0
		s.text(486, y, "%d SCRIP   YOU HAVE %d" % [_scrip(cost), int(world.credits)], "micro", OCHRE)
	if not flying and where == "bench":
		s.button("fly", Rect2(486, 352, 219, 24), "Fly this ship", false)
	elif not cost.is_empty():
		if _can_pay(cost):
			s.solid_button("buy/%d" % picked, Rect2(486, 352, 219, 24), "Upgrade for %d" % _scrip(cost))
		else:
			s.button("buy/%d" % picked, Rect2(486, 352, 219, 24), _missing(cost), false, "label", false)


func _paint_crew() -> void:
	var s := screen
	var seats: int = _seats()
	s.panel(Rect2(56, 84, 412, 298), "power", "Crew")
	if seats <= 0:
		s.wrap_text(66, 116, 392, "Your fighter is a one-seater: just you and the drone. Crew fly with you on a ship with a crew deck, like the covered fighter in the bay.", "label", MUTED, 16.0)
	else:
		s.text(300, 88, "SEATS %d BESIDES YOU" % seats, "micro", MUTED)
	var y: float = 112.0 if seats > 0 else 170.0
	# Freya and Ana
	for who in ["Freya", "Ana"]:
		var hearts: int = world._crew_hearts(who)
		var box := Rect2(60, y, 404, 30)
		s.frame(box, Color("f0ede4"), Color("d0c9bb"))
		s.text(70, y + 4, who, "strong", INK if hearts >= 6 else GREY)
		var role: String = "ENGINEER: REPAIRS TWICE AS FAST" if who == "Freya" else "PILOT: MORE EVASION IN THE COCKPIT"
		if hearts >= 8:
			role = "ENGINEER: REPAIRS 2.5X AS FAST" if who == "Freya" else "PILOT: EVEN MORE EVASION"
		s.text_fit(140, y + 6, 190, role if hearts >= 6 else "JOINS YOU AT 6 HEARTS (%d NOW)" % hearts, "micro", MUTED if hearts >= 6 else GREY)
		if hearts >= 6 and where != "field":
			var going: bool = bool(world.crew_taking.get(who, false))
			s.button("take/" + who, Rect2(box.end.x - 74, y + 7, 70, 16), "Coming" if going else "Stays home", going, "micro")
		y += 34.0
	# hired hands
	s.text(66, y + 4, "HIRED HANDS (%d OF %d)" % [world.crew_roster.size(), ROSTER_MAX], "micro", INK)
	y += 18.0
	if world.crew_roster.is_empty():
		s.text(66, y + 2, "Nobody yet. Eshu pins hirelings to the crew board in the Shuttle Bay.", "label", MUTED)
	for i in range(world.crew_roster.size()):
		var c: Dictionary = world.crew_roster[i]
		var kind: Array = ShipData.HIRE_KINDS.get(str(c["kind"]), ShipData.HIRE_KINDS["human"])
		var box2 := Rect2(60, y, 404, 28)
		s.frame(box2, Color("f0ede4"), Color("d0c9bb"))
		s.text(70, y + 4, str(c["name"]), "strong", INK)
		var sk: Array = world.crew_skill(c)
		var skill_words: String = ""
		if float(sk[0]) >= 0.05 or float(sk[1]) >= 0.05:
			skill_words = "  REPAIRS +%d%%, FIGHTS +%d%%" % [int(float(sk[0]) * 100), int(float(sk[1]) * 100)]
		s.text_fit(150, y + 7, 220, "%s. %s%s" % [str(c["kind"]).capitalize(), str(kind[1]), skill_words], "micro", MUTED)
		if where != "field":
			s.button("dismiss/%d" % i, Rect2(box2.end.x - 64, y + 6, 60, 16), "Let go", false, "micro")
		y += 32.0
	# the board, or a note about it
	var right := Rect2(476, 84, 239, 298)
	if where != "board":
		s.panel(right, "map", "Hiring")
		s.wrap_text(486, 114, 219, "Hire crew at Eshu's crew board in the Shuttle Bay, by launch control. New faces every few days." if bool(world._courier_here()) \
				else "Nobody is hiring out crew on the Landing yet. That should change once the lane is open again.", "label", MUTED, 16.0)
		return
	s.panel(right, "map", "Crew available")
	var offers: Array = world.crew_board_offers()
	var oy: float = 112.0
	if offers.is_empty():
		s.wrap_text(486, oy, 219, "Everyone on the board has signed on with someone. Eshu pins up new names every few days.", "label", MUTED, 16.0)
	for i in range(offers.size()):
		var o: Dictionary = offers[i]
		var card := Rect2(482, oy, 227, 84)
		s.frame(card, Color("f8f6ef"), Color("d0c9bb"))
		s.text(490, oy + 4, str(o["name"]), "strong", INK)
		s.text_right(card.end.x - 8, oy + 7, str(o["kind"]).capitalize().to_upper(), "micro", MUTED)
		s.wrap_text(490, oy + 26, 211, str(o["trait"]), "label", MUTED, 15.0)
		s.text(490, oy + 64, "%d SCRIP" % int(o["fee"]), "micro", OCHRE)
		s.button("hire/%d" % i, Rect2(card.end.x - 64, oy + 60, 58, 18), "Hire", false, "micro", int(world.credits) >= int(o["fee"]))
		oy += 90.0


# Freya's restoration of the covered fighter: the three stages (done, next, still to come) with what each needs and
# what you have, the ship in a scope, and Hand it over for the next stage (main.gd COVERED_REPAIRS).
func _paint_restore() -> void:
	var s := screen
	var stages: Array = world.COVERED_REPAIRS
	var done: int = int(world.covered_stage)
	s.panel(Rect2(56, 54, 412, 328), "power", "Restoring the covered fighter")
	s.text(330, 58, "STAGE %d OF %d" % [mini(done + 1, stages.size()), stages.size()], "micro", MUTED)
	var row_y := 84.0
	for i in range(stages.size()):
		var st: Dictionary = stages[i]
		var box := Rect2(60, row_y, 404, 30 if i < done else 90)     # finished stages fold down to one line
		row_y += box.size.y + 6.0
		var now: bool = i == done
		s.frame(box, Color("f8f6ef") if now else Color("f0ede4"), ORANGE if now else Color("d0c9bb"))
		if now:
			s.outline(box, ORANGE, 2.0)
		var head: String = "%d. %s" % [i + 1, str(st["name"]).capitalize()]
		s.text_fit(box.position.x + 10, box.position.y + 6, 300, head, "strong", INK if i <= done else GREY)
		if i < done:
			s.text_right(box.end.x - 10, box.position.y + 8, "DONE", "micro", ShipScreen.PIP_ON)
			continue
		var y: float = box.position.y + 30
		var needs: Dictionary = st["needs"]
		for item in needs:
			_item_icon(item, Rect2(box.position.x + 12, y - 2, 12, 12))
			var have: int = int(world._count(item))
			s.text(box.position.x + 28, y, "%d %s   YOU HAVE %d" % [int(needs[item]), _item_name(item).to_upper(), have],
					"micro", (INK if have >= int(needs[item]) else BAD) if now else GREY)
			y += 14.0
		s.text(box.position.x + 12, y, "%d SCRIP   YOU HAVE %d" % [int(st["cost"]), int(world.credits)], "micro", OCHRE if now else GREY)
	# the ship
	var sc := Rect2(476, 54, 239, 150)
	s.scope(sc, 2)
	var d: Dictionary = ShipData.COVERED_FIGHTER
	var hull_tex: Texture2D = load(str(d["art"])) if ResourceLoader.exists(str(d["art"])) else null
	if hull_tex != null:
		var xf: Transform2D = s.fit_into(Vector2(hull_tex.get_size()), Rect2(sc.position + Vector2(8, 18), sc.size - Vector2(16, 26)))
		s.texture_xf(hull_tex, xf, Rect2(), Color(1, 1, 1, 0.35 + 0.65 * float(done) / float(stages.size())))
	s.text(sc.position.x + 8, sc.position.y + 6, "COVERED FIGHTER", "micro", ShipScreen.SCOPE_TEXT)
	s.text_right(sc.end.x - 8, sc.position.y + 6, "%d CREW SEATS" % int(ShipData.CREW_SEATS["covered_fighter"]), "micro", ShipScreen.SCOPE_TEXT)
	var box2 := Rect2(476, 210, 239, 172)
	if done >= stages.size():
		s.panel(box2, "power", "She's yours")
		s.wrap_text(486, 238, 219, "Choose which ship flies at Freya's workbench.", "label", MUTED, 16.0)
		return
	var st2: Dictionary = stages[done]
	s.panel(box2, "power", "Next: stage %d" % (done + 1))
	s.wrap_text(486, 238, 219, "Freya fits %s once you bring what's on the list. The rest of the ship waits under the tarp." % str(st2["name"]), "label", MUTED, 16.0)
	var can: bool = int(world.credits) >= int(st2["cost"]) and world._has_all(st2["needs"])
	if can:
		s.solid_button("restore", Rect2(486, 346, 219, 26), "Hand it over (%d)" % int(st2["cost"]))
	else:
		s.button("restore", Rect2(486, 346, 219, 26), "Not enough yet", false, "label", false)


func _paint_contracts() -> void:
	var s := screen
	s.panel(Rect2(56, 84, 412, 298), "map", "Your contracts")
	var y: float = 112.0
	if world.contracts.is_empty():
		s.wrap_text(66, y, 392, "None taken. Eshu posts bounties and capture contracts on the crew board in the Shuttle Bay. The wanted ship shows on your map on every run until it's done.", "label", MUTED, 16.0)
	for i in range(world.contracts.size()):
		var c: Dictionary = world.contracts[i]
		var box := Rect2(60, y, 404, 52)
		s.frame(box, Color("f0ede4"), Color("d0c9bb"))
		s.text(70, y + 4, str(c["target_name"]), "strong", INK)
		s.text_right(box.end.x - 8, y + 6, ("CAPTURE" if str(c["kind"]) == "capture" else "BOUNTY") + "  %d SCRIP" % int(c["reward"]), "micro", OCHRE)
		s.text_fit(70, y + 22, 300, ("Down its crew with the hull whole" if str(c["kind"]) == "capture" else "Destroy or capture it") + ": %s, ring %d" % ["the Reach" if str(c["zone"]) == "Reach" else str(c["zone"]) + " zone", int(c["ring"])], "micro", MUTED)
		if where != "field":
			s.button("drop_c/%d" % i, Rect2(box.end.x - 64, y + 32, 60, 16), "Drop", false, "micro")
		y += 58.0
	var right := Rect2(476, 84, 239, 298)
	if where != "board":
		s.panel(right, "map", "New contracts")
		s.wrap_text(486, 114, 219, "New contracts go up on Eshu's crew board in the Shuttle Bay every few days." if bool(world._courier_here()) \
				else "Nobody is posting contracts on the Landing yet.", "label", MUTED, 16.0)
		return
	s.panel(right, "map", "Posted by Eshu")
	var offers: Array = world.contract_offers()
	var oy: float = 112.0
	if offers.is_empty():
		s.wrap_text(486, oy, 219, "Nothing new. Eshu posts more every few days.", "label", MUTED, 16.0)
	for i in range(offers.size()):
		var o: Dictionary = offers[i]
		var card := Rect2(482, oy, 227, 96)
		s.frame(card, Color("f8f6ef"), Color("d0c9bb"))
		s.text_fit(490, oy + 4, 150, str(o["target_name"]), "strong", INK)
		s.text_right(card.end.x - 8, oy + 7, "CAPTURE" if str(o["kind"]) == "capture" else "BOUNTY", "micro", MUTED)
		var words: String = ("Wanted whole: down its crew without breaking the hull. Needs a ship that can board, or fire and gas."
				if str(o["kind"]) == "capture" else "Wanted: destroyed or taken.")
		s.wrap_text(490, oy + 26, 211, words, "label", MUTED, 15.0)
		s.text(490, oy + 76, "%d SCRIP   RING %d" % [int(o["reward"]), int(o["ring"])], "micro", OCHRE)
		s.button("take_c/%d" % i, Rect2(card.end.x - 64, oy + 72, 58, 18), "Take", false, "micro", world.contracts.size() < 2)
		oy += 102.0


func _item_icon(item: String, r: Rect2) -> void:
	var tex: Texture2D = world.items_tex
	if tex == null or not ItemData.ITEMS.has(item):
		return
	var cell: int = tex.get_height()
	screen.texture(tex, r, Rect2(int(ItemData.ITEMS[item]["icon"]) * cell, 0, cell, cell))
