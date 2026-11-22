extends Control
# The ship screens' drawing surface (21 Nov 2026): one 768 x 432 page in the Terran field-datapad style, used by
# the battle (scripts/ship_battle.gd), the jump map (ship_map.gd), the event window (ship_event.gd) and the store
# (ship_store.gd). Zachary picked the Space UI pack's look for these screens; its parts (housing, panel liner,
# icons, fonts) are the datapad's own, in datapad/art, so the screens draw from those.
#
# It draws the way the datapad does (datapad/datapad.gd): the page is fitted to the window with whole-pixel steps
# where it can be (ui/pixel_grid.gd), and composed off-screen at the screen's own pixel size, so pixel art stays
# hard-edged and text is drawn sharp with a real font.
#
# A screen owns one of these, sets paint (called on every redraw to fill the page with the helpers below) and
# on_click (id, page position, mouse button), and calls redraw() each frame while it's open. Positions are page
# pixels: (0, 0) is the top-left of the 768 x 432 page. hit(id, rect) makes a clickable area; button() and
# solid_button() add their own.

const Art = preload("res://datapad/art.gd")
const PixelGrid = preload("res://ui/pixel_grid.gd")

const DESIGN := Vector2(768, 432)
const INK := Color("373b36")
const MUTED := Color("595e55")
const RULE := Color("cbc7ba")
const OCHRE := Color("a45736")
const ORANGE := Color("ac5c36")
const IVORY := Color("fffdf7")
const SPACE := Color("10151f")
const SCOPE_TEXT := Color("bac9b0")
const HOSTILE_TEXT := Color("dec49b")
const PIP_ON := Color("6e9a76")
const PIP_OFF := Color("d6d1c4")
const PIP_RED := Color("c6403a")
const SHIELD := Color("6fb0c6")
# The scope's own rows of text (the case is drawn from housing.png, 720 x 406, at 24, 13).
const STATUS_Y := 391

# Text: as datapad.gd, a real font at the screen's pixel size, measured with the bitmap fonts' advances.
const TEXT_SIZE := {"label": 11.2, "body": 12.6, "strong": 14.0, "mid": 18.2, "title": 25.2, "clock": 21.0}
const TEXT_BASE := {"label": 12, "body": 14, "strong": 15, "mid": 20, "title": 27, "clock": 20}
const TEXT_BOLD := ["strong", "title", "clock"]

var paint: Callable = Callable()       # fills the page
var on_click: Callable = Callable()    # (id: String, at: Vector2, button: int); id is "" off the hit areas
var mouse := Vector2(-99, -99)          # the pointer, in page pixels
var hover_id := ""
var cmds: Array = []
var hits: Array = []                    # [id, Rect2]

# Fill mode (Zachary, 22 Nov: "we need all the space we can get"): the page grows to fill the window at a whole
# number of screen pixels per page pixel, instead of a 768 x 432 page with bars round it. page is its size then.
var fill := false
var page := DESIGN
var _off := Vector2.ZERO                # shift(): everything drawn and every hit area moves by this

var _layout := Transform2D.IDENTITY
var _bounds := Rect2i(0, 0, 768, 432)
var _px := 1.0
var _target := SubViewport.new()
var _raster := Node2D.new()
var _font: Font
var _font_bold: Font
var _scopes := {}
var _stars: Texture2D


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_target.disable_3d = true
	_target.transparent_bg = true
	_target.gui_disable_input = true
	_target.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	_target.render_target_update_mode = SubViewport.UPDATE_DISABLED
	add_child(_target)
	_target.add_child(_raster)
	_raster.draw.connect(_paint_native)
	_font = ThemeDB.fallback_font
	var bold := FontVariation.new()
	bold.base_font = _font
	bold.variation_embolden = 0.6
	_font_bold = bold
	var composite := CanvasItemMaterial.new()
	composite.blend_mode = CanvasItemMaterial.BLEND_MODE_PREMULT_ALPHA
	material = composite
	_stars = _star_texture()


# Screen pixels per page pixel.
func px() -> float:
	return _px


