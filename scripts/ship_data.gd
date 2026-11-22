extends RefCounted
# Ships, weapons and fights for the FTL-style space battles (scripts/ship_battle.gd). 21 Nov 2026.
# Design: claude/echo-landing-ship-combat.md in the Project. Every number here is a first guess to tune in play.
#
# Ships are built on a grid of 24-px cells, FTL-style (Zachary, 21 Nov). A room is a rectangle of cells
# ("cells": Rect2i(column, row, width, height)); build() works out its picture rectangle ("rect"). Older ships
# still give "rect" in picture pixels. "sys" is the system the room holds: shields, engines, weapons, life
# (oxygen), pilot (cockpit), drones. A hit on a room damages its system.
#
# Doors (Zachary, 21 Nov: "doors to go to each room you can close and upgrade to lock"): each door joins two
# neighbouring cells of different rooms, [Vector2i, Vector2i]. Crew and the drone open them as they pass. You can
# click your own doors shut; "door_level" 2 or more locks shut doors (for boarders and fire, when those come).
# "max" is how many bars a system can hold; "power" is how many it starts with. pilot and drones are subsystems:
# they never take reactor power, they only work or not.

const SHIELD_RECHARGE := 2.5       # seconds to bring back one shield layer
const DRONE_REPAIR_TIME := 3.0     # seconds for the repair drone to fix one bar
const DRONE_SPEED := 70.0          # ship-picture pixels a second through the ducts
const ENEMY_REPAIR_TIME := 7.0     # seconds for an enemy crew to fix one bar
const SHOT_TIME := 0.7             # seconds a shot takes to cross the gap
const CELL := 24.0                 # one room cell, in ship-picture pixels (one station tile)

# The repair drone is your first crew member (Zachary, 21 Nov): you select it and send it bay to bay, the way you
# will order crew around on bigger ships. It repairs the bay it is in. In a working bay it boosts that system.
const DRONE_BOOST := {"shields": "shields recharge 25% faster", "weapons": "weapons charge 15% faster", "engines": "+5% evasion"}

const WEAPONS := {
	"burst_laser": {"name": "Burst laser", "type": "laser", "shots": 2, "damage": 1, "charge": 9.0, "power": 2, "color": Color("ff6a5a"),
		"price": 70, "about": "Two quick shots. The first strips a shield layer; the second gets through."},
	"rabble_laser": {"name": "Rabble laser", "type": "laser", "shots": 1, "damage": 1, "charge": 11.0, "power": 1, "color": Color("7dff8a"),
		"price": 35, "about": "Cheap, light, and everywhere the Rabble go. Better in pairs."},
	"heavy_laser": {"name": "Heavy laser", "type": "laser", "shots": 1, "damage": 2, "charge": 14.0, "power": 1, "color": Color("b6ff5a"),
		"price": 90, "about": "One slow, hard-hitting shot. Best once their shields are down."},
	# Ivan's overcharged gun (phase 2). Needs no power; a hit on his weapons room drains its charge.
	"ivan_cannon": {"name": "Overcharged cannon", "type": "special", "shots": 1, "damage": 3, "charge": 16.0, "power": 0, "color": Color("ffd34a"),
		"price": 0, "about": "Ivan's. Not for sale."},
}

# Stores (Zachary, 21 Nov: a trading window like FTL's). Prices are first guesses: fuel, missiles and drone
# parts each, hull repair per point. Weapons sell back for half.
const STORES := {
	"moogli_trader": {"name": "Moogli trader", "weapons": ["heavy_laser", "rabble_laser"],
		"fuel": 6, "missiles": 12, "drone_parts": 10, "repair": 8},
}

