extends Node
# The hotel (Zachary, 24 Nov 2026; design: claude/echo-landing-hotel-design.md in the Project).
#
# Stage 1 (this file so far): S.A.R.A.'s call, building guest rooms and grading them, and the management desk.
#   - The first Monday after Ivan falls, S.A.R.A. gets a call: a civilian transport is coming, due on Friday.
#     Running a hotel is her dream, and she asks you to help.
#   - Guest rooms are built RimWorld-style in the hotel's two guest wings: walls on every side and a door make a
#     room. Hotel walls, doors and furniture are crafted (scripts/item_data.gd RECIPES) and set down from the
#     hotbar like the furnace (main.gd _build; FURNITURE below joins main.gd PLACEABLE).
#   - Each room is graded out of 2.5 stars on size, comfort and decoration (grade()). A guest's whole day is out
#     of 5: room 2.5, lunch 1.5, activities 1 (lunch and activities come in later stages).
#   - The management desk (the desk in your office) lists the rooms with their grades, what's holding each back,
#     and an open/closed switch: on Thursday you choose how many rooms to rent out.
# Stage 2: the weekly transport, guests, nightly pay and the end-of-night star screen.
#   - Every Friday from first_guests_day, the transport brings guests_for(rating) guests, one to each open room that
#     can be rented (the best rooms first). They stay Friday, Saturday and Sunday and leave on Sunday night.
#   - Each guest day is scored at 06:00 (everything has to be done in advance): room grade + lunch + activities,
#     out of 5. The score sets the guest's mood, the mood sets their pay for the night (MOOD_PAY), and the night's
#     moods move the hotel's star rating (MOOD_RATING). The pay goes in the day's account as "Hotel guests", and the
#     day summary shows the moods and the rating (datapad recap).
#   - Until lunch (stage 3) and activities (stage 4) exist, Jasper sends lunch over from the mess hall
#     (LUNCH_FOR_NOW stars) and the lounge as it is gives ACTIVITIES_FOR_NOW.
# F2 (debug builds): the hotel test kit (see debug_kit), then F2 again ends the day, to step through a weekend.
#
# Not run in Godot yet; written to be checked by Zachary.

const ItemData = preload("res://scripts/item_data.gd")
const MapData = preload("res://scripts/map_data.gd")

# Furniture for guest rooms, set down like the furnace. art: art/lunar/<art>.png; w, h in tiles.
# comfort and beauty feed grade(); "bed" makes a room rentable; "walk" means you can walk over it.
const FURNITURE := {
	"hotel_wall": {"art": "hotel_wall_piece", "w": 1, "h": 1, "name": "Hotel wall", "station": "", "decor": true, "wall": true},
	"hotel_door": {"art": "inner_door_s_frame", "w": 1, "h": 1, "name": "Hotel door", "station": "", "decor": true, "door": true, "walk": true},
	"guest_bed": {"art": "bed", "w": 2, "h": 3, "name": "Guest bed", "station": "", "decor": true, "bed": true, "comfort": 0.5},
	"fine_guest_bed": {"art": "bed_double_steel", "w": 3, "h": 3, "name": "Fine guest bed", "station": "", "decor": true, "bed": true, "comfort": 0.8},
	"guest_armchair": {"art": "armchair", "w": 2, "h": 2, "name": "Armchair", "station": "", "decor": true, "comfort": 0.2},
	"guest_dresser": {"art": "dresser_steel", "w": 2, "h": 2, "name": "Dresser", "station": "", "decor": true, "comfort": 0.15},
	"guest_wardrobe": {"art": "wardrobe", "w": 2, "h": 3, "name": "Wardrobe", "station": "", "decor": true, "comfort": 0.15},
	"guest_desk": {"art": "desk_steel", "w": 3, "h": 2, "name": "Writing desk", "station": "", "decor": true, "comfort": 0.1, "beauty": 0.05},
	"bedside_lamp": {"art": "bedside_lamp", "w": 1, "h": 2, "name": "Bedside lamp", "station": "", "decor": true, "comfort": 0.1, "beauty": 0.15},
	"guest_bookshelf": {"art": "bookshelf_steel", "w": 2, "h": 3, "name": "Bookshelf", "station": "", "decor": true, "beauty": 0.2},
	"potted_plant": {"art": "potted_plant", "w": 1, "h": 2, "name": "Potted plant", "station": "", "decor": true, "beauty": 0.2},
	"small_fern": {"art": "fern", "w": 1, "h": 1, "name": "Small fern", "station": "", "decor": true, "beauty": 0.1},
	"berry_rug": {"art": "rug_berry", "w": 3, "h": 2, "name": "Berry rug", "station": "", "decor": true, "beauty": 0.3, "walk": true},
	# Tobbin's 8 (24 Nov): his first real-wood chair, and the ones you make once he's taught you
	"heirloom_chair": {"art": "heirloom_chair", "w": 1, "h": 2, "name": "Heirloom chair", "station": "", "decor": true, "comfort": 0.3, "beauty": 0.3},
}

