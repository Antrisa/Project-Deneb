extends Node
# Heart-event cutscenes (22 Nov 2026). Plays an event from scripts/heart_events.gd, Stardew-style:
#   - residents step out of their schedules: placed, walked, turned, posed (their heart-event sheet,
#     art/npc_<id>_event.png, or a row of their action sheet) and given emote bubbles;
#   - the player is walked and turned too;
#   - lines go through the talk box with portraits; choices are listed in the box, under the question;
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
#                                      {"partner": who}, {"dating_other": who}, {"has": item} (it's in your pack)
#   ["flag", name]  ["friendship", who, points]  ["perk", id, toast]  ["keepsake", id, toast]
#   ["partner", who]  ["toast", text]  ["give", item, count, toast]   puts items in your pack (Rusk's seeds); toast ""
#                                      gives it quietly, for several gifts and then one "toast"
#   ["mail", letter, days]             sends a letter (scripts/mail_data.gd): it comes with the post that many mornings
#                                      later (1: the next morning), with its gift if it has one
#   ["hide", who]  ["show", who]        out of sight and back (boarding your ship); everyone shows again at the end
#   ["ship", "lift" or "land", seconds] your ship in the Shuttle Bay rises out through the launch doors and fades,
#                                      or comes back down onto its pad; it's back on the pad when the scene ends
#   ["sky", event]                     the Observation Lounge's window shows that sky event ("meteors", "aurora",
#                                      "comet"...; scripts/lounge_sky.gd) until the scene ends
#   ["energy", -points]                a small cost for a wrong choice (a bee sting): takes that much energy
#   ["fx", kind, x, y, spread]         bees, fireflies, steam, heartbeats, spray or bubbles drawn round that tile
#                                      (scripts/scene_fx.gd); the same kind again moves it there (bees settling on a hand);
#                                      ["fx", kind, "off"] stops it (the pipe is mended); all gone when the scene ends
#   ["sara", clip]                     S.A.R.A. plays one of her hologram clips (sara/animations_data.gd: greeting, laugh,
#                                      glitch_hand, standby, wake...): her portable projection if the scene placed one,
#                                      else her pad in this area. "emote" and "say" work for "Sara" too.
#   ["sara", "place", x, y]            her portable projection (her 6 onwards) materializes on that tile, and her pad here
#                                      hides; after a "go", place it again. Gone, and her pads back, when the scene ends.
# Picture panels (the prologue, 24 Nov): a full-screen picture over the world, under the talk box, with sprites the
# scene moves about on it. Board coordinates are the screen's 640 x 360 pixels, sprites by their top-left corner.
#   ["board", path]                    shows that picture over the screen (a fade first looks best); "" puts the board
#                                      and its sprites away (they are gone when the scene ends anyway)
#   ["bsprite", id, path, x, y, opts]  puts a sprite on the board; opts (all optional): "flip" (mirrored), "frames" and
#                                      "fps" (a strip of frames that plays), "loop" (false: plays once and stays on the
#                                      last), "alpha", "z" (higher in front), "scale" (a whole number: the main
#                                      menu's fighter is shown 3x, as the menu shows it), "bob" ([pixels, seconds]: a
#                                      slow float; sprites with the same bob move as one), "add" (true: drawn as light,
#                                      added to what's under it); path "" takes it away
#   ["bmove", id, x, y, seconds, ease] moves it there and waits ("in" speeds up, "out" slows down, else even);
#                                      ["bmoves", [[id, x, y], ...], seconds, ease] moves several at once; either
#                                      with "nowait" after the ease goes on at once (a rock drifting past)
#   ["bfade", id, alpha, seconds]      fades it and waits; ["bfade", id, alpha, seconds, "nowait"] goes on at once
#   ["flash", hex, seconds]            the screen flashes that colour, then clears
#   "shake" shakes the board too. ["board", "clear"] puts up an empty board: sprites over the map (the glyphs).
# Sprites in the world (24 Nov: the crash site), placed by tile, at the map's art scale, over the props:
#   ["wsprite", id, path, tx, ty, opts]  as "bsprite" (but no "scale"), its top-left at tile tx, ty (fractions fine)
#   ["wmove", id, tx, ty, seconds, ease]  ["wfade", id, alpha, seconds] (or "nowait")
# Sound under the scene (24 Nov: "some random music plays over the whole thing"):
#   ["music", mode]       "silence" (the music fades out and stays out), a song's id (music_director.gd SONGS), or
#                         "" to give the music back; a scene can start with "music" set the same way
#   ["score", song, from, hold_from, hold_to]   the end of a song timed to the scene (25 Nov): starts at `from`
#                         seconds and holds on [hold_from, hold_to) while the player reads; ["score_cue", t] moves it
#                         on to t at the next bar (or at once, cross-faded); ["score_wait", t] waits till it's at t;
#                         ["score_end"] waits till it ends. ["say_timed", who, lines, label, [seconds a line]] turns
#                         its lines over by themselves (no clicking), so the scene plays out in time with its music
#   ["ambient", bed]      "none", "amb_space", "amb_caves", "amb_station"..., or "" for the place's own
# Events can also need a second resident at the same hearts ("with": ["Evarra"]) and play only in some
# seasons ("seasons": ["Autumn", "Winter"]): main.gd _event_ready.
# play() also takes the story scenes in HeartEvents.SCENES (your first morning) and StoryScenes.SCENES (the main
# story: scripts/story_scenes.gd), which main.gd starts itself.

