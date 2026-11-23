extends Node
# Heart-event cutscenes (22 Nov 2026). Plays an event from scripts/heart_events.gd, Stardew-style:
#   - residents step out of their schedules: placed, walked, turned, posed (their heart-event sheet,
#     art/npc_<id>_event.png, or a row of their action sheet) and given emote bubbles;
#   - the player is walked and turned too;
#   - lines go through the dialogue box with portraits; choices come up in a small menu;
#   - the screen fades and shakes; the scene sets flags, friendship, perks, keepsakes and your partner.
# main.gd starts it (play()), stops the clock and the residents' schedules while it runs (paused), sends it
# the keys (handle_input, handle_click), and puts everyone back where their day says when it ends.
#
# Steps are arrays, the name first. "player" is the player; any other name is a resident.
#   ["say", who, [lines], label]      lines with [happy]-style portrait tags; who "" is narration; label
#                                      (optional) is shown instead of the name, e.g. "Tikka (comms)"
#   ["place", who, x, y, dir]          dir "d", "u", "l", "r"
#   ["met", who]                       you've now met them (a scene that introduces someone)
#   ["go", area, x, y, dir]            the scene moves to another map: the player goes to that tile (fade first;
#                                      place the cast there after it)
#   ["walk", who, x, y]                walks there and waits; ["walks", [[who, x, y], ...]] walks several at once
#   ["face", who, dir_or_name]         a direction, or another person's name to turn toward them
#   ["pose", who, pose]                "talk" "laugh" "sad" "jump" "gift" "bench" "wave", or an action row like
#                                      "hammer u"; "" stands them back up
#   ["emote", who, id]                 surprise, question, love, joy, sad, frustrated, hello, ready, no, wait...
#   ["wait", seconds]  ["fade", alpha, seconds]  ["shake", seconds, pixels]  ["sfx", name]  ["clock", minutes]
#   ["choose", [{"text": ..., "friendship": points, "steps": [...]}, ...]]   friendship goes to the event's resident
#   ["if", {condition}, [then steps], [else steps]]   conditions: {"flag": f}, {"not_flag": f}, {"arrived": who},
#                                      {"partner": who}, {"dating_other": who}
#   ["flag", name]  ["friendship", who, points]  ["perk", id, toast]  ["keepsake", id, toast]
#   ["partner", who]  ["toast", text]
#   ["hide", who]  ["show", who]        out of sight and back (boarding your ship); everyone shows again at the end
#   ["ship", "lift" or "land", seconds] your ship in the Shuttle Bay rises out through the launch doors and fades,
#                                      or comes back down onto its pad; it's back on the pad when the scene ends
#   ["sky", event]                     the Observation Lounge's window shows that sky event ("meteors", "aurora",
#                                      "comet"...; scripts/lounge_sky.gd) until the scene ends
#   ["energy", -points]                a small cost for a wrong choice (a bee sting): takes that much energy
#   ["fx", kind, x, y, spread]         bees, fireflies, steam or heartbeats drawn round that tile (scripts/scene_fx.gd); the
#                                      same kind again moves it there (bees settling on a hand); all gone when the scene ends
#   ["sara", clip]                     S.A.R.A. plays one of her hologram clips (sara/animations_data.gd: greeting, laugh,
#                                      glitch_hand, standby, wake...): her portable projection if the scene placed one,
#                                      else her pad in this area. "emote" and "say" work for "Sara" too.
#   ["sara", "place", x, y]            her portable projection (her 6 onwards) materializes on that tile, and her pad here
#                                      hides; after a "go", place it again. Gone, and her pads back, when the scene ends.
# Events can also need a second resident at the same hearts ("with": ["Evarra"]) and play only in some
# seasons ("seasons": ["Autumn", "Winter"]): main.gd _event_ready.

const HeartEvents = preload("res://scripts/heart_events.gd")
const SceneFx = preload("res://scripts/scene_fx.gd")
const NineFrame = preload("res://scripts/nine_frame.gd")
const DIRS := {"d": 0, "u": 1, "l": 2, "r": 3}

signal _dialogue_done
signal _walk_done
signal _choice_made(index: int)
signal finished(id: String)

var world                       # main.gd
var running := false
var event_id := ""
var event: Dictionary = {}

