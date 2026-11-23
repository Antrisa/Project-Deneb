extends Node2D
# The player. Position is the point between the feet.

const Poses = preload("res://scripts/player_poses.gd")
const WalkCycle = preload("res://scripts/walk_cycle.gd")
const MapData = preload("res://scripts/map_data.gd")

const SPEED := 70.0
const CARRY_SPEED := 50.0

var world            # set by main.gd before entering the tree
var frozen := false
var carrying := false

var _sprite: Sprite2D
var _action_body: Sprite2D
var _water_arm: Sprite2D
var _crate: Sprite2D
var _cam: Camera2D
var _walk_distance := 0.0
var _dir := 0            # column in the sprite sheet
var _last_phase := -1
var _slash: Sprite2D
var _slash_time := 0.0
var _beam: Line2D
var _beam_time := 0.0
var _tool: Sprite2D
var _tool_time := 0.0
# Tool textures have their grip at the centre. Each pose supplies a native hand position.
var _held: Sprite2D
var _held_kind := ""
var _held_time := 0.0
var _held_facing := 0
var _held_length := 0.42
const HELD_LEN := 0.42
const HELD_VIEWS := ["south", "north", "west", "east"]                 # by _dir
const HELD_GRIP := [Vector2(1, -9), Vector2(0, -12), Vector2(-4, -11), Vector2(4, -11)]   # hand on legacy 8-row sheets, by _dir
# Where the beam leaves the laser, from grips.csv, relative to the grip in art pixels (same for every tier).
const LASER_EMITTER := [Vector2(0, 12), Vector2(0, -13), Vector2(-17, -6), Vector2(17, -6)]
var _flash_time := 0.0
var _weapon: Sprite2D        # the spear or sword while it is being swung
var _spear_tex: Texture2D
var _sword_tex: Texture2D
var _attack_time := 0.0
var _attack_kind := ""
var _attack_dir := Vector2.DOWN

const ATTACK_LEN := 0.26
const HAND := Vector2(0, -11)

# Eating, as in Stardew: facing the screen, the food is held up over the head (the carry pose), dropped
# into the open mouth, and swallowed. The food and mouth sprites are made the first time they are needed.
const EAT_FOOD := "res://player_eating/ration_6.png"   # the ration has no inventory picture of its own
const EAT_HOLD := 0.45       # held up
const EAT_DROP := 0.15       # falling into the mouth
const EAT_CHEW := 0.12       # mouth still open
const EAT_GULP := 0.30       # mouth shut, a small nod as it goes down
const EAT_HELD_Y := -31.0    # centre of the food held up between the hands
const EAT_MOUTH := [Vector2i(11, 18), Vector2i(11, 17)]   # top-left art pixel of the open mouth, per body
var eating := false
var _eat_time := 0.0
var _eat_food: Sprite2D
var _eat_mouth: Sprite2D
var _eat_size := 1.0