const HeartEvents = preload("res://scripts/heart_events.gd")
const StoryScenes = preload("res://scripts/story_scenes.gd")
const SceneFx = preload("res://scripts/scene_fx.gd")
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
var _shake_time := 0.0
var _shake_px := 0.0
var _ship_home := Vector2.INF   # where your ship stands on its pad, while a scene flies it
const SHIP_RISE := 220.0        # how far up the ship climbs before it's gone through the launch doors
var _fx := {}                   # kind -> the scene's effect node (scripts/scene_fx.gd)
var _holo = null                # S.A.R.A.'s portable projection in this scene ("sara", "place")
var _board_layer: CanvasLayer   # the picture panels: under the fade (9) and the talk box (10)
var _board: Node2D
var _board_bg: Sprite2D
var _board_sprites := {}        # id -> Sprite2D
var _hands_off := false         # a "say_timed" line is up: it turns over by itself, clicks do nothing
var _bob := {}                  # sprite id ("w:" + id for world sprites) -> [pixels, seconds, base offset y]
var _bob_time := 0.0
var _add_mat: CanvasItemMaterial = null
var _board_anim := {}           # id -> [fps, seconds so far, loop]
var _flash: ColorRect
var board_box_top := true       # the talk box over a picture panel: at the top, unless the scene says "box": "bottom"
var _world_sprites := {}        # id -> Sprite2D in the world ("wsprite")
var music_mode := ""            # read by scripts/music_director.gd while a scene runs ("music")
var amb_mode := ""              # ... and the ambient bed ("ambient")
const ART := 2.0 / 3.0          # the map's art scale (24 art pixels to a 16-unit tile), as main.gd


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
	_flash = ColorRect.new()
	_flash.color = Color(1, 1, 1, 0)
	_flash.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_flash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_layer.add_child(_flash)
	_board_layer = CanvasLayer.new()
	_board_layer.layer = 8
	add_child(_board_layer)
	_board = Node2D.new()
	_board.visible = false
	_board_layer.add_child(_board)
	_board_bg = Sprite2D.new()
	_board_bg.centered = false
	_board_bg.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_board.add_child(_board_bg)


# ---------------------------------------------------------------- playing an event