var _actors := {}               # who -> resident node taken over by this scene
var _walkers: Array = []        # [who, node, waypoints (player only)]
var _fade_layer: CanvasLayer
var _fade: ColorRect
var _choice_layer: CanvasLayer
var _choice_panel: Control
var _choice_labels: Array = []
var _choices: Array = []
var _choice_at := 0
var _choosing := false
var _shake_time := 0.0
var _shake_px := 0.0
var _ship_home := Vector2.INF   # where your ship stands on its pad, while a scene flies it
const SHIP_RISE := 220.0        # how far up the ship climbs before it's gone through the launch doors
var _fx := {}                   # kind -> the scene's effect node (scripts/scene_fx.gd)
var _holo = null                # S.A.R.A.'s portable projection in this scene ("sara", "place")


func _ready() -> void:
	# The fade sits under the dialogue box (layer 10), so lines can be read over a dark screen.
	_fade_layer = CanvasLayer.new()
	_fade_layer.layer = 9
	add_child(_fade_layer)
	_fade = ColorRect.new()
	_fade.color = Color(0.03, 0.04, 0.08, 0.0)
	_fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_layer.add_child(_fade)
	# The choice menu: laid out for 320x180 like the dialogue box, above it.
	_choice_layer = CanvasLayer.new()
	_choice_layer.layer = 11
	_choice_layer.scale = Vector2(2, 2)
	_choice_layer.visible = false
	add_child(_choice_layer)
	var box = NineFrame.new()
	box.tex = load("res://art/ui_dialogue.png")
	_choice_panel = box
	_choice_layer.add_child(_choice_panel)


# ---------------------------------------------------------------- playing an event

func play(id: String) -> void:
	if running or not HeartEvents.EVENTS.has(id):
		return
	event_id = id
	event = world._event_place(HeartEvents.EVENTS[id])     # its backup place, if the story hasn't opened its own
	running = true
	_actors = {}
	_walkers = []
	await _fade_to(1.0, 0.35)
	if event.has("player"):
		var p: Array = event["player"]
		world.player.position = world._feet(Vector2i(int(p[0]), int(p[1])))
		world.player.scene_face(int(DIRS.get(p[2], 0)))
	for c in event.get("cast", []):
		_place(str(c[0]), int(c[1]), int(c[2]), str(c[3]))
		if c.size() > 4:
			var r = _actor(str(c[0]))
			if r != null:
				r.scene_pose(str(c[4]))
	await _fade_to(0.0, 0.45)
	await _run(event.get("steps", []))
	await _fade_to(1.0, 0.45)
	for r in _actors.values():
		r.scene_end()
	_actors = {}
	world.player.visible = true
	world.sky_override = ""
	if _ship_home != Vector2.INF and world.wreck_sprite != null:
		world.wreck_sprite.position = _ship_home
		world.wreck_sprite.modulate.a = 1.0
	_ship_home = Vector2.INF
	for n in _fx.values():
		n.queue_free()
	_fx = {}
	if _holo != null:
		_holo.queue_free()
		_holo = null
	for pair in world.sara_nodes:      # her pads: shown where you are, back to idle
		pair[0].visible = pair[1] == world.current_area
		pair[0].play("idle")
	world.player.scene_walking = false
	world.player._cam.offset = Vector2.ZERO
	world._heart_event_done(id)
	await _fade_to(0.0, 0.45)
	running = false
	finished.emit(id)


func _run(steps: Array) -> void:
	for s in steps:
		await _step(s)


