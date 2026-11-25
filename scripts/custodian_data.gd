extends RefCounted
# The Custodians and their bundles (24 Nov 2026, Zachary's plan: docs/story/CUSTODIANS.md). Each Custodian asks for
# three bundles of things; you give them at its crystal (main.gd _custodian_crystal), and a finished bundle fixes
# one part of the station overnight (main.gd _custodian_rewards). The datapad's Relics page lists what each needs
# (scripts/datapad_bridge.gd).
#
# The bundle lists follow the Drive doc "Custodian Bundles", with things the game doesn't have yet swapped for
# things it does. The lines are Claude's drafts.
#
# Per Custodian:
#   name, wing     shown on the Relics page
#   home, spot     the area and tile of its crystal (the three in the Sanctum from the start; the others where
#                  you find them, and in the Sanctum once their bundles are done)
#   voice          who speaks for it in scenes and at its crystal (its portrait: art/portrait_<voice lower>.png)
#   hello          what it says when you come to its crystal; "thanks" when you give; "done" once all three are done
#   bundles        id, name, items (item id -> how many), fixes (what main.gd does overnight), reward (the text)

const ORDER := ["sovereign", "chancellor", "forgemaster", "harbinger", "shepherd", "warden"]

const CUSTODIANS := {
	"sovereign": {
		"name": "The Sovereign of Hydro-Flora", "wing": "Agri Complex", "voice": "Sovereign",
		"home": "sanctum", "spot": [13, 18],
		"hello": ["Small walker. Does green life still breathe beneath this stone sky? Bring me what grows, and what lets it grow."],
		"thanks": ["[happy] Ah. I can taste the soil in these already."],
		"done": ["[happy] The domes are breathing again. Go and listen to them grow."],
		"bundles": [
			{"id": "soil", "name": "Mineral Soil Base", "items": {"silica_sand": 15, "ice": 10, "copper_bar": 5},
				"fixes": "sprinklers", "reward": "Sprinklers: the recipe goes on your datapad's Crafting page. Each one waters the four tiles beside it every morning."},
			{"id": "starter", "name": "Bio-Starter", "items": {"carbon": 10, "chitin": 6, "moon_olivine": 1},
				"fixes": "storage", "reward": "The storage dome by your field: its glass and seals made whole, and its doors open."},
			{"id": "harvest", "name": "First Harvest Offering", "items": {"moon_wheat": 10, "star_tomato": 5, "crater_potato": 5},
				"fixes": "orchard", "reward": "Fruit trees for the agri dome: moon-peach, star-apple and sun-fig saplings."},
		],
	},
	"chancellor": {
		"name": "The Chancellor of Hearths", "wing": "Hotel & Spaceport", "voice": "Chancellor",
		"home": "sanctum", "spot": [15, 14],
		"hello": ["Oh, it's you! Do come in. Mind the dust, I've been meaning to have a word with someone about the dust.",
			"Rooms, hearths, places to gather: bring me the makings and I'll put this place to rights."],
		"thanks": ["[happy] Oh, lovely. Lovely! Quality materials. I can always tell."],
		"done": ["[happy] Warm rooms and open doors. Now THAT is hospitality."],
		"bundles": [
			{"id": "framing", "name": "Structural Framing", "items": {"iron_bar": 10, "brick": 10, "glass_pane": 4},
				"fixes": "hotel_wing", "reward": "The hotel's second wing: four more guest suites."},
			{"id": "hearth", "name": "Hearth & Lighting Grid", "items": {"thermal_quartz": 6, "lithium_cell": 3, "copper_bar": 5},
				"fixes": "kiosks", "reward": "The Spaceport's empty kiosks, lit and stocked again."},
			{"id": "comforts", "name": "Hospitality Comforts", "items": {"woven_scarf": 2, "guest_bed": 2, "moon_wheat_bread": 3},
				"fixes": "gates", "reward": "The Spaceport's sealed gates, ready for passenger shuttles."},
		],
	},
	"forgemaster": {
		"name": "The Forgemaster of Keels", "wing": "Shuttle Bay", "voice": "Forgemaster",
		"home": "sanctum", "spot": [15, 22],
		"hello": ["Archivist. This station's hull is held together with rust and hope. Bring me metal and I'll give it a keel."],
		"thanks": ["Good metal. Honest weight. Stow it there."],
		"done": ["[happy] Shipshape, keel to masthead. Fair winds, Archivist."],
		"bundles": [
			{"id": "gantry", "name": "Hull & Gantry Alloy", "items": {"iron_bar": 15, "titanium_bar": 8, "scrap": 10},
				"fixes": "suite", "reward": "The Shipwright's Suite in the Shuttle Bay, opened up for Freya and Tikka."},
			{"id": "ftl", "name": "FTL Drive Core", "items": {"lithium_cell": 4, "precision_lens": 2, "circuit_board": 2},
				"fixes": "shipyard", "reward": "A shipyard in the Shuttle Bay: new ships to buy."},
			{"id": "plating", "name": "Storm Plating", "items": {"cobalt_60": 5, "high_density_core": 2, "chitin": 5},
				"fixes": "storm_plating", "reward": "Storm plating for your ship: it can fly into the great storm in Collective space."},
		],
	},
	"harbinger": {
		"name": "The Harbinger", "wing": "The Caverns", "voice": "Harbinger",
		"home": "cav_25", "spot": [0, 0],
		"hello": ["Ah! Please don't be alarmed. I'm the Harbinger. Of Destruction, technically. It's only a title.",
			"There is a sea under this rock, and it wants out. Bring me something volatile and I'll let it out gently. Mostly gently."],
		"thanks": ["[happy] Oh, these are wonderfully unstable. Thank you. Do stand back a little."],
		"done": ["[happy] The sea is free, and nobody was hurt. I'm told that's a first for a Harbinger."],
		"bundles": [
			{"id": "containment", "name": "Thermal Containment", "items": {"titanium_bar": 12, "copper_bar": 10, "steel_bar": 6},
				"fixes": "braced", "reward": "The cavern walls braced against the shock."},
			{"id": "charge", "name": "Volatile Charge", "items": {"sulphur": 8, "lithium_salts": 8, "fire_opal": 3, "thermal_quartz": 6},
				"fixes": "primed", "reward": "The charge, primed."},
			{"id": "core", "name": "Blasting Core", "items": {"basalt_core": 8, "cobalt_60": 5, "magnet": 2},
				"fixes": "blast", "reward": "The blast: the sea under the caverns opens, and with it the East Complex's garden dome and the Underground Lake."},
		],
	},
	"shepherd": {
		"name": "The Shepherd of Storms", "wing": "Collective space", "voice": "Shepherd",
		"home": "space", "spot": [0, 0],
		"hello": ["You came through the storm. Then you have seen her. She is dying, slowly, and it hurts her.",
			"Bring me what I ask, and I can help her sleep."],
		"thanks": ["Thank you. She is quieter already."],
		"done": ["She is at rest. Look: the sky is clear for the first time in a hundred of your years."],
		"bundles": [
			{"id": "salvage", "name": "Hull Salvage", "items": {"scrap": 20, "hull_plate": 6, "coil_wire": 6},
				"fixes": "", "reward": "A frame for the lullaby."},
			{"id": "lattice", "name": "Resonant Lattice", "items": {"rare_earths": 6, "void_sapphire": 2, "precision_lens": 2},
				"fixes": "", "reward": "The lattice that will carry it."},
			{"id": "lullaby", "name": "The Lullaby", "items": {"lithium_cell": 4, "circuit_board": 4, "high_density_core": 2},
				"fixes": "storm_ends", "reward": "The storm ends, and the world it hid appears on your jump map."},
		],
	},
	"warden": {
		"name": "The Warden of Tidelight", "wing": "Tidelight", "voice": "Warden",
		"home": "tidelight", "spot": [0, 0],
		"hello": ["The sun has stood at the edge of this world since before your kind. I have stood here with it."],
		"thanks": ["[happy] These remember the light. Thank you."],
		"done": ["[happy] Take me home, Archivist. The others are calling."],
		"bundles": [],
	},
}