func redraw() -> void:
	if not is_node_ready() or not is_inside_tree():
		return
	if fill:
		var device := PixelGrid.to_pixels(self)
		var available := size * device.get_scale().abs()
		var fit := minf(available.x / DESIGN.x, available.y / DESIGN.y)
		var step := floorf(fit + 0.00001) if fit >= 1.99999 else maxf(fit, 0.01)
		page = (available / step).floor()
		var start := (device.origin + (available - page * step) * 0.5).round()
		_layout = device.affine_inverse() * Transform2D(0.0, Vector2.ONE * step, 0.0, start)
	else:
		page = DESIGN
		_layout = PixelGrid.layout(self)
	var extent := _layout.affine_inverse() * Rect2(Vector2.ZERO, size)
	var first := Vector2i(extent.position.floor())
	var last := Vector2i(extent.end.ceil())
	_bounds = Rect2i(first, (last - first).max(Vector2i.ONE))
	_px = maxf(1.0, (get_viewport_transform() * get_global_transform() * _layout).get_scale().x)
	var native := Vector2i((Vector2(_bounds.size) * _px).ceil())
	if _target.size != native:
		_target.size = native
	_raster.scale = Vector2(_px, _px)
	_raster.position = -Vector2(_bounds.position) * _px
	cmds.clear()
	hits.clear()
	_off = Vector2.ZERO
	if paint.is_valid():
		paint.call()
	_raster.queue_redraw()
	_target.render_target_update_mode = SubViewport.UPDATE_ONCE
	queue_redraw()


func _draw() -> void:
	if not is_instance_valid(_target) or not _target.is_inside_tree():
		return
	draw_set_transform_matrix(_layout)
	draw_texture_rect(_target.get_texture(), Rect2(_bounds), false)


func _gui_input(event: InputEvent) -> void:
	var mouse_event := event as InputEventMouse
	if mouse_event == null:
		return
	mouse = _layout.affine_inverse() * mouse_event.position
	hover_id = hit_at(mouse)
	var press := event as InputEventMouseButton
	if press != null and press.pressed:
		accept_event()
		if on_click.is_valid():
			on_click.call(hover_id, mouse, press.button_index)


func hit_at(p: Vector2) -> String:
	for j in range(hits.size() - 1, -1, -1):
		if (hits[j][1] as Rect2).has_point(p):
			return str(hits[j][0])
	return ""


func hit(id: String, r: Rect2) -> void:
	hits.append([id, Rect2(r.position + _off, r.size)])


func hovering(r: Rect2) -> bool:
	return Rect2(r.position + _off, r.size).has_point(mouse)


# In fill mode the status line and the button at its right end sit along the bottom of the page: shift() by these
# before drawing them as designed (status() at x 61, a button at x 625..707, y 388).
func bottom_left() -> Vector2:
	return Vector2(12.0 - 53.0, page.y - 418.0)


func bottom_right() -> Vector2:
	return Vector2(page.x - 14.0 - 707.0, page.y - 418.0)


# Move everything drawn after this (and its hit areas) by o page pixels, until the next shift(); shift(Vector2.ZERO)
# puts it back. Lets a screen lay out a block of its page as designed and then place the block anywhere.
func shift(o: Vector2) -> void:
	_off = o


# Snap a page position to the screen's pixel grid, so pixel art drawn there lines up with screen pixels.
func snap(p: Vector2) -> Vector2:
	return (p * _px).round() / _px


# The biggest scale at which a picture of this size fits the area, keeping each art pixel a whole number of screen
# pixels (2x, 1.5x at a 2x screen, and so on). Only a picture too big for one screen pixel per art pixel gets a
# fractional shrink. most: the largest scale wanted (0 for no limit).
func fit_scale(picture: Vector2, area: Vector2, most: float = 0.0) -> float:
	if picture.x <= 0.0 or picture.y <= 0.0:
		return 1.0
	var fit: float = minf(area.x / picture.x, area.y / picture.y)
	if most > 0.0:
		fit = minf(fit, most)
	if fit * _px >= 1.0:
		return floorf(fit * _px + 0.0001) / _px
	return fit


# A picture fitted into an area and centred there: picture pixels -> page pixels.
func fit_into(picture: Vector2, area: Rect2, margin: float = 0.0, most: float = 0.0) -> Transform2D:
	var s: float = fit_scale(picture, area.size - Vector2(margin, margin) * 2.0, most)
	var top_left: Vector2 = snap(area.position + (area.size - picture * s) / 2.0)
	return Transform2D(0.0, Vector2(s, s), 0.0, top_left)


