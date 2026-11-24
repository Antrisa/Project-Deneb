extends RefCounted
# Perks and keepsakes (24 Nov 2026), for the datapad's Perks tab in the inventory (Zachary: "a tab in the inventory
# for perks, and the icons will be stuff like freyas wrench etc. showing all the perks you have").
#
# Heart events give them (scripts/heart_events.gd: ["perk", id, toast] sets story flag "perk_<id>",
# ["keepsake", id, toast] sets "keepsake_<id>"); scripts/datapad_bridge.gd lists the ones you have, in this order.
# Each has an icon in art/perks.png (stand-ins by tools/dev/perk_icons.py: the thing from the heart event).
# "works": false marks the ones whose effect isn't in the game yet; the tab says so.

const PERKS := {
	# Freya
	"pioneer_stabilizer": {"icon": 0, "name": "Pioneer Stabilizer", "from": "Freya", "works": true,
		"desc": "Jorvik's FTL stabilizer, finished at last: an ion storm no longer halves your reactor."},
	"master_mechanic": {"icon": 1, "name": "Master Mechanic", "from": "Freya", "works": true,
		"desc": "20% off ship upgrades."},
	# Jasper, Evarra, and the two of them together
	"parisian_bistro_menu": {"icon": 2, "name": "Parisian Bistro Menu", "from": "Jasper", "works": false,
		"desc": "Jasper's bistro dishes, on the mess hall's menu."},
	"sous_chefs_blessing": {"icon": 3, "name": "Sous-Chef's Blessing", "from": "Jasper", "works": true,
		"desc": "Food and drink buffs last 20% longer."},
	"honey_lavender_brioche": {"icon": 4, "name": "Honey-Lavender Brioche", "from": "Evarra", "works": false,
		"desc": "A recipe: Evarra's brioche, once there's honey."},
	"green_thumb": {"icon": 5, "name": "Green Thumb", "from": "Evarra", "works": false,
		"desc": "Better-quality crops."},
	"wildflower_honey": {"icon": 6, "name": "Wildflower Honey", "from": "Jasper & Evarra", "works": false,
		"desc": "The garden dome's bees make honey."},
	"starlight_souffle": {"icon": 7, "name": "Starlight Souffle", "from": "Jasper & Evarra", "works": false,
		"desc": "A recipe: Starlight Souffle & Lunar Truffle Glaze, a big boost at the Grand Hotel Inspection."},
	"family_table": {"icon": 8, "name": "Family Table", "from": "Jasper & Evarra", "works": true,
		"desc": "Cooked meals restore 25% more health and energy."},
	# Job
	"bedrock_strength": {"icon": 9, "name": "Bedrock Strength", "from": "Job", "works": true,
		"desc": "Mining uses 20% less energy, and more geodes turn up."},
	# Quill
	"xeno_salve": {"icon": 10, "name": "Xeno-Salve", "from": "Quill", "works": false,
		"desc": "A recipe: Xeno-Salve restores full health and cures what ails you."},
	"guardian_medic": {"icon": 11, "name": "Guardian Medic", "from": "Quill", "works": true,
		"desc": "Two more hearts of health, and collapsing costs no Scrip."},
	# Ix'ali
	"star_knight_aegis": {"icon": 12, "name": "Star-Knight Aegis", "from": "Ix'ali", "works": false,
		"desc": "Ix'ali can forge the Star-Knight Aegis armour tier."},
	"chivalric_guard": {"icon": 13, "name": "Chivalric Guard", "from": "Ix'ali", "works": true,
		"desc": "Take 20% less damage."},
	# Artie
	"junior_scout_reports": {"icon": 14, "name": "Junior Scout Reports", "from": "Artie", "works": false,
		"desc": "The Junior Scouts mark rare finds on your map."},
	"thrifty": {"icon": 15, "name": "Thrifty", "from": "Artie", "works": true,
		"desc": "Geodes sometimes hold rare finds. (Recycling too, once the station has a recycler.)"},
	# Stu
	"five_star_partner": {"icon": 16, "name": "Five-Star Partner", "from": "Stu", "works": true,
		"desc": "+20% hotel income and tips."},
	# Ana
	"wingmate": {"icon": 17, "name": "Wingmate", "from": "Ana", "works": true,
		"desc": "+20% ship evasion, and your fold drive charges a fifth faster."},
	# S.A.R.A.
	"concierge": {"icon": 18, "name": "Concierge", "from": "S.A.R.A.", "works": true,
		"desc": "S.A.R.A. sends you to any of her pads, and pings you each morning with what's ready."},
	# Tar'Besh
	"relic_appraisal": {"icon": 19, "name": "Relic Appraisal", "from": "Tar'Besh", "works": true,
		"desc": "+25% on the Scrip the museum pays you for every 5 relics you give."},
	# Zaas
	"deep_sea_sonar_lure": {"icon": 20, "name": "Deep-Sea Sonar Lure", "from": "Zaas", "works": false,
		"desc": "A lure for the deep water, for when there's fishing."},
	# Vzz'ket, and Vzz'ket & Rusk
	"monster_radar": {"icon": 21, "name": "Cavern Monster Radar", "from": "Vzz'ket", "works": true,
		"desc": "S.A.R.A. warns you what's waiting on the floor below."},
	"chitin_piercer_traps": {"icon": 22, "name": "Chitin-Piercer Traps", "from": "Vzz'ket & Rusk", "works": false,
		"desc": "Ix'ali's traps at the cavern gate."},
	# Bram
	"moogli_trade_beacon": {"icon": 23, "name": "Moogli Trade Beacon", "from": "Bram", "works": true,
		"desc": "On a free flight, spend 1 fuel to call the Ollo family trader to where you are."},
	# Tikka & Sesska
	"smelter_overclock": {"icon": 24, "name": "Smelter Overclock", "from": "Tikka", "works": true,
		"desc": "Every furnace smelts in half the time."},
	"void_silk_linens": {"icon": 25, "name": "Void-Silk Linens", "from": "Sesska", "works": true,
		"desc": "Luxury linens for the hotel's guest beds: every guest room is more comfortable."},
	# Maren, Owen & Pip
	"advanced_med_stims": {"icon": 26, "name": "Advanced Med-Stims", "from": "Maren", "works": true,
		"desc": "Medpacks heal twice as much."},
	"library_lore_compendium": {"icon": 27, "name": "Lore Compendium", "from": "Owen", "works": false,
		"desc": "The codexes you find will fill it in."},
	# Tobbin, Merrow & Nub
	"heirloom_chair": {"icon": 28, "name": "Heirloom Chair", "from": "Tobbin", "works": true,
		"desc": "The recipe: 3 real-wood planks and a hide, at a manufacturing hub."},
	"hydro_boost": {"icon": 29, "name": "Hydro-Boost", "from": "Merrow", "works": true,
		"desc": "Your hydroponic beds grow 20% faster."},
	# Garrick, Saffi & Kit
	"self_defence": {"icon": 30, "name": "Self-Defence Class", "from": "Garrick", "works": true,
		"desc": "On your own ship, your crew hit boarders half again as hard."},
	"well_fed": {"icon": 31, "name": "Well Fed", "from": "Saffi", "works": true,
		"desc": "Your energy bar is 30 longer."},
}

