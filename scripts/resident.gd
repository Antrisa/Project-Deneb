extends Sprite2D
# A resident who follows a daily schedule: at set times they walk to a new spot,
# taking the lifts, airlock or mine ramp if the spot is in another area.
# Schedules live in tools/build.py (SCHEDULES) and are written to scripts/map_data.gd.

const WalkCycle = preload("res://scripts/walk_cycle.gd")
const MapData = preload("res://scripts/map_data.gd")

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
var _walker := 1             # seed for this resident's own taste in routes (main.gd find_path)
var _lane := Vector2.ZERO    # where on each tile they walk, so two on one route don't overlap
var _settled := false        # standing at their spot (and blocking that tile)
var _walk_distance := 0.0
var _walk_rows := 3
var _dir := 0                # column in the sprite sheet: 0 down, 1 up, 2 left, 3 right
var _foot_offset := Vector2(-8, -32)
var _base_scale := 1.0
var _walk_tex: Texture2D
var _act_tex: Texture2D = null   # optional art/npc_<id>_act.png: 4 frames across (36x48 each), one row per action
var _act_row := -1           # which row of the action sheet to play at this stop (-1 = none)
var _act_rows := 1           # how many rows the action sheet has
var _facing := 0             # which way they face once they have arrived
# The row of their eyes in the standing frame (art pixels; from tools/poses.py): in bed the eyes go to the
# middle of the pillow, so children, Moogli and the tall alike show their face over the covers.
const EYE_ROW := {"evarra": 14, "rusk": 13, "ooma": 14, "tobbin": 17, "merrow": 12, "nub": 23, "garrick": 10,
	"saffi": 15, "tally": 18, "stu": 12, "ana": 13, "sara": 12, "artie": 14, "vzzket": 12, "tarbesh": 13,
	"zaas": 20, "job": 13, "freya": 13, "tikka": 16, "bram": 17, "sesska": 14, "pip": 23, "kit": 23,
	"ixali": 12, "maren": 13, "quill": 13, "owen": 14, "jasper": 14}
var _act := "idle"           # what they do there: work, eat, idle or sleep
var _idle_time := 0.0
var activity_pose: Node2D
var away := false            # a visitor who is not on the station today: not shown, cannot be talked to
var emote = null             # the bubble over their head (overhead_emotes/overhead_emote.gd), added by main.gd

const FACING := {"d": 0, "u": 1, "l": 2, "r": 3}
const ACT_ROW := {"work": 0, "eat": 1, "idle": 2}


func setup(main, person_name: String, tex: Texture2D, entries: Array, entry_thing: Dictionary, activity_tex: Texture2D = null) -> void:
	world = main
	who = person_name
	_walker = maxi(1, absi(hash(person_name)) % 100000)
	var lane_seed: int = absi(hash(person_name + " lane"))
	_lane = Vector2(float(lane_seed % 7) - 3.0, float((lane_seed / 7) % 5) - 2.0)
	_walk_tex = tex
	_walk_rows = WalkCycle.rows(tex)
	_act_tex = activity_tex
	texture = tex
	hframes = 4
	vframes = _walk_rows
	centered = false
	# Sheets can be drawn at any size (16x32 frames, or larger for more detail):
	# the sprite is scaled so a frame is always 16 wide in the world, with the feet at the bottom centre.
	var frame_w: float = tex.get_width() / 4.0
	var frame_h: float = tex.get_height() / float(_walk_rows)
	_base_scale = 16.0 / frame_w
	scale = Vector2(_base_scale, _base_scale)
	_foot_offset = Vector2(-frame_w / 2.0, -frame_h)
	offset = _foot_offset
	if _act_tex != null:
		# Action frames are 1.5 times as wide as walking frames and the same height.
		_act_rows = maxi(1, roundi(_act_tex.get_height() / frame_h))
	# A soft ground shadow at the feet, 18 art pixels wide (cozy art pass); drawn under the sprite.
	_shadow = preload("res://scripts/prop_fx.gd").make_shadow(18, Vector2(0, -1.0 / _base_scale), Vector2.ONE * (2.0 / 3.0) / _base_scale)
	add_child(_shadow)
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
	if in_scene:
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
		_path = world.find_path(area, tile, goals, _walker)
	if _path.is_empty() and not (area == _target_area and tile == _target_tile):
		# No route found: appear at the destination rather than getting stuck.
		area = _target_area
		tile = _target_tile
		position = _spot(tile)


