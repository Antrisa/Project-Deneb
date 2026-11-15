extends SceneTree

const Maker = preload("res://scripts/player_maker.gd")
var failures: Array[String] = []

func check(ok: bool, message: String) -> void:
	if not ok:
		failures.append(message)

func _initialize() -> void:
	var maker = Maker.new()
	check(maker.load_layers(), "Animated layer atlases load")
	if not failures.is_empty():
		finish()
		return
	var baseline: Image = maker.sheet(maker.defaults()).get_image()
	check(baseline.get_size() == Vector2i(128, 192), "Output size")
	baseline.save_png("res://tests/godot_player.png")
	# Every top/bottom pairing, all four directions and three poses: the waist has no air gap.
	for top in 10:
		for bottom in 10:
			var look: Dictionary = maker.defaults()
			look["tops"] = top
			look["bottoms"] = bottom
			var img: Image = maker.sheet(look).get_image()
			for pose in 3:
				for dir in 4:
					for y in range(41, 47):
						var occupied := false
						for x in range(13, 19):
							if img.get_pixel(dir * 32 + x, pose * 64 + y).a > 0.5:
								occupied = true
						check(occupied, "Waist gap: top %d bottom %d dir %d pose %d y %d" % [top, bottom, dir, pose, y])
					for y in range(62, 64):
						for x in 32:
							check(img.get_pixel(dir * 32 + x, pose * 64 + y).a == 0.0, "Foot margin")
	# All face/top pairs keep a connected neck and collar through body bobbing.
	for face in 10:
		for top in 10:
			var look: Dictionary = maker.defaults()
			look["faces"] = face
			look["tops"] = top
			var img: Image = maker.sheet(look).get_image()
			for pose in 3:
				for dir in 4:
					for y in range(25, 31):
						var occupied := false
						for x in range(11, 22):
							if img.get_pixel(dir * 32 + x, pose * 64 + y).a > 0.5:
								occupied = true
						check(occupied, "Neck gap: face %d top %d direction %d pose %d row %d" % [face, top, dir, pose, y])
	# Every top visibly changes its arms between step A and B (not just a whole-body bob).
	for top in 10:
		var look: Dictionary = maker.defaults()
		look["tops"] = top
		var layer: Image = maker._tinted("tops", look)
		for dir in 4:
			var a: Image = layer.get_region(Rect2i(dir * 32, 64 + 31, 32, 18))
			var b: Image = layer.get_region(Rect2i(dir * 32, 128 + 31, 32, 18))
			check(a.get_data() != b.get_data(), "Arm phases identical: top %d direction %d" % [top, dir])
	for bottom in 10:
		var look: Dictionary = maker.defaults()
		look["bottoms"] = bottom
		var layer: Image = maker._tinted("bottoms", look)
		for dir in 4:
			check(layer.get_region(Rect2i(dir * 32, 64 + 47, 32, 15)).get_data() != layer.get_region(Rect2i(dir * 32, 128 + 47, 32, 15)).get_data(), "Leg phases identical: bottom %d direction %d" % [bottom, dir])
	for key in Maker.PALETTES:
		var look: Dictionary = maker.defaults()
		look[key] = "#ef29c7"
		check(maker.sheet(look).get_image().get_data() != baseline.get_data(), "Color control: " + str(key))
	# Existing saved dictionaries need no migration; bad values stay bounded.
	var old: Dictionary = maker.defaults()
	check(maker.tidy(old) == old, "Existing appearance compatibility")
	check(maker.tidy({"hair": 100})["hair"] == 9, "Choice clamping")
	var creator = load("res://scripts/creator.gd").new()
	creator.maker = maker
	creator.look = maker.defaults()
	creator.row = 1  # hair colour
	creator._set_color_axis(0, 0.65)
	creator._set_color_axis(1, 0.8)
	creator._set_color_axis(2, 0.9)
	var custom: Color = Color.html(creator.look["hairColor"])
	check(absf(custom.h - 0.65) < 0.01, "Creator hue slider")
	check(absf(custom.s - 0.8) < 0.01, "Creator saturation slider")
	check(absf(custom.v - 0.9) < 0.01, "Creator lightness slider")
	check(maker.tidy(creator.look)["hairColor"] == creator.look["hairColor"], "Custom colour survives save validation")
	creator.free()
	finish()

func finish() -> void:
	if failures.is_empty():
		print("PASS: 100 clothing and 100 face/top pairs, waist/neck continuity, 40 arm and 40 leg cycles, HSV sliders, colors, dimensions and save compatibility")
	else:
		for message in failures.slice(0, 20):
			push_error(message)
		print("FAILURES: ", failures.size())
	quit(0 if failures.is_empty() else 1)
