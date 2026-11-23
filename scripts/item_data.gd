extends RefCounted
# Everything the player can carry, and what can be crafted.
# "icon" is the position of the picture in art/items.png (made by tools/build.py).
# "use" says what pressing Space does with it selected: "mine", "weapon", "eat", "hoe", "water", "plant",
# or nothing. Farming (21 Nov): the crops are placeholders until the economy chat's crop list; "crop" on a seed
# names what it grows (CROPS in scripts/main.gd).

const ITEMS = {
	"laser": {"name": "Mining laser", "icon": 0, "use": "mine",
			"desc": "Job's spare. Select it on the hotbar and hold Space (or the left button) on a vein or rock. Harder ore takes longer, and every cut tires you."},
	"spear": {"name": "Zaa'sh spear", "icon": 1, "use": "weapon",
			"desc": "It stabs: far and narrow. It was Vzz'ket's clutch-brother's. Bring it back clean."},
	"sword": {"name": "Zaa'sh sword", "icon": 2, "use": "weapon",
			"desc": "It swings: near and wide. It was Vzz'ket's clutch-brother's. Bring it back clean."},
	"iron_ore": {"name": "Iron ore", "icon": 3, "use": "",
			"desc": "Cut from the red veins in the mine. Two pour one iron bar in ore processing."},
	"copper_ore": {"name": "Copper ore", "icon": 4, "use": "",
			"desc": "Cut from the green veins in the mine. Two pour one copper bar in ore processing."},
	"iron_bar": {"name": "Iron bar", "icon": 5, "use": "",
			"desc": "Bram buys these. Three make a hull plate."},
	"copper_bar": {"name": "Copper bar", "icon": 6, "use": "",
			"desc": "Bram buys these. Two make a spool of coil wire."},
	"hull_plate": {"name": "Hull plate", "icon": 7, "use": "",
			"desc": "A pressed iron plate. Tikka needs these to patch your ship."},
	"coil_wire": {"name": "Coil wire", "icon": 8, "use": "",
			"desc": "Drawn copper wire. Tikka is very interested in this."},
	"chitin": {"name": "Bug shell", "icon": 9, "use": "",
			"desc": "A cave bug's shell, light and hard. Bram buys these."},
	"hide": {"name": "Lizard hide", "icon": 10, "use": "",
			"desc": "Tough, scaly hide from a rock lizard. Bram buys these."},
	"ration": {"name": "Ration pack six", "icon": 11, "use": "eat", "energy": 25,
			"desc": "Jasper's special. Select it and press Space to eat it: mends 5 hearts and 25 energy."},
	"stone": {"name": "Stone", "icon": 13, "use": "",
			"desc": "Plain moon rock, cut from the boulders in the mine. Bram pays a credit apiece; builders will want it."},
	"quartz": {"name": "Quartz", "icon": 14, "use": "",
			"desc": "Clear crystal from the caverns. Bram pays well; one day it will make glass and lenses."},
	"gold_ore": {"name": "Gold ore", "icon": 15, "use": "",
			"desc": "Rare yellow veins, deep in the caverns. Bram pays 40 credits a lump."},
	"titanium_ore": {"name": "Titanium ore", "icon": 16, "use": "",
			"desc": "Hard blue-grey ore from the steamy depths. It takes the laser a long time to cut."},
	"silica_sand": {"name": "Silica sand", "icon": 50, "use": "",
			"desc": "Pale sand drifted over the cavern rock. Fired, it makes glass; refined, the silicon in every circuit."},
	"lithium_salts": {"name": "Lithium salts", "icon": 51, "use": "",
			"desc": "Pink crystal blocks from the green and steamy caverns. The heart of every lithium cell."},
	"carbon": {"name": "Carbon", "icon": 17, "use": "",
			"desc": "Soft black graphite from the rock floors of the caverns. With iron, it makes steel."},
	"steel_bar": {"name": "Steel bar", "icon": 18, "use": "",
			"desc": "Two iron bars and a lump of carbon, worked on the Crafting page. Bram pays 30."},
	"steel_laser": {"name": "Steel mining laser", "icon": 19, "use": "mine", "tier": 2,
			"desc": "Job's old laser rebuilt in steel. It cuts faster than the basic one, and it can cut titanium."},
	"gold_bar": {"name": "Gold bar", "icon": 20, "use": "",
			"desc": "Poured from gold ore at any furnace. Bram pays 90."},
	"titanium_bar": {"name": "Titanium bar", "icon": 21, "use": "",
			"desc": "Poured from titanium ore at any furnace. Light and very strong. Bram pays 60."},
	"harbinger_scale": {"name": "Harbinger scale", "icon": 22, "use": "",
			"desc": "A plate from the Harbinger's hide, still warm. Tar'Besh would give a great deal to see it."},
	"medpack": {"name": "Medpack", "icon": 12, "use": "eat", "heal": 10,
			"desc": "From Maren in the medbay. Select it and press Space to mend every heart."},
	"hoe": {"name": "Hoe", "icon": 23, "use": "hoe",
			"desc": "Evarra's spare. Select it and press Space on the field in the Agri dome to dig a tile for planting."},
	"hydro_bed": {"name": "Hydroponic bed", "icon": 49, "use": "place",
			"desc": "A self-watering growing tray. Select it and press Space on open soil in the Agri dome to set it down; plant seeds in it like a dug tile. It waters itself every night."},
	"watering_can": {"name": "Watering can", "icon": 24, "use": "water",
			"desc": "Select it and press Space on a dug tile to water it. Crops only grow on days they were watered."},
	"crater_potato_seeds": {"name": "Crater potato seeds", "icon": 25, "use": "plant", "crop": "crater_potato",
			"desc": "Plant on a dug tile. Ready in 4 watered days."},
	"moon_wheat_seeds": {"name": "Moon wheat seeds", "icon": 26, "use": "plant", "crop": "moon_wheat",
			"desc": "Plant on a dug tile. Ready in 3 watered days."},
	"star_tomato_seeds": {"name": "Star tomato seeds", "icon": 27, "use": "plant", "crop": "star_tomato",
			"desc": "Plant on a dug tile. Ready in 6 watered days, then fruits again every 3."},
	"crater_potato": {"name": "Crater potato", "icon": 28, "use": "eat", "energy": 15, "heal": 1,
			"desc": "Lumpy, purple-skinned and filling. Bram buys them."},
	"moon_wheat": {"name": "Moon wheat", "icon": 29, "use": "",
			"desc": "Pale wheat that grows fast under the dome lights. Bram buys it; one day it will be flour."},
	"star_tomato": {"name": "Star tomato", "icon": 30, "use": "eat", "energy": 20, "heal": 1,
			"desc": "A five-pointed tomato, sweet and sharp. Bram pays well for them."},
	# Salvage from beaten ships (23 Nov). Icons 31-37 are the artist's (art/items/), copied in by tools/dev/relic_art.py.
	"scrap": {"name": "Scrap", "icon": 31, "use": "",
			"desc": "Twisted hull, cable and broken fittings from a beaten ship. Bram takes it by the sackful."},
	"circuit_board": {"name": "Circuit board", "icon": 32, "use": "",
			"desc": "Pulled whole from a wrecked console. Machines and blasters will need these."},
	"lithium_cell": {"name": "Lithium cell", "icon": 33, "use": "",
			"desc": "A charged power cell from a ship's battery rack. Bram buys them."},
	"rare_earths": {"name": "Rare earths", "icon": 34, "use": "",
			"desc": "Ore from a freighter's hold. It makes the magnets inside motors."},
	"helium_3": {"name": "Helium-3", "icon": 35, "use": "",
			"desc": "A bottle of fusion fuel from a ship's tanks. Worth a great deal to the right buyer."},
	"cobalt_60": {"name": "Cobalt-60", "icon": 36, "use": "",
			"desc": "A shielded canister from deep in the Reach. Handle with care; Bram pays well for it."},
	"void_sapphire": {"name": "Void sapphire", "icon": 37, "use": "",
			"desc": "A deep blue gem, someone's hidden treasure. Bram pays a fortune; others might love it more."},
	# Relics (23 Nov): rare finds for Tar'Besh's museum. Give them at his desk or to him. "relic" is the picture
	# in art/museum/ and "gallery" the wing of cases it goes to first (MapData.MUSEUM_SLOTS). "pirate" relics drop
	# from beaten Chernobog (pirate) ships; the others come from space events ("relic: <name>" in scripts/space_events.gd).
	"relic_pilgrim_bell": {"name": "Pilgrim's bell", "icon": 38, "use": "", "relic": "pilgrim_bell", "gallery": "Peoples of the Rim",
			"desc": "A silver bell from a pilgrim ship. It still rings true. For Tar'Besh's museum."},
	"relic_station_crest": {"name": "Station crest plate", "icon": 39, "use": "", "relic": "station_crest", "gallery": "The first settlers",
			"desc": "The old crest of a station long gone, unbolted from a dead beacon. For Tar'Besh's museum."},
	"relic_duellist_bell": {"name": "Duellist's bell", "icon": 40, "use": "", "relic": "duellist_bell", "gallery": "Peoples of the Rim",
			"desc": "A Zaa'sh pilot's mast bell, given in respect. For Tar'Besh's museum."},
	"relic_convoy_charm": {"name": "Convoy charm", "icon": 41, "use": "", "relic": "convoy_charm", "gallery": "Peoples of the Rim",
			"desc": "A carved charm from a refugee convoy, smooth from being held. For Tar'Besh's museum."},
	"relic_garden_seeds": {"name": "Garden-ship seeds", "icon": 42, "use": "", "relic": "garden_seeds", "gallery": "Natural history",
			"desc": "Strange seeds, warm to the touch, from a Vuultam garden ship. For Tar'Besh's museum."},
	"relic_rabble_flag": {"name": "Torn Chernobog banner", "icon": 43, "use": "", "relic": "rabble_flag", "gallery": "Precursor gallery", "pirate": true,
			"desc": "A raider's banner, scorched where you hit them. For Tar'Besh's museum."},
	"relic_bone_dice": {"name": "Pirate's bone dice", "icon": 44, "use": "", "relic": "bone_dice", "gallery": "Precursor gallery", "pirate": true,
			"desc": "Loaded, of course. Found in a raider captain's pocket. For Tar'Besh's museum."},
	"relic_star_compass": {"name": "Raider's star compass", "icon": 45, "use": "", "relic": "star_compass", "gallery": "Precursor gallery", "pirate": true,
			"desc": "A brass compass that points at no star you know. For Tar'Besh's museum."},
	"relic_captain_signet": {"name": "Chernobog captain's signet", "icon": 46, "use": "", "relic": "captain_signet", "gallery": "Precursor gallery", "pirate": true,
			"desc": "A heavy gold ring with a red stone, worn by a Chernobog captain. For Tar'Besh's museum."},
	"relic_gold_tooth": {"name": "Raider's gold tooth", "icon": 47, "use": "", "relic": "gold_tooth", "gallery": "Precursor gallery", "pirate": true,
			"desc": "A gold fang on a cord. You decide not to ask. For Tar'Besh's museum."},
	"relic_captain_log": {"name": "Pirate captain's log", "icon": 48, "use": "", "relic": "captain_log", "gallery": "Precursor gallery", "pirate": true,
			"desc": "Years of raids in a cramped hand, with the Landing on the last page. For Tar'Besh's museum."},
}

