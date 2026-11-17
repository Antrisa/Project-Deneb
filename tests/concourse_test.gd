extends SceneTree
const Map = preload("res://scripts/map_data.gd")
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	assert(Map.CONCOURSE_FRONTS.size()==18)
	var scene = load("res://main.tscn").instantiate()
	root.add_child(scene)
	await process_frame
	scene.set_process(false)
	scene.player.set_physics_process(false)
	if scene.creator != null: scene.creator.open=false; scene.creator.visible=false
	scene.appearance=scene.maker.defaults()
	scene.player.set_sheet(scene.maker.sheet(scene.appearance))
	for p in Map.CONCOURSE_PROPS:
		assert(p[0] != "board") # Attached to fountain, never a second freestanding object.
	var seats: Array = scene.things.filter(func(t): return t.kind=="seat" and t.area=="main")
	assert(seats.size()==25)
	for t in seats:
		scene._go_to("main",Vector2i(115,108),false)
		var start: Vector2 = scene.player.position
		scene._interact(t)
		assert(scene.seated and scene.player.sitting)
		assert(scene.player._dir == (1 if "[N]" in t.name else 3 if "[E]" in t.name or "left" in t.name else 2 if "[W]" in t.name or "right" in t.name else 0))
		scene._stand_from_seat()
		assert(scene.player.position==start and not scene.player.sitting)
	var visits:=0
	for t in scene.things:
		if t.kind!="portal" or t.area!="main":continue
		var e: Array = t.entry
		scene._go_to("main",Vector2i(e[1],e[2]+2),false)
		var key: String=t.key
		scene.set_door_locked("main",Vector2i(e[1],e[2]),true)
		await scene._enter_portal(t)
		assert(scene.current_area=="main" and not scene.travelling)
		assert(scene.portals[key].opening==0)
		scene.set_door_locked("main",Vector2i(e[1],e[2]),false)
		assert(scene.solid_at(t.pos))
		await scene._enter_portal(t)
		assert(scene.current_area==e[3] and not scene.travelling)
		assert(scene.portals[key].opening==0)
		visits+=1
	assert(visits==18)
	for t in scene.things:
		if t.kind == "portal" and t.area in ["top","eng"]:
			scene._go_to(t.area,Vector2i(t.entry[1],t.entry[2]+2),false)
			await scene._enter_portal(t)
			assert(scene.current_area=="main" and not scene.travelling)
	print("PASS: 18 animated portals, locks reject entry, two lift rides, 25 seats and return poses.")
	for n in scene.find_children("*","AudioStreamPlayer",true,false):n.stop();n.stream=null
	await create_timer(1.0).timeout
	scene.queue_free()
	await process_frame
	quit()
