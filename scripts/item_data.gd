extends RefCounted
# Everything the player can carry, and what can be crafted.
# "icon" is the position of the picture in art/items.png (made by tools/build.py).
# "use" says what pressing Space does with it selected: "mine", "weapon", "eat", or nothing.

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
	"medpack": {"name": "Medpack", "icon": 12, "use": "eat", "heal": 10,
			"desc": "From Maren in the medbay. Select it and press Space to mend every heart."},
}

# What a furnace makes from each ore you can hold.
const SMELTS = {"iron_ore": "iron_bar", "copper_ore": "copper_bar"}

# What the Crafting page offers. "needs" is item -> how many.
const RECIPES = [
	{"makes": "hull_plate", "n": 1, "needs": {"iron_bar": 3}},
	{"makes": "coil_wire", "n": 1, "needs": {"copper_bar": 2}},
]
