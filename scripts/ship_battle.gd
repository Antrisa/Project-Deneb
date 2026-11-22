extends CanvasLayer
# The FTL-style space battle (21 Nov 2026). Real time; Space pauses. Power goes from the reactor to shields,
# engines, weapons and life support. Pick a weapon, then an enemy room, and it fires when charged. Your starter
# ship's bays are sealed: the repair drone is your one crew member. Click it, then click a bay, and it crawls there
# through the ducts. It repairs the bay it is in, and in a working bay it boosts that system (ShipData.DRONE_BOOST).
# It never moves on its own: this is the lesson for ordering crew about on bigger ships.
#
# The screen (Zachary, 21 Nov): the Terran field datapad (ui/ship_screen.gd), with each ship in a window of its
# own, yours on the left and theirs on the right, so a ship of any size is fitted to its window: at a whole number
# of screen pixels per art pixel where it fits, shrunk only when it doesn't. Shots leave one window and come in
# from the edge of the other, as in FTL. Mock-up: battle_two_windows_x2.png in the Drive folder.
#
# main.gd owns the story around a fight: it calls start() with a fight, shows any dialogue (which pauses the
# battle), and gets on_end.call(result, hull_left) with result "won", "lost" or "fled". Ships, weapons and
# numbers are in scripts/ship_data.gd. Until the new ship art exists, enemy ships are drawn as simple shapes.

const ShipData = preload("res://scripts/ship_data.gd")
const ShipScreen = preload("res://ui/ship_screen.gd")

# Page layout (768 x 432 page; see ui/ship_screen.gd).
const MY_WIN := Rect2(53, 75, 388, 218)      # your ship's window
const FOE_WIN := Rect2(447, 75, 268, 218)    # theirs
const FOE_HEAD := 44.0                       # the top of their window: name, hull, shields
const SHIELD_ROOM := 12.0                    # space kept round a ship for its shield bubble
const MOST_SCALE := 2.0                      # small ships are enlarged to fit, but no more than this
const REACTOR_SYS := ["shields", "engines", "weapons", "life"]
const SYS_LABEL := {"shields": "SHD", "engines": "ENG", "weapons": "WPN", "life": "O2"}
const SYS_NAME := {"shields": "Shields", "engines": "Engines", "weapons": "Weapons", "life": "Oxygen"}
const REPAIR_ORDER := ["shields", "weapons", "pilot", "engines", "life", "drones"]
const INK := Color("373b36")          # as ui/ship_screen.gd
const MUTED := Color("595e55")          # as ui/ship_screen.gd
const OCHRE := Color("a45736")          # as ui/ship_screen.gd
const ORANGE := Color("ac5c36")          # as ui/ship_screen.gd
const DIM := Color("969cb0")
const GOLD := Color("fadc5a")
const GOOD := Color("5adc6e")
const BAD := Color("e6463c")
const SHIELD_BLUE := Color("5ab4ff")
const YOU := Color("ffc878")
const DRONE := Color("f2c94c")
const DOOR := Color("fb7412")

var world                        # main.gd
var open := false
var paused := false
var on_end: Callable = Callable()
var fight: Dictionary = {}
var result := ""                 # "" while fighting, then "won", "lost" or "fled"
var result_text := ""
var end_timer := 0.0

var screen: ShipScreen
var me_ship: Dictionary = {}         # your ship, built for battle (ShipData.build): rooms, doors
var ship_tex: Texture2D
var interior_tex: Texture2D          # your ship's cut-away
var enemy_tex: Texture2D
var enemy_inside: Texture2D      # their cut-away, when the art has one
var my_xf := Transform2D.IDENTITY    # your ship picture -> page
var foe_xf := Transform2D.IDENTITY   # theirs

# your ship
var hull := 0
var hull_max := 0
var reactor := 0
var sys := {}                    # name -> {"max", "power", "damage"}
var layers := 0
var shield_timer := 0.0
var uplink := false              # S.A.R.A.'s link near the Landing: one extra shield layer
var oxygen := 100.0
var weapons: Array = []          # [{"id", "charge", "target", "on"}]
var selected := -1               # weapon picked and waiting for a target
var autofire := false
var fold := 0.0                  # fold drive charge, 0..100
var drone_pos := Vector2.ZERO    # in ship-picture pixels
var drone_path: Array = []       # points still to walk
var drone_room := "drones"
var drone_goal := ""
var drone_work := 0.0
var drone_selected := false      # clicked, waiting for a bay to go to
var drone_last := "drones"       # the room the drone is in, or last walked into

# the enemy
var foe: Dictionary = {}
var foe_id := ""
var e_hull := 0
var e_hull_max := 0
var e_sys := {}
var e_layers := 0
var e_shield_timer := 0.0
var e_weapons: Array = []
var e_crew := 0                  # how many of their crew are still standing
# Their crew (Zachary, 21 Nov): each starts at a station (pilot, weapons, shields, engines; any extra in a spare
# room) and walks off to repair a damaged room, then goes back. Manning a station helps that system a little;
# with nobody in the cockpit they can't dodge. A hit on a room hurts whoever is in it.
# Each: {"home", "room" (where they are; "" while walking), "target", "pos" (ship picture), "hp", "task"}.
var e_crew_list: Array = []
var e_room_repair := {}          # room id -> seconds of repair work done on it
const CREW_SPEED := 22.0         # picture pixels a second
const CREW_HP := 100.0
const CREW_HIT := 15.0           # health lost per point of damage when a shot hits their room
const STATIONS := ["pilot", "weapons", "shields", "engines"]
const CREW_SPOTS := [Vector2(0, 0), Vector2(-7, -5), Vector2(7, 5), Vector2(-7, 5), Vector2(7, -5), Vector2(0, 6)]
var overcharged := false

var shots: Array = []            # shots in flight, in ship-picture pixels: {"from", "to", "t", "at_player", ...}
var pops: Array = []             # floating words, in page pixels: {"pos", "text", "t", "color"}
var shake := 0.0
var tutorial_said := {}


func _ready() -> void:
	layer = 9                    # under the dialogue box (10), so story lines show over the battle
	visible = false
	screen = ShipScreen.new()
	add_child(screen)
	screen.paint = Callable(self, "_paint")
	screen.on_click = Callable(self, "_click")
	if ResourceLoader.exists(ShipData.STARTER["art"]):
		ship_tex = load(ShipData.STARTER["art"])
	var inside: String = str(ShipData.STARTER.get("interior", ""))
	if inside != "" and ResourceLoader.exists(inside):
		interior_tex = load(inside)
	me_ship = ShipData.build(ShipData.STARTER)


# ---------------------------------------------------------------- starting and ending

# fight: {"enemy": id, "story": bool, "uplink": bool, "tutorial": bool}. hull_now: your hull coming in.
func start(new_fight: Dictionary, cb: Callable, hull_now: int) -> void:
	fight = new_fight
	on_end = cb
	result = ""
	result_text = ""
	paused = false
	shots.clear()
	pops.clear()
	selected = -1
	fold = 0.0
	oxygen = 100.0
	tutorial_said = {}
	me_ship = ShipData.build(ShipData.STARTER)
	var me: Dictionary = me_ship
	hull_max = int(me["hull"])
	hull = clampi(hull_now, 1, hull_max)
	reactor = int(me["reactor"])
	uplink = bool(fight.get("uplink", false))
	sys = _make_systems(me["systems"])
	layers = _max_layers()
	weapons.clear()
	var fitted: Array = world.ship_weapons if world.ship_weapons.size() == me["weapons"].size() else me["weapons"]
	for wid in fitted:
		weapons.append({"id": str(wid), "charge": 0.0, "target": "", "on": str(wid) != ""})
	drone_room = "drones"
	drone_last = "drones"
	drone_pos = me["hub"]
	drone_path = []
	drone_goal = ""
	drone_work = 0.0
	drone_selected = false

	foe_id = str(fight["enemy"])
	foe = ShipData.enemy(foe_id)
	e_hull_max = int(foe["hull"])
	e_hull = e_hull_max
	e_sys = _make_systems(foe["systems"])
	e_layers = _layers_of(e_sys)
	e_weapons.clear()
	for wid in foe["weapons"]:
		# Enemies start part-charged so the first shots don't all land together.
		e_weapons.append({"id": str(wid), "charge": randf_range(1.0, 4.0), "target": "", "on": true})
	_make_enemy_crew()
	overcharged = false
	enemy_tex = _load_tex(str(foe.get("art", "")))
	enemy_inside = _load_tex(str(foe.get("interior", "")))
	_fit_ships()
	open = true
	visible = true
	screen.redraw()


