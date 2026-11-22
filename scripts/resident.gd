extends Sprite2D
# A resident who follows a daily schedule: at set times they walk to a new spot,
# taking the lifts, airlock or mine ramp if the spot is in another area.
# Schedules live in tools/build.py (SCHEDULES) and are written to scripts/map_data.gd.

const TILE := 16
const SPEED := 48.0      # pixels per second (the player walks at 70)

var world                    # main.gd
var who := ""
var area := ""
var tile := Vector2i.ZERO
var thing: Dictionary = {}   # this resident's entry in world.things (what you press E on)
var schedule: Array = []     # [[minute of day, area, x, y, talk radius], ...] in time order

var _entry := -1
var _target_area := ""
var _target_tile := Vector2i.ZERO
var _path: Array = []        # tiles still to walk in the current area
var _settled := false        # standing at their spot (and blocking that tile)
var _walk_time := 0.0
var _dir := 0                # column in the sprite sheet: 0 down, 1 up, 2 left, 3 right
var _foot_offset := Vector2(-8, -32)
var _base_scale := 1.0
var _walk_tex: Texture2D
var _act_tex: Texture2D = null   # optional art/npc_<id>_act.png: 4 frames across (48x64 each), one row per action
var _act_row := -1           # which row of the action sheet to play at this stop (-1 = none)
var _act_rows := 1           # how many rows the action sheet has
var _facing := 0             # which way they face once they have arrived
var _act := "idle"           # what they do there: work, eat or idle
var _idle_time := 0.0
var activity_pose: Node2D
var away := false            # a visitor who is not on the station today: not shown, cannot be talked to
var emote = null             # the bubble over their head (overhead_emotes/overhead_emote.gd), added by main.gd

const FACING := {"d": 0, "u": 1, "l": 2, "r": 3}
const ACT_ROW := {"work": 0, "eat": 1, "idle": 2}


func setup(main, person_name: String, tex: Texture2D, entries: Array, entry_thing: Dictionary, activity_tex: Texture2D = null) -> void:
	world = main
	who = person_name
	_walk_tex = tex
	_act_tex = activity_tex
	texture = tex
	hframes = 4              # sheets are 4 directions x 3 walking frames
	vframes = 3
	centered = false
	# Sheets can be drawn at any size (16x32 frames, or larger for more detail):
	# the sprite is scaled so a frame is always 16 wide in the world, with the feet at the bottom centre.
	var frame_w: float = tex.get_width() / 4.0
	var frame_h: float = tex.get_height() / 3.0
	_base_scale = 16.0 / frame_w
	scale = Vector2(_base_scale, _base_scale)
	_foot_offset = Vector2(-frame_w / 2.0, -frame_h)
	offset = _foot_offset
	if _act_tex != null:
		# Action frames are 1.5 times as wide as walking frames and the same height.
		_act_rows = maxi(1, roundi(_act_tex.get_height() / frame_h))
	# A soft ground shadow at the feet, 18 art pixels wide (cozy art pass); drawn under the sprite.
	add_child(preload("res://scripts/prop_fx.gd").make_shadow(18, Vector2(0, -1.0 / _base_scale), Vector2.ONE * (2.0 / 3.0) / _base_scale))
	activity_pose = preload("res://scripts/resident_activity.gd").new()
	activity_pose.resident = self
	activity_pose.scale = Vector2.ONE / _base_scale
	add_child(activity_pose)
	schedule = entries
	thing = entry_thing


# Put the resident where their schedule says they should be right now (used each morning).
func snap(minutes: float) -> void:
	_unsettle()
	if away:
		area = ""
		_path = []
		_entry = -1
		visible = false
		thing["area"] = ""
		return
	_entry = _entry_for(minutes)
	var e: Array = schedule[_entry]
	_target_area = e[1]
	_target_tile = Vector2i(int(e[2]), int(e[3]))
	area = _target_area
	tile = _target_tile
	position = _spot(tile)
	_path = []
	offset = _foot_offset
	_settle()
	visible = area == world.current_area
	_sync_thing()


func tick(delta: float, minutes: float) -> void:
	if away:
		visible = false
		return
	var want: int = _entry_for(minutes)
	if want != _entry:
		_entry = want
		var e: Array = schedule[_entry]
		_target_area = e[1]
		_target_tile = Vector2i(int(e[2]), int(e[3]))
		_unsettle()
		_plan()
	_move(delta)
	if _settled:
		_idle(delta)
	visible = area == world.current_area


func _entry_for(minutes: float) -> int:
	# The latest entry whose time has passed; before the first one, last night's final entry.
	var best: int = schedule.size() - 1
	for i in schedule.size():
		var e: Array = schedule[i]
		if float(e[0]) <= minutes:
			best = i
	return best


func _spot(t: Vector2i) -> Vector2:
	return Vector2(t.x * TILE + 8, t.y * TILE + 16)


func _plan() -> void:
	var goals: Array = []
	if area == _target_area:
		goals = [_target_tile]
	else:
		var next_area: String = world.next_area(area, _target_area)
		if next_area != "":
			goals = world.pads_to(area, next_area)
	_path = []
	if not goals.is_empty():
		_path = world.find_path(area, tile, goals)
	if _path.is_empty() and not (area == _target_area and tile == _target_tile):
		# No route found: appear at the destination rather than getting stuck.
		area = _target_area
		tile = _target_tile
		position = _spot(tile)


