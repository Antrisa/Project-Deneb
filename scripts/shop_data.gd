extends RefCounted
# The station's shops, prices, geodes, drinks, cooking and wearables (Zachary, 23 Nov 2026).
# Reviewed in the Sheet "Echo Landing price sheet (draft, 23 Nov)": https://claude.ai/artifact/UB9Gc7Q2wRcLzdWekgpzU2
#
# Selling: every item has one VALUE (credits). The shop that buys its kind (BUYS) pays all of it, and so does the
# shipping crate (Zachary: "shipping bin pays most"). Bram's counter takes anything on the list, at BRAM_RATE.
# Buying: shops charge more than anything is worth, so buying something back is never a profit. Stock has no
# limit (Zachary, 23 Nov: "everything can be inf buying if you got the money").
# Shops open by talking to the keeper while they are at work (main.gd _shop_offer); the screen is the datapad's
# Shop page (datapad/datapad.gd _shop), fed by scripts/shops.gd.

const BRAM_RATE := 0.8

# What each item is worth. Relics are not on the list: they are for Tar'Besh's museum.
const VALUE := {
	# ore and rock (Tikka)
	"stone": 1, "iron_ore": 5, "copper_ore": 7, "aluminium_ore": 10, "gold_ore": 40, "titanium_ore": 25, "carbon": 6,
	"silica_sand": 4, "lithium_salts": 30, "sulphur": 15, "basalt_core": 60,
	# bars and parts (Tikka)
	"iron_bar": 12, "copper_bar": 18, "aluminium_bar": 35, "steel_bar": 32, "gold_bar": 90, "titanium_bar": 60,
	"hull_plate": 42, "coil_wire": 42, "glass_pane": 12, "refined_silicon": 30, "brick": 5, "magnet": 50, "motor": 140,
	"precision_lens": 160, "high_density_core": 600,
	# salvage (Tikka)
	"scrap": 2, "circuit_board": 45, "lithium_cell": 35, "rare_earths": 25, "helium_3": 80, "cobalt_60": 70,
	# creature drops (Sesska)
	"chitin": 6, "hide": 10,
	# crops and cooking (Jasper)
	"crater_potato": 18, "moon_wheat": 10, "star_tomato": 30, "flour": 10, "milk_powder": 3,
	"moon_wheat_bread": 32, "crater_potato_mash": 46, "star_tomato_soup": 68, "mess_hall_stew": 80, "station_breakfast": 70,
	# ice (Rusk); Ilsa's vine, from Rusk's 8 (23 Nov): grapes (Jasper buys them), and the wine Rusk's cask makes from
	# them (nobody buys it at full value but the shipping crate: Bram's cousins on the trade lanes)
	"ice": 6, "nebula_grape": 45, "nebula_wine": 350,
	# gems, minerals and geodes (Job)
	"quartz": 12, "thermal_quartz": 45, "moon_opal": 60, "crater_garnet": 90, "void_sapphire": 140,
	"lunar_agate": 20, "anorthosite": 18, "moon_olivine": 25, "regolith_jasper": 22, "ilmenite": 45, "selenite_rose": 50,
	"armalcolite": 120, "orange_glass": 40, "spinel": 45, "basalt_glass": 35, "fire_opal": 85, "tranquillityite": 110,
	"geode": 5, "cavern_geode": 10,
}

# Who pays full value for what. Bram is the general dealer: he buys anything in VALUE, at BRAM_RATE.
const BUYS := {
	"Tikka": ["stone", "iron_ore", "copper_ore", "aluminium_ore", "gold_ore", "titanium_ore", "carbon", "silica_sand",
		"lithium_salts", "sulphur", "basalt_core", "iron_bar", "copper_bar", "aluminium_bar", "steel_bar", "gold_bar",
		"titanium_bar", "hull_plate", "coil_wire", "glass_pane", "refined_silicon", "brick", "magnet", "motor",
		"precision_lens", "high_density_core", "scrap", "circuit_board", "lithium_cell", "rare_earths", "helium_3", "cobalt_60"],
	"Jasper": ["crater_potato", "moon_wheat", "star_tomato", "nebula_grape", "flour", "moon_wheat_bread", "crater_potato_mash",
		"star_tomato_soup", "mess_hall_stew", "station_breakfast"],
	"Sesska": ["chitin", "hide"],
	"Rusk": ["ice"],
	"Job": ["quartz", "thermal_quartz", "moon_opal", "crater_garnet", "void_sapphire", "lunar_agate", "anorthosite",
		"moon_olivine", "regolith_jasper", "ilmenite", "selenite_rose", "armalcolite", "orange_glass", "spinel",
		"basalt_glass", "fire_opal", "tranquillityite", "geode", "cavern_geode"],
}