func close() -> void:
	open = false
	visible = false
	on_end = Callable()


# Each ship fitted to its own window (the enemy's below the band with its name and hull).
# Ships drawn at double resolution ("art_scale" 2) are fitted on their art pixels, so each art pixel is a whole
# number of screen pixels; rooms, crew and doors stay in 24-px cell units through the same transform. Enemies with
# art are mirrored to face you (art faces right), so the transform's x scale is negative for them.
func _fit_ships() -> void:
	my_xf = _fit(me_ship, _my_area(), false)
	if not foe.is_empty():
		foe_xf = _fit(foe, _foe_area(), foe.has("art"))


func _fit(ship: Dictionary, area: Rect2, mirror: bool) -> Transform2D:
	var a: float = float(ship.get("art_scale", 1))
	var size: Vector2 = ship["size"]
	var xf: Transform2D = screen.fit_into(size * a, area, SHIELD_ROOM, MOST_SCALE / a)
	var k: float = xf.get_scale().y * a
	if mirror:
		return Transform2D(Vector2(-k, 0), Vector2(0, k), xf.origin + Vector2(size.x * k, 0))
	return Transform2D(Vector2(k, 0), Vector2(0, k), xf.origin)


func _load_tex(path: String) -> Texture2D:
	if path != "" and ResourceLoader.exists(path):
		return load(path)
	return null


# Where a ship's picture goes on the page; its width is negative when the ship is mirrored, which flips it.
func _ship_rect(xf: Transform2D, size: Vector2) -> Rect2:
	return Rect2(xf.origin, Vector2(size.x * xf.x.x, size.y * xf.y.y))


func _my_area() -> Rect2:
	return MY_WIN


func _foe_area() -> Rect2:
	return Rect2(FOE_WIN.position + Vector2(0, FOE_HEAD), FOE_WIN.size - Vector2(0, FOE_HEAD))


# A point on a ship picture, on the page.
func _on_page(at_player: bool, p: Vector2) -> Vector2:
	return (my_xf if at_player else foe_xf) * p


func _ship_scale(at_player: bool) -> float:
	return absf((my_xf if at_player else foe_xf).y.y)

func _make_systems(table: Dictionary) -> Dictionary:
	var out := {}
	for key in table:
		var pair: Array = table[key]
		out[key] = {"max": int(pair[0]), "power": int(pair[1]), "damage": 0}
	return out


func _finish() -> void:
	var cb: Callable = on_end
	var what: String = result
	result = "done"
	if cb.is_valid():
		cb.call(what, maxi(0, hull))


func _win() -> void:
	if result != "": return
	result = "won"
	result_text = "%s destroyed" % str(foe["name"])
	end_timer = 2.2
	shake = 0.6
	world.sfx("die", 0.6)


func _lose(why: String) -> void:
	if result != "": return
	result = "lost"
	result_text = why
	end_timer = 2.0
	world.sfx("die")


func _jump() -> void:
	if result != "" or fold < 100.0 or bool(fight.get("story", false)): return
	result = "fled"
	result_text = "Fold jump: heading home"
	end_timer = 1.0
	world.sfx("warp")


# ---------------------------------------------------------------- the clock

func _process(delta: float) -> void:
	if not open:
		return
	screen.redraw()
	shake = maxf(0.0, shake - delta)
	for p in pops:
		p["t"] = float(p["t"]) + delta
	pops = pops.filter(func(p): return float(p["t"]) < 1.2)
	if world.dialogue.active:
		return
	if result == "done":
		return
	if result != "":
		end_timer -= delta
		_move_shots(delta, false)
		if end_timer <= 0.0:
			_finish()
		return
	if paused:
		return
	_tick(delta)


func _tick(delta: float) -> void:
	# shields come back one layer at a time
	var top := _max_layers()
	if layers > top: layers = top
	if layers < top:
		shield_timer += delta
		if shield_timer >= ShipData.SHIELD_RECHARGE * (0.75 if _boosting("shields") else 1.0):
			shield_timer = 0.0
			layers += 1
	else:
		shield_timer = 0.0
	var e_top := _layers_of(e_sys)
	if e_layers > e_top: e_layers = e_top
	if e_layers < e_top:
		e_shield_timer += delta
		if e_shield_timer >= ShipData.SHIELD_RECHARGE * (0.9 if _manned("shields") else 1.0):
			e_shield_timer = 0.0
			e_layers += 1
	else:
		e_shield_timer = 0.0

	_charge_weapons(weapons, sys, delta, true)
	_charge_weapons(e_weapons, e_sys, delta, false)
	_move_shots(delta, true)
	_move_drone(delta)
	_enemy_crew(delta)
	_tick_doors(me_ship, delta)
	_tick_doors(foe, delta)

	# oxygen: only you are aboard, and without life support the air runs thin
	if _eff(sys, "life") <= 0:
		oxygen -= 1.5 * delta
		if oxygen <= 0.0:
			oxygen = 0.0
			_lose("You black out as the air runs out")
	else:
		oxygen = minf(100.0, oxygen + 3.0 * delta)

	if not bool(fight.get("story", false)) and _eff(sys, "pilot") > 0:
		fold = minf(100.0, fold + delta * 0.6 * (1 + _eff(sys, "engines")))

	# Ivan's second phase
	if foe.has("overcharge_at") and not overcharged and e_hull <= int(ceil(e_hull_max * float(foe["overcharge_at"]))):
		overcharged = true
		e_weapons.append({"id": "ivan_cannon", "charge": 0.0, "target": "", "on": true})
		world._say("Ivan", [
			"[angry] Enough. Every coil to the cannon!",
		])
		world._say_then(Callable(self, "_after_overcharge"))
	# A story break (Ana's fight): the battle stops at this much hull and main.gd carries the story on.
	if foe.has("break_at") and e_hull <= int(ceil(e_hull_max * float(foe["break_at"]))):
		result = "break"
		result_text = "Their guns go quiet..."
		end_timer = 1.0
		return
	_tutorial_hints()


func _after_overcharge() -> void:
	_pop(_on_page(false, Vector2((foe["size"] as Vector2).x / 2.0, 0)), "Hit his weapons to drain the cannon", GOLD)


func _charge_weapons(list: Array, systems: Dictionary, delta: float, mine: bool) -> void:
	var budget: int = _eff(systems, "weapons")
	for w in list:
		if str(w["id"]) == "":
			continue
		var data: Dictionary = ShipData.WEAPONS[w["id"]]
		var cost: int = int(data["power"])
		var powered: bool = bool(w["on"]) and cost <= budget
		if powered:
			budget -= cost
			var speed: float = 1.0
			if mine and _boosting("weapons"):
				speed = 1.15
			elif not mine and _manned("weapons"):
				speed = 1.1
			w["charge"] = minf(float(data["charge"]), float(w["charge"]) + delta * speed)
		else:
			w["charge"] = maxf(0.0, float(w["charge"]) - delta * 2.0)
		if not powered or float(w["charge"]) < float(data["charge"]):
			continue
		if mine:
			if str(w["target"]) == "":
				continue
			_fire(w, false)
			if not autofire:
				w["target"] = ""
		else:
			w["target"] = _enemy_pick_room()
			_fire(w, true)
		w["charge"] = 0.0


func _enemy_pick_room() -> String:
	var bag: Array = []
	for room in me_ship["rooms"]:
		var weight: int = {"shields": 3, "weapons": 3, "engines": 2, "life": 1, "pilot": 1, "drones": 1}.get(room["sys"], 1)
		for i in range(weight):
			bag.append(room["id"])
	return str(bag.pick_random())


# ---------------------------------------------------------------- systems and power

func _eff(systems: Dictionary, key: String) -> int:
	if not systems.has(key):
		return 0
	var s: Dictionary = systems[key]
	return mini(int(s["power"]), int(s["max"]) - int(s["damage"]))


func _layers_of(systems: Dictionary) -> int:
	return floori(_eff(systems, "shields") / 2.0)


func _max_layers() -> int:
	return _layers_of(sys) + (1 if uplink else 0)


func _evasion(systems: Dictionary) -> int:
	var eng: int = _eff(systems, "engines")
	if eng <= 0 or _eff(systems, "pilot") <= 0:
		return 0
	return 5 * eng + 5


# Your evasion: the engines, the cockpit, and the drone if it is boosting the engines.
func _my_evasion() -> int:
	var base: int = _evasion(sys)
	return base + 5 if base > 0 and _boosting("engines") else base


