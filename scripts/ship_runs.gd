# Normal ship runs (slice 2, 22 Nov 2026; design: claude/echo-landing-ship-combat.md section 2).
# Once the first two flights are done, Launch control offers a free flight. Each day has its own map, made here
# from the day number: stops on rings 1-3 (rings 4-5 open later with a bigger tank or a bigger ship), each linked
# to its neighbours on its ring and to the nearest stops on the rings either side. You jump along a link for one
# fuel cell, and fold home (free outside a fight) whenever you like, which ends the run.
#
# What a stop holds is decided when you get there (you don't know until you jump):
#   beacon   - a fight (more likely further out) or a random event from the pool for that zone and ring
#   distress - a distress event for that zone and ring
#   store    - the store window
#   store    - the zone's store (ShipData.ZONE_STORE: Terran depot, Moogli trader, Collective market, pirate fence)
#   nest     - the Rabble's Nest, until you've raided it: three fights in a row (main.gd _nest_*)
#   special  - after the Nest falls, a smaller pirate stronghold on each run (a hard fight, better loot)
#   ooma     - Ooma's ship, the special merchant, on the days she isn't on the station (not Wed or Sat)
# Hidden stops (23 Nov): an event's "reveal: <name>" adds one next to where you are (add_hidden): a wreck or old
# survey site to pick over, a quiet sector to rest in, a pirate market, or another stronghold.
# Events come from SpaceEvents.EVENTS (the ones with "kind", "zones" and "rings", not "story"); none repeats in a
# run. Fights draw the zone's own ships or Rabble raiders (a cutter or a repainted culture ship).

const SpaceEvents = preload("res://scripts/space_events.gd")
const ShipData = preload("res://scripts/ship_data.gd")
const ItemData = preload("res://scripts/item_data.gd")

const MAX_RING := 3                          # rings open on a run with the starting tank (the tank upgrade opens 4 and 5)
const ZONE_KEYS := ["Terran", "Zaa'sh", "Reach", "Collective"]   # ShipData.ZONES order; the events' zone names
const FIGHT_CHANCE := [0.0, 0.25, 0.35, 0.45, 0.5, 0.55]          # a beacon being a fight, by ring
const ZONE_SHIPS := {
	"Terran": ["terran_patrol"],
	"Zaa'sh": ["zaash_skiff"],
	"Collective": ["collective_freighter"],
	"Reach": ["rabble_cutter", "loyalist_gunship"],
}
const RAIDERS := ["rabble_cutter", "terran_patrol_rabble", "zaash_skiff_rabble", "moogli_trader_rabble",
	"collective_freighter_rabble", "vuultam_garden_rabble", "ervani_courier_rabble", "arachnay_weaver_rabble",
	"scyldar_lantern_rabble"]
const STORE_NAMES := {"Terran": "Terran supply depot", "Zaa'sh": "Moogli trader", "Reach": "Pirate fence",
	"Collective": "Collective market"}
const ABOUT := {
	"beacon": "An ordinary beacon. Salvage, travellers or pirates: you find out when you get there.",
	"distress": "Someone is calling for help on an open band.",
	"store": "A trader. Repairs, fuel, missiles and weapons, for a price.",
	"special": "A Rabble stronghold dug into an asteroid. Heavily armed.",
	"nest": "The Rabble's Nest: their home base, guarded by pickets and a gun platform. One raid, if you dare.",
	"ooma": "Ooma's ship, hung with lanterns. Rare goods for rare customers.",
	"wreck": "Something worth picking over, if nobody beats you to it.",
	"quiet": "A still patch of space, off every trade lane. Somewhere to rest and patch up.",
}
# Hazards (23 Nov): a beacon, distress signal or stronghold from ring 2 out may sit in one, by zone. They change
# the fight there (ship_battle.gd _tick_space): asteroids hit either ship, flares start fires on both, a nebula
# adds evasion to both, an ion storm halves your reactor.
const HAZARD_CHANCE := 0.25
const ZONE_HAZARD := {"Reach": "asteroids", "Terran": "flare", "Zaa'sh": "nebula", "Collective": "ion_storm"}
const HAZARD_ABOUT := {"asteroids": "Asteroids drift through: rocks will hit both ships.",
	"flare": "A star close by: its flares start fires on both ships.",
	"nebula": "Inside a nebula: both ships are harder to hit.",
	"ion_storm": "An ion storm: your reactor runs at half power here."}

