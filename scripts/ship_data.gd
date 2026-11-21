extends RefCounted
# Ships, weapons and fights for the FTL-style space battles (scripts/ship_battle.gd). 21 Nov 2026.
# Design: claude/echo-landing-ship-combat.md in the Project. Every number here is a first guess to tune in play.
#
# Room rectangles are in the ship picture's own pixels, from its top-left corner. "sys" is the system the room
# holds: shields, engines, weapons, life (oxygen), pilot (cockpit), drones. A hit on a room damages its system.
# "max" is how many bars a system can hold; "power" is how many it starts with. pilot and drones are subsystems:
# they never take reactor power, they only work or not.

const SHIELD_RECHARGE := 2.5       # seconds to bring back one shield layer
const DRONE_REPAIR_TIME := 3.0     # seconds for the repair drone to fix one bar
const DRONE_SPEED := 70.0          # ship-picture pixels a second through the ducts
const ENEMY_REPAIR_TIME := 7.0     # seconds for an enemy crew to fix one bar
const SHOT_TIME := 0.7             # seconds a shot takes to cross the gap

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

# The repaired fighter from the Shuttle Bay (art/lunar/player_ship.png, frame 4 of 4, 168x96).
# Only the cockpit is reachable; the bays behind it are sealed, and the repair drone crawls between them.
const STARTER := {
	"name": "Your fighter",
	"art": "res://art/lunar/player_ship.png", "frames": 4, "frame": 3, "size": Vector2(168, 96),
	"hull": 12, "reactor": 6, "drones": 1,
	"weapons": ["burst_laser", ""],          # "" is an empty slot
	"systems": {"shields": [2, 2], "engines": [2, 1], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1], "drones": [1, 1]},
	"rooms": [
		{"id": "weapons", "label": "Weapons bay", "sys": "weapons", "rect": Rect2(44, 6, 66, 14)},
		{"id": "engines", "label": "Engine bay", "sys": "engines", "rect": Rect2(44, 66, 66, 14)},
		{"id": "life", "label": "Life support", "sys": "life", "rect": Rect2(42, 26, 24, 34)},
		{"id": "drones", "label": "Drone bay", "sys": "drones", "rect": Rect2(66, 26, 24, 34)},
		{"id": "shields", "label": "Shields", "sys": "shields", "rect": Rect2(90, 26, 24, 34)},
		{"id": "cockpit", "label": "Cockpit", "sys": "pilot", "rect": Rect2(114, 30, 28, 24), "crew": true},
	],
	"hub": Vector2(78, 43),                 # where the ducts meet, in the drone bay
}

# Enemy ships. "shape" is the outline drawn until real art exists (art/ships/<id>.png, facing left).
const ENEMIES := {
	"rabble_cutter": {
		"name": "Rabble Cutter", "size": Vector2(120, 92), "hull": 8, "crew": 3,
		"weapons": ["rabble_laser", "rabble_laser"],
		"systems": {"shields": [2, 2], "engines": [1, 1], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1]},
		"shape": [Vector2(0, 46), Vector2(18, 24), Vector2(44, 14), Vector2(92, 10), Vector2(116, 24), Vector2(120, 46),
				Vector2(116, 68), Vector2(92, 82), Vector2(44, 78), Vector2(18, 68)],
		"fins": [[Vector2(46, 16), Vector2(36, 0), Vector2(60, 14)], [Vector2(46, 76), Vector2(36, 92), Vector2(60, 78)]],
		"hull_color": Color("60463e"), "trim": Color("962828"),
		"rooms": [
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "rect": Rect2(8, 37, 22, 18)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "rect": Rect2(30, 25, 26, 21)},
			{"id": "shields", "label": "Shields", "sys": "shields", "rect": Rect2(30, 46, 26, 21)},
			{"id": "crew", "label": "Crew", "sys": "", "rect": Rect2(56, 23, 30, 23)},
			{"id": "life", "label": "Oxygen", "sys": "life", "rect": Rect2(56, 46, 30, 23)},
			{"id": "engines", "label": "Engines", "sys": "engines", "rect": Rect2(86, 29, 26, 34)},
		],
	},
	"ivan_flagship": {
		"name": "Ivan's flagship", "size": Vector2(124, 96), "hull": 14, "crew": 5,
		"weapons": ["rabble_laser", "heavy_laser"],
		"systems": {"shields": [2, 2], "engines": [2, 2], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1]},
		"shape": [Vector2(0, 48), Vector2(14, 30), Vector2(30, 12), Vector2(70, 4), Vector2(112, 10), Vector2(124, 30),
				Vector2(124, 66), Vector2(112, 86), Vector2(70, 92), Vector2(30, 84), Vector2(14, 66)],
		"fins": [[Vector2(34, 12), Vector2(20, 0), Vector2(56, 8)], [Vector2(34, 84), Vector2(20, 96), Vector2(56, 88)],
				[Vector2(0, 48), Vector2(-8, 44), Vector2(-8, 52)]],
		"hull_color": Color("3e2a34"), "trim": Color("c89a3c"),
		"overcharge_at": 0.5,              # at half hull he brings out the cannon
		"rooms": [
			{"id": "pilot", "label": "Bridge", "sys": "pilot", "rect": Rect2(8, 38, 20, 20)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "rect": Rect2(28, 20, 30, 26)},
			{"id": "shields", "label": "Shields", "sys": "shields", "rect": Rect2(28, 50, 30, 26)},
			{"id": "crew", "label": "Crew", "sys": "", "rect": Rect2(58, 14, 30, 30)},
			{"id": "life", "label": "Oxygen", "sys": "life", "rect": Rect2(58, 52, 30, 30)},
			{"id": "engines", "label": "Engines", "sys": "engines", "rect": Rect2(88, 24, 30, 48)},
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


# Every enemy ship, whatever table it is in.
static func enemy(id: String) -> Dictionary:
	if ENEMIES.has(id):
		return ENEMIES[id]
	return ANA_SHIPS.get(id, {})

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
