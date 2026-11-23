extends SceneTree
# Plays every heart event (scripts/heart_events.gd) from start to finish, the way F4 does in a debug build,
# picking the first answer at every choice and clicking through every line. Checks that each one ends, is
# remembered, gives its flags and puts everyone back on their schedule.
#   godot --headless --script res://tests/heart_events_test.gd

const HeartEvents = preload("res://scripts/heart_events.gd")


func _initialize() -> void:
	call_deferred("run")


func run() -> void:
	var s = load("res://main.tscn").instantiate()
	root.add_child(s)
	await process_frame
	if s.creator != null:
		s.creator.open = false
		s.creator.visible = false
	if s.title != null:
		s.title.open = false
	s.flights = 1
	s.artie_found_day = 1
	s.ana_found_day = 1
	s.day = 10
	for id in HeartEvents.ORDER:
		s._debug_next_heart_event()
		await process_frame
		assert(s.cutscene.running, id + " started")
		var started := Time.get_ticks_msec()
		while s.cutscene.running and Time.get_ticks_msec() - started < 120000:
			if s.cutscene._choosing:
				s.cutscene._pick(0)
			elif s.dialogue.active:
				s.dialogue.advance()      # finish typing the line
				s.dialogue.advance()      # and go on to the next
			await process_frame
		assert(not s.cutscene.running, id + " finished")
		assert(s.events_seen.has(id), id + " remembered")
		for r in s.residents:
			assert(not r.in_scene, id + ": " + r.who + " is back on their schedule")
		assert(not s.player.scene_walking)
	assert(s.story_flags.get("freya_plans", false) and s.story_flags.get("freya_crew", false))
	assert(s.story_flags.get("perk_master_mechanic", false) and s.story_flags.get("keepsake_wrench_pendant", false))
	assert(s.partner == "Freya")
	print("PASS: ", HeartEvents.ORDER.size(), " heart events played to the end, choices picked, flags set.")
	quit()