func _ready() -> void:
	# A soft ground shadow at the feet (cozy art pass), added first so everything else draws over it.
	add_child(preload("res://scripts/prop_fx.gd").make_shadow(18, Vector2(0, 1), Vector2.ONE * (2.0 / 3.0)))
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://art/player.png")
	_sprite.hframes = 4      # columns: down, up, left, right
	_sprite.centered = false
	_sprite.position = Vector2(-8, -30)     # sprite frames are 16x32
	add_child(_sprite)
	_action_body = Sprite2D.new()
	_action_body.centered = false
	_action_body.hframes = 4
	_action_body.vframes = Poses.LEGACY_COUNT
	add_child(_action_body)
	_water_arm = Sprite2D.new()
	_water_arm.centered = false
	_water_arm.hframes = 4
	_water_arm.vframes = Poses.WATER_ROWS.size()
	_water_arm.visible = false
	add_child(_water_arm)
	var fallback_actions: Texture2D = null
	if ResourceLoader.exists("res://art/player_actions.png"):
		fallback_actions = load("res://art/player_actions.png")
	set_sheet(_sprite.texture, fallback_actions)

	# The crate shown over the head while carrying (crate tile from tiles.png).
	_crate = Sprite2D.new()
	_crate.texture = load("res://art/tiles.png")
	var cell: int = _crate.texture.get_width() / int(MapData.TILE_COLUMNS)
	var crate_index: int = MapData.TILE_OBJ["c"]
	_crate.region_enabled = true
	_crate.region_rect = Rect2(crate_index * cell, cell, cell, cell)
	_crate.scale = Vector2(16.0 / cell, 16.0 / cell)
	_crate.centered = false
	_crate.position = Vector2(-8, -44)
	_crate.visible = false
	add_child(_crate)

	# The swing effect for weapons. art/slash.png: frame 0 sword arc, frame 1 spear thrust.
	_slash = Sprite2D.new()
	_slash.texture = load("res://art/slash.png")
	_slash.hframes = 2
	_slash.scale = Vector2.ONE * (16.0 / _slash.texture.get_height())     # any size; shown 16 high
	_slash.visible = false
	add_child(_slash)

	# The mining laser's beam.
	_beam = Line2D.new()
	_beam.width = 1.5
	_beam.default_color = Color(1.0, 0.35, 0.3)
	_beam.visible = false
	add_child(_beam)

	# The tool or weapon shown in the hand while it is being used (a picture from art/items.png).
	_tool = Sprite2D.new()
	_tool.texture = load("res://art/items.png")
	_tool.region_enabled = true
	_tool.scale = Vector2.ONE * (16.0 / _tool.texture.get_height())     # icons can be any size
	_tool.visible = false
	add_child(_tool)

	_held = Sprite2D.new()
	_held.scale = Vector2.ONE * (2.0 / 3.0)       # one tool pixel = one player pixel
	_held.visible = false
	add_child(_held)

	# Weapon art is drawn pointing right with the grip at the left end, so it can be turned about the hand.
	_spear_tex = load("res://art/weapon_spear.png")
	_sword_tex = load("res://art/weapon_sword.png")
	_weapon = Sprite2D.new()
	_weapon.centered = false
	_weapon.visible = false
	add_child(_weapon)

	_cam = Camera2D.new()
	_cam.position = Vector2(0, -8)
	_cam.zoom = Vector2.ONE * 1.5          # 640x360 screen, 24-pixel art at two-thirds: one art pixel per screen pixel
	add_child(_cam)
	_cam.make_current()


func set_limits(size: Vector2i, headroom: int = 0) -> void:
	# A room smaller than the view (640x360 at 1.5x zoom: about 427x240 world units) is centred instead of
	# sitting in the top-left corner.
	var pad_x: int = maxi(0, (427 - size.x) / 2)
	var pad_y: int = maxi(0, (240 - size.y) / 2)
	_cam.limit_left = -pad_x
	_cam.limit_top = -pad_y - headroom
	_cam.limit_right = size.x + pad_x
	_cam.limit_bottom = size.y + pad_y
	_cam.reset_smoothing()


# The direction the player is facing, as a vector.
func facing() -> Vector2:
	var dirs: Array = [Vector2(0, 1), Vector2(0, -1), Vector2(-1, 0), Vector2(1, 0)]
	var d: Vector2 = dirs[_dir]
	return d


func _icon_rect(icon: int) -> Rect2:
	var cell: float = _tool.texture.get_height()
	return Rect2(icon * cell, 0, cell, cell)


# The character screen replaces the whole walk sheet when a look changes.
func set_sheet(tex: Texture2D, actions: Texture2D = null) -> void:
	_sprite.frame = 0
	_sprite.texture = tex
	_sprite.vframes = WalkCycle.rows(tex)
	_sprite.frame_coords = Vector2i(_dir, 0)
	var frame_w: float = tex.get_width() / 4.0
	_sprite.scale = Vector2.ONE * (16.0 / frame_w)
	_action_body.frame = 0
	_action_body.texture = actions
	_water_arm.texture = null
	if actions is Poses.ActionSheet:
		_water_arm.texture = actions.watering_arms
	elif actions != null and actions.resource_path == "res://art/player_actions.png" and ResourceLoader.exists("res://art/player_watering_arms.png"):
		_water_arm.texture = load("res://art/player_watering_arms.png")
	if actions != null:
		_action_body.vframes = WalkCycle.rows(actions)
	_action_body.scale = _sprite.scale
	_refresh_body_pose()