func play(id: String) -> void:
	if running or not has_scene(id):
		return
	event_id = id
	# a heart event at its backup place if the story hasn't opened its own, or a story scene (HeartEvents.SCENES,
	# StoryScenes.SCENES)
	event = world._event_place(scene_def(id))
	running = true
	_actors = {}
	_walkers = []
	await _fade_to(1.0, 0.35)
	var area: String = str(event.get("area", "here"))     # "here": wherever you are (the Harbinger's cavern floor)
	if area != "here" and area != world.current_area:
		# a story scene somewhere else (the prologue, from your flat to the Medbay): go there under the fade
		var at: Array = event.get("player", [1, 1, "d"])
		world._go_to(str(event["area"]), Vector2i(int(at[0]), int(at[1])), false)
		world._event_area = world.current_area
	if event.has("player"):
		var p: Array = event["player"]
		world.player.position = world._feet(_stand(Vector2i(int(p[0]), int(p[1]))))
		world.player.scene_face(int(DIRS.get(p[2], 0)))
	for c in event.get("cast", []):
		_place(str(c[0]), int(c[1]), int(c[2]), str(c[3]))
		if c.size() > 4:
			var r = _actor(str(c[0]))
			if r != null:
				r.scene_pose(str(c[4]))
	board_box_top = str(event.get("box", "top")) != "bottom"
	music_mode = str(event.get("music", ""))
	amb_mode = str(event.get("ambient", ""))
	if event.has("board"):            # the scene opens on a picture (the prologue)
		_board_bg.texture = load(str(event["board"]))
		_board.visible = true
		for st in event.get("board_setup", []):
			await _step(st)
	await _fade_to(0.0, 0.45)
	await _run(event.get("steps", []))
	await _fade_to(1.0, 0.45)
	for r in _actors.values():
		r.scene_end()
	_actors = {}
	world.scene_stand_player()
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
	_board_clear()
	_world_clear()
	music_mode = ""
	amb_mode = ""
	world._heart_event_done(id)
	await _fade_to(0.0, 0.45)
	running = false
	finished.emit(id)


static func has_scene(id: String) -> bool:
	return HeartEvents.EVENTS.has(id) or HeartEvents.SCENES.has(id) or StoryScenes.SCENES.has(id)


static func scene_def(id: String) -> Dictionary:
	if HeartEvents.EVENTS.has(id):
		return HeartEvents.EVENTS[id]
	if HeartEvents.SCENES.has(id):
		return HeartEvents.SCENES[id]
	return StoryScenes.SCENES.get(id, {})


func _run(steps: Array) -> void:
	var i := 0
	while i < steps.size():
		var s: Array = steps[i]
		# A line followed by a choice (with only instant steps between): the answers come up inside the same box,
		# under the question, as in Stardew (24 Nov). The steps between play once you've answered.
		if str(s[0]) == "say" and not (str(s[1]) != "" and str(s[1]) != "player" and _absent(str(s[1]))):
			var j := i + 1
			while j < steps.size() and str(steps[j][0]) in INSTANT:
				j += 1
			if j < steps.size() and str(steps[j][0]) == "choose":
				var label: String = str(s[3]) if s.size() > 3 else str(s[1])
				var options: Array = steps[j][1]
				var pick: int = await _say_choose(label, s[2], str(s[1]), options)
				for k in range(i + 1, j):
					await _step(steps[k])
				await _chosen(options, pick)
				i = j + 1
				continue
		await _step(s)
		i += 1


