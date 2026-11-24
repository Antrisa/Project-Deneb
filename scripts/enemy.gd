extends Sprite2D
# A cave creature. It wanders near where it started, chases the player when they come close,
# and bites on contact. Where they start is set in tools/build.py (ENEMIES).

const KINDS := {
	"bug": {"art": "res://art/enemy_bug.png", "w": 16.0, "hp": 2, "speed": 34.0, "damage": 1, "drop": "chitin", "sight": 70.0},
	"lizard": {"art": "res://art/enemy_lizard.png", "w": 16.0, "hp": 4, "speed": 24.0, "damage": 2, "drop": "hide", "sight": 90.0},
	"spore_crawler": {"art": "res://art/enemy_spore_crawler.png", "w": 16.0, "hp": 3, "speed": 30.0, "damage": 1, "drop": "chitin", "sight": 80.0},
	"vent_crab": {"art": "res://art/enemy_vent_crab.png", "w": 16.0, "hp": 5, "speed": 26.0, "damage": 2, "drop": "hide", "sight": 85.0},
	# A flier (23 Nov), like Stardew's bats: flies straight through walls, rocks and props (only the map's edge stops
	# it), and once it has seen you it never gives up, flitting at you on a jittery zigzag that overshoots and loops back.
	"echo_bat": {"art": "res://art/enemy_echo_bat.png", "w": 16.0, "hp": 3, "speed": 46.0, "damage": 1, "drop": "hide", "sight": 110.0, "fly": true},
	"harbinger": {"art": "res://art/enemy_harbinger.png", "w": 16.0, "hp": 40, "speed": 22.0, "damage": 3, "drop": "harbinger_scale", "sight": 420.0},
}

var world                    # main.gd
var kind := ""
var area := ""
var home := Vector2.ZERO
var hp := 1
var alive := true

var _info: Dictionary = {}
var _wander := Vector2.ZERO
var _wander_time := 0.0
var _hurt_time := 0.0
var _bite_time := 0.0
var _knock := Vector2.ZERO
var _anim := 0.0
var _dir := 0                # 0 down, 1 up, 2 left, 3 right (the sheet's columns)
var _walked := 0.0           # distance walked, for the walk cycle
var _fly := false            # a flier: passes over rocks and props, flaps by time, bobs in the air
var _base_offset := Vector2.ZERO
var _vel := Vector2.ZERO     # a flier's current velocity (it steers, so it drifts and overshoots)
var _aim := Vector2.ZERO     # the velocity it is currently steering towards
var _jitter := 0.0           # time left before it picks a new zigzag heading
var _aggro := false          # a flier that has seen you chases you until you leave the floor
const WalkCycle := preload("res://scripts/walk_cycle.gd")


func setup(main, enemy_kind: String, area_name: String, start: Vector2) -> void:
	world = main
	kind = enemy_kind
	area = area_name
	home = start
	_info = KINDS[kind]
	texture = load(_info["art"])
	# Laid out like the residents' sheets (23 Nov): four columns (down, up, left, right) and five rows
	# (standing, then the walk). A frame is drawn "w" units wide (the art is 24 pixels a tile; the Harbinger's
	# sheet is drawn for four times its "w", since boost() makes it four times bigger).
	hframes = 4
	vframes = 5
	centered = false
	var fw: float = texture.get_width() / 4.0
	var fh: float = texture.get_height() / 5.0
	var k: float = float(_info.get("w", 16.0)) / fw
	scale = Vector2(k, k)
	offset = Vector2(-fw * 0.5, -(fh - 2.0))       # centred, feet at the bottom
	_base_offset = offset
	_fly = bool(_info.get("fly", false))
	if _fly:
		z_index = 1          # drawn over the walls it flies through (and over the overhead wall tops)
	if get_node_or_null("Shadow") == null:          # a soft ground shadow, like the residents'
		var sh: Sprite2D = preload("res://scripts/prop_fx.gd").make_shadow(int(fw * 0.75), Vector2(0, -1.0 / k), Vector2.ONE * (2.0 / 3.0) / k)
		sh.name = "Shadow"
		add_child(sh)
	reset()


# Deeper in the caverns: tougher, harder-biting and bigger (main.gd CAV_POWER).
func boost(hp_mult: float, extra_damage: int, size: float) -> void:
	_info = _info.duplicate()
	_info["hp"] = maxi(1, int(round(float(_info["hp"]) * hp_mult)))
	_info["damage"] = int(_info["damage"]) + extra_damage
	scale *= size
	reset()


# Back to full health at its starting spot (each morning, and after the player collapses).
func reset() -> void:
	alive = true
	hp = int(_info["hp"])
	position = home
	_aggro = false
	_vel = Vector2.ZERO
	modulate = Color.WHITE
	_knock = Vector2.ZERO
	_hurt_time = 0.0
	_bite_time = 0.0


func drop_item() -> String:
	var item: String = _info["drop"]
	return item