# Holds an item out for a moment. icon is its position in art/items.png.
func show_tool(icon: int) -> void:
	var spots: Array = [Vector2(6, -9), Vector2(6, -13), Vector2(-9, -12), Vector2(9, -12)]
	_tool.region_rect = _icon_rect(icon)
	_tool.position = spots[_dir]
	_tool.rotation = 0.0
	_tool.flip_v = false
	_tool.flip_h = _dir == 2
	_behind(_tool, _dir == 1)
	_tool.visible = true
	_tool_time = 0.3


# Pushed back by a hit (stops at walls).
func knock(push: Vector2) -> void:
	for i in 3:
		var next: Vector2 = position + push / 3.0
		if not _blocked(next):
			position = next


# Blinks red for a moment after being hurt.
func flash() -> void:
	_flash_time = 0.6


# Turns to face a point in the world.
func face(target: Vector2) -> void:
	var d: Vector2 = target - position
	if absf(d.x) > absf(d.y):
		_dir = 2 if d.x < 0.0 else 3
	else:
		_dir = 1 if d.y < 0.0 else 0
	_sprite.frame_coords = Vector2i(_dir, 0)


# Draws the mining laser's beam from the player to a point in the world for a moment.
func fire_laser(target: Vector2, icon: int, tool_id: String = "") -> void:
	face(target + Vector2(0, 8))
	if tool_id != "" and tool_action(tool_id, "laser", target):
		return
	# Hold the laser in the hand, pointed at the vein, with the beam coming out of its tip.
	var hand: Vector2 = HAND + facing() * 5.0
	var aim: Vector2 = (target - position) - hand
	_tool.region_rect = _icon_rect(icon)
	_tool.position = hand
	_tool.rotation = aim.angle()
	_tool.flip_h = false
	_tool.flip_v = absf(aim.angle()) > PI / 2.0
	_tool.visible = true
	_tool_time = 0.3
	_behind(_tool, _dir == 1)
	_beam.clear_points()
	_beam.add_point(hand + aim.normalized() * 7.0)
	_beam.add_point(target - position)
	_beam.visible = true
	_beam_time = 0.18


# Held tool art has its grip in the centre of the texture.
func tool_action(tool_id: String, kind: String, beam_to: Vector2 = Vector2.INF) -> bool:
	var path := "res://art/tools/%s/%s.png" % [tool_id, HELD_VIEWS[_dir]]
	if not ResourceLoader.exists(path):
		return false
	_start_held(load(path), kind, 0.49 if kind == "scythe" else HELD_LEN)
	if kind == "laser":
		var from: Vector2 = _held.position + LASER_EMITTER[_held_facing] * Poses.ART_SCALE
		_beam.clear_points()
		_beam.add_point(from)
		_beam.add_point(beam_to - position if beam_to != Vector2.INF else from + facing() * 10.0)
		_beam.visible = true
		_beam_time = 0.18 if beam_to != Vector2.INF else 0.08
	return true


func show_pickup(picture: Texture2D) -> void:
	if picture != null:
		_start_held(picture, "pickup", 0.62)


func _start_held(picture: Texture2D, kind: String, duration: float) -> void:
	_tool.visible = false
	_held.texture = picture
	_held_kind = kind
	_held_facing = _dir
	_held_length = duration
	_held_time = duration
	_held.scale = Vector2.ONE * Poses.ART_SCALE
	_held.offset = Vector2.ZERO
	if kind == "pickup":
		var size := picture.get_size()
		_held.scale *= minf(1.0, minf(14.0 / size.x, 14.0 / size.y))
	_held.visible = true
	_behind(_held, _held_facing == 1 and kind != "pickup")
	if kind == "water" and _held_facing != 1:
		move_child(_water_arm, -1)
	_animate_held()
	_refresh_body_pose()


