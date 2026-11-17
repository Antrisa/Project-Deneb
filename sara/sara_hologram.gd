extends Node2D
## Self-contained front-facing S.A.R.A. projection. Root origin is projector center.
signal clip_finished(clip_name: String)
signal hologram_summoned(object_name: String)
signal hologram_dismissed(object_name: String)

@export var automatic_idle: bool = true
@export var show_projector: bool = true
@export var art_scale: float = 0.5

const ROOT := "res://sara/"
var clips: Dictionary = {}
var current_clip: String = ""
var elapsed: float = 0.0
var frame_index: int = 0
var idle_delay: float = 5.0
var object_active: bool = false
var body := Sprite2D.new()
var objects := Sprite2D.new()
var projector := Sprite2D.new()
var visuals := Node2D.new()

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(visuals)
	visuals.scale = Vector2.ONE * art_scale
	projector.texture = load("res://art/lunar/holo_dais.png")
	projector.position.y = -26
	projector.visible = show_projector
	visuals.add_child(projector)
	visuals.add_child(body)
	visuals.add_child(objects)
	body.position = Vector2(0, -48)
	objects.position = body.position
	body.hframes = 24
	objects.hframes = 24
	var parsed: Variant = preload("res://sara/animations_data.gd").DATA
	if not parsed is Dictionary:
		push_error("Missing SARA animation manifest")
		return
	for entry: Dictionary in parsed["animations"]:
		clips[entry["name"]] = entry
	play("idle")

func play(clip_name: String) -> bool:
	if not clips.has(clip_name):
		push_warning("Unknown SARA animation: " + clip_name)
		return false
	if object_active:
		hologram_dismissed.emit(str(clips[current_clip]["prop"]))
	object_active = false
	current_clip = clip_name
	elapsed = 0.0
	frame_index = 0
	var entry: Dictionary = clips[clip_name]
	body.texture = load(ROOT + str(entry["body"]))
	objects.texture = load(ROOT + str(entry["objects"]))
	body.frame = 0
	objects.frame = 0
	return true

func animation_names() -> Array:
	return clips.keys()

func _process(delta: float) -> void:
	if current_clip.is_empty():
		return
	var entry: Dictionary = clips[current_clip]
	elapsed += delta
	var next_frame := int(elapsed * float(entry["fps"]))
	var count := int(entry["frames"])
	if next_frame >= count:
		if bool(entry["loop"]):
			elapsed = fmod(elapsed, float(count) / float(entry["fps"]))
			next_frame %= count
		else:
			var finished := current_clip
			if object_active:
				hologram_dismissed.emit(str(entry["prop"]))
				object_active = false
			if finished == "dissolve":
				body.frame = count - 1
				objects.frame = count - 1
				current_clip = ""
			else:
				play("idle")
			clip_finished.emit(finished)
			return
	frame_index = next_frame
	body.frame = frame_index
	objects.frame = frame_index
	if entry["prop"] != null and frame_index >= 4 and frame_index < count - 4 and not object_active:
		object_active = true
		hologram_summoned.emit(str(entry["prop"]))
	elif object_active and frame_index >= count - 4:
		object_active = false
		hologram_dismissed.emit(str(entry["prop"]))
	if automatic_idle and current_clip == "idle":
		idle_delay -= delta
		if idle_delay <= 0.0:
			idle_delay = randf_range(5.0, 10.0)
			play(["blink", "glance_left", "glance_right", "head_tilt", "clasp_hands"].pick_random())