# What each shop sells: [item, price, unlock]. Unlocks are checked by shops.gd unlocked(): "" is always;
# "later" is for things whose system isn't built yet (they stay hidden).
# Recipes are "recipe:<dish>": buying one teaches it (shops.gd known_recipes) instead of giving an item.
const STOCK := {
	"Bram": [["crater_potato_seeds", 8, ""], ["moon_wheat_seeds", 4, ""], ["star_tomato_seeds", 70, ""],
		["ration", 15, ""], ["hydro_bed", 350, ""]],
	"Tikka": [["iron_bar", 30, ""], ["copper_bar", 45, ""], ["carbon", 15, ""], ["steel_bar", 80, ""],
		["hull_plate", 105, ""], ["coil_wire", 105, ""], ["circuit_board", 115, "flown"], ["lithium_cell", 90, "flown"]],
	"Rusk": [["house_tea", 15, ""], ["iced_moon_tea", 20, ""], ["ginger_brew", 28, ""], ["spacer_fizz", 35, ""],
		["night_watch", 40, ""], ["anchor_tonic", 45, ""], ["captains_reserve", 80, ""],
		["garden_cordial", 50, "later"], ["comet_float", 60, "later"]],
	"Jasper": [["ration", 12, ""], ["moon_wheat_bread", 48, ""], ["crater_potato_mash", 69, ""],
		["star_tomato_soup", 100, ""], ["station_breakfast", 105, ""], ["mess_hall_stew", 120, ""],
		["flour", 25, ""], ["milk_powder", 8, ""],
		["recipe:moon_wheat_bread", 100, ""], ["recipe:crater_potato_mash", 120, ""], ["recipe:station_breakfast", 140, ""],
		["recipe:mess_hall_stew", 150, ""], ["recipe:star_tomato_soup", 180, ""],
		# the hotel's bigger kitchen: French cooking (Zachary: "beuf borgingion best dish in the game")
		["recipe:croissant", 200, "hotel_kitchen"], ["recipe:french_onion_soup", 220, "hotel_kitchen"],
		["recipe:quiche_aux_poireaux", 240, "hotel_kitchen"], ["recipe:ratatouille", 260, "hotel_kitchen"],
		["recipe:creme_brulee", 300, "hotel_kitchen"], ["recipe:cassoulet", 320, "hotel_kitchen"],
		["recipe:bouillabaisse", 380, "hotel_kitchen"], ["recipe:space_bourguignon", 600, "hotel_kitchen_8_hearts"]],
	"Sesska": [["knit_cap", 45, ""], ["woven_scarf", 45, ""], ["work_shirt", 65, ""], ["woven_shawl", 110, ""],
		["station_coat", 140, ""], ["silk_coat", 280, "later"]],
	"Ix'ali": [["hard_hat", 70, ""], ["padded_vest", 110, ""], ["work_boots", 90, ""]],
	"Maren": [["medpack", 40, ""]],
}

# The shops' names on the screen, and a line from the keeper when it opens.
const TITLES := {
	"Bram": "Bram's Sundries", "Tikka": "Engineering stores", "Rusk": "Rusk's bar", "Jasper": "The mess hall",
	"Sesska": "Sesska's weaving", "Ix'ali": "The armoury", "Maren": "The medbay", "Job": "Job's geode bench",
}