# True when the drone has arrived in an undamaged bay holding that system.
func _boosting(sname: String) -> bool:
	if drone_path.size() > 0 or drone_room == "":
		return false
	var room: Dictionary = _room(me_ship["rooms"], drone_room)
	return str(room.get("sys", "")) == sname and sys.has(sname) and int(sys[sname]["damage"]) == 0


func spare_power() -> int:
	var used := 0
	for key in REACTOR_SYS:
		if sys.has(key):
			used += int(sys[key]["power"])
	return reactor - used


func _add_power(key: String) -> void:
	var s: Dictionary = sys[key]
	if spare_power() <= 0 or int(s["power"]) >= int(s["max"]) - int(s["damage"]):
		world.sfx("deny")
		return
	s["power"] = int(s["power"]) + 1
	world.sfx("click", 1.3, -6.0)


func _remove_power(key: String) -> void:
	var s: Dictionary = sys[key]
	if int(s["power"]) <= 0:
		return
	s["power"] = int(s["power"]) - 1
	world.sfx("click", 0.9, -6.0)


func _clip_power(systems: Dictionary) -> void:
	for key in systems:
		var s: Dictionary = systems[key]
		s["power"] = mini(int(s["power"]), int(s["max"]) - int(s["damage"]))


# ---------------------------------------------------------------- shots

func _room(rooms: Array, id: String) -> Dictionary:
	for room in rooms:
		if str(room["id"]) == id:
			return room
	return {}


# The middle of a room, in ship-picture pixels. at_player: a room on your ship.
func _room_center(at_player: bool, id: String) -> Vector2:
	if at_player:
		var r: Rect2 = _room(me_ship["rooms"], id).get("rect", Rect2(78, 43, 0, 0))
		return r.get_center()
	var e: Rect2 = _room(foe["rooms"], id).get("rect", Rect2(40, 46, 0, 0))
	return e.get_center()


func _fire(w: Dictionary, at_player: bool) -> void:
	var data: Dictionary = ShipData.WEAPONS[w["id"]]
	var target: String = str(w["target"])
	var from: Vector2 = _room_center(not at_player, "weapons")
	# Shots leave from the gun on that weapon's mount (the starter's wings, the cutter's gun platforms).
	var slot: int = (e_weapons if at_player else weapons).find(w)
	var mounts: Array = (foe if at_player else me_ship).get("mounts", [])
	if slot >= 0 and slot < mounts.size():
		from = mounts[slot]
	var to: Vector2 = _room_center(at_player, target)
	var dodge: int = _my_evasion() if at_player else _enemy_evasion()
	# from and to are ship-picture pixels: from on the firing ship, to on the target.
	for i in range(int(data["shots"])):
		shots.append({"from": from, "to": to + Vector2(randf_range(-3, 3), randf_range(-3, 3)),
			"t": -0.3 * i, "dmg": int(data["damage"]), "at_player": at_player, "room": target,
			"hit": randf() * 100.0 >= dodge, "color": data["color"], "heavy": int(data["damage"]) >= 3})
	world.sfx("zap", 1.2 if not at_player else 0.8, -4.0)


func _move_shots(delta: float, resolve: bool) -> void:
	var left: Array = []
	for s in shots:
		s["t"] = float(s["t"]) + delta / ShipData.SHOT_TIME
		if float(s["t"]) < 1.0:
			left.append(s)
		elif resolve:
			_land(s)
	shots = left


func _land(s: Dictionary) -> void:
	if result != "":
		return
	var at_player: bool = s["at_player"]
	var where: Vector2 = _on_page(at_player, s["to"])
	if not bool(s["hit"]):
		_pop(where, "Miss", DIM)
		return
	if at_player and layers > 0:
		layers -= 1
		shield_timer = 0.0
		_pop(where + Vector2(-10, 0), "Blocked", SHIELD_BLUE)
		world.sfx("click", 0.6)
		return
	if not at_player and e_layers > 0:
		e_layers -= 1
		e_shield_timer = 0.0
		_pop(where + Vector2(10, 0), "Blocked", SHIELD_BLUE)
		return
	var dmg: int = s["dmg"]
	var room_id: String = s["room"]
	if at_player:
		hull -= dmg
		var room: Dictionary = _room(me_ship["rooms"], room_id)
		var sname: String = str(room.get("sys", ""))
		if sys.has(sname):
			sys[sname]["damage"] = mini(int(sys[sname]["max"]), int(sys[sname]["damage"]) + dmg)
			_clip_power(sys)
		_pop(where, "-%d" % dmg, BAD)
		shake = 0.25
		world.sfx("hurt")
		if hull <= 0:
			hull = 0
			_lose("Hull breached")
	else:
		e_hull -= dmg
		var room2: Dictionary = _room(foe["rooms"], room_id)
		var sname2: String = str(room2.get("sys", ""))
		if e_sys.has(sname2):
			e_sys[sname2]["damage"] = mini(int(e_sys[sname2]["max"]), int(e_sys[sname2]["damage"]) + dmg)
			_clip_power(e_sys)
		_hurt_crew(room_id, dmg, where)
		if sname2 == "weapons" and overcharged:
			for w in e_weapons:
				if str(w["id"]) == "ivan_cannon" and float(w["charge"]) > 0.0:
					w["charge"] = 0.0
					_pop(where + Vector2(0, -8), "Cannon drained!", GOLD)
		_pop(where, "-%d" % dmg, GOLD)
		world.sfx("hit")
		if e_hull <= 0:
			e_hull = 0
			_win()


func _pop(pos: Vector2, text: String, color: Color) -> void:
	pops.append({"pos": pos, "text": text, "t": 0.0, "color": color})


# ---------------------------------------------------------------- the repair drone and enemy repairs

func _damaged_rooms() -> Array:
	var out: Array = []
	for sname in REPAIR_ORDER:
		if sys.has(sname) and int(sys[sname]["damage"]) > 0:
			for room in me_ship["rooms"]:
				if str(room["sys"]) == sname:
					out.append(str(room["id"]))
	return out


func send_drone(room_id: String) -> void:
	if room_id == drone_goal and drone_path.size() > 0:
		return
	if room_id == drone_room and drone_path.is_empty():
		return
	var me: Dictionary = me_ship
	var target: Dictionary = _room(me["rooms"], room_id)
	if target.is_empty():
		return
	# Room to room through the doors (ShipData.route), from the room it's in now; then to the middle of the bay.
	var steps: Array = ShipData.route(me, drone_last, room_id)
	if steps.is_empty() and drone_last != room_id and not (me.get("door_list", []) as Array).is_empty():
		return                       # no way through
	drone_goal = room_id
	drone_work = 0.0
	drone_path = []
	for st in steps:
		drone_path.append({"pos": st["door"]["at"], "room": str(st["room"]), "door": st["door"]})
	drone_path.append({"pos": (target["rect"] as Rect2).get_center(), "room": room_id})
	drone_room = ""


# Crew and the drone open a door as they go through; it shuts again behind them.
func _door_pass(door: Dictionary) -> void:
	door["pass"] = 0.5


func _tick_doors(ship: Dictionary, delta: float) -> void:
	for d in ship.get("door_list", []):
		if float(d["pass"]) > 0.0:
			d["pass"] = maxf(0.0, float(d["pass"]) - delta)


func _move_drone(delta: float) -> void:
	var slow: float = 0.5 if int(sys["drones"]["damage"]) > 0 else 1.0
	if drone_path.size() > 0:
		var next: Dictionary = drone_path[0]
		var to: Vector2 = next["pos"]
		var step: float = ShipData.DRONE_SPEED * slow * delta
		if drone_pos.distance_to(to) <= step:
			drone_pos = to
			drone_last = str(next["room"])
			if next.has("door"):
				_door_pass(next["door"])
			drone_path.pop_front()
			if drone_path.is_empty():
				drone_room = drone_goal
		else:
			drone_pos += (to - drone_pos).normalized() * step
		return
	var here: Dictionary = _room(me_ship["rooms"], drone_room)
	var sname: String = str(here.get("sys", ""))
	if sname != "" and sys.has(sname) and int(sys[sname]["damage"]) > 0:
		drone_work += delta * slow
		if drone_work >= ShipData.DRONE_REPAIR_TIME:
			drone_work = 0.0
			sys[sname]["damage"] = int(sys[sname]["damage"]) - 1
			_pop(_on_page(true, drone_pos) + Vector2(0, -10), "Fixed", GOOD)
			world.sfx("click", 1.6, -4.0)
			if int(sys[sname]["damage"]) == 0 and ShipData.DRONE_BOOST.has(sname):
				_pop(_on_page(true, drone_pos) + Vector2(0, -22), "Boosting", GOLD)


# ---------------------------------------------------------------- enemy crew

