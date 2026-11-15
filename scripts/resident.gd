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


func setup(main, person_name: String, tex: Texture2D, entries: Array, entry_thing: Dictionary) -> void:
	world = main
	who = person_name
	texture = tex
	hframes = 4              # sheets are 4 directions x 3 walking frames
	vframes = 3
	centered = false
	# Sheets can be drawn at any size (16x32 frames, or larger for more detail):
	# the sprite is scaled so a frame is always 16 wide in the world, with the feet at the bottom centre.
	var frame_w: float = tex.get_width() / 4.0
	var frame_h: float = tex.get_height() / 3.0
	scale = Vector2(16.0 / frame_w, 16.0 / frame_w)
	_foot_offset = Vector2(-frame_w / 2.0, -frame_h)
	offset = _foot_offset
	schedule = entries
	thing = entry_thing


# Put the resident where their schedule says they should be right now (used each morning).
func snap(minutes: float) -> void:
	_unsettle()
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
	var want: int = _entry_for(minutes)
	if want != _entry:
		_entry = want
		var e: Array = schedule[_entry]
		_target_area = e[1]
		_target_tile = Vector2i(int(e[2]), int(e[3]))
		_unsettle()
		_plan()
	_move(delta)
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
	_dir = 0
	frame_coords = Vector2i(0, 0)
	var here: Dictionary = world.blocked[area]
	here[tile] = true
	var e: Array = schedule[_entry]
	thing["radius"] = float(e[4])


func _unsettle() -> void:
	if _settled:
		var here: Dictionary = world.blocked[area]
		here.erase(tile)
	_settled = false
	thing["radius"] = 26.0


func _sync_thing() -> void:
	thing["area"] = area
	thing["pos"] = position + Vector2(0, -6)
