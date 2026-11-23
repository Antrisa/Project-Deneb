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
	# Missiles (Zachary, 21 Nov: lasers, missiles and beams): straight through shields, but each shot uses one of
	# your missiles (enemies have their own). Beams: a slow line cut across rooms; every room on the line takes the
	# damage, less one for each shield layer, and beams don't knock shields down. "length": the cut, in cell px.
	"missile_launcher": {"name": "Missile launcher", "type": "missile", "shots": 1, "damage": 2, "charge": 12.0, "power": 1,
		"color": Color("ffb04a"), "ammo": 1, "price": 65, "about": "Goes straight through shields. Uses one missile a shot."},
	"cutting_beam": {"name": "Cutting beam", "type": "beam", "shots": 1, "damage": 1, "charge": 12.0, "power": 1, "length": 40.0,
		"color": Color("ff5a5a"), "price": 50, "about": "Cuts a line across their rooms. Any shield stops it, so knock them down first."},
	"heavy_beam": {"name": "Heavy beam", "type": "beam", "shots": 1, "damage": 2, "charge": 16.0, "power": 3, "length": 56.0,
		"color": Color("ffd34a"), "price": 110, "about": "A long, hot cut across rooms. Each shield layer takes 1 off its damage."},
	# Rare weapons with special effects (Zachary, 21 Nov: "a couple more weapons with rare effects"). "rare": sold
	# by special merchants (Ooma, when she comes) and found in events; the Moogli trader carries them for now.
	# Twin missile: loads two missiles one after the other ("stages"); aim once one is loaded to fire it, or aim
	# before and it waits for both. Ion: no hull damage; knocks off a shield layer and stops shields coming back for
	# a moment, or with shields down shuts the room's system off for "ion" seconds. Toxin dart: fills the room with
	# gas that hurts the crew for "gas" seconds (your suit keeps it off you). Fire beam: sets every room it cuts
	# across on fire (fire damages the system and hurts the crew until it burns out or is put out). Flak: shards
	# that scatter over the rooms round the target. Chain laser: each volley in a row charges "chain" faster (two
	# steps at most; it resets when unpowered).
	"twin_missile": {"name": "Twin missile", "type": "missile", "shots": 1, "damage": 2, "charge": 9.0, "stages": 2, "power": 2,
		"color": Color("ffb04a"), "ammo": 1, "rare": true, "price": 130,
		"about": "Loads two missiles. Fire one as soon as it's in, or wait and fire both."},
	"ion_blast": {"name": "Ion blast", "type": "ion", "shots": 1, "damage": 0, "ion": 6.0, "charge": 8.0, "power": 1,
		"color": Color("5ac8ff"), "rare": true, "price": 75,
		"about": "No hull damage. Strips a shield layer and jams it, or shuts a system off for a few seconds."},
	"toxin_dart": {"name": "Toxin dart", "type": "poison", "shots": 1, "damage": 0, "gas": 6.0, "charge": 11.0, "power": 1,
		"color": Color("9cff5a"), "rare": true, "price": 80,
		"about": "Fills a room with gas that hurts the crew inside. Shields stop it."},
	"fire_beam": {"name": "Fire beam", "type": "beam", "shots": 1, "damage": 0, "fire": true, "charge": 14.0, "power": 2, "length": 48.0,
		"color": Color("ff8a2a"), "rare": true, "price": 95,
		"about": "Sets every room it cuts across on fire. Any shield stops it."},
	"flak_cannon": {"name": "Flak cannon", "type": "flak", "shots": 3, "damage": 1, "charge": 13.0, "power": 2,
		"color": Color("e0c8a0"), "rare": true, "price": 85,
		"about": "Three shards that scatter over nearby rooms. Great for stripping shields."},
	"chain_laser": {"name": "Chain laser", "type": "laser", "shots": 2, "damage": 1, "charge": 12.0, "chain": 0.25, "power": 2,
		"color": Color("45e1d5"), "rare": true, "price": 95,
		"about": "Two shots. Charges faster with every volley in a row."},
	# Ivan's overcharged gun (phase 2). Needs no power; a hit on his weapons room drains its charge.
	"ivan_cannon": {"name": "Overcharged cannon", "type": "special", "shots": 1, "damage": 3, "charge": 16.0, "power": 0, "color": Color("ffd34a"),
		"price": 0, "about": "Ivan's. Not for sale."},
}