func _step(s: Array) -> void:
	var op: String = s[0]
	match op:
		"say":
			var who: String = s[1]
			if who != "" and who != "player" and _absent(who):
				return
			var label: String = str(s[3]) if s.size() > 3 else who
			await _say(label, s[2], who)
		"place":
			_place(str(s[1]), int(s[2]), int(s[3]), str(s[4]))
		"met":
			# the scene introduces them, so talking to them next isn't a first meeting
			if world.persons.has(str(s[1])):
				world.persons[str(s[1])]["met"] = true
		"go":
			# the scene moves to another map (best done under a fade): the player goes there; place the cast after
			world._go_to(str(s[1]), Vector2i(int(s[2]), int(s[3])), false)
			world._event_area = world.current_area
			if _holo != null:
				_holo.visible = false      # the scene places her again on the new map
			world.player.scene_face(int(DIRS.get(str(s[4]), 0)))
		"walk":
			_start_walk(str(s[1]), Vector2i(int(s[2]), int(s[3])))
			await _wait_walkers()
		"walks":
			for w in s[1]:
				_start_walk(str(w[0]), Vector2i(int(w[1]), int(w[2])))
			await _wait_walkers()
		"face":
			_face(str(s[1]), str(s[2]))
		"pose":
			var r = _actor(str(s[1]))
			if r != null:
				r.scene_pose(str(s[2]))
		"emote":
			if str(s[1]) == "player":
				world.player.show_emote(StringName(str(s[2])))
			elif str(s[1]) == "Sara":
				_sara_emote(StringName(str(s[2])))
			elif _actor(str(s[1])) != null:
				world._emote(str(s[1]), StringName(str(s[2])))
		"wait":
			await get_tree().create_timer(float(s[1])).timeout
		"fade":
			await _fade_to(float(s[1]), float(s[2]))
		"shake":
			_shake_time = float(s[1])
			_shake_px = float(s[2])
		"sfx":
			world.sfx(str(s[1]))
		"clock":
			world.minutes += float(s[1])
		"choose":
			var options: Array = s[1]
			var pick: int = await _choose(options)
			var chosen: Dictionary = options[pick]
			var points: int = int(chosen.get("friendship", 0))
			if points != 0:
				world._add_friendship(str(event["who"]), points)
			await _run(chosen.get("steps", []))
		"if":
			if _test(s[1]):
				await _run(s[2])
			elif s.size() > 3:
				await _run(s[3])
		"flag":
			world.story_flags[str(s[1])] = true
		"friendship":
			world._add_friendship(str(s[1]), int(s[2]))
		"perk":
			world.story_flags["perk_" + str(s[1])] = true
			world.sfx("quest")
			world._toast(str(s[2]))
		"keepsake":
			world.story_flags["keepsake_" + str(s[1])] = true
			world.sfx("quest")
			world._toast(str(s[2]))
		"partner":
			world.partner = str(s[1])
		"toast":
			world._toast(str(s[1]))
		"hide", "show":
			if str(s[1]) == "player":
				world.player.visible = op == "show"
			elif _actor(str(s[1])) != null:
				_actor(str(s[1])).visible = op == "show"     # main.gd's _snap_residents shows them again afterwards
		"ship":
			await _ship(str(s[1]), float(s[2]) if s.size() > 2 else 2.5)
		"sky":
			world.sky_override = str(s[1])
		"energy":
			world.energy = maxi(0, int(world.energy) + mini(0, int(s[1])))
		"sara":
			_sara(s)
		"fx":
			_show_fx(str(s[1]), Vector2i(int(s[2]), int(s[3])), float(s[4]) if s.size() > 4 else 14.0)
		_:
			push_warning("cutscene: unknown step " + op)


func _test(cond: Dictionary) -> bool:
	if cond.has("flag"):
		return world._flag(str(cond["flag"]))
	if cond.has("not_flag"):
		return not world._flag(str(cond["not_flag"]))
	if cond.has("arrived"):
		return world._arrived(str(cond["arrived"]))
	if cond.has("partner"):
		return world.partner == str(cond["partner"])
	if cond.has("dating_other"):
		return world.partner != "" and world.partner != str(cond["dating_other"])
	return false


# ---------------------------------------------------------------- actors

# The resident called who, taken over for this scene; null if they aren't on the station yet (the scene plays
# without them, as the hard-lock rule says).
func _actor(who: String):
	if _actors.has(who):
		return _actors[who]
	if _absent(who):
		return null
	for r in world.residents:
		if r.who == who:
			r.scene_begin()
			_actors[who] = r
			return r
	return null


func _absent(who: String) -> bool:
	return not world._arrived(who)


func _place(who: String, x: int, y: int, dir: String) -> void:
	if who == "player":
		world.player.position = world._feet(Vector2i(x, y))
		world.player.scene_face(int(DIRS.get(dir, 0)))
		return
	var r = _actor(who)
	if r != null:
		r.scene_place(world.current_area, Vector2i(x, y), int(DIRS.get(dir, 0)))