func _move(delta: float) -> void:
	if _settled:
		return
	if _path.is_empty():
		_walk_distance = 0.0
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
	# keep to their own lane on the way, and step onto the very middle of the last tile
	var dest: Vector2 = _spot(next) + (_lane if _path.size() > 1 else Vector2.ZERO)
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

	# Only the distance walked on this tile counts. A lift can move the actor across maps.
	var distance := minf(heading.length(), step)
	_walk_distance = fmod(_walk_distance + distance, WalkCycle.STRIDE)
	var row := WalkCycle.pose(WalkCycle.phase(_walk_distance), _walk_rows) if distance > 0.0 else 0
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
	if _act != "sleep":
		_sit_if_seat(_act_tex if _act_row >= 0 else null, _act_row, _act_rows, _row_label(_act_row))
	if _act == "sleep":
		# In bed, under the covers: the spot in the bed rather than the middle of the tile.
		var eyes: int = int(EYE_ROW.get(who.to_lower().replace("'", ""), 13))
		var slot = world.bed_slot(area, tile, eyes, _base_scale)
		if slot != null:
			position = slot
			_sync_thing()


# What a resident does while standing at their spot.
# With an action sheet (art/npc_<id>_act.png) the row for this stop is played: see ACTION_ROWS in map_data.gd.
# Without them, the resident breathes, leans into their work, nods over their food, or glances about.
func _idle(delta: float) -> void:
	_idle_time += delta
	if not _sit_seat.is_empty():
		_sit_animate(_idle_time)
		return
	if _act_row == DANCE_ROW:
		_dance()
		return
	if _act_row == JUMP_ROW:
		_jump()
		return
	if _act in ["garden","chess","hologame","observe","read","browse","restock"]:
		texture = _walk_tex
		hframes = 4
		vframes = _walk_rows
		frame_coords = Vector2i(_facing,0)
		offset = _foot_offset
		scale = Vector2.ONE * _base_scale
		rotation = 0.0   # no tilting pixel art (it breaks pixels at 1080p and 1440p)
		self_modulate.a = 0.0 if activity_pose.has_painted_pose() or _act in ["chess","hologame"] else 1.0
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
	_sit_up()
	_walk_distance = 0.0
	self_modulate.a = 1.0
	if activity_pose != null: activity_pose.visible = false
	if _settled:
		var here: Dictionary = world.blocked[area]
		here.erase(tile)
		if _act == "sleep":
			position = _spot(tile)     # out of bed, back on the tile
	_settled = false
	# Back to the walking sheet, standing straight.
	if texture != _walk_tex:
		frame_coords = Vector2i.ZERO
		texture = _walk_tex
		hframes = 4
		vframes = _walk_rows
	rotation = 0.0
	offset = _foot_offset
	scale = Vector2(_base_scale, _base_scale)
	thing["radius"] = 26.0


func _sync_thing() -> void:
	thing["area"] = area
	thing["pos"] = position + Vector2(0, -6)


# ---------------------------------------------------------------- heart-event scenes (scripts/cutscene.gd)
# A scene takes a resident over: they leave their schedule, stand, walk and pose where the scene says, and
# main.gd puts everyone back where their day says once it ends (_snap_residents).
# Poses: "talk", "laugh", "sad", "jump", "gift", "bench", "wave" are rows of art/npc_<id>_event.png (the heart-
# event sheet, art handoff 4b); anything else names a row of their action sheet ("hammer u", "rest d").
const EVENT_ROWS := ["talk", "laugh", "sad", "jump", "gift", "bench", "wave"]

var in_scene := false
var _scene_path: Array = []
var _scene_pose_tex: Texture2D = null
var _scene_pose_row := -1
var _scene_pose_rows := 1
var _scene_time := 0.0
var _event_tex: Texture2D = null


func scene_begin() -> void:
	_unsettle()
	in_scene = true
	_scene_path = []
	_scene_pose_tex = null
	_load_event_tex()