# Steps that take no time, which may sit between a question and its answers.
const INSTANT := ["emote", "face", "pose", "sfx", "met", "flag", "show", "hide"]


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
			_world_clear()
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
		"sfx":         # ["sfx", name] or ["sfx", name, pitch] (a lower pitch also plays it slower)
			world.sfx(str(s[1]), float(s[2]) if s.size() > 2 else 1.0)
		"clock":
			world.minutes += float(s[1])
		"choose":
			var options: Array = s[1]
			var pick: int = await _choose(options)
			await _chosen(options, pick)
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
		"give":
			world._give(str(s[1]), int(s[2]))
			if s.size() > 3 and str(s[3]) != "":       # "" gives it quietly (several gifts, then one "toast")
				world.sfx("gift")
				world._toast(str(s[3]))
		"mail":
			world.send_mail(str(s[1]), int(s[2]) if s.size() > 2 else 1)
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
			if s.size() == 3 and str(s[2]) == "off":
				if _fx.has(str(s[1])):
					_fx[str(s[1])].queue_free()
					_fx.erase(str(s[1]))
			else:
				_show_fx(str(s[1]), Vector2i(int(s[2]), int(s[3])), float(s[4]) if s.size() > 4 else 14.0)
		"board":
			if str(s[1]) == "":
				_board_clear()
			elif str(s[1]) == "clear":
				_board_bg.texture = null
				_board.visible = true
			else:
				_board_bg.texture = load(str(s[1]))
				_board.visible = true
		"wsprite":
			_world_sprite(str(s[1]), str(s[2]), float(s[3]), float(s[4]), s[5] if s.size() > 5 else {})
		"wmove":
			var wsp: Sprite2D = _world_sprites.get(str(s[1]))
			if wsp != null:
				var wt := create_tween()
				var tw := wt.tween_property(wsp, "position", Vector2(float(s[2]) * 16.0, float(s[3]) * 16.0), maxf(0.01, float(s[4])))
				if s.size() > 5 and str(s[5]) == "in":
					tw.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
				elif s.size() > 5 and str(s[5]) == "out":
					tw.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
				await wt.finished
		"wfade":
			var fsp: Sprite2D = _world_sprites.get(str(s[1]))
			if fsp != null:
				var ft := create_tween()
				ft.tween_property(fsp, "modulate:a", float(s[2]), maxf(0.01, float(s[3])))
				if not (s.size() > 4 and str(s[4]) == "nowait"):
					await ft.finished
		"score":
			# ["score", song, from, loop_from, loop_to]: the end of a song timed to the scene (music_director.gd
			# score_play): it starts at `from` and holds on [loop_from, loop_to) until a "score_cue"
			music_mode = "score"
			if world.music_director != null:
				var hold := Vector2(float(s[3]), float(s[4])) if s.size() > 4 else Vector2(-1.0, -1.0)
				world.music_director.score_play(str(s[1]), float(s[2]), hold)
		"score_cue":
			if world.music_director != null:
				world.music_director.score_cue(float(s[1]))
		"score_wait":
			# waits for the score to reach a moment (the FTL jump lands on Space Battle's big hit)
			while world.music_director != null and not world.music_director.score_done() and world.music_director.score_pos() < float(s[1]):
				await get_tree().process_frame
		"score_end":
			while world.music_director != null and not world.music_director.score_done():
				await get_tree().process_frame
		"say_timed":
			# ["say_timed", who, [lines], label, [seconds a line]]: lines that turn over by themselves, so the scene
			# keeps time with its music (Zachary, 25 Nov: "just have it play out, you cant click to continue");
			# clicks and keys do nothing while they're up
			var tlabel: String = str(s[3]) if s.size() > 3 and str(s[3]) != "" else str(s[1])
			var secs: Array = s[4] if s.size() > 4 and s[4] is Array else []
			_hands_off = true
			world._say(tlabel, s[2], Callable(), "", Callable(), "Not now", str(s[1]) if str(s[1]) != "" else tlabel)
			while world.dialogue.active:
				var at: int = world.dialogue.line_index()
				var left: float = float(secs[at]) if at < secs.size() else 3.0
				while left > 0.0 and world.dialogue.active and world.dialogue.line_index() == at:
					await get_tree().process_frame
					left -= get_process_delta_time()
				if world.dialogue.active and world.dialogue.line_index() == at:
					world.dialogue.turn_line()
			_hands_off = false
		"music":
			music_mode = str(s[1])
		"ambient":
			amb_mode = str(s[1])
		"bsprite":
			_board_sprite(str(s[1]), str(s[2]), float(s[3]) if s.size() > 3 else 0.0, float(s[4]) if s.size() > 4 else 0.0, s[5] if s.size() > 5 else {})
		"bmove":
			# ["bmove", id, x, y, seconds, easing?, "nowait"?]: "nowait" lets the scene go on while it glides
			if s.size() > 6 and str(s[6]) == "nowait":
				_board_move([[s[1], s[2], s[3]]], float(s[4]), str(s[5]))
			else:
				await _board_move([[s[1], s[2], s[3]]], float(s[4]), str(s[5]) if s.size() > 5 else "")
		"bmoves":
			if s.size() > 4 and str(s[4]) == "nowait":
				_board_move(s[1], float(s[2]), str(s[3]))
			else:
				await _board_move(s[1], float(s[2]), str(s[3]) if s.size() > 3 else "")
		"bfade":
			var sp: Sprite2D = _board_sprites.get(str(s[1]))
			if sp != null:
				var t := create_tween()
				t.tween_property(sp, "modulate:a", float(s[2]), maxf(0.01, float(s[3])))
				if not (s.size() > 4 and str(s[4]) == "nowait"):
					await t.finished
		"flash":
			_flash.color = Color(str(s[1]))
			_flash.color.a = 1.0
			var t := create_tween()
			t.tween_property(_flash, "color:a", 0.0, float(s[2]))
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
	if cond.has("has"):
		return world._count(str(cond["has"])) > 0
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