# ---------------------------------------------------------------- drawing commands

func rect(r: Rect2, col: Color) -> void:
	if r.size.x > 0.0 and r.size.y > 0.0:
		cmds.append(["r", Rect2(r.position + _off, r.size), col])


func outline(r: Rect2, col: Color, thick: float = 1.0) -> void:
	rect(Rect2(r.position, Vector2(r.size.x, thick)), col)
	rect(Rect2(r.position + Vector2(0, r.size.y - thick), Vector2(r.size.x, thick)), col)
	rect(Rect2(r.position, Vector2(thick, r.size.y)), col)
	rect(Rect2(r.position + Vector2(r.size.x - thick, 0), Vector2(thick, r.size.y)), col)


func line(a: Vector2, b: Vector2, col: Color, thick: float = 1.0) -> void:
	cmds.append(["l", a + _off, b + _off, col, thick])


func circle(c: Vector2, radius: float, col: Color) -> void:
	cmds.append(["c", c + _off, radius, col])


func ring(c: Vector2, radius: float, col: Color, thick: float = 1.0) -> void:
	cmds.append(["a", c + _off, radius, col, thick])


func ellipse(c: Vector2, radii: Vector2, col: Color, thick: float = 1.0) -> void:
	cmds.append(["e", c + _off, radii, col, thick])


func polygon(points: PackedVector2Array, col: Color) -> void:
	if points.size() >= 3:
		cmds.append(["p", _moved(points), col])


func polyline(points: PackedVector2Array, col: Color, thick: float = 1.0) -> void:
	if points.size() >= 2:
		cmds.append(["pl", _moved(points), col, thick])


func _moved(points: PackedVector2Array) -> PackedVector2Array:
	if _off == Vector2.ZERO:
		return points
	var out := PackedVector2Array()
	for v in points:
		out.append(v + _off)
	return out


# A texture, or part of one (src), drawn into a page rectangle.
func texture(tex: Texture2D, dest: Rect2, src: Rect2 = Rect2(), col: Color = Color.WHITE) -> void:
	if tex != null:
		cmds.append(["tx", tex, Rect2(dest.position + _off, dest.size), src, col])


# A picture drawn through a transform (picture pixels -> page), so it can turn and flip: pieces of a ship breaking
# up. src: the part of the picture (all of it when empty).
func texture_xf(tex: Texture2D, xf: Transform2D, src: Rect2 = Rect2(), col: Color = Color.WHITE) -> void:
	if tex != null:
		cmds.append(["txx", tex, Transform2D(0.0, _off) * xf, src if src.size != Vector2.ZERO else Rect2(Vector2.ZERO, tex.get_size()), col])


# One of the datapad's own pictures (datapad/art), tinted.
func img(id: String, r: Rect2, col: Color = Color.WHITE) -> void:
	if Art.TEXTURES.has(id):
		texture(Art.TEXTURES[id], r, Rect2(), col)


func text(x: float, y: float, s: String, font: String = "label", col: Color = INK) -> void:
	cmds.append(["t", int(x + _off.x), int(y + _off.y), s, font, col])


func text_right(right: float, y: float, s: String, font: String = "label", col: Color = INK) -> void:
	text(right - width(s, font), y, s, font, col)


func text_center(center_x: float, y: float, s: String, font: String = "label", col: Color = INK) -> void:
	text(roundf(center_x - width(s, font) / 2.0), y, s, font, col)


# As much of s as fits in w pixels.
func text_fit(x: float, y: float, w: float, s: String, font: String = "micro", col: Color = INK) -> void:
	var out := s
	while out.length() > 0 and width(out, font) > w:
		out = out.left(out.length() - 1)
	if out != "":
		text(x, y, out, font, col)


func width(s: String, font: String = "label") -> int:
	var f: Dictionary = Art.FONTS[font]
	var total := 0
	for i in s.length():
		total += int(f.advance[clampi(s.unicode_at(i) - 32, 0, 94)])
	return total


func font_height(font: String) -> int:
	return int(Art.FONTS[font].ch)