const ROOM_MAX := 2.5
const SIZE_MAX := 0.5
const COMFORT_MAX := 1.0
const DECOR_MAX := 1.0
const MIN_TILES := 6                # smaller than this is a cupboard, not a room
const FULL_SIZE_TILES := 30         # this many floor tiles earns the whole size half-star
const FLOOD_LIMIT := 160            # a space bigger than this isn't closed in (it leaks into the corridor)
const GUEST_WINGS := ["West guest wing", "East guest wing"]
const TIERS := [[2.0, "Luxurious"], [1.4, "Comfortable"], [0.8, "Decent"], [0.0, "Shabby"]]

const MOODS := ["Angry", "Neutral", "Happy", "Ecstatic"]
const MOOD_FROM := [0.0, 2.0, 3.0, 4.25]                  # a day's score (out of 5) for each mood, low to high
const MOOD_PAY := {"Angry": 0.25, "Neutral": 0.75, "Happy": 1.0, "Ecstatic": 1.5}
const MOOD_RATING := {"Angry": -0.3, "Neutral": 0.0, "Happy": 0.1, "Ecstatic": 0.4}   # stars per guest-night, averaged
const RATING_START := 2.5
const BASE_PAY_AT_3 := 200.0        # a guest's pay for a night at a 3-star hotel; it scales with the rating
const GUESTS_BY_STARS := [0, 2, 4, 8, 14, 20]              # how many come each week at 0..5 stars
const FIVE_STAR_PERK := 1.2         # Stu's 8, Five-Star Partner: base pay x1.2 (your share of the tips)
const LINENS_COMFORT := 0.2         # Sesska's 8, Void-Silk Linens: every guest bed's room is this much comfier
const LUNCH_FOR_NOW := 0.75         # until the hotel kitchen (stage 3): Jasper's lunch from the mess hall
const ACTIVITIES_FOR_NOW := 0.5     # until activities (stage 4): the lounge as it is
const RACES := ["Terran", "Moogli", "Zaa'sh", "Vuultam", "Chernobog", "Sesskan"]

var world                           # main.gd
var rating := RATING_START          # the hotel's stars, 1 to 5
var guests: Array = []              # this weekend's: [{"room", "race", "score", "mood"}]
var last_night: Dictionary = {}     # the night just paid, for the day summary: {"moods", "pay", "from", "to", "left"}
var _news := ""
var stage := 0                      # 0 before S.A.R.A.'s call, 1 after it (guests from first_guests_day)
var first_guests_day := -1          # the Friday the first transport arrives
var room_open: Dictionary = {}      # room id -> false when closed (rooms are open by default)
var _call_due := false


func setup(main_world) -> void:
	world = main_world


func tick(_delta: float) -> void:
	if world.dialogue.active:
		return
	if _call_due:
		_call_due = false
		_sara_call()
	elif _news != "":
		world._toast(_news)
		_news = ""


# ---------------------------------------------------------------- the call