# A scripted spot on a wall, or on the floor row a south wall's picture covers, moves to the nearest proper floor
# tile, trying straight up first (Zachary, 24 Nov: in Freya's 2-heart event "your character is standing on a wall").
func _stand(t: Vector2i) -> Vector2i:
	if _standable(t):
		return t
	for r in range(1, 4):
		for off in [Vector2i(0, -r), Vector2i(-r, 0), Vector2i(r, 0), Vector2i(0, r),
				Vector2i(-r, -r), Vector2i(r, -r), Vector2i(-r, r), Vector2i(r, r)]:
			if _standable(t + off):
				return t + off
	return t


func _standable(t: Vector2i) -> bool:
	var mid := Vector2((t.x + 0.5) * world.TILE, (t.y + 0.5) * world.TILE)
	if world.solid_at(mid):
		return false
	return not (world.has_method("wall_face_at") and world.wall_face_at(mid))


func _place(who: String, x: int, y: int, dir: String) -> void:
	var t := _stand(Vector2i(x, y))
	if who == "player":
		world.scene_stand_player()
		world.player.position = world._feet(t)
		world.player.scene_face(int(DIRS.get(dir, 0)))
		world.scene_sit_player()
		return
	var r = _actor(who)
	if r != null:
		r.scene_place(world.current_area, t, int(DIRS.get(dir, 0)))


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
	to = _stand(to)
	if who == "player":
		world.scene_stand_player()           # up out of a seat first
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
						world.player.scene_walking = false
						world.scene_sit_player()       # walked onto a chair: sit in it (24 Nov)
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
		_board.position = world.player._cam.offset.round()
	_bob_time += delta
	for id in _bob:
		var bsp: Sprite2D = _board_sprites.get(id) if not str(id).begins_with("w:") else _world_sprites.get(str(id).substr(2))
		if bsp == null:
			continue
		var bob: Array = _bob[id]
		# a whole number of screen pixels, so sprites bobbing together (a ship and its flames) stay together
		var px: float = round(sin(_bob_time * TAU / float(bob[1])) * float(bob[0]))
		bsp.offset.y = float(bob[2]) + px / maxf(0.01, bsp.scale.y)
	for id in _board_anim:
		var a: Array = _board_anim[id]
		var sp: Sprite2D = _board_sprites.get(id) if not str(id).begins_with("w:") else _world_sprites.get(str(id).substr(2))
		if sp == null or sp.hframes < 2:
			continue
		a[1] = float(a[1]) + delta
		var f: int = int(float(a[1]) * float(a[0]))
		sp.frame = f % sp.hframes if bool(a[2]) else mini(f, sp.hframes - 1)


# ---------------------------------------------------------------- picture panels

func _board_sprite(id: String, path: String, x: float, y: float, opts: Dictionary) -> void:
	if _board_sprites.has(id):
		_board_sprites[id].queue_free()
		_board_sprites.erase(id)
		_board_anim.erase(id)
		_bob.erase(id)
	if path == "":
		return
	var sp := Sprite2D.new()
	sp.texture = load(path)
	sp.centered = false
	sp.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sp.position = Vector2(x, y)
	sp.scale = Vector2.ONE * float(opts.get("scale", 1.0))   # whole numbers only, so the pixels stay square
	_sprite_opts(sp, id, opts)
	_board.add_child(sp)
	_board_sprites[id] = sp


# The options board and world sprites share: flip, frames + fps + loop (an animation strip), alpha, z, bob
# ([pixels, seconds]: a slow float up and down) and add (drawn as light, added to what's under it).
func _sprite_opts(sp: Sprite2D, key: String, opts: Dictionary) -> void:
	sp.flip_h = bool(opts.get("flip", false))
	sp.hframes = maxi(1, int(opts.get("frames", 1)))
	sp.modulate.a = float(opts.get("alpha", 1.0))
	sp.z_index += int(opts.get("z", 0))
	if bool(opts.get("add", false)):
		if _add_mat == null:
			_add_mat = CanvasItemMaterial.new()
			_add_mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		sp.material = _add_mat
	if sp.hframes > 1:
		_board_anim[key] = [float(opts.get("fps", 8.0)), 0.0, bool(opts.get("loop", true))]
	if opts.has("bob"):
		var b: Array = opts["bob"]
		_bob[key] = [float(b[0]), maxf(0.1, float(b[1])), sp.offset.y]