func wrap_lines(s: String, w: float, font: String = "label") -> Array:
	var lines: Array = []
	for para in s.split("\n"):
		var ln := ""
		for word in para.split(" ", false):
			if ln != "" and width(ln + " " + word, font) > w:
				lines.append(ln)
				ln = word
			else:
				ln = word if ln == "" else ln + " " + word
		lines.append(ln)
	return lines


# Wrapped text; returns the y below the last line.
func wrap_text(x: float, y: float, w: float, s: String, font: String = "label", col: Color = INK, gap: float = 17.0) -> float:
	for ln in wrap_lines(s, w, font):
		text(x, y, ln, font, col)
		y += gap
	return y


# ---------------------------------------------------------------- the datapad's parts

# The dark of space behind the case, the case itself, and its title row: TERRAN | FIELD DATAPAD ... tag.
func case(tag: String, tag_color: Color = Color("62816e")) -> void:
	rect(Rect2(_bounds), SPACE)
	texture(_stars, Rect2(Vector2.ZERO, DESIGN))
	img("housing_shadow", Rect2(27, 17, 720, 406))
	img("housing", Rect2(24, 13, 720, 406))
	img("i_mark", Rect2(50, 26, 19, 19), OCHRE)
	text(75, 25, "TERRAN", "strong", INK)
	rect(Rect2(140, 31, 1, 12), Color("9d927c"))
	text(148, 30, "FIELD DATAPAD", "micro", MUTED)
	if tag != "":
		rect(Rect2(602, 35, 4, 4), tag_color)
		text(612, 30, tag.to_upper(), "micro", INK)


# The case in fill mode: the same paper and rim as the datapad housing, drawn to fit the whole page, with the title
# row (TERRAN | FIELD DATAPAD ... tag) along its top.
func case_fill(tag: String, tag_color: Color = Color("62816e")) -> void:
	rect(Rect2(_bounds), SPACE)
	var r := Rect2(Vector2(3, 3), page - Vector2(6, 6))
	rect(Rect2(r.position + Vector2(2, 2), r.size), Color(0, 0, 0, 0.35))
	rect(r, Color("c2643a"))
	rect(r.grow(-2.0), Color("f4f1e8"))
	outline(r.grow(-2.0), Color("e9b68c"))
	outline(r.grow(-5.0), Color("dcd6c8"))
	img("i_mark", Rect2(14, 9, 15, 15), OCHRE)
	text(34, 8, "TERRAN", "strong", INK)
	rect(Rect2(99, 13, 1, 12), Color("9d927c"))
	text(107, 12, "FIELD DATAPAD", "micro", MUTED)
	if tag != "":
		var w: float = width(tag.to_upper(), "micro")
		rect(Rect2(page.x - 22 - w, 17, 4, 4), tag_color)
		text(page.x - 14 - w, 12, tag.to_upper(), "micro", INK)


# A raised paper frame (the panels, cards and buttons are all built on this).
func frame(r: Rect2, fill: Color, rim: Color = Color("b5ac9e"), hi: Color = Color("fffdf5"), edge: Color = Color("dad4c7")) -> void:
	rect(r, fill)
	outline(r, rim)
	rect(Rect2(r.position + Vector2(1, 1), Vector2(r.size.x - 2, 1)), hi)
	rect(Rect2(r.position + Vector2(1, 1), Vector2(1, r.size.y - 3)), hi)
	rect(Rect2(r.position + Vector2(2, r.size.y - 2), Vector2(r.size.x - 3, 1)), edge)
	rect(Rect2(r.position + Vector2(r.size.x - 2, 2), Vector2(1, r.size.y - 4)), edge)


# A panel with an icon and a heading, ruled off underneath. icon: "power", "blaster", "map", "bolt", "mark"...
func panel(r: Rect2, icon: String, heading: String) -> void:
	frame(r, Color("f0ede4"), Color("bdb4a5"), Color("fffdf7"), Color("d9d4c7"))
	var x := r.position.x + 8.0
	if icon != "":
		img("i_" + icon, Rect2(r.position + Vector2(6, 5), Vector2(14, 14)), OCHRE)
		x = r.position.x + 24.0
	text(x, r.position.y + 4, heading, "strong", INK)
	rect(Rect2(r.position.x + 6, r.position.y + 22, r.size.x - 13, 1), RULE)


