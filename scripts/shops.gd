extends Node
# The station's shops (Zachary, 23 Nov 2026): buying and selling at the keepers' counters, Job's geode bench,
# cooking at your kitchenette, drink effects and what you wear. Prices and stock are in scripts/shop_data.gd.
#
# The screen is the datapad's Shop page (datapad/datapad.gd _shop): a tab per kind of business, four rows a page.
# main.gd opens it (_shop_offer when you talk to a keeper at work, the kitchenette at home) and owns the money and
# the bag; this file builds the rows, acts on the buttons and keeps the state that is saved:
#   known_recipes  dishes you can cook (bought from Jasper)
#   wearing        gear-page slot -> item (head, armor, boots, hat, outfit)
# The drink effect (drink, drink_left) is not saved: it wears off overnight anyway.
#
# Not run in Godot yet; written to be checked by Zachary.

const ShopData = preload("res://scripts/shop_data.gd")
const ItemData = preload("res://scripts/item_data.gd")
const HEART_POINTS := 5            # friendship points per heart (scripts/datapad_bridge.gd)

var world                          # main.gd
var shop := ""                     # the shop open on the datapad, or "Cook" for the kitchenette; "" when closed
var known_recipes: Array = []
var wearing: Dictionary = {}
var drink := ""
var drink_left := 0.0
var _rng := RandomNumberGenerator.new()


func setup(main_world) -> void:
	world = main_world
	_rng.randomize()


func tick(delta: float) -> void:
	if drink_left > 0.0:
		drink_left -= delta
		if drink_left <= 0.0:
			world._toast("The %s has worn off." % _name(drink).to_lower())
			drink = ""
			_apply_drink()
	if shop != "" and (world.datapad == null or world.datapad.pad == null or str(world.datapad.pad.page) != "Shop"):
		shop = ""


# ---------------------------------------------------------------- opening the screen

# From the keeper's dialogue: open once the dialogue box has closed and the key that closed it is done with.
func open_later(who: String) -> void:
	call_deferred("open", who)


func open(who: String) -> void:
	if world.datapad == null or world.datapad.pad == null:
		world._toast("The shop screen needs the datapad.")
		return
	var reopening := shop == who
	shop = who
	var tabs: Array = []
	if who == "Cook":
		tabs.append(["Cook", _cook_rows()])
	elif who == "Concierge":
		tabs.append(["Pads", world.concierge_rows()])      # S.A.R.A.'s 8 (main.gd sara_send)
	elif who == "Hotel":
		tabs = world.hotel.desk_tabs()      # the management desk (scripts/hotel.gd)
	elif who == "Job":
		tabs.append(["Crack", _crack_rows()])
		tabs.append(["Sell", _sell_rows(who)])
	else:
		tabs.append(["Buy", _buy_rows(who)])
		if who == "Bram" or ShopData.BUYS.has(who):
			tabs.append(["Sell", _sell_rows(who)])
		if who == "Tikka":
			tabs.append(["Upgrade", _upgrade_rows()])
	var title: String = {"Cook": "Your kitchenette", "Hotel": "Hotel management", "Concierge": "S.A.R.A.'s pads"}.get(who,
			str(ShopData.TITLES.get(who, who)))
	var keeper: String = "Sara" if who in ["Hotel", "Concierge"] else who
	world.datapad.pad.shop_portrait = world.datapad.portrait_key(keeper) if who != "Cook" else ""
	var hello: String = str(world.SHOP_HELLO.get(who, ""))
	if who == "Hotel":
		hello = "Every guest needs a bed, four walls and a door. Make it lovely and they'll pay for it."
	elif who == "Cook":
		hello = "Recipes you know, and what each one needs."
	elif who == "Concierge":
		hello = "Pick a pad and I'll fold you there. Mind the step."
	world.datapad.pad.shop_greeting = hello.substr(hello.find("]") + 1).strip_edges() if hello.begins_with("[") else hello
	world.datapad.pad.show_shop(title, tabs, reopening)
	if str(world.datapad.pad.page) != "Shop":
		push_warning("shops.gd: the datapad did not open the Shop page for %s" % who)
		world._toast("The shop screen didn't open (shop: %s). Tell Claude." % who)