# main.gd _next_day: the first Monday after Ivan falls, S.A.R.A. gets the call.
func new_day() -> void:
	var weekday: int = (int(world.day) - 1) % 7
	if stage == 0 and int(world.artie_found_day) >= 0 and int(world.day) > int(world.artie_found_day) and weekday == 0:
		stage = 1
		first_guests_day = int(world.day) + 4
		_call_due = true
	if stage < 1 or int(world.day) < first_guests_day:
		return
	if weekday == 4:
		_check_in()
	if weekday >= 4 and not guests.is_empty():
		_score_day()


# ---------------------------------------------------------------- guests

static func guests_for(stars: float) -> int:
	var i: int = clampi(int(floor(stars)), 0, 5)
	if i >= 5:
		return GUESTS_BY_STARS[5]
	return int(round(lerpf(GUESTS_BY_STARS[i], GUESTS_BY_STARS[i + 1], stars - i)))


func base_pay() -> int:
	var pay: float = BASE_PAY_AT_3 * rating / 3.0
	if world._flag("perk_five_star_partner"):
		pay *= FIVE_STAR_PERK
	return int(round(pay))


# Friday 06:00: the transport docks. One guest to each open room that can be rented, best rooms first.
func _check_in() -> void:
	guests.clear()
	var ready: Array = []
	for room in rooms():
		var g: Dictionary = grade(room)
		if bool(g["rentable"]) and is_open(str(room["id"])):
			ready.append([float(g["total"]), str(room["id"])])
	ready.sort_custom(func(a, b): return float(a[0]) > float(b[0]))
	var n: int = mini(ready.size(), guests_for(rating))
	for i in n:
		guests.append({"room": str(ready[i][1]), "race": RACES[randi() % RACES.size()], "score": 0.0, "mood": "Neutral"})
	if n == 0:
		_news = "The transport docked, but the hotel had no rooms open. Its passengers stayed aboard."
	else:
		_news = "The transport docked: %d guest%s checked in at the hotel, until Sunday." % [n, "" if n == 1 else "s"]


# Each guest day at 06:00: score every guest on the hotel as it is now.
func _score_day() -> void:
	var by_id := {}
	for room in rooms():
		by_id[str(room["id"])] = room
	for g in guests:
		var room_stars := 0.0
		if by_id.has(str(g["room"])):
			var gr: Dictionary = grade(by_id[str(g["room"])])
			room_stars = float(gr["total"]) if bool(gr["rentable"]) else 0.0
		var score: float = room_stars + lunch_stars() + activity_stars()
		g["score"] = score
		g["mood"] = mood_for(score)


static func mood_for(score: float) -> String:
	var mood: String = MOODS[0]
	for i in MOODS.size():
		if score >= float(MOOD_FROM[i]):
			mood = MOODS[i]
	return mood


func lunch_stars() -> float:
	return LUNCH_FOR_NOW


func activity_stars() -> float:
	return ACTIVITIES_FOR_NOW


# main.gd _end_day, before the day's account is added up: pay for tonight if guests are staying, move the rating,
# and on Sunday night see them off.
func night_pay() -> void:
	last_night = {}
	var weekday: int = (int(world.day) - 1) % 7
	if guests.is_empty() or weekday < 4:
		return
	var moods := {"Angry": 0, "Neutral": 0, "Happy": 0, "Ecstatic": 0}
	var pay := 0
	var change := 0.0
	var base := base_pay()
	for g in guests:
		var mood: String = str(g["mood"])
		moods[mood] = int(moods[mood]) + 1
		pay += int(round(base * float(MOOD_PAY[mood])))
		change += float(MOOD_RATING[mood])
	var before := rating
	rating = clampf(rating + change / guests.size(), 1.0, 5.0)
	if pay > 0:
		world._money(pay, "Hotel guests")
	last_night = {"moods": moods, "pay": pay, "from": before, "to": rating, "left": weekday == 6}
	if weekday == 6:
		guests.clear()


