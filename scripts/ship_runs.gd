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
#   special  - the pirate stronghold (a hard fight; the Nest raid and Ooma's ship come later)
# Events come from SpaceEvents.EVENTS (the ones with "kind", "zones" and "rings", not "story"); none repeats in a
# run. Fights draw the zone's own ships or Rabble raiders (a cutter or a repainted culture ship).

const SpaceEvents = preload("res://scripts/space_events.gd")
const ItemData = preload("res://scripts/item_data.gd")

const MAX_RING := 3                          # rings open on a run for now
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
static func make_run(day: int, ring_stops: Array) -> Array:
	var rng := RandomNumberGenerator.new()
	rng.seed = 7919 * day + 17
	var stops: Array = []
	var by_ring: Array = [[]]
	for ring in range(1, MAX_RING + 1):
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
	for ring in range(1, MAX_RING + 1):
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
	for i in by_ring[MAX_RING]:
		if zone_of(float(stops[i]["angle"])) == "Reach" and str(stops[i]["kind"]) == "beacon":
			reach.append(i)
	if reach.size() > 0:
		stops[reach[rng.randi() % reach.size()]]["kind"] = "special"
	# links: neighbours on the same ring, and the nearest one or two on the next ring out
	for ring in range(1, MAX_RING + 1):
		var here: Array = by_ring[ring]
		var ordered: Array = here.duplicate()
		ordered.sort_custom(func(a, b): return float(stops[a]["angle"]) < float(stops[b]["angle"]))
		for k in range(ordered.size()):
			_link(stops, ordered[k], ordered[(k + 1) % ordered.size()])
		if ring < MAX_RING:
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
			"distress":
				s["name"] = "Distress signal"
			"special":
				s["name"] = "Pirate stronghold"
			_:
				s["name"] = "Beacon"
		s["about"] = ABOUT[str(s["kind"])]
	return stops


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
# loot for player like hull plating, rare resources. And rare pirate relics for musem."): scrap every time, hull
# plate and wire often, rarer things further out. Rabble ships (ids with "rabble", and the stronghold) can carry a
# pirate relic you haven't found yet; the stronghold always does while any are left. `found` lists the relic ids
# the player already has or has given to the museum.
const RELIC_CHANCE := [0.0, 0.08, 0.12, 0.16, 0.2, 0.24]     # a Rabble ship carrying a relic, by ring

static func reward(ring: int, special: bool, rng: RandomNumberGenerator, enemy_id := "", found: Array = []) -> Array:
	var r: int = clampi(ring, 1, 5)
	var out: Array = ["+%d Scrip" % (20 + 15 * r + rng.randi_range(0, 15) + (80 if special else 0))]
	if rng.randf() < 0.4 or special:
		out.append("+1 fuel")
	if rng.randf() < 0.3 or special:
		out.append("+%d missiles" % rng.randi_range(1, 2))
	if rng.randf() < 0.25:
		out.append("+1 drone parts")
	# salvage
	out.append("item: scrap x%d" % rng.randi_range(2, 3 + r))
	if special:
		out.append("item: hull_plate x2")
	elif rng.randf() < 0.35:
		out.append("item: hull_plate x1")
	if rng.randf() < 0.3:
		out.append("item: coil_wire x%d" % rng.randi_range(1, 2))
	if rng.randf() < 0.1 + 0.05 * r or special:
		out.append("item: circuit_board x1")
	if rng.randf() < 0.15:
		out.append("item: lithium_cell x1")
	if r >= 2 and rng.randf() < 0.2:
		out.append("item: rare_earths x%d" % rng.randi_range(1, 2))
	if r >= 2 and rng.randf() < 0.08 * r:
		out.append("item: helium_3 x1")
	if r >= 3 and rng.randf() < 0.1:
		out.append("item: cobalt_60 x1")
	if rng.randf() < (0.5 if special else 0.04):
		out.append("item: void_sapphire x1")
	if special or enemy_id.contains("rabble"):
		var left: Array = []
		for id in ItemData.pirate_relics():
			if not found.has(id):
				left.append(id)
		if not left.is_empty() and (special or rng.randf() < float(RELIC_CHANCE[r])):
			out.append("item: %s x1" % str(left[rng.randi() % left.size()]))
	return out