# The starter fighter, redrawn after the intro movie and approved by Zachary (21 Nov): plane wings, engine pods out
# behind, a 2 x 2 cockpit under a long canopy. 7 x 4 cells (168 x 96). Art by tools/dev/ship_art/starter.py:
# art/ships/starter/hull.png outside, interior.png the cut-away; art/lunar/player_ship.png is its four repair stages
# for the Shuttle Bay. A single-seat fighter: behind the cockpit are sealed bays only the repair drone gets into,
# through small hatches (the "doors" below). Other ships are walkable all through.
const STARTER := {
	"name": "Your fighter",
	"art": "res://art/ships/starter/hull.png", "frames": 1, "frame": 0, "size": Vector2(168, 96),
	"interior": "res://art/ships/starter/interior.png",
	"hull": 12, "reactor": 6, "drones": 1, "door_level": 1,
	"weapons": ["burst_laser", ""],          # "" is an empty slot; bigger ships have more slots
	"mounts": [Vector2(80, 9), Vector2(80, 86)],   # where each weapon slot's gun sits, near the wing tips
	"systems": {"shields": [2, 2], "engines": [2, 1], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1], "drones": [1, 1]},
	"rooms": [
		{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 1, 1, 2)},
		{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(2, 1, 1, 1)},
		{"id": "drones", "label": "Drone bay", "sys": "drones", "cells": Rect2i(2, 2, 1, 1)},
		{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(3, 1, 1, 1)},
		{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(3, 2, 1, 1)},
		{"id": "cockpit", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(4, 1, 2, 2), "crew": true},
	],
	"doors": [
		[Vector2i(1, 1), Vector2i(2, 1)], [Vector2i(1, 2), Vector2i(2, 2)], [Vector2i(2, 1), Vector2i(2, 2)],
		[Vector2i(2, 1), Vector2i(3, 1)], [Vector2i(2, 2), Vector2i(3, 2)], [Vector2i(3, 1), Vector2i(3, 2)],
		[Vector2i(3, 1), Vector2i(4, 1)],
	],
	"hub": Vector2(60, 60),                 # the drone's home: the middle of the drone bay
}

