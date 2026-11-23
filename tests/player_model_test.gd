extends SceneTree
const Maker = preload("res://scripts/player_maker.gd")
const Poses = preload("res://scripts/player_poses.gd")
const Player = preload("res://scripts/player.gd")
const Eating = preload("res://player_eating/eating.gd")
var failures: Array[String] = []
var bites := 0


func check(ok: bool, message: String) -> void:
	if not ok:
		failures.append(message)


func same_visible(a: Image, b: Image) -> bool:
	if a.get_size() != b.get_size():
		return false
	var size := a.get_size()
	for y in size.y:
		for x in size.x:
			var v := a.get_pixel(x, y)
			var other := b.get_pixel(x, y)
			if v.a != other.a or (v.a > 0 and v != other):
				return false
	return true


# Compare the game composite to the independently sampled turnaround. Colour ramps
# are reduced at native scale, and the brows, eyes and two-pixel mouth are hand keyed.
func check_reference(maker, body: int, reference: Image) -> void:
	var walk: Image = maker.sheet(maker.defaults(body)).get_image()
	for dir in 4:
		var key: int = [0, 1, 2, 2][dir]
		var source := reference.get_region(Rect2i(key * 24, body * 48, 24, 48))
		if dir == 2:
			source.flip_x()
		var sample := walk.get_region(Rect2i(dir * 24, 0, 24, 48))
		var mismatch := 0
		var channel_error := 0
		var pixels := 0
		for y in 48:
			for x in 24:
				var a := sample.get_pixel(x, y)
				var b := source.get_pixel(x, y)
				if a.a8 != b.a8:
					mismatch += 1
				elif b.a8 > 0:
					channel_error += absi(a.r8-b.r8) + absi(a.g8-b.g8) + absi(a.b8-b.b8)
					pixels += 1
		check(mismatch == 0, "Turnaround silhouette, body %d direction %d" % [body,dir])
		check(pixels > 0 and channel_error <= 8 * 3 * pixels, "Turnaround colours, body %d direction %d" % [body,dir])


# Catch a one-pixel break between the lifted shoe and a slim trouser leg or between a sleeve and hand.
func connected(cell: Image) -> bool:
	var w := cell.get_width()
	var h := cell.get_height()
	var opaque := PackedByteArray()
	opaque.resize(w * h)
	var total := 0
	var pending: Array[int] = []
	for y in h:
		for x in w:
			if cell.get_pixel(x, y).a > 0.5:
				opaque[y*w+x] = 1
				total += 1
				if pending.is_empty():
					pending.append(y*w+x)
	if total == 0:
		return false
	opaque[pending[0]] = 0
	var visited := 0
	while not pending.is_empty():
		var index: int = pending.pop_back()
		visited += 1
		var x := index % w
		var y := index / w
		for ny in range(maxi(0,y-1), mini(h,y+2)):
			for nx in range(maxi(0,x-1), mini(w,x+2)):
				var n := ny*w+nx
				if opaque[n]:
					opaque[n] = 0
					pending.append(n)
	return visited == total


func check_watering(player: Player, dir: int) -> void:
	var tank_centres := [Vector2(0, 3), Vector2.ZERO, Vector2(0, 9), Vector2(0, 9)]
	var rows := [Poses.WATER_GATHER, Poses.WATER_RAISE, Poses.WATER_READY, Poses.POUR, Poses.WATER_RAISE, Poses.WATER_GATHER]
	var times := [0.02, 0.20, 0.37, 0.65, 0.84, 0.96]
	for tier in ["basic", "steel", "titanium", "precursor"]:
		check(player.tool_action("watering_can_" + tier, "water"), "Watering starts with the " + tier + " can")
		var before := 0.0
		for i in rows.size():
			var t: float = times[i]
			player._process((t - before) * Player.HELD_LEN)
			before = t
			var row: int = rows[i]
			check(player._action_body.frame_coords == Vector2i(dir, row), "Watering phase %d, direction %d" % [i,dir])
			var hand := Poses.world_grip(row, dir)
			var rim := player.to_local(player._held.to_global(player._held.offset + Poses.CAN_RIM[dir]))
			check(rim.is_equal_approx(hand), "Can handle stays on the palm")
			check(Poses.head_offset(row, dir) == Vector2i.ZERO, "Watering head stays at standing position")
			var tank: Vector2 = player._held.to_global(player._held.offset + tank_centres[dir])
			var native := player.to_local(tank) / Poses.ART_SCALE + Vector2(Poses.FOOT)
			check(native.y >= 15 and native.y <= 34, "Watering can stays at chest height")
			if dir >= 2:
				var lead := native.x if dir == 3 else 23.0 - native.x
				check(lead >= 21, "Can stays ahead of the face in profile")
				check(player._water_arm.visible and player._water_arm.get_index() > player._held.get_index(), "Near arm wraps over the can")
				check(player._water_arm.transform.is_equal_approx(player._action_body.transform), "Forearm and body share one pivot")
			elif dir == 1:
				check(native.x <= 8 and not player._water_arm.visible, "Back view shows the can beyond the shoulder")
		player._process(0.1)
		check(player._sprite.visible and not player._held.visible and not player._water_arm.visible, "Can and arm overlay return to idle")


