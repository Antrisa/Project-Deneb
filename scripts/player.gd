extends Node2D
# The player. Position is the point between the feet.

const MapData = preload("res://scripts/map_data.gd")

const SPEED := 70.0
const CARRY_SPEED := 50.0

var world            # set by main.gd before entering the tree
var frozen := false
var carrying := false

var _sprite: Sprite2D
var _crate: Sprite2D
var _cam: Camera2D
var _walk_time := 0.0
var _dir := 0            # column in the sprite sheet
var _last_phase := -1
var _slash: Sprite2D
var _slash_time := 0.0
var _beam: Line2D
var _beam_time := 0.0
var _tool: Sprite2D
var _tool_time := 0.0
var _flash_time := 0.0
var _weapon: Sprite2D        # the spear or sword while it is being swung
var _spear_tex: Texture2D
var _sword_tex: Texture2D
var _attack_time := 0.0
var _attack_kind := ""
var _attack_dir := Vector2.DOWN

const ATTACK_LEN := 0.26
const HAND := Vector2(0, -11)

# The eating animation (player_eating/, from the 20 Nov player pack). It is made the first time it is needed.
const EAT_SCENE := "res://player_eating/eating.tscn"
var eating := false
var _eat_anim = null         # player_eating/eating.gd


func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://art/player.png")
	_sprite.hframes = 4      # columns: down, up, left, right
	_sprite.vframes = 3      # rows: standing, step A, step B
	_sprite.centered = false
	_sprite.position = Vector2(-8, -30)     # sprite frames are 16x32
	set_sheet(_sprite.texture)
	add_child(_sprite)

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


# Swaps the walk sheet (4 columns x 3 rows, any size) - used by the character screen.
func set_sheet(tex: Texture2D) -> void:
	_sprite.texture = tex
	var frame_w: float = tex.get_width() / 4.0
	_sprite.scale = Vector2.ONE * (16.0 / frame_w)


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
func fire_laser(target: Vector2, icon: int) -> void:
	face(target + Vector2(0, 8))
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


# Plays the eating animation: the food is lifted to the mouth, eaten, and the hand comes back down (0.58 s).
# look is the character-screen choices (scripts/player_maker.gd), so the animation wears the player's own
# hair, clothes and colours. food is the item's picture; null uses the pack's own small ration picture.
# Returns false, changing nothing, if it can't play just now (sitting, carrying, or already eating).
func play_eating(look: Dictionary, food: Texture2D = null) -> bool:
	if eating or sitting or carrying or look.is_empty() or not ResourceLoader.exists(EAT_SCENE):
		return false
	if _eat_anim == null:
		_eat_anim = load(EAT_SCENE).instantiate()
		_eat_anim.scale = Vector2.ONE * (2.0 / 3.0)       # 24-pixel art, like the walk sheet
		# Its cells (48x68, feet at 24,63) put the feet one art pixel higher than the walk sheet does.
		_eat_anim.position = Vector2(0, 2.0 / 3.0)
		add_child(_eat_anim)
		_eat_anim.eating_finished.connect(_eating_done)
	_eat_anim.body_type = 2 if int(look.get("body", 0)) == 1 else 1       # Female uses body 2, as in player_maker
	_eat_anim.hair_style = clampi(int(look.get("hair", 0)), 0, 9)
	_eat_anim.face_style = clampi(int(look.get("faces", 0)), 0, 9)
	_eat_anim.top_style = clampi(int(look.get("tops", 0)), 0, 9)
	_eat_anim.bottom_style = clampi(int(look.get("bottoms", 0)), 0, 9)
	_eat_anim.hair_color = _look_colour(look, "hairColor")
	_eat_anim.skin_color = _look_colour(look, "skinColor")
	_eat_anim.eye_color = _look_colour(look, "eyeColor")
	_eat_anim.top_color = _look_colour(look, "topColor")
	_eat_anim.bottom_color = _look_colour(look, "bottomColor")
	var facings: Array = [&"south", &"north", &"west", &"east"]
	var started: bool = _eat_anim.play_eating(facings[_dir]) if food == null else _eat_anim.play_eating(facings[_dir], food)
	if not started:
		return false
	eating = true
	_sprite.visible = false
	return true


# The walk sheet (4 directions x 3 poses), for pictures of the player elsewhere: the datapad's gear page.
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
	_sprite.visible = not sitting


