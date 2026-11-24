extends SceneTree
# Plays your first morning, then every heart event (scripts/heart_events.gd), from start to finish, the way F3 does in a debug build,
# picking the first answer at every choice and clicking through every line. Checks that each one ends, is
# remembered, gives its flags and puts everyone back on their schedule; then that their letters come.
#   godot --headless --script res://tests/heart_events_test.gd

const HeartEvents = preload("res://scripts/heart_events.gd")
const BridgeScript = preload("res://scripts/datapad_bridge.gd")
const MailData = preload("res://scripts/mail_data.gd")


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
	# Your first morning (HeartEvents.SCENES "welcome"): stepping out of your front door plays it, once.
	s.welcomed = false
	s._go_to("agri", Vector2i(59, 57), false)
	for i in 30:
		if s.cutscene.running:
			break
		await process_frame
	assert(s.cutscene.running, "your first morning starts when you step outside")
	await _click_through(s)
	assert(not s.cutscene.running, "your first morning finished")
	assert(s.welcomed)
	assert(s._count("hoe") >= 1 and s._count("watering_can") >= 1 and s._count("hydro_bed") >= 2, "Bram's tools and beds")
	assert(s._count("crater_potato_seeds") >= 15 and s._count("moon_wheat_seeds") >= 10, "Jasper's seeds")
	assert(s.persons["Bram"]["met"] and s.persons["Jasper"]["met"], "you've met them now")
	for r in s.residents:
		assert(not r.in_scene, "welcome: " + r.who + " is back on their schedule")
	s._go_to("aptPlayer", Vector2i(14, 23), false)
	await process_frame
	s._go_to("agri", Vector2i(59, 57), false)
	await process_frame
	await process_frame
	assert(not s.cutscene.running, "your first morning plays only once")

	s.flights = 1
	s.artie_found_day = 1
	s.ana_found_day = 1
	s.day = 10
	for id in HeartEvents.ORDER:
		s._debug_next_heart_event()
		await process_frame
		assert(s.cutscene.running, id + " started")
		await _click_through(s)
		assert(not s.cutscene.running, id + " finished")
		assert(s.events_seen.has(id), id + " remembered")
		for r in s.residents:
			assert(not r.in_scene, id + ": " + r.who + " is back on their schedule")
		assert(not s.player.scene_walking)
		assert(s.cutscene._fx.is_empty(), id + ": its bees, fireflies, steam, spray and bubbles are gone")
		assert(s.cutscene._holo == null, id + ": S.A.R.A.'s portable projection is gone")
		if id == "evarra_10":
			assert(s.current_area == "east", "Evarra's 10 ends in the little park")
		if id == "ana_8":
			assert(s.sky_override == "", "the lounge's window goes back to the day's own sky after Ana's 8")
		if id == "siblings_10":
			assert(["Autumn", "Winter"].has(str(BridgeScript.season_date(s.day)[0])), "the siblings' banquet is in autumn or winter")
		if id == "zaas_6":
			assert(s.leviathan_slain, "Zaas's 6 is at the lake, so F3 kills the Leviathan first")
		if id == "vzzket_8":
			assert(s._count("vzzket_first_spear") == 1, "Vzz'ket gives you his first spear")
		if id == "rusk_8":
			assert(s._count("nebula_grape_seeds") >= 3, "Rusk gives you seeds of Ilsa's vine")
		if id == "nightwatch_8":
			assert(s.current_area == "bar", "the side arc's 8 ends in the bar, under the new sign")
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
			"keepsake_flight_jacket",
			"siblings_pod_story", "perk_wildflower_honey", "siblings_bees", "perk_starlight_souffle",
			"perk_family_table", "keepsake_family_photo", "siblings_feast",
			"sara_lost_property", "sara_concierge", "sara_emitter", "sara_rest", "perk_concierge", "sara_night_shift",
			"tarbesh_astrolabe", "tarbesh_assignment", "tarbesh_summons", "tarbesh_plaque", "perk_relic_appraisal",
			"zaas_helmet", "zaas_heartbeat", "merrow_deep", "zaas_captain", "perk_deep_sea_sonar_lure",
			"vzzket_wall", "vzzket_blessing", "vzzket_clutch_brother", "vzzket_sensors", "perk_monster_radar",
			"rusk_lights", "rusk_tail", "rusk_sea_chest", "rusk_first_page",
			"vzzket_tall_tales", "vzzket_shell", "vzzket_open_mic", "vzzket_sentinels", "perk_chitin_piercer_traps",
			"bram_night_pod", "bram_quiet_credit", "bram_long_column", "bram_told", "bram_paid_in_full", "perk_moogli_trade_beacon",
			"tikka_manifold", "tikka_freya_helps", "tikka_day_off", "tikka_sundays_off", "perk_smelter_overclock",
			"sesska_jacket", "sesska_landing_pattern", "sesska_cavern_silk", "sesska_void_silk", "perk_void_silk_linens",
			"forty_workwear", "forty_anniversary"]:
		assert(s.story_flags.get(f, false), f)
	# F3 makes you the partner for each 10, so the last one's resident is your partner at the end (and the 8s
	# after the first 10 play their friendship endings)
	assert(s.partner == "Ana")
	# Letters (scripts/mail_data.gd): the events sent theirs (the first choice always sends, even in Job's 4 and
	# Tar'Besh's 4), and they come with the next morning's post. A letter's gift goes in your pack once.
	for id in MailData.LETTERS:
		if id != "welcome" and id != "vzzket_caverns":
			assert(s.mail_due.has(id), id + " was sent by its heart event")
	var morning: int = s.day
	for id in s.mail_due:
		morning = maxi(morning, int(s.mail_due[id]))
	s.day = morning
	s._deliver_mail()
	for id in ["freya_pump", "jasper_wheat", "zaas_hydrophones", "quill_spores", "tarbesh_letter", "rusk_ilsa_vine"]:
		assert(s.mail_waiting.has(id), id + " came with the post")
	var medpacks: int = s._count("medpack")
	s.read_letter("quill_spores")
	assert(s._count("medpack") == medpacks + 2, "Quill's letter has two medpacks in it")
	assert(not s.mail_waiting.has("quill_spores"), "and now it's read")
	s.read_letter("quill_spores")
	assert(s._count("medpack") == medpacks + 2, "a letter's gift only comes the first time you open it")
	print("PASS: your first morning, and ", HeartEvents.ORDER.size(), " heart events played to the end, choices picked, flags set, letters sent.")
	quit()


# Click through a scene: the first answer at every choice, every line typed out and then moved on from.
func _click_through(s) -> void:
	var started := Time.get_ticks_msec()
	while s.cutscene.running and Time.get_ticks_msec() - started < 120000:
		if s.cutscene._choosing:
			s.cutscene._pick(0)
		elif s.dialogue.active:
			s.dialogue.advance()      # finish typing the line
			s.dialogue.advance()      # and go on to the next
		await process_frame