func refresh() -> void:
	if shop != "":
		open(shop)


func unlocked(rule: String) -> bool:
	match rule:
		"":
			return true
		"flown":
			return int(world.flights) >= 1
		"hotel_kitchen":
			return world.station_fixed.has("hotel_kitchen")
		"hotel_kitchen_8_hearts":
			return world.station_fixed.has("hotel_kitchen") and _hearts("Jasper") >= 8
		"sesska_silk":                # Sesska's 6: she spins the North Cave's glow-spider silk
			return world._flag("sesska_cavern_silk")
		"tobbin_wood":                # Tobbin's 4: the garden dome's first limb
			return world._flag("tobbin_first_wood")
	return false                   # "later": its system isn't in the game yet


func _hearts(who: String) -> int:
	if not world.persons.has(who):
		return 0
	return int(world.persons[who].get("friendship", 0)) / HEART_POINTS


# ---------------------------------------------------------------- rows

func _buy_rows(who: String) -> Array:
	var rows: Array = []
	var cash: int = int(world.credits)
	for entry in ShopData.STOCK.get(who, []):
		if not unlocked(str(entry[2])):
			continue
		var id: String = str(entry[0])
		var price: int = int(entry[1])
		if id.begins_with("recipe:"):
			var dish := id.trim_prefix("recipe:")
			var known: bool = known_recipes.has(dish)
			rows.append([dish, "Recipe: " + _name(dish), "You know it" if known else _needs_text(dish), "%d scrip" % price,
				[["learn/" + dish, "Known" if known else "Learn", not known and cash >= price]]])
		elif ItemData.ITEMS.has(id):
			var buttons: Array = [["buy1/" + id, "Buy", cash >= price]]
			if not ItemData.ITEMS[id].has("wear") and id != "hydro_bed":
				buttons.append(["buy5/" + id, "Buy 5", cash >= price * 5])
			rows.append([id, _name(id), _about(id), "%d scrip" % price, buttons])
	return rows


func _sell_rows(who: String) -> Array:
	var rows: Array = []
	for id in world.items:
		var n: int = world._count(str(id))
		var each: int = ShopData.pays(who, str(id))
		if n <= 0 or each <= 0 or _worn(str(id)) >= n:
			continue
		var spare: int = n - _worn(str(id))
		rows.append([id, _name(id), "You have %d" % spare, "%d scrip each" % each,
			[["sell1/" + str(id), "Sell 1", true], ["sellall/" + str(id), "Sell all (%d)" % (spare * each), true]]])
	rows.sort_custom(func(a, b): return str(a[1]) < str(b[1]))
	return rows


func _crack_rows() -> Array:
	var rows: Array = []
	var cash: int = int(world.credits)
	for id in ShopData.CRACK_FEE:
		var n: int = world._count(str(id))
		var fee: int = int(ShopData.CRACK_FEE[id])
		var sub: String = "You have %d. Minerals inside, if you're lucky; sometimes just ore" % n if n > 0 else "You have none. Look for them while you mine"
		rows.append([id, _name(id), sub, "%d scrip each" % fee,
			[["crack1/" + str(id), "Crack 1", n > 0 and cash >= fee], ["crackall/" + str(id), "Crack all", n > 0 and cash >= fee]]])
	return rows


