extends RefCounted
# Builds the player's walk sheet from layers: bottoms, tops, faces and hair, each recoloured.
#
# The layer files are in art/player/. Each is 4 directions across (down, up, left, right) and
# 10 choices down, each with 3 pose rows (idle, step A, step B) in 32x64 cells.
# Atlas size: 128x1920. Arm/leg articulation and waist overlap are baked into each layer. Each has a "_mask" file saying which pixels take a colour:
# red = the layer's main colour (hair, top, bottom or skin), green = skin, blue = eyes.
# This follows the same rules as the customizer tool that came with the art, so the two match.

const LAYERS := ["bottoms", "tops", "faces", "hair"]          # drawn in this order
const PRIMARY := {"hair": "hairColor", "tops": "topColor", "bottoms": "bottomColor", "faces": "skinColor"}
const DIVISOR := [140.0, 185.0, 150.0]                          # brightness that counts as "full colour": main, skin, eyes

const NAMES := {
	"hair": ["Side part", "Tousled crop", "Short curls", "Bob", "Shoulder length", "Ponytail", "Bun", "Undercut", "Textured coils", "Long waves"],
	"faces": ["Soft oval", "Square", "Freckled", "Angular", "Heart-shaped", "High cheekbones", "Rounded", "Mature", "Strong chin", "Cheek scar"],
	"tops": ["Crew tee", "Utility vest", "Flight jacket", "Mechanic coveralls", "Space tunic", "Hoodie", "Expedition coat", "Light armor", "Workshirt", "Circuit suit"],
	"bottoms": ["Work pants", "Cargo pants", "Flight trousers", "Fitted trousers", "Explorer shorts", "Utility skirt", "Expedition pants", "Mechanic trousers", "Tech leggings", "Cuffed trousers"],
}

# The colours offered in the game's character screen.
const PALETTES := {
	"hairColor": ["#68452f", "#2b1d16", "#111418", "#8c5a2e", "#c98a3d", "#e8c36a", "#b5432e", "#d9d9df", "#5a6fb0", "#7a3f8f", "#3c8f6a", "#e07aa8"],
	"eyeColor": ["#54b7c4", "#3f6fb3", "#4c8f4a", "#7a5230", "#2e2a2a", "#8a8f99", "#b08a2e", "#8f4fb0"],
	"skinColor": ["#efb583", "#f6d0b0", "#f0c6a0", "#e0a070", "#c68652", "#a5683c", "#7d4a2a", "#59341f"],
	"topColor": ["#578d99", "#b5432e", "#3f6fb3", "#4c8f4a", "#d0a030", "#7a3f8f", "#d9d9df", "#30343c", "#c96a2e", "#e07aa8"],
	"bottomColor": ["#657081", "#30343c", "#6b4a2e", "#3f5a8a", "#4a6a4a", "#8a8f99", "#7a2e2e", "#c9b38a"],
}

# Choices that are not pictures. "body" only appears on the character screen when a second
# set of layers exists in art/player/body2/ (same eight file names and layout).
const OPTIONS := {
	"body": ["Male", "Female"],
	"pronouns": ["They / them", "She / her", "He / him"],
}

# The words residents use for the player. In any line of dialogue write the "they" form in
# curly brackets and the game swaps in the right one:
#   {they} {them} {their} {theirs} {they're} {they've} {are} {were} {have} {s}
# A capital letter is kept: {They} -> She. {s} is the verb ending: "{they} look{s} tired".
const WORDS := {
	"they": ["they", "she", "he"], "them": ["them", "her", "him"], "their": ["their", "her", "his"],
	"theirs": ["theirs", "hers", "his"], "they're": ["they're", "she's", "he's"],
	"they've": ["they've", "she's", "he's"], "are": ["are", "is", "is"], "were": ["were", "was", "was"],
	"have": ["have", "has", "has"], "s": ["", "s", "s"],
}

const DEFAULTS := {
	"body": 0, "pronouns": 0,
	"tops": 2, "bottoms": 1, "faces": 0, "hair": 0,
	"hairColor": "#68452f", "eyeColor": "#54b7c4", "topColor": "#578d99", "bottomColor": "#657081", "skinColor": "#efb583",
}

var _art := {}       # layer name -> Image
var _mask := {}
var _art2 := {}      # the second body's layers, if art/player/body2/ exists
var _mask2 := {}
const ATLAS_SIZE := Vector2i(128, 1920)
const CHOICE_HEIGHT := 192


# Loads the layer pictures. Returns false if any are missing (the game then keeps art/player.png).
func load_layers() -> bool:
	var art := {}
	var masks := {}
	for k in LAYERS:
		var art_path: String = "res://art/player/%s.png" % k
		var mask_path: String = "res://art/player/%s_mask.png" % k
		if not ResourceLoader.exists(art_path) or not ResourceLoader.exists(mask_path):
			push_warning("Missing player layer: " + str(k))
			return false
		var img: Image = _image(art_path)
		var mask: Image = _image(mask_path)
		if img.get_size() != ATLAS_SIZE or mask.get_size() != ATLAS_SIZE:
			push_warning("Player layers must be v2 animated 128x1920 atlases: " + str(k))
			return false
		art[k] = img
		masks[k] = mask
	_art = art
	_mask = masks
	_load_second_body()
	return true


