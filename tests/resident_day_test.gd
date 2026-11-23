extends SceneTree

const MapData = preload("res://scripts/map_data.gd")
const STEP := 0.12
const ALL_PHASES := 0b1111


func _initialize() -> void:
	call_deferred("run")


func run() -> void:
	var station = load("res://main.tscn").instantiate()
	root.add_child(station)
	await process_frame
	station.set_process(false)
	station.player.set_process(false)

	# Wednesday after both rescues brings Ooma, Artie, Stu, Eshu and Ana onto their regular schedules.
	station.artie_found_day = 1
	station.ana_found_day = 1
	station.day = 10
	station.minutes = 361
	station._snap_residents()
	station._go_to("agri", Vector2i(44, 19), false)

	var walks := {}
	var meals := {}
	var occupations := {}
	while station.minutes < 23 * 60:
		for resident in station.residents:
			resident.tick(STEP, station.minutes)
			var who: String = resident.who
			if not resident._settled:
				var pose: int = resident.frame_coords.y
				if resident.texture == resident._walk_tex and pose > 0:
					walks[who] = walks.get(who, 0) | (1 << (pose - 1))
				continue
			var row: int = resident._act_row
			if row < 0:
				continue
			var phase: int
			if resident.texture == resident._act_tex:
				phase = resident.frame_coords.x
			else:
				resident.activity_pose._process(STEP)
				if not resident.activity_pose.visible or not resident.activity_pose.has_painted_pose() or resident.self_modulate.a > 0:
					continue
				phase = int(resident._idle_time * 3.0) % 4
			var action: String = MapData.ACTION_ROWS[who][row].get_slice(" ", 0)
			if resident._act == "eat" and action == "eat":
				meals[who] = meals.get(who, 0) | (1 << phase)
			if resident._act == "work" or action in ["restock", "guard"]:
				occupations[who] = occupations.get(who, 0) | (1 << phase)
		station.minutes += STEP / station.SECONDS_PER_GAME_MINUTE

	var failed := false
	for who in MapData.SCHEDULES:
		if walks.get(who, 0) != ALL_PHASES or meals.get(who, 0) != ALL_PHASES or occupations.get(who, 0) != ALL_PHASES:
			failed = true
			push_error("%s missing phases. Walk %s, meal %s, occupation %s." % [who, walks.get(who, 0), meals.get(who, 0), occupations.get(who, 0)])
	if not failed:
		print("PASS: all ", MapData.SCHEDULES.size(), " residents walked between stops, ate and worked or studied through all four animation phases on a regular visiting day.")
	for audio in station.find_children("*", "AudioStreamPlayer", true, false):
		audio.stop()
		audio.stream = null
	await create_timer(1).timeout
	station.queue_free()
	await process_frame
	quit(1 if failed else 0)
