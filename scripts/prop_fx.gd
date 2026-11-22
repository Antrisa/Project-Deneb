# Cozy art pass (21 Nov 2026): ground shadows, lamp glows and leaf sway for props and people.
# Art is never painted with a ground shadow: the game puts a soft, pixel-stepped oval under each piece here.
# Glows come from art/lunar/<name>_glow.png (white to pale yellow on transparent) and get brighter at night.
extends RefCounted

const ART := 2.0 / 3.0
const SHADOW_EDGE := Color(0.18, 0.09, 0.13, 0.22)
const SHADOW_CORE := Color(0.18, 0.09, 0.13, 0.34)
# Flat or wall-hung pieces get no shadow on the floor.
const NO_SHADOW := ["prayer_mat", "rubble", "glass_shards", "steam_vent", "mag_clamp", "launch_door", "lab_door",
	"wall_screen", "star_chart", "paris_pictures", "precursor_mural", "departures_board", "key_board",
	"holy_banner", "rug_berry", "window", "tarp_fighter"]
# Leafy pieces lean a pixel in a slow breeze from the air vents.
const SWAY := ["plants", "flowers", "tree_tub", "park_tree", "fruit_tree", "planter_long", "potted_plant"]
# Where the light sits in the picture, as a share of its height up from the bottom (default: the middle).
const GLOW_AT := {"lamp_post": 0.9, "bollard_light": 0.78, "brazier": 0.82, "fireplace": 0.35,
	"bedside_lamp": 0.8, "arc_smelter": 0.3}

static var _shadows := {}
static var _sway_mat: ShaderMaterial = null
static var _glow_mat: CanvasItemMaterial = null


# A soft oval w art pixels wide: a darker core and a lighter rim, hard pixel edges.
static func shadow_texture(w: int) -> ImageTexture:
	w = clampi(w, 6, 112)
	if _shadows.has(w):
		return _shadows[w]
	var h: int = clampi(int(round(w * 0.3)), 4, 12)
	var img := Image.create_empty(w, h, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	var rx: float = w / 2.0
	var ry: float = h / 2.0
	for y in h:
		for x in w:
			var dx: float = (x + 0.5 - rx) / rx
			var dy: float = (y + 0.5 - ry) / ry
			var d: float = dx * dx + dy * dy
			if d <= 0.42:
				img.set_pixel(x, y, SHADOW_CORE)
			elif d <= 1.0:
				img.set_pixel(x, y, SHADOW_EDGE)
	var tex := ImageTexture.create_from_image(img)
	_shadows[w] = tex
	return tex


# A shadow sprite to add as a child; the parent draws over it. pos and scale are in the parent's units.
static func make_shadow(width_art: int, pos: Vector2, sc: Vector2) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = shadow_texture(width_art)
	s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	s.centered = true
	s.position = pos
	s.scale = sc
	s.show_behind_parent = true
	return s


static func sway_material() -> ShaderMaterial:
	if _sway_mat == null:
		_sway_mat = ShaderMaterial.new()
		_sway_mat.shader = load("res://shaders/sway.gdshader")
	return _sway_mat


# Shadow, glow and sway for one prop sprite (art pixels, standing on its bottom edge).
# Returns the glow sprite, if the prop has one, so main.gd can brighten it at night.
static func decorate(sprite: Sprite2D, name: String, fw: int, fh: int) -> Sprite2D:
	var base: String = name.trim_suffix("_steel")
	var bottom: float = sprite.offset.y + fh     # chairs draw lower than their origin (see main.gd)
	if not (base in NO_SHADOW or base.begins_with("rug")):
		sprite.add_child(make_shadow(int(fw * 0.86), Vector2(fw * 0.5, bottom - 2.0), Vector2.ONE))
	if base in SWAY and sprite.material == null:
		sprite.material = sway_material()
	var path := "res://art/lunar/%s_glow.png" % name
	if not ResourceLoader.exists(path):
		return null
	if _glow_mat == null:
		_glow_mat = CanvasItemMaterial.new()
		_glow_mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	var g := Sprite2D.new()
	g.texture = load(path)
	g.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	g.material = _glow_mat
	g.centered = true
	g.position = Vector2(fw * 0.5, bottom - fh * float(GLOW_AT.get(base, 0.5)))
	sprite.add_child(g)
	return g


# How strong lamp glows are for the current scene tint: faint by day, full at night.
static func glow_strength(tint: Color) -> float:
	var lum: float = tint.r * 0.3 + tint.g * 0.59 + tint.b * 0.11
	return clampf(0.35 + (1.0 - lum) * 1.8, 0.35, 1.0)
