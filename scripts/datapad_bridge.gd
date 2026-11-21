extends Node
# Connects the Terran datapad (datapad/, from Echo_Landing_Complete_UI.zip, 20 Nov) to the game.
#
# The datapad draws the HUD (health and energy, the clock and scrip, the eight quick slots) and its pages:
# Inventory, Crafting, Skills, NPC relations, Map, Quests, Settings and Relics, plus the station menu (Escape),
# the emote picker (V) and the end-of-day summary. The game keeps its own dialogue box, shops and character
# screen. This script feeds the datapad the game's state and turns its signals into game actions.
#
# The datapad lays itself out in screen pixels (2x at 1080p, 3x at 1440p, 5x at 4K: ui/pixel_grid.gd), so it
# sits on its own CanvasLayer at scale 1 rather than on the old 2x UI layer.

const PAD_SCENE := "res://datapad/datapad.tscn"
const ItemData = preload("res://scripts/item_data.gd")
const HEART_POINTS := 5            # friendship points per heart, as on the old Friends page
const SEASONS := [["Spring", 28], ["Summer", 31], ["Autumn", 31], ["Winter", 31]]   # NPC master doc, section 2

# From the NPC master doc's roster: role, a short note, birthday (Claude's placeholder birthdays).
const RESIDENTS := {
	"Sara": ["Steward and concierge", "The station's AI. She looks after everyone on the Landing.", "Winter 1"],
	"Freya": ["Junior shipwright", "Human.", "Summer 2"],
	"Artie": ["Stasis survivor", "Human. Frozen for centuries; found in Ivan's wreck.", "Autumn 18"],
	"Stu": ["Hotel lobby boy", "Moogli. Stowed away on the first visitor transport.", "Spring 17"],
	"Tally": ["Courier and bounty pilot", "Arachnay. Runs the Post & Privateer Dispatch.", "Spring 27"],
	"Ana": ["Flight navigator", "Human. Ivan's sister.", "Winter 23"],
	"Tikka": ["Chief engineer", "Arachnay. Married to Sesska.", "Winter 9"],
	"Sesska": ["Master weaver", "Arachnay. Married to Tikka.", "Autumn 10"],
	"Jasper": ["Head chef", "Ervani. Evarra's adoptive brother.", "Spring 3"],
	"Evarra": ["Chief baker and gardener", "Vuultam. Jasper's adoptive sister.", "Spring 3"],
	"Job": ["Heavy miner", "Human.", "Summer 18"],
	"Zaas": ["Water reclamation officer", "Scyldar.", "Summer 9"],
	"Tar'Besh": ["Cleric and curator", "Zaa'sh.", "Winter 18"],
	"Vzz'ket": ["Cavern hunter", "Zaa'sh.", "Autumn 26"],
	"Bram": ["Salvage broker", "Moogli.", "Summer 26"],
	"Maren": ["Doctor", "Human. Pip's grandmother.", "Autumn 28"],
	"Owen": ["Librarian", "Human. Pip's grandfather.", "Winter 5"],
	"Pip": ["Maren and Owen's grandson", "Human, nine years old.", "Spring 6"],
	"Quill": ["Medical assistant", "Vuultam.", "Spring 11"],
	"Rusk": ["Bartender", "Ervani. Saffi's uncle.", "Autumn 3"],
	"Tobbin": ["Furniture maker", "Moogli. Nub's father.", "Autumn 7"],
	"Merrow": ["Hydroponics", "Moogli. Nub's mother; she also does Zaas's water work.", "Spring 9"],
	"Nub": ["Tobbin and Merrow's kid", "Moogli.", "Spring 22"],
	"Garrick": ["Security chief and quartermaster", "Human. Kit's father.", "Winter 12"],
	"Saffi": ["Community host", "Ervani. Kit's mother.", "Autumn 23"],
	"Kit": ["Garrick and Saffi's kid", "Ervani.", "Summer 12"],
	"Ix'ali": ["Armourer", "Zaa'sh.", "Summer 5"],
	"Ooma": ["Curio trader", "Scyldar. Visits on Wednesdays and Saturdays.", "Summer 20"],
}