# Tikka's tool upgrades (ShopData.UPGRADES): the next step for each tool you carry.
func _upgrade_rows() -> Array:
	var rows: Array = []
	var cash: int = int(world.credits)
	for u in ShopData.UPGRADES:
		var from: String = str(u[0])
		if world._count(from) <= 0:
			continue
		var to: String = str(u[1])
		var price: int = int(u[2])
		var needs: Dictionary = u[3]
		var parts: Array = []
		for m in needs:
			parts.append("%d/%d %s" % [mini(world._count(str(m)), int(needs[m])), int(needs[m]), _name(str(m)).to_lower()])
		var ok: bool = cash >= price and world._has_all(needs)
		rows.append([to, "%s -> %s" % [_name(from), _name(to)], "Needs " + ", ".join(parts), "%d scrip" % price,
			[["upgrade/" + from, "Upgrade", ok]]])
	if rows.is_empty():
		rows.append(["", "Nothing to upgrade", "Bring a mining laser, hoe or watering can", "", []])
	return rows


func _upgrade(from: String) -> void:
	for u in ShopData.UPGRADES:
		if str(u[0]) != from:
			continue
		var to: String = str(u[1])
		var price: int = int(u[2])
		var needs: Dictionary = u[3]
		if world._count(from) <= 0:
			return
		if int(world.credits) < price or not world._has_all(needs):
			world.sfx("deny")
			world._toast("Tikka needs the scrip and the materials first.")
			return
		world._money(-price, "Tool upgrade")
		for m in needs:
			world._give(str(m), -int(needs[m]))
		world._swap_item(from, to)
		world.sfx("smelt")
		world._toast("Tikka hands it back: %s!" % _name(to))
		return


func _cook_rows() -> Array:
	var rows: Array = []
	for r in ShopData.COOKING:
		var dish: String = str(r["makes"])
		if not known_recipes.has(dish):
			continue
		var ok: bool = world._has_all(r["needs"])
		rows.append([dish, _name(dish), _needs_text(dish), "You have %d" % world._count(dish),
			[["cook1/" + dish, "Cook", ok], ["cook5/" + dish, "Cook 5", ok and _can_make(r["needs"], 5)]]])
	if rows.is_empty():
		rows.append(["", "No recipes yet", "Jasper sells them at the mess hall", "", []])
	return rows


# ---------------------------------------------------------------- the buttons

func on_action(action: String) -> void:
	var pair := action.split("/", true, 1)
	if pair.size() < 2:
		return
	var verb: String = pair[0]
	var id: String = pair[1]
	match verb:
		"buy1": _buy(id, 1)
		"buy5": _buy(id, 5)
		"learn": _learn(id)
		"sell1": _sell(id, 1)
		"sellall": _sell(id, world._count(id) - _worn(id))
		"crack1": _crack(id, 1)
		"crackall": _crack(id, world._count(id))
		"cook1": _cook(id, 1)
		"cook5": _cook(id, 5)
		"room": world.hotel.on_action(verb, id)
		"upgrade": _upgrade(id)
		"pad":
			shop = ""
			world.sara_send(id)
			return
	refresh()


func _price(id: String) -> int:
	for entry in ShopData.STOCK.get(shop, []):
		if str(entry[0]) == id and unlocked(str(entry[2])):
			return int(entry[1])
	return -1


func _buy(id: String, n: int) -> void:
	var price := _price(id)
	if price < 0 or n <= 0:
		return
	if int(world.credits) < price * n:
		world.sfx("deny")
		world._toast("Not enough scrip.")
		return
	world._money(-price * n, "Shopping")
	world._give(id, n)
	world.sfx("coin")
	world._toast("Bought %s  -%d" % [_counted(id, n), price * n])


func _learn(dish: String) -> void:
	var price := _price("recipe:" + dish)
	if price < 0 or known_recipes.has(dish):
		return
	if int(world.credits) < price:
		world.sfx("deny")
		world._toast("Not enough scrip.")
		return
	world._money(-price, "Shopping")
	known_recipes.append(dish)
	world.sfx("recipe_new")
	world._toast("Learned: %s. Cook it at your kitchenette." % _name(dish))


