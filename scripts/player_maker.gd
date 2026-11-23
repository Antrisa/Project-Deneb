extends RefCounted
# Builds the player's walk sheet from layers: bottoms, tops, faces and hair, each recoloured.
#
# The layer files are in art/player/. Each is 4 directions across (down, up, left, right) and
# 10 choices down, each in 24x48 cells. The five rows are stand, contact A/B, then passing A/B.
# The paired "_mask" file selects which pixels take a colour:
# red = the layer's main colour (hair, top, bottom or skin), green = skin, blue = eyes.
# This follows the same rules as the customizer tool that came with the art, so the two match.

const LAYERS := ["bottoms", "faces", "tops", "hair"]          # drawn in this order
# The shirt goes over the head-and-neck layer (as in player_eating/), so the collar hides the base of the neck.
const PRIMARY := {"hair": "hairColor", "tops": "topColor", "bottoms": "bottomColor", "faces": "skinColor"}
const DIVISOR := [140.0, 185.0, 150.0]                          # brightness that counts as "full colour": main, skin, eyes

const NAMES := {
	# 20 Nov player art: eight new hairstyles, then the two kept from before. Every face slot now holds the same
	# shared face, so the character screen no longer offers a face choice (creator.gd).
	"hair": ["Tousled crop", "Side part", "Low ponytail", "Medium bob", "Long loose hair", "Twin braids", "Buzz cut", "Short faux hawk", "Textured coils", "Long waves"],
	"faces": ["Face", "Face", "Face", "Face", "Face", "Face", "Face", "Face", "Face", "Face"],
	"tops": ["Crew tee", "Utility vest", "Flight jacket", "Mechanic coveralls", "Space tunic", "Hoodie", "Expedition coat", "Light armor", "Workshirt", "Circuit suit"],
	"bottoms": ["Work pants", "Cargo pants", "Flight trousers", "Fitted trousers", "Explorer shorts", "Utility skirt", "Expedition pants", "Mechanic trousers", "Tech leggings", "Cuffed trousers"],
}

# The colours offered in the game's character screen.
const PALETTES := {
	"hairColor": ["#82482e", "#492835", "#68452f", "#2b1d16", "#111418", "#8c5a2e", "#c98a3d", "#e8c36a", "#b5432e", "#d9d9df", "#5a6fb0", "#7a3f8f", "#3c8f6a", "#e07aa8"],
	"eyeColor": ["#42613a", "#45643d", "#54b7c4", "#3f6fb3", "#4c8f4a", "#7a5230", "#2e2a2a", "#8a8f99", "#b08a2e", "#8f4fb0"],
	"skinColor": ["#f5b88a", "#ce835e", "#efb583", "#f6d0b0", "#f0c6a0", "#e0a070", "#c68652", "#a5683c", "#7d4a2a", "#59341f"],
	"topColor": ["#58686a", "#b5603e", "#578d99", "#b5432e", "#3f6fb3", "#4c8f4a", "#d0a030", "#7a3f8f", "#d9d9df", "#30343c", "#c96a2e", "#e07aa8"],
	"bottomColor": ["#51454b", "#506063", "#657081", "#30343c", "#6b4a2e", "#3f5a8a", "#4a6a4a", "#8a8f99", "#7a2e2e", "#c9b38a"],
}

