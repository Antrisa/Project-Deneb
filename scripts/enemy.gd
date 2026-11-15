extends Sprite2D
# A cave creature. It wanders near where it started, chases the player when they come close,
# and bites on contact. Where they start is set in tools/build.py (ENEMIES).

const KINDS := {
	"bug": {"art": "res://art/enemy_bug.png", "hp": 2, "speed": 34.0, "damage": 1, "drop": "chitin", "sight": 70.0},
	"lizard": {"art": "res://art/enemy_lizard.png", "hp": 4, "speed": 24.0, "damage": 2, "drop": "hide", "sight": 90.0},
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


func setup(main, enemy_kind: String, area_name: String, start: Vector2) -> void:
	world = main
	kind = enemy_kind
	area = area_name
	home = start
	_info = KINDS[kind]
	texture = load(_info["art"])
	hframes = 2
	centered = false
	offset = Vector2(-8, -14)
	reset()


# Back to full health at its starting spot (each morning, and after the player collapses).
func reset() -> void:
	alive = true
	hp = int(_info["hp"])
	position = home
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
	if _knock.length() > 2.0:
		# Knocked back by a hit.
		move = _knock
		_knock = _knock.lerp(Vector2.ZERO, minf(1.0, delta * 8.0))
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
	if absf(move.x) > 0.5:
		flip_h = move.x > 0.0        # the art faces left
	frame = int(_anim * 6.0) % 2 if move.length() > 1.0 else 0

	if dist < 11.0 and _bite_time <= 0.0 and _hurt_time <= 0.0:
		_bite_time = 0.9
		var damage: int = _info["damage"]
		world.hurt_player(damage, position)


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
		if world.solid_at(corner):
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