# Stores (Zachary, 21 Nov: a trading window like FTL's). Prices are first guesses: fuel, missiles and drone
# parts each, hull repair per point. Weapons sell back for half.
# By zone (23 Nov): each zone's store has its own weapons, prices and trade goods.
#   "markup"  - weapon prices times this
#   "goods"   - trade goods it sells (TRADE_VALUE x "sells_at")
#   "buys"    - trade goods it buys: item -> times TRADE_VALUE ("*" = anything in TRADE_VALUE)
# The pirate fence pays best for salvage, no questions asked; the Collective pays well for rare resources.
# Ooma's ship is the special merchant (claude/echo-landing-ship-combat.md): met on runs on the days she isn't on
# the station (not Wednesdays or Saturdays), selling the rare weapons.
const STORES := {
	"terran_depot": {"name": "Terran supply depot", "weapons": ["burst_laser", "heavy_laser", "missile_launcher", "cutting_beam"],
		"markup": 1.0, "fuel": 5, "missiles": 10, "drone_parts": 9, "repair": 6, "sells_at": 2.0,
		"goods": ["hull_plate", "coil_wire", "lithium_cell", "circuit_board"],
		"buys": {"*": 0.9}},
	"moogli_trader": {"name": "Moogli trader", "weapons": ["heavy_laser", "rabble_laser", "cutting_beam", "toxin_dart", "twin_missile"],
		"markup": 1.0, "fuel": 6, "missiles": 12, "drone_parts": 10, "repair": 8, "sells_at": 1.8,
		"goods": ["coil_wire", "lithium_cell", "rare_earths", "hull_plate"],
		"buys": {"*": 1.0}},
	"collective_market": {"name": "Collective market", "weapons": ["heavy_beam", "ion_blast", "missile_launcher", "burst_laser"],
		"markup": 1.1, "fuel": 7, "missiles": 11, "drone_parts": 8, "repair": 9, "sells_at": 2.0,
		"goods": ["helium_3", "rare_earths", "circuit_board", "lithium_cell"],
		"buys": {"*": 1.0, "rare_earths": 1.3, "helium_3": 1.3, "cobalt_60": 1.3, "void_sapphire": 1.2}},
	"pirate_fence": {"name": "Pirate fence", "weapons": ["rabble_laser", "flak_cannon", "missile_launcher", "heavy_laser"],
		"markup": 1.2, "fuel": 8, "missiles": 9, "drone_parts": 12, "repair": 10, "sells_at": 2.5,
		"goods": ["cobalt_60", "void_sapphire", "circuit_board"],
		"buys": {"*": 1.5}},
	"ooma": {"name": "Ooma's ship", "weapons": ["twin_missile", "ion_blast", "toxin_dart", "fire_beam", "flak_cannon", "chain_laser"],
		"markup": 1.1, "fuel": 6, "missiles": 10, "drone_parts": 8, "repair": 8, "sells_at": 2.2,
		"goods": ["void_sapphire", "helium_3", "cobalt_60", "circuit_board"],
		"buys": {"*": 1.2}},
}
const ZONE_STORE := {"Terran": "terran_depot", "Zaa'sh": "moogli_trader", "Collective": "collective_market", "Reach": "pirate_fence"}

# What trade goods are worth (Bram's price in main.gd SELL, where he buys them). Stores buy and sell around this.
const TRADE_VALUE := {"scrap": 2, "hull_plate": 25, "coil_wire": 15, "circuit_board": 45, "lithium_cell": 35,
	"rare_earths": 25, "helium_3": 80, "cobalt_60": 70, "void_sapphire": 100}


# The starter fighter, redrawn after the intro movie and approved by Zachary (21 Nov): plane wings, engine pods out
# behind, a 2 x 2 cockpit under a long canopy. 7 x 4 cells (168 x 96). Art by tools/dev/ship_art/starter.py:
# art/ships/starter/hull.png outside, interior.png the cut-away; art/lunar/player_ship.png is its four repair stages
# for the Shuttle Bay. A single-seat fighter: behind the cockpit are sealed bays only the repair drone gets into,
# through small hatches (the "doors" below). Other ships are walkable all through.
const STARTER := {
	# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
	"airlocks": [[Vector2i(3, 2), Vector2i(3, 3)]],
	"name": "Your fighter",
	"art": "res://art/ships/starter/hull.png", "frames": 1, "frame": 0, "size": Vector2(168, 96),
	"interior": "res://art/ships/starter/interior.png", "art_scale": 2,    # double resolution: story2x.py
	"hull": 12, "reactor": 6, "drones": 1, "door_level": 1,
	"weapons": ["burst_laser", ""],          # "" is an empty slot; bigger ships have more slots
	"mounts": [Vector2(66, 16), Vector2(66, 82)],   # each weapon slot's gun, on the housings near the wing tips
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

# Your first bigger ship, after Freya's quest (the tarp-covered fighter in the bay), at double resolution: walkable
# all through, for a crew. Art and rooms: tools/dev/ship_art/story2x.py. Not wired in yet: the battle still
# assumes the starter (one pilot and the repair drone); crew of your own come with this ship. Stats are first guesses.
const COVERED_FIGHTER := {
	# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
	"airlocks": [[Vector2i(2, 2), Vector2i(2, 1)], [Vector2i(2, 2), Vector2i(2, 3)]],
	"name": "Covered fighter",
	"art": "res://art/ships/covered_fighter/hull.png", "frames": 1, "frame": 0, "size": Vector2(216, 120),
	"interior": "res://art/ships/covered_fighter/interior.png", "art_scale": 2,
	"hull": 16, "reactor": 8, "drones": 0, "door_level": 1,
	"weapons": ["burst_laser", "", ""],
	"mounts": [Vector2(169, 40), Vector2(170.5, 80), Vector2(108, 15.5), Vector2(108, 104.5)],
	# boarding pods and a medbay (Zachary, 22 Nov; claude/echo-landing-boarding.md); not used in battle until boarding
	"systems": {"shields": [2, 2], "engines": [2, 1], "weapons": [3, 2], "life": [1, 1], "pilot": [1, 1],
		"pods": [2, 1], "medbay": [1, 1]},
	"rooms": [
		{"id": "pods", "label": "Boarding pods", "sys": "pods", "cells": Rect2i(3, 2, 1, 1), "crew": true},
		{"id": "crew", "label": "Crew deck", "sys": "", "cells": Rect2i(4, 2, 1, 1), "crew": true},
		{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 2, 1, 1), "crew": true},
		{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(2, 2, 1, 1), "crew": true},
		{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(3, 1, 2, 1), "crew": true},
		{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(3, 3, 2, 1), "crew": true},
		{"id": "medbay", "label": "Medbay", "sys": "medbay", "cells": Rect2i(5, 2, 1, 1), "crew": true},
		{"id": "cockpit", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(6, 2, 2, 1), "crew": true},
	],
	"doors": [
		[Vector2i(1, 2), Vector2i(2, 2)], [Vector2i(2, 2), Vector2i(3, 2)], [Vector2i(3, 2), Vector2i(3, 1)],
		[Vector2i(3, 2), Vector2i(3, 3)], [Vector2i(3, 2), Vector2i(4, 2)], [Vector2i(4, 2), Vector2i(5, 2)],
		[Vector2i(5, 2), Vector2i(6, 2)],
	],
}