# The datapad's map is a schematic of the station with seven places. Each game map belongs to one of them.
const PLACES := [
	["Town square", 181, 102, "Main level", "The Community Concourse: shops, the bar, the library, the medbay, the Survey building and the lounge."],
	["Engineering", 74, 117, "Engineering Level", "Ore processing, the furnaces, the geothermal core, Tikka's workshop and the shuttle bay."],
	["Spaceport", 84, 53, "Spaceport District", "Arrivals, customs, the viewing deck and the hotel."],
	["Agri dome", 192, 38, "Agri Complex", "Your crop beds, the seed rack, the shed and the workshop."],
	["East complex", 284, 82, "East Complex", "The mess hall gardens, the park, the gym and the laundry."],
	["Apartments", 253, 151, "East Complex", "The eight homes off the East Complex ring."],
	["Mine", 49, 31, "Mining sector", "Job's dig, the North Cave above it and the cavern gate at its west end."],
]
const AREA_PLACE := {
	"eng": "Engineering", "bay": "Engineering", "west": "Spaceport", "hotel": "Spaceport", "agri": "Agri dome",
	"east": "East complex", "mine": "Mine", "tunnels": "Mine",
}
# Which person or place each journal entry belongs to (scripts/main.gd journal()).
const QUEST_GIVER := {
	"Get off this moon": ["Tikka", "Engineering"], "A hand in the mine": ["Job", "Mine"],
	"Clear the north tunnels": ["Job", "Mine"], "Today's request": ["Bulletin board", "Town square"],
	"Bram's crates": ["Bram", "Town square"],
}

var world                    # main.gd
var pad                      # datapad/datapad.gd, or null if the datapad folder is missing
var _sent := {}              # what the datapad was last given, so it only redraws when something changes
var _max_hp := 10            # main.gd MAX_HP
var _layer: CanvasLayer


func setup(game) -> bool:
	world = game
	if not ResourceLoader.exists(PAD_SCENE):
		return false
	_layer = CanvasLayer.new()
	_layer.layer = 8
	add_child(_layer)
	var consts: Dictionary = world.get_script().get_script_constant_map()
	_max_hp = int(consts.get("MAX_HP", 10))
	pad = load(PAD_SCENE).instantiate()
	# The game's content replaces the pack's sample content before the datapad first draws.
	pad.catalog = {}
	pad.extra_textures = {}
	for id in ItemData.ITEMS:
		var info: Dictionary = ItemData.ITEMS[id]
		pad.catalog[id] = [str(info["name"]), _category(info), _kind(id, info), str(info.get("desc", ""))]
		pad.extra_textures[id] = _icon(int(info["icon"]))
	pad.recipes = _recipes()
	pad.produce_items = []
	pad.gear_types = {}            # no equipment system yet
	pad.skills = []                # no skills yet: the page says "No skills recorded"
	pad.crew = []
	pad.jobs = []
	pad.places = PLACES.duplicate(true)
	pad.known_gifts = {}
	pad.inventory_capacity = int(consts.get("SLOT_COUNT", 24))
	pad.location_name = ""
	_layer.add_child(pad)
	pad.item_used.connect(_on_item_used)
	pad.craft_requested.connect(_on_craft)
	pad.hotbar_changed.connect(_on_hotbar_changed)
	pad.menu_changed.connect(_on_menu_changed)
	pad.recap_closed.connect(_on_recap_closed)
	pad.emote_selected.connect(_on_emote)
	pad.discard_requested.connect(_on_discard)
	pad.quit_requested.connect(_on_quit)
	return true


# True while a datapad page, the station menu, the emote picker or the day summary is open: the game pauses.
func blocking() -> bool:
	return pad != null and str(pad.page) != "HUD"


func open_page(page_name: String) -> void:
	if pad != null:
		pad.show_page(page_name)