# What an event's "reveal: <name>" adds to the map: [kind, name, store id or ""]. Anything else is a wreck.
const REVEALS := {
	"wreck field": ["wreck", "Wreck field", ""],
	"old survey site": ["wreck", "Old survey site", ""],
	"pirate stronghold": ["special", "Pirate stronghold", ""],
	"quiet sector": ["quiet", "Quiet sector", ""],
	"pirate market": ["store", "Pirate market", "pirate_fence"],
}


static func zone_of(angle: float) -> String:
	var a: float = fposmod(angle, 360.0)
	if a >= 225.0 and a < 315.0:
		return "Terran"
	if a >= 315.0 or a < 45.0:
		return "Zaa'sh"
	if a < 135.0:
		return "Reach"
	return "Collective"


# A day's map: [{"kind", "name", "ring", "angle", "about", "zone", "links": [stop indices], "seen": false}].
# Ring 1's stops are linked to the Landing (stop -1).
static func make_run(day: int, ring_stops: Array, max_ring := MAX_RING, nest_done := false, ooma_out := false) -> Array:
	var rng := RandomNumberGenerator.new()
	rng.seed = 7919 * day + 17
	var stops: Array = []
	var by_ring: Array = [[]]
	for ring in range(1, max_ring + 1):
		var n: int = int(ring_stops[ring])
		var turn: float = rng.randf() * 360.0 / n
		var here: Array = []
		for k in range(n):
			var ang: float = turn + k * 360.0 / n + rng.randf_range(-8.0, 8.0)
			here.append(stops.size())
			stops.append({"kind": "beacon", "ring": ring, "angle": fposmod(ang, 360.0), "links": [], "seen": false})
		by_ring.append(here)
	# what kind each stop is: mostly beacons; a store on every ring; a distress signal or two per ring; the
	# stronghold on the outermost ring, in the Reach
	for ring in range(1, max_ring + 1):
		var here: Array = by_ring[ring]
		var order: Array = here.duplicate()
		_shuffle(order, rng)
		var stores: int = 1
		var distress: int = 1 + int(ring >= 2)
		for i in order:
			if stores > 0:
				stops[i]["kind"] = "store"
				stores -= 1
			elif distress > 0:
				stops[i]["kind"] = "distress"
				distress -= 1
	var reach: Array = []
	for i in by_ring[max_ring]:
		if zone_of(float(stops[i]["angle"])) == "Reach" and str(stops[i]["kind"]) == "beacon":
			reach.append(i)
	if reach.size() > 0:
		stops[reach[rng.randi() % reach.size()]]["kind"] = "special" if nest_done else "nest"
	if ooma_out:
		var plain: Array = []
		for i in by_ring[mini(2, max_ring)]:
			if str(stops[i]["kind"]) == "beacon":
				plain.append(i)
		if not plain.is_empty():
			stops[plain[rng.randi() % plain.size()]]["kind"] = "ooma"
	# links: neighbours on the same ring, and the nearest one or two on the next ring out
	for ring in range(1, max_ring + 1):
		var here: Array = by_ring[ring]
		var ordered: Array = here.duplicate()
		ordered.sort_custom(func(a, b): return float(stops[a]["angle"]) < float(stops[b]["angle"]))
		for k in range(ordered.size()):
			_link(stops, ordered[k], ordered[(k + 1) % ordered.size()])
		if ring < max_ring:
			for i in here:
				var out: Array = by_ring[ring + 1].duplicate()
				out.sort_custom(func(a, b): return _gap(stops, i, a) < _gap(stops, i, b))
				_link(stops, i, out[0])
				if _gap(stops, i, out[1]) < 360.0 / float(ring_stops[ring + 1]) * 1.2:
					_link(stops, i, out[1])
	for s in stops:
		var z: String = zone_of(float(s["angle"]))
		s["zone"] = z
		match str(s["kind"]):
			"store":
				s["name"] = STORE_NAMES[z]
				s["store"] = ShipData.ZONE_STORE[z]
			"distress":
				s["name"] = "Distress signal"
			"special":
				s["name"] = "Pirate stronghold"
			"nest":
				s["name"] = "The Rabble's Nest"
			"ooma":
				s["name"] = "Ooma's ship"
				s["store"] = "ooma"
			_:
				s["name"] = "Beacon"
		s["about"] = ABOUT[str(s["kind"])]
	for st in stops:
		if int(st["ring"]) >= 2 and str(st["kind"]) in ["beacon", "distress", "special"] and rng.randf() < HAZARD_CHANCE:
			st["hazard"] = ZONE_HAZARD[str(st["zone"])]
			st["about"] = str(st.get("about", "")) + " " + str(HAZARD_ABOUT[st["hazard"]])
	return stops