func _sara_call() -> void:
	world._say("Sara", [
		"[happy] Pilot! Pilot, are you awake? I just took a call. A civilian transport, the Merrow Line. It's coming here.",
		"Passengers! Real travellers, who want to stop at the Landing for the weekend. They asked if we have rooms.",
		"We have a hotel. We have always had a hotel. It has just been... empty. For a very long time.",
		"[bashful] I have wanted to run it since before anyone lived here. Would you help me? I can't carry a bed. I don't have hands.",
		"The guest wings are bare. Build rooms there: four walls and a door make a room, and every guest needs a bed.",
		"Craft walls, doors and furniture, set them down, then check your desk in the hotel office. It will tell you what the guests will think.",
		"The ship arrives on Friday. That gives us a week. [happy] Oh, this is going to be wonderful.",
	])
	world.sfx("quest")


# ---------------------------------------------------------------- rooms

# Every closed room in the guest wings: [{"id", "tiles": {Vector2i: true}, "doors": [Vector2i], "things": [item]}].
func rooms() -> Array:
	var walls := {}
	var doors := {}
	for e in world.placed:
		if str(e["area"]) != "hotel":
			continue
		var spec: Dictionary = FURNITURE.get(str(e["item"]), {})
		var at := Vector2i(int(e["x"]), int(e["y"]))
		if spec.get("wall", false):
			walls[at] = true
		elif spec.get("door", false):
			doors[at] = true
	var found: Array = []
	var seen := {}
	for d in doors:
		for step in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var start: Vector2i = d + step
			if seen.has(start) or _barrier(start, walls, doors):
				continue
			var tiles: Dictionary = _flood(start, walls, doors)
			for t in tiles:
				seen[t] = true
			if tiles.is_empty() or tiles.size() > FLOOD_LIMIT or not _in_wings(tiles):
				continue
			found.append(_room_from(tiles, doors))
	found.sort_custom(func(a, b): return str(a["id"]) < str(b["id"]))
	return found


func _flood(start: Vector2i, walls: Dictionary, doors: Dictionary) -> Dictionary:
	var tiles := {start: true}
	var todo: Array = [start]
	while not todo.is_empty() and tiles.size() <= FLOOD_LIMIT:
		var t: Vector2i = todo.pop_back()
		for step in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var n: Vector2i = t + step
			if not tiles.has(n) and not _barrier(n, walls, doors):
				tiles[n] = true
				todo.append(n)
	return tiles


# Map walls, hotel walls and doors close a room in; furniture doesn't.
func _barrier(t: Vector2i, walls: Dictionary, doors: Dictionary) -> bool:
	if walls.has(t) or doors.has(t):
		return true
	var rows: Array = MapData.AREAS["hotel"]["floor"]
	if t.y < 0 or t.y >= rows.size() or t.x < 0 or t.x >= str(rows[t.y]).length():
		return true
	return MapData.SOLID_FLOOR.contains(str(rows[t.y])[t.x])


func _in_wings(tiles: Dictionary) -> bool:
	for z in MapData.AREAS["hotel"]["zones"]:
		if not GUEST_WINGS.has(str(z[0])):
			continue
		var inside := true
		for t in tiles:
			if t.x < int(z[1]) or t.x > int(z[3]) or t.y < int(z[2]) or t.y > int(z[4]):
				inside = false
				break
		if inside:
			return true
	return false


func _room_from(tiles: Dictionary, doors: Dictionary) -> Dictionary:
	var first := Vector2i(9999, 9999)
	for t in tiles:
		if t.y < first.y or (t.y == first.y and t.x < first.x):
			first = t
	var room_doors: Array = []
	for d in doors:
		for step in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			if tiles.has(d + step):
				room_doors.append(d)
				break
	var inside: Array = []
	for e in world.placed:
		if str(e["area"]) != "hotel" or not FURNITURE.has(str(e["item"])):
			continue
		var spec: Dictionary = FURNITURE[str(e["item"])]
		if spec.get("wall", false) or spec.get("door", false):
			continue
		if tiles.has(Vector2i(int(e["x"]), int(e["y"]))):
			inside.append(str(e["item"]))
	return {"id": "%d_%d" % [first.x, first.y], "tiles": tiles, "doors": room_doors, "things": inside}