func _move(delta: float) -> void:
	if _settled:
		return
	if _path.is_empty():
		if area == _target_area and tile == _target_tile:
			# Arrived. Wait for the player to step off the spot before standing on it.
			frame_coords = Vector2i(_dir, 0)
			if not world.player_overlaps_tile(area, tile):
				_settle()
		else:
			_plan()
		_sync_thing()
		return

	var next: Vector2i = _path[0]
	var dest: Vector2 = _spot(next)
	var step: float = SPEED * delta
	var heading: Vector2 = dest - position
	if heading.length() > 0.5:
		if absf(heading.x) > absf(heading.y):
			_dir = 2 if heading.x < 0.0 else 3
		else:
			_dir = 1 if heading.y < 0.0 else 0
	if position.distance_to(dest) <= step:
		position = dest
		tile = next
		_path.remove_at(0)
		# Stepped onto a lift, airlock or ramp pad: carry on in the next area.
		var pads: Dictionary = world.warps[area]
		if pads.has(tile):
			var d: Array = pads[tile]
			area = d[0]
			tile = Vector2i(int(d[1]), int(d[2]))
			position = _spot(tile)
			_plan()
	else:
		position = position.move_toward(dest, step)

	# Walk cycle: step A, standing, step B, standing.
	_walk_time += delta
	var cycle: Array = [1, 0, 2, 0]
	var row: int = cycle[int(_walk_time * 6.0) % 4]
	frame_coords = Vector2i(_dir, row)
	_sync_thing()


func _settle() -> void:
	_settled = true
	offset = _foot_offset
	var here: Dictionary = world.blocked[area]
	here[tile] = true
	var e: Array = schedule[_entry]
	thing["radius"] = float(e[4])
	_facing = int(FACING.get(e[5], 0))
	_act = e[6]
	_act_row = int(e[7]) if e.size() > 7 else -1
	_dir = _facing
	_idle_time = randf() * 6.0
	frame_coords = Vector2i(_facing, 0)


# What a resident does while standing at their spot.
# With an action sheet (art/npc_<id>_act.png) the row for this stop is played: see ACTION_ROWS in map_data.gd.
# Without them, the resident breathes, leans into their work, nods over their food, or glances about.
func _idle(delta: float) -> void:
	_idle_time += delta
	if _act in ["garden","chess","hologame","observe","read","browse","restock"]:
		texture = _walk_tex
		hframes = 4; vframes = 3
		frame_coords = Vector2i(_facing,0)
		offset = _foot_offset
		scale = Vector2.ONE * _base_scale
		rotation = 0.0   # no tilting pixel art (it breaks pixels at 1080p and 1440p)
		self_modulate.a = 0.0 if _act in ["chess","hologame"] else 1.0
		return
	if _act_tex != null and _act_row >= 0 and _act_row < _act_rows:
		if texture != _act_tex:
			frame = 0
			texture = _act_tex
			hframes = 4
			vframes = _act_rows
			rotation = 0.0
			scale = Vector2(_base_scale, _base_scale)
			# feet at the bottom centre of the wider frame
			offset = Vector2(-_act_tex.get_width() / 8.0, -float(_act_tex.get_height()) / _act_rows)
		frame_coords = Vector2i(int(_idle_time * 3.0) % 4, _act_row)
		return
	var look: int = _facing
	rotation = 0.0
	offset = _foot_offset
	# Breathing and working move the sprite by whole art pixels (1 texture pixel = half a world pixel). Stretching
	# or tilting pixel art drops and doubles pixel rows on screen, so neither is used.
	scale = Vector2(_base_scale, _base_scale)
	if sin(_idle_time * 2.2) > 0.6: offset = _foot_offset + Vector2(0, -1)
	if _act == "work":
		if sin(_idle_time * 5.0) > 0.0: offset = _foot_offset + Vector2(0, -1)
	elif _act == "eat":
		if fmod(_idle_time, 1.7) < 0.3:
			offset = _foot_offset + Vector2(0, 1.0 / _base_scale)
	elif _facing == 0:
		var beat: float = fmod(_idle_time, 8.0)
		if beat > 6.0 and beat < 7.0:
			look = 2 if int(_idle_time / 8.0) % 2 == 0 else 3
	frame_coords = Vector2i(look, 0)


func _unsettle() -> void:
	self_modulate.a = 1.0
	if activity_pose != null: activity_pose.visible = false
	if _settled:
		var here: Dictionary = world.blocked[area]
		here.erase(tile)
	_settled = false
	# Back to the walking sheet, standing straight.
	if texture != _walk_tex:
		frame_coords = Vector2i.ZERO
		texture = _walk_tex
		hframes = 4
		vframes = 3
	rotation = 0.0
	offset = _foot_offset
	scale = Vector2(_base_scale, _base_scale)
	thing["radius"] = 26.0


func _sync_thing() -> void:
	thing["area"] = area
	thing["pos"] = position + Vector2(0, -6)
