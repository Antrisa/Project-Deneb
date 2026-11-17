# Echo Landing: resources, components, tools, machines, food, hotel furniture. Draft for Zachary, 17 Nov.
RES_H = ["Resource", "Kind", "Where", "Mine / gather time", "Regrows", "Sell (scrip)", "Main uses"]
RES = [
 ["Stone", "Rock", "Every plain rock; crater surface", "0.5 s", "Daily (rocks)", 1, "Arc Smelter, bricks, paths, charges"],
 ["Copper ore", "Ore", "Mine, North Cave, Caverns 1-15", "0.8 s", "2-3 days (North Cave)", 5, "Copper bar"],
 ["Iron ore", "Ore", "Mine, North Cave, Caverns 1-30", "1.2 s", "2-3 days (North Cave)", 8, "Iron bar, steel"],
 ["Carbon (graphite)", "Ore", "Graphite seams, Caverns 1-15", "1.0 s", "New each floor", 6, "Steel (with iron)"],
 ["Silica sand", "Ore", "Crater rim, Caverns 1-15", "0.6 s", "New each floor", 4, "Glass pane, refined silicon"],
 ["Quartz", "Gem rock", "Caverns 1-15", "1.0 s", "New each floor", 12, "Refined silicon, glass, lenses"],
 ["Aluminium ore (anorthite)", "Ore", "Caverns 5-30", "1.2 s", "New each floor", 10, "Aluminium bar: light frames, hull plate, furniture"],
 ["Titanium ore", "Ore", "Caverns 16-45", "2.0 s (needs steel laser)", "New each floor", 25, "Titanium bar"],
 ["Gold ore", "Ore", "Rare veins, Caverns 16-45", "1.6 s", "New each floor", 40, "Gold bar: good electronics, jewellery"],
 ["Rare earths", "Ore", "Rare veins, Caverns 20-45", "1.8 s", "New each floor", 35, "Magnets for motors"],
 ["Lithium salts", "Brine node", "Hot pools, Caverns 31-45", "1.5 s", "New each floor", 30, "Lithium cell"],
 ["Thermal quartz", "Gem rock", "Steam vents, Caverns 31-45", "2.0 s", "New each floor", 45, "Precision lens, blaster optics, hatcheries"],
 ["Sulphur", "Vent crust", "Steam vents, Caverns 31-45", "0.8 s", "New each floor", 15, "Charges, fertiliser"],
 ["Basalt core", "Ore", "Caverns 35-45", "3.0 s (needs titanium laser)", "New each floor", 60, "High-density core"],
 ["Cobalt-60", "Ore (radioactive)", "Caverns 40-45; needs hazard vest", "3.0 s (needs titanium laser)", "New each floor", 120, "High-density core: Harbinger, thrusters"],
 ["Ice", "Ice seam", "Zaas's water works, cavern pools", "1.0 s", "Daily (water works)", 6, "Sell, ice cream, drinks, cold store"],
 ["Helium-3", "Gas pocket", "Crater surface (suit), deep vents 40-45", "Collector", "Weekly", 150, "Ship fuel (late game)"],
 ["Geode", "Rock", "Any floor, rare", "1.0 s", "-", 10, "Crack at Job's: gems, fossils, relics"],
 ["Moon opal", "Gem", "Geodes, Caverns 1-15", "-", "-", 60, "Gifts, rings, jewellery"],
 ["Crater garnet", "Gem", "Geodes, Caverns 16-30", "-", "-", 90, "Gifts, rings, jewellery"],
 ["Void sapphire", "Gem", "Geodes, Caverns 31-45", "-", "-", 140, "Gifts, rings, Precursor gear"],
 ["Fossil / relic", "Museum find", "Geodes, rare rocks, all floors", "-", "-", "donate", "Museum cases (Tar'Besh)"],
 ["Precursor crystal shard", "Crystal", "One at floors 15, 30, 45; rare elsewhere", "2.5 s", "-", "-", "Sanctum cradles, Custodians, Precursor gear"],
 ["Bioluminescent spores", "Forage", "Caverns 16-30", "Pick", "New each floor", 8, "Glow-flares, tonics, parka lining"],
 ["Glow-moss", "Forage", "Caverns 16-30", "Pick", "New each floor", 6, "Tonics, Hydro-Flora bundle, decor"],
 ["Cave mushroom", "Forage", "Caverns 16-30; mushroom log at home", "Pick", "New each floor", 10, "Food, tonics, dye"],
 ["Cavern silk", "Creature drop / webs", "Glow spiders, webs 16-30", "Cut", "-", 12, "Reinforced silk"],
 ["Chitin plate", "Creature drop", "Cave bugs 1-30", "-", "-", 6, "Hazard vest, armour, decor"],
 ["Lizard hide", "Creature drop", "Lizards 1-30", "-", "-", 8, "Leather: boots, belts, chairs"],
 ["Scrap", "Salvage", "Wrecked station areas, caverns crates", "Search", "Weekly", 2, "Recycler: back into metals"],
 ["Logs (lunar birch, ironwood)", "Wood", "Agridome grove, crater saplings", "Cut 1.0 s", "Trees regrow", 4, "Planks (1 log = 4 planks)"],
 ["Resin", "Tree tap", "Agridome trees", "Tap", "Every 3 days", 10, "Seal kit, glow-flares, varnish"],
 ["Lunar cotton", "Crop", "Agri dome, hydroponics", "Harvest", "Crop", 8, "Cotton cloth"],
 ["Bio-plankton", "Crop / trap", "Troughs, plankton vat, shoreline pots", "Harvest", "Daily", 3, "Protein, fish feed"],
 ["Honey", "Machine", "Bee hive", "-", "Every 4 days", 25, "Food, drinks, mead"],
 ["Milk powder", "Shop", "Bram's Exchange", "-", "-", "buy 8", "Ice cream, baking"],
]
COMP_H = ["Component", "Recipe", "Station", "Sell (scrip)", "Used for"]
COMP = [
 ["Copper bar", "3 copper ore", "Arc Smelter", 20, "Wire, circuit boards, gear tier 1"],
 ["Iron bar", "3 iron ore", "Arc Smelter", 30, "Steel, chests, tools"],
 ["Steel bar", "2 iron bar + 1 carbon", "Arc Smelter", 70, "Steel tier tools and weapons, motors, frames"],
 ["Aluminium bar", "3 aluminium ore", "Arc Smelter", 35, "Hull plate, furniture frames, light armour"],
 ["Titanium bar", "4 titanium ore", "Arc Smelter", 110, "Titanium tier gear, hatcheries, EVA rig"],
 ["Gold bar", "3 gold ore", "Arc Smelter", 140, "Good circuits, rings, luxury furniture"],
 ["Glass pane", "3 silica sand", "Arc Smelter", 12, "Dome and window repair, jars, lamps, display cases"],
 ["Refined silicon", "2 silica sand + 1 quartz", "Arc Smelter", 30, "Circuit boards, lenses"],
 ["Brick", "4 stone", "Arc Smelter", 5, "Paths, planters, fireplaces"],
 ["Wood plank", "1 log = 4 planks", "Workbench", 2, "Furniture, chests, handles"],
 ["Flour", "2 moon-wheat or 2 star-oats", "Kitchen Stove (mill)", 12, "Bread, tarts, noodles"],
 ["Copper wire", "1 copper bar = 3 wire", "Manufacturing Hub", 9, "Motors, lights, ship repair (replaces coil wire)"],
 ["Magnet", "1 rare earths + 1 iron bar", "Manufacturing Hub", 50, "Motors"],
 ["Motor", "2 copper wire + 1 steel bar + 1 magnet", "Manufacturing Hub", 140, "Machines, fans, kitchen bot, laser tiers"],
 ["Circuit board", "2 copper bar + 2 refined silicon", "Manufacturing Hub", 80, "Machines, blaster, scanner, bots"],
 ["Hull plate", "2 aluminium bar or 1 steel bar", "Manufacturing Hub", 70, "Ship repair, armour, hatches"],
 ["Precision lens", "2 thermal quartz + 1 copper bar + 1 refined silicon", "Manufacturing Hub", 160, "Laser lens slot, sonar rod, blaster optics"],
 ["Lithium cell", "2 lithium salts", "Arc Smelter", 60, "Upgraded power pack, blaster ammo"],
 ["High-density core", "2 cobalt-60 + 2 basalt core", "Arc Smelter", 600, "The Harbinger, ship thrusters, demolition charge"],
 ["Seal kit", "1 resin + 1 cavern silk", "Workbench", 25, "Anything that holds water: hatchery, ponds, aquarium"],
 ["Cotton cloth", "3 lunar cotton", "Loom", 30, "Clothes, curtains, bedding, rods"],
 ["Reinforced silk", "3 cavern silk", "Loom", 45, "EVA rig, luxury bedding"],
 ["Dyed cloth", "1 cotton cloth + 1 cave mushroom (or flower)", "Loom", 40, "Coloured curtains, rugs, sofas"],
 ["Leather", "2 lizard hide", "Workbench", 20, "Boots, armchairs, belts"],
 ["Precursor alloy", "1 titanium bar + 1 Precursor crystal shard + 1 gold bar", "Sanctum altar (Tar'Besh)", "-", "Precursor tier gear"],
]
TOOL_H = ["Tool / weapon", "Basic (start)", "Steel", "Titanium", "Precursor", "Upgrade bonus"]
TOOLS = [
 ["Mining laser", "Given", "3 steel bar + 1 motor", "3 titanium bar + 1 motor + 1 circuit board", "2 Precursor alloy + 1 high-density core", "Mines 30% faster each tier; titanium tier mines basalt and cobalt-60; Precursor mines anything in one pass"],
 ["Laser lens slot", "-", "-", "Precision lens", "Precursor lens (lens + crystal shard)", "x2 ore yield, Precursor x3"],
 ["Laser power slot", "-", "-", "Upgraded power pack (2 lithium cell + 2 copper bar + 1 circuit board)", "-", "35-40% less mining time"],
 ["Hoe", "Given", "2 steel bar + 2 planks", "2 titanium bar + 2 planks", "1 Precursor alloy", "Tills 1 / 3 / 5 / 9 tiles"],
 ["Watering can", "Given", "2 steel bar + 1 seal kit", "2 titanium bar + 1 seal kit", "1 Precursor alloy + 1 seal kit", "Waters 1 / 3 / 5 / 9 tiles; 2x / 3x / 4x capacity"],
 ["Cutter (trees)", "Given", "2 steel bar + 1 plank", "2 titanium bar + 1 plank", "1 Precursor alloy", "Fells trees faster; titanium cuts ironwood"],
 ["Fishing rod", "Telescopic (2 iron bar + 2 planks + 2 cloth)", "Steel rod (+ reel: 1 motor)", "Deep-sea sonar rod (3 titanium + 1 circuit + 1 lens)", "Precursor rod", "Bigger catch window; sonar shows fish; Precursor catches legendary fish"],
 ["Sword", "Spear or sword from Vzz'ket", "3 steel bar + 1 leather", "3 titanium bar + 1 leather", "2 Precursor alloy + 1 void sapphire", "Damage 10 / 20 / 35 / 60"],
 ["Spear", "Spear from Vzz'ket", "2 steel bar + 2 planks", "2 titanium bar + 2 planks", "2 Precursor alloy + 1 plank", "Longer reach, damage 8 / 16 / 30 / 52"],
 ["Blaster pistol", "-", "3 steel bar + 2 copper bar + 1 circuit board + 1 quartz", "3 titanium bar + 1 circuit board + 1 precision lens", "2 Precursor alloy + 1 precision lens", "Ranged; uses ammo cells; 12 / 22 / 40"],
 ["Body armour", "Chitin-lined hazard vest (3 cloth + 4 chitin + 2 iron bar)", "Steel plate vest (3 steel bar + 2 leather)", "Alloy-plated EVA rig (3 reinforced silk + 3 titanium bar + 1 circuit board)", "Precursor shell (2 Precursor alloy + 2 reinforced silk)", "Defence 5 / 10 / 18 / 30; hazard vest needed for cobalt-60; EVA rig = space suit (opens the airlocks)"],
 ["Helmet", "Miner's hard hat (1 iron bar + 1 glow-flare)", "Steel helmet (2 steel bar)", "Titanium visor (2 titanium bar + 1 glass pane)", "Precursor crown (1 Precursor alloy + 1 gem)", "Defence 2 / 4 / 7 / 12; lamp lights dark floors"],
 ["Boots", "Work boots (2 leather)", "Steel-toe boots (1 steel bar + 2 leather)", "Mag boots (1 titanium bar + 1 magnet + 2 leather)", "Precursor striders (1 Precursor alloy + 2 leather)", "Speed +0 / +5% / +10% / +20%; mag boots never slip on wet floors"],
 ["Chest", "Wooden chest (15 planks) 24 slots", "Steel chest (4 steel bar + 10 planks) 36 slots", "Reinforced alloy chest (4 titanium bar + 10 planks) 48 slots", "Precursor vault (1 Precursor alloy + 1 crystal) 72 slots, shared everywhere", "Storage"],
 ["Sprinkler", "Hydroponic sprayer (2 circuit + 3 iron bar + 1 copper bar): 4 tiles", "Steel sprinkler (2 steel bar + 1 seal kit + 1 copper wire): 8 tiles", "Titanium sprinkler (2 titanium bar + 1 seal kit + 1 circuit): 24 tiles", "Precursor mist tower (1 Precursor alloy + 1 seal kit): 48 tiles", "Waters every morning"],
]
MACH_H = ["Machine / station", "Recipe", "Takes", "Makes", "Time", "Notes"]
MACH = [
 ["Workbench", "10 planks + 5 stone", "-", "Planks, seal kits, leather, simple furniture", "-", "Where crafting starts"],
 ["Arc Smelter", "10 iron ore + 5 stone", "Ore, sand, stone", "Bars, glass, bricks, cells, cores", "30 min per batch", "In Engineering too (the furnaces)"],
 ["Manufacturing Hub", "4 iron bar + 2 copper bar + 8 planks", "Bars, silicon", "Wire, motors, circuits, lenses, hull plate", "1 h", "Pulls from chests within 3-4 tiles"],
 ["Loom", "10 planks + 2 iron bar + 4 lunar cotton", "Cotton, silk, dyes", "Cloth, silk, dyed cloth", "2 h", "Sesska's speciality"],
 ["Hotel Carpentry bench", "1 Manufacturing Hub + 10 planks + 2 steel bar", "Planks, cloth, bars, glass", "All furniture", "2-8 h", "In the hotel; makes the furniture catalogue"],
 ["Kitchen Stove", "4 iron bar + 4 brick + 1 copper wire", "Ingredients", "Dishes", "Instant", "Your own cooking"],
 ["Kitchen bot", "1 motor + 2 circuit board + 2 steel bar + 1 glass pane", "A weekly recipe + ingredients", "The hotel's weekly meal", "Serves all week", "See Hotel meals tab"],
 ["Fermenter", "2 steel bar + 1 seal kit + 1 glass pane", "Fruit, grain, honey", "Wine, cider, beer, mead", "3-7 days", "Sells well; Rusk buys drinks"],
 ["Preserver", "2 glass pane + 1 iron bar + 1 resin", "Fruit, vegetables, fish", "Jams, pickles, smoked fish", "2 days", "Jasper buys preserves"],
 ["Ice cream maker", "1 motor + 1 steel bar + 1 glass pane", "Ice + milk powder + flavour (fruit, honey, berries)", "Ice cream", "4 h", "Sells high; guests love it; summer festival"],
 ["Dehydrator", "4 planks + 1 copper wire + 1 glass pane", "Fruit, mushrooms, plankton", "Dried snacks, ration packs", "1 day", "Light food for the caverns"],
 ["Recycler", "2 steel bar + 1 motor", "Scrap, broken items", "Stone, metals, glass", "1 h", "Turns the wreckage into materials"],
 ["Bee hive", "8 planks + 1 resin", "Nectar-blossoms nearby", "Honey", "4 days", "Restored agri dome only"],
 ["Mushroom log", "1 log + 5 cave mushroom", "-", "Cave mushrooms", "Every 3 days", "Grows in the dark"],
 ["Plankton vat", "2 titanium bar + 2 seal kit + 1 glass pane", "Water", "Bio-plankton", "Daily", "Bigger, automatic plankton trough"],
 ["Seed maker", "1 motor + 1 iron bar + 4 planks", "Any crop", "1-3 seeds", "1 day", "Re-plant without buying"],
 ["Geode cracker", "2 steel bar + 1 motor", "Geodes", "Gems, fossils, relics", "Instant", "Job will also crack them for 10 scrip"],
 ["Protein Synthesizer", "3 iron bar + 2 circuit board + 1 quartz + 2 resin", "Bio-plankton", "Synth-steak, ground protein, cured strips", "1 day", "From the bible"],
 ["Fish hatchery", "4 titanium bar + 2 circuit board + 2 thermal quartz + 4 resin", "Fish + plankton", "More fish", "2-3 days", "After the Harbinger"],
 ["Abyssal trap pot", "2 iron bar + 2 planks", "Bait", "Crabs, salvage", "1 day", "Ocean shore"],
]
CONS_H = ["Consumable", "Recipe", "Station", "Effect", "Sell (scrip)"]
CONS = [
 ["Glow-flare", "1 bioluminescent spores + 1 resin", "Pocket", "Lights a dark floor for 2 min", 15],
 ["Small charge", "2 stone + 1 sulphur + 1 copper wire", "Workbench", "Blasts rocks in a small ring", 20],
 ["Cluster charge", "4 brick + 2 sulphur + 2 copper wire", "Manufacturing Hub", "Blasts a big ring of rocks", 60],
 ["Demolition charge", "1 high-density core + 4 sulphur + 1 circuit board", "Manufacturing Hub", "Opens sealed walls and secret rooms", 400],
 ["Rope ladder", "4 cotton cloth + 2 planks", "Workbench", "Drops you one floor down at once", 30],
 ["Return beacon", "1 circuit board + 1 Precursor crystal shard (small)", "Manufacturing Hub", "Warps you to the mine head", 120],
 ["Ore scanner", "1 circuit board + 1 glass pane + 1 copper wire", "Manufacturing Hub", "Shows ore and the way down on the floor", "tool"],
 ["Ammo cell", "1 lithium cell + 1 copper bar = 10 shots", "Manufacturing Hub", "Blaster ammunition", 6],
 ["Field rations", "2 crops or berries", "Pocket", "+25 energy", 20],
 ["Stamina tonic", "1 glow-moss + 1 cave mushroom + 1 honey", "Kitchen Stove", "+80 energy", 60],
 ["Healing tonic", "2 glow-moss + 1 ice", "Kitchen Stove", "+5 hearts", 50],
 ["Fertiliser", "1 sulphur + 2 bio-plankton", "Workbench", "Crops grow 25% faster", 10],
]
FOOD_H = ["Dish", "Ingredients", "Energy", "Health", "Guest happiness (per serving)", "Sell (scrip)", "Notes"]
FOOD = [
 ["Ice cream (vanilla)", "1 ice + 1 milk powder", 30, 0, 3, 45, "Ice cream maker"],
 ["Star-apple ice cream", "1 ice + 1 milk powder + 1 star-apple", 40, 0, 4, 70, "Ice cream maker"],
 ["Honey frost ice cream", "1 ice + 1 milk powder + 1 honey", 45, 1, 5, 90, "Ice cream maker"],
 ["Frost-berry sorbet", "1 ice + 2 frost-berries", 35, 1, 5, 85, "Ice cream maker"],
 ["Moon-wheat bread", "2 flour", 40, 1, 1, 30, ""],
 ["Crater-potato mash", "2 crater-potatoes + 1 milk powder", 50, 1, 2, 40, ""],
 ["Star-tomato soup", "3 star-tomatoes + 1 void-onion", 60, 2, 3, 55, ""],
 ["Synth-steak and mash", "1 synth-steak + 1 crater-potato mash", 90, 3, 4, 95, ""],
 ["Plankton noodles", "2 ground protein + 1 flour", 70, 2, 2, 60, ""],
 ["Cave mushroom risotto", "2 cave mushrooms + 1 star-oats + 1 milk powder", 85, 3, 4, 90, ""],
 ["Glow-moss salad", "1 glow-moss + 1 star-tomato + 1 void-onion", 45, 2, 3, 50, ""],
 ["Moon-peach tart", "1 moon-peach + 1 flour + 1 honey", 60, 1, 5, 110, "Jasper's favourite"],
 ["Sun-fig preserves on toast", "1 sun-fig jam + 1 bread", 55, 1, 3, 70, ""],
 ["Grilled cave-trout", "1 cave-trout + 1 void-onion", 75, 3, 4, 100, "After the Harbinger"],
 ["Crayfish boil", "2 thermal crayfish + 1 crater-potato", 90, 4, 6, 150, "After the Harbinger"],
 ["Lantern-eel sushi", "1 lantern-eel + 1 star-oats + 1 glow-moss", 100, 4, 7, 220, "After the Harbinger"],
 ["King crab feast", "1 abyssal king crab + 2 crater-potatoes + 1 honey + 1 milk powder", 150, 6, 9, 420, "After the Harbinger"],
 ["Mess hall stew", "1 any meat or protein + 2 any vegetables", 80, 3, 3, 60, "Cheap way to feed many guests"],
 ["Station breakfast", "1 moon-wheat bread + 1 ground protein + 1 fruit", 60, 2, 3, 55, ""],
]
HOTEL_H = ["Hotel meal rule", "Detail"]
HOTEL = [
 ["Energy bar", "Like Stardew: every swing, cut, till and dig costs energy. Food tops it up. Sleeping refills it; collapsing costs credits and wakes you in the medbay (already in the game)."],
 ["The weekly meal", "Each Monday you give the hotel's kitchen bot one recipe from your cookbook. It cooks that dish for every guest, every day, all week."],
 ["How much to stock", "Servings needed = guests x 7. You load the ingredients into the kitchen's pantry chest; the bot takes them each morning. Example: 6 guests, Star-tomato soup = 42 servings = 126 star-tomatoes + 42 void-onions."],
 ["Running out", "If the pantry runs dry mid-week, guests get a plain ration that day: happiness falls and some leave early. A fully stocked week gives a bonus."],
 ["Guest happiness", "Each night: room comfort (from furniture) + meal happiness + extras (lounge, spa, ice cream) - complaints (no meal, broken things, noise)."],
 ["Pay and rating", "Nightly rate = room base x (1 + happiness bonus). Average happiness over the week sets the hotel's star rating (1-5). More stars bring more guests, richer guests and special visitors."],
 ["Variety", "Serving the same dish two weeks running gives less happiness. Better dishes (fish, crab, ice cream desserts) are worth much more but cost rarer ingredients."],
 ["Dessert slot (upgrade)", "Upgrade the kitchen bot with a second motor to add a dessert: ice cream is the best dessert in the game."],
 ["Who helps", "Evarra can teach recipes; Jasper sells bulk flour and milk powder; Merrow supplies plankton; the restored greenhouse feeds the menu."],
]
FURN_H = ["Furniture", "Room", "Recipe", "Comfort", "Style", "Sell (scrip)"]
FURN = []
def f(name, room, recipe, comfort, style, sell): FURN.append([name, room, recipe, comfort, style, sell])
# guest rooms
f("Single bed", "Guest room", "6 planks + 1 cotton cloth", 2, "Basic", 60)
f("Double bed", "Guest room", "10 planks + 2 cotton cloth", 4, "Comfort", 120)
f("Luxury double bed", "Guest room", "8 planks + 1 gold bar + 2 reinforced silk", 8, "Luxury", 400)
f("Bunk bed", "Guest room / family", "8 planks + 2 iron bar + 2 cotton cloth", 2, "Basic", 90)
f("Wardrobe", "Guest room", "12 planks + 1 iron bar", 2, "Basic", 80)
f("Mirrored wardrobe", "Guest room", "10 planks + 2 glass pane + 1 steel bar", 3, "Comfort", 150)
f("Bedside table", "Guest room", "4 planks", 1, "Basic", 25)
f("Bedside lamp", "Guest room", "1 glass pane + 1 copper wire + 1 copper bar", 1, "Comfort", 40)
f("Writing desk", "Guest room", "8 planks + 1 iron bar", 2, "Comfort", 90)
f("Desk chair", "Guest room", "4 planks + 1 leather", 1, "Comfort", 45)
f("Armchair", "Guest room / lounge", "6 planks + 2 leather", 2, "Comfort", 90)
f("Velvet armchair", "Guest room / lounge", "6 planks + 2 dyed cloth + 1 gold bar", 4, "Luxury", 260)
f("Rug (plain)", "Any", "2 cotton cloth", 1, "Basic", 30)
f("Rug (patterned)", "Any", "2 dyed cloth + 1 cotton cloth", 2, "Comfort", 70)
f("Moon-opal rug", "Any", "3 reinforced silk + 1 moon opal", 4, "Luxury", 300)
f("Curtains", "Guest room", "2 cotton cloth + 1 iron bar", 1, "Basic", 35)
f("Velvet curtains", "Guest room", "2 dyed cloth + 1 copper bar", 2, "Comfort", 80)
f("Viewport window frame", "Guest room", "4 glass pane + 2 aluminium bar", 3, "Comfort", 160)
f("Wall painting (crater)", "Any", "1 dyed cloth + 2 planks", 1, "Comfort", 60)
f("Holo-art frame", "Any", "1 circuit board + 1 glass pane + 1 aluminium bar", 3, "Luxury", 220)
f("Potted fern", "Any", "1 brick + 1 glow-moss", 1, "Basic", 20)
f("Glow-moss terrarium", "Any", "2 glass pane + 2 glow-moss + 1 seal kit", 2, "Comfort", 90)
f("Bookshelf", "Any", "10 planks", 1, "Basic", 50)
f("Minibar", "Guest room", "6 planks + 1 glass pane + 1 motor", 3, "Luxury", 250)
# bathroom
f("Toilet", "Bathroom", "3 brick + 1 glass pane + 1 seal kit", 2, "Basic", 60)
f("Washbasin", "Bathroom", "2 brick + 1 glass pane + 1 copper bar", 1, "Basic", 50)
f("Shower", "Bathroom", "3 glass pane + 1 steel bar + 1 seal kit", 2, "Comfort", 110)
f("Bathtub", "Bathroom", "4 brick + 2 steel bar + 1 seal kit", 4, "Luxury", 220)
f("Hot-spring tub", "Bathroom / spa", "6 brick + 2 titanium bar + 2 seal kit + 1 thermal quartz", 6, "Luxury", 500)
f("Towel rail", "Bathroom", "1 copper bar + 1 cotton cloth", 1, "Basic", 30)
# lobby, dining, lounge
f("Front desk bell", "Lobby", "1 gold bar", 1, "Luxury", 90)
f("Lobby sofa", "Lobby / lounge", "10 planks + 3 dyed cloth", 3, "Comfort", 160)
f("Fountain kit", "Lobby", "8 brick + 2 seal kit + 1 motor", 4, "Luxury", 350)
f("Dining table (4)", "Dining", "12 planks + 1 iron bar", 2, "Basic", 110)
f("Dining chair", "Dining", "4 planks", 1, "Basic", 25)
f("Banquet table (8)", "Dining", "20 planks + 2 steel bar + 2 cotton cloth", 4, "Luxury", 320)
f("Buffet counter", "Dining", "10 planks + 2 steel bar + 2 glass pane", 3, "Comfort", 200)
f("Chandelier", "Dining / lobby", "4 glass pane + 2 gold bar + 4 copper wire", 5, "Luxury", 480)
f("Bar counter", "Lounge", "14 planks + 2 steel bar + 1 glass pane", 3, "Comfort", 240)
f("Bar stool", "Lounge", "2 planks + 1 leather + 1 iron bar", 1, "Basic", 35)
f("Fireplace", "Lounge", "12 brick + 2 iron bar", 4, "Comfort", 260)
f("Piano", "Lounge", "20 planks + 4 copper wire + 1 steel bar", 5, "Luxury", 600)
f("Games table", "Lounge", "8 planks + 1 cotton cloth", 2, "Comfort", 120)
f("Aquarium (wall)", "Lounge / lobby", "6 glass pane + 2 seal kit + 1 motor + fish", 6, "Luxury", 700)
f("Telescope", "Lounge / rooms", "2 glass pane + 1 precision lens + 1 steel bar", 4, "Luxury", 450)
f("Ice cream counter", "Dining / lounge", "Ice cream maker + 8 planks + 2 glass pane", 4, "Comfort", 300)
# outdoor / station
f("Planter box", "Any", "4 planks + 2 stone", 1, "Basic", 20)
f("Brick path (5 tiles)", "Floors", "4 brick", 0, "Basic", 5)
f("Parquet floor (5 tiles)", "Floors", "6 planks + 1 resin", 1, "Comfort", 20)
f("Marble floor (5 tiles)", "Floors", "8 stone + 1 quartz", 2, "Luxury", 45)
f("Wallpaper (one wall)", "Walls", "2 dyed cloth", 1, "Comfort", 15)
f("Wall lamp", "Walls", "1 glass pane + 1 copper wire", 1, "Basic", 25)
f("Room sign / number plate", "Doors", "1 copper bar", 0, "Basic", 10)
f("Vending machine", "Halls", "2 steel bar + 1 motor + 1 circuit board + 2 glass pane", 2, "Comfort", 300)
SHEETS = [("Resources", RES_H, RES), ("Components", COMP_H, COMP), ("Tools and weapons", TOOL_H, TOOLS), ("Machines", MACH_H, MACH),
          ("Consumables", CONS_H, CONS), ("Food", FOOD_H, FOOD), ("Hotel meals", HOTEL_H, HOTEL), ("Hotel furniture", FURN_H, FURN)]
if __name__ == "__main__":
    for t, h, rows in SHEETS: print(t, len(rows))