func _face(who: String, toward: String) -> void:
	var dir := -1
	if DIRS.has(toward):
		dir = int(DIRS[toward])
	else:
		var from: Vector2 = world.player.position if who == "player" else (_actor(who).position if _actor(who) != null else Vector2.ZERO)
		var to: Vector2 = world.player.position if toward == "player" else (_actor(toward).position if _actor(toward) != null else from)
		var d: Vector2 = to - from
		if d.length() > 0.5:
			dir = (2 if d.x < 0.0 else 3) if absf(d.x) > absf(d.y) else (1 if d.y < 0.0 else 0)
	if dir < 0:
		return
	if who == "player":
		world.player.scene_face(dir)
	elif _actor(who) != null:
		_actor(who).scene_face(dir)


func _start_walk(who: String, to: Vector2i) -> void:
	if who == "player":
		var from: Vector2i = world.player_tile()
		var path: Array = world.find_path(world.current_area, from, [to])
		if path.is_empty():
			path = [to]
		var points: Array = []
		for t in path:
			points.append(world._feet(t))
		world.player.scene_walking = true
		_walkers.append(["player", null, points])
		return
	var r = _actor(who)
	if r != null:
		r.scene_walk_to(to)
		_walkers.append([who, r, []])


func _wait_walkers() -> void:
	if _walkers.is_empty():
		return
	await _walk_done


func _process(delta: float) -> void:
	if not running:
		return
	for r in _actors.values():
		r.scene_tick(delta)
	if not _walkers.is_empty():
		var done: Array = []
		for w in _walkers:
			if w[0] == "player":
				var points: Array = w[2]
				if points.is_empty() or world.player.scene_step(points[0], delta):
					if not points.is_empty():
						points.remove_at(0)
					if points.is_empty():
						done.append(w)
			elif w[1].scene_step(delta):
				done.append(w)
		for w in done:
			_walkers.erase(w)
			if w[0] == "player":
				world.player.scene_walking = false
		if _walkers.is_empty():
			_walk_done.emit()
	if _shake_time > 0.0:
		_shake_time -= delta
		world.player._cam.offset = Vector2(randf_range(-_shake_px, _shake_px), randf_range(-_shake_px, _shake_px)) if _shake_time > 0.0 else Vector2.ZERO


# Your ship (main.gd's wreck_sprite, in the Shuttle Bay) lifts off its pad, climbing faster as it goes and fading
# out through the launch doors, or comes back down and settles. The bay shakes a little as it goes.
func _ship(how: String, seconds: float) -> void:
	var ship: Sprite2D = world.wreck_sprite
	if ship == null:
		return
	if _ship_home == Vector2.INF:
		_ship_home = ship.position
	var up: Vector2 = _ship_home + Vector2(0, -SHIP_RISE)
	var t := create_tween().set_parallel(true)
	if how == "lift":
		ship.position = _ship_home
		ship.modulate.a = 1.0
		_shake_time = seconds * 0.5
		_shake_px = 1.5
		t.tween_property(ship, "position", up, seconds).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
		t.tween_property(ship, "modulate:a", 0.0, seconds * 0.4).set_delay(seconds * 0.6)
	else:
		ship.position = up
		ship.modulate.a = 0.0
		t.tween_property(ship, "position", _ship_home, seconds).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		t.tween_property(ship, "modulate:a", 1.0, seconds * 0.4)
	await t.finished
	if how != "lift":
		_shake_time = 0.3
		_shake_px = 1.0


# Bees, fireflies or steam round a tile (a little above the floor, where hands and flowers are). The same kind
# again drifts the one already there to the new tile.
func _show_fx(kind: String, t: Vector2i, spread: float) -> void:
	var at: Vector2 = world._feet(t) + Vector2(0, -10)
	if _fx.has(kind):
		_fx[kind].move_to(at, spread)
		return
	var n = SceneFx.new()
	n.setup(kind, at, spread)
	world.actors.add_child(n)
	_fx[kind] = n


# S.A.R.A. in a scene: the hologram that's speaking here (her portable projection, else her pad in this area).
func _sara_here():
	if _holo != null and _holo.visible:
		return _holo
	for pair in world.sara_nodes:
		if pair[1] == world.current_area:
			return pair[0]
	return null


func _sara(s: Array) -> void:
	if str(s[1]) == "place":
		if _holo == null:
			if not ResourceLoader.exists("res://sara/sara_hologram.tscn"):
				return
			_holo = load("res://sara/sara_hologram.tscn").instantiate()
			_holo.show_projector = false            # a beam from the emitter on your belt, no dais
			_holo.art_scale = (2.0 / 3.0) / 2.0     # the same size as her pads (main.gd _add_sara)
			world.actors.add_child(_holo)
		_holo.position = world._feet(Vector2i(int(s[2]), int(s[3])))
		_holo.visible = true
		_holo.play("materialize")
		for pair in world.sara_nodes:              # one S.A.R.A. at a time
			if pair[1] == world.current_area:
				pair[0].visible = false
		return
	var h = _sara_here()
	if h != null:
		h.play(str(s[1]))