# A room's stars: {"size", "comfort", "decor", "total", "tier", "rentable", "note"}.
func grade(room: Dictionary) -> Dictionary:
	var n: int = room["tiles"].size()
	var size: float = SIZE_MAX * clampf(float(n - MIN_TILES) / float(FULL_SIZE_TILES - MIN_TILES), 0.0, 1.0)
	var comfort := 0.0
	var beauty := 0.0
	var bed := 0.0
	for item in room["things"]:
		var spec: Dictionary = FURNITURE[item]
		if spec.get("bed", false):
			bed = maxf(bed, float(spec.get("comfort", 0.0)))      # one guest, one bed: the best one counts
		else:
			comfort += float(spec.get("comfort", 0.0))
		beauty += float(spec.get("beauty", 0.0))
	comfort = minf(COMFORT_MAX, bed + comfort)
	if bed > 0.0 and world._flag("perk_void_silk_linens"):
		comfort = minf(COMFORT_MAX, comfort + LINENS_COMFORT)
	# bigger rooms need more decoration to look finished
	var decor: float = minf(DECOR_MAX, beauty / (0.5 + n / 40.0))
	var total: float = size + comfort + decor
	var rentable: bool = n >= MIN_TILES and bed > 0.0
	var note := ""
	if n < MIN_TILES:
		note = "Too small: needs %d floor tiles" % MIN_TILES
	elif bed <= 0.0:
		note = "No bed: every guest needs one"
	else:
		var gaps := {"size": SIZE_MAX - size, "comfort": COMFORT_MAX - comfort, "decoration": DECOR_MAX - decor}
		var worst := ""
		for k in gaps:
			if worst == "" or float(gaps[k]) > float(gaps[worst]):
				worst = k
		if float(gaps[worst]) < 0.05:
			note = "Guests will love it"
		else:
			note = {"size": "Cramped: build it bigger",
				"comfort": "Needs comfort: chair, dresser, better bed",
				"decoration": "Bare: add plants, a rug, a lamp"}[worst]
	return {"size": size, "comfort": comfort, "decor": decor, "total": total, "tier": tier_name(total),
		"rentable": rentable, "note": note}


static func tier_name(stars: float) -> String:
	for t in TIERS:
		if stars >= float(t[0]):
			return str(t[1])
	return "Shabby"


func is_open(id: String) -> bool:
	return bool(room_open.get(id, true))


func toggle(id: String) -> void:
	room_open[id] = not is_open(id)
	world.sfx("click")


# ---------------------------------------------------------------- the desk

# The datapad page for the management desk (opened through scripts/shops.gd as shop "Hotel").
func desk_tabs() -> Array:
	var rows: Array = []
	var list: Array = rooms()
	var ready := 0
	for i in list.size():
		var room: Dictionary = list[i]
		var g: Dictionary = grade(room)
		var id: String = str(room["id"])
		if bool(g["rentable"]) and is_open(id):
			ready += 1
		var label := "Open" if is_open(id) else "Closed"
		rows.append(["guest_bed" if bool(g["rentable"]) else "hotel_wall", "Room %d, %s" % [i + 1, str(g["tier"])],
			"%d tiles. Size %.1f, comfort %.1f, decor %.1f. %s" % [room["tiles"].size(), float(g["size"]), float(g["comfort"]), float(g["decor"]), str(g["note"])],
			label if bool(g["rentable"]) else "Not rentable",
			[["room/" + id, "Close" if is_open(id) else "Open", bool(g["rentable"])]], [float(g["total"]), 3]])
	if rows.is_empty():
		rows.append(["hotel_wall", "No guest rooms yet", "Build in the guest wings: walls on every side, a door, and a bed inside", "", []])
	var about: Array = [
		["guest_bed", "%d room%s ready for guests" % [ready, "" if ready == 1 else "s"],
			_arrival_text(), "", []],
		["hotel_wall", "How rooms are graded (2.5 stars)", "Size up to 0.5, comfort up to 1, decoration up to 1", "", []],
		["potted_plant", "A guest's day (5 stars)", "Room 2.5, lunch 1.5, activities 1. Lunch and activities come soon", "", []],
	]
	about.insert(0, ["potted_plant", "Hotel rating",
		"%.1f stars. Base pay %d a guest a night; about %d guests a week" % [rating, base_pay(), guests_for(rating)], "", [], [rating, 5]])
	if not guests.is_empty():
		var counts := {}
		for g in guests:
			counts[g["mood"]] = int(counts.get(g["mood"], 0)) + 1
		var parts: Array = []
		for m in MOODS:
			if counts.has(m):
				parts.append("%d %s" % [int(counts[m]), str(m).to_lower()])
		about.insert(1, ["guest_bed", "%d guest%s staying" % [guests.size(), "" if guests.size() == 1 else "s"],
			"Today: " + ", ".join(parts), "", []])
	return [["Rooms", rows], ["Hotel", about]]