func _initialize() -> void:
	call_deferred("run")


func run() -> void:
	var maker := Maker.new()
	if not maker.load_layers():
		push_error("Player layers could not be loaded")
		quit(1)
		return
	var player := Player.new()
	root.add_child(player)
	player.set_process(false)
	player.frozen = true
	var base := maker.defaults()
	var fallback: Texture2D = load("res://art/player.png")
	var fallback_actions: Texture2D = load("res://art/player_actions.png")
	check(same_visible(fallback.get_image(), maker.sheet(base).get_image()), "Default walk and fallback agree")
	var starter_sheet := maker.action_sheet(base) as Poses.ActionSheet
	check(same_visible(fallback_actions.get_image(), starter_sheet.get_image()), "Default action poses and fallback agree")
	check(same_visible(player._water_arm.texture.get_image(), starter_sheet.watering_arms.get_image()), "Default foreground sleeve and fallback agree")
	var reference := Image.new()
	if reference.load("res://docs/player_turnaround_24x48.png") != OK:
		push_error("Player turnaround reference is missing")
		player.free()
		quit(1)
		return
	for body in 2:
		check_reference(maker, body, reference)
		for style in 10:
			var look := maker.defaults()
			look.body = body
			look.tops = style
			look.bottoms = style
			look.hair = style
			var walk := maker.sheet(look)
			var actions := maker.action_sheet(look)
			check(actions != null and actions.get_size() == Vector2(96, 48 * Poses.COUNT), "All player action rows load")
			if actions == null:
				continue
			var walking := walk.get_image()
			var working := actions.get_image()
			var arm_sheet: Image = (actions as Poses.ActionSheet).watering_arms.get_image()
			for i in Poses.WATER_ROWS.size():
				var row: int = Poses.WATER_ROWS[i]
				for d in 4:
					var crown := Rect2i(d * 24, 0, 24, 16)
					var active := Rect2i(crown.position + Vector2i(0, row * 48), crown.size)
					check(same_visible(walking.get_region(crown), working.get_region(active)), "Crown and eyes stay level throughout watering")
					if d >= 2:
						var arm := arm_sheet.get_region(Rect2i(d * 24, i * 48, 24, 48))
						check(connected(arm) and arm.get_pixelv(Poses.hand(row,d)).a > 0.99, "One continuous sleeve from shoulder to gripping hand")
						check(arm.get_region(Rect2i(10, 21, 5, 4)).get_used_rect().has_area(), "Visible sleeve is attached at the shoulder")
			# Clothing and feet stay registered when a moving player picks up a box.
			for row in 5:
				for d in 4:
					var cell := Rect2i(d*24, row*48, 24, 48)
					check(connected(walking.get_region(cell)), "Disconnected walk pixels, body %d style %d direction %d row %d" % [body,style,d,row])
				var lower_legs := Rect2i(0, row*48+38, 96, 8)
				check(same_visible(walking.get_region(lower_legs), working.get_region(lower_legs)), "Carry feet %d %d %d" % [body,style,row])
			# Check each outfit and its mask as the eating scene returns to idle.
			var folder := "res://art/player/" if body == 0 else "res://art/player/body2/"
			for i in 4:
				for m in 2:
					var suffix := "_mask" if m == 1 else ""
					var regular: Image = load(folder + str(Eating.LAYERS[i]) + suffix + ".png").get_image()
					var eat: Image = Eating.ATLAS[body][i][m].get_image()
					for dir in 4:
						var standing := regular.get_region(Rect2i(dir*24,style*240,24,48))
						var final_eat := eat.get_region(Rect2i(dir*48+12,(style*4+3)*68+17,24,48))
						check(same_visible(standing, final_eat), "Eating registration %d %d %s %d" % [body,style,Eating.LAYERS[i],dir])
			if style != 4:
				continue
			player.set_sheet(walk, actions)
			for dir in 4:
				player._dir = dir
				player.set_carrying(true)
				check(player._action_body.visible and not player._sprite.visible and player._crate.visible, "Carrying uses posed model")
				player._process(0.001)
				check(player._action_body.frame_coords == Vector2i(dir,0), "Carry facing")
				player.set_carrying(false)
				check(player.tool_action("hoe_basic","hoe"), "Hoe starts")
				player._process(0.12)
				check(player._action_body.frame_coords == Vector2i(dir, Poses.LIFT) and player._held.position.is_equal_approx(Poses.world_grip(Poses.LIFT, dir)), "Hands match lifted hoe")
				player._process(0.17)
				check(player._action_body.frame_coords == Vector2i(dir, Poses.STRIKE), "Lowered hoe")
				player._process(0.3)
				check_watering(player, dir)
				check(player.tool_action("mining_laser_basic","laser"), "Laser starts")
				check(player._action_body.frame_coords == Vector2i(dir, Poses.BRACE) and player._held.offset == Vector2.ZERO, "Laser grip resets after watering")
				player._process(0.06)
				var emitter: Vector2 = Poses.world_grip(Poses.RECOIL, dir) + player.LASER_EMITTER[dir] * Poses.ART_SCALE
				check(player._action_body.frame_coords.y == Poses.RECOIL and player._beam.get_point_position(0).is_equal_approx(emitter), "Laser and beam recoil together")
				player._process(0.5)
				check(player.tool_action("scythe","scythe"), "Scythe starts")
				check(player._action_body.frame_coords == Vector2i(dir, Poses.WINDUP), "Shoulders turn on the backswing")
				player._dir = (dir + 1) % 4
				for row in [Poses.SWEEP, Poses.FOLLOW, Poses.RECOVER]:
					player._process(0.16 if row == Poses.SWEEP else 0.13)
					check(player._action_body.frame_coords == Vector2i(dir, row) and player._held.position.is_equal_approx(Poses.world_grip(row, dir)), "Scythe stays with the striking hand")
				player._process(0.2)
				player._dir = dir
				player.show_pickup(fallback)
				check(player._action_body.frame_coords == Vector2i(dir, Poses.REACH) and not player._held.visible, "Torso bends to collect the crop")
				player._process(0.35)
				check(player._held.visible and player._action_body.frame_coords == Vector2i(dir, Poses.SHOW_ITEM), "Both hands lift the crop overhead")
				var base_y := player._held.position.y + player._held.texture.get_height()*player._held.scale.y/2.0
				check(is_equal_approx(base_y, (5 - Poses.FOOT.y) * Poses.ART_SCALE), "Crop rests on overhead hands")
				player._process(0.35)
				check(player._sprite.visible and not player._held.visible, "Harvest returns to walking")
				check(player.play_eating(look), "Eating starts")
				var eat_anim = player._eat_anim
				if not eat_anim.bite.is_connected(_count_bite):
					eat_anim.bite.connect(_count_bite)
				check(eat_anim.body_type == body+1 and not player._action_body.visible and not player._sprite.visible, "Eating body and layer visibility")
				check(eat_anim._layers[4].frame_coords == Vector2i(dir,style*4), "Raised sleeve follows shirt style")
				eat_anim._process(0.35)
				check(not eat_anim.food.visible and eat_anim._frame == 2, "Bite hides the item")
				eat_anim._process(0.3)
				check(player._sprite.visible and not player._action_body.visible and not player.eating, "Returns to walking model")
	check(bites == 8, "One bite per facing and body")
	player.set_sitting(true, 0)
	check(not player._sprite.visible and not player._action_body.visible, "Seated body drawn only once")
	player.set_sitting(false)
	var old_sheet := ImageTexture.create_from_image(fallback_actions.get_image().get_region(Rect2i(0, 0, 96, 48 * Poses.LEGACY_COUNT)))
	player.set_sheet(fallback, old_sheet)
	check(player.tool_action("watering_can_basic", "water"), "Older eight-row actions still play")
	player._process(0.2)
	check(player._action_body.frame_coords.y == Poses.LEGACY_ROWS[Poses.POUR], "Legacy watering grip stays within the sheet")
	var previous_sheet := ImageTexture.create_from_image(fallback_actions.get_image().get_region(Rect2i(0, 0, 96, 48 * Poses.PREVIOUS_COUNT)))
	player.set_sheet(fallback, previous_sheet)
	check(player.tool_action("watering_can_basic", "water"), "Previous seventeen-row hand positions still load")
	player._process(0.2)
	check(player._action_body.frame_coords.y == Poses.POUR and player._held.offset == Vector2.ZERO and player._held.position.is_equal_approx(Poses.world_grip(Poses.POUR, player._dir, Poses.PREVIOUS_COUNT)), "Original waist-height grip stays on the previous atlas")
	player.free()
	for message in failures.slice(0,12):
		push_error(message)
	if failures.is_empty():
		print("PASS: both models, ten outfits, five carry rows, all four directions, hoe, forward pouring with a level head and connected profile arms, scythe, hand harvest, laser recoil, eating and legacy poses.")
	quit(0 if failures.is_empty() else 1)


func _count_bite() -> void:
	bites += 1