func _sys_room(sname: String) -> String:
	for room in foe["rooms"]:
		if str(room["sys"]) == sname:
			return str(room["id"])
	return ""


func _spare_room() -> String:
	var r: String = _sys_room("")
	return r if r != "" else str(foe["rooms"][0]["id"])


# Where crew member i stands in a room: at the console when they're on station in a room with one (Zachary, 21 Nov:
# "the rooms should just have consoles the people can work at"), otherwise the middle, spread out a little.
func _crew_spot(room_id: String, i: int, on_station: bool = false) -> Vector2:
	var room: Dictionary = _room(foe["rooms"], room_id)
	var r: Rect2 = room.get("rect", Rect2(40, 40, 10, 10))
	if on_station and str(room.get("sys", "")) in STATIONS:
		return _station_spot(room)
	var p: Vector2 = r.get_center() + CREW_SPOTS[i % CREW_SPOTS.size()]
	return Vector2(clampf(p.x, r.position.x + 4, r.end.x - 4), clampf(p.y, r.position.y + 4, r.end.y - 4))


# In front of a room's console, in ship-picture pixels: the middle of the cell the console is in.
func _station_spot(room: Dictionary) -> Vector2:
	if not room.has("cells"):
		var r: Rect2 = room["rect"]
		return r.get_center()
	var cell: Vector2i = _console_at(foe, room)[0]
	return (Vector2(cell) + Vector2(0.5, 0.5)) * ShipData.CELL


# Which cell's wall holds a room's console, and which wall: [Vector2i cell, Vector2i side]. A console never sits
# where a door is (Zachary, 21 Nov). The cockpit prefers its front (right) wall, the rest the top wall, then the
# other walls; the first cell, row by row, whose wall there is an outside wall with no door. The art uses the same
# rule (tools/dev/ship_art/kit2x.py, console_at()).
func _console_at(ship: Dictionary, room: Dictionary) -> Array:
	var c: Rect2i = room["cells"]
	var sides: Array = [Vector2i(1, 0), Vector2i(0, -1), Vector2i(0, 1), Vector2i(-1, 0)] if str(room.get("sys", "")) == "pilot" \
			else [Vector2i(0, -1), Vector2i(0, 1), Vector2i(-1, 0), Vector2i(1, 0)]
	for side in sides:
		for y in range(c.position.y, c.end.y):
			for x in range(c.position.x, c.end.x):
				var here := Vector2i(x, y)
				var there: Vector2i = here + side
				if c.has_point(there) or _has_door(ship, here, there):
					continue
				return [here, side]
	return [c.position, Vector2i(0, -1)]


func _has_door(ship: Dictionary, a: Vector2i, b: Vector2i) -> bool:
	for pair in ship.get("doors", []):
		if (pair[0] == a and pair[1] == b) or (pair[0] == b and pair[1] == a):
			return true
	return false


func _make_enemy_crew() -> void:
	e_crew_list.clear()
	e_room_repair.clear()
	for i in range(int(foe["crew"])):
		var home: String = ""
		if i < STATIONS.size():
			home = _sys_room(STATIONS[i])
		if home == "":
			home = _spare_room()
		e_crew_list.append({"home": home, "room": home, "target": home, "pos": _crew_spot(home, i, true), "hp": CREW_HP, "task": "station",
			"last": home, "path": [], "path_to": home})
	e_crew = e_crew_list.size()


# True when someone is standing at that system's station (manning it gives a small bonus, and nobody in the
# cockpit means no evasion).
func _manned(sname: String) -> bool:
	var rid: String = _sys_room(sname)
	if rid == "":
		return false
	for c in e_crew_list:
		if float(c["hp"]) > 0.0 and str(c["task"]) == "station" and str(c["room"]) == rid and str(c["home"]) == rid:
			return true
	return false


func _enemy_evasion() -> int:
	var eng: int = _eff(e_sys, "engines")
	if eng <= 0 or _eff(e_sys, "pilot") <= 0 or not _manned("pilot"):
		return 0
	return 5 * eng + 5 + (5 if _manned("engines") else 0)


func _enemy_crew(delta: float) -> void:
	# Send someone to each damaged room nobody is already seeing to. Never the pilot; spare hands first,
	# then whoever is nearest.
	for sname in REPAIR_ORDER:
		if not e_sys.has(sname) or int(e_sys[sname]["damage"]) <= 0:
			continue
		var rid: String = _sys_room(sname)
		if rid == "":
			continue
		var covered := false
		for c in e_crew_list:
			if float(c["hp"]) > 0.0 and str(c["task"]) == "repair" and str(c["target"]) == rid:
				covered = true
		if covered:
			continue
		var best := -1
		var best_score := INF
		var to: Vector2 = _crew_spot(rid, 0)
		for i in range(e_crew_list.size()):
			var c2: Dictionary = e_crew_list[i]
			if float(c2["hp"]) <= 0.0 or str(c2["task"]) != "station" or str(c2["home"]) == _sys_room("pilot"):
				continue
			var spare: bool = str(_room(foe["rooms"], str(c2["home"])).get("sys", "")) == ""
			var score: float = (c2["pos"] as Vector2).distance_to(to) - (1000.0 if spare else 0.0)
			if score < best_score:
				best_score = score
				best = i
		if best >= 0:
			e_crew_list[best]["task"] = "repair"
			e_crew_list[best]["target"] = rid
	# Walk, and work.
	var working := {}
	for i in range(e_crew_list.size()):
		var c3: Dictionary = e_crew_list[i]
		if float(c3["hp"]) <= 0.0:
			continue
		if str(c3["task"]) == "repair":
			var tsys: String = str(_room(foe["rooms"], str(c3["target"])).get("sys", ""))
			if not e_sys.has(tsys) or int(e_sys[tsys]["damage"]) <= 0:
				c3["task"] = "station"
				c3["target"] = c3["home"]
		# Through the doors when the ship has them (ShipData.route), from the room they're in now.
		if str(c3["path_to"]) != str(c3["target"]):
			c3["path_to"] = c3["target"]
			var steps: Array = []
			for st in ShipData.route(foe, str(c3["last"]), str(c3["target"])):
				steps.append({"pos": st["door"]["at"], "room": str(st["room"]), "door": st["door"]})
			c3["path"] = steps
		var goal: Vector2 = _crew_spot(str(c3["target"]), i, str(c3["task"]) == "station" and str(c3["target"]) == str(c3["home"]))
		var at: Vector2 = c3["pos"]
		var step: float = CREW_SPEED * delta
		var path: Array = c3["path"]
		if path.size() > 0:
			var wp: Dictionary = path[0]
			var to: Vector2 = wp["pos"]
			if at.distance_to(to) <= step:
				c3["pos"] = to
				c3["last"] = wp["room"]
				_door_pass(wp["door"])
				path.pop_front()
			else:
				c3["pos"] = at + (to - at).normalized() * step
			c3["room"] = ""
		elif at.distance_to(goal) > step:
			c3["pos"] = at + (goal - at).normalized() * step
			c3["room"] = ""
		else:
			c3["pos"] = goal
			c3["room"] = c3["target"]
			c3["last"] = c3["target"]
			if str(c3["task"]) == "repair":
				working[c3["room"]] = int(working.get(c3["room"], 0)) + 1
	for rid2 in working:
		var sname2: String = str(_room(foe["rooms"], str(rid2)).get("sys", ""))
		if not e_sys.has(sname2):
			continue
		e_room_repair[rid2] = float(e_room_repair.get(rid2, 0.0)) + delta * int(working[rid2])
		if float(e_room_repair[rid2]) >= ShipData.ENEMY_REPAIR_TIME:
			e_room_repair[rid2] = 0.0
			e_sys[sname2]["damage"] = maxi(0, int(e_sys[sname2]["damage"]) - 1)
			e_sys[sname2]["power"] = int(e_sys[sname2]["max"]) - int(e_sys[sname2]["damage"])


# A hit on an enemy room hurts whoever is standing in it. When the last of them goes down, the fight is won.
func _hurt_crew(room_id: String, dmg: int, where: Vector2) -> void:
	for c in e_crew_list:
		if float(c["hp"]) > 0.0 and str(c["room"]) == room_id:
			c["hp"] = maxf(0.0, float(c["hp"]) - CREW_HIT * dmg)
			if float(c["hp"]) <= 0.0:
				_pop(where + Vector2(0, 10), "Crew down", Color("ffbeaa"))
	var standing := 0
	for c2 in e_crew_list:
		if float(c2["hp"]) > 0.0:
			standing += 1
	e_crew = standing
	if e_crew == 0 and e_hull > 0 and result == "":
		result = "won"
		result_text = "Their crew is down"
		end_timer = 2.0
		world.sfx("quest")


