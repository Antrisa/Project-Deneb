extends CanvasLayer
# The FTL-style space battle (21 Nov 2026). Real time; Space pauses. Your ship on the left in cut-away, the enemy
# on the right. Power goes from the reactor to shields, engines, weapons and life support. Pick a weapon, then an
# enemy room, and it fires when charged. Your starter ship's bays are sealed: the repair drone is your one crew
# member. Click it, then click a bay, and it crawls there through the ducts. It repairs the bay it is in, and in a
# working bay it boosts that system (ShipData.DRONE_BOOST). It never moves on its own: this is the lesson for
# ordering crew about on bigger ships.
#
# main.gd owns the story around a fight: it calls start() with a fight, shows any dialogue (which pauses the
# battle), and gets on_end.call(result, hull_left) with result "won", "lost" or "fled". Ships, weapons and
# numbers are in scripts/ship_data.gd. Laid out for 320x180, drawn at 2x like the rest of the interface.
# Until the ship art pack exists, enemy ships and effects are drawn here as simple shapes.

const ShipData = preload("res://scripts/ship_data.gd")

const W := 320.0
const H := 180.0
const PLAYER_POS := Vector2(6, 40)       # top-left of your ship picture
const ENEMY_POS := Vector2(192, 46)      # top-left of the enemy ship
const REACTOR_SYS := ["shields", "engines", "weapons", "life"]
const SYS_LABEL := {"shields": "Shield", "engines": "Engine", "weapons": "Weapon", "life": "Oxygen"}
const REPAIR_ORDER := ["shields", "weapons", "pilot", "engines", "life", "drones"]
const WHITE := Color("ececf0")
const DIM := Color("969cb0")
const GOLD := Color("fadc5a")
const GOOD := Color("5adc6e")
const BAD := Color("e6463c")
const SHIELD_BLUE := Color("5ab4ff")
const PANEL := Color(0.08, 0.09, 0.16, 0.92)
const EDGE := Color("46506e")

var world                        # main.gd
var open := false
var paused := false
var on_end: Callable = Callable()
var fight: Dictionary = {}
var result := ""                 # "" while fighting, then "won", "lost" or "fled"
var result_text := ""
var end_timer := 0.0

var view: Control
var font: Font
var stars: Array = []
var ship_tex: Texture2D
var enemy_tex: Texture2D

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
# Enemy crew (21 Nov): each has a station (cockpit, weapons, shields, engines; extras wait in the crew room),
# walks off to repair damaged rooms and back, and is hurt by hits on the room they're in.
# Each: {"home": station room, "room": room they're in ("" while walking), "target": room they're going to,
#        "pos": Vector2 in the enemy picture's pixels, "hp": float, "task": "station" or "repair"}
var e_crew_list: Array = []
var e_room_repair := {}          # room id -> seconds of repair work done on it
const CREW_SPEED := 22.0         # picture pixels a second
const CREW_HP := 100.0
const CREW_HIT := 15.0           # health lost per point of damage when a shot hits their room
const STATIONS := ["pilot", "weapons", "shields", "engines"]
const CREW_SPOTS := [Vector2(0, 0), Vector2(-7, -5), Vector2(7, 5), Vector2(-7, 5), Vector2(7, -5), Vector2(0, 6)]
var overcharged := false

var shots: Array = []            # shots in flight
var pops: Array = []             # floating words: {"pos", "text", "t", "color"}
var shake := 0.0
var hover := Vector2(-99, -99)
var tutorial_said := {}


func _ready() -> void:
	layer = 9                    # under the dialogue box (10), so story lines show over the battle
	scale = Vector2(2, 2)
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
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	for i in range(140):
		stars.append([Vector2(rng.randf() * W, rng.randf() * H), rng.randf_range(0.3, 0.9)])
	if ResourceLoader.exists(ShipData.STARTER["art"]):
		ship_tex = load(ShipData.STARTER["art"])


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
	var me: Dictionary = ShipData.STARTER
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
	var art_path := "res://art/ships/%s.png" % foe_id
	enemy_tex = load(art_path) if ResourceLoader.exists(art_path) else null
	open = true
	visible = true