func _held_pose() -> int:
	return Poses.tool_row(_held_kind, 1.0 - _held_time / _held_length, _action_body.vframes if _action_body.texture != null else 0)


func _animate_held() -> void:
	var t := clampf(1.0 - _held_time / _held_length, 0.0, 1.0)
	var row := _held_pose()
	var side := -1.0 if _held_facing == 2 else 1.0
	var rows := _action_body.vframes if _action_body.texture != null else 0
	if rows >= Poses.PREVIOUS_COUNT:
		_held.position = Poses.world_grip(row, _held_facing, rows)
	else:
		var old_row: int = Poses.LEGACY_ROWS[row]
		_held.position = HELD_GRIP[_held_facing] + Vector2(0, -6 if old_row == 6 else 2 if old_row == 7 else 0)
	_held.rotation = 0.0
	_held.flip_v = false
	match _held_kind:
		"hoe":
			if _held_facing >= 2:
				# Lift slowly, accelerate through contact, then ease out.
				var angle := -1.48 * smoothstep(0.0, 0.31, t) + 1.91 * smoothstep(0.35, 0.53, t) - 0.43 * smoothstep(0.79, 1.0, t)
				_held.rotation = angle * side
			else:
				_held.flip_v = _held_facing == 0 and row == Poses.LIFT
		"water":
			_held.offset = -Poses.CAN_RIM[_held_facing] if rows == Poses.COUNT else Vector2.ZERO
			if rows == Poses.COUNT:
				var tip := smoothstep(0.43, 0.55, t) * (1.0 - smoothstep(0.73, 0.90, t))
				if _held_facing >= 2:
					var lift := smoothstep(0.10, 0.27, t) * (1.0 - smoothstep(0.38, 0.50, t))
					_held.rotation = side * (0.97 * tip - 0.12 * lift)
				else:
					_held.rotation = tip * (0.22 if _held_facing == 0 else -0.18)
			elif _held_facing >= 2:
				var tilt := smoothstep(0.06, 0.27, t) * (1.0 - smoothstep(0.76, 0.99, t))
				_held.rotation = 0.68 * tilt * side
		"scythe":
			var sweep := -0.86 + 2.71 * smoothstep(0.20, 0.62, t) - 0.78 * smoothstep(0.78, 1.0, t)
			_held.rotation = sweep * (-side if _held_facing == 1 else side)
		"pickup":
			_held.visible = row == Poses.SHOW_ITEM
			var grip := Vector2(12.0 if _held_facing < 2 else (10.0 if _held_facing == 2 else 13.0), 5.0)
			_held.position = (grip - Vector2(Poses.FOOT)) * Poses.ART_SCALE
			_held.position.y -= _held.texture.get_height() * _held.scale.y * 0.5
		"laser":
			if _beam.visible and _beam.get_point_count() == 2:
				_beam.set_point_position(0, _held.position + LASER_EMITTER[_held_facing] * Poses.ART_SCALE)


# World position on the actual rotated can, sampled as each droplet leaves the spout.
func watering_spout() -> Vector2:
	if _held_kind != "water" or _held_time <= 0.0 or not _held.visible:
		return Vector2.INF
	return _held.to_global(_held.offset + Poses.CAN_SPOUT[_held_facing])


# Draws a held item behind the body (when facing away) or in front of it.
func _behind(item: Node, yes: bool) -> void:
	move_child(item, 0 if yes else get_child_count() - 1)