# The relics, and the ones Chernobog ships can drop.
static func relics() -> Array:
	var out: Array = []
	for id in ITEMS:
		if ITEMS[id].has("relic"):
			out.append(id)
	return out


static func pirate_relics() -> Array:
	var out: Array = []
	for id in ITEMS:
		if bool(ITEMS[id].get("pirate", false)):
			out.append(id)
	return out


# The relic item with this name ("Pilgrim's bell"), or "" (space events name relics by their names).
static func relic_named(relic_name: String) -> String:
	for id in ITEMS:
		if ITEMS[id].has("relic") and str(ITEMS[id]["name"]).to_lower() == relic_name.to_lower():
			return id
	return ""

# What a furnace makes from each ore you can hold.
const SMELTS = {"iron_ore": "iron_bar", "copper_ore": "copper_bar", "gold_ore": "gold_bar", "titanium_ore": "titanium_bar"}

# What the Crafting page offers. "needs" is item -> how many.
const RECIPES = [
	{"makes": "hull_plate", "n": 1, "needs": {"iron_bar": 3}},
	{"makes": "coil_wire", "n": 1, "needs": {"copper_bar": 2}},
	{"makes": "steel_bar", "n": 1, "needs": {"iron_bar": 2, "carbon": 1}},
	{"makes": "steel_laser", "n": 1, "needs": {"laser": 1, "steel_bar": 3, "coil_wire": 1}},
	{"makes": "hydro_bed", "n": 1, "needs": {"iron_bar": 1, "copper_bar": 1}},
]