# Enemy ships. "shape" is the outline drawn until real art exists (art/ships/<id>.png, facing left).
const ENEMIES := {
	# Drawn at double resolution (Zachary, 21 Nov: "lets double the pixels"): 48 art px per cell, so "art_scale" 2.
	# "size" and every room stay in 24-px cells; the battle fits the picture on its own pixels. Art and its rooms:
	# tools/dev/ship_art/rabble_cutter_2x.py (ROOMS and DOORS there must match these). Art faces right; the battle
	# mirrors ships with art so they face you.
	"rabble_cutter": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(2, 1), Vector2i(2, 0)]],
		"name": "Rabble Cutter", "size": Vector2(144, 96), "hull": 8, "crew": 3,
		"art": "res://art/ships/rabble_cutter/hull.png", "interior": "res://art/ships/rabble_cutter/interior.png", "art_scale": 2,
		"weapons": ["rabble_laser", "rabble_laser"],
		# Where guns attach to the hull's sides near the front, FTL-style (Zachary, 21 Nov): just outside the hull edge,
		# in the order guns fill them: top front, bottom front, top back, bottom back. Whatever guns the ship spawns
		# with go on the first ones; the game draws them there.
		"mounts": [Vector2(93, 15.5), Vector2(93, 80.5), Vector2(60, 14), Vector2(60, 80)],
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
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(2, 1), Vector2i(2, 0)], [Vector2i(2, 4), Vector2i(2, 5)]],
		"name": "Ivan's flagship", "size": Vector2(216, 144), "hull": 14, "crew": 5,
		"art": "res://art/ships/ivan_flagship/hull.png", "interior": "res://art/ships/ivan_flagship/interior.png", "art_scale": 2,
		"weapons": ["rabble_laser", "heavy_laser"],
		"mounts": [Vector2(176.5, 39.5), Vector2(177.5, 104.5), Vector2(204, 72), Vector2(142.5, 15.5), Vector2(142.5, 128.5)],
		# "cannon": the room for his special weapon (Zachary, 21 Nov, like FTL's special weapon rooms). Crewed, the
		# cannon charges faster; damaged, it can't charge, and a hit there drains it.
		"systems": {"shields": [2, 2], "engines": [2, 2], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1], "cannon": [1, 1]},
		"overcharge_at": 0.5,              # at half hull he brings out the cannon
		"rooms": [
			{"id": "crew", "label": "Crew deck", "sys": "", "cells": Rect2i(5, 2, 2, 2)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(1, 1, 2, 1)},
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 2, 2, 2)},
			{"id": "brig", "label": "Brig", "sys": "", "cells": Rect2i(1, 4, 2, 1)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(3, 1, 2, 2)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(3, 3, 2, 2)},
			{"id": "cannon", "label": "Cannon", "sys": "cannon", "cells": Rect2i(5, 1, 2, 1)},
			{"id": "hold_bottom", "label": "Hold", "sys": "", "cells": Rect2i(5, 4, 2, 1)},
			{"id": "pilot", "label": "Bridge", "sys": "pilot", "cells": Rect2i(7, 2, 1, 2)},
		],
		"doors": [
			[Vector2i(1, 1), Vector2i(1, 2)], [Vector2i(1, 3), Vector2i(1, 4)], [Vector2i(2, 2), Vector2i(3, 2)],
			[Vector2i(2, 3), Vector2i(3, 3)], [Vector2i(4, 2), Vector2i(5, 2)], [Vector2i(4, 3), Vector2i(5, 3)],
			[Vector2i(6, 1), Vector2i(6, 2)], [Vector2i(6, 3), Vector2i(6, 4)], [Vector2i(6, 2), Vector2i(7, 2)],
		],
	},
	# Pirate bases at double resolution (art and rooms: tools/dev/ship_art/bases2x.py INSIDES, which these must match).
	# Asteroids don't dodge: no engines, so no evasion. Their guns sit on the turret rings. Stats are first guesses.
	"pirate_stronghold": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(4, 2), Vector2i(4, 1)]],
		"name": "Pirate stronghold", "size": Vector2(192, 144), "hull": 16, "crew": 4,
		"art": "res://art/ships/pirate_stronghold/hull.png", "interior": "res://art/ships/pirate_stronghold/interior.png", "art_scale": 2,
		"weapons": ["heavy_laser", "rabble_laser"],
		"mounts": [Vector2(147, 41), Vector2(147, 103), Vector2(57, 40), Vector2(57, 104)],
		"systems": {"shields": [4, 4], "weapons": [3, 3], "life": [1, 1], "pilot": [1, 1]},
		"rooms": [
			{"id": "crew", "label": "Barracks", "sys": "", "cells": Rect2i(4, 2, 1, 2)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(3, 2, 1, 1)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(3, 3, 1, 1)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(5, 2, 1, 1)},
			{"id": "pilot", "label": "Command", "sys": "pilot", "cells": Rect2i(5, 3, 1, 1)},
		],
		"doors": [[Vector2i(3, 2), Vector2i(4, 2)], [Vector2i(3, 3), Vector2i(4, 3)], [Vector2i(4, 2), Vector2i(5, 2)], [Vector2i(4, 3), Vector2i(5, 3)]],
	},
	"rabble_nest": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(4, 2), Vector2i(4, 1)], [Vector2i(3, 3), Vector2i(3, 4)]],
		"name": "The Nest", "size": Vector2(240, 144), "hull": 24, "crew": 6,
		"art": "res://art/ships/rabble_nest/hull.png", "interior": "res://art/ships/rabble_nest/interior.png", "art_scale": 2,
		"weapons": ["heavy_laser", "heavy_laser", "rabble_laser"],
		"mounts": [Vector2(152, 40), Vector2(152, 104), Vector2(67, 40), Vector2(67, 106), Vector2(30, 70)],
		"systems": {"shields": [4, 4], "weapons": [4, 4], "life": [2, 2], "pilot": [1, 1]},
		"rooms": [
			{"id": "crew", "label": "Barracks", "sys": "", "cells": Rect2i(4, 2, 1, 2)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(3, 2, 1, 1)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(3, 3, 1, 1)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(5, 2, 1, 1)},
			{"id": "pilot", "label": "Command", "sys": "pilot", "cells": Rect2i(5, 3, 1, 1)},
			{"id": "dock", "label": "Dock", "sys": "", "cells": Rect2i(6, 2, 1, 2)},
			{"id": "hangar", "label": "Hangar", "sys": "", "cells": Rect2i(7, 2, 2, 2)},
		],
		"doors": [[Vector2i(3, 2), Vector2i(4, 2)], [Vector2i(3, 3), Vector2i(4, 3)], [Vector2i(4, 2), Vector2i(5, 2)], [Vector2i(4, 3), Vector2i(5, 3)], [Vector2i(5, 2), Vector2i(6, 2)], [Vector2i(6, 2), Vector2i(7, 2)]],
	},
}

