extends SceneTree

const Maker = preload("res://scripts/player_maker.gd")
const Walk = preload("res://scripts/walk_cycle.gd")
var failures: Array[String] = []


class QuietWorld:
	func sfx(_id: String, _pitch: float, _volume: float) -> void:
		pass


func check(ok: bool, message: String) -> void:
	if not ok:
		failures.append(message)


func occupied(img: Image, xs: int, xe: int, y: int) -> bool:
	for x in range(xs, xe):
		if img.get_pixel(x, y).a > 0.5:
			return true
	return false


func check_body(maker, body: int) -> void:
	var look: Dictionary = maker.defaults()
	look.body = body
	var baseline: Image = maker.sheet(look).get_image()
	check(baseline.get_size() == Vector2i(96, 240), "Native frame size and five poses")
	for top in 10:
		look.tops = top
		# Use each possible shirt/trouser combination, with every face represented on each shirt.
		for bottom in 10:
			look.bottoms = bottom
			look.faces = bottom
			var img: Image = maker.sheet(look).get_image()
			for pose in 5:
				for dir in 4:
					var x := dir * 24
					var y := pose * 48
					var description := "body %d, top %d, bottom %d, dir %d, row %d" % [body, top, bottom, dir, pose]
					for wy in range(29, 34):
						check(occupied(img, x + 8, x + 16, y + wy), "Waist gap in " + description)
					for ny in range(18, 23):
						check(occupied(img, x + 7, x + 18, y + ny), "Neck gap in " + description)
					check(not occupied(img, x, x + 24, y + 46) and not occupied(img, x, x + 24, y + 47), "Foot margin in " + description)
	for style in 10:
		for k in ["tops", "bottoms"]:
			look[k] = style
			var layer: Image = maker._tinted(k, look)
			var y := 23 if k == "tops" else 35
			for dir in 4:
				var drawings: Array = []
				for pose in Walk.POSES:
					var box := Rect2i(dir * 24, pose * 48 + y, 24, 11)
					var drawing := layer.get_region(box).get_data()
					if not drawings.has(drawing):
						drawings.append(drawing)
				check(drawings.size() == 4, "%s %d, body %d, dir %d needs four distinct limb drawings" % [k, style, body, dir])
	for key in Maker.PALETTES:
		var custom: Dictionary = maker.defaults()
		custom.body = body
		custom[key] = "#ef29c7"
		check(maker.sheet(custom).get_image().get_data() != baseline.get_data(), "Colour control " + str(key))


func _initialize() -> void:
	var maker = Maker.new()
	if not maker.load_layers():
		push_error("Could not load player layers")
		quit(1)
		return
	check(maker.body_count() == 1, "One body for every player (24 Nov)")
	for body in maker.body_count():
		check_body(maker, body)
	var old: Dictionary = maker.defaults()
	old.erase("body")
	check(maker.tidy(old).body == 0, "Older saved look")
	check(maker.tidy({"hair": 100}).hair == 9, "Choice clamping")
	var creator = preload("res://scripts/creator.gd").new()
	creator.maker = maker
	creator.world = QuietWorld.new()
	creator.show_for(maker.defaults(), true)
	creator._change(0, 1)
	check(creator.look == maker.defaults(1), "Second starter has the tunic and ponytail from the reference")
	creator._change(0, -1)
	check(creator.look == maker.defaults(0), "First starter restores its jacket and crop")
	creator.look.hairColor = "#37988b"
	creator._change(0, 1)
	check(creator.look.hairColor == "#37988b" and creator.look.tops == 2, "Custom hair and outfit survive a body switch")
	creator.show_for(maker.defaults(), false)
	creator._change(0, 1)
	check(creator.look.tops == 2 and creator.look.hair == 0, "Locker keeps the saved wardrobe")
	creator._use_starter()
	check(creator.look == maker.defaults(1), "Locker can apply the matching starter look to an existing save")
	var legacy := {"body": 1, "topColor": "#578d99", "hair": 7, "tops": 8}
	check(maker.tidy(legacy).topColor == legacy.topColor and maker.tidy(legacy).tops == 8 and maker.tidy(legacy).hair == 7, "Explicit saved choices survive new presets")
	creator.show_for(maker.defaults(), false)
	creator.row = creator._rows.find(["hairColor", "Hair colour"])
	creator._set_color_axis(0, 0.65)
	creator._set_color_axis(1, 0.8)
	creator._set_color_axis(2, 0.9)
	var colour := Color.html(creator.look.hairColor)
	check(absf(colour.h - 0.65) < 0.01 and absf(colour.s - 0.8) < 0.01 and absf(colour.v - 0.9) < 0.01, "Creator HSV sliders")
	check(maker.tidy(creator.look).hairColor == creator.look.hairColor, "Saving a custom colour")
	creator.free()
	for message in failures.slice(0, 15):
		push_error(message)
	if failures.is_empty():
		print("PASS: 200 clothing combinations across two bodies, four directions and five rows, limb articulation, colours and save compatibility.")
	else:
		print("Failures: ", failures.size())
	quit(0 if failures.is_empty() else 1)