func _sell(id: String, n: int) -> void:
	var each: int = ShopData.pays(shop, id)
	n = mini(n, world._count(id) - _worn(id))
	if each <= 0 or n <= 0:
		return
	world._give(id, -n)
	world._money(each * n, "Sold to " + shop)
	world.sfx("coin")
	world._toast("Sold %s  +%d" % [_counted(id, n), each * n])


# Job opens geodes one at a time and takes his fee for each; what's inside goes in your bag.
func _crack(id: String, n: int) -> void:
	var fee: int = int(ShopData.CRACK_FEE.get(id, 0))
	var found: Dictionary = {}
	var cracked := 0
	while cracked < n and world._count(id) > 0 and int(world.credits) >= fee:
		world._give(id, -1)
		world._money(-fee, "Job's geode bench")
		var roll: Array = roll_geode(id)
		world._give(str(roll[0]), int(roll[1]))
		found[roll[0]] = int(found.get(roll[0], 0)) + int(roll[1])
		cracked += 1
	if cracked == 0:
		world.sfx("deny")
		world._toast("Not enough scrip for Job's fee." if world._count(id) > 0 else "You have no geodes.")
		return
	world.sfx("geode_crack")
	var parts: Array = []
	for item in found:
		parts.append(_counted(str(item), int(found[item])))
	world._toast("Job cracks %s: %s" % ["it" if cracked == 1 else "%d" % cracked, ", ".join(parts)])


# [item, how many] from one geode, by ShopData.GEODE_ROLLS.
func roll_geode(id: String) -> Array:
	var rolls: Array = ShopData.GEODE_ROLLS.get(id, [])
	if world._flag("perk_thrifty") and rolls.size() >= 2 and _rng.randf() < THRIFTY_CHANCE:
		# Artie's 8: now and then the geode is one of the good ones (the two rarest rows)
		var rare: Array = (rolls[rolls.size() - 2][1] as Array) + (rolls[rolls.size() - 1][1] as Array)
		return [str(rare[_rng.randi() % rare.size()]), 1]
	var x: float = _rng.randf()
	for r in rolls:
		x -= float(r[0])
		if x <= 0.0:
			var pool: Array = r[1]
			return [str(pool[_rng.randi() % pool.size()]), _rng.randi_range(int(r[2]), int(r[3]))]
	return ["stone", 1]


# A geode turns up now and then as you cut rock or ore in the mine and the north tunnels.
const THRIFTY_CHANCE := 0.15


func maybe_geode(area: String) -> void:
	var chance: float = ShopData.GEODE_CHANCE * (1.5 if world._flag("perk_bedrock_strength") else 1.0)   # Job's 8
	if (area == "mine" or area == "tunnels") and _rng.randf() < chance:
		world._give("geode", 1)
		world._toast("A geode fell out of the rock! Job cracks them open.")


func _cook(dish: String, n: int) -> void:
	var r: Dictionary = ShopData.cooking_for(dish)
	if r.is_empty() or not known_recipes.has(dish):
		return
	var made := 0
	while made < n and world._has_all(r["needs"]):
		var needs: Dictionary = r["needs"]
		for item in needs:
			world._give(str(item), -int(needs[item]))
		world._give(dish, 1)
		made += 1
	if made == 0:
		world.sfx("deny")
		world._toast("You're missing something for that.")
		return
	world.sfx("cook")
	world._toast("Cooked %s" % _counted(dish, made))


# ---------------------------------------------------------------- drinks

# Called by main.gd _eat after a drink. Only one drink works at a time: a new one replaces the last.
func start_drink(item: String) -> void:
	if not ShopData.DRINK_EFFECTS.has(item):
		return
	drink = item
	drink_left = float(ShopData.DRINK_EFFECTS[item][0])
	if world._flag("perk_sous_chefs_blessing"):
		drink_left *= 1.2                 # Jasper's 8: what you eat and drink stays with you a fifth longer
	_apply_drink()


func _apply_drink() -> void:
	world.player.speed_mult = float(ShopData.DRINK_EFFECTS[drink][1]) if drink != "" else 1.0


