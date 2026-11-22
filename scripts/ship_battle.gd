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
const REPAIR_ORDER := ["shields", "weapons", "cannon", "pilot", "engines", "life", "drones"]
const INK := Color("373b36")          # as ui/ship_screen.gd
const MUTED := Color("595e55")          # as ui/ship_screen.gd
const OCHRE := Color("a45736")          # as ui/ship_screen.gd
const ORANGE := Color("ac5c36")          # as ui/ship_screen.gd
const DIM := Color("969cb0")
const GOLD := Color("fadc5a")
const GOOD := Color("5adc6e")
const BAD := Color("e6463c")
const SHIELD_BLUE := Color("5ab4ff")
# The shield bubble, FTL-style (Zachary, 21 Nov: "instead of a blue line an actual bubble"): see-through blue with a
# faint hex pattern that thickens toward the edge and a bright rim, over the ship; a ripple where a shot is blocked.
var shield_texes := {}          # bubble pictures by size, made once
# Weapons (Zachary, 21 Nov: lasers, missiles and beams): each gun drawn on its mount from art/ships/weapons/<id>.png,
# six frames (idle, charging 1 and 2, ready, firing 1 and 2; tools/dev/ship_art/weapons2x.py), missiles from
# art/ships/shots/missile.png, and beams cutting a line across rooms.
var weapon_texes := {}
var missile_tex: Texture2D
var beams: Array = []            # {"at_player", "from", "a", "b" (target picture px), "t", "dmg", "color", "hit", "rooms"}
const BEAM_TIME := 0.9
# Crew sprites, FTL-style (Zachary, 21 Nov: "mini people sprites like ftl and player in a space suit"):
# art/ships/crew/<kind>.png, 48 x 48 frames (tools/dev/ship_art/crew2x.py), rows: walk down, up, right (left is right
# mirrored), idle, typing at a console facing up, right, down, repairing, knocked out, fighting, putting out a fire.
# Who crews which ship:
var crew_texes := {}
const CREW_KIND := {"terran_patrol": "terran_marine", "zaash_skiff": "zaash", "vuultam_garden": "vuultam",
	"moogli_trader": "moogli", "ervani_courier": "ervani", "scyldar_lantern": "scyldar", "arachnay_weaver": "arachnay",
	"collective_freighter": ["vuultam", "moogli", "ervani", "scyldar", "arachnay"]}
const CREW_ROW := {"walk_down": 0, "walk_up": 1, "walk_right": 2, "idle": 3, "work_up": 4, "work_right": 5, "work_down": 6,
	"repair": 7, "down": 8, "fight": 9, "extinguish": 10}
# Hazards from the rare weapons: rooms on fire and rooms full of gas, by room id: {"t": seconds left, "acc"}.
var my_fires := {}
var foe_fires := {}
var foe_gas := {}
var shield_jam := 0.0            # ion on your shields: they don't come back while this runs
var e_shield_jam := 0.0
const FIRE_TIME := 12.0          # a fire left alone burns this long
const FIRE_HURT := 3.0           # seconds of burning for each bar of damage to the room's system
const FIRE_CREW := 6.0           # crew health lost a second in a burning room
const GAS_CREW := 12.0           # ... and in a gassed one
const SHIELD_JAM := 4.0
# Air, room by room (Zachary, 22 Nov: "every ship need 1 or 2 airlocks to vent air for fires"), 0..1 by room id.
# Life support fills every room; open doors even it out; an open airlock (a striped hatch to space) empties its room.
# Fire eats air and dies fast without it; crew choke in thin air. You have your suit: when the cockpit runs out, it
# holds SUIT_AIR seconds.
var my_air := {}
var foe_air := {}
var suit_air := 25.0
const SUIT_AIR := 25.0
const AIR_REFILL := 0.04         # a second, for each bar of life support
const AIR_LEAK := 0.012          # a second, in every room, with life support down
const AIR_VENT := 0.35           # a second, out through an open airlock
const AIR_MIX := 1.5             # how fast two rooms with an open door between them even out
const AIR_BURN := 0.03           # a fire eats this much a second
const AIR_THIN := 0.15           # below this, crew choke ...
const AIR_CHOKE := 5.0           # ... losing this much health a second
const FIRE_SPREAD := 8.0         # a fire with air to burn reaches the next room this often (open doors; shut ones 1 in 3)
# Effects (tools/dev/ship_art/fx2x.py): fire and smoke loop over burning rooms, 48 x 48 a cell, 4 frames; a hit is a
# 6-frame blast where a shot lands.
var fx_fire: Texture2D
var fx_smoke: Texture2D
var fx_hit: Texture2D
var blasts: Array = []           # {"pos" (page), "t", "k"}
const BLAST_FRAME := 0.07
const GUN_FRAME := {"small": Vector2(64, 24), "big": Vector2(96, 32)}
const GUN_MOUNT := {"small": Vector2(6, 12), "big": Vector2(8, 16)}
var shield_hits: Array = []      # {"mine", "pos" (page), "t"}
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
# Breaking up, FTL-style (Zachary, 21 Nov): an enemy blown apart splits into pieces with its insides showing
# (art/ships/<id>/gib_N.png, tools/dev/ship_art/gibs2x.py) that drift apart and spin; when you're beaten, bits break
# off your fighter (chip_N.png, interior_broken.png) and it makes an emergency jump home. The fold jump streaks too.
var foe_gibs: Array = []         # {"tex", "c": its middle in art px, "dir", "spin"}
var my_chips: Array = []
var broken_tex: Texture2D
var break_t := -1.0              # seconds since the enemy broke up (-1: it hasn't)
var lose_t := -1.0               # seconds since your ship was beaten
var jump_t := -1.0               # seconds since your ship started its jump (emergency or fold)
const BREAK_FLASH := 0.45        # the ship flashes with blasts this long before it splits
const JUMP_AT := 2.1             # when beaten: bits break off, the drive charges, then this many seconds in it jumps
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
const STATIONS := ["pilot", "weapons", "shields", "engines", "cannon"]
# System icons, FTL-style (Zachary, 21 Nov): art/ui/ship/icons_systems.png, 32 x 32 each in this order
# (tools/dev/ship_art/icons2x.py). They mark each system's room (16 x 16 cell pixels, in the middle) and sit under
# its power bars on the system bar: green powered, grey off, red damaged.
const ROOM_ICONS := ["shields", "engines", "weapons", "life", "pilot", "drones", "cannon", "medbay", "crew", "doors", "sensors"]
const ICON_POWERED := Color("78d46a")
const ICON_ION := Color("5ac8ff")
const ICON_OK := Color("8a8590")
const ICON_HIT := Color("e0503c")
var room_icons: Texture2D
const CREW_SPOTS := [Vector2(0, 0), Vector2(-7, -5), Vector2(7, 5), Vector2(-7, 5), Vector2(7, -5), Vector2(0, 6)]
var overcharged := false

var shots: Array = []            # shots in flight, in ship-picture pixels: {"from", "to", "t", "at_player", ...}
var pops: Array = []             # floating words, in page pixels: {"pos", "text", "t", "color"}
var shake := 0.0
var tutorial_said := {}
static var fire_hint_said := false   # Sara explains fire and airlocks the first time your ship burns (once a session)


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
	room_icons = _load_tex("res://art/ui/ship/icons_systems.png")
	missile_tex = _load_tex("res://art/ships/shots/missile.png")
	fx_fire = _load_tex("res://art/ships/fx/fire.png")
	fx_smoke = _load_tex("res://art/ships/fx/smoke.png")
	fx_hit = _load_tex("res://art/ships/fx/hit.png")
	for kind in ["player", "human", "freya", "ana", "rabble_pirate", "terran_marine", "zaash", "arachnay", "moogli", "ervani", "vuultam", "scyldar"]:
		var ct: Texture2D = _load_tex("res://art/ships/crew/%s.png" % kind)
		if ct != null:
			crew_texes[kind] = ct
	for wid in ShipData.WEAPONS:
		var tex: Texture2D = _load_tex("res://art/ships/weapons/%s.png" % wid)
		if tex != null:
			weapon_texes[wid] = tex
	broken_tex = _load_tex(str(ShipData.STARTER.get("interior", "")).replace("interior.png", "interior_broken.png"))
	my_chips = _pieces(str(ShipData.STARTER["art"]).replace("hull.png", "chip_%d.png"), ShipData.STARTER)


# ---------------------------------------------------------------- starting and ending