func scene_end() -> void:
	in_scene = false
	_scene_path = []
	_scene_stand(false)


# Put them on a tile of the area the player is in, facing 0 down, 1 up, 2 left, 3 right.
func scene_place(area_name: String, t: Vector2i, dir: int) -> void:
	area = area_name
	tile = t
	position = _spot(t)
	_dir = dir
	_scene_path = []
	_scene_stand()
	visible = area == world.current_area
	_sync_thing()


func scene_face(dir: int) -> void:
	if not _sit_seat.is_empty():
		return                       # seated: they keep facing the way the seat does
	_dir = dir
	if _scene_pose_tex == null:
		frame_coords = Vector2i(_dir, 0)


# Walk to a tile in this area; scene_step() moves them each frame until it returns true.
func scene_walk_to(t: Vector2i) -> void:
	_scene_stand(false)
	_scene_path = world.find_path(area, tile, [t])
	if _scene_path.is_empty() and tile != t:
		_scene_path = [t]


func scene_step(delta: float) -> bool:
	if _scene_path.is_empty():
		frame_coords = Vector2i(_dir, 0)
		return true
	var next: Vector2i = _scene_path[0]
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
		_scene_path.remove_at(0)
	else:
		position = position.move_toward(dest, step)
	var distance := minf(heading.length(), step)
	_walk_distance = fmod(_walk_distance + distance, WalkCycle.STRIDE)
	frame_coords = Vector2i(_dir, WalkCycle.pose(WalkCycle.phase(_walk_distance), _walk_rows) if distance > 0.0 else 0)
	if _scene_path.is_empty():
		_sit_if_seat(null, 0, 1, "")     # walked onto a seat: sit down on it
	_sync_thing()
	return _scene_path.is_empty()


# Play a pose until the next one (or "" to stand). Returns false if they have no art for it.
func scene_pose(pose: String) -> bool:
	_scene_stand()
	if pose == "":
		return true
	var tex: Texture2D = null
	var row := -1
	var rows := 1
	var flip := false
	var pose_name: String = pose.get_slice(" ", 0)
	if EVENT_ROWS.has(pose_name) and _event_tex != null:
		tex = _event_tex
		rows = maxi(1, roundi(_event_tex.get_height() / 48.0))
		row = EVENT_ROWS.find(pose_name)
		flip = pose_name == "gift" and (_dir == 2 or pose.ends_with(" l"))
	elif _act_tex != null:
		var labels: Array = preload("res://scripts/map_data.gd").ACTION_ROWS.get(who, [])
		row = labels.find(pose)
		tex = _act_tex
		rows = _act_rows
	if tex == null or row < 0 or row >= rows:
		return false
	if not _seat_here().is_empty():
		# on a seat: the pose is played sitting (an action pose turned to face the way the seat does; the heart-
		# event sheets are drawn facing the camera, so they only sit in a seat that faces it too)
		if tex == _act_tex:
			_sit_if_seat(tex, row, rows, pose)
		elif int(_seat_here()["dir"]) == 0:
			_sit_if_seat(tex, row, rows, "")
		else:
			_sit_if_seat(null, 0, 1, "")
		_scene_time = 0.0
		return true
	_scene_pose_tex = tex
	_scene_pose_row = row
	_scene_pose_rows = rows
	_scene_time = 0.0
	texture = tex
	hframes = 4
	vframes = rows
	flip_h = flip
	scale = Vector2(_base_scale, _base_scale)
	offset = Vector2(-tex.get_width() / 8.0, -float(tex.get_height()) / rows)
	frame_coords = Vector2i(0, row)
	return true


func scene_tick(delta: float) -> void:
	_scene_time += delta
	if not _sit_seat.is_empty():
		_sit_animate(_scene_time)
		return
	if _scene_pose_tex != null:
		frame_coords = Vector2i(int(_scene_time * 3.0) % 4, _scene_pose_row)


