extends SceneTree

const Walk = preload("res://scripts/walk_cycle.gd")
const Player = preload("res://scripts/player.gd")
const Resident = preload("res://scripts/resident.gd")
const MapData = preload("res://scripts/map_data.gd")
const Npcs = preload("res://scripts/npc_data.gd")

class WalkWorld extends Node2D:
	var wall := false
	var footsteps := 0
	var blocked := {"test": {}}
	var warps := {"test": {}}
	var current_area := "test"

	func solid_at(_point: Vector2) -> bool:
		return wall

	func sfx(effect: String, _pitch: float, _volume: float) -> void:
		if effect == "step":
			footsteps += 1

	func player_overlaps_tile(_area: String, _tile: Vector2i) -> bool:
		return false

var errors: Array[String] = []


func check(ok: bool, message: String) -> void:
	if not ok:
		errors.append(message)


func _initialize() -> void:
	call_deferred("run")


func run() -> void:
	var world := WalkWorld.new()
	root.add_child(world)
	var player := Player.new()
	player.world = world
	world.add_child(player)
	player.set_process(false)
	var actions := ["move_down", "move_up", "move_left", "move_right"]
	for action in actions:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
	for d in 4:
		Input.action_press(actions[d])
		player._process(0.01)
		check(player._sprite.frame_coords == Vector2i(d, 1), "First contact in direction %s" % d)
		for expected in [3, 2, 4, 1]:
			player._process(Walk.UNITS_PER_PHASE / Player.SPEED)
			check(player._sprite.frame_coords == Vector2i(d, expected), "Player direction %d, row %d" % [d, expected])
		Input.action_release(actions[d])
		player._process(0.01)
		check(player._sprite.frame_coords == Vector2i(d, 0), "Standing on release")
	check(world.footsteps == 12, "A sound only when a foot lands")
	world.wall = true
	var before := player.position
	Input.action_press("move_right")
	player._process(0.2)
	check(world.footsteps == 12 and player.position == before and player._sprite.frame_coords == Vector2i(3, 0), "No stride or step against a solid wall")
	world.wall = false
	player.set_carrying(true)
	player._process(0.01)
	player._process(Walk.UNITS_PER_PHASE / Player.CARRY_SPEED)
	check(player._sprite.frame_coords.y == 3, "Carrying follows actual distance")
	player.frozen = true
	player._process(0.1)
	check(player._sprite.frame_coords.y == 0, "Frozen during dialogue")
	Input.action_release("move_right")

	var scheduled := MapData.SCHEDULES.size()
	for who in MapData.SCHEDULES:
		var path := "res://art/npc_%s.png" % Npcs.PEOPLE[who].id
		var tex := load(path) as Texture2D
		check(tex != null and tex.get_size() == Vector2(96, 240), who + " has a native, independent walk")
		if tex == null:
			continue
		var activity_path := "res://art/npc_%s_act.png" % Npcs.PEOPLE[who].id
		var sheet := load(activity_path) as Texture2D
		var labels: Array = MapData.ACTION_ROWS[who]
		check(sheet != null and sheet.get_width() == 144 and sheet.get_height() % 48 == 0 and sheet.get_height() >= labels.size() * 48, who + " has a complete activity sheet")
		var eats := false
		var works := false
		for stop in MapData.SCHEDULES[who]:
			var row: int = stop[7]
			if row < 0 or row >= labels.size():
				continue
			var pose := str(labels[row]).get_slice(" ", 0)
			eats = eats or (stop[6] == "eat" and pose == "eat")
			works = works or stop[6] == "work" or pose in ["restock", "guard"]
		check(eats and works, "%s has a playable meal and occupation on the regular route" % who)
		var stops: Array = MapData.SCHEDULES[who] + MapData.SCHEDULES_ALT.get(who, [])
		for stop in stops:
			var row := int(stop[7])
			check(row >= 0 and row < labels.size() and str(labels[row]).ends_with(" " + str(stop[5])), "%s has a matching pose at %s" % [who, stop[1]])
		if sheet != null:
			var art := sheet.get_image()
			for row in labels.size():
				var poses: Array = []
				for f in 4:
					var cell := art.get_region(Rect2i(f * 36, row * 48, 36, 48))
					var pixels := cell.get_data()
					if cell.get_used_rect().has_area() and not poses.has(pixels):
						poses.append(pixels)
				check(poses.size() == 4, "%s %s needs four distinct activity frames" % [who, labels[row]])
		var img := tex.get_image()
		for d in 4:
			var drawings: Array = []
			for row in Walk.POSES:
				var pixels := img.get_region(Rect2i(d * 24, row * 48, 24, 48)).get_data()
				if not drawings.has(pixels):
					drawings.append(pixels)
			check(drawings.size() == 4, "%s direction %d needs four walk drawings" % [who, d])

	var resident := Resident.new()
	var entry := [[0, "test", 3, 0, 26, "r", "work", 0]]
	var freya: Texture2D = load("res://art/npc_freya.png")
	var activity: Texture2D = load("res://art/npc_freya_act.png")
	resident.setup(world, "Freya", freya, entry, {}, activity)
	world.add_child(resident)
	resident.area = "test"
	resident._entry = 0
	resident._target_area = "test"
	resident._target_tile = Vector2i(3, 0)
	resident.position = resident._spot(Vector2i.ZERO)
	resident._path = [Vector2i(1, 0), Vector2i(2, 0), Vector2i(3, 0)]
	resident._move(0.01)
	check(resident.frame_coords == Vector2i(3, 1), "NPC contact")
	# Move in small steps, as in the game, so each tile transition remains part of the stride.
	var seen: Array = [resident.frame_coords.y]
	while not resident._path.is_empty():
		resident._move(1.0 / 60.0)
		if resident.frame_coords.y != seen.back():
			seen.append(resident.frame_coords.y)
	check(seen.slice(0, 5) == [1, 3, 2, 4, 1], "NPC gait across adjacent tiles")
	resident._move(0.01)
	resident._idle(0.1)
	check(resident.texture == activity and resident.vframes == int(activity.get_height() / 48), "Action rows after arrival")
	resident._unsettle()
	check(resident.texture == freya and resident.vframes == 5 and resident.offset == Vector2(-12, -48), "Activity back to full native walk")
	resident._act = "chess"
	resident._idle(0.1)
	check(resident.vframes == 5 and resident.frame_coords.y == 0, "Seated activity uses a single standing cell")

	var legacy: Texture2D = load("res://art/npc_sara.png")
	check(Walk.rows(legacy) == 3, "Three-row legacy sheet")
	for phase in 4:
		check(Walk.pose(phase, 3) == [1, 0, 2, 0][phase], "Legacy row order")
	player.set_sheet(legacy)
	check(player._sprite.vframes == 3, "Player accepts legacy sheets")
	world.free()
	for message in errors:
		push_error(message)
	if errors.is_empty():
		print("PASS: %d scheduled resident sheets, player and resident gait, contacts, collision, carrying, activities and legacy sheets." % scheduled)
	quit(0 if errors.is_empty() else 1)