const KEEPSAKES := {
	"wrench_pendant": {"icon": 32, "name": "Wrench Pendant", "from": "Freya",
		"desc": "A tiny wrench on a chain, made from the wrench Jorvik gave her when she was six."},
	"jasper_apron": {"icon": 33, "name": "Cafe Apron", "from": "Jasper",
		"desc": "An apron with both your names stitched on the pocket."},
	"pressed_flower_frame": {"icon": 34, "name": "Pressed Flowers", "from": "Evarra",
		"desc": "The flowers from her crown, pressed and framed."},
	"oar_charm": {"icon": 35, "name": "Oar Charm", "from": "Job",
		"desc": "A little carved oar on a cord, worn smooth by his thumbs."},
	"stethoscope_compass": {"icon": 36, "name": "Stethoscope Compass", "from": "Quill",
		"desc": "A brass charm he engraved himself: a stethoscope on one side, a compass on the other."},
	"pauldron": {"icon": 37, "name": "Ceremonial Pauldron", "from": "Ix'ali",
		"desc": "One of a matching pair she forged, lighter than it looks."},
	"scoutmaster_badge": {"icon": 38, "name": "Scoutmaster Badge", "from": "Artie",
		"desc": "Honorary Scoutmaster, by vote of the Junior Scouts."},
	"silver_bell": {"icon": 39, "name": "Silver Bell", "from": "Stu",
		"desc": "A little silver bell like the one on the desk. Ring it and he'll come running."},
	"flight_jacket": {"icon": 40, "name": "Flight Jacket", "from": "Ana",
		"desc": "A flight jacket in your size, Sesska's stitching. Hers has both your initials on the collar."},
	"family_photo": {"icon": 41, "name": "Family Photo", "from": "Jasper & Evarra",
		"desc": "Jasper, Evarra and you, above the mess hall counter."},
}

const ICON_COUNT := 42