# Energy a tool or the laser costs, after Night Watch coffee.
func tool_energy(base: int) -> int:
	if drink != "":
		return maxi(1, int(round(base * float(ShopData.DRINK_EFFECTS[drink][2]))))
	return base


# Damage after armour and the Anchor tonic: each defence point is a 10% chance (up to 60%) to shrug off each point.
func damage_taken(amount: int) -> int:
	var block: float = minf(0.6, 0.1 * defence())
	if drink != "":
		block = minf(0.75, block + (1.0 - float(ShopData.DRINK_EFFECTS[drink][3])))
	if world._flag("perk_chivalric_guard"):
		block = 1.0 - (1.0 - block) * 0.8     # Ix'ali's 8: a fifth less of what gets through
	var left := 0
	for i in amount:
		if _rng.randf() >= block:
			left += 1
	return left


# ---------------------------------------------------------------- what you wear

func defence() -> int:
	var total := 0
	for slot in wearing:
		total += int(ShopData.WEAR.get(str(wearing[slot]), ["", 0])[1])
	return total


# How many of an item are being worn (so they can't be sold or eaten out from under you).
func _worn(id: String) -> int:
	return wearing.values().count(id)


# The datapad's gear page changed: keep only what fits each slot and is in the bag.
func set_wearing(slots: Dictionary) -> void:
	wearing = {}
	for slot in slots:
		var id: String = str(slots[slot])
		if ShopData.WEAR.has(id) and str(ShopData.WEAR[id][0]) == str(slot) and world._count(id) > 0:
			wearing[slot] = id


# ---------------------------------------------------------------- words

func _name(id: String) -> String:
	if ItemData.ITEMS.has(id):
		return str(ItemData.ITEMS[id]["name"])
	return str(ShopData.RECIPE_NAMES.get(id, id.capitalize()))


func _counted(id: String, n: int) -> String:
	return _name(id).to_lower() if n == 1 else "%d %s" % [n, _name(id).to_lower()]


# A short line for the row: what it does, or the first sentence of its description.
func _about(id: String) -> String:
	var info: Dictionary = ItemData.ITEMS[id]
	if info.has("crop"):
		return "Seeds: plant on a dug tile"
	if info.has("wear"):
		var w: Array = ShopData.WEAR.get(id, ["", 0])
		var slot: String = {"head": "Head armour", "armor": "Body armour", "boots": "Boots", "hat": "Hat (looks)", "outfit": "Outfit (looks)"}.get(str(w[0]), "")
		return slot + (", +%d defence" % int(w[1]) if int(w[1]) > 0 else "")
	var desc: String = str(info.get("desc", ""))
	if ShopData.DRINK_EFFECTS.has(id):
		return desc.substr(desc.find(". ") + 2) if desc.find(". ") > 0 else desc
	if str(info.get("use", "")) == "eat":
		var parts: Array = []
		if int(info.get("energy", 0)) > 0:
			parts.append("+%d energy" % int(info["energy"]))
		if int(info.get("heal", 0)) > 0:
			parts.append("%d hearts" % int(info["heal"]) if int(info["heal"]) < 10 else "every heart")
		if not parts.is_empty():
			return ", ".join(parts)
	var cut := desc.find(". ")
	if cut > 0:
		desc = desc.substr(0, cut + 1)
	if desc.length() > 54:
		desc = desc.substr(0, 52) + "..."
	return desc


func _needs_text(dish: String) -> String:
	var r: Dictionary = ShopData.cooking_for(dish)
	if r.is_empty():
		return "Hotel kitchen dish"
	var parts: Array = []
	var needs: Dictionary = r["needs"]
	for item in needs:
		parts.append("%d %s" % [int(needs[item]), _name(str(item)).to_lower()])
	return "Needs " + ", ".join(parts)


func _can_make(needs: Dictionary, n: int) -> bool:
	for item in needs:
		if world._count(str(item)) < int(needs[item]) * n:
			return false
	return true