func _scene_stand(sit_ok: bool = true) -> void:
	_sit_up()
	_scene_pose_tex = null
	flip_h = false
	self_modulate.a = 1.0
	if activity_pose != null: activity_pose.visible = false
	texture = _walk_tex
	hframes = 4
	vframes = _walk_rows
	offset = _foot_offset
	scale = Vector2(_base_scale, _base_scale)
	rotation = 0.0
	frame_coords = Vector2i(_dir, 0)
	if sit_ok and in_scene and _scene_path.is_empty():
		_sit_if_seat(null, 0, 1, "")      # placed on a seat, or standing still on one: sit


# ---------------------------------------------------------------- sitting (Zachary, 24 Nov: "give them a sitting
# animation for when they sit here or eat or anything else")
# Nobody's sheets have sitting frames, so they are made here the way the player's are (player.gd _sit_picture):
# from each frame of the pose they would have played standing (eating, resting, talking), the body is kept down to
# the hips and the legs are tucked out of sight behind a seat that faces away, shortened under one that faces the
# camera, or folded out along a seat seen side-on. The frames are made once each time they sit and played at the
# usual three a second, so they keep eating, fidgeting and talking. The hips go on the seat's own hip slot
# (main.gd SEATS); a seat whose back faces the camera is drawn over them.
var _shadow: Sprite2D = null
var _sit_sprite: Sprite2D = null
var _sit_frames: Array = []          # ImageTexture frames of the current sitting pose
var _sit_seat: Dictionary = {}       # main.gd seat_for(): the seat they're on (empty: not sitting)
var _hip_row := -1                   # art row of their hips in a standing frame
var _images := {}                    # Texture2D -> Image, read once


func _seat_here() -> Dictionary:
	if world == null or not world.has_method("seat_for"):
		return {}
	return world.seat_for(area, tile)


func _row_label(row: int) -> String:
	var labels: Array = MapData.ACTION_ROWS.get(who, [])
	return str(labels[row]) if row >= 0 and row < labels.size() else ""


# Sit if this tile is a seat. tex/row/rows: the pose to sit in, with label its action-sheet name ("eat d"), so it
# can be turned to face the way the seat does; tex null sits still (the standing frame of the walking sheet).
func _sit_if_seat(tex: Texture2D, row: int, rows: int, label: String) -> void:
	var seat := _seat_here()
	if seat.is_empty():
		return
	var face: int = int(seat["dir"])
	if label != "" and tex == _act_tex:
		var labels: Array = MapData.ACTION_ROWS.get(who, [])
		row = labels.find(label.get_slice(" ", 0) + " " + "dulr"[face])
		if row < 0 or row >= _act_rows:
			tex = null
	var sources: Array = []
	if tex != null and row >= 0:
		var img: Image = _image_of(tex)
		var fw: int = img.get_width() / 4
		var fh: int = img.get_height() / maxi(1, rows)
		for i in 4:
			sources.append(img.get_region(Rect2i(i * fw, row * fh, fw, fh)))
	else:
		var walk: Image = _image_of(_walk_tex)
		var wfw: int = walk.get_width() / 4
		var wfh: int = walk.get_height() / _walk_rows
		sources.append(walk.get_region(Rect2i(face * wfw, 0, wfw, wfh)))
	var hip := _hip()
	var frames: Array = []
	var hip_x := 0.0
	for src in sources:
		var built: Array = _fold(src, face, hip)
		frames.append(ImageTexture.create_from_image(built[0]))
		hip_x = float(built[1])
	_sit_seat = seat
	_sit_frames = frames
	_dir = face
	var seat_hip: Vector2 = seat["hip"]
	position = Vector2(round(seat_hip.x), float(seat["sort_y"]) + (-1.0 if bool(seat["behind"]) else 1.0))
	if _sit_sprite == null:
		_sit_sprite = Sprite2D.new()
		_sit_sprite.centered = false
		add_child(_sit_sprite)
	_sit_sprite.texture = frames[0]
	# the sprite is a child, in this node's scaled space: one unit is one art pixel
	_sit_sprite.position = ((seat_hip - position) / _base_scale - Vector2(hip_x, hip)).round()
	_sit_sprite.visible = true
	self_modulate.a = 0.0
	if activity_pose != null: activity_pose.visible = false
	if _shadow != null: _shadow.visible = false
	_sync_thing()