func button(id: String, r: Rect2, label: String, on: bool = false, font: String = "label", enabled: bool = true) -> void:
	if not enabled:
		frame(r, Color("e6e4de"), Color("d0c9bb"), Color("f2f0ea"), Color("dcd7cc"))
	elif on:
		frame(r, Color("f0d4b9"), Color("c3b8a5"), Color("f9e8d2"), Color("bd8b67"))
	else:
		frame(r, Color("f0eee7"), Color("c3b8a5"), Color("fffdf6"), Color("d5cfc1"))
	var col := INK if on else MUTED
	if not enabled:
		col = Color("a8a69e")
	text_center(r.get_center().x, r.position.y + floorf((r.size.y - font_height(font)) / 2.0) + 1.0, label, font, col)
	if on:
		rect(Rect2(r.position.x, r.end.y - 2, r.size.x, 2), ORANGE)
	if enabled:
		if hovering(r):
			outline(r, ORANGE)
		hit(id, r)


func solid_button(id: String, r: Rect2, label: String, enabled: bool = true) -> void:
	rect(r, Color("a9552f") if enabled else Color("c9b4a6"))
	outline(r, Color("7c3d22") if enabled else Color("a8968a"))
	rect(Rect2(r.position + Vector2(1, 1), Vector2(r.size.x - 2, 1)), Color("c87650") if enabled else Color("d6c6ba"))
	text_center(r.get_center().x, r.position.y + floorf((r.size.y - font_height("strong")) / 2.0) + 1.0, label, "strong", Color("fff6ea"))
	if enabled:
		if hovering(r):
			outline(r, Color("f2c94c"))
		hit(id, r)


# The datapad's dark readout window, with its grid, ticks and corner marks. hostile: the enemy's, a warmer grey.
func scope(r: Rect2, pattern: int = 1, hostile: bool = false) -> void:
	texture(_scope_texture(int(r.size.x), int(r.size.y), pattern, hostile), r)


# A row of pips: n of them, the first filled ones lit.
func pips(x: float, y: float, n: int, filled: int, w: float = 5.0, h: float = 9.0, gap: float = 2.0,
		on: Color = PIP_ON, off: Color = PIP_OFF, rim_on: Color = Color("4d5a4e"), rim_off: Color = Color("bdb4a5")) -> void:
	for i in range(n):
		var r := Rect2(x + i * (w + gap), y, w, h)
		rect(r, on if i < filled else off)
		outline(r, rim_on if i < filled else rim_off)


# The bottom row of the case: a line of text on the left (what's happening, or what to do next).
func status(s: String, col: Color = INK) -> void:
	text_fit(61, STATUS_Y, 556, s, "label", col)


# ---------------------------------------------------------------- composing

func _paint_native() -> void:
	for c in cmds:
		match c[0]:
			"r": _raster.draw_rect(c[1], c[2])
			"l": _raster.draw_line(c[1], c[2], c[3], c[4])
			"c": _raster.draw_circle(c[1], c[2], c[3])
			"a": _raster.draw_arc(c[1], c[2], 0.0, TAU, maxi(12, int(c[2] * 2.0)), c[3], c[4])
			"e":
				var radii: Vector2 = c[2]
				var pts := PackedVector2Array()
				var steps: int = maxi(24, int((radii.x + radii.y) * 0.6))
				for i in range(steps + 1):
					var a: float = TAU * i / steps
					pts.append((c[1] as Vector2) + Vector2(cos(a) * radii.x, sin(a) * radii.y))
				_raster.draw_polyline(pts, c[3], c[4])
			"p": _raster.draw_colored_polygon(c[1], c[2])
			"pl": _raster.draw_polyline(c[1], c[2], c[3])
			"tx":
				var src: Rect2 = c[3]
				if src.size == Vector2.ZERO:
					_raster.draw_texture_rect(c[1], c[2], false, c[4])
				else:
					_raster.draw_texture_rect_region(c[1], c[2], src, c[4])
			"txx":
				var area: Rect2 = c[3]
				_raster.draw_set_transform_matrix(c[2])
				_raster.draw_texture_rect_region(c[1], Rect2(Vector2.ZERO, area.size), area, c[4])
				_raster.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
			"t": _paint_text(c[1], c[2], c[3], c[4], c[5])