func _board_move(moves: Array, seconds: float, easing: String) -> void:
	var t := create_tween().set_parallel(true)
	var any := false
	for m in moves:
		var sp: Sprite2D = _board_sprites.get(str(m[0]))
		if sp == null:
			continue
		any = true
		var tw := t.tween_property(sp, "position", Vector2(float(m[1]), float(m[2])), maxf(0.01, seconds))
		if easing == "in":
			tw.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
		elif easing == "out":
			tw.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	if any:
		await t.finished
	else:
		t.kill()


func _world_sprite(id: String, path: String, tx: float, ty: float, opts: Dictionary) -> void:
	if _world_sprites.has(id):
		_world_sprites[id].queue_free()
		_world_sprites.erase(id)
		_board_anim.erase("w:" + id)
		_bob.erase("w:" + id)
	if path == "":
		return
	var sp := Sprite2D.new()
	sp.texture = load(path)
	sp.centered = false
	sp.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sp.scale = Vector2.ONE * ART
	sp.position = Vector2(tx * 16.0, ty * 16.0)
	sp.z_index = 40                                  # over the props and people
	_sprite_opts(sp, "w:" + id, opts)
	world.actors.add_child(sp)
	_world_sprites[id] = sp


func _world_clear() -> void:
	for sp in _world_sprites.values():
		sp.queue_free()
	for id in _world_sprites:
		_board_anim.erase("w:" + str(id))
		_bob.erase("w:" + str(id))
	_world_sprites = {}


func board_up() -> bool:
	return _board != null and _board.visible


func _board_clear() -> void:
	for sp in _board_sprites.values():
		sp.queue_free()
	_board_sprites = {}
	for id in _bob.keys():                       # the world sprites' animations and bobbing carry on
		if not str(id).begins_with("w:"):
			_bob.erase(id)
	for id in _board_anim.keys():
		if not str(id).begins_with("w:"):
			_board_anim.erase(id)
	_board_bg.texture = null
	_board.visible = false
	_board.position = Vector2.ZERO
	_flash.color.a = 0.0


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


# The answers you can give, listed in the talk box (scripts/dialogue_box.gd start_choice): under the question when
# a line comes just before (_say_choose), else under the last line shown.
func _choose(options: Array) -> int:
	world.dialogue.start_choice("", [], _option_texts(options), Callable(self, "_on_pick"))
	return await _choice_made


func _say_choose(label: String, lines: Array, who: String, options: Array) -> int:
	world._say_choice(label, lines, _option_texts(options), Callable(self, "_on_pick"), who if who != "" else label)
	return await _choice_made


func _option_texts(options: Array) -> Array:
	var texts: Array = []
	for o in options:
		texts.append(str(o.get("text", "")))
	return texts


func _on_pick(i: int) -> void:
	_choice_made.emit(i)


# What an answer does: its friendship, then its own steps.
func _chosen(options: Array, pick: int) -> void:
	var chosen: Dictionary = options[clampi(pick, 0, options.size() - 1)]
	var points: int = int(chosen.get("friendship", 0))
	if points != 0:
		world._add_friendship(str(event["who"]), points)
	await _run(chosen.get("steps", []))


func _fade_to(alpha: float, seconds: float) -> void:
	var t := create_tween()
	t.tween_property(_fade, "color:a", alpha, seconds)
	await t.finished


# ---------------------------------------------------------------- input (main.gd sends it while running)

# (the talk box takes up, down, the wheel, 1 to 4 and the mouse pointer for choices itself)
func handle_input(e: InputEvent) -> void:
	if _hands_off:
		return
	if world.dialogue.active and (e.is_action_pressed("interact") or e.is_action_pressed("use")):
		world.dialogue.advance()


func handle_click(button: int) -> void:
	if _hands_off:
		return
	if world.dialogue.active and button == MOUSE_BUTTON_LEFT:
		world.dialogue.advance()