# An emote bubble over S.A.R.A. (her holograms have none of their own).
func _sara_emote(id: StringName) -> void:
	var h = _sara_here()
	if h == null or not ResourceLoader.exists("res://overhead_emotes/overhead_emote.tscn"):
		return
	var e = h.get_node_or_null("SceneEmote")
	if e == null:
		e = load("res://overhead_emotes/overhead_emote.tscn").instantiate()
		e.name = "SceneEmote"
		e.scale = Vector2.ONE * (2.0 / 3.0)       # as over the player: 24-pixel art above a 32-tall figure
		h.add_child(e)
	e.show_story(id, 1.4)


# ---------------------------------------------------------------- lines, choices, fades

func _say(label: String, lines: Array, who: String) -> void:
	world._say(label, lines, Callable(), "", Callable(), "Not now", who if who != "" else label)
	world.dialogue.on_done = Callable(self, "_on_dialogue_done")
	await _dialogue_done


func _on_dialogue_done() -> void:
	_dialogue_done.emit()


func _choose(options: Array) -> int:
	_choices = options
	_choice_at = 0
	for l in _choice_labels:
		l.queue_free()
	_choice_labels = []
	var h: float = 6.0 + 11.0 * options.size()
	_choice_panel.position = Vector2(8, 102 - h)
	_choice_panel.size = Vector2(304, h)
	for i in options.size():
		var l := Label.new()
		l.position = Vector2(8, 3 + 11 * i)
		l.size = Vector2(290, 11)
		l.clip_text = true
		l.add_theme_font_size_override("font_size", 8)
		_choice_panel.add_child(l)
		_choice_labels.append(l)
	_show_choices()
	_choosing = true
	_choice_layer.visible = true
	var pick: int = await _choice_made
	_choosing = false
	_choice_layer.visible = false
	return pick


func _show_choices() -> void:
	for i in _choice_labels.size():
		var l: Label = _choice_labels[i]
		var text: String = str(_choices[i].get("text", ""))
		l.text = ("> " if i == _choice_at else "  ") + "%d. %s" % [i + 1, text]
		l.add_theme_color_override("font_color", Color("ffd27f") if i == _choice_at else Color.WHITE)


func _pick(i: int) -> void:
	if not _choosing or i < 0 or i >= _choices.size():
		return
	world.sfx("click")
	_choice_made.emit(i)


func _fade_to(alpha: float, seconds: float) -> void:
	var t := create_tween()
	t.tween_property(_fade, "color:a", alpha, seconds)
	await t.finished


# ---------------------------------------------------------------- input (main.gd sends it while running)

func handle_input(e: InputEvent) -> void:
	if _choosing:
		if e.is_action_pressed("move_up"):
			_choice_at = (_choice_at + _choices.size() - 1) % _choices.size()
			_show_choices()
		elif e.is_action_pressed("move_down"):
			_choice_at = (_choice_at + 1) % _choices.size()
			_show_choices()
		elif e.is_action_pressed("interact") or e.is_action_pressed("use"):
			_pick(_choice_at)
		elif e is InputEventKey and e.pressed and not e.echo:
			var k: int = (e as InputEventKey).physical_keycode
			if k >= KEY_1 and k <= KEY_4:
				_pick(k - KEY_1)
		return
	if world.dialogue.active and (e.is_action_pressed("interact") or e.is_action_pressed("use")):
		world.dialogue.advance()


func handle_click(button: int) -> void:
	if _choosing:
		if button == MOUSE_BUTTON_WHEEL_UP:
			_choice_at = (_choice_at + _choices.size() - 1) % _choices.size()
			_show_choices()
		elif button == MOUSE_BUTTON_WHEEL_DOWN:
			_choice_at = (_choice_at + 1) % _choices.size()
			_show_choices()
		elif button == MOUSE_BUTTON_LEFT:
			_pick(_choice_at)
		return
	if world.dialogue.active and button == MOUSE_BUTTON_LEFT:
		world.dialogue.advance()