# Ana's fight (second flight, Zachary 21 Nov). At half hull ("break_at") the battle stops: her own crew, Ivan's
# loyalists, turn on her, and main.gd starts the fight against their gunship.
const ANA_SHIPS := {
	# Both at double resolution (art_scale 2). Art and rooms: tools/dev/ship_art/story2x.py (INSIDES there must
	# match these rooms and doors). Guns attach at "mounts" on the hull's sides, front pair first.
	"ana_corsair": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(2, 1), Vector2i(2, 0)], [Vector2i(2, 3), Vector2i(2, 4)]],
		"name": "Ana's corsair", "size": Vector2(168, 120), "hull": 12, "crew": 4,
		"art": "res://art/ships/ana_corsair/hull.png", "interior": "res://art/ships/ana_corsair/interior.png", "art_scale": 2,
		"weapons": ["rabble_laser", "heavy_laser"],
		"mounts": [Vector2(84, 40), Vector2(84, 80), Vector2(51, 14), Vector2(51, 106)],
		"systems": {"shields": [2, 2], "engines": [2, 2], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1]},
		"break_at": 0.5,
		"rooms": [
			{"id": "crew", "label": "Crew", "sys": "", "cells": Rect2i(1, 2, 1, 1)},
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 1, 2, 1)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(1, 3, 2, 1)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(2, 2, 1, 1)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(3, 2, 1, 1)},
			{"id": "chart", "label": "Charts", "sys": "", "cells": Rect2i(4, 2, 1, 1)},
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(5, 2, 1, 1)},
		],
		"doors": [
			[Vector2i(1, 1), Vector2i(1, 2)], [Vector2i(1, 2), Vector2i(1, 3)], [Vector2i(1, 2), Vector2i(2, 2)],
			[Vector2i(2, 2), Vector2i(3, 2)], [Vector2i(3, 2), Vector2i(4, 2)], [Vector2i(4, 2), Vector2i(5, 2)],
		],
	},
	"loyalist_gunship": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(3, 1), Vector2i(3, 0)]],
		"name": "Loyalist gunship", "size": Vector2(120, 96), "hull": 8, "crew": 3,
		"art": "res://art/ships/loyalist_gunship/hull.png", "interior": "res://art/ships/loyalist_gunship/interior.png", "art_scale": 2,
		"weapons": ["rabble_laser", "rabble_laser"],
		"mounts": [Vector2(80.5, 14), Vector2(84.5, 80.5), Vector2(47.5, 16), Vector2(51.5, 80)],
		"systems": {"shields": [2, 2], "engines": [1, 1], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1]},
		"rooms": [
			{"id": "crew", "label": "Crew", "sys": "", "cells": Rect2i(3, 1, 1, 1)},
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 1, 1, 2)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(2, 1, 1, 1)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(2, 2, 1, 1)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(3, 2, 1, 1)},
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(4, 1, 1, 2)},
		],
		"doors": [
			[Vector2i(1, 1), Vector2i(2, 1)], [Vector2i(1, 2), Vector2i(2, 2)], [Vector2i(2, 1), Vector2i(3, 1)],
			[Vector2i(2, 2), Vector2i(3, 2)], [Vector2i(3, 1), Vector2i(3, 2)], [Vector2i(3, 1), Vector2i(4, 1)],
		],
	},
}