# Shows the weapon swing in the direction the player is facing.
func swing(kind: String) -> void:
	_attack_kind = kind
	_attack_dir = facing()
	_attack_time = ATTACK_LEN
	_weapon.texture = _spear_tex if kind == "spear" else _sword_tex
	# Weapon art can be any size: the spear is shown 7 high in the world, the sword 9.
	var weapon_scale: float = 2.0 / 3.0       # 24-pixel-grid art, like everything else
	_weapon.scale = Vector2(weapon_scale, weapon_scale)
	_weapon.offset = (Vector2(-3, -3.5) if kind == "spear" else Vector2(-2, -4.5)) / weapon_scale
	_weapon.flip_v = _attack_dir.x < 0.0
	_weapon.visible = true
	_behind(_weapon, _dir == 1)
	# The streak of the blow.
	_slash.frame = 1 if kind == "spear" else 0
	_slash.position = HAND + _attack_dir * (24.0 if kind == "spear" else 15.0)
	_slash.rotation = _attack_dir.angle()
	_slash.visible = true
	_slash_time = 0.16
	_animate_attack()


# The spear is thrust out and drawn back; the sword sweeps through an arc. The body leans into it.
func _animate_attack() -> void:
	var k: float = 1.0 - clampf(_attack_time / ATTACK_LEN, 0.0, 1.0)
	var lean: float = sin(k * PI)
	var hand: Vector2 = HAND + _attack_dir * 3.0
	if _attack_kind == "spear":
		_weapon.position = hand + _attack_dir * (lean * 13.0 - 7.0)
		_weapon.rotation = _attack_dir.angle()
	else:
		var sweep: float = lerpf(-1.4, 1.4, k)
		if _attack_dir.x < 0.0:
			sweep = -sweep
		_weapon.position = hand
		_weapon.rotation = _attack_dir.angle() + sweep
	_sprite.position = Vector2(-8, -30) + _attack_dir * lean * 2.0


func set_carrying(value: bool) -> void:
	carrying = value
	_crate.visible = value
	_refresh_body_pose()


# Plays the eating animation, facing the screen (1.02 s). look is the character-screen choices
# (scripts/player_maker.gd), used for the body (the mouth sits a pixel higher on body 2). food is the
# item's picture; null uses the ration's.
# Returns false, changing nothing, if it can't play just now (sitting, carrying, or already eating).
func play_eating(look: Dictionary, food: Texture2D = null) -> bool:
	if eating or sitting or carrying or _action_body.texture == null:
		return false
	if food == null and ResourceLoader.exists(EAT_FOOD):
		food = load(EAT_FOOD)
	if _eat_food == null:
		_eat_mouth = Sprite2D.new()
		var img := Image.create(2, 2, false, Image.FORMAT_RGBA8)
		img.set_pixel(0, 0, Color("3b1e22"))
		img.set_pixel(1, 0, Color("3b1e22"))
		img.set_pixel(0, 1, Color("b4505a"))
		img.set_pixel(1, 1, Color("9c3f4a"))
		_eat_mouth.texture = ImageTexture.create_from_image(img)
		_eat_mouth.centered = false
		_eat_mouth.scale = Vector2.ONE * Poses.ART_SCALE
		_eat_mouth.visible = false
		add_child(_eat_mouth)
		_eat_food = Sprite2D.new()
		_eat_food.visible = false
		add_child(_eat_food)
	var at: Vector2i = EAT_MOUTH[1 if int(look.get("body", 0)) == 1 else 0]
	_eat_mouth.position = Vector2(-8, -30) + Vector2(at) * Poses.ART_SCALE
	_eat_food.texture = food
	_eat_size = Poses.ART_SCALE
	if food != null:
		var size := food.get_size()
		_eat_size *= minf(1.0, minf(12.0 / size.x, 12.0 / size.y))
	_dir = 0
	_sprite.frame_coords = Vector2i(0, 0)
	eating = true
	_eat_time = 0.0
	_animate_eating()
	return true