func _process(delta: float) -> void:
	if sitting:
		sit_blend = move_toward(sit_blend,1.0,delta*5.0)
		queue_redraw()
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
	if _flash_time > 0.0:
		_flash_time -= delta
		_sprite.modulate = Color(1.0, 0.45, 0.45) if int(_flash_time * 16.0) % 2 == 0 and _flash_time > 0.0 else Color.WHITE
		if _eat_anim != null:
			_eat_anim.modulate = _sprite.modulate
	if _beam_time > 0.0:
		_beam_time -= delta
		_beam.default_color = Color(1.0, 0.35, 0.3) if int(_beam_time * 40.0) % 2 == 0 else Color(1.0, 0.85, 0.8)
		if _beam_time <= 0.0:
			_beam.visible = false
	if frozen or eating:
		_sprite.frame_coords = Vector2i(_dir, 0)
		return

	var dir: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if dir == Vector2.ZERO:
		_walk_time = 0.0
		_sprite.frame_coords = Vector2i(_dir, 0)
		return

	if absf(dir.x) > absf(dir.y):
		_dir = 2 if dir.x < 0.0 else 3
	else:
		_dir = 1 if dir.y < 0.0 else 0

	var speed: float = CARRY_SPEED if carrying else SPEED
	var step: Vector2 = dir * speed * delta
	var next_x: Vector2 = position + Vector2(step.x, 0)
	if not _blocked(next_x):
		position = next_x
	var next_y: Vector2 = position + Vector2(0, step.y)
	if not _blocked(next_y):
		position = next_y

	# Walk cycle: step A, standing, step B, standing.
	_walk_time += delta
	var cycle: Array = [1, 0, 2, 0]
	var phase: int = int(_walk_time * 8.0) % 4
	var row: int = cycle[phase]
	_sprite.frame_coords = Vector2i(_dir, row)
	# A footstep each time a foot comes down.
	if phase != _last_phase and row != 0:
		world.sfx("step", randf_range(0.85, 1.15), -9.0)
	_last_phase = phase


func _blocked(p: Vector2) -> bool:
	for off in [Vector2(-5, -6), Vector2(5, -6), Vector2(-5, 0), Vector2(5, 0)]:
		var corner: Vector2 = p + off
		if world.solid_at(corner):
			return true
	return false

# Seated pose uses the current customized character texture, articulated at hips/knees.
# Unlike moving the standing sprite behind a bench, this hides the standing legs.
var sitting := false
var sit_blend := 0.0
var seat_pants := Color("405363")
var seat_boots := Color("26313d")
func _seat_palette(row_start: int, row_end: int, fallback: Color) -> Color:
	var image := _sprite.texture.get_image()
	if image.is_compressed(): image.decompress()
	var unit: float = image.get_width()/4.0/16.0
	var votes := {}
	var best := 0
	var chosen := fallback
	for y in range(row_start,row_end):
		for x in range(4,12):
			var c := image.get_pixel(int((_dir*16+x)*unit),int(y*unit))
			if c.a<0.9: continue
			var k := c.to_html()
			votes[k] = int(votes.get(k,0))+1
			if votes[k]>best:
				best = votes[k]
				chosen = c
	return chosen
func set_sitting(value: bool, direction: int = 0) -> void:
	sitting = value
	_dir = direction
	if value:
		seat_pants = _seat_palette(21,26,seat_pants)
		seat_boots = _seat_palette(27,32,seat_boots)
	_sprite.visible = not value
	z_index = 1 if value else 0
	if not value: sit_blend = 0.0
	queue_redraw()
func _seat_piece(src: Rect2, dest: Rect2) -> void:
	var tex: Texture2D = _sprite.texture
	var unit: float = tex.get_width()/4.0/16.0
	var frame_x: float = _dir*16.0*unit
	draw_texture_rect_region(tex,dest,Rect2(Vector2(frame_x,0)+src.position*unit,src.size*unit))
func _draw() -> void:
	if not sitting or _sprite == null:return
	var lower := floorf((1.0-sit_blend)*3.0)
	draw_set_transform(Vector2(0,-lower))
	_seat_piece(Rect2(0,0,16,21),Rect2(-8,-29,16,21))
	if _dir == 0:
		# Knees project forward and outward; shins hang from the cushion.
		for x in [-7.0,1.0]:
			draw_rect(Rect2(x,-8,6,4),seat_pants)
			draw_rect(Rect2(x+1,-8,4,2),seat_pants.lightened(0.12))
			draw_rect(Rect2(x,-5,6,1),seat_pants.darkened(0.22))
			draw_rect(Rect2(x+1,-4,4,4),seat_pants.darkened(0.12))
			draw_rect(Rect2(x,0,6,3),seat_boots)
			draw_rect(Rect2(x,2,6,1),seat_boots.darkened(0.2))
	else:
		# A right-angle bend at the hip and forward-shifted shins in side view.
		var right := _dir == 3
		draw_set_transform(Vector2(0,-8-lower),-PI/2.0 if right else PI/2.0)
		_seat_piece(Rect2(4,21,8,7),Rect2(-4,0,8,7))
		draw_set_transform(Vector2(0,-lower))
		_seat_piece(Rect2(4,26,8,6),Rect2(3 if right else -11,-4,8,6))
	draw_set_transform(Vector2.ZERO)