# Enemy ships. "shape" is the outline drawn until real art exists (art/ships/<id>.png, facing left).
const ENEMIES := {
	# Drawn at double resolution (Zachary, 21 Nov: "lets double the pixels"): 48 art px per cell, so "art_scale" 2.
	# "size" and every room stay in 24-px cells; the battle fits the picture on its own pixels. Art and its rooms:
	# tools/dev/ship_art/rabble_cutter_2x.py (ROOMS and DOORS there must match these). Art faces right; the battle
	# mirrors ships with art so they face you.
	"rabble_cutter": {
		"name": "Rabble Cutter", "size": Vector2(144, 96), "hull": 8, "crew": 3,
		"art": "res://art/ships/rabble_cutter/hull.png", "interior": "res://art/ships/rabble_cutter/interior.png", "art_scale": 2,
		"weapons": ["rabble_laser", "rabble_laser"],
		# Where guns attach to the hull's sides near the front, FTL-style (Zachary, 21 Nov): just outside the hull edge,
		# in the order guns fill them: top front, bottom front, top back, bottom back. Whatever guns the ship spawns
		# with go on the first ones; the game draws them there.
		"mounts": [Vector2(122, 22), Vector2(122, 73.5), Vector2(107, 15), Vector2(107, 80.5)],
		"systems": {"shields": [2, 2], "engines": [1, 1], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1]},
		"rooms": [
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 1, 1, 2)},
			{"id": "crew", "label": "Crew", "sys": "", "cells": Rect2i(2, 1, 1, 1)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(2, 2, 1, 1)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(3, 1, 1, 1)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(3, 2, 1, 1)},
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(4, 1, 1, 2)},
		],
		"doors": [
			[Vector2i(1, 1), Vector2i(2, 1)], [Vector2i(1, 2), Vector2i(2, 2)], [Vector2i(2, 1), Vector2i(2, 2)],
			[Vector2i(2, 1), Vector2i(3, 1)], [Vector2i(2, 2), Vector2i(3, 2)], [Vector2i(3, 1), Vector2i(3, 2)],
			[Vector2i(3, 1), Vector2i(4, 1)], [Vector2i(3, 2), Vector2i(4, 2)],
		],
	},
	# Ivan's flagship at double resolution (art_scale 2), 9 x 6 cells. Art and rooms: tools/dev/ship_art/story2x.py
	# (INSIDES there must match these rooms and doors). Mounts on the hull's sides near the front, in the order guns
	# fill them: top front, bottom front, then the nose for the overcharged cannon he adds at half hull, then the
	# back pair.
	"ivan_flagship": {
		"name": "Ivan's flagship", "size": Vector2(216, 144), "hull": 14, "crew": 5,
		"art": "res://art/ships/ivan_flagship/hull.png", "interior": "res://art/ships/ivan_flagship/interior.png", "art_scale": 2,
		"weapons": ["rabble_laser", "heavy_laser"],
		"mounts": [Vector2(176, 27), Vector2(176, 116.5), Vector2(204, 72), Vector2(158, 18), Vector2(158, 125.5)],
		"systems": {"shields": [2, 2], "engines": [2, 2], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1]},
		"overcharge_at": 0.5,              # at half hull he brings out the cannon
		"rooms": [
			{"id": "crew", "label": "Crew deck", "sys": "", "cells": Rect2i(5, 2, 2, 2)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(1, 1, 2, 1)},
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 2, 2, 2)},
			{"id": "brig", "label": "Brig", "sys": "", "cells": Rect2i(1, 4, 2, 1)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(3, 1, 2, 2)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(3, 3, 2, 2)},
			{"id": "hold_top", "label": "Hold", "sys": "", "cells": Rect2i(5, 1, 2, 1)},
			{"id": "hold_bottom", "label": "Hold", "sys": "", "cells": Rect2i(5, 4, 2, 1)},
			{"id": "pilot", "label": "Bridge", "sys": "pilot", "cells": Rect2i(7, 2, 1, 2)},
		],
		"doors": [
			[Vector2i(1, 1), Vector2i(1, 2)], [Vector2i(1, 3), Vector2i(1, 4)], [Vector2i(2, 2), Vector2i(3, 2)],
			[Vector2i(2, 3), Vector2i(3, 3)], [Vector2i(4, 2), Vector2i(5, 2)], [Vector2i(4, 3), Vector2i(5, 3)],
			[Vector2i(6, 1), Vector2i(6, 2)], [Vector2i(6, 3), Vector2i(6, 4)], [Vector2i(6, 2), Vector2i(7, 2)],
		],
	},
}