func close() -> void:
	open = false
	visible = false
	on_end = Callable()


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
	view.queue_redraw()
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
	_pop(ENEMY_POS + Vector2(40, -4), "Hit his weapons to drain the cannon", GOLD)


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
	for room in ShipData.STARTER["rooms"]:
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
	var room: Dictionary = _room(ShipData.STARTER["rooms"], drone_room)
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


func _room_center(at_player: bool, id: String) -> Vector2:
	if at_player:
		var r: Rect2 = _room(ShipData.STARTER["rooms"], id).get("rect", Rect2(78, 43, 0, 0))
		return PLAYER_POS + r.get_center()
	var e: Rect2 = _room(foe["rooms"], id).get("rect", Rect2(40, 46, 0, 0))
	return ENEMY_POS + e.get_center()


func _fire(w: Dictionary, at_player: bool) -> void:
	var data: Dictionary = ShipData.WEAPONS[w["id"]]
	var target: String = str(w["target"])
	var from: Vector2 = _room_center(not at_player, "weapons")
	var to: Vector2 = _room_center(at_player, target)
	var dodge: int = _my_evasion() if at_player else _enemy_evasion()
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
	var where: Vector2 = s["to"]
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
		var room: Dictionary = _room(ShipData.STARTER["rooms"], room_id)
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
			for room in ShipData.STARTER["rooms"]:
				if str(room["sys"]) == sname:
					out.append(str(room["id"]))
	return out


func send_drone(room_id: String) -> void:
	if room_id == drone_goal and drone_path.size() > 0:
		return
	if room_id == drone_room and drone_path.is_empty():
		return
	var me: Dictionary = ShipData.STARTER
	var target: Dictionary = _room(me["rooms"], room_id)
	if target.is_empty():
		return
	drone_goal = room_id
	drone_work = 0.0
	drone_path = []
	if drone_room != "drones":
		drone_path.append(me["hub"])
	var r: Rect2 = target["rect"]
	drone_path.append(r.get_center())
	drone_room = ""


func _move_drone(delta: float) -> void:
	var slow: float = 0.5 if int(sys["drones"]["damage"]) > 0 else 1.0
	if drone_path.size() > 0:
		var next: Vector2 = drone_path[0]
		var step: float = ShipData.DRONE_SPEED * slow * delta
		if drone_pos.distance_to(next) <= step:
			drone_pos = next
			drone_path.pop_front()
			if drone_path.is_empty():
				drone_room = drone_goal
		else:
			drone_pos += (next - drone_pos).normalized() * step
		return
	var here: Dictionary = _room(ShipData.STARTER["rooms"], drone_room)
	var sname: String = str(here.get("sys", ""))
	if sname != "" and sys.has(sname) and int(sys[sname]["damage"]) > 0:
		drone_work += delta * slow
		if drone_work >= ShipData.DRONE_REPAIR_TIME:
			drone_work = 0.0
			sys[sname]["damage"] = int(sys[sname]["damage"]) - 1
			_pop(PLAYER_POS + drone_pos + Vector2(0, -6), "Fixed", GOOD)
			world.sfx("click", 1.6, -4.0)
			if int(sys[sname]["damage"]) == 0 and ShipData.DRONE_BOOST.has(sname):
				_pop(PLAYER_POS + drone_pos + Vector2(0, -14), "Boosting", GOLD)


# ---------------------------------------------------------------- enemy crew

func _sys_room(sname: String) -> String:
	for room in foe["rooms"]:
		if str(room["sys"]) == sname:
			return str(room["id"])
	return ""


func _spare_room() -> String:
	var r: String = _sys_room("")
	return r if r != "" else str(foe["rooms"][0]["id"])