# The culture ships (Claude, 21 Nov; art approved by Zachary), at double resolution (art_scale 2). Generated from
# tools/dev/ship_art/fleet2x.py INSIDES (rooms, doors, mounts), so art and game agree; stats are first guesses to
# tune. Each also comes Rabble-repainted: enemy("<id>_rabble") flies it as a pirate (hull_rabble.png art).
const CULTURE_SHIPS := {
	"terran_patrol": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(3, 1), Vector2i(3, 0)]],
		"name": "Terran patrol", "size": Vector2(168, 96), "hull": 10, "crew": 4,
		"art": "res://art/ships/terran_patrol/hull.png", "interior": "res://art/ships/terran_patrol/interior.png", "art_scale": 2,
		"weapons": ["burst_laser", "missile_launcher"],
		"mounts": [Vector2(106, 15.5), Vector2(106, 80.5), Vector2(73, 14), Vector2(73, 80)],
		"systems": {"shields": [2, 2], "engines": [2, 2], "weapons": [3, 3], "life": [1, 1], "pilot": [1, 1]},
		"rooms": [
			{"id": "crew", "label": "Crew", "sys": "", "cells": Rect2i(3, 1, 2, 1)},
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 1, 1, 2)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(2, 1, 1, 1)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(2, 2, 1, 1)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(3, 2, 2, 1)},
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(5, 1, 1, 2)},
		],
		"doors": [[Vector2i(1, 1), Vector2i(2, 1)], [Vector2i(1, 2), Vector2i(2, 2)], [Vector2i(2, 1), Vector2i(3, 1)], [Vector2i(2, 2), Vector2i(3, 2)], [Vector2i(3, 1), Vector2i(3, 2)], [Vector2i(4, 1), Vector2i(5, 1)]],
	},
	"zaash_skiff": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(2, 2), Vector2i(2, 3)]],
		"name": "Zaa'sh skiff", "size": Vector2(144, 96), "hull": 9, "crew": 3,
		"art": "res://art/ships/zaash_skiff/hull.png", "interior": "res://art/ships/zaash_skiff/interior.png", "art_scale": 2,
		"weapons": ["heavy_laser", "cutting_beam"],
		"mounts": [Vector2(68, 16), Vector2(66, 81.5), Vector2(35, 16), Vector2(33, 82)],
		"systems": {"shields": [2, 2], "engines": [2, 2], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1]},
		"rooms": [
			{"id": "crew", "label": "Crew", "sys": "", "cells": Rect2i(3, 2, 1, 1)},
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 1, 1, 2)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(2, 1, 1, 1)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(2, 2, 1, 1)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(3, 1, 1, 1)},
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(4, 1, 1, 2)},
		],
		"doors": [[Vector2i(1, 1), Vector2i(2, 1)], [Vector2i(1, 2), Vector2i(2, 2)], [Vector2i(2, 1), Vector2i(3, 1)], [Vector2i(2, 2), Vector2i(3, 2)], [Vector2i(3, 1), Vector2i(4, 1)]],
	},
	"vuultam_garden": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(2, 1), Vector2i(2, 0)]],
		"name": "Vuultam garden ship", "size": Vector2(168, 96), "hull": 10, "crew": 3,
		"art": "res://art/ships/vuultam_garden/hull.png", "interior": "res://art/ships/vuultam_garden/interior.png", "art_scale": 2,
		"weapons": ["rabble_laser"],
		"mounts": [Vector2(106, 15.5), Vector2(106, 80.5), Vector2(73, 16), Vector2(73, 80)],
		"systems": {"shields": [4, 4], "engines": [1, 1], "weapons": [1, 1], "life": [2, 2], "pilot": [1, 1]},
		"rooms": [
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 1, 1, 2)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(2, 1, 2, 2)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(4, 1, 1, 1)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(4, 2, 1, 1)},
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(5, 1, 1, 2)},
		],
		"doors": [[Vector2i(1, 1), Vector2i(2, 1)], [Vector2i(1, 2), Vector2i(2, 2)], [Vector2i(3, 1), Vector2i(4, 1)], [Vector2i(3, 2), Vector2i(4, 2)], [Vector2i(4, 1), Vector2i(5, 1)]],
	},
	"moogli_trader": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(2, 1), Vector2i(2, 0)], [Vector2i(1, 2), Vector2i(1, 3)]],
		"name": "Moogli trader", "size": Vector2(144, 96), "hull": 8, "crew": 3,
		"art": "res://art/ships/moogli_trader/hull.png", "interior": "res://art/ships/moogli_trader/interior.png", "art_scale": 2,
		"weapons": ["rabble_laser"],
		"mounts": [Vector2(101.5, 15.5), Vector2(101, 80.5)],
		"systems": {"shields": [2, 2], "engines": [1, 1], "weapons": [1, 1], "life": [1, 1], "pilot": [1, 1]},
		"rooms": [
			{"id": "crew", "label": "Crew", "sys": "", "cells": Rect2i(2, 2, 1, 1)},
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 1, 1, 2)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(2, 1, 1, 1)},
			{"id": "hold", "label": "Hold", "sys": "", "cells": Rect2i(3, 1, 1, 2)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(4, 1, 1, 1)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(4, 2, 1, 1)},
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(5, 1, 1, 2)},
		],
		"doors": [[Vector2i(1, 1), Vector2i(2, 1)], [Vector2i(1, 2), Vector2i(2, 2)], [Vector2i(2, 1), Vector2i(3, 1)], [Vector2i(2, 2), Vector2i(3, 2)], [Vector2i(3, 1), Vector2i(4, 1)], [Vector2i(3, 2), Vector2i(4, 2)], [Vector2i(4, 1), Vector2i(5, 1)]],
	},
	"ervani_courier": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(2, 1), Vector2i(2, 0)]],
		"name": "Ervani courier", "size": Vector2(144, 96), "hull": 7, "crew": 3,
		"art": "res://art/ships/ervani_courier/hull.png", "interior": "res://art/ships/ervani_courier/interior.png", "art_scale": 2,
		"weapons": ["rabble_laser", "rabble_laser"],
		"mounts": [Vector2(41, 15), Vector2(42, 80.5), Vector2(131.5, 41), Vector2(131.5, 55)],
		"systems": {"shields": [2, 2], "engines": [3, 3], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1]},
		"rooms": [
			{"id": "crew", "label": "Crew", "sys": "", "cells": Rect2i(2, 1, 1, 1)},
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 1, 1, 2)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(2, 2, 1, 1)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(3, 1, 1, 1)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(3, 2, 1, 1)},
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(4, 1, 1, 2)},
		],
		"doors": [[Vector2i(1, 1), Vector2i(2, 1)], [Vector2i(1, 2), Vector2i(2, 2)], [Vector2i(2, 1), Vector2i(3, 1)], [Vector2i(2, 2), Vector2i(3, 2)], [Vector2i(3, 1), Vector2i(4, 1)]],
	},
	"scyldar_lantern": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(2, 1), Vector2i(2, 0)], [Vector2i(1, 2), Vector2i(1, 3)]],
		"name": "Scyldar lantern ship", "size": Vector2(168, 96), "hull": 10, "crew": 3,
		"art": "res://art/ships/scyldar_lantern/hull.png", "interior": "res://art/ships/scyldar_lantern/interior.png", "art_scale": 2,
		"weapons": ["heavy_laser"],
		"mounts": [Vector2(107, 15.5), Vector2(107, 80.5), Vector2(74, 16), Vector2(74, 80)],
		"systems": {"shields": [2, 2], "engines": [2, 2], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1]},
		"rooms": [
			{"id": "crew", "label": "Crew", "sys": "", "cells": Rect2i(2, 2, 1, 1)},
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 1, 1, 2)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(2, 1, 1, 1)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(3, 1, 1, 1)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(3, 2, 1, 1)},
			{"id": "hold", "label": "Hold", "sys": "", "cells": Rect2i(4, 1, 1, 2)},
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(5, 1, 1, 2)},
		],
		"doors": [[Vector2i(1, 1), Vector2i(2, 1)], [Vector2i(1, 2), Vector2i(2, 2)], [Vector2i(2, 1), Vector2i(3, 1)], [Vector2i(2, 2), Vector2i(3, 2)], [Vector2i(3, 1), Vector2i(4, 1)], [Vector2i(4, 1), Vector2i(5, 1)]],
	},
	"arachnay_weaver": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(2, 1), Vector2i(2, 0)], [Vector2i(1, 2), Vector2i(1, 3)]],
		"name": "Arachnay weaver", "size": Vector2(144, 96), "hull": 9, "crew": 4,
		"art": "res://art/ships/arachnay_weaver/hull.png", "interior": "res://art/ships/arachnay_weaver/interior.png", "art_scale": 2,
		"weapons": ["rabble_laser", "heavy_laser"],
		"mounts": [Vector2(110.5, 8.5), Vector2(110.5, 87.5), Vector2(77.5, 15.5), Vector2(77.5, 80.5)],
		"systems": {"shields": [2, 2], "engines": [2, 2], "weapons": [2, 2], "life": [1, 1], "pilot": [1, 1]},
		"rooms": [
			{"id": "crew", "label": "Crew", "sys": "", "cells": Rect2i(2, 2, 1, 1)},
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 1, 1, 2)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(2, 1, 1, 1)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(3, 1, 1, 1)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(3, 2, 1, 1)},
			{"id": "hold", "label": "Hold", "sys": "", "cells": Rect2i(4, 1, 1, 2)},
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(5, 1, 1, 2)},
		],
		"doors": [[Vector2i(1, 1), Vector2i(2, 1)], [Vector2i(1, 2), Vector2i(2, 2)], [Vector2i(2, 1), Vector2i(3, 1)], [Vector2i(2, 2), Vector2i(3, 2)], [Vector2i(3, 1), Vector2i(4, 1)], [Vector2i(4, 1), Vector2i(5, 1)]],
	},
	"collective_freighter": {
		# airlocks to space, for venting fires (tools/dev/ship_art/kit2x.py pick_airlocks)
		"airlocks": [[Vector2i(2, 1), Vector2i(2, 0)], [Vector2i(1, 3), Vector2i(1, 4)]],
		"name": "Collective freighter", "size": Vector2(192, 120), "hull": 12, "crew": 4,
		"art": "res://art/ships/collective_freighter/hull.png", "interior": "res://art/ships/collective_freighter/interior.png", "art_scale": 2,
		"weapons": ["rabble_laser"],
		"mounts": [Vector2(154.5, 37.5), Vector2(154.5, 83.5), Vector2(41, 15.5), Vector2(121.5, 104.5)],
		"systems": {"shields": [2, 2], "engines": [1, 1], "weapons": [1, 1], "life": [1, 1], "pilot": [1, 1]},
		"rooms": [
			{"id": "crew", "label": "Crew", "sys": "", "cells": Rect2i(3, 3, 1, 1)},
			{"id": "engines", "label": "Engines", "sys": "engines", "cells": Rect2i(1, 1, 1, 3)},
			{"id": "corridor", "label": "Corridor", "sys": "", "cells": Rect2i(2, 2, 5, 1)},
			{"id": "life", "label": "Oxygen", "sys": "life", "cells": Rect2i(2, 1, 1, 1)},
			{"id": "shields", "label": "Shields", "sys": "shields", "cells": Rect2i(3, 1, 1, 1)},
			{"id": "hold_top", "label": "Hold", "sys": "", "cells": Rect2i(4, 1, 2, 1)},
			{"id": "weapons", "label": "Weapons", "sys": "weapons", "cells": Rect2i(2, 3, 1, 1)},
			{"id": "hold_bottom", "label": "Hold", "sys": "", "cells": Rect2i(4, 3, 2, 1)},
			{"id": "pilot", "label": "Cockpit", "sys": "pilot", "cells": Rect2i(7, 2, 1, 1)},
		],
		"doors": [[Vector2i(1, 2), Vector2i(2, 2)], [Vector2i(2, 2), Vector2i(2, 1)], [Vector2i(3, 2), Vector2i(3, 1)], [Vector2i(4, 2), Vector2i(4, 1)], [Vector2i(2, 2), Vector2i(2, 3)], [Vector2i(3, 2), Vector2i(3, 3)], [Vector2i(4, 2), Vector2i(4, 3)], [Vector2i(6, 2), Vector2i(7, 2)]],
	},
}

