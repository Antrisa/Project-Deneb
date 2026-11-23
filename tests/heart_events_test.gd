extends SceneTree
# Plays every heart event (scripts/heart_events.gd) from start to finish, the way F3 does in a debug build,
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
		if id == "evarra_10":
			assert(s.current_area == "east", "Evarra's 10 ends in the little park")
		if id == "ana_8":
			assert(s.sky_override == "", "the lounge's window goes back to the day's own sky after Ana's 8")
		if id == "ana_10":
			assert(s.player.visible, "you step back out of your ship after Ana's 10")
			assert(s.wreck_sprite.modulate.a == 1.0, "your ship is back on its pad after Ana's 10")
	assert(s.story_flags.get("freya_plans", false) and s.story_flags.get("freya_crew", false))
	assert(s.story_flags.get("perk_master_mechanic", false) and s.story_flags.get("keepsake_wrench_pendant", false))
	for f in ["jasper_butter_deposit", "perk_parisian_bistro_menu", "perk_sous_chefs_blessing", "keepsake_jasper_apron",
			"evarra_wildflowers", "perk_honey_lavender_brioche", "perk_green_thumb", "keepsake_pressed_flower_frame",
			"job_rig_quest", "perk_bedrock_strength", "keepsake_oar_charm",
			"perk_xeno_salve", "quill_clinic_door", "perk_guardian_medic", "keepsake_stethoscope_compass",
			"ixali_folded_titanium", "perk_star_knight_aegis", "perk_chivalric_guard", "keepsake_pauldron",
			"artie_troop_story", "artie_scouts", "perk_junior_scout_reports", "perk_thrifty", "keepsake_scoutmaster_badge",
			"stu_uniform", "stu_nameplate", "perk_five_star_partner", "keepsake_silver_bell",
			"ana_soup", "ana_seat", "ana_corridors", "ana_compass", "perk_wingmate", "ana_true_north_console",
			"keepsake_flight_jacket"]:
		assert(s.story_flags.get(f, false), f)
	# F3 makes you the partner for each 10, so the last one's resident is your partner at the end (and the 8s
	# after the first 10 play their friendship endings)
	assert(s.partner == "Ana")
	print("PASS: ", HeartEvents.ORDER.size(), " heart events played to the end, choices picked, flags set.")
	quit()