# Called every frame by main.gd. modal: one of the game's own windows (title, dialogue, character screen,
# community game, calendar) is open, so the datapad stops taking keys and clicks until it closes.
# An open datapad page always keeps the keys and sits above those windows: passing out shows the day summary
# with S.A.R.A.'s wake-up lines waiting under it, and the summary has to close first.
func sync(modal: bool) -> void:
	if pad == null:
		return
	var page_open: bool = blocking()
	pad.set_process_input(page_open or not modal)
	_layer.layer = 20 if page_open else 8       # the HUD stays under the dialogue box (10); pages go over it
	var changed := false
	var counts := {}
	for id in world.items:
		if int(world.items[id]) > 0 and ItemData.ITEMS.has(id):
			counts[id] = int(world.items[id])
	var quick: Array = world.slots.slice(0, 8)
	if counts != _sent.get("counts") or quick != _sent.get("quick") or int(world.selected) != int(_sent.get("selected", -1)):
		_sent["counts"] = counts
		_sent["quick"] = quick
		_sent["selected"] = int(world.selected)
		pad.set_inventory(counts, quick, int(world.selected))
	var vitals := [int(world.hp), _max_hp, int(world.energy), int(world.max_energy)]
	if vitals != _sent.get("vitals"):
		_sent["vitals"] = vitals
		pad.set_vitals(vitals[0], vitals[1], vitals[2], vitals[3])
	var minute_block: int = int(world.minutes) / 10 * 10
	var clock := [minute_block, int(world.day)]
	if clock != _sent.get("clock"):
		_sent["clock"] = clock
		var date: Array = season_date(int(world.day))
		pad.set_clock(minute_block, int(date[1]), str(date[0]))
	if int(world.credits) != int(_sent.get("credits", -1)):
		_sent["credits"] = int(world.credits)
		pad.station_scrip = int(world.credits)
	var place: String = _place_for(str(world.current_area))
	if place != str(_sent.get("place", "")):
		_sent["place"] = place
		pad.location_name = place
		changed = true
	if changed:
		pad.refresh()


func notify(message: String) -> void:
	if pad != null:
		pad.notify_player(message)


func show_recap(finished_day: int, lines: Array, _net: int, _total: int, _talked: int) -> void:
	var earned := 0
	var spent := 0
	for entry in lines:
		var amount: int = int(entry[1])
		if amount > 0:
			earned += amount
		else:
			spent -= amount
	var date: Array = season_date(finished_day)
	world.ui.recap_open = true
	pad.show_recap("%s %d (day %d)" % [date[0], int(date[1]), finished_day], earned, spent)


func close_recap() -> void:
	if pad != null and str(pad.page) == "Recap":
		pad.show_page("HUD")
	world.ui.recap_open = false


# The player's front-facing picture for the gear page: the first frame of their walk sheet.
func set_player_picture(sheet: Texture2D) -> void:
	if pad == null or sheet == null:
		return
	var front := AtlasTexture.new()
	front.atlas = sheet
	front.region = Rect2(0, 0, sheet.get_width() / 4.0, sheet.get_height() / 3.0)
	pad.set_player_portrait(front)


# Day 1 is Spring 1. Spring has 28 days; Summer, Autumn and Winter have 31 each (121 days a year).
static func season_date(day: int) -> Array:
	var d: int = posmod(day - 1, 121)
	for s in SEASONS:
		if d < int(s[1]):
			return [s[0], d + 1]
		d -= int(s[1])
	return ["Winter", 31]


func _place_for(area: String) -> String:
	if AREA_PLACE.has(area):
		return AREA_PLACE[area]
	if area.begins_with("home"):
		return "Apartments"
	if area.begins_with("cav_"):
		return "Mine"
	return "Town square"


func _icon(index: int) -> Texture2D:
	var tex: Texture2D = world.items_tex
	var cell: float = tex.get_height()
	var pic := AtlasTexture.new()
	pic.atlas = tex
	pic.region = Rect2(index * cell, 0, cell, cell)
	return pic


func _category(info: Dictionary) -> String:
	match str(info.get("use", "")):
		"mine", "weapon":
			return "Tools"
		"eat":
			return "Supplies"
	return "Materials"


func _kind(id: String, info: Dictionary) -> String:
	match str(info.get("use", "")):
		"mine":
			return "Mining tool"
		"weapon":
			return "Weapon"
		"eat":
			return "Food" if int(info.get("energy", 0)) > 0 else "Medicine"
	if id.ends_with("_ore"):
		return "Raw material"
	if id.ends_with("_bar"):
		return "Refined metal"
	if id in ["hull_plate", "coil_wire"]:
		return "Component"
	if id in ["chitin", "hide", "harbinger_scale"]:
		return "Creature part"
	return "Mineral"


# The game's recipes ({"makes", "n", "needs"}) in the datapad's form: [output, first material, its amount,
# amount made, station, all materials]. Everything is made from the Crafting page itself ("Pocket").
func _recipes() -> Array:
	var out: Array = []
	for recipe in ItemData.RECIPES:
		var needs: Dictionary = recipe["needs"]
		var first: String = needs.keys()[0]
		out.append([str(recipe["makes"]), first, int(needs[first]), int(recipe["n"]), "Pocket", needs.duplicate()])
	return out