# What a won fight pays: [credits, {item: count}].
const REWARDS := {
	"rabble_cutter": [40, {"hull_plate": 1, "scrap": 3}],
	"ivan_flagship": [150, {"hull_plate": 2, "coil_wire": 2, "scrap": 5, "circuit_board": 1}],
	"loyalist_gunship": [60, {"coil_wire": 1, "scrap": 3, "lithium_cell": 1}],
}


# Every enemy ship, whatever table it is in, built for battle.
static func enemy(id: String) -> Dictionary:
	if ENEMIES.has(id):
		return build(ENEMIES[id])
	if CULTURE_SHIPS.has(id):
		return build(CULTURE_SHIPS[id])
	# Rabble pirates fly other peoples' ships, haphazardly repainted (Zachary, 21 Nov): the same rooms, the repainted
	# art, and Rabble guns.
	if id.ends_with("_rabble") and CULTURE_SHIPS.has(id.trim_suffix("_rabble")):
		var base: String = id.trim_suffix("_rabble")
		var def: Dictionary = CULTURE_SHIPS[base].duplicate(true)
		def["name"] = "Rabble %s" % str(def["name"]).to_lower()
		def["art"] = "res://art/ships/%s/hull_rabble.png" % base
		def["interior"] = "res://art/ships/%s/interior_rabble.png" % base
		var guns: Array = []
		for i in range(maxi(2, (def["weapons"] as Array).size())):
			guns.append("rabble_laser")
		def["weapons"] = guns
		return build(def)
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
	for pair in ship.get("doors", []) + ship.get("airlocks", []):
		var a: Vector2i = pair[0]
		var b: Vector2i = pair[1]
		var across: bool = a.y == b.y
		var at := Vector2(maxi(a.x, b.x) * CELL, (a.y + 0.5) * CELL) if across else Vector2((a.x + 0.5) * CELL, maxi(a.y, b.y) * CELL)
		var ra: String = _room_at_cell(rooms, a)
		var rb: String = _room_at_cell(rooms, b)
		if ra == "":                 # an airlock: the room always on side a, space ("") on side b
			ra = rb
			rb = ""
		doors.append({"a": ra, "b": rb, "at": at, "across": across, "airlock": rb == "",
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
	"nest": {"label": "The Nest", "color": Color("ff4a3a")},
	"ooma": {"label": "Ooma's ship", "color": Color("ff9ad2")},
	"wreck": {"label": "Wreck", "color": Color("9ab4c8")},
	"quiet": {"label": "Quiet sector", "color": Color("8ee0c8")},
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


# ---------------------------------------------------------------- upgrades (23 Nov; mock-up approved by Zachary)
# At Freya's workbench before you set out, or from the map in space (a field refit). Each ship keeps its own
# levels (main.gd ship_ups[ship id]). Costs are first guesses: Scrip plus salvage.
const SHIP_DEFS := {"starter": STARTER, "covered_fighter": COVERED_FIGHTER}
const SHIP_NAMES := {"starter": "Your fighter", "covered_fighter": "Covered fighter"}
# system -> [highest level, Scrip for the first upgrade, Scrip added per level after]
const SYSTEM_UPGRADES := {
	"shields": [6, 60, 30], "engines": [6, 50, 30], "weapons": [6, 60, 30], "life": [3, 40, 30],
	"pilot": [3, 45, 30], "drones": [3, 45, 30], "pods": [3, 50, 30], "medbay": [3, 50, 30],
}
const SYSTEM_LABELS := {"shields": "Shields", "engines": "Engines", "weapons": "Weapons", "life": "Oxygen",
	"pilot": "Cockpit", "drones": "Drone bay", "pods": "Boarding pods", "medbay": "Medbay"}
const SYSTEM_EFFECTS := {"shields": "a shield layer for every two bars", "engines": "+1 bar of engines: more evasion",
	"weapons": "power for more or bigger guns", "life": "air refills faster", "pilot": "more evasion, a faster fold",
	"drones": "the drone repairs faster", "pods": "pods recharge faster", "medbay": "crew heal faster"}
const SYSTEM_ABOUT := {
	"shields": "Each layer stops one shot. A layer needs two bars of power.",
	"engines": "Engines give evasion and charge the fold drive. Every bar powered helps.",
	"weapons": "Each gun needs bars of weapons power to fire. More bars, more guns at once.",
	"life": "Oxygen refills the rooms' air. Matters when fires, breaches or airlocks thin it.",
	"pilot": "The cockpit gives evasion while crewed and charges the fold drive faster.",
	"drones": "The drone bay powers your repair drone. Higher levels make it work faster.",
	"pods": "Boarding pods carry your crew across. Higher levels recharge them faster.",
	"medbay": "The medbay heals crew standing in it. Higher levels heal faster.",
}
const REACTOR_MAX_ADD := 6                   # reactor bars you can add
const HULL_STEP := 2                         # hull added per plating level
const HULL_LEVELS := 4
const TANK_LEVELS := 2                       # each opens one more ring on runs, and one more fuel at launch
const TANK_COSTS := [[250, {"helium_3": 2, "hull_plate": 2}], [400, {"helium_3": 3, "hull_plate": 3, "cobalt_60": 1}]]
const TETHER_COST := [180, {"coil_wire": 4, "circuit_board": 1}]


# What a system upgrade to `level` costs: [Scrip, {item: count}].
static func system_cost(key: String, level: int) -> Array:
	var row: Array = SYSTEM_UPGRADES[key]
	var base: int = int(STARTER["systems"].get(key, COVERED_FIGHTER["systems"].get(key, [1, 1]))[0])
	var step: int = maxi(0, level - base - 1)
	var scrip: int = int(row[1]) + int(row[2]) * step
	var items := {}
	match level:
		2: items = {"coil_wire": 1}
		3: items = {"circuit_board": 1}
		4: items = {"circuit_board": 1, "coil_wire": 2}
		5: items = {"circuit_board": 2, "rare_earths": 1}
		_: items = {"circuit_board": 2, "cobalt_60": 1}
	return [scrip, items]


static func reactor_cost(added: int) -> Array:      # the cost of the (added+1)th extra bar
	var items := {"coil_wire": 1, "lithium_cell": 1}
	if added >= 2:
		items["circuit_board"] = 1
	return [40 + 15 * added, items]


static func hull_cost(level: int) -> Array:         # level 0 -> 1 is the first plating upgrade
	return [50 + 20 * level, {"hull_plate": 2 + level / 2}]


# Hired crew (23 Nov): Tally pins hirelings to the crew board in the Shuttle Bay. Each kind has a trait, as FTL's
# races do. [signing fee, trait text, fight_x, repair_x, heal_x]. Names are drawn for each board.
const HIRE_KINDS := {
	"human": [50, "Steady: no weak spots", 1.0, 1.0, 1.0],
	"zaash": [75, "Fierce: fights half again as hard", 1.5, 1.0, 1.0],
	"arachnay": [70, "Four hands: repairs faster", 1.0, 1.6, 1.0],
	"moogli": [60, "Hardy: heals faster in the medbay", 1.0, 1.0, 1.6],
	"vuultam": [65, "Patient: repairs and heals a little faster", 1.0, 1.25, 1.25],
	"ervani": [60, "Quick: fights and repairs a little better", 1.2, 1.2, 1.0],
	"scyldar": [70, "Tough: fights and heals better", 1.25, 1.0, 1.3],
}
const HIRE_NAMES := ["Dax", "Rook", "Mira", "Tesh", "Orrin", "Kell", "Sabe", "Juno", "Pell", "Vex", "Nim", "Harrow",
	"Lio", "Brask", "Ottie", "Quen", "Zarra", "Fen", "Wick", "Talla"]
const CREW_SEATS := {"starter": 0, "covered_fighter": 3}   # crew besides you