func tick(delta: float) -> void:
	visible = alive and area == world.current_area
	if not visible:
		return
	_anim += delta
	_bite_time = maxf(0.0, _bite_time - delta)
	if _hurt_time > 0.0:
		_hurt_time -= delta
		modulate = Color(1.0, 0.5, 0.5) if int(_hurt_time * 20.0) % 2 == 0 else Color.WHITE
	else:
		modulate = Color.WHITE

	var ppos: Vector2 = world.player.position
	var to_player: Vector2 = ppos - position
	var dist: float = to_player.length()
	var speed: float = _info["speed"]
	var sight: float = _info["sight"]
	var move := Vector2.ZERO
	if _fly and _knock.length() <= 2.0:
		move = _fly_move(delta, to_player, dist, speed, sight)
	elif _knock.length() > 2.0:
		# Knocked back by a hit.
		move = _knock
		_knock = _knock.lerp(Vector2.ZERO, minf(1.0, delta * 8.0))
		if _fly:
			_vel = move          # a bat you hit tumbles away, then picks up its chase from there
	elif dist < sight:
		if dist > 8.0:
			move = to_player.normalized() * speed
	else:
		_wander_time -= delta
		if _wander_time <= 0.0:
			_wander_time = randf_range(0.8, 2.2)
			if position.distance_to(home) > 40.0:
				_wander = (home - position).normalized() * speed * 0.5
			elif randf() < 0.5:
				_wander = Vector2.ZERO
			else:
				_wander = Vector2.from_angle(randf() * TAU) * speed * 0.5
		move = _wander

	_step(move * delta)
	if _fly:
		# always flapping (rows 1-4 in turn), facing the way it last moved, bobbing a pixel or two in the air
		if move.length() > 1.0:
			if absf(move.x) > absf(move.y):
				_dir = 2 if move.x < 0.0 else 3
			else:
				_dir = 1 if move.y < 0.0 else 0
		frame_coords = Vector2i(_dir, 1 + int(_anim * 10.0) % 4)
		offset = _base_offset + Vector2(0, sin(_anim * 4.0) * 1.5)
		var sh: Node2D = get_node_or_null("Shadow")
		if sh != null:
			sh.visible = not world.wall_at(position)     # no shadow on top of a wall it is crossing
	elif move.length() > 1.0:
		if absf(move.x) > absf(move.y):
			_dir = 2 if move.x < 0.0 else 3
		else:
			_dir = 1 if move.y < 0.0 else 0
		_walked += move.length() * delta
		frame_coords = Vector2i(_dir, WalkCycle.pose(WalkCycle.phase(_walked), 5))
	else:
		frame_coords = Vector2i(_dir, 0)

	if dist < 11.0 and _bite_time <= 0.0 and _hurt_time <= 0.0:
		_bite_time = 0.9
		var damage: int = _info["damage"]
		world.hurt_player(damage, position)


# How a flier moves: flutters in loose loops round where it started until it sees you, then chases you for good,
# steering towards a new, jittery heading every fraction of a second (sometimes with a burst of speed).
func _fly_move(delta: float, to_player: Vector2, dist: float, speed: float, sight: float) -> Vector2:
	if not _aggro and dist < sight:
		_aggro = true
	if _aggro:
		_jitter -= delta
		if _jitter <= 0.0:
			_jitter = randf_range(0.12, 0.4)
			var burst: float = randf_range(0.7, 1.6) if randf() < 0.8 else 2.2
			_aim = to_player.normalized().rotated(randf_range(-1.2, 1.2)) * speed * burst
		_vel = _vel.lerp(_aim, minf(1.0, delta * 4.0))
	else:
		var loop := Vector2(cos(_anim * 1.3), sin(_anim * 2.1)) * speed * 0.35
		if position.distance_to(home) > 30.0:
			loop += (home - position).normalized() * speed * 0.4
		_vel = _vel.lerp(loop, minf(1.0, delta * 3.0))
	return _vel


func _step(v: Vector2) -> void:
	var next_x: Vector2 = position + Vector2(v.x, 0)
	if not _blocked(next_x):
		position = next_x
	var next_y: Vector2 = position + Vector2(0, v.y)
	if not _blocked(next_y):
		position = next_y


func _blocked(p: Vector2) -> bool:
	for off in [Vector2(-4, -5), Vector2(4, -5), Vector2(-4, 0), Vector2(4, 0)]:
		var corner: Vector2 = p + off
		if (world.outside_map(corner) if _fly else world.solid_at(corner)):
			return true
	return false


# Called by main.gd when a weapon swing lands. push is the direction of the blow.
func hurt(amount: int, push: Vector2) -> void:
	if not alive:
		return
	hp -= amount
	_hurt_time = 0.25
	_knock = push * 140.0
	if hp <= 0:
		alive = false
		visible = false
		world.enemy_died(self)
	else:
		world.sfx("hit", randf_range(0.9, 1.1))
		if randf() < 0.5 and kind.contains("bug"):
			world.sfx("bug_noise", randf_range(0.9, 1.15), -4.0)