# A room's name for S.A.R.A.'s lines: "engine room", "drone bay"...
func _room_words(room: Dictionary) -> String:
	var words := {"engines": "engine room", "weapons": "weapons room", "drones": "drone bay", "life": "oxygen room",
		"shields": "shield room", "pilot": "cockpit"}
	return str(words.get(str(room.get("sys", "")), str(room.get("label", "room")).to_lower()))


func _tutorial_hints() -> void:
	if not bool(fight.get("tutorial", false)):
		return
	var any_target := false
	for w in weapons:
		if str(w["target"]) != "":
			any_target = true
	var hurt: Array = _damaged_rooms()
	if not tutorial_said.has("hit") and hurt.size() > 0:
		tutorial_said["hit"] = true
		paused = true
		var room: Dictionary = _room(me_ship["rooms"], str(hurt[0]))
		world._say("Sara", [
			"Your %s has been hit. A damaged room shows red, and its system loses bars until it's mended." % _room_words(room),
			"Your drone is your crew. Click the drone, then click the %s. It goes through the doors and repairs whatever room it's in." % _room_words(room),
			"Press Space when you're ready.",
		])
	elif tutorial_said.has("hit") and not tutorial_said.has("boost") and hurt.is_empty() and drone_room != "drones" and drone_path.is_empty():
		tutorial_said["boost"] = true
		world._say("Sara", [
			"[happy] Mended. And while the drone sits in a working bay, it boosts that system.",
			"Shields recharge faster, weapons charge faster, or the engines give you more evasion. Put it where it helps most.",
			"Ordering a crew about works the same way: click them, then click where they should go.",
		])
	elif not tutorial_said.has("power") and _eff(sys, "shields") < 2 and int(sys["shields"]["damage"]) == 0:
		tutorial_said["power"] = true
		paused = true
		world._say("Sara", ["Your shields are short of power. Click the Shield bars at the bottom to give them more."])
	elif not any_target and selected < 0 and not tutorial_said.has("aim") and float(weapons[0]["charge"]) >= float(ShipData.WEAPONS["burst_laser"]["charge"]):
		tutorial_said["aim"] = true
		paused = true
		world._say("Sara", ["Your laser is charged. Click it, then click their Shields room."])
# ---------------------------------------------------------------- input

func handle_input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key == null or not key.pressed or key.echo:
		return
	match key.physical_keycode:
		KEY_SPACE, KEY_P:
			_toggle_pause()
		KEY_1, KEY_2, KEY_3:
			_pick_weapon(key.physical_keycode - KEY_1)
		KEY_ESCAPE, KEY_Q:
			selected = -1
			drone_selected = false
		KEY_D, KEY_TAB:
			_select_drone()
		KEY_V:
			autofire = not autofire
			world.sfx("click")
		KEY_J:
			_jump()


func _toggle_pause() -> void:
	if result == "":
		paused = not paused
		world.sfx("click")


func _select_drone() -> void:
	drone_selected = not drone_selected
	selected = -1
	world.sfx("click", 1.4)


func _pick_weapon(i: int) -> void:
	if i < 0 or i >= weapons.size() or str(weapons[i]["id"]) == "":
		return
	var w: Dictionary = weapons[i]
	if not bool(w["on"]):
		w["on"] = true
	var cost: int = int(ShipData.WEAPONS[w["id"]]["power"])
	if _eff(sys, "weapons") < cost:
		_add_power("weapons")
	selected = i if selected != i else -1
	drone_selected = false
	world.sfx("click")


# A click on the page (ui/ship_screen.gd). id names a button or card; anything else is found by where it landed.
# Orders can be given while paused, as in FTL.
func _click(id: String, p: Vector2, button: int) -> void:
	if world.dialogue.active:
		if button == MOUSE_BUTTON_LEFT:
			world.dialogue.advance()
		return
	if result != "":
		return
	var left: bool = button == MOUSE_BUTTON_LEFT
	var right: bool = button == MOUSE_BUTTON_RIGHT
	if not left and not right:
		return
	if id == "jump":
		_jump()
		return
	if id == "pause":
		_toggle_pause()
		return
	if id == "auto":
		autofire = not autofire
		world.sfx("click")
		return
	if id.begins_with("sys/"):
		var key: String = REACTOR_SYS[int(id.get_slice("/", 1))]
		if left:
			_add_power(key)
		else:
			_remove_power(key)
		return
	if id.begins_with("weapon/"):
		var i: int = int(id.get_slice("/", 1))
		if left:
			_pick_weapon(i)
		elif str(weapons[i]["id"]) != "":
			weapons[i]["target"] = ""
			weapons[i]["on"] = false
			if selected == i:
				selected = -1
		return
	# the drone: click it (on the ship or in the Aboard list) to select it
	if left and (id == "drone" or _drone_rect().has_point(p)):
		_select_drone()
		return
	# your doors: click one to shut it or open it again
	for d in me_ship.get("door_list", []):
		if _door_rect(d, my_xf).grow(3.0).has_point(p):
			d["open"] = not bool(d["open"])
			world.sfx("click", 0.8 if bool(d["open"]) else 1.1, -4.0)
			return
	# a bay on your ship: with the drone selected, send it there (left or right click, as with crew in FTL)
	for room in me_ship["rooms"]:
		if (my_xf * (room["rect"] as Rect2)).has_point(p):
			if bool(room.get("crew", false)):
				if drone_selected:
					_pop(p, "Only you fit in here", DIM)
			elif drone_selected:
				drone_selected = false
				send_drone(str(room["id"]))
				world.sfx("click", 1.4)
			elif left:
				_pop(p, "Click the drone first", DIM)
			return
	if right:
		selected = -1
		drone_selected = false
		return
	# a room on their ship: aim
	if selected >= 0:
		for room in foe["rooms"]:
			if (foe_xf * (room["rect"] as Rect2)).has_point(p):
				weapons[selected]["target"] = str(room["id"])
				selected = -1
				world.sfx("click", 1.2)
				return


# ---------------------------------------------------------------- layout (page pixels)

func _sys_rect(i: int) -> Rect2: return Rect2(87 + i * 42, 322, 33, 56)
func _drone_card_rect() -> Rect2: return Rect2(569, 341, 142, 20)


func _weapon_rect(i: int) -> Rect2:
	var n: int = maxi(1, weapons.size())
	var w: float = floorf((284.0 - (n - 1) * 6.0) / n)
	return Rect2(270 + i * (w + 6.0), 323, w, 51)


func _drone_rect() -> Rect2:
	var half: float = maxf(6.0, 4.0 * _ship_scale(true))
	return Rect2(_on_page(true, drone_pos) - Vector2(half, half), Vector2(half, half) * 2.0)


# ---------------------------------------------------------------- drawing

func _paint() -> void:
	_fit_ships()
	screen.case("In combat", ShipScreen.PIP_RED)
	_paint_strip()
	_paint_my_window()
	_paint_foe_window()
	_paint_shots()
	for p in pops:
		var c: Color = p["color"]
		c.a = 1.0 - float(p["t"]) / 1.2
		var at: Vector2 = p["pos"]
		screen.text_center(at.x, at.y - float(p["t"]) * 12.0 - 8.0, str(p["text"]), "label", c)
	_paint_reactor()
	_paint_weapons()
	_paint_aboard()
	_paint_status()


# Your ship's readings, along the top of the case.
func _paint_strip() -> void:
	var s := screen
	s.text(58, 59, "HULL", "micro", MUTED)
	var step: float = minf(7.0, floorf(84.0 / maxf(1.0, float(hull_max))))
	var low: bool = hull * 3 <= hull_max
	s.pips(86, 59, hull_max, hull, step - 2.0, 9.0, 2.0, ShipScreen.PIP_RED if low else ShipScreen.PIP_ON)
	s.text(178, 59, "SHIELDS", "micro", MUTED)
	var top: int = _max_layers()
	for i in range(top):
		var c := Vector2(230.5 + i * 12, 63.5)
		var from_sara: bool = uplink and i == top - 1
		var lit := Color("78d8e6") if from_sara else ShipScreen.SHIELD
		s.circle(c, 4.5, lit if i < layers else ShipScreen.PIP_OFF)
		s.ring(c, 4.5, Color("3f6a78"))
	var ev_x: float = maxf(270.0, 234.0 + top * 12.0)
	s.text(ev_x, 59, "EVASION %d%%   OXYGEN %d%%" % [_my_evasion(), int(oxygen)], "micro", MUTED if oxygen > 40.0 else ShipScreen.PIP_RED)
	s.text(440, 59, "FOLD DRIVE", "micro", MUTED)
	var story: bool = bool(fight.get("story", false))
	if story:
		s.text(496, 59, "NOT ON THIS FLIGHT", "micro", MUTED)
	else:
		s.rect(Rect2(496, 61, 106, 5), ShipScreen.PIP_OFF)
		s.rect(Rect2(496, 61, 106.0 * fold / 100.0, 5), ORANGE)
	var can_jump: bool = fold >= 100.0 and not story and result == ""
	s.button("jump", Rect2(610, 55, 48, 16), "Jump", can_jump, "micro", can_jump)
	s.button("auto", Rect2(664, 55, 48, 16), "Auto", autofire, "micro")