func _paint_text(x: int, y: int, value: String, font_name: String, color: Color) -> void:
	var f: Dictionary = Art.FONTS[font_name]
	if TEXT_SIZE.has(font_name) and _font != null:
		var font: Font = _font_bold if font_name in TEXT_BOLD else _font
		var font_size: int = maxi(1, roundi(float(TEXT_SIZE[font_name]) * _px))
		var base_y: float = roundf((float(y) + float(TEXT_BASE[font_name])) * _px)
		_raster.draw_set_transform(Vector2.ZERO, 0.0, Vector2(1.0 / _px, 1.0 / _px))
		for i in value.length():
			var idx := clampi(value.unicode_at(i) - 32, 0, 94)
			var advance: int = int(f.advance[idx])
			if idx != 0:
				var w: float = font.get_char_size(value.unicode_at(i), font_size).x
				_raster.draw_char(font, Vector2(roundf(x * _px + (advance * _px - w) / 2.0), base_y), value[i], font_size, color)
			x += advance
		_raster.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	else:
		var atlas: Texture2D = Art.TEXTURES["f_" + font_name]
		for i in value.length():
			var idx := clampi(value.unicode_at(i) - 32, 0, 94)
			if idx != 0:
				var area := Rect2((idx % 16) * f.cw, floori(idx / 16.0) * f.ch, f.cw, f.ch)
				_raster.draw_texture_rect_region(atlas, Rect2(x, y, f.cw, f.ch), area, color)
			x += int(f.advance[idx])


func _star_texture() -> Texture2D:
	var image := Image.create_empty(int(DESIGN.x), int(DESIGN.y), false, Image.FORMAT_RGBA8)
	var rng := RandomNumberGenerator.new()
	rng.seed = 2
	var colors := [Color("3a4660"), Color("566382"), Color("8090b0")]
	for i in range(260):
		image.set_pixel(rng.randi_range(0, int(DESIGN.x) - 1), rng.randi_range(0, int(DESIGN.y) - 1), colors[rng.randi_range(0, 2)])
	return ImageTexture.create_from_image(image)


func _scope_texture(w: int, h: int, pattern: int, hostile: bool) -> Texture2D:
	var key := "%d,%d,%d,%s" % [w, h, pattern, hostile]
	if _scopes.has(key):
		return _scopes[key]
	w = maxi(w, 24)
	h = maxi(h, 24)
	var image := Image.create_empty(w, h, false, Image.FORMAT_RGBA8)
	image.fill(Color("433f3c") if hostile else Color("3d4946"))
	var dots := [Color("708076"), Color("6b7972"), Color("5b6b62"), Color("7f8b7e")]
	for i in range(int(w * h / 180.0)):
		image.set_pixel((i * 71 + i * i * 13 + 19 * pattern) % w, (i * 41 + i * i * 11 + 7 * pattern) % h, dots[i % 4])
	var grid := Color("4e4844") if hostile else Color("48544e")
	for xx in range(12, w, 14):
		for yy in range(10, h, 14):
			image.set_pixel(xx, yy, grid)
	for xx in range(18, w - 13, 7):
		var t := 4 if (xx - 18) % 35 == 0 else 2
		for yy in range(h - 4 - t, h - 3):
			image.set_pixel(xx, yy, Color("788473"))
	var rims := [Color("343b35"), Color("806b66") if hostile else Color("71806b")]
	for k in range(2):
		for xx in range(k, w - k):
			image.set_pixel(xx, k, rims[k])
			image.set_pixel(xx, h - 1 - k, rims[k])
		for yy in range(k, h - k):
			image.set_pixel(k, yy, rims[k])
			image.set_pixel(w - 1 - k, yy, rims[k])
	var mark := Color("c8a89c") if hostile else Color("b5bc9c")
	for corner in [[6, 6, 1, 1], [w - 7, 6, -1, 1], [6, h - 7, 1, -1], [w - 7, h - 7, -1, -1]]:
		for i in range(8):
			image.set_pixel(corner[0], corner[1] + i * corner[3], mark)
		for i in range(10):
			image.set_pixel(corner[0] + i * corner[2], corner[1], mark)
	var tex := ImageTexture.create_from_image(image)
	_scopes[key] = tex
	return tex