func _sit_animate(t: float) -> void:
	if _sit_sprite == null or _sit_frames.is_empty():
		return
	self_modulate.a = 0.0
	_sit_sprite.texture = _sit_frames[int(t * 3.0) % _sit_frames.size()]


func _sit_up() -> void:
	if _sit_seat.is_empty():
		return
	_sit_seat = {}
	_sit_frames = []
	if _sit_sprite != null:
		_sit_sprite.visible = false
	self_modulate.a = 1.0
	if _shadow != null: _shadow.visible = true
	position = _spot(tile)


func _image_of(tex: Texture2D) -> Image:
	if _images.has(tex):
		return _images[tex]
	var img: Image = tex.get_image()
	if img.is_compressed():
		img.decompress()
	img.convert(Image.FORMAT_RGBA8)
	_images[tex] = img
	return img


# The hips: just above where the legs part in the front-facing standing frame (or 72% of the way down the figure).
func _hip() -> int:
	if _hip_row >= 0:
		return _hip_row
	var walk: Image = _image_of(_walk_tex)
	var fw: int = walk.get_width() / 4
	var fh: int = walk.get_height() / _walk_rows
	var f: Image = walk.get_region(Rect2i(0, 0, fw, fh))
	var top := -1
	var bottom := -1
	for y in fh:
		if not _opaque_x(f, y).is_empty():
			if top < 0: top = y
			bottom = y
	if top < 0:
		_hip_row = int(fh * 0.75)
		return _hip_row
	_hip_row = int(round(top + (bottom - top) * 0.72))
	var half: int = top + (bottom - top) / 2
	var y := bottom - 2
	while y > half:
		var runs := 0
		var prev := -9
		for x in _opaque_x(f, y):
			if int(x) != prev + 1: runs += 1
			prev = int(x)
		if runs < 2:
			break
		y -= 1
	if y < bottom - 3 and y > half:
		_hip_row = y
	return _hip_row


# [picture, hip x] for one frame sitting facing face (0 down, 1 up, 2 left, 3 right): player.gd _sit_picture's way.
func _fold(stand: Image, face: int, hip: int) -> Array:
	var fw := stand.get_width()
	var fh := stand.get_height()
	if face < 2:
		var out := Image.create(fw, fh, false, Image.FORMAT_RGBA8)
		out.blit_rect(stand, Rect2i(0, 0, fw, hip + 2), Vector2i.ZERO)
		if face == 0:          # facing the camera: the legs, shortened, over the front of the seat
			out.blit_rect(stand, Rect2i(0, hip + 4, fw, fh - hip - 4), Vector2i(0, hip + 2))
		return [out, _middle_x(stand, hip)]
	var img := Image.new()
	img.copy_from(stand)
	if face == 2:
		img.flip_x()
	var w := fw + 12
	var side := Image.create(w, fh, false, Image.FORMAT_RGBA8)
	side.blit_rect(img, Rect2i(0, 0, fw, hip + 2), Vector2i.ZERO)
	# the legs: the run of pixels nearest the middle a few rows below the hips (an action frame is wider than a
	# walking one, and a hand or a fork at hip height mustn't be taken for a knee, as it would by its far edge)
	var legs := _leg_run(img, hip)
	var back: int = legs.x
	var front: int = legs.y
	for y in range(hip + 2, mini(hip + 8, fh)):          # hands, a hem, whatever is held below the hips, stays
		for x in _opaque_x(img, y):
			if int(x) < back - 1 or int(x) > front + 1:
				side.set_pixel(int(x), y, img.get_pixel(int(x), y))
	for y in range(hip + 2, mini(hip + 5, fh)):          # the seat of the trousers, on the cushion
		for x in _opaque_x(img, y):
			if int(x) >= back - 1 and int(x) < front - 1:
				side.set_pixel(int(x), y, img.get_pixel(int(x), y))
	for y in range(hip, fh - 2):                          # the legs turned a quarter, out along the seat
		for x in _opaque_x(img, y):
			if int(x) < back - 1 or int(x) > front + 1:
				continue
			if int(x) < front - 4 and y < hip + 6:
				continue
			var nx: int = front - 1 + (y - hip)
			var ny: int = hip + (front - int(x))
			if ny >= 0 and ny < fh and nx >= 0 and nx < w:
				side.set_pixel(nx, ny, img.get_pixel(int(x), y))
	var hip_x := _middle_x(img, hip)
	if face == 2:
		side.flip_x()
		hip_x = w - 1 - hip_x
	return [side, hip_x]