func _paint_my_window() -> void:
	var s := screen
	s.scope(MY_WIN, 1)
	s.text(MY_WIN.position.x + 11, MY_WIN.position.y + 7, "OWN SHIP", "micro", ShipScreen.SCOPE_TEXT)
	if uplink:
		s.text_right(MY_WIN.end.x - 11, MY_WIN.position.y + 7, "S.A.R.A. UPLINK", "micro", Color("78d8e6"))
	var me: Dictionary = me_ship
	var size: Vector2 = me["size"]
	var k: float = _ship_scale(true)
	var off := Vector2(randf_range(-1, 1), randf_range(-1, 1)) * (2.0 if shake > 0.0 else 0.0)
	var xf := Transform2D(0.0, Vector2(k, k), 0.0, my_xf.origin + off)
	if layers > 0:
		var mid: Vector2 = xf * (size / 2.0 + Vector2(6, 0))
		s.ellipse(mid, size * k / 2.0 + Vector2(8, 8), Color(SHIELD_BLUE, 0.55 + 0.2 * layers), 1.0)
		if layers > 1:
			s.ellipse(mid, size * k / 2.0 + Vector2(12, 12), Color(Color("78f0ff"), 0.7), 1.0)
	# The cut-away when there is one; otherwise the hull with the rooms drawn over it.
	var inside: bool = interior_tex != null
	if inside:
		s.texture(interior_tex, Rect2(xf.origin, size * k))
	elif ship_tex != null:
		var fw: float = ship_tex.get_width() / float(me["frames"])
		s.texture(ship_tex, Rect2(xf.origin, size * k), Rect2(fw * int(me["frame"]), 0, fw, ship_tex.get_height()))
	# the rooms: red while damaged, a name tag, and the system's bars
	for room in me["rooms"]:
		var rr: Rect2 = xf * (room["rect"] as Rect2)
		var sname: String = room["sys"]
		var dmg: int = int(sys[sname]["damage"]) if sys.has(sname) else 0
		var crew_room: bool = bool(room.get("crew", false))
		if inside:
			if dmg > 0:
				s.rect(rr.grow(-2.0 * k), Color(0.86, 0.22, 0.16, 0.38))
		else:
			var fill := Color(0.92, 0.9, 0.86, 0.95) if crew_room else Color(0.38, 0.4, 0.46, 0.88)
			if dmg > 0:
				fill = fill.lerp(Color("a0463c"), 0.65)
			s.rect(rr, fill)
			s.outline(rr, Color("282834"))
		_room_tag(rr, str(room["label"]), k)
		if sys.has(sname) and sname != "pilot":
			var bars: int = int(sys[sname]["max"])
			for i in range(bars):
				var bar := Rect2(rr.position + Vector2(3.0 * k + i * 4.0 * k, rr.size.y - 3.0 * k - 2.0 * k), Vector2(3.0 * k, 2.0 * k))
				s.rect(bar, GOOD if i < bars - dmg else BAD)
		if drone_selected and not crew_room and result == "" and rr.has_point(s.mouse):
			s.outline(rr.grow(-1.0), GOOD, maxf(1.0, k * 0.5))
	_paint_doors(me_ship, xf, k, true)
	_paint_guns(me, weapons, xf)
	# you, in the cockpit
	var cockpit: Rect2 = _room(me["rooms"], "cockpit")["rect"]
	var you: Vector2 = xf * (cockpit.get_center() + Vector2(-2, 0))      # in the seat, under the canopy
	s.circle(you, 5.0 * k, YOU)
	s.ring(you, 5.0 * k, Color("201e28"))
	# the drone
	var dp: Vector2 = xf * drone_pos
	var dh: float = 3.0 * k
	var body := Rect2(dp - Vector2(dh, dh), Vector2(dh, dh) * 2.0)
	if drone_selected:
		s.ring(dp, dh * 2.0, GOOD)
	s.rect(body, DRONE)
	s.outline(body, Color("282018"))
	if drone_room != "" and drone_work > 0.0:
		s.rect(Rect2(dp + Vector2(-5, -7) * k, Vector2(10.0 * k * drone_work / ShipData.DRONE_REPAIR_TIME, maxf(1.0, k))), GOOD)
	if paused and result == "" and not world.dialogue.active:
		var tag := Rect2(MY_WIN.get_center().x - 30, MY_WIN.position.y + 4, 60, 14)
		s.rect(tag, Color("f2c94c"))
		s.text_center(tag.get_center().x, tag.position.y, "PAUSED", "micro", INK)


# The guns on their mounts, pointing at the nose (shapes until the weapon art exists). Drawn in ship-picture pixels
# through the ship's transform, so an enemy's guns are mirrored with it and point at you.
func _paint_guns(ship: Dictionary, list: Array, xf: Transform2D) -> void:
	var mounts: Array = ship.get("mounts", [])
	for i in range(mini(mounts.size(), list.size())):
		if str(list[i]["id"]) == "":
			continue
		var m: Vector2 = mounts[i]
		var data: Dictionary = ShipData.WEAPONS[list[i]["id"]]
		var f: float = 1.7 if int(data["damage"]) >= 3 else 1.0          # big guns (Ivan's cannon) drawn bigger
		# a bracket against the hull, the gun body, its barrel and a lit tip
		screen.rect(xf * Rect2(m + Vector2(-6, -3) * f, Vector2(8, 6) * f), Color("3a3644"))
		screen.rect(xf * Rect2(m + Vector2(-5, -2) * f, Vector2(6, 4) * f), Color("5d5868"))
		screen.rect(xf * Rect2(m + Vector2(-5, -2) * f, Vector2(6, 1) * f), Color("8a8498"))
		screen.rect(xf * Rect2(m + Vector2(1, -1) * f, Vector2(10, 2) * f), Color("6e6a7c"))
		screen.rect(xf * Rect2(m + Vector2(9, -1) * f, Vector2(2, 2) * f), data["color"])


# A room's name in a small dark tag in its top-left corner (cut to the room's width).
func _room_tag(rr: Rect2, label: String, k: float) -> void:
	if rr.size.y < 18.0:
		return
	var s := screen
	var words := label.to_upper()
	var room_w: float = rr.size.x - 4.0 * k - 2.0
	while words.length() > 0 and s.width(words, "micro") > room_w:
		words = words.left(words.length() - 1)
	var w: float = s.width(words, "micro") + 4.0
	var at := rr.position + Vector2(2.0 * k, 2.0 * k)
	s.rect(Rect2(at, Vector2(w, 11)), Color(0.08, 0.09, 0.12, 0.78))
	s.text(at.x + 2, at.y - 2, words, "micro", Color("fff6ea"))


# A door's slab, on the page. Doors sit in the gap the interior art leaves in the wall: 10 x 4 picture pixels.
func _door_rect(d: Dictionary, xf: Transform2D) -> Rect2:
	var at: Vector2 = xf * (d["at"] as Vector2)
	var k: float = absf(xf.y.y)
	var half := Vector2(2.0, 5.0) * k if bool(d["across"]) else Vector2(5.0, 2.0) * k
	return Rect2(at - half, half * 2.0)


# Doors (Zachary, 21 Nov): open (just the frame's ends), shut (an orange slab), or locked (red, door_level 2+).
# Someone walking through holds a door open for a moment. Your own doors light up under the pointer.
func _paint_doors(ship: Dictionary, xf: Transform2D, k: float, mine: bool) -> void:
	var s := screen
	var locks: bool = int(ship.get("door_level", 1)) >= 2
	for d in ship.get("door_list", []):
		var slab := _door_rect(d, xf)
		var is_open: bool = bool(d["open"]) or float(d["pass"]) > 0.0
		if is_open:
			var e: float = maxf(1.0, k)
			if bool(d["across"]):
				s.rect(Rect2(slab.position, Vector2(slab.size.x, e)), DOOR)
				s.rect(Rect2(slab.position + Vector2(0, slab.size.y - e), Vector2(slab.size.x, e)), DOOR)
			else:
				s.rect(Rect2(slab.position, Vector2(e, slab.size.y)), DOOR)
				s.rect(Rect2(slab.position + Vector2(slab.size.x - e, 0), Vector2(e, slab.size.y)), DOOR)
		else:
			s.rect(slab, ShipScreen.PIP_RED if locks else DOOR)
			s.rect(slab.grow(-maxf(1.0, k * 0.5)), Color("ffa096") if locks else Color("ffd08a"))
		if mine and result == "" and slab.grow(3.0).has_point(s.mouse):
			s.outline(slab.grow(2.0), Color("fff6ea"))