# fight: {"enemy": id, "story": bool, "uplink": bool, "tutorial": bool}. hull_now: your hull coming in.
func start(new_fight: Dictionary, cb: Callable, hull_now: int) -> void:
	fight = new_fight
	on_end = cb
	result = ""
	result_text = ""
	paused = false
	shots.clear()
	beams.clear()
	my_fires.clear()
	foe_fires.clear()
	foe_gas.clear()
	shield_jam = 0.0
	e_shield_jam = 0.0
	shield_hits.clear()
	pops.clear()
	selected = -1
	fold = 0.0
	oxygen = 100.0
	suit_air = SUIT_AIR
	blasts.clear()
	tutorial_said = {}
	me_ship = ShipData.build(ShipData.STARTER)
	_fill_air(me_ship, my_air)
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
	_fill_air(foe, foe_air)
	_make_enemy_crew()
	overcharged = false
	enemy_tex = _load_tex(str(foe.get("art", "")))
	enemy_inside = _load_tex(str(foe.get("interior", "")))
	var art: String = str(foe.get("art", ""))
	foe_gibs = _pieces(art.get_basename().replace("hull", "gib") + "_%d.png", foe) if art != "" else []
	break_t = -1.0
	lose_t = -1.0
	jump_t = -1.0
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
		out[key] = {"max": int(pair[0]), "power": int(pair[1]), "damage": 0, "ion": 0.0}
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
	if e_hull <= 0 and not foe_gibs.is_empty():
		break_t = 0.0                # it breaks apart (a ship won by downing its crew stays whole)
		end_timer = 3.0
	world.sfx("die", 0.6)


func _lose(why: String) -> void:
	if result != "": return
	result = "lost"
	result_text = why
	end_timer = JUMP_AT + 1.2
	lose_t = 0.0
	shake = 1.4
	world.sfx("die")


func _jump() -> void:
	if result != "" or fold < 100.0 or bool(fight.get("story", false)): return
	result = "fled"
	result_text = "Fold jump: heading home"
	end_timer = 1.2
	jump_t = 0.0
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
	for h in shield_hits:
		h["t"] = float(h["t"]) + delta
	shield_hits = shield_hits.filter(func(h): return float(h["t"]) < 0.5)
	for b in blasts:
		b["t"] = float(b["t"]) + delta
	blasts = blasts.filter(func(b): return float(b["t"]) < BLAST_FRAME * 6.0)
	if world.dialogue.active:
		return
	if result == "done":
		return
	if result != "":
		end_timer -= delta
		if break_t >= 0.0:
			break_t += delta
		if lose_t >= 0.0:
			lose_t += delta
			if lose_t >= JUMP_AT and jump_t < 0.0:
				jump_t = 0.0
				world.sfx("warp")
		if jump_t >= 0.0:
			jump_t += delta
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
	shield_jam = maxf(0.0, shield_jam - delta)
	e_shield_jam = maxf(0.0, e_shield_jam - delta)
	for systems in [sys, e_sys]:
		for key in systems:
			systems[key]["ion"] = maxf(0.0, float(systems[key].get("ion", 0.0)) - delta)
	_tick_hazards(delta)
	if layers < top and shield_jam <= 0.0:
		shield_timer += delta
		if shield_timer >= ShipData.SHIELD_RECHARGE * (0.75 if _boosting("shields") else 1.0):
			shield_timer = 0.0
			layers += 1
	else:
		shield_timer = 0.0
	var e_top := _layers_of(e_sys)
	if e_layers > e_top: e_layers = e_top
	if e_layers < e_top and e_shield_jam <= 0.0:
		e_shield_timer += delta
		if e_shield_timer >= ShipData.SHIELD_RECHARGE * (0.9 if _manned("shields") else 1.0):
			e_shield_timer = 0.0
			e_layers += 1
	else:
		e_shield_timer = 0.0

	_charge_weapons(weapons, sys, delta, true)
	_charge_weapons(e_weapons, e_sys, delta, false)
	for w in weapons + e_weapons:
		w["fired"] = maxf(0.0, float(w.get("fired", 0.0)) - delta)
	_move_shots(delta, true)
	_move_beams(delta)
	_move_drone(delta)
	_enemy_crew(delta)
	_tick_doors(me_ship, delta)
	_tick_doors(foe, delta)

	_tick_air(true, delta)
	_tick_air(false, delta)
	_breathe(delta)
	if result != "":
		return

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
	_pop(_on_page(false, Vector2((foe["size"] as Vector2).x / 2.0, 0)), "Hit his cannon room to drain the cannon" if e_sys.has("cannon") else "Hit his weapons to drain the cannon", GOLD)


func _charge_weapons(list: Array, systems: Dictionary, delta: float, mine: bool) -> void:
	var budget: int = _eff(systems, "weapons")
	for w in list:
		if str(w["id"]) == "":
			continue
		var data: Dictionary = ShipData.WEAPONS[w["id"]]
		var cost: int = int(data["power"])
		var powered: bool = bool(w["on"]) and cost <= budget
		var full: float = _full_charge(w, data)
		if powered:
			budget -= cost
			var speed: float = 1.0
			if mine and _boosting("weapons"):
				speed = 1.15
			elif not mine and _manned("weapons"):
				speed = 1.1
			# Ivan's cannon runs off its own room: crewed it charges faster, damaged it can't charge at all
			if not mine and e_sys.has("cannon") and str(w["id"]) == "ivan_cannon":
				speed = 0.0 if _eff(e_sys, "cannon") <= 0 else (1.1 if _manned("cannon") else 1.0)
			w["charge"] = minf(full, float(w["charge"]) + delta * speed)
		else:
			w["charge"] = maxf(0.0, float(w["charge"]) - delta * 2.0)
			w["chain_n"] = 0
		var loaded: int = _loaded(w, data)
		if not powered or loaded <= 0:
			continue
		var stages: int = int(data.get("stages", 1))
		if mine:
			if str(w["target"]) == "":
				continue
			# a twin missile aimed before anything was loaded waits for both
			if loaded < mini(int(w.get("want", stages)), stages):
				continue
			if int(data.get("ammo", 0)) > 0 and int(world.missiles) < int(data["ammo"]):
				continue                 # charged, but no missiles left to fire
			_fire(w, false)
			if not autofire:
				w["target"] = ""
		else:
			if loaded < stages:
				continue
			w["target"] = _enemy_pick_room()
			_fire(w, true)
		w["charge"] = 0.0
		w["want"] = stages
		if data.has("chain"):
			w["chain_n"] = mini(2, int(w.get("chain_n", 0)) + 1)


# How much charge a weapon fires at: a twin missile holds two loads; a chain laser needs less after each volley.
func _full_charge(w: Dictionary, data: Dictionary) -> float:
	var c: float = float(data["charge"])
	if data.has("stages"):
		return c * int(data["stages"])
	if data.has("chain"):
		c *= 1.0 - float(data["chain"]) * int(w.get("chain_n", 0))
	return c