func _arrival_text() -> String:
	if stage == 0:
		return "The hotel is closed. Nobody is coming yet"
	var weekday: int = (int(world.day) - 1) % 7
	if int(world.day) < first_guests_day:
		return "The first transport arrives on Friday (day %d)" % first_guests_day
	if weekday <= 3:
		return "Guests arrive on Friday. Thursday is the day to open or close rooms"
	return "Guests stay Friday to Sunday"


func on_action(verb: String, id: String) -> void:
	if verb == "room":
		toggle(id)


# ---------------------------------------------------------------- journal and saving

func journal() -> Array:
	if stage == 0:
		return []
	var ready := 0
	for room in rooms():
		if bool(grade(room)["rentable"]) and is_open(str(room["id"])):
			ready += 1
	return [["S.A.R.A.'s hotel", [
		"Build guest rooms in the hotel's guest wings: walls on every side, a door, and a bed. Craft them at a manufacturing hub.",
		"Check each room at your desk in the hotel office. Rooms ready for guests: %d." % ready,
		_arrival_text() + ".",
	], false]]


# F2 (debug builds): start the hotel, jump to Thursday morning and hand over enough to build two rooms. After
# that, F2 ends the day (as if you slept), so you can step through a weekend: check-in, three nights, check-out.
func debug_kit() -> void:
	if stage > 0:
		world._end_day()
		return
	if int(world.artie_found_day) < 0:
		world.artie_found_day = int(world.day)
	var weekday: int = (int(world.day) - 1) % 7
	world.day = int(world.day) + (3 - weekday + 7) % 7          # the coming Thursday (or today)
	stage = 1
	first_guests_day = int(world.day) + 1
	var kit := {"hotel_wall": 60, "hotel_door": 2, "guest_bed": 1, "fine_guest_bed": 1, "guest_armchair": 1,
			"bedside_lamp": 2, "potted_plant": 2, "berry_rug": 1, "guest_bookshelf": 1}
	for item in kit:
		world._give(str(item), int(kit[item]))
	world._toast("Debug: hotel started, it's Thursday (day %d). Build rooms in a guest wing, then F2 to sleep." % int(world.day))


func save(cfg: ConfigFile) -> void:
	cfg.set_value("hotel", "rating", rating)
	cfg.set_value("hotel", "guests", guests)
	cfg.set_value("hotel", "stage", stage)
	cfg.set_value("hotel", "first_guests_day", first_guests_day)
	cfg.set_value("hotel", "room_open", room_open)


func load_from(cfg: ConfigFile) -> void:
	stage = int(cfg.get_value("hotel", "stage", 0))
	rating = clampf(float(cfg.get_value("hotel", "rating", RATING_START)), 1.0, 5.0)
	var saved_guests = cfg.get_value("hotel", "guests", [])
	guests = saved_guests if saved_guests is Array else []
	first_guests_day = int(cfg.get_value("hotel", "first_guests_day", -1))
	var saved = cfg.get_value("hotel", "room_open", {})
	room_open = saved if saved is Dictionary else {}