# Their window: the band with their name, hull, shields, evasion and crew, then the ship.
func _paint_foe_window() -> void:
	var s := screen
	s.scope(FOE_WIN, 4, true)
	var x0: float = FOE_WIN.position.x + 11
	var y0: float = FOE_WIN.position.y
	s.text_fit(x0, y0 + 6, 150, str(foe.get("name", "")).to_upper(), "label", Color("f0e6d0"))
	var step: float = minf(7.0, floorf(150.0 / maxf(1.0, float(e_hull_max))))
	s.pips(x0, y0 + 25, e_hull_max, e_hull, step - 2.0, 9.0, 2.0, Color("c9a46a"), Color("5a524c"), Color("3a2a22"), Color("6e625a"))
	var shield_x: float = x0 + e_hull_max * step + 6.0
	for i in range(_layers_of(e_sys)):
		var c := Vector2(shield_x + 4.5 + i * 12, y0 + 29.5)
		s.circle(c, 4.5, ShipScreen.SHIELD if i < e_layers else Color("5a524c"))
		s.ring(c, 4.5, Color("3f6a78"))
	var right: float = FOE_WIN.end.x - 11
	s.text_right(right, y0 + 7, "HOSTILE", "micro", ShipScreen.HOSTILE_TEXT)
	s.text_right(right, y0 + 19, "EVASION %d%%" % _enemy_evasion(), "micro", Color("c8b8a8"))
	s.text_right(right, y0 + 31, "CREW %d" % e_crew, "micro", Color("c8b8a8"))
	if overcharged:
		for w in e_weapons:
			if str(w["id"]) == "ivan_cannon":
				var full: float = float(ShipData.WEAPONS["ivan_cannon"]["charge"])
				s.rect(Rect2(x0, y0 + 38, 150, 3), Color("3c2a1e"))
				s.rect(Rect2(x0, y0 + 38, 150.0 * float(w["charge"]) / full, 3), GOLD)
	var destroyed: bool = e_hull <= 0
	if not (destroyed and (end_timer < 1.6 or result == "done")):
		_paint_enemy()
	if destroyed and result != "done":
		_paint_blast()


func _paint_enemy() -> void:
	var s := screen
	var xf: Transform2D = foe_xf
	var k: float = _ship_scale(false)
	var size: Vector2 = foe["size"]
	if e_layers > 0:
		s.ellipse(xf * (size / 2.0), size * k / 2.0 + Vector2(10, 10), Color(SHIELD_BLUE, 0.8), 1.0)
	var inside: bool = enemy_inside != null
	if inside:
		s.texture(enemy_inside, _ship_rect(xf, size))
	elif enemy_tex != null:
		s.texture(enemy_tex, _ship_rect(xf, size))
	else:
		for fin in foe.get("fins", []):
			var pts := PackedVector2Array()
			for v in fin:
				pts.append(xf * (v as Vector2))
			s.polygon(pts, Color(foe.get("hull_color", Color("60463e"))).lightened(0.15))
		var shape := PackedVector2Array()
		for v in foe.get("shape", [Vector2.ZERO, Vector2(size.x, 0), size, Vector2(0, size.y)]):
			shape.append(xf * (v as Vector2))
		s.polygon(shape, foe.get("hull_color", Color("60463e")))
		shape.append(shape[0])
		s.polyline(shape, Color("241818"), 1.0)
		s.line(xf * Vector2(30, size.y / 2.0), xf * Vector2(size.x - 10, size.y / 2.0), foe.get("trim", Color("962828")), 2.0)
	for room in foe["rooms"]:
		var rr: Rect2 = xf * (room["rect"] as Rect2)
		var sname: String = room["sys"]
		var dmg: int = int(e_sys[sname]["damage"]) if e_sys.has(sname) else 0
		if inside:
			if dmg > 0:
				s.rect(rr.grow(-2.0 * k), Color(0.86, 0.22, 0.16, 0.38))
			_room_tag(rr, str(room["label"]), k)
		else:
			var fill := Color(0.69, 0.59, 0.53, 0.92)
			if dmg > 0:
				fill = fill.lerp(Color("a0463c"), 0.6)
			s.rect(rr, fill)
			s.outline(rr, Color("32221e"))
			if rr.size.y >= 18.0:
				s.text_fit(rr.position.x + 3, rr.position.y + 2, rr.size.x - 5, str(room["label"]), "micro", Color("281814"))
		if e_sys.has(sname) and sname != "pilot":
			var bars: int = int(e_sys[sname]["max"])
			for i in range(bars):
				var bar := Rect2(rr.position + Vector2(3.0 * k + i * 4.0 * k, rr.size.y - 3.0 * k - 2.0 * k), Vector2(3.0 * k, 2.0 * k))
				s.rect(bar, GOOD if i < bars - dmg else BAD)
		if selected >= 0 and rr.has_point(s.mouse):
			s.outline(rr, BAD)
	_paint_doors(foe, xf, k, false)
	_paint_guns(foe, e_weapons, xf)
	# their crew: red at stations, orange when repairing, a health bar once hurt
	for c in e_crew_list:
		var cpos: Vector2 = xf * (c["pos"] as Vector2)
		var cr: float = 3.0 * k
		if float(c["hp"]) <= 0.0:
			s.line(cpos + Vector2(-cr, -cr), cpos + Vector2(cr, cr), Color("5a4a48"), 1.0)
			s.line(cpos + Vector2(-cr, cr), cpos + Vector2(cr, -cr), Color("5a4a48"), 1.0)
			continue
		s.circle(cpos, cr, Color("f0a040") if str(c["task"]) == "repair" else Color("e65a50"))
		s.ring(cpos, cr, Color("201010"))
		if float(c["hp"]) < CREW_HP:
			var hp_bar := Rect2(cpos + Vector2(-4, -6) * k, Vector2(8.0 * k, maxf(1.0, k)))
			s.rect(hp_bar, Color("3c2020"))
			s.rect(Rect2(hp_bar.position, Vector2(hp_bar.size.x * float(c["hp"]) / CREW_HP, hp_bar.size.y)), GOOD)
	# where your weapons are aimed
	for i in range(weapons.size()):
		var tid: String = str(weapons[i]["target"])
		if tid == "":
			continue
		var at: Vector2 = xf * _room_center(false, tid)
		var r: float = (6.0 + i * 2.0) * k
		s.ring(at, r, BAD)
		s.line(at + Vector2(-r - 3, 0), at + Vector2(r + 3, 0), BAD, 1.0)
		s.line(at + Vector2(0, -r - 3), at + Vector2(0, r + 3), BAD, 1.0)
		s.text(at.x + r + 1, at.y - r - 10, str(i + 1), "micro", BAD)


func _paint_blast() -> void:
	var s := screen
	var k: float = _ship_scale(false)
	var c: Vector2 = foe_xf * ((foe["size"] as Vector2) / 2.0)
	var t: float = clampf(1.0 - (end_timer - 0.2) / 2.0, 0.0, 1.0)
	for i in range(4):
		var r: float = (10.0 + i * 12.0) * t * 1.6 * k
		s.circle(c + Vector2(i * 7 - 10, (i % 2) * 8 - 4) * k, r * 0.6, Color(1.0, 0.7 - i * 0.12, 0.2, maxf(0.0, 0.9 - t)))
	for i in range(10):
		var a: float = i * TAU / 10.0
		s.rect(Rect2(c + Vector2(cos(a), sin(a)) * 70.0 * t * k, Vector2(3, 2) * k), Color(0.6, 0.5, 0.45, maxf(0.0, 1.0 - t)))