func _animate_eating() -> void:
	var t := _eat_time
	var mouth := _eat_mouth.position + Vector2(1, 1) * Poses.ART_SCALE
	var held := Vector2(0, EAT_HELD_Y)
	_eat_food.visible = _eat_food.texture != null and t < EAT_HOLD + EAT_DROP
	# let go at the end of the hold: it falls, shrinking into the mouth
	var k := clampf((t - EAT_HOLD) / EAT_DROP, 0.0, 1.0)
	_eat_food.position = held.lerp(mouth, k * k)
	_eat_food.scale = Vector2.ONE * _eat_size * lerpf(1.0, 0.45, k * k)
	_eat_mouth.visible = t >= EAT_HOLD and t < EAT_HOLD + EAT_DROP + EAT_CHEW
	var gulp := t >= EAT_HOLD + EAT_DROP + EAT_CHEW and t < EAT_HOLD + EAT_DROP + EAT_CHEW + 0.12
	_sprite.position = Vector2(-8, -30) + (Vector2(0, Poses.ART_SCALE) if gulp else Vector2.ZERO)
	_eat_mouth.modulate = _sprite.modulate
	_eat_food.modulate = _sprite.modulate
	_refresh_body_pose()


# The gear page takes its standing picture from the first row of the active walk sheet.
func front_sheet() -> Texture2D:
	return _sprite.texture


# A bubble over the player's head (overhead_emotes/), picked on the datapad's emote page (V).
var _emote = null
func show_emote(id: StringName) -> void:
	if _emote == null:
		if not ResourceLoader.exists("res://overhead_emotes/overhead_emote.tscn"):
			return
		_emote = load("res://overhead_emotes/overhead_emote.tscn").instantiate()
		_emote.scale = Vector2.ONE * (2.0 / 3.0)       # 24-pixel art; its foot sits just above the 32-tall sprite
		add_child(_emote)
	_emote.show_story(id, 1.4)


func _look_colour(look: Dictionary, key: String) -> Color:
	var hex: String = str(look.get(key, ""))
	return Color.html(hex) if Color.html_is_valid(hex) else Color.WHITE


func _eating_done() -> void:
	eating = false
	_eat_food.visible = false
	_eat_mouth.visible = false
	_sprite.position = Vector2(-8, -30)
	_refresh_body_pose()


func _process(delta: float) -> void:
	if _slash_time > 0.0:
		_slash_time -= delta
		if _slash_time <= 0.0:
			_slash.visible = false
	if _attack_time > 0.0:
		_attack_time -= delta
		_animate_attack()
		if _attack_time <= 0.0:
			_weapon.visible = false
			_sprite.position = Vector2(-8, -30)
	if _tool_time > 0.0:
		_tool_time -= delta
		if _tool_time <= 0.0:
			_tool.visible = false
	if _held_time > 0.0:
		_held_time -= delta
		_animate_held()
		if _held_time <= 0.0:
			_held.visible = false
	if _flash_time > 0.0:
		_flash_time -= delta
		_sprite.modulate = Color(1.0, 0.45, 0.45) if int(_flash_time * 16.0) % 2 == 0 and _flash_time > 0.0 else Color.WHITE
	if _beam_time > 0.0:
		_beam_time -= delta
		_beam.default_color = Color(1.0, 0.35, 0.3) if int(_beam_time * 40.0) % 2 == 0 else Color(1.0, 0.85, 0.8)
		if _beam_time <= 0.0:
			_beam.visible = false
	if eating:
		_eat_time += delta
		if _eat_time >= EAT_HOLD + EAT_DROP + EAT_CHEW + EAT_GULP:
			_eating_done()
		else:
			_animate_eating()
	_move_player(delta)
	_refresh_body_pose()


func _move_player(delta: float) -> void:
	if frozen or eating or sitting:
		_stop_walking()
		return

	var dir: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if dir == Vector2.ZERO:
		_stop_walking()
		return

	if absf(dir.x) > absf(dir.y):
		_dir = 2 if dir.x < 0.0 else 3
	else:
		_dir = 1 if dir.y < 0.0 else 0

	var start := position
	# put down somewhere already on a wall's picture (an old save, a door): let them walk off it
	var faces := not _blocked(position)
	var speed: float = CARRY_SPEED if carrying else SPEED
	var step: Vector2 = dir * speed * delta
	var next_x: Vector2 = position + Vector2(step.x, 0)
	if not _blocked(next_x, faces):
		position = next_x
	var next_y: Vector2 = position + Vector2(0, step.y)
	if not _blocked(next_y, faces):
		position = next_y

	var distance := start.distance_to(position)
	if is_zero_approx(distance):
		_stop_walking()
		return
	_walk_distance = fmod(_walk_distance + distance, WalkCycle.STRIDE)
	var beat := WalkCycle.phase(_walk_distance)
	_sprite.frame_coords = Vector2i(_dir, WalkCycle.pose(beat, _sprite.vframes))
	if beat != _last_phase and beat % 2 == 0:
		world.sfx("step", randf_range(0.85, 1.15), -9.0)
	_last_phase = beat