# Adds the stop an event revealed, one ring further out than `from` (or on it, at the edge), between its
# neighbours, linked to `from` and the two nearest stops on its ring. Returns its index.
static func add_hidden(stops: Array, from: int, reveal: String, rng: RandomNumberGenerator, max_ring := MAX_RING) -> int:
	var spec: Array = REVEALS.get(reveal.to_lower(), ["wreck", reveal.capitalize(), ""])
	var base_ring: int = int(stops[from]["ring"]) if from >= 0 else 0
	var ring: int = clampi(base_ring + 1, 1, max_ring)
	var base_angle: float = float(stops[from]["angle"]) if from >= 0 else rng.randf() * 360.0
	var spacing: float = 360.0 / float(ShipData.RING_STOPS[ring])
	var angle: float = fposmod(base_angle + spacing * 0.5 * (1.0 if rng.randf() < 0.5 else -1.0), 360.0)
	var z: String = zone_of(angle)
	var stop := {"kind": str(spec[0]), "ring": ring, "angle": angle, "links": [], "seen": false, "zone": z,
		"name": str(spec[1]), "hidden": true}
	stop["about"] = ABOUT.get(str(spec[0]), "")
	if str(spec[2]) != "":
		stop["store"] = str(spec[2])
	var i: int = stops.size()
	stops.append(stop)
	if from >= 0:
		_link(stops, from, i)
	var same: Array = []
	for k in range(i):
		if int(stops[k]["ring"]) == ring:
			same.append(k)
	same.sort_custom(func(a, b): return _gap(stops, i, a) < _gap(stops, i, b))
	for k in range(mini(2, same.size())):
		_link(stops, i, same[k])
	return i


# Eshu's contracts (23 Nov): each active contract turns a beacon in its zone, as near its ring as there is, into
# a "contract" stop: the wanted ship waits there.
static func place_contracts(stops: Array, contracts: Array, rng: RandomNumberGenerator) -> void:
	for c in contracts:
		var best := -1
		var best_gap := 99
		for i in stops.size():
			var st: Dictionary = stops[i]
			if str(st["kind"]) != "beacon" or str(st["zone"]) != str(c["zone"]):
				continue
			var gap: int = absi(int(st["ring"]) - int(c["ring"])) * 10 + rng.randi_range(0, 3)
			if gap < best_gap:
				best_gap = gap
				best = i
		if best < 0:
			continue
		var st2: Dictionary = stops[best]
		st2["kind"] = "contract"
		st2["enemy"] = str(c["enemy"])
		st2["contract"] = str(c["id"])
		st2["name"] = "Wanted: " + str(c["target_name"])
		st2["about"] = ("Eshu's contract: capture the %s with its hull in one piece. Down its crew." if str(c["kind"]) == "capture" \
				else "Eshu's bounty: the %s, destroyed or taken.") % str(c["target_name"]).to_lower()


static func _shuffle(a: Array, rng: RandomNumberGenerator) -> void:
	for i in range(a.size() - 1, 0, -1):
		var j: int = rng.randi() % (i + 1)
		var t = a[i]
		a[i] = a[j]
		a[j] = t


static func _gap(stops: Array, a: int, b: int) -> float:
	var d: float = absf(fposmod(float(stops[a]["angle"]) - float(stops[b]["angle"]) + 180.0, 360.0) - 180.0)
	return d


static func _link(stops: Array, a: int, b: int) -> void:
	if a == b:
		return
	if not (stops[a]["links"] as Array).has(b):
		stops[a]["links"].append(b)
	if not (stops[b]["links"] as Array).has(a):
		stops[b]["links"].append(a)