# How many shots' worth are loaded: up to "stages" for a twin missile, otherwise 1 when charged.
func _loaded(w: Dictionary, data: Dictionary) -> int:
	if data.has("stages"):
		return mini(int(data["stages"]), floori(float(w["charge"]) / float(data["charge"]) + 0.0001))
	return 1 if float(w["charge"]) >= _full_charge(w, data) - 0.0001 else 0


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
	if float(s.get("ion", 0.0)) > 0.0:
		return 0                     # shut off by ion
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
	var kind: String = str(data.get("type", "laser"))
	w["fired"] = 0.3
	var volleys: int = maxi(1, _loaded(w, data)) if data.has("stages") else 1
	if not at_player and int(data.get("ammo", 0)) > 0:
		volleys = mini(volleys, int(world.missiles) / int(data["ammo"]))
		world.missiles = maxi(0, int(world.missiles) - int(data["ammo"]) * volleys)
	if kind == "beam":
		# a cut across the target room, tilted a little from up-and-down
		var dir := Vector2.DOWN.rotated(randf_range(-0.6, 0.6))
		var half: float = float(data.get("length", 40.0)) / 2.0
		beams.append({"at_player": at_player, "from": from, "a": to - dir * half, "b": to + dir * half, "t": -0.15,
			"dmg": int(data["damage"]), "color": data["color"], "hit": randf() * 100.0 >= dodge, "rooms": {}, "said": false,
			"fire": bool(data.get("fire", false))})
		world.sfx("zap", 0.6, -2.0)
		return
	# from and to are ship-picture pixels: from on the firing ship, to on the target.
	var rooms: Array = (me_ship if at_player else foe)["rooms"]
	for i in range(int(data["shots"]) * volleys):
		var room_id: String = target
		var aim: Vector2 = to
		if kind == "flak":
			# each shard lands on a room near the target
			var near: Array = []
			for room in rooms:
				if (room["rect"] as Rect2).get_center().distance_to(to) <= 40.0:
					near.append(room)
			if not near.is_empty():
				var pick: Dictionary = near[randi() % near.size()]
				room_id = str(pick["id"])
				aim = (pick["rect"] as Rect2).get_center()
		shots.append({"from": from, "to": aim + Vector2(randf_range(-3, 3), randf_range(-3, 3)),
			"t": -0.3 * i, "dmg": int(data["damage"]), "at_player": at_player, "room": room_id, "kind": kind,
			"ion": float(data.get("ion", 0.0)), "gas": float(data.get("gas", 0.0)),
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
	var missile: bool = str(s.get("kind", "")) == "missile"
	var kind: String = str(s.get("kind", ""))
	if kind == "ion":
		_ion_hit(at_player, str(s["room"]), float(s["ion"]), where)
		return
	if at_player and layers > 0 and not missile:
		layers -= 1
		shield_timer = 0.0
		_pop(where + Vector2(-10, 0), "Blocked", SHIELD_BLUE)
		shield_hits.append({"mine": true, "pos": _shield_edge(true, where), "t": 0.0})
		world.sfx("click", 0.6)
		return
	if not at_player and e_layers > 0 and not missile:
		e_layers -= 1
		e_shield_timer = 0.0
		_pop(where + Vector2(10, 0), "Blocked", SHIELD_BLUE)
		shield_hits.append({"mine": false, "pos": _shield_edge(false, where), "t": 0.0})
		return
	if kind == "poison":
		if at_player:
			_pop(where, "Gas! Your suit holds", Color("b6ff8a"))
		else:
			foe_gas[str(s["room"])] = {"t": float(s["gas"])}
			_pop(where, "Gas!", Color("b6ff8a"))
		return
	_damage(at_player, str(s["room"]), int(s["dmg"]), where)


# A hit on a room: hull, the room's system, its crew. at_player: the hit is on you.
func _damage(at_player: bool, room_id: String, dmg: int, where: Vector2) -> void:
	if result != "" or dmg <= 0:
		return
	blasts.append({"pos": where, "t": 0.0, "k": _ship_scale(at_player)})
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
		if sname2 == ("cannon" if e_sys.has("cannon") else "weapons") and overcharged:
			for w in e_weapons:
				if str(w["id"]) == "ivan_cannon" and float(w["charge"]) > 0.0:
					w["charge"] = 0.0
					_pop(where + Vector2(0, -8), "Cannon drained!", GOLD)
		_pop(where, "-%d" % dmg, GOLD)
		world.sfx("hit")
		if e_hull <= 0:
			e_hull = 0
			_win()


# Beams sweep their line; each room the line crosses takes the damage once, less one per shield layer (shields
# aren't knocked down). A dodged beam misses altogether.
func _move_beams(delta: float) -> void:
	var left: Array = []
	for bm in beams:
		bm["t"] = float(bm["t"]) + delta / BEAM_TIME
		var t: float = float(bm["t"])
		if t >= 0.0 and t <= 1.0 and result == "":
			var at_player: bool = bm["at_player"]
			var p: Vector2 = (bm["a"] as Vector2).lerp(bm["b"], t)
			var where: Vector2 = _on_page(at_player, p)
			if not bool(bm["hit"]):
				if not bool(bm["said"]):
					_pop(where, "Miss", DIM)
					bm["said"] = true
			else:
				for room in (me_ship if at_player else foe)["rooms"]:
					var rid: String = str(room["id"])
					if (room["rect"] as Rect2).has_point(p) and not (bm["rooms"] as Dictionary).has(rid):
						bm["rooms"][rid] = true
						var shield: int = layers if at_player else e_layers
						var dmg: int = int(bm["dmg"]) - shield
						if shield >= maxi(1, int(bm["dmg"])):
							if not bool(bm["said"]):
								_pop(where, "Blocked", SHIELD_BLUE)
								shield_hits.append({"mine": at_player, "pos": _shield_edge(at_player, where), "t": 0.0})
								bm["said"] = true
						else:
							_damage(at_player, rid, dmg, where)
							if bool(bm.get("fire", false)):
								_set_fire(at_player, rid, where)
		if t < 1.25:
			left.append(bm)
	beams = left


# Ion: on shields, knocks off a layer and jams them for a moment; with shields down, shuts the room's system off.
func _ion_hit(at_player: bool, room_id: String, secs: float, where: Vector2) -> void:
	var ion_col := Color("8adcff")
	if at_player and layers > 0:
		layers -= 1
		shield_timer = 0.0
		shield_jam = SHIELD_JAM
		shield_hits.append({"mine": true, "pos": _shield_edge(true, where), "t": 0.0})
		_pop(where, "Shields jammed", ion_col)
		return
	if not at_player and e_layers > 0:
		e_layers -= 1
		e_shield_timer = 0.0
		e_shield_jam = SHIELD_JAM
		shield_hits.append({"mine": false, "pos": _shield_edge(false, where), "t": 0.0})
		_pop(where, "Shields jammed", ion_col)
		return
	var systems: Dictionary = sys if at_player else e_sys
	var sname: String = str(_room((me_ship if at_player else foe)["rooms"], room_id).get("sys", ""))
	if systems.has(sname):
		systems[sname]["ion"] = secs
		_pop(where, "Ion! %s off" % sname.capitalize(), ion_col)
	else:
		_pop(where, "Ion: nothing to jam", DIM)


func _set_fire(at_player: bool, room_id: String, where: Vector2) -> void:
	var fires: Dictionary = my_fires if at_player else foe_fires
	if not fires.has(room_id):
		_pop(where + Vector2(0, -10), "Fire!", Color("ffb04a"))
	fires[room_id] = {"t": FIRE_TIME, "acc": 0.0}


# Fires burn: they damage the room's system a bar at a time and hurt the crew there, until they burn out or are put
# out (their crew working in the room, or your drone in the bay, puts it out faster). Gas hurts the crew in its room.
func _tick_hazards(delta: float) -> void:
	for at_player in [true, false]:
		var fires: Dictionary = my_fires if at_player else foe_fires
		var systems: Dictionary = sys if at_player else e_sys
		var ship: Dictionary = me_ship if at_player else foe
		for rid in fires.keys():
			var f: Dictionary = fires[rid]
			var workers := 0
			if at_player:
				workers = 1 if drone_room == rid and drone_path.is_empty() else 0
			else:
				for c in e_crew_list:
					if float(c["hp"]) > 0.0 and str(c["room"]) == rid:
						workers += 1
						c["hp"] = maxf(0.0, float(c["hp"]) - FIRE_CREW * delta)
			var air: Dictionary = my_air if at_player else foe_air
			var breath: float = float(air.get(rid, 1.0))
			# with almost no air left a fire chokes out five times as fast (venting the room)
			f["t"] = float(f["t"]) - delta * (1.0 + 3.0 * workers) * (5.0 if breath < 0.12 else 1.0)
			f["acc"] = float(f["acc"]) + delta
			f["spread"] = float(f.get("spread", 0.0)) + delta
			if float(f["spread"]) >= FIRE_SPREAD:
				f["spread"] = 0.0
				if breath > 0.4:
					_spread_fire(at_player, ship, rid)
			var sname: String = str(_room(ship["rooms"], rid).get("sys", ""))
			if float(f["acc"]) >= FIRE_HURT:
				f["acc"] = 0.0
				if systems.has(sname) and int(systems[sname]["damage"]) < int(systems[sname]["max"]):
					systems[sname]["damage"] = int(systems[sname]["damage"]) + 1
					_clip_power(systems)
			if float(f["t"]) <= 0.0:
				fires.erase(rid)
				_pop(_on_page(at_player, _room_center(at_player, rid)), "Fire out", DIM)
	for rid in foe_gas.keys():
		var gas: Dictionary = foe_gas[rid]
		gas["t"] = float(gas["t"]) - delta
		for c in e_crew_list:
			if float(c["hp"]) > 0.0 and str(c["room"]) == rid:
				c["hp"] = maxf(0.0, float(c["hp"]) - GAS_CREW * delta)
		if float(gas["t"]) <= 0.0:
			foe_gas.erase(rid)
	var choking := false
	for c in e_crew_list:
		var here: String = str(c["room"]) if str(c["room"]) != "" else str(c["last"])
		if float(c["hp"]) > 0.0 and float(foe_air.get(here, 1.0)) < AIR_THIN:
			c["hp"] = maxf(0.0, float(c["hp"]) - AIR_CHOKE * delta)
			choking = true
	if choking or not foe_fires.is_empty() or not foe_gas.is_empty():
		_count_crew(_on_page(false, (foe["size"] as Vector2) / 2.0))


# A fire reaches into a room next door: through an open door, or a shut one now and then. Not through airlocks.
func _spread_fire(at_player: bool, ship: Dictionary, rid: String) -> void:
	var fires: Dictionary = my_fires if at_player else foe_fires
	var air: Dictionary = my_air if at_player else foe_air
	var ways: Array = []
	for d in ship.get("door_list", []):
		if bool(d.get("airlock", false)):
			continue
		var other: String = str(d["b"]) if str(d["a"]) == rid else (str(d["a"]) if str(d["b"]) == rid else "")
		if other == "" or fires.has(other) or float(air.get(other, 1.0)) < 0.3:
			continue
		if bool(d["open"]) or float(d["pass"]) > 0.0 or randf() < 0.33:
			ways.append(other)
	if ways.is_empty():
		return
	var to: String = ways[randi() % ways.size()]
	_set_fire(at_player, to, _on_page(at_player, _room_center(at_player, to)))


func _fill_air(ship: Dictionary, air: Dictionary) -> void:
	air.clear()
	for room in ship.get("rooms", []):
		air[str(room["id"])] = 1.0


# The ship's airlock out of that room, or {} if it has none.
func _airlock_of(ship: Dictionary, rid: String) -> Dictionary:
	for d in ship.get("door_list", []):
		if bool(d.get("airlock", false)) and str(d["a"]) == rid:
			return d
	return {}


# Life support fills the rooms (a ship with no oxygen system has scrubbers worth one bar); without it every room
# leaks. Fires eat air. Open doors even two rooms out; an open airlock empties its room into space.
func _tick_air(at_player: bool, delta: float) -> void:
	var ship: Dictionary = me_ship if at_player else foe
	var air: Dictionary = my_air if at_player else foe_air
	var systems: Dictionary = sys if at_player else e_sys
	var life: int = _eff(systems, "life") if systems.has("life") else 1
	for rid in air:
		if life > 0:
			air[rid] = minf(1.0, float(air[rid]) + AIR_REFILL * life * delta)
		else:
			air[rid] = maxf(0.0, float(air[rid]) - AIR_LEAK * delta)
	for rid in (my_fires if at_player else foe_fires):
		if air.has(rid):
			air[rid] = maxf(0.0, float(air[rid]) - AIR_BURN * delta)
	var mix: float = minf(0.5, AIR_MIX * delta)
	for d in ship.get("door_list", []):
		if not bool(d["open"]) and float(d["pass"]) <= 0.0:
			continue
		var a: String = str(d["a"])
		if not air.has(a):
			continue
		if bool(d.get("airlock", false)):
			air[a] = maxf(0.0, float(air[a]) - AIR_VENT * delta)
		elif air.has(str(d["b"])):
			var b: String = str(d["b"])
			var flow: float = (float(air[a]) - float(air[b])) * mix
			air[a] = float(air[a]) - flow
			air[b] = float(air[b]) + flow


# You, in the cockpit: when its air runs thin you're on your suit's tank, which fills again once the air is back.
# The readout along the top is the whole ship's air.
func _breathe(delta: float) -> void:
	var total := 0.0
	for rid in my_air:
		total += float(my_air[rid])
	oxygen = 100.0 * total / maxf(1.0, float(my_air.size()))
	if float(my_air.get("cockpit", 1.0)) < AIR_THIN:
		suit_air -= delta
		if suit_air <= 0.0:
			suit_air = 0.0
			_lose("Your suit runs out of air")
	else:
		suit_air = minf(SUIT_AIR, suit_air + 2.0 * delta)


# Air, fires, smoke and gas, drawn over a ship's rooms: thin air turns a room red (FTL's warning), fires burn in
# every cell of the room with smoke rising (art/ships/fx), a system knocked right out smokes too, gas is a green haze.
func _paint_hazards(at_player: bool, xf: Transform2D, k: float) -> void:
	var ship: Dictionary = me_ship if at_player else foe
	var ms: float = Time.get_ticks_msec() / 1000.0
	var systems: Dictionary = sys if at_player else e_sys
	var air: Dictionary = my_air if at_player else foe_air
	var fires: Dictionary = my_fires if at_player else foe_fires
	var cell: float = float(ShipData.CELL)
	for room in ship["rooms"]:
		var rr: Rect2 = xf * (room["rect"] as Rect2)
		var rid: String = str(room["id"])
		var sname: String = str(room["sys"])
		var breath: float = float(air.get(rid, 1.0))
		if breath < 0.75:
			var thin: float = (0.75 - breath) / 0.75
			screen.rect(rr.grow(-2.0 * k), Color(0.95, 0.2, 0.32, 0.12 + 0.3 * thin + (0.08 * sin(ms * 6.0) if breath < AIR_THIN else 0.0)))
		if systems.has(sname) and float(systems[sname].get("ion", 0.0)) > 0.0:
			screen.rect(rr.grow(-2.0 * k), Color(0.35, 0.75, 1.0, 0.28 + 0.1 * sin(ms * 12.0)))
		if (foe_gas if not at_player else {}).has(rid):
			screen.rect(rr.grow(-2.0 * k), Color(0.55, 0.95, 0.3, 0.3))
			for i in range(4):
				var bx: float = rr.position.x + rr.size.x * fmod(0.2 + i * 0.23 + ms * 0.05, 1.0)
				var by: float = rr.end.y - fmod(ms * 8.0 + i * 7.0, rr.size.y)
				screen.circle(Vector2(bx, by), 1.5 * k, Color(0.75, 1.0, 0.55, 0.7))
		var r_logical: Rect2 = room["rect"]
		var cols: int = maxi(1, int(round(r_logical.size.x / cell)))
		var rows: int = maxi(1, int(round(r_logical.size.y / cell)))
		var burning: bool = fires.has(rid)
		if burning:
			screen.rect(rr.grow(-2.0 * k), Color(1.0, 0.45, 0.15, 0.18))
			for cy in range(rows):
				for cx in range(cols):
					var cr: Rect2 = xf * Rect2(r_logical.position + Vector2(cx, cy) * cell, Vector2(cell, cell))
					if fx_fire != null:
						var fi: int = (int(ms * 9.0) + cx * 3 + cy * 2) % 4
						screen.texture(fx_fire, cr, Rect2(fi * 48, 0, 48, 48))
					else:
						for i in range(3):
							var fx: float = cr.position.x + cr.size.x * (0.25 + 0.25 * i)
							var h: float = 7.0 * k * (0.6 + 0.4 * sin(ms * 14.0 + i * 1.7 + cx))
							var fy: float = cr.end.y - 3.0 * k
							screen.polygon(PackedVector2Array([Vector2(fx - 2.5 * k, fy), Vector2(fx, fy - h), Vector2(fx + 2.5 * k, fy)]), Color(1.0, 0.55, 0.15, 0.9))
		var knocked_out: bool = systems.has(sname) and int(systems[sname]["max"]) > 0 and int(systems[sname]["damage"]) >= int(systems[sname]["max"])
		if (burning or knocked_out) and fx_smoke != null:
			var top_cell: Rect2 = xf * Rect2(r_logical.position + Vector2((cols - 1) * 0.5 * cell, 0), Vector2(cell, cell))
			var si: int = int(ms * 5.0 + rid.length()) % 4
			screen.texture(fx_smoke, top_cell.grow(2.0 * k), Rect2(si * 48, 0, 48, 48), Color(1, 1, 1, 0.9 if burning else 0.55))


# Blasts where shots land on a hull.
func _paint_blasts() -> void:
	if fx_hit == null:
		return
	for b in blasts:
		var f: int = mini(5, int(float(b["t"]) / BLAST_FRAME))
		var size: float = 30.0 * float(b["k"])
		var at: Vector2 = b["pos"]
		screen.texture(fx_hit, Rect2(at - Vector2(size, size) / 2.0, Vector2(size, size)), Rect2(f * 48, 0, 48, 48))


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
		var kinds: Variant = CREW_KIND.get(foe_id, "rabble_pirate")
		var kind: String = str(kinds[i % (kinds as Array).size()]) if kinds is Array else str(kinds)
		e_crew_list.append({"home": home, "room": home, "target": home, "pos": _crew_spot(home, i, true), "hp": CREW_HP, "task": "station",
			"kind": kind, "face": Vector2.DOWN, "walking": false,
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
		if rid == "" or bool(_airlock_of(foe, rid).get("vented", false)):
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
	# Venting: a fire in a room with an airlock and nobody in it or on the way gets its airlock opened, and the fire
	# chokes out; the airlock shuts again once the fire is out.
	for d in foe.get("door_list", []):
		if not bool(d.get("airlock", false)):
			continue
		var vr: String = str(d["a"])
		var want: bool = foe_fires.has(vr) and not _crew_bound(vr)
		if want and not bool(d["open"]):
			d["open"] = true
			d["vented"] = true
			_pop(_on_page(false, _room_center(false, vr)) + Vector2(0, -12), "Venting", Color("dfe8ff"))
		elif not want and bool(d.get("vented", false)) and not foe_fires.has(vr):
			d["open"] = false
			d["vented"] = false
	# Fires: someone goes to put out each one nobody is seeing to (never the pilot), unless it's being vented.
	for rid_f in foe_fires.keys():
		if bool(_airlock_of(foe, str(rid_f)).get("vented", false)):
			continue
		var covered_f := false
		for c in e_crew_list:
			if float(c["hp"]) > 0.0 and str(c["task"]) == "repair" and str(c["target"]) == str(rid_f):
				covered_f = true
		if covered_f:
			continue
		var best_f := -1
		var best_d := INF
		var to_f: Vector2 = _crew_spot(str(rid_f), 0)
		for i in range(e_crew_list.size()):
			var cf: Dictionary = e_crew_list[i]
			if float(cf["hp"]) <= 0.0 or str(cf["task"]) != "station" or str(cf["home"]) == _sys_room("pilot"):
				continue
			var dd: float = (cf["pos"] as Vector2).distance_to(to_f)
			if dd < best_d:
				best_d = dd
				best_f = i
		if best_f >= 0:
			e_crew_list[best_f]["task"] = "repair"
			e_crew_list[best_f]["target"] = str(rid_f)
	# Walk, and work.
	var working := {}
	for i in range(e_crew_list.size()):
		var c3: Dictionary = e_crew_list[i]
		if float(c3["hp"]) <= 0.0:
			continue
		if str(c3["task"]) == "repair":
			var tsys: String = str(_room(foe["rooms"], str(c3["target"])).get("sys", ""))
			if (not e_sys.has(tsys) or int(e_sys[tsys]["damage"]) <= 0) and not foe_fires.has(str(c3["target"])):
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
			if at.distance_to(to) > 0.01:
				c3["face"] = (to - at).normalized()
			c3["walking"] = true
			c3["room"] = ""
		elif at.distance_to(goal) > step:
			c3["pos"] = at + (goal - at).normalized() * step
			c3["face"] = (goal - at).normalized()
			c3["walking"] = true
			c3["room"] = ""
		else:
			c3["walking"] = false
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


# True when one of their crew is in that room or on the way to it.
func _crew_bound(rid: String) -> bool:
	for c in e_crew_list:
		if float(c["hp"]) > 0.0 and (str(c["room"]) == rid or str(c["target"]) == rid):
			return true
	return false


# A hit on an enemy room hurts whoever is standing in it. When the last of them goes down, the fight is won.
func _hurt_crew(room_id: String, dmg: int, where: Vector2) -> void:
	for c in e_crew_list:
		if float(c["hp"]) > 0.0 and str(c["room"]) == room_id:
			c["hp"] = maxf(0.0, float(c["hp"]) - CREW_HIT * dmg)
			if float(c["hp"]) <= 0.0:
				_pop(where + Vector2(0, 10), "Crew down", Color("ffbeaa"))
	_count_crew(where)


# How many of their crew are still standing; when none are, the fight is won.
func _count_crew(_where: Vector2) -> void:
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
	if not my_fires.is_empty() and not fire_hint_said:
		fire_hint_said = true
		paused = true
		world._say("Sara", [
			"Fire aboard! It eats the air and wrecks the room's system.",
			"Send the drone in to put it out, or click the striped airlock on that room to vent it. No air, no fire. Shut it again after.",
		])
		return
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
			if bool(d.get("airlock", false)):
				_pop(p + Vector2(0, -10), "Venting" if bool(d["open"]) else "Airlock shut", Color("dfe8ff"))
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
				var wd: Dictionary = ShipData.WEAPONS[weapons[selected]["id"]]
				var have: int = _loaded(weapons[selected], wd)
				weapons[selected]["want"] = have if have >= 1 else int(wd.get("stages", 1))
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
	_paint_beams()
	_paint_blasts()
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
	var on_suit: bool = suit_air < SUIT_AIR - 0.01 and float(my_air.get("cockpit", 1.0)) < AIR_THIN
	var air_words: String = ("SUIT AIR %ds" % int(ceil(suit_air))) if on_suit else ("OXYGEN %d%%" % int(oxygen))
	s.text(ev_x, 59, "EVASION %d%%   %s" % [_my_evasion(), air_words], "micro", MUTED if oxygen > 40.0 and not on_suit else ShipScreen.PIP_RED)
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
	if jump_t >= 0.0:
		_paint_jump(size, k)
		return
	var off := Vector2(randf_range(-1, 1), randf_range(-1, 1)) * (2.0 if shake > 0.0 else 0.0)
	var xf := Transform2D(0.0, Vector2(k, k), 0.0, my_xf.origin + off)
	# The cut-away when there is one; otherwise the hull with the rooms drawn over it.
	var inside: bool = interior_tex != null
	var bits_gone: bool = lose_t >= 0.3 and broken_tex != null
	if inside:
		s.texture(broken_tex if bits_gone else interior_tex, Rect2(xf.origin, size * k))
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
		if not _room_icon(rr, sname, k, dmg > 0, sys.has(sname) and float(sys[sname].get("ion", 0.0)) > 0.0):
			_room_tag(rr, str(room["label"]), k)
		if sys.has(sname) and sname != "pilot":
			var bars: int = int(sys[sname]["max"])
			for i in range(bars):
				var bar := Rect2(rr.position + Vector2(3.0 * k + i * 4.0 * k, rr.size.y - 3.0 * k - 2.0 * k), Vector2(3.0 * k, 2.0 * k))
				s.rect(bar, GOOD if i < bars - dmg else BAD)
		if drone_selected and not crew_room and result == "" and rr.has_point(s.mouse):
			s.outline(rr.grow(-1.0), GOOD, maxf(1.0, k * 0.5))
	_paint_hazards(true, xf, k)
	_paint_shield(true, xf, size, k, layers)
	_paint_doors(me_ship, xf, k, true)
	_paint_guns(me, weapons, xf)
	# you, in the cockpit
	var cockpit_room: Dictionary = _room(me["rooms"], "cockpit")
	var cockpit: Rect2 = cockpit_room["rect"]
	var seat: Array = _console_at(me, cockpit_room)
	var you_at: Vector2 = (Vector2(seat[0]) + Vector2(0.5, 0.5)) * ShipData.CELL
	var t_ms: float = Time.get_ticks_msec() / 1000.0
	if not _paint_crew(me, xf, "player", you_at, _work_pose(seat[1], t_ms)):
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
	if lose_t >= 0.0:
		_paint_my_damage(xf, size, k)
	if paused and result == "" and not world.dialogue.active:
		var tag := Rect2(MY_WIN.get_center().x - 30, MY_WIN.position.y + 4, 60, 14)
		s.rect(tag, Color("f2c94c"))
		s.text_center(tag.get_center().x, tag.position.y, "PAUSED", "micro", INK)


# The guns on their mounts, pointing at the nose (shapes until the weapon art exists). Drawn in ship-picture pixels
# through the ship's transform, so an enemy's guns are mirrored with it and point at you.
func _paint_guns(ship: Dictionary, list: Array, xf: Transform2D) -> void:
	var mounts: Array = ship.get("mounts", [])
	var art_xf: Transform2D = _art_xf(ship, xf)
	var a: float = float(ship.get("art_scale", 1))
	var mine: bool = is_same(ship, me_ship)
	var powered: Array = _powered_weapons() if mine else []
	for i in range(mini(mounts.size(), list.size())):
		var w: Dictionary = list[i]
		if str(w["id"]) == "":
			continue
		var m: Vector2 = mounts[i]
		var data: Dictionary = ShipData.WEAPONS[w["id"]]
		var tex: Texture2D = weapon_texes.get(str(w["id"]))
		if tex != null:
			var big: String = "big" if int(data["damage"]) >= 3 else "small"
			var fsize: Vector2 = GUN_FRAME[big]
			var c: float = float(w["charge"]) / _full_charge(w, data)
			if data.has("stages"):
				c = 0.5 * _loaded(w, data) + (0.4 if fmod(float(w["charge"]), float(data["charge"])) > 0.1 else 0.0)
			var frame := 0
			var fired: float = float(w.get("fired", 0.0))
			if fired > 0.15:
				frame = 4
			elif fired > 0.0:
				frame = 5
			elif mine and (not bool(w["on"]) or not bool(powered[i])):
				frame = 0
			elif c >= 1.0:
				frame = 3
			elif c >= 0.5:
				frame = 2
			elif c > 0.05:
				frame = 1
			var at: Transform2D = art_xf * Transform2D(0.0, m * a - (GUN_MOUNT[big] as Vector2))
			screen.texture_xf(tex, at, Rect2(frame * fsize.x, 0, fsize.x, fsize.y))
			continue
		var f: float = 1.7 if int(data["damage"]) >= 3 else 1.0
		screen.rect(xf * Rect2(m + Vector2(-6, -3) * f, Vector2(8, 6) * f), Color("3a3644"))
		screen.rect(xf * Rect2(m + Vector2(-5, -2) * f, Vector2(6, 4) * f), Color("5d5868"))
		screen.rect(xf * Rect2(m + Vector2(1, -1) * f, Vector2(10, 2) * f), Color("6e6a7c"))
		screen.rect(xf * Rect2(m + Vector2(9, -1) * f, Vector2(2, 2) * f), data["color"])


# Which frame a crew member shows: [row name, frame, mirrored].
func _crew_pose(c: Dictionary) -> Array:
	var t: float = Time.get_ticks_msec() / 1000.0 + float(c.get("hp", 0.0)) * 0.01
	if float(c["hp"]) <= 0.0:
		return ["down", 0, false]
	if bool(c.get("walking", false)):
		var f: Vector2 = c.get("face", Vector2.DOWN)
		var step: int = int(t * 8.0) % 4
		if absf(f.x) > absf(f.y):
			return ["walk_right", step, f.x < 0.0]
		return ["walk_down" if f.y >= 0.0 else "walk_up", step, false]
	var room: Dictionary = _room(foe["rooms"], str(c["room"]))
	if str(c["task"]) == "fight":
		return ["fight", int(t * 6.0) % 4, float(c.get("foe_x", 0.0)) < (c["pos"] as Vector2).x]
	if str(c["task"]) == "repair" and foe_fires.has(str(c["room"])):
		# spraying the fire, toward the middle of the room
		var mid: Vector2 = (room.get("rect", Rect2()) as Rect2).get_center()
		return ["extinguish", int(t * 8.0) % 4, mid.x < (c["pos"] as Vector2).x - 1.0]
	if str(c["task"]) == "repair":
		return ["repair", int(t * 6.0) % 4, false]
	if str(c["room"]) == str(c["home"]) and str(room.get("sys", "")) in STATIONS and room.has("cells"):
		return _work_pose(_console_at(foe, room)[1], t)
	return ["idle", int(t * 1.5) % 2, false]


# Typing at a console on the given side of the cell: [row, frame, mirrored]. The hands take turns on the keys.
func _work_pose(side: Vector2i, t: float) -> Array:
	var f: int = int(t * 6.0) % 4
	if side == Vector2i(0, -1):
		return ["work_up", f, false]
	if side == Vector2i(0, 1):
		return ["work_down", f, false]
	return ["work_right", f, side == Vector2i(-1, 0)]


# One crew sprite standing at pos (ship-picture px) on a ship drawn through xf. False if there's no sprite for them.
func _paint_crew(ship: Dictionary, xf: Transform2D, kind: String, pos: Vector2, pose: Array) -> bool:
	var tex: Texture2D = crew_texes.get(kind)
	if tex == null:
		return false
	var a: float = float(ship.get("art_scale", 1))
	var row: int = int(CREW_ROW[pose[0]])
	var src := Rect2(int(pose[1]) * 48, row * 48, 48, 48)
	# the figure's middle (its waist) at pos; in art pixels the frame is 48 x 48 and the figure's waist is at (24, 28)
	var m: Transform2D = _art_xf(ship, xf) * Transform2D(0.0, pos * a - Vector2(24, 28))
	if bool(pose[2]):
		m = m * Transform2D(Vector2(-1, 0), Vector2(0, 1), Vector2(48, 0))
	screen.texture_xf(tex, m, src)
	return true


# A system room's marking in the middle of the room: grey while working, red while damaged. False when the room
# has no marking (crew decks, holds), so the caller can give it a name tag instead.
func _room_icon(rr: Rect2, sname: String, k: float, hurt: bool, ion: bool = false) -> bool:
	var i: int = ROOM_ICONS.find(sname)
	if i < 0 or room_icons == null:
		return false
	var size := Vector2(16.0, 16.0) * k
	var col: Color = ICON_ION if ion else (ICON_HIT if hurt else ICON_OK)
	screen.texture(room_icons, Rect2(screen.snap(rr.get_center() - size / 2.0), size), Rect2(i * 32, 0, 32, 32), col)
	return true


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
# Airlocks (22 Nov) are striped yellow and black; open, the room's air streams out of them into space.
func _paint_doors(ship: Dictionary, xf: Transform2D, k: float, mine: bool) -> void:
	var s := screen
	var locks: bool = int(ship.get("door_level", 1)) >= 2
	var air: Dictionary = my_air if mine else foe_air
	var ms: float = Time.get_ticks_msec() / 1000.0
	for d in ship.get("door_list", []):
		var slab := _door_rect(d, xf)
		var is_open: bool = bool(d["open"]) or float(d["pass"]) > 0.0
		if bool(d.get("airlock", false)):
			_paint_airlock(ship, d, slab, xf, k, is_open, float(air.get(str(d["a"]), 0.0)), ms)
		elif is_open:
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


const HAZARD_Y := Color("f2c94c")
const HAZARD_K := Color("24222c")


func _paint_airlock(ship: Dictionary, d: Dictionary, slab: Rect2, xf: Transform2D, k: float, is_open: bool, breath: float, ms: float) -> void:
	var s := screen
	var long_x: bool = slab.size.x >= slab.size.y
	var length: float = slab.size.x if long_x else slab.size.y
	var e: float = maxf(1.0, k)
	if is_open:
		# just the striped ends of the frame
		if long_x:
			s.rect(Rect2(slab.position, Vector2(2.0 * e, slab.size.y)), HAZARD_Y)
			s.rect(Rect2(Vector2(slab.end.x - 2.0 * e, slab.position.y), Vector2(2.0 * e, slab.size.y)), HAZARD_Y)
		else:
			s.rect(Rect2(slab.position, Vector2(slab.size.x, 2.0 * e)), HAZARD_Y)
			s.rect(Rect2(Vector2(slab.position.x, slab.end.y - 2.0 * e), Vector2(slab.size.x, 2.0 * e)), HAZARD_Y)
		# air streaming out, away from the room, while there's any left to lose
		if breath > 0.03:
			var room_c: Vector2 = xf * (_room(ship["rooms"], str(d["a"])).get("rect", Rect2(d["at"], Vector2.ZERO)) as Rect2).get_center()
			var out: Vector2 = (slab.get_center() - room_c).normalized()
			var side := Vector2(-out.y, out.x)
			for i in range(5):
				var t: float = fmod(ms * 1.6 + i * 0.21, 1.0)
				var p: Vector2 = slab.get_center() + out * (t * 16.0 * k) + side * ((i - 2) * 1.6 * k + sin(ms * 7.0 + i) * k)
				s.rect(Rect2(p - Vector2(e, e) * 0.5, Vector2(e, e)), Color(0.9, 0.96, 1.0, (1.0 - t) * minf(1.0, breath * 2.0)))
		return
	s.rect(slab, HAZARD_K)
	var n: int = maxi(3, int(length / (2.0 * e)))
	var seg: float = length / n
	for i in range(n):
		if i % 2 == 0:
			if long_x:
				s.rect(Rect2(slab.position + Vector2(i * seg, 0), Vector2(seg, slab.size.y)), HAZARD_Y)
			else:
				s.rect(Rect2(slab.position + Vector2(0, i * seg), Vector2(slab.size.x, seg)), HAZARD_Y)




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
	if break_t >= 0.0:
		if result != "done":
			_paint_break_up()
	else:
		if not (destroyed and (end_timer < 1.6 or result == "done")):
			_paint_enemy()
		if destroyed and result != "done":
			_paint_blast()


func _paint_enemy() -> void:
	var s := screen
	var xf: Transform2D = foe_xf
	var k: float = _ship_scale(false)
	var size: Vector2 = foe["size"]
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
			if not _room_icon(rr, sname, k, dmg > 0, e_sys.has(sname) and float(e_sys[sname].get("ion", 0.0)) > 0.0):
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
	_paint_hazards(false, xf, k)
	_paint_shield(false, xf, size, k, e_layers)
	_paint_doors(foe, xf, k, false)
	_paint_guns(foe, e_weapons, xf)
	# their crew: red at stations, orange when repairing, a health bar once hurt
	for c in e_crew_list:
		var cpos: Vector2 = xf * (c["pos"] as Vector2)
		var cr: float = 3.0 * k
		if float(c["hp"]) <= 0.0:
			if not _paint_crew(foe, xf, str(c.get("kind", "rabble_pirate")), c["pos"], ["down", 0, false]):
				s.line(cpos + Vector2(-cr, -cr), cpos + Vector2(cr, cr), Color("5a4a48"), 1.0)
				s.line(cpos + Vector2(-cr, cr), cpos + Vector2(cr, -cr), Color("5a4a48"), 1.0)
			continue
		if not _paint_crew(foe, xf, str(c.get("kind", "rabble_pirate")), c["pos"], _crew_pose(c)):
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


# The bubble round a ship: its middle and half-size on the page.
func _shield_shape(mine: bool) -> Array:
	var ship: Dictionary = me_ship if mine else foe
	var size: Vector2 = ship["size"]
	var xf: Transform2D = my_xf if mine else foe_xf
	var k: float = _ship_scale(mine)
	return [xf * (size / 2.0), (size * k / 2.0 + Vector2(10, 10)).round()]


# Where a blocked shot meets the bubble: from the middle toward the shot's target, out to the rim.
func _shield_edge(mine: bool, where: Vector2) -> Vector2:
	var shape: Array = _shield_shape(mine)
	var mid: Vector2 = shape[0]
	var r: Vector2 = shape[1]
	var d: Vector2 = where - mid
	# the side the shot comes from: yours from the right, theirs from the left
	d.x = absf(d.x) * (1.0 if mine else -1.0) + (r.x * 0.6 if mine else -r.x * 0.6)
	var a: float = atan2(d.y / r.y, d.x / r.x)
	return mid + Vector2(cos(a) * r.x, sin(a) * r.y)


func _paint_shield(mine: bool, xf: Transform2D, size: Vector2, k: float, up: int) -> void:
	var shape: Array = _shield_shape(mine)
	var mid: Vector2 = xf * (size / 2.0)
	var r: Vector2 = shape[1]
	var flash := 0.0
	for h in shield_hits:
		if bool(h["mine"]) == mine:
			flash = maxf(flash, 1.0 - float(h["t"]) / 0.5)
	if up > 0:
		var tex: Texture2D = _shield_tex(Vector2i(int(r.x * 2.0), int(r.y * 2.0)))
		screen.texture(tex, Rect2(screen.snap(mid - r), r * 2.0), Rect2(), Color(1, 1, 1, minf(1.0, 0.6 + 0.1 * up + 0.4 * flash)))
		if up > 1:
			screen.ellipse(mid, r + Vector2(3, 3), Color(Color("9ae8ff"), 0.55), 1.0)
	# ripples where shots were stopped
	for h in shield_hits:
		if bool(h["mine"]) != mine:
			continue
		var t: float = float(h["t"]) / 0.5
		var p: Vector2 = h["pos"]
		screen.ring(p, 2.0 + 12.0 * t, Color(0.85, 0.97, 1.0, 1.0 - t))
		screen.ring(p, 1.0 + 6.0 * t, Color(0.6, 0.88, 1.0, (1.0 - t) * 0.8))


# The bubble's picture at one size, in page pixels: see-through in the middle, a hex pattern that shows more toward
# the edge, and a bright rim. Made once per size.
func _shield_tex(sz: Vector2i) -> Texture2D:
	var key := "%dx%d" % [sz.x, sz.y]
	if shield_texes.has(key):
		return shield_texes[key]
	var img := Image.create_empty(maxi(sz.x, 2), maxi(sz.y, 2), false, Image.FORMAT_RGBA8)
	var c := Vector2(sz) / 2.0
	var rim: float = 1.0 - 1.6 / minf(c.x, c.y)
	var dirs: Array = [Vector2(1, 0), Vector2(0.5, 0.866), Vector2(-0.5, 0.866)]
	var cell := 7.0
	for y in range(sz.y):
		for x in range(sz.x):
			var u: float = (x + 0.5 - c.x) / c.x
			var v: float = (y + 0.5 - c.y) / c.y
			var r2: float = u * u + v * v
			if r2 > 1.0:
				continue
			var rr: float = sqrt(r2)
			var a: float = 0.05 + 0.22 * pow(rr, 6.0)
			var col := Color(0.42, 0.74, 1.0)
			var p := Vector2(x, y) - c
			for d in dirs:
				var t: float = p.dot(d) / cell
				if absf(t - roundf(t)) < 0.07:
					a += 0.1 * r2
					col = Color(0.6, 0.86, 1.0)
					break
			if rr > rim:
				a = 0.75
				col = Color(0.75, 0.94, 1.0)
			elif rr > rim - 0.03:
				a = maxf(a, 0.3)
			img.set_pixel(x, y, Color(col, minf(a, 1.0)))
	var tex := ImageTexture.create_from_image(img)
	shield_texes[key] = tex
	return tex


# A ship's pieces (gib_N.png or chip_N.png, numbered from 1): each with where its middle is in the picture, the way
# it flies (out from the ship's middle) and how fast it turns.
func _pieces(pattern: String, ship: Dictionary) -> Array:
	var out: Array = []
	var a: float = float(ship.get("art_scale", 1))
	var mid: Vector2 = (ship["size"] as Vector2) * a / 2.0
	for i in range(1, 9):
		var tex: Texture2D = _load_tex(pattern % i)
		if tex == null:
			break
		var used: Rect2i = tex.get_image().get_used_rect()
		var c: Vector2 = Vector2(used.position) + Vector2(used.size) / 2.0
		var dir: Vector2 = (c - mid).normalized() if c.distance_to(mid) > 1.0 else Vector2.UP
		out.append({"tex": tex, "c": c, "dir": dir.rotated(randf_range(-0.35, 0.35)),
			"speed": randf_range(14.0, 26.0), "spin": randf_range(-0.9, 0.9)})
	return out


# Art pixels -> page for a ship drawn through xf (which works in 24-px cell units).
func _art_xf(ship: Dictionary, xf: Transform2D) -> Transform2D:
	var a: float = float(ship.get("art_scale", 1))
	return xf * Transform2D(0.0, Vector2(1.0 / a, 1.0 / a), 0.0, Vector2.ZERO)


# One piece of a ship, moved d page pixels and turned by ang about its own middle.
func _paint_piece(piece: Dictionary, art_xf: Transform2D, d: Vector2, ang: float, col: Color) -> void:
	var c: Vector2 = piece["c"]
	var m: Transform2D = Transform2D(0.0, d) * art_xf * Transform2D(0.0, c) * Transform2D(ang, Vector2.ZERO) * Transform2D(0.0, -c)
	screen.texture_xf(piece["tex"], m, Rect2(), col)


# A blast: an orange ball that swells and fades over life seconds.
func _puff(at: Vector2, t: float, life: float, size: float) -> void:
	if t < 0.0 or t > life:
		return
	var u: float = t / life
	screen.circle(at, size * (0.4 + u), Color(1.0, 0.85 - 0.5 * u, 0.35, 0.9 * (1.0 - u)))
	screen.circle(at, size * (0.2 + 0.5 * u), Color(1.0, 0.97, 0.8, 0.9 * (1.0 - u) * (1.0 - u)))


# The enemy breaking up: it flashes with blasts, then splits into its pieces, which drift apart, turn and fade.
func _paint_break_up() -> void:
	var k: float = _ship_scale(false)
	var size: Vector2 = foe["size"]
	var art_xf: Transform2D = _art_xf(foe, foe_xf)
	if break_t < BREAK_FLASH:
		if enemy_inside != null:
			screen.texture(enemy_inside, _ship_rect(foe_xf, size))
		for i in range(5):
			var p: Vector2 = foe_xf * (size * Vector2(0.2 + 0.15 * i, 0.3 + 0.4 * float(i % 2)))
			_puff(p, break_t - i * 0.07, 0.4, 6.0 * k)
		return
	var t: float = break_t - BREAK_FLASH
	var fade: float = clampf(1.0 - (t - 1.7) / 0.8, 0.0, 1.0)
	for piece in foe_gibs:
		var d: Vector2 = (art_xf.basis_xform(piece["dir"]) as Vector2).normalized() * float(piece["speed"]) * t * k * 0.8
		_paint_piece(piece, art_xf, d, float(piece["spin"]) * t, Color(1, 1, 1, fade))
	# blasts where it tore apart, and a ring of debris
	var mid: Vector2 = foe_xf * (size / 2.0)
	_puff(mid, t, 0.6, 16.0 * k)
	for i in range(foe_gibs.size()):
		var piece: Dictionary = foe_gibs[i]
		var at: Vector2 = art_xf * (piece["c"] as Vector2)
		_puff(mid.lerp(at, 0.5), t - 0.08 * i, 0.5, 7.0 * k)
	for i in range(12):
		var a: float = i * TAU / 12.0 + 0.3
		var r: float = (20.0 + 50.0 * t) * k
		screen.rect(Rect2(mid + Vector2(cos(a), sin(a)) * r, Vector2(2, 2) * k), Color(0.62, 0.55, 0.5, maxf(0.0, 1.0 - t * 0.7)))


# Beaten: bits break off your fighter (with blasts where they tore), and the drive charges for the jump.
func _paint_my_damage(xf: Transform2D, size: Vector2, k: float) -> void:
	var art_xf: Transform2D = _art_xf(me_ship, xf)
	var t: float = lose_t - 0.3
	for i in range(my_chips.size()):
		var piece: Dictionary = my_chips[i]
		var at: Vector2 = art_xf * (piece["c"] as Vector2)
		_puff(at, t - 0.15 * i, 0.5, 5.0 * k)
		if t > 0.15 * i:
			var tt: float = t - 0.15 * i
			var d: Vector2 = (piece["dir"] as Vector2) * (float(piece["speed"]) + 20.0) * tt * k * 0.5
			_paint_piece(piece, art_xf, d, float(piece["spin"]) * 3.0 * tt, Color(1, 1, 1, clampf(1.0 - tt / 1.6, 0.0, 1.0)))
	if lose_t > 1.3:
		# the fold drive spooling up: a blue glow round the ship
		var u: float = clampf((lose_t - 1.3) / (JUMP_AT - 1.3), 0.0, 1.0)
		var mid: Vector2 = xf * (size / 2.0)
		screen.ellipse(mid, size * k / 2.0 + Vector2(4, 4) * (1.0 + u * 2.0), Color(0.55, 0.85, 1.0, 0.3 + 0.6 * u), 1.0 + u * 2.0)


# The jump: the ship stretches into a streak and is gone in a flash, leaving a fading line.
func _paint_jump(size: Vector2, k: float) -> void:
	var u: float = clampf(jump_t / 0.45, 0.0, 1.0)
	var start := Rect2(my_xf.origin, size * k)
	var tex: Texture2D = ship_tex if ship_tex != null else interior_tex
	if u < 1.0 and tex != null:
		var dx: float = u * u * 260.0
		var stretch: float = 1.0 + u * 2.5
		for j in range(3, -1, -1):
			var lag: float = float(j) * 0.12
			var x: float = maxf(0.0, dx - lag * 260.0 * u)
			var r := Rect2(start.position + Vector2(x, size.y * k * u * 0.15), Vector2(start.size.x * stretch, start.size.y * (1.0 - u * 0.3)))
			screen.texture(tex, r, Rect2(), Color(0.75, 0.9, 1.0, (1.0 - u) * (1.0 - j * 0.22)))
	var mid: Vector2 = start.get_center()
	var flash: float = clampf(1.0 - absf(jump_t - 0.4) / 0.25, 0.0, 1.0)
	if flash > 0.0:
		screen.circle(mid + Vector2(120, 0) * u, 18.0 * k * flash, Color(1, 1, 1, flash))
	var fade: float = clampf(1.0 - (jump_t - 0.4) / 0.7, 0.0, 1.0)
	if jump_t > 0.2 and fade > 0.0:
		screen.rect(Rect2(mid.x, mid.y - 1, MY_WIN.end.x - 8 - mid.x, 2), Color(0.75, 0.92, 1.0, fade))


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
		var col: Color = sh["color"]
		if str(sh.get("kind", "")) == "missile" and missile_tex != null:
			# the missile sprite, nose along its path, flame flickering
			var frame: int = int(Time.get_ticks_msec() / 60) % 3
			var m: Transform2D = Transform2D(dir.angle(), head) * Transform2D(0.0, Vector2(-14, -4))
			screen.texture_xf(missile_tex, m, Rect2(frame * 16, 0, 16, 8))
			continue
		# a laser bolt: a soft glow with a bright core
		screen.line(head - dir * (tail + 2.0), head + dir, Color(col, 0.45), 5.0 if heavy else 4.0)
		screen.line(head - dir * tail, head, col, 3.0 if heavy else 2.0)
		screen.line(head - dir * tail * 0.6, head, Color(1, 1, 1, 0.9), 1.0)


# Beams: from the gun, out of its window, in at the near edge of the target's, to the point cutting across the
# rooms; the cut it leaves glows and fades.
func _paint_beams() -> void:
	for bm in beams:
		var t: float = float(bm["t"])
		if t < 0.0:
			continue
		var at_player: bool = bm["at_player"]
		var col: Color = bm["color"]
		var tt: float = clampf(t, 0.0, 1.0)
		var fade: float = clampf((1.25 - t) / 0.25, 0.0, 1.0) if t > 1.0 else 1.0
		var p: Vector2 = _on_page(at_player, (bm["a"] as Vector2).lerp(bm["b"], tt))
		var a0: Vector2 = _on_page(at_player, bm["a"])
		# the scar
		screen.line(a0, p, Color(col, 0.5 * fade), 3.0)
		screen.line(a0, p, Color(1, 0.95, 0.85, 0.7 * fade), 1.0)
		if t > 1.0:
			continue
		var g0: Vector2 = _on_page(not at_player, bm["from"])
		var out_x: float = (FOE_WIN.position.x + 3.0) if at_player else (MY_WIN.end.x - 3.0)
		var in_x: float = (MY_WIN.end.x - 3.0) if at_player else (FOE_WIN.position.x + 3.0)
		var wob: float = sin(Time.get_ticks_msec() / 30.0) * 0.5 + 0.5
		for seg in [[g0, Vector2(out_x, g0.y)], [Vector2(in_x, p.y), p]]:
			screen.line(seg[0], seg[1], Color(col, 0.35 + 0.15 * wob), 6.0)
			screen.line(seg[0], seg[1], col, 3.0)
			screen.line(seg[0], seg[1], Color(1, 1, 1, 0.9), 1.0)
		if bool(bm["hit"]):
			screen.circle(p, 3.0 + 2.0 * wob, Color(1, 0.9, 0.6, 0.9))


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
		var icon_i: int = ROOM_ICONS.find(key)
		if room_icons != null and icon_i >= 0:
			var tint: Color = ICON_HIT if int(st["damage"]) > 0 else (ICON_POWERED if int(st["power"]) > 0 else ICON_OK)
			if float(st.get("ion", 0.0)) > 0.0:
				tint = ICON_ION
			s.texture(room_icons, Rect2(x + 3.5, 360, 16, 16), Rect2(icon_i * 32, 0, 32, 32), tint)
		else:
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
	else:
		for w in weapons:
			if str(w["id"]) != "" and int(ShipData.WEAPONS[w["id"]].get("ammo", 0)) > 0:
				s.text_right(r.end.x - 8, r.position.y + 7, "MISSILES %d" % int(world.missiles), "micro", MUTED)
				break
	for i in range(weapons.size()):
		var card := _weapon_rect(i)
		var w: Dictionary = weapons[i]
		if str(w["id"]) == "":
			s.frame(card, Color("ece9e0"))
			s.text(card.position.x + 6, card.position.y + 4, "%d  Empty slot" % (i + 1), "label", MUTED)
			s.text(card.position.x + 6, card.position.y + 33, "BUY OR SALVAGE ONE", "micro", MUTED)
			continue
		var data: Dictionary = ShipData.WEAPONS[w["id"]]
		var full: float = _full_charge(w, data)
		var loaded: int = _loaded(w, data)
		var charged: bool = loaded >= 1
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
		s.rect(Rect2(bar.position, Vector2(bar.size.x * float(w["charge"]) / full, bar.size.y)), ORANGE if charged else Color("6f9fb4"))
		for k in range(1, int(data.get("stages", 1))):
			s.rect(Rect2(bar.position.x + bar.size.x * k / float(data["stages"]) - 0.5, bar.position.y, 1, bar.size.y), INK)
		if int(w.get("chain_n", 0)) > 0:
			s.text_right(bar.end.x, bar.position.y - 9, "CHAIN x%d" % (int(w["chain_n"]) + 1), "micro", OCHRE)
		var note := "OFF - CLICK TO POWER"
		if on:
			note = "READY - CLICK TO AIM" if charged else "CHARGING"
			if not bool(powered[i]):
				note = "NEEDS %d POWER" % cost
			elif selected == i:
				note = "AIM: CLICK A ROOM"
			elif str(w["target"]) != "":
				note = "AIMED"
			if data.has("stages") and bool(powered[i]) and selected != i:
				var stages: int = int(data["stages"])
				if loaded >= stages:
					note = "%d LOADED - AIM TO FIRE ALL" % stages if str(w["target"]) == "" else "FIRING %d" % stages
				elif loaded >= 1:
					note = "%d LOADED - AIM TO FIRE, OR WAIT" % loaded if str(w["target"]) == "" else "AIMED - WAITING FOR %d" % mini(int(w.get("want", stages)), stages)
			if int(data.get("ammo", 0)) > 0 and int(world.missiles) < int(data["ammo"]):
				note = "NO MISSILES LEFT"
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
		var words: String = "Emergency jump: heading home" if result == "lost" and jump_t >= 0.0 else result_text
		s.text_center(box.get_center().x, box.position.y + 9, words, "strong", tone)
