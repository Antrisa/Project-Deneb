extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var s=load("res://main.tscn").instantiate()
	root.add_child(s)
	await process_frame
	s.set_process(false)
	s.player.set_physics_process(false)
	s.creator.open=false;s.creator.visible=false
	s._go_to("main",Vector2i(115,100),false)
	var f=s.actors.get_node("LayeredFountain")
	assert(f.y_sort_enabled and f.get_child_count()==4)
	assert(s.solid_at(Vector2(1848,1528)))
	for moment in [875,970]:
		s.minutes=moment;s._snap_residents()
		var active:=0
		for r in s.residents:
			if r.area=="main" and r._act in ["garden","chess","hologame","observe","read","restock"]:
				assert(r._settled)
				r._idle(0.1)
				assert(r.activity_pose!=null)
				if r._act in ["chess","hologame"]:
					assert(r.self_modulate.a==0)
					r._unsettle()
					assert(r.self_modulate.a==1)
				active+=1
		assert(active>=4)
	var gardens=s.things.filter(func(t):return t.kind=="garden")
	assert(gardens.size()>0)
	await s._water_garden(gardens[0])
	assert(s.garden_watered_day==s.day and not s.garden_busy)
	await s._water_garden(gardens[0])
	assert(not s.garden_busy)
	var g=s.community_game
	g.start()
	g.cells.assign([1,1,0,0,2,0,0,0,0])
	g._move(6)
	assert(g.cells[2]==2) # AI blocks immediate win.
	g.cells.assign([2,2,0,1,1,0,0,0,0])
	g._move(8)
	assert(g.winner(g.cells)==2) # AI takes win before blocking.
	g.hide_game();assert(not g.open)
	print("PASS: layered fountain collision, social schedules and poses, daily watering, table-game blocking and wins.")
	for n in s.find_children("*","AudioStreamPlayer",true,false):n.stop();n.stream=null
	await create_timer(1).timeout
	s.queue_free();await process_frame
	quit()