# Shots leave the firing ship's window and come in from the near edge of the target's, as in FTL.
func _paint_shots() -> void:
	for sh in shots:
		var t: float = float(sh["t"])
		if t < 0.0:
			continue
		var at_player: bool = sh["at_player"]
		var a: Vector2 = _on_page(not at_player, sh["from"])
		var b: Vector2 = _on_page(at_player, sh["to"])
		var out_x: float = (FOE_WIN.position.x + 3.0) if at_player else (MY_WIN.end.x - 3.0)
		var in_x: float = (MY_WIN.end.x - 3.0) if at_player else (FOE_WIN.position.x + 3.0)
		var leave := Vector2(out_x, a.y)
		var enter := Vector2(in_x, lerpf(b.y, a.y, 0.25))
		var first: float = a.distance_to(leave)
		var split: float = first / maxf(1.0, first + enter.distance_to(b))
		var heavy: bool = sh["heavy"]
		var tail: float = 12.0 if heavy else 8.0
		var head: Vector2
		var dir: Vector2
		if t < split:
			head = a.lerp(leave, t / maxf(0.001, split))
			dir = (leave - a).normalized()
			tail = minf(tail, head.distance_to(a))
		else:
			head = enter.lerp(b, (t - split) / maxf(0.001, 1.0 - split))
			dir = (b - enter).normalized()
			tail = minf(tail, head.distance_to(enter))
		screen.line(head - dir * tail, head, sh["color"], 3.0 if heavy else 2.0)


func _paint_reactor() -> void:
	var s := screen
	var r := Rect2(53, 297, 206, 83)
	s.panel(r, "power", "Reactor")
	var spare: int = spare_power()
	s.text_right(r.end.x - 8, r.position.y + 7, "%d FREE / %d" % [spare, reactor], "micro", MUTED)
	for i in range(reactor):
		var unit := Rect2(62, 368 - i * 6, 13, 4)
		s.rect(unit, ShipScreen.PIP_ON if i < spare else ShipScreen.PIP_OFF)
	for k in range(REACTOR_SYS.size()):
		var key: String = REACTOR_SYS[k]
		var box := _sys_rect(k)
		var x: float = box.position.x + 5
		var st: Dictionary = sys[key]
		var top: int = int(st["max"])
		var step: float = 8.0 if top <= 4 else floorf(32.0 / top)
		for i in range(top):
			var col := ShipScreen.PIP_OFF
			if i >= top - int(st["damage"]):
				col = ShipScreen.PIP_RED
			elif i < int(st["power"]):
				col = ShipScreen.PIP_ON
			var bar := Rect2(x, 354 - i * step, 23, step - 2.0)
			s.rect(bar, col)
			s.outline(bar, Color("4d5a4e") if col == ShipScreen.PIP_ON else Color("bdb4a5"))
		if _boosting(key):
			s.rect(Rect2(x + 9, 326, 5, 5), DRONE)
			s.outline(Rect2(x + 9, 326, 5, 5), Color("5a4512"))
		s.text_center(x + 11.5, 364, str(SYS_LABEL[key]), "micro", MUTED)
		if s.hovering(box):
			s.outline(box, ORANGE)
		s.hit("sys/%d" % k, box)


# Which of your weapons the weapons system has power for, in slot order (as _charge_weapons spends it).
func _powered_weapons() -> Array:
	var budget: int = _eff(sys, "weapons")
	var out: Array = []
	for w in weapons:
		var ok := false
		if str(w["id"]) != "" and bool(w["on"]):
			var cost: int = int(ShipData.WEAPONS[w["id"]]["power"])
			if cost <= budget:
				budget -= cost
				ok = true
		out.append(ok)
	return out


# Each card shows the weapon's power use (Zachary, 21 Nov): one pip per bar it needs, lit while it has them.
func _paint_weapons() -> void:
	var s := screen
	var powered: Array = _powered_weapons()
	var r := Rect2(264, 297, 296, 83)
	s.panel(r, "blaster", "Weapons")
	if autofire:
		s.text_right(r.end.x - 8, r.position.y + 7, "AUTOFIRE ON", "micro", OCHRE)
	for i in range(weapons.size()):
		var card := _weapon_rect(i)
		var w: Dictionary = weapons[i]
		if str(w["id"]) == "":
			s.frame(card, Color("ece9e0"))
			s.text(card.position.x + 6, card.position.y + 4, "%d  Empty slot" % (i + 1), "label", MUTED)
			s.text(card.position.x + 6, card.position.y + 33, "BUY OR SALVAGE ONE", "micro", MUTED)
			continue
		var data: Dictionary = ShipData.WEAPONS[w["id"]]
		var charged: bool = float(w["charge"]) >= float(data["charge"])
		var on: bool = bool(w["on"])
		s.frame(card, Color("f8f6ef") if on else Color("e6e4de"))
		if selected == i:
			s.outline(card, ORANGE, 2.0)
		var cost: int = int(data["power"])
		var pips_w: float = cost * 7.0 + 12.0
		s.text_fit(card.position.x + 6, card.position.y + 4, card.size.x - 18 - pips_w, "%d  %s" % [i + 1, str(data["name"])], "label", INK if on else MUTED)
		s.img("i_bolt", Rect2(card.end.x - 6 - pips_w, card.position.y + 8, 9, 9), OCHRE if bool(powered[i]) else MUTED)
		s.pips(card.end.x - 6 - cost * 7.0 + 2, card.position.y + 8, cost, cost if bool(powered[i]) else 0, 5.0, 9.0, 2.0)
		var bar := Rect2(card.position.x + 6, card.position.y + 25, card.size.x - 12, 5)
		s.rect(bar, ShipScreen.PIP_OFF)
		s.rect(Rect2(bar.position, Vector2(bar.size.x * float(w["charge"]) / float(data["charge"]), bar.size.y)), ORANGE if charged else Color("6f9fb4"))
		var note := "OFF - CLICK TO POWER"
		if on:
			note = "READY - CLICK TO AIM" if charged else "CHARGING"
			if not bool(powered[i]):
				note = "NEEDS %d POWER" % cost
			elif selected == i:
				note = "AIM: CLICK A ROOM"
			elif str(w["target"]) != "":
				note = "AIMED"
		s.text_fit(card.position.x + 6, card.position.y + 33, card.size.x - 12, note, "micro", OCHRE if charged and on else MUTED)
		if s.hovering(card) and selected != i:
			s.outline(card, ORANGE)
		s.hit("weapon/%d" % i, card)


func _paint_aboard() -> void:
	var s := screen
	var r := Rect2(565, 297, 150, 83)
	s.panel(r, "mark", "Aboard")
	s.circle(Vector2(578.5, 331.5), 4.5, YOU)
	s.ring(Vector2(578.5, 331.5), 4.5, Color("2a2420"))
	s.text(590, 325, "You", "label", INK)
	s.text_right(r.end.x - 8, 328, "PILOT", "micro", MUTED)
	var card := _drone_card_rect()
	if drone_selected:
		s.rect(card, Color("ecdcc4"))
		s.outline(card, ORANGE)
	elif s.hovering(card):
		s.outline(card, ORANGE)
	s.rect(Rect2(574, 347, 9, 9), DRONE)
	s.outline(Rect2(574, 347, 9, 9), Color("5a4512"))
	s.text(590, 344, "Drone", "label", INK)
	var note := "IDLE"
	if drone_selected:
		note = "PICK A BAY"
	elif drone_path.size() > 0:
		note = "MOVING"
	elif drone_work > 0.0:
		note = "REPAIRING"
	else:
		for sname in ShipData.DRONE_BOOST:
			if _boosting(sname):
				note = "BOOSTING %s" % str(SYS_LABEL.get(sname, sname)).to_upper()
	s.text_right(r.end.x - 8, 347, note, "micro", MUTED)
	s.hit("drone", card)
	s.text(574, 366, "D DRONE   ESC CANCEL", "micro", MUTED)


func _paint_status() -> void:
	var s := screen
	var line := "1-2 weapons   D drone   V autofire   Space pause"
	if not bool(fight.get("story", false)):
		line += "   J jump"
	var col := INK
	if result != "" and result != "done":
		line = result_text
	elif world.dialogue.active:
		line = ""
	elif paused:
		line = "Paused. You can still give orders; Space or Resume carries on."
	elif drone_selected:
		line = "Click a bay on your ship to send the drone there."
	elif selected >= 0:
		line = "Click a room on their ship to aim the %s." % str(ShipData.WEAPONS[weapons[selected]["id"]]["name"])
	s.status(line, col)
	s.solid_button("pause", Rect2(625, 388, 82, 22), "Resume" if paused else "Pause", result == "")
	if result != "" and result != "done":
		var box := Rect2(234, 166, 300, 34)
		s.frame(box, Color("f8f7f1"))
		var tone := OCHRE
		if result == "won":
			tone = Color("3f7a4c")
		elif result == "lost":
			tone = Color("a43a2a")
		s.text_center(box.get_center().x, box.position.y + 9, result_text, "strong", tone)