# A random event for this kind of stop, zone and ring that hasn't come up this run, or "".
static func pick_event(kind: String, zone: String, ring: int, used: Array, rng: RandomNumberGenerator) -> String:
	var pool: Array = []
	for id in SpaceEvents.EVENTS:
		var e: Dictionary = SpaceEvents.EVENTS[id]
		if bool(e.get("story", false)) or not e.has("kind") or used.has(id):
			continue
		if str(e["kind"]) != kind:
			continue
		var zones: Array = e.get("zones", ["any"])
		if not (zones.has("any") or zones.has(zone)):
			continue
		var rings: Array = e.get("rings", [1, 5])
		if ring < int(rings[0]) or ring > int(rings[1]):
			continue
		pool.append(id)
	if pool.is_empty():
		return ""
	return pool[rng.randi() % pool.size()]


# Who you fight at a beacon: half the time the zone's own ships (the Reach's are pirates anyway), otherwise Rabble
# raiders, in a cutter or someone else's repainted ship.
static func pick_enemy(zone: String, rng: RandomNumberGenerator) -> String:
	if rng.randf() < 0.5:
		var own: Array = ZONE_SHIPS[zone]
		return own[rng.randi() % own.size()]
	return RAIDERS[rng.randi() % RAIDERS.size()]


# What a won fight pays, as event effects (main.gd apply_space_effects): Scrip growing with the ring, a chance of
# fuel, missiles or a drone part, and the ship's salvage for the player (23 Nov, Zachary: "ships should also give
# loot for player like hull plating, rare resources. And rare pirate relics for musem."). Every item can turn up on
# every ring; the further out, the likelier the rare ones ("All rings should have a chance. But it increases the
# likelihood of rare loot further you go."). Chernobog ships (ids with "rabble", and the stronghold) can carry a pirate
# relic you haven't found yet; the stronghold always does while any are left. `found` lists the relic ids the
# player already has or has given to the museum.
# item: [chance on ring 1, added per ring further out, fewest, most]
const SALVAGE := {
	"hull_plate": [0.35, 0.05, 1, 1],
	"coil_wire": [0.30, 0.05, 1, 2],
	"circuit_board": [0.12, 0.06, 1, 1],
	"lithium_cell": [0.12, 0.05, 1, 2],
	"rare_earths": [0.06, 0.07, 1, 2],
	"helium_3": [0.04, 0.06, 1, 1],
	"cobalt_60": [0.02, 0.04, 1, 1],
	"void_sapphire": [0.01, 0.03, 1, 1],
}
const RELIC_CHANCE := [0.04, 0.05]          # a Chernobog ship carrying a relic: on ring 1, added per ring

static func salvage_chance(item: String, ring: int) -> float:
	var row: Array = SALVAGE[item]
	return float(row[0]) + float(row[1]) * (clampi(ring, 1, 5) - 1)


static func reward(ring: int, special: bool, rng: RandomNumberGenerator, enemy_id := "", found: Array = []) -> Array:
	var r: int = clampi(ring, 1, 5)
	var out: Array = ["+%d Scrip" % (20 + 15 * r + rng.randi_range(0, 15) + (80 if special else 0))]
	if rng.randf() < 0.4 or special:
		out.append("+1 fuel")
	if rng.randf() < 0.3 or special:
		out.append("+%d missiles" % rng.randi_range(1, 2))
	if rng.randf() < 0.25:
		out.append("+1 drone parts")
	# salvage: scrap every time, then each item on its own roll (the stronghold counts as two rings further out)
	out.append("item: scrap x%d" % rng.randi_range(2, 3 + r))
	var roll_ring: int = r + (2 if special else 0)
	for item in SALVAGE:
		var row: Array = SALVAGE[item]
		var guaranteed: bool = special and (item == "hull_plate" or item == "circuit_board")
		if guaranteed or rng.randf() < salvage_chance(item, roll_ring):
			var n: int = rng.randi_range(int(row[2]), int(row[3])) + (1 if special and item == "hull_plate" else 0)
			out.append("item: %s x%d" % [item, n])
	if special or enemy_id.contains("rabble"):
		var left: Array = []
		for id in ItemData.pirate_relics():
			if not found.has(id):
				left.append(id)
		var chance: float = float(RELIC_CHANCE[0]) + float(RELIC_CHANCE[1]) * (r - 1)
		if not left.is_empty() and (special or rng.randf() < chance):
			out.append("item: %s x1" % str(left[rng.randi() % left.size()]))
	return out