func _stop_walking() -> void:
	_walk_distance = 0.0
	_last_phase = -1
	_sprite.frame_coords = Vector2i(_dir, 0)


# The walk sprite remains the source of direction, contact row, and the datapad picture.
func _refresh_body_pose() -> void:
	var visible_body := not sitting
	var can_pose := visible_body and _action_body.texture != null
	var row := -1
	var dir := _dir
	if can_pose and eating:
		# the hands stay up while the food falls
		if _eat_time < EAT_HOLD + EAT_DROP:
			row = 0
			dir = 0
	elif can_pose and carrying:
		row = _sprite.frame_coords.y
	elif can_pose and _held_time > 0.0:
		row = _held_pose()
		dir = _held_facing
		if _action_body.vframes == Poses.LEGACY_COUNT:
			row = Poses.LEGACY_ROWS[row]
	_action_body.visible = row >= 0
	_sprite.visible = visible_body and row < 0
	if row >= 0:
		_action_body.frame_coords = Vector2i(dir, row)
		_action_body.position = _sprite.position
		_action_body.modulate = _sprite.modulate
	var water_index := Poses.WATER_ROWS.find(row) if _held_kind == "water" else -1
	_water_arm.visible = water_index >= 0 and dir != 1 and _water_arm.texture != null
	if _water_arm.visible:
		_water_arm.transform = _action_body.transform
		_water_arm.modulate = _action_body.modulate
		_water_arm.frame_coords = Vector2i(dir, water_index)
	if carrying and _crate != null:
		# walking toward or away from the camera the body drops a pixel on the contact steps and
		# rises one on the passing steps (tools/fix_player_walk.py); from the side it only drops
		var bob := Poses.ART_SCALE if row in [1, 2] else (-Poses.ART_SCALE if row in [3, 4] and dir < 2 else 0.0)
		_crate.position.x = -8.0
		_crate.position.y = -42.0 + bob if can_pose else -44.0


# faces: also keep off the tile in front of a wall below you, where the wall's picture is drawn (it
# stands a tile tall above its own tile), so you don't walk on top of the walls on a room's south side.
func _blocked(p: Vector2, faces: bool = true) -> bool:
	for off in [Vector2(-5, -6), Vector2(5, -6), Vector2(-5, 0), Vector2(5, 0)]:
		var corner: Vector2 = p + off
		if world.solid_at(corner):
			return true
		if faces and world.has_method("wall_face_at") and world.wall_face_at(corner):
			return true
	return false

# Sitting (22 Nov): the seated picture is built from the standing frame of the player's own sheet, so
# it wears their colours. Facing the screen or away, the thighs are foreshortened (two rows of leg come
# out); from the side, the thighs run forward along the seat and the shins hang from the knee.
# main.gd says where the hips go and, for a seat whose back is between the sitter and the camera, the
# line below which the sitter is hidden.
const SIT_HIP := 36          # art row of the hips in a standing frame
const SIT_THIGH := 5         # how far the thighs reach forward, sitting sideways
var sitting := false
var _sit_sprite: Sprite2D