# Residents the player has met, for the NPC relations page.
func _crew() -> Array:
	var out: Array = []
	for who in world.persons:
		var st: Dictionary = world.persons[who]
		if not st.get("met", false):
			continue
		var facts: Array = RESIDENTS.get(who, ["Resident", "", "Unknown"])
		var hearts: int = int(st.get("friendship", 0)) / HEART_POINTS
		out.append([who, facts[0], facts[1], hearts, {"birthday": facts[2]}])
		var key: String = "p_" + str(who)
		if not pad.extra_textures.has(key) and st.get("portrait") != null:
			var face: Texture2D = _small_portrait(st["portrait"])
			if face != null:
				pad.extra_textures[key] = face
	return out


# The neutral face from a portrait strip (square pictures side by side), smoothly shrunk to the 74x70 frame
# on the resident file. The datapad draws at its own small pixel size, so a 128-pixel face needs shrinking.
func _small_portrait(strip: Texture2D) -> Texture2D:
	var img: Image = strip.get_image()
	if img == null:
		return null
	if img.is_compressed():
		img.decompress()
	img.convert(Image.FORMAT_RGBA8)
	var side: int = img.get_height()
	var face: Image = img.get_region(Rect2i(0, 0, side, side))
	face.resize(70, 70, Image.INTERPOLATE_LANCZOS)
	var framed := Image.create_empty(74, 70, false, Image.FORMAT_RGBA8)
	framed.blit_rect(face, Rect2i(0, 0, 70, 70), Vector2i(2, 0))
	return ImageTexture.create_from_image(framed)


# The journal (main.gd journal(): [title, [lines], done]) as the datapad's requests.
func _jobs() -> Array:
	var out: Array = []
	for entry in world.journal():
		var title: String = entry[0]
		var lines: Array = entry[1]
		var done: bool = entry[2]
		var who: Array = QUEST_GIVER.get(title, ["Station", "Town square"])
		var objective: String = "Done" if done else str(lines[1] if lines.size() > 1 else lines[0])
		out.append([title, who[0], str(lines[0]), objective, "", {"place": who[1]}])
	return out


func _on_menu_changed(page_name: String) -> void:
	if page_name in ["Crew", "Journal", "Inventory", "Map"]:
		pad.crew = _crew()
		pad.jobs = _jobs()
		if world.player != null and world.player.has_method("front_sheet"):
			set_player_picture(world.player.front_sheet())
		pad.refresh()
	if page_name != "HUD":
		world.sfx("click")


func _on_item_used(id: String) -> void:
	var info: Dictionary = ItemData.ITEMS.get(id, {})
	if str(info.get("use", "")) == "eat":
		pad.show_page("HUD")
		world._eat(id)
	else:
		pad.notify_player("Put it on a quick slot, then press Space to use it")


func _on_craft(index: int) -> void:
	if index < 0 or index >= ItemData.RECIPES.size():
		return
	if world.craft(index):
		var makes: String = ItemData.RECIPES[index]["makes"]
		pad.notify_player("Made: " + str(ItemData.ITEMS[makes]["name"]))


# The datapad pins an item to a quick slot or picks a slot. In the game each item sits in exactly one slot,
# so a pinned item swaps places with whatever was in that slot.
func _on_hotbar_changed(wanted: Array, active: int) -> void:
	world.selected = clampi(active, 0, 7)
	for i in mini(8, wanted.size()):
		var want: String = str(wanted[i]) if wanted[i] != null else ""
		if want == "" or str(world.slots[i]) == want:
			continue
		var j: int = world.slots.find(want)
		if j != -1:
			world.swap_slots(i, j)
	_sent.erase("quick")


func _on_recap_closed() -> void:
	world.ui.recap_open = false


func _on_emote(id: String) -> void:
	if world.player != null and world.player.has_method("show_emote"):
		world.player.show_emote(StringName(id))


func _on_discard(id: String, amount: int) -> void:
	var info: Dictionary = ItemData.ITEMS.get(id, {})
	if str(info.get("use", "")) in ["mine", "weapon"]:
		pad.notify_player("You can't throw that away")
		return
	world._give(id, -amount)
	pad.notify_player("Discarded %d %s" % [amount, str(info.get("name", id)).to_lower()])


func _on_quit() -> void:
	world._save_game()
	get_tree().quit()