# The optional second body: all eight files in art/player/body2/, same layout.
func _load_second_body() -> void:
	var art := {}
	var masks := {}
	for k in LAYERS:
		var art_path: String = "res://art/player/body2/%s.png" % k
		var mask_path: String = "res://art/player/body2/%s_mask.png" % k
		if not ResourceLoader.exists(art_path) or not ResourceLoader.exists(mask_path):
			return
		var img: Image = _image(art_path)
		var mask: Image = _image(mask_path)
		if img.get_size() != ATLAS_SIZE or mask.get_size() != ATLAS_SIZE:
			push_warning("art/player/body2 layers must be 128x1920: " + str(k))
			return
		art[k] = img
		masks[k] = mask
	_art2 = art
	_mask2 = masks


func body_count() -> int:
	return 2 if not _art2.is_empty() else 1


# How many choices an OPTIONS line has right now.
func option_count(key: String) -> int:
	if key == "body":
		return body_count()
	var names: Array = OPTIONS[key]
	return names.size()


# Swaps {they}, {them}, {their}... in a line of dialogue for the player's pronouns.
func with_pronouns(line: String, look: Dictionary) -> String:
	if line.find("{") == -1:
		return line
	var which: int = clampi(int(look.get("pronouns", 0)), 0, 2)
	var out: String = line
	for word in WORDS:
		var forms: Array = WORDS[word]
		var form: String = forms[which]
		var key: String = word
		out = out.replace("{" + key + "}", form)
		if key != "s":
			out = out.replace("{" + key.substr(0, 1).to_upper() + key.substr(1) + "}", form.substr(0, 1).to_upper() + form.substr(1))
	return out


func _image(path: String) -> Image:
	var tex: Texture2D = load(path)
	var img: Image = tex.get_image()
	if img.is_compressed():
		img.decompress()
	if img.get_format() != Image.FORMAT_RGBA8:
		img.convert(Image.FORMAT_RGBA8)
	return img


func defaults() -> Dictionary:
	return DEFAULTS.duplicate()


# A look with anything missing or out of range replaced by the default.
func tidy(look: Dictionary) -> Dictionary:
	var out: Dictionary = DEFAULTS.duplicate()
	for k in NAMES:
		if look.has(k):
			out[k] = clampi(int(look[k]), 0, 9)
	for k in PALETTES:
		if look.has(k) and Color.html_is_valid(str(look[k])):
			out[k] = str(look[k])
	for k in OPTIONS:
		if look.has(k):
			out[k] = clampi(int(look[k]), 0, option_count(k) - 1)
	return out


func random_look() -> Dictionary:
	var out := {}
	for k in NAMES:
		out[k] = randi() % 10
	for k in PALETTES:
		var colours: Array = PALETTES[k]
		out[k] = colours[randi() % colours.size()]
	return out


# One choice's three baked poses (four directions, 128x192), recoloured.
func _tinted(k: String, look: Dictionary) -> Image:
	var choice: int = look[k]
	var second: bool = int(look.get("body", 0)) == 1 and not _art2.is_empty()
	var art_all: Image = _art2[k] if second else _art[k]
	var mask_all: Image = _mask2[k] if second else _mask[k]
	var art: Image = art_all.get_region(Rect2i(0, choice * CHOICE_HEIGHT, 128, CHOICE_HEIGHT))
	var mask: Image = mask_all.get_region(Rect2i(0, choice * CHOICE_HEIGHT, 128, CHOICE_HEIGHT))
	var primary_key: String = PRIMARY[k]
	var targets: Array = [Color.html(look[primary_key]), Color.html(look["skinColor"]), Color.html(look["eyeColor"])]
	var px: PackedByteArray = art.get_data()
	var mk: PackedByteArray = mask.get_data()
	var i := 0
	var count: int = px.size()
	while i < count:
		if px[i + 3] != 0 and mk[i + 3] != 0:
			var kind := 0
			if mk[i] == 0:
				kind = 1 if mk[i + 1] != 0 else 2
			var t: Color = targets[kind]
			var div: float = DIVISOR[kind]
			var factor: float = (0.2126 * px[i] + 0.7152 * px[i + 1] + 0.0722 * px[i + 2]) / div
			px[i] = clampi(roundi(t.r8 * factor), 0, 255)
			px[i + 1] = clampi(roundi(t.g8 * factor), 0, 255)
			px[i + 2] = clampi(roundi(t.b8 * factor), 0, 255)
		i += 4
	return Image.create_from_data(128, CHOICE_HEIGHT, false, Image.FORMAT_RGBA8, px)


# Draws part of src onto dst, trimming anything that would fall outside dst.
func _blend(dst: Image, src: Image, sx: int, sy: int, w: int, h: int, dx: int, dy: int) -> void:
	if dx < 0:
		sx -= dx
		w += dx
		dx = 0
	if dy < 0:
		sy -= dy
		h += dy
		dy = 0
	w = mini(w, dst.get_width() - dx)
	h = mini(h, dst.get_height() - dy)
	if w > 0 and h > 0:
		dst.blend_rect(src, Rect2i(sx, sy, w, h), Vector2i(dx, dy))


# The full walk sheet: 4 directions across, 3 rows (standing, step A, step B), 32x64 frames.
# The poses are already drawn into the layers; this recolours them and stacks them.
func sheet(look_in: Dictionary) -> ImageTexture:
	var look: Dictionary = tidy(look_in)
	var out: Image = Image.create_empty(128, 192, false, Image.FORMAT_RGBA8)
	for k in LAYERS:
		var layer: Image = _tinted(k, look)
		out.blend_rect(layer, Rect2i(0, 0, 128, 192), Vector2i.ZERO)
	return ImageTexture.create_from_image(out)
