extends SceneTree

var summons := 0
var dismissals := 0

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var actor = load("res://sara/sara_hologram.tscn").instantiate()
	actor.automatic_idle = false
	root.add_child(actor)
	actor.set_process(false)
	actor.hologram_summoned.connect(func(_name): summons += 1)
	actor.hologram_dismissed.connect(func(_name): dismissals += 1)
	assert(actor.animation_names().size() == 33)
	for name in actor.animation_names():
		assert(actor.play(name))
		var clip: Dictionary = actor.clips[name]
		assert(actor.body.texture.get_width() == 80 * 24)
		assert(actor.objects.texture.get_width() == 128 * 24)
		for frame in range(25):
			actor._process(1.0 / float(clip.fps) + 0.00001)
			assert(actor.body.frame >= 0 and actor.body.frame < 24)
		if name == "dissolve":
			assert(actor.current_clip == "")
		elif not clip.loop:
			assert(actor.current_clip == "idle")
	assert(summons == 8 and dismissals == 8)
	print("PASS: 33 clips, frame sizes, transitions, and 8 paired object events")
	actor.queue_free()
	quit()