# Where crew member i stands in a room: the middle, spread out a little, kept inside the room.
func _crew_spot(room_id: String, i: int) -> Vector2:
	var r: Rect2 = _room(foe["rooms"], room_id).get("rect", Rect2(40, 40, 10, 10))
	var p: Vector2 = r.get_center() + CREW_SPOTS[i % CREW_SPOTS.size()]
	return Vector2(clampf(p.x, r.position.x + 4, r.end.x - 4), clampf(p.y, r.position.y + 4, r.end.y - 4))


func _make_enemy_crew() -> void:
	e_crew_list.clear()
	e_room_repair.clear()
	for i in range(int(foe["crew"])):
		var home: String = ""
		if i < STATIONS.size():
			home = _sys_room(STATIONS[i])
		if home == "":
			home = _spare_room()
		e_crew_list.append({"home": home, "room": home, "target": home, "pos": _crew_spot(home, i), "hp": CREW_HP, "task": "station"})
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
		var goal: Vector2 = _crew_spot(str(c3["target"]), i)
		var at: Vector2 = c3["pos"]
		var step: float = CREW_SPEED * delta
		if at.distance_to(goal) > step:
			c3["pos"] = at + (goal - at).normalized() * step
			c3["room"] = ""
		else:
			c3["pos"] = goal
			c3["room"] = c3["target"]
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
		var room: Dictionary = _room(ShipData.STARTER["rooms"], str(hurt[0]))
		world._say("Sara", [
			"Your %s has been hit. A damaged bay shows red, and its system loses bars until it's mended." % str(room["label"]),
			"Your drone is your crew. Click the drone, then click the %s. It repairs whatever bay it's in." % str(room["label"]),
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
			if result == "":
				paused = not paused
				world.sfx("click")
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


func _on_gui_input(event: InputEvent) -> void:
	var motion := event as InputEventMouseMotion
	if motion != null:
		hover = motion.position
		return
	var click := event as InputEventMouseButton
	if click == null or not click.pressed:
		return
	view.accept_event()
	if world.dialogue.active:
		if click.button_index == MOUSE_BUTTON_LEFT:
			world.dialogue.advance()
		return
	if result != "":
		return
	var p: Vector2 = click.position
	var left: bool = click.button_index == MOUSE_BUTTON_LEFT
	var right: bool = click.button_index == MOUSE_BUTTON_RIGHT
	if not left and not right:
		return
	# buttons along the top
	if _jump_rect().has_point(p):
		_jump()
		return
	if _pause_rect().has_point(p):
		paused = not paused
		world.sfx("click")
		return
	if _auto_rect().has_point(p):
		autofire = not autofire
		world.sfx("click")
		return
	# power bars
	for i in range(REACTOR_SYS.size()):
		if _sys_rect(i).has_point(p):
			if left: _add_power(REACTOR_SYS[i])
			else: _remove_power(REACTOR_SYS[i])
			return
	# weapon cards
	for i in range(weapons.size()):
		if _weapon_rect(i).has_point(p):
			if left:
				_pick_weapon(i)
			elif str(weapons[i]["id"]) != "":
				weapons[i]["target"] = ""
				weapons[i]["on"] = false
				if selected == i: selected = -1
			return
	# the drone: click it (on the ship or in the Aboard list) to select it
	var dp: Vector2 = PLAYER_POS + drone_pos
	if left and (Rect2(dp - Vector2(6, 6), Vector2(12, 12)).has_point(p) or _drone_card_rect().has_point(p)):
		_select_drone()
		return
	# a bay on your ship: with the drone selected, send it there (left or right click, as with crew in FTL)
	for room in ShipData.STARTER["rooms"]:
		var r2: Rect2 = room["rect"]
		if Rect2(PLAYER_POS + r2.position, r2.size).has_point(p):
			if bool(room.get("crew", false)):
				if drone_selected: _pop(p, "Only you fit in here", DIM)
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
			var r: Rect2 = room["rect"]
			if Rect2(ENEMY_POS + r.position, r.size).has_point(p):
				weapons[selected]["target"] = str(room["id"])
				selected = -1
				world.sfx("click", 1.2)
				return


# ---------------------------------------------------------------- layout

func _jump_rect() -> Rect2: return Rect2(186, 4, 26, 11)
func _pause_rect() -> Rect2: return Rect2(124, 18, 42, 11)
func _auto_rect() -> Rect2: return Rect2(170, 18, 42, 11)
func _sys_rect(i: int) -> Rect2: return Rect2(24 + i * 24, 142, 20, 30)
func _weapon_rect(i: int) -> Rect2: return Rect2(124 + i * 56, 142, 52, 34)
func _drone_card_rect() -> Rect2: return Rect2(242, 160, 74, 11)


# ---------------------------------------------------------------- drawing

func _text(pos: Vector2, s: String, color: Color = WHITE, size: int = 8) -> void:
	view.draw_string(font, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)


func _text_c(center_x: float, y: float, s: String, color: Color = WHITE, size: int = 8) -> void:
	var w: float = font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	_text(Vector2(center_x - w / 2.0, y), s, color, size)


func _ellipse(center: Vector2, radii: Vector2, color: Color, width: float) -> void:
	view.draw_set_transform(center, 0.0, Vector2(1.0, radii.y / radii.x))
	view.draw_arc(Vector2.ZERO, radii.x, 0.0, TAU, 48, color, width)
	view.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _draw_view() -> void:
	var off := Vector2(randf_range(-1, 1), randf_range(-1, 1)) * (2.0 if shake > 0.0 else 0.0)
	# space and the gas giant
	view.draw_rect(Rect2(0, 0, W, H), Color("0a0c1a"))
	for s in stars:
		view.draw_rect(Rect2(s[0], Vector2.ONE), Color(1, 1, 1, float(s[1])))
	for i in range(8):
		view.draw_circle(Vector2(270, -70), 120.0 - i * 3.0, Color(0.16 + i * 0.02, 0.3 + i * 0.03, 0.55 + i * 0.03))
	_draw_player(off)
	if not (result == "won" and end_timer < 1.6) and result != "done":
		_draw_enemy()
	if result == "won":
		_draw_blast()
	for s in shots:
		var t: float = float(s["t"])
		if t < 0.0:
			continue
		var from: Vector2 = s["from"]
		var to: Vector2 = s["to"]
		var at: Vector2 = from.lerp(to, t)
		var dir: Vector2 = (to - from).normalized()
		view.draw_line(at - dir * (9.0 if bool(s["heavy"]) else 6.0), at, s["color"], 3.0 if bool(s["heavy"]) else 2.0)
	for p in pops:
		var c: Color = p["color"]
		c.a = 1.0 - float(p["t"]) / 1.2
		_text_c((p["pos"] as Vector2).x, (p["pos"] as Vector2).y - float(p["t"]) * 12.0, str(p["text"]), c, 8)
	_draw_top()
	_draw_bottom()
	if paused and result == "" and not world.dialogue.active:
		view.draw_rect(Rect2(110, 36, 100, 12), Color(0.98, 0.86, 0.35, 0.95))
		_text_c(160, 45, "PAUSED - Space to resume", Color("1e180a"))
	if result != "" and result != "done":
		view.draw_rect(Rect2(70, 76, 180, 16), Color(0.05, 0.06, 0.12, 0.92))
		_text_c(160, 87, result_text, GOOD if result == "won" else (BAD if result == "lost" else GOLD), 9)


func _draw_player(off: Vector2) -> void:
	var me: Dictionary = ShipData.STARTER
	var size: Vector2 = me["size"]
	var base: Vector2 = PLAYER_POS + off
	var bubble := 0.0
	if layers > 0:
		bubble = 0.55 + 0.2 * layers
	if bubble > 0.0:
		_ellipse(base + size / 2.0 + Vector2(6, 0), size / 2.0 + Vector2(8, 8), Color(SHIELD_BLUE, bubble), 1.0)
		if layers > 1:
			_ellipse(base + size / 2.0 + Vector2(6, 0), size / 2.0 + Vector2(12, 12), Color(Color("78f0ff"), 0.7), 1.0)
	if ship_tex != null:
		var fw: float = ship_tex.get_width() / float(me["frames"])
		view.draw_texture_rect_region(ship_tex, Rect2(base, size), Rect2(fw * int(me["frame"]), 0, fw, ship_tex.get_height()))
	else:
		view.draw_rect(Rect2(base + Vector2(36, 20), Vector2(110, 44)), Color("dcd8cc"))
	# ducts
	var hub: Vector2 = me["hub"]
	for room in me["rooms"]:
		if bool(room.get("crew", false)):
			continue
		var c: Vector2 = (room["rect"] as Rect2).get_center()
		var d: float = hub.distance_to(c)
		var n: int = int(d / 4.0)
		for i in range(n + 1):
			var q: Vector2 = hub.lerp(c, float(i) / maxf(1.0, float(n)))
			view.draw_rect(Rect2(base + q - Vector2(0.5, 0.5), Vector2.ONE), Color(1, 0.82, 0.35, 0.35))
	# rooms
	for room in me["rooms"]:
		var r: Rect2 = room["rect"]
		var rr := Rect2(base + r.position, r.size)
		var sname: String = room["sys"]
		var dmg: int = int(sys[sname]["damage"]) if sys.has(sname) else 0
		var fill := Color(0.92, 0.9, 0.86, 0.95) if bool(room.get("crew", false)) else Color(0.38, 0.4, 0.46, 0.9)
		if dmg > 0:
			fill = fill.lerp(Color("a0463c"), 0.65)
		view.draw_rect(rr, fill)
		view.draw_rect(rr, Color("282834"), false, 1.0)
		var label_col := Color("1e1e28") if bool(room.get("crew", false)) else Color(0.9, 0.9, 0.95, 0.9)
		_text(rr.position + Vector2(2, 7), str(room["label"]), label_col, 6)
		if sys.has(sname) and sname != "pilot":
			for i in range(int(sys[sname]["max"])):
				var on: bool = i < int(sys[sname]["max"]) - dmg
				view.draw_rect(Rect2(rr.position + Vector2(2 + i * 4, rr.size.y - 4), Vector2(3, 2)), GOOD if on else BAD)
		if drone_selected and rr.has_point(hover) and not bool(room.get("crew", false)) and result == "":
			view.draw_rect(rr, GOOD, false, 1.0)
	# you, in the cockpit
	var cockpit: Rect2 = _room(me["rooms"], "cockpit")["rect"]
	var you: Vector2 = base + cockpit.get_center() + Vector2(2, 2)
	view.draw_circle(you, 5.0, Color("ffc878"))
	view.draw_arc(you, 5.0, 0.0, TAU, 16, Color("201e28"), 1.0)
	# the drone
	var dp: Vector2 = base + drone_pos
	if drone_selected:
		view.draw_arc(dp, 6.0, 0.0, TAU, 16, GOOD, 1.0)
	view.draw_rect(Rect2(dp - Vector2(3, 3), Vector2(6, 6)), GOLD)
	view.draw_rect(Rect2(dp - Vector2(3, 3), Vector2(6, 6)), Color("282018"), false, 1.0)
	if drone_room != "" and drone_work > 0.0:
		view.draw_rect(Rect2(dp + Vector2(-5, -7), Vector2(10.0 * drone_work / ShipData.DRONE_REPAIR_TIME, 2)), GOOD)


func _draw_enemy() -> void:
	var base: Vector2 = ENEMY_POS
	var size: Vector2 = foe["size"]
	if e_layers > 0:
		_ellipse(base + size / 2.0, size / 2.0 + Vector2(10, 10), Color(SHIELD_BLUE, 0.8), 1.0)
	if enemy_tex != null:
		view.draw_texture_rect(enemy_tex, Rect2(base, size), false)
	else:
		for fin in foe["fins"]:
			var pts := PackedVector2Array()
			for v in fin:
				pts.append(base + v)
			view.draw_colored_polygon(pts, Color(foe["hull_color"]).lightened(0.15))
		var shape := PackedVector2Array()
		for v in foe["shape"]:
			shape.append(base + v)
		view.draw_colored_polygon(shape, foe["hull_color"])
		shape.append(shape[0])
		view.draw_polyline(shape, Color("241818"), 1.0)
		view.draw_line(base + Vector2(30, size.y / 2.0), base + Vector2(size.x - 10, size.y / 2.0), foe["trim"], 2.0)
	for room in foe["rooms"]:
		var r: Rect2 = room["rect"]
		var rr := Rect2(base + r.position, r.size)
		var sname: String = room["sys"]
		var dmg: int = int(e_sys[sname]["damage"]) if e_sys.has(sname) else 0
		var fill := Color(0.69, 0.59, 0.53, 0.92)
		if dmg > 0:
			fill = fill.lerp(Color("a0463c"), 0.6)
		view.draw_rect(rr, fill)
		view.draw_rect(rr, Color("32221e"), false, 1.0)
		_text(rr.position + Vector2(2, 7), str(room["label"]), Color("281814"), 6)
		if e_sys.has(sname) and sname != "pilot":
			for i in range(int(e_sys[sname]["max"])):
				var on: bool = i < int(e_sys[sname]["max"]) - dmg
				view.draw_rect(Rect2(rr.position + Vector2(2 + i * 4, rr.size.y - 4), Vector2(3, 2)), GOOD if on else BAD)
		if selected >= 0 and rr.has_point(hover):
			view.draw_rect(rr, BAD, false, 1.0)
	# their crew: red at stations, orange when repairing, a health bar once hurt
	for c in e_crew_list:
		var cpos: Vector2 = base + (c["pos"] as Vector2)
		if float(c["hp"]) <= 0.0:
			view.draw_line(cpos + Vector2(-2, -2), cpos + Vector2(2, 2), Color("5a4a48"), 1.0)
			view.draw_line(cpos + Vector2(-2, 2), cpos + Vector2(2, -2), Color("5a4a48"), 1.0)
			continue
		view.draw_circle(cpos, 3.0, Color("f0a040") if str(c["task"]) == "repair" else Color("e65a50"))
		view.draw_arc(cpos, 3.0, 0.0, TAU, 12, Color("201010"), 1.0)
		if float(c["hp"]) < CREW_HP:
			view.draw_rect(Rect2(cpos + Vector2(-4, -6), Vector2(8, 1)), Color("3c2020"))
			view.draw_rect(Rect2(cpos + Vector2(-4, -6), Vector2(8.0 * float(c["hp"]) / CREW_HP, 1)), GOOD)
	# where your weapons are aimed
	for i in range(weapons.size()):
		var tid: String = str(weapons[i]["target"])
		if tid == "":
			continue
		var c: Vector2 = _room_center(false, tid)
		view.draw_arc(c, 6.0 + i * 2.0, 0.0, TAU, 20, BAD, 1.0)
		view.draw_line(c + Vector2(-9, 0), c + Vector2(9, 0), BAD, 1.0)
		view.draw_line(c + Vector2(0, -9), c + Vector2(0, 9), BAD, 1.0)
		_text(c + Vector2(8, -6), str(i + 1), BAD, 7)


func _draw_blast() -> void:
	var size: Vector2 = foe["size"]
	var c: Vector2 = ENEMY_POS + size / 2.0
	var t: float = clampf(1.0 - (end_timer - 0.2) / 2.0, 0.0, 1.0)
	for i in range(4):
		var r: float = (10.0 + i * 12.0) * t * 1.6
		view.draw_circle(c + Vector2(i * 7 - 10, (i % 2) * 8 - 4), r * 0.6, Color(1.0, 0.7 - i * 0.12, 0.2, maxf(0.0, 0.9 - t)))
	for i in range(10):
		var a: float = i * TAU / 10.0
		view.draw_rect(Rect2(c + Vector2(cos(a), sin(a)) * 70.0 * t, Vector2(3, 2)), Color(0.6, 0.5, 0.45, maxf(0.0, 1.0 - t)))


func _bar(pos: Vector2, n: int, filled: int, color: Color) -> void:
	for i in range(n):
		view.draw_rect(Rect2(pos + Vector2(i * 5, 0), Vector2(4, 7)), color if i < filled else Color("3c3c46"))


func _draw_top() -> void:
	# yours
	view.draw_rect(Rect2(2, 2, 116, 34), PANEL)
	_text(Vector2(5, 10), "HULL", WHITE, 7)
	_bar(Vector2(26, 4), hull_max, hull, BAD if hull * 3 <= hull_max else GOOD)
	_text(Vector2(5, 21), "SHIELD", WHITE, 7)
	for i in range(_max_layers()):
		var c := Vector2(36 + i * 10, 18)
		view.draw_circle(c, 3.5, SHIELD_BLUE if i < layers else Color("283c5a"))
		view.draw_arc(c, 3.5, 0.0, TAU, 12, Color("c8e6ff"), 1.0)
	if uplink:
		_text(Vector2(58, 21), "S.A.R.A. uplink", Color("78f0ff"), 6)
	_text(Vector2(5, 32), "Evasion %d%%   Oxygen %d%%" % [_my_evasion(), int(oxygen)], DIM if oxygen > 40 else BAD, 7)
	# fold drive, pause, autofire
	view.draw_rect(Rect2(122, 2, 94, 30), PANEL)
	_text(Vector2(125, 10), "FOLD DRIVE", WHITE, 7)
	view.draw_rect(Rect2(125, 12, 58, 3), Color("283046"))
	view.draw_rect(Rect2(125, 12, 58.0 * fold / 100.0, 3), Color("78c8ff"))
	var jr := _jump_rect()
	var can_jump: bool = fold >= 100.0 and not bool(fight.get("story", false))
	view.draw_rect(jr, Color("4664a0") if can_jump else Color("323646"))
	_text_c(jr.get_center().x, jr.position.y + 8, "JUMP", WHITE if can_jump else DIM, 7)
	var pr := _pause_rect()
	view.draw_rect(pr, Color("323646"))
	_text_c(pr.get_center().x, pr.position.y + 8, "Resume" if paused else "Pause", WHITE, 7)
	var ar := _auto_rect()
	view.draw_rect(ar, Color("3c5a3c") if autofire else Color("323646"))
	_text_c(ar.get_center().x, ar.position.y + 8, "Autofire %s" % ("on" if autofire else "off"), WHITE, 6)
	# theirs
	view.draw_rect(Rect2(220, 2, 98, 36), Color(0.14, 0.08, 0.1, 0.92))
	_text(Vector2(223, 10), str(foe["name"]), Color("ffbeaa"), 7)
	_bar(Vector2(223, 13), e_hull_max, e_hull, GOOD)
	for i in range(_layers_of(e_sys)):
		var c2 := Vector2(226 + i * 10, 26)
		view.draw_circle(c2, 3.5, SHIELD_BLUE if i < e_layers else Color("283c5a"))
	_text(Vector2(250, 29), "Evasion %d%%  Crew %d" % [_enemy_evasion(), e_crew], DIM, 6)
	if overcharged:
		for w in e_weapons:
			if str(w["id"]) == "ivan_cannon":
				var full: float = float(ShipData.WEAPONS["ivan_cannon"]["charge"])
				view.draw_rect(Rect2(223, 32, 92, 3), Color("3c2a1e"))
				view.draw_rect(Rect2(223, 32, 92.0 * float(w["charge"]) / full, 3), GOLD)


func _draw_bottom() -> void:
	# reactor and systems
	view.draw_rect(Rect2(2, 138, 118, 40), PANEL)
	_text(Vector2(4, 146), "PWR", WHITE, 6)
	var spare: int = spare_power()
	for i in range(reactor):
		view.draw_rect(Rect2(6, 170 - i * 4, 10, 3), GOOD if i < spare else Color("2c3040"))
	for k in range(REACTOR_SYS.size()):
		var key: String = REACTOR_SYS[k]
		var r := _sys_rect(k)
		var s: Dictionary = sys[key]
		for i in range(int(s["max"])):
			var col := Color("2c3040")
			if i >= int(s["max"]) - int(s["damage"]):
				col = BAD
			elif i < int(s["power"]):
				col = GOOD
			view.draw_rect(Rect2(r.position.x + 3, 164 - i * 5, 14, 4), col)
		if r.has_point(hover):
			view.draw_rect(r, Color(1, 1, 1, 0.25), false, 1.0)
		_text_c(r.get_center().x, 176, str(SYS_LABEL[key]), WHITE, 6)
	# weapons
	view.draw_rect(Rect2(122, 138, 116, 40), PANEL)
	for i in range(weapons.size()):
		var r := _weapon_rect(i)
		var w: Dictionary = weapons[i]
		if str(w["id"]) == "":
			view.draw_rect(r, Color("1e2030"))
			view.draw_rect(r, Color("3c4050"), false, 1.0)
			_text(r.position + Vector2(3, 9), "Empty slot", DIM, 7)
			_text(r.position + Vector2(3, 18), "buy or salvage", DIM, 6)
			continue
		var data: Dictionary = ShipData.WEAPONS[w["id"]]
		var ready: bool = float(w["charge"]) >= float(data["charge"])
		view.draw_rect(r, Color("2c3246") if bool(w["on"]) else Color("1e2030"))
		view.draw_rect(r, GOLD if selected == i else (Color("8a90a8") if ready else Color("3c4050")), false, 1.0)
		_text(r.position + Vector2(3, 9), "%d  %s" % [i + 1, str(data["name"])], WHITE, 7)
		var status := "off (left-click)"
		if bool(w["on"]):
			status = "aim: click a room" if selected == i else ("READY" if ready else "charging")
			if str(w["target"]) != "" and selected != i:
				status = "aimed"
		_text(r.position + Vector2(3, 19), status, GOLD if ready else DIM, 6)
		view.draw_rect(Rect2(r.position + Vector2(3, 26), Vector2(46, 3)), Color("283046"))
		view.draw_rect(Rect2(r.position + Vector2(3, 26), Vector2(46.0 * float(w["charge"]) / float(data["charge"]), 3)), GOLD if ready else Color("78c8ff"))
	# who is aboard
	view.draw_rect(Rect2(240, 138, 78, 40), PANEL)
	_text(Vector2(243, 146), "ABOARD", WHITE, 6)
	view.draw_circle(Vector2(248, 154), 3.5, Color("ffc878"))
	_text(Vector2(254, 157), "You: pilot", WHITE, 6)
	var card := _drone_card_rect()
	if drone_selected:
		view.draw_rect(card, Color(0.35, 0.86, 0.43, 0.25))
	view.draw_rect(Rect2(245, 162, 6, 6), GOLD)
	var drone_note := "idle"
	if drone_selected:
		drone_note = "pick a bay"
	elif drone_path.size() > 0:
		drone_note = "moving"
	elif drone_work > 0.0:
		drone_note = "repairing"
	else:
		for sname in ShipData.DRONE_BOOST:
			if _boosting(sname):
				drone_note = "boosting %s" % sname
	_text(Vector2(254, 168), "Drone: %s" % drone_note, WHITE, 6)
	_text(Vector2(243, 176), "Space pause  D drone", DIM, 6)