# Ana's fight (second flight, Zachary 21 Nov). At half hull ("break_at") the battle stops: her own crew, Ivan's
# loyalists, turn on her, and main.gd starts the fight against their gunship.
const ANA_SHIPS := {
	"ana_corsair": {
		"name": "Ana's corsair", "size": Vector2(118, 88), "hull": 12, "crew": 4,
		"weapons": ["rabble_laser", "heavy_laser"],
		"systems": {"shields": [2, 2], "engines": [2, 2], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1]},
		"shape": [Vector2(0, 44), Vector2(22, 26), Vector2(54, 18), Vector2(100, 22), Vector2(118, 34), Vector2(118, 54),
				Vector2(100, 66), Vector2(54, 70), Vector2(22, 62)],
		"fins": [[Vector2(60, 19), Vector2(78, 2), Vector2(88, 21)], [Vector2(60, 69), Vector2(78, 86), Vector2(88, 67)]],
		"hull_color": Color("2e3e48"), "trim": Color("c84646"),
		"break_at": 0.5,
		"rooms": [
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "rect": Rect2(10, 35, 22, 18)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "rect": Rect2(32, 24, 26, 20)},
			{"id": "shields", "label": "Shields", "sys": "shields", "rect": Rect2(32, 44, 26, 20)},
			{"id": "crew", "label": "Crew", "sys": "", "rect": Rect2(58, 22, 28, 22)},
			{"id": "life", "label": "Oxygen", "sys": "life", "rect": Rect2(58, 44, 28, 22)},
			{"id": "engines", "label": "Engines", "sys": "engines", "rect": Rect2(86, 26, 26, 36)},
		],
	},
	"loyalist_gunship": {
		"name": "Loyalist gunship", "size": Vector2(120, 92), "hull": 8, "crew": 3,
		"weapons": ["rabble_laser", "rabble_laser"],
		"systems": {"shields": [2, 2], "engines": [1, 1], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1]},
		"shape": [Vector2(0, 46), Vector2(18, 24), Vector2(44, 14), Vector2(92, 10), Vector2(116, 24), Vector2(120, 46),
				Vector2(116, 68), Vector2(92, 82), Vector2(44, 78), Vector2(18, 68)],
		"fins": [[Vector2(46, 16), Vector2(36, 0), Vector2(60, 14)], [Vector2(46, 76), Vector2(36, 92), Vector2(60, 78)]],
		"hull_color": Color("4a3a3a"), "trim": Color("c89a3c"),
		"rooms": [
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "rect": Rect2(8, 37, 22, 18)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "rect": Rect2(30, 25, 26, 21)},
			{"id": "shields", "label": "Shields", "sys": "shields", "rect": Rect2(30, 46, 26, 21)},
			{"id": "crew", "label": "Crew", "sys": "", "rect": Rect2(56, 23, 30, 23)},
			{"id": "life", "label": "Oxygen", "sys": "life", "rect": Rect2(56, 46, 30, 23)},
			{"id": "engines", "label": "Engines", "sys": "engines", "rect": Rect2(86, 29, 26, 34)},
		],
	},
}


# What a won fight pays: [credits, {item: count}].
const REWARDS := {
	"rabble_cutter": [40, {"hull_plate": 1}],
	"ivan_flagship": [150, {"hull_plate": 2, "coil_wire": 2}],
	"loyalist_gunship": [60, {"coil_wire": 1}],
}


# Every enemy ship, whatever table it is in, built for battle.
static func enemy(id: String) -> Dictionary:
	if ENEMIES.has(id):
		return build(ENEMIES[id])
	return build(ANA_SHIPS.get(id, {}))


# A ship ready for battle: a copy of its table, with each room's picture rectangle ("rect") worked out from its
# cells, and its doors as "door_list": {"a", "b" (the rooms either side; "" is space, for an airlock), "at" (the
# door's middle, picture pixels), "across" (true for a door in a wall that runs up and down), "open", "locked",
# "pass" (seconds it stays open after someone walks through)}.
static func build(def: Dictionary) -> Dictionary:
	var ship: Dictionary = def.duplicate(true)
	var rooms: Array = ship.get("rooms", [])
	for room in rooms:
		if room.has("cells"):
			var c: Rect2i = room["cells"]
			room["rect"] = Rect2(Vector2(c.position) * CELL, Vector2(c.size) * CELL)
	var doors: Array = []
	for pair in ship.get("doors", []):
		var a: Vector2i = pair[0]
		var b: Vector2i = pair[1]
		var across: bool = a.y == b.y
		var at := Vector2(maxi(a.x, b.x) * CELL, (a.y + 0.5) * CELL) if across else Vector2((a.x + 0.5) * CELL, maxi(a.y, b.y) * CELL)
		doors.append({"a": _room_at_cell(rooms, a), "b": _room_at_cell(rooms, b), "at": at, "across": across,
			"open": false, "locked": false, "pass": 0.0})
	ship["door_list"] = doors
	return ship


static func _room_at_cell(rooms: Array, cell: Vector2i) -> String:
	for room in rooms:
		if room.has("cells") and (room["cells"] as Rect2i).has_point(cell):
			return str(room["id"])
	return ""