# ---------------------------------------------------------------- geodes (Job cracks them)
# A geode turns up as you cut rock or ore in the mine and the north tunnels (GEODE_CHANCE a cut); the caverns'
# geode veins give cavern geodes. Job opens them for a fee. Each roll: [chance, items, low, high].
const GEODE_CHANCE := 0.04
const CRACK_FEE := {"geode": 15, "cavern_geode": 30}
const GEODE_ROLLS := {
	"geode": [[0.15, ["stone"], 3, 5], [0.12, ["iron_ore"], 2, 4], [0.10, ["copper_ore"], 2, 4], [0.08, ["quartz"], 1, 2],
		[0.40, ["lunar_agate", "anorthosite", "moon_olivine", "regolith_jasper"], 1, 1],
		[0.12, ["moon_opal", "ilmenite", "selenite_rose"], 1, 1], [0.03, ["armalcolite"], 1, 1]],
	"cavern_geode": [[0.15, ["iron_ore"], 2, 4], [0.12, ["gold_ore"], 1, 2], [0.10, ["titanium_ore"], 2, 2],
		[0.08, ["lithium_salts"], 1, 1], [0.40, ["orange_glass", "spinel", "basalt_glass"], 1, 1],
		[0.12, ["crater_garnet", "fire_opal", "tranquillityite"], 1, 1], [0.03, ["void_sapphire"], 1, 1]],
}

# ---------------------------------------------------------------- drinks
# One drink effect at a time; a new drink replaces it. [seconds, speed x, tool energy x, damage x]
const DRINK_EFFECTS := {
	"spacer_fizz": [120.0, 1.1, 1.0, 1.0],
	"night_watch": [120.0, 1.0, 0.5, 1.0],
	"anchor_tonic": [120.0, 0.9, 1.0, 0.85],
}

# ---------------------------------------------------------------- cooking
# Cooked at the kitchenette in your apartment, once you know the recipe. "hotel" dishes need the hotel kitchen.
const COOKING := [
	{"makes": "moon_wheat_bread", "needs": {"moon_wheat": 3}},
	{"makes": "crater_potato_mash", "needs": {"crater_potato": 2, "milk_powder": 1}},
	{"makes": "star_tomato_soup", "needs": {"star_tomato": 2, "milk_powder": 1}},
	{"makes": "mess_hall_stew", "needs": {"crater_potato": 2, "star_tomato": 1, "moon_wheat": 1}},
	{"makes": "station_breakfast", "needs": {"moon_wheat_bread": 1, "crater_potato": 1, "milk_powder": 1}},
]
# The French recipes' dishes are listed (with what they will need) in the price sheet; they join COOKING with
# the hotel kitchen, once their ingredients (onions, leeks, beef, wine, fish) are in the game.
const RECIPE_NAMES := {
	"croissant": "Croissants", "french_onion_soup": "French onion soup", "quiche_aux_poireaux": "Quiche aux poireaux",
	"ratatouille": "Ratatouille", "creme_brulee": "Crème brûlée", "cassoulet": "Cassoulet",
	"bouillabaisse": "Bouillabaisse", "space_bourguignon": "Boeuf bourguignon",
}

# ---------------------------------------------------------------- wearables
# Armour goes in the gear page's Head, Armour and Boots slots; clothes in the Hat and Outfit slots, which show over
# the armour. "defence" points each give a 10% chance to shrug off a point of damage (up to 60%).
const WEAR := {
	"hard_hat": ["head", 1], "padded_vest": ["armor", 2], "work_boots": ["boots", 1],
	"knit_cap": ["hat", 0], "woven_scarf": ["hat", 0],
	"work_shirt": ["outfit", 0], "woven_shawl": ["outfit", 0], "station_coat": ["outfit", 0], "silk_coat": ["outfit", 0],
}


static func value(item: String) -> int:
	return int(VALUE.get(item, 0))


# What a shop pays for one: full value where it buys that kind, Bram's rate at his counter, else 0.
static func pays(shop: String, item: String) -> int:
	if not VALUE.has(item):
		return 0
	if BUYS.get(shop, []).has(item):
		return value(item)
	if shop == "Bram":
		return maxi(1, int(floor(value(item) * BRAM_RATE)))
	return 0


static func cooking_for(dish: String) -> Dictionary:
	for r in COOKING:
		if str(r["makes"]) == dish:
			return r
	return {}