func set_sitting(value: bool, direction: int = 0, hip: Vector2 = Vector2.ZERO, hide_below: float = INF) -> void:
	sitting = value
	_dir = direction
	if value:
		if _sit_sprite == null:
			_sit_sprite = Sprite2D.new()
			_sit_sprite.centered = false
			_sit_sprite.scale = Vector2.ONE * Poses.ART_SCALE
			add_child(_sit_sprite)
		var built: Array = _sit_picture(direction)
		var img: Image = built[0]
		var hip_x: float = built[1]
		# the hips land on the seat; anything below hide_below (world y) is behind the seat back
		var at: Vector2 = (hip - position - Vector2(hip_x, SIT_HIP) * Poses.ART_SCALE).round()
		if hide_below < INF:
			var keep := int(floor((hide_below - position.y - at.y) / Poses.ART_SCALE))
			for y in range(maxi(keep, 0), img.get_height()):
				for x in img.get_width():
					img.set_pixel(x, y, Color(0, 0, 0, 0))
		_sit_sprite.texture = ImageTexture.create_from_image(img)
		_sit_sprite.position = at
	if _sit_sprite != null:
		_sit_sprite.visible = value
	_refresh_body_pose()


# [picture, hip x] for sitting with the given facing, from the standing frame of the walk sheet.
func _sit_picture(face: int) -> Array:
	var sheet: Image = _sprite.texture.get_image()
	if sheet.is_compressed():
		sheet.decompress()
	sheet.convert(Image.FORMAT_RGBA8)
	var fw := int(sheet.get_width() / 4)
	var fh := int(sheet.get_height() / _sprite.vframes)
	var stand := sheet.get_region(Rect2i(face * fw, 0, fw, fh))
	if face < 2:
		var out := Image.create(fw, fh, false, Image.FORMAT_RGBA8)
		out.blit_rect(stand, Rect2i(0, 0, fw, SIT_HIP + 2), Vector2i.ZERO)
		# from behind, the legs go forward under the seat or table, out of sight
		if face == 0:
			out.blit_rect(stand, Rect2i(0, SIT_HIP + 4, fw, fh - SIT_HIP - 4), Vector2i(0, SIT_HIP + 2))
		return [out, _middle(stand, SIT_HIP)]
	# Sideways: worked out facing right, then mirrored for left.
	if face == 2:
		stand.flip_x()
	var w := fw + SIT_THIGH + 2
	var side := Image.create(w, fh, false, Image.FORMAT_RGBA8)
	side.blit_rect(stand, Rect2i(0, 0, fw, SIT_HIP), Vector2i.ZERO)
	var knee := 0
	for y in range(SIT_HIP, SIT_HIP + 4):           # the thighs, along the seat
		var xs := _opaque(stand, y)
		if xs.is_empty():
			continue
		var a: int = xs[0]
		var b: int = xs[xs.size() - 1]
		for x in range(a, b + 1):
			side.set_pixel(x, y, stand.get_pixel(x, y))
		var cloth := stand.get_pixel(maxi(a, b - 2), y)
		for x in range(b - 1, b - 1 + SIT_THIGH):
			side.set_pixel(x, y, cloth)
		side.set_pixel(b + SIT_THIGH - 2, y, stand.get_pixel(maxi(a, b - 1), y))
		side.set_pixel(b + SIT_THIGH - 1, y, stand.get_pixel(b, y))
		knee = maxi(knee, b + SIT_THIGH - 1)
	var toes := 0
	for y in range(SIT_HIP + 4, fh):
		var xs := _opaque(stand, y)
		if not xs.is_empty():
			toes = maxi(toes, xs[xs.size() - 1])
	var shift := knee - toes + 1
	for y in range(SIT_HIP + 4, fh):                  # the shins and feet, hanging from the knees
		for x in _opaque(stand, y):
			if x + shift >= 0 and x + shift < w:
				side.set_pixel(x + shift, y, stand.get_pixel(x, y))
	var hip_x := _middle(stand, SIT_HIP)
	if face == 2:
		side.flip_x()
		hip_x = w - 1 - hip_x
	return [side, hip_x]


func _opaque(img: Image, y: int) -> Array:
	var xs := []
	for x in img.get_width():
		if img.get_pixel(x, y).a > 0.0:
			xs.append(x)
	return xs


func _middle(img: Image, y: int) -> float:
	var xs := _opaque(img, y)
	return img.get_width() / 2.0 if xs.is_empty() else (float(xs[0]) + float(xs[xs.size() - 1])) / 2.0
