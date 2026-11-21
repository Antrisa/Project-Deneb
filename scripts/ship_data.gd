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

const WEAPONS := {
	"burst_laser": {"name": "Burst laser", "shots": 2, "damage": 1, "charge": 9.0, "power": 2, "color": Color("ff6a5a")},
	"rabble_laser": {"name": "Rabble laser", "shots": 1, "damage": 1, "charge": 11.0, "power": 1, "color": Color("7dff8a")},
	"heavy_laser": {"name": "Heavy laser", "shots": 1, "damage": 2, "charge": 14.0, "power": 1, "color": Color("b6ff5a")},
	# Ivan's overcharged gun (phase 2). Needs no power; a hit on his weapons room drains its charge.
	"ivan_cannon": {"name": "Overcharged cannon", "shots": 1, "damage": 3, "charge": 16.0, "power": 0, "color": Color("ffd34a")},
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

# What a won fight pays: [credits, {item: count}].
const REWARDS := {
	"rabble_cutter": [40, {"hull_plate": 1}],
	"ivan_flagship": [150, {"hull_plate": 2, "coil_wire": 2}],
}