# (first, last) column of the legs, from the run of opaque pixels nearest the frame's middle just below the hips
func _leg_run(img: Image, hip: int) -> Vector2i:
	var mid: float = img.get_width() / 2.0
	for dy in [4, 5, 3, 6, 2]:
		var xs := _opaque_x(img, hip + int(dy))
		if xs.is_empty():
			continue
		var best := Vector2i(-1, -1)
		var start: int = int(xs[0])
		var prev: int = int(xs[0])
		for i in range(1, xs.size() + 1):
			var x: int = int(xs[i]) if i < xs.size() else -99
			if x != prev + 1:
				var run := Vector2i(start, prev)
				if best.x < 0 or absf((run.x + run.y) / 2.0 - mid) < absf((best.x + best.y) / 2.0 - mid):
					best = run
				start = x
			prev = x
		return best
	return Vector2i(0, img.get_width() / 2)


func _opaque_x(img: Image, y: int) -> Array:
	var xs := []
	if y < 0 or y >= img.get_height():
		return xs
	for x in img.get_width():
		if img.get_pixel(x, y).a > 0.0:
			xs.append(x)
	return xs


func _middle_x(img: Image, y: int) -> float:
	var xs := _opaque_x(img, y)
	return img.get_width() / 2.0 if xs.is_empty() else (float(xs[0]) + float(xs[xs.size() - 1])) / 2.0


# ---------------------------------------------------------------- poses made in code (25 Nov: the community
# centre's dances and fitness class). Schedules name them like any pose (tools/build.py CODE_POSES); nobody's sheet
# has them, so they are made from frames everyone already has.
const DANCE_ROW := -10
const JUMP_ROW := -11


func _load_event_tex() -> void:
	if _event_tex != null:
		return
	var id: String = who.to_lower().replace("'", "").replace(".", "")
	var path := "res://art/npc_%s_event.png" % id
	if ResourceLoader.exists(path):
		_event_tex = load(path)


# A dance from the walking frames, in bars of two seconds: stepping in time facing their partner, a sway, a turn
# to face the room, and a spin. Partners stand side by side facing each other (Tikka and Sesska, Saffi).
func _dance() -> void:
	texture = _walk_tex
	hframes = 4
	vframes = _walk_rows
	scale = Vector2(_base_scale, _base_scale)
	rotation = 0.0
	var bar: int = int(_idle_time / 2.0) % 4
	var beat: int = int(_idle_time * 2.4)
	var look: int = _facing
	if bar == 2:
		look = 0
	elif bar == 3:
		look = [0, 3, 1, 2][int(_idle_time * 4.0) % 4]       # down, right, up, left: a spin
	frame_coords = Vector2i(look, 0 if bar == 1 else WalkCycle.pose(beat, _walk_rows))
	var sway: float = (-1.0 if beat % 2 == 0 else 1.0) if bar == 1 else 0.0
	offset = _foot_offset + Vector2(sway, -1.0 if beat % 2 == 0 else 0.0)


# Jumping jacks: the arms-up row of their heart-event sheet ("jump"), hopping on the arms-up frames.
func _jump() -> void:
	_load_event_tex()
	rotation = 0.0
	scale = Vector2(_base_scale, _base_scale)
	var frame: int = int(_idle_time * 3.0) % 4
	var hop := Vector2(0, -3.0 if frame == 1 or frame == 2 else 0.0)
	if _event_tex == null:
		texture = _walk_tex
		hframes = 4
		vframes = _walk_rows
		frame_coords = Vector2i(0, 0)
		offset = _foot_offset + hop
		return
	var rows: int = maxi(1, roundi(_event_tex.get_height() / 48.0))
	texture = _event_tex
	hframes = 4
	vframes = rows
	offset = Vector2(-_event_tex.get_width() / 8.0, -float(_event_tex.get_height()) / rows) + hop
	frame_coords = Vector2i(frame, EVENT_ROWS.find("jump"))