# Choices that are not pictures. "body" is the Gender line: Male uses the layers in art/player/,
# Female uses art/player/body2/ (same eight file names and layout). It also sets the pronouns.
const OPTIONS := {
	"body": ["Male", "Female"],
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

const STARTER_LOOKS := [
	{
		"body": 0, "tops": 2, "bottoms": 1, "faces": 0, "hair": 0,
		"hairColor": "#82482e", "eyeColor": "#42613a", "topColor": "#58686a",
		"bottomColor": "#51454b", "skinColor": "#f5b88a",
	},
	{
		"body": 1, "tops": 4, "bottoms": 0, "faces": 0, "hair": 2,
		"hairColor": "#492835", "eyeColor": "#45643d", "topColor": "#b5603e",
		"bottomColor": "#506063", "skinColor": "#ce835e",
	},
]

var _art := {}       # layer name -> Image
var _mask := {}
var _art2 := {}      # the second body's layers, if art/player/body2/ exists
var _mask2 := {}
var _watering_arm_mask: Image
const CHOICES := 10
const FRAME := Vector2i(24, 48)
const Poses = preload("res://scripts/player_poses.gd")


func load_layers() -> bool:
	_art.clear()
	_mask.clear()
	_art2.clear()
	_mask2.clear()
	if not _load_body("res://art/player/", _art, _mask):
		return false
	_load_body("res://art/player/body2/", _art2, _mask2)
	var path := "res://art/player/watering_arm_mask.png"
	_watering_arm_mask = _image(path) if ResourceLoader.exists(path) else null
	return true


# Each body may use an older three-pose atlas. Its eight files must all use the same layout.
func _load_body(folder: String, art: Dictionary, masks: Dictionary) -> bool:
	var size := Vector2i.ZERO
	for k in LAYERS:
		var art_path := folder + str(k) + ".png"
		var mask_path := folder + str(k) + "_mask.png"
		if not ResourceLoader.exists(art_path) or not ResourceLoader.exists(mask_path):
			art.clear()
			masks.clear()
			return false
		var img := _image(art_path)
		var mask := _image(mask_path)
		if size == Vector2i.ZERO:
			size = img.get_size()
		if size.x != FRAME.x * 4 or size.y not in [FRAME.y * 3 * CHOICES, FRAME.y * 5 * CHOICES] or img.get_size() != size or mask.get_size() != size:
			push_warning("Incompatible player layer dimensions in " + art_path)
			art.clear()
			masks.clear()
			return false
		art[k] = img
		masks[k] = mask
	# Only the arms and clothing change for carrying and held tools.
	var action_path := folder + "action_tops.png"
	var action_mask_path := folder + "action_tops_mask.png"
	if size.y == FRAME.y * 5 * CHOICES and ResourceLoader.exists(action_path) and ResourceLoader.exists(action_mask_path):
		var action := _image(action_path)
		var action_mask := _image(action_mask_path)
		var layout := action.get_size()
		var current := Vector2i(size.x * CHOICES, FRAME.y * Poses.COUNT)
		var preceding := Vector2i(size.x * CHOICES, FRAME.y * Poses.PREVIOUS_COUNT)
		var legacy := Vector2i(size.x, FRAME.y * Poses.LEGACY_COUNT * CHOICES)
		if layout in [current, preceding, legacy] and action_mask.get_size() == layout:
			art["action_tops"] = action
			masks["action_tops"] = action_mask
	return true


func body_count() -> int:
	return 2 if not _art2.is_empty() else 1


# How many choices an OPTIONS line has right now.
func option_count(key: String) -> int:
	var names: Array = OPTIONS[key]
	return names.size()


# Swaps {they}, {them}, {their}... in a line of dialogue for he or she, from the player's gender.
func with_pronouns(line: String, look: Dictionary) -> String:
	if line.find("{") == -1:
		return line
	var which: int = 1 if int(look.get("body", 0)) == 1 else 2      # she for Female, he for Male
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


func defaults(body: int = 0) -> Dictionary:
	return STARTER_LOOKS[clampi(body, 0, STARTER_LOOKS.size() - 1)].duplicate()


# A look with anything missing or out of range replaced by the default. Each gender has one fixed
# outfit and hairstyle (its starter look); only the colours are the player's to choose (22 Nov).
func tidy(look: Dictionary) -> Dictionary:
	var out := defaults(int(look.get("body", 0)))
	for k in PALETTES:
		if look.has(k) and Color.html_is_valid(str(look[k])):
			out[k] = str(look[k])
	for k in OPTIONS:
		if look.has(k):
			out[k] = clampi(int(look[k]), 0, option_count(k) - 1)
	return out


# Random colours; the outfit and hairstyle stay the gender's own (see tidy).
func random_look() -> Dictionary:
	var out := {}
	for k in PALETTES:
		var colours: Array = PALETTES[k]
		out[k] = colours[randi() % colours.size()]
	return out


# Recolour a single choice across its directions and walk poses.
func _tinted(k: String, look: Dictionary) -> Image:
	var style_key := "tops" if k == "action_tops" else k
	var choice: int = look[style_key]
	var second: bool = int(look.get("body", 0)) == 1 and not _art2.is_empty()
	var art_all: Image = _art2[k] if second else _art[k]
	var mask_all: Image = _mask2[k] if second else _mask[k]
	var height := floori(float(art_all.get_height()) / CHOICES)
	var region := Rect2i(0, choice * height, art_all.get_width(), height)
	if k == "action_tops" and art_all.get_width() == 4 * FRAME.x * CHOICES:
		# The four facings for each outfit sit side by side, keeping both atlas dimensions small.
		region = Rect2i(choice * 4 * FRAME.x, 0, 4 * FRAME.x, art_all.get_height())
	var art := art_all.get_region(region)
	var mask := mask_all.get_region(region)
	var primary_key: String = PRIMARY[style_key]
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
			# A red or green mask with 64 blue keeps the painted hue shifts in its ramp.
			# Pure masks retain the luminance tint used by older atlas packs.
			var painted := mk[i + 2] == 64 and kind != 2
			var lum := 0.2126 * px[i] + 0.7152 * px[i + 1] + 0.0722 * px[i + 2]
			var light := Vector3(px[i], px[i + 1], px[i + 2]) if painted else Vector3.ONE * lum
			px[i] = clampi(roundi(t.r8 * light.x / div), 0, 255)
			px[i + 1] = clampi(roundi(t.g8 * light.y / div), 0, 255)
			px[i + 2] = clampi(roundi(t.b8 * light.z / div), 0, 255)
		i += 4
	return Image.create_from_data(region.size.x, region.size.y, false, Image.FORMAT_RGBA8, px)


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


# Bottoms form the base image. Clothing, face, and hair keep the same registration in every row.
func sheet(look_in: Dictionary) -> ImageTexture:
	var look := tidy(look_in)
	var out := _tinted(LAYERS[0], look)
	for k in LAYERS.slice(1):
		var layer := _tinted(k, look)
		out.blend_rect(layer, Rect2i(Vector2i.ZERO, out.get_size()), Vector2i.ZERO)
	return ImageTexture.create_from_image(out)


# Five carry rows follow the feet in the walk sheet. Working poses pivot the upper body over planted boots.
func action_sheet(look_in: Dictionary) -> ImageTexture:
	var look := tidy(look_in)
	var body: Dictionary = _art2 if look.body == 1 and not _art2.is_empty() else _art
	if not body.has("action_tops"):
		return null
	var bottoms := _tinted("bottoms", look)
	var faces := _tinted("faces", look)
	var hair := _tinted("hair", look)
	var tops := _tinted("action_tops", look)
	var out := Image.create_empty(tops.get_width(), tops.get_height(), false, Image.FORMAT_RGBA8)
	var rows := tops.get_height() / FRAME.y
	var water_arms: Image
	var width := tops.get_width()
	if rows == Poses.COUNT and _watering_arm_mask != null:
		var height := FRAME.y * Poses.WATER_ROWS.size()
		var body_index := 1 if look.body == 1 and not _art2.is_empty() else 0
		water_arms = Image.create_empty(width, height, false, Image.FORMAT_RGBA8)
		for i in Poses.WATER_ROWS.size():
			var strip := tops.get_region(Rect2i(0, Poses.WATER_ROWS[i] * FRAME.y, width, FRAME.y))
			var stencil := _watering_arm_mask.get_region(Rect2i(look.tops * width, body_index * height + i * FRAME.y, width, FRAME.y))
			water_arms.blit_rect_mask(strip, stencil, Rect2i(0, 0, width, FRAME.y), Vector2i(0, i * FRAME.y))
	for row in rows:
		var water_index := Poses.WATER_ROWS.find(row) if water_arms != null else -1
		var base_row := row if row < Poses.GRIP else 0
		for dir in 4:
			var base := Rect2i(Vector2i(dir * FRAME.x, base_row * FRAME.y), FRAME)
			var dest := Rect2i(Vector2i(dir * FRAME.x, row * FRAME.y), FRAME)
			var head := Poses.head_offset(row, dir, rows) if rows >= Poses.PREVIOUS_COUNT else Vector2i.ZERO
			var head_source := Rect2i(base.position + (-head).max(Vector2i.ZERO), FRAME - head.abs())
			var head_at := dest.position + head.max(Vector2i.ZERO)
			out.blit_rect(bottoms, base, dest.position)
			out.blend_rect(faces, head_source, head_at)
			out.blend_rect(tops, dest, dest.position)
			out.blend_rect(hair, head_source, head_at)
			if dir != 1 and water_index < 0:
				var high := Rect2i(dest.position, Vector2i(FRAME.x, 20 + head.y))
				out.blend_rect(tops, high, dest.position)
		if water_index >= 0:
			# Only the camera-side sleeve and hand pass in front of the hair in profile.
			out.blend_rect(water_arms, Rect2i(0, water_index * FRAME.y, width, FRAME.y), Vector2i(0, row * FRAME.y))
	var tex := Poses.ActionSheet.new()
	tex.set_image(out)
	if water_arms != null:
		tex.watering_arms = ImageTexture.create_from_image(water_arms)
	return tex