# The way from one room to another through the doors, as steps {"door", "room" (the room you are in after it)}.
# Empty when they are the same room, when there's no way through, or when the ship has no doors.
static func route(ship: Dictionary, from_id: String, to_id: String) -> Array:
	if from_id == to_id or from_id == "":
		return []
	var came := {from_id: []}
	var queue: Array = [from_id]
	while queue.size() > 0:
		var here: String = queue.pop_front()
		if here == to_id:
			break
		for d in ship.get("door_list", []):
			var other := ""
			if str(d["a"]) == here:
				other = str(d["b"])
			elif str(d["b"]) == here:
				other = str(d["a"])
			if other == "" or came.has(other):
				continue
			came[other] = [here, d]
			queue.append(other)
	if not came.has(to_id):
		return []
	var steps: Array = []
	var at: String = to_id
	while at != from_id:
		var link: Array = came[at]
		steps.push_front({"door": link[1], "room": at})
		at = str(link[0])
	return steps

# ---------------------------------------------------------------- the jump map (scripts/ship_map.gd)
# A big circle round the Landing: five rings, split into four zones of control. All of it is the neutral zone.
# Angles in degrees: 0 points right (east), 90 points down (south).
const ZONES := [
	{"name": "Terran influence", "from": -135.0, "to": -45.0, "color": Color("222e5c"), "text": Color("6eaaff")},
	{"name": "Zaa'sh influence", "from": -45.0, "to": 45.0, "color": Color("4e361e"), "text": Color("f0aa5a")},
	{"name": "The Rabble's Reach", "from": 45.0, "to": 135.0, "color": Color("46161e"), "text": Color("f05050")},
	{"name": "Collective influence", "from": 135.0, "to": 225.0, "color": Color("1c4030"), "text": Color("6edc8c")},
]
const RING_STOPS := [0, 4, 8, 12, 16, 20]      # how many stops each ring has (ring 0 is the Landing)
# The kinds of stop on the map (Zachary, 21 Nov), as in FTL:
#   beacon   - an ordinary stop: any random event or a fight. You don't know which until you jump.
#              What turns up leans toward the zone's owner (Terran patrols, Zaa'sh pilgrims, Collective convoys, pirates).
#   distress - a labelled distress signal: a special event whose outcome can be good or bad depending on your choice.
#   store    - a trader: repairs, fuel, and later parts and weapons.
#   special  - a special sector: the Rabble's Nest, a wandering merchant, story stops such as Ivan.
const STOP_KINDS := {
	"beacon": {"label": "Beacon", "color": Color("d2d6e4")},
	"distress": {"label": "Distress signal", "color": Color("fadc5a")},
	"store": {"label": "Store", "color": Color("c8a0ff")},
	"special": {"label": "Special", "color": Color("ff8c3c")},
}

# The first flight (Zachary, 21 Nov): the route is locked. It heads off the Rabble and stops once at each kind
# of stop on the way, as a tutorial for exploring and fighting. S.A.R.A. has scanned ahead, so the beacons say
# what they hold. Ring and angle place each stop on the map; "event" is what main.gd runs there.
const FIRST_FLIGHT := [
	{"kind": "beacon", "event": "ice_field", "name": "Ice field", "ring": 1, "angle": 100.0,
		"about": "Wreckage frozen into a drift of ice. Something might still be worth cutting free."},
	{"kind": "distress", "event": "patient_wren", "name": "Drifting freighter", "ring": 2, "angle": 15.0,
		"about": "A distress call on a Collective band. Scorch marks on the hull."},
	{"kind": "beacon", "event": "picket", "name": "Rabble picket", "ring": 3, "angle": 55.0, "enemy": "rabble_cutter",
		"about": "A Rabble Cutter scouting ahead of the others."},
	{"kind": "store", "event": "moogli_trader", "name": "Moogli trader", "ring": 2, "angle": 125.0,
		"about": "A trader's skiff, keeping out of the way. Repairs and fuel, for a price."},
	{"kind": "special", "event": "ivan", "name": "Ivan's flagship", "ring": 3, "angle": 95.0, "enemy": "ivan_flagship",
		"about": "The Rabble's main force, on its way to the Landing. Ivan leads it himself."},
]
const FIRST_FLIGHT_FUEL := 6          # you set off with at least this much
