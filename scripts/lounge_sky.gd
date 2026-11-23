extends MeshInstance2D
## Curved glazing in the Survey Level lounge. World dimensions use the 16 px map grid.
## The view is drawn by scripts/lounge_sky.gdshader from the station clock (23 Nov): the stars and the
## gas giant stay put, the sun crosses with the time of day and sets behind the giant in the evening,
## and the day's sky event plays over it. The old 32-frame loops made the sun bob back and forth.
const HEIGHT := 64
const WIDTH := 912
const LEFT := 144
const EVENTS := {
	3: "eclipse", 7: "gas_cloud", 9: "storm", 11: "meteors",
	15: "transit", 20: "aurora", 23: "storm", 26: "comet",
}
const EVENT_IDS := {
	"clear": 0, "eclipse": 1, "gas_cloud": 2, "meteors": 3, "transit": 4, "aurora": 5, "comet": 6, "storm": 7,
}
const LABELS := {
	"eclipse": "Solar eclipse", "gas_cloud": "Violet gas cloud", "meteors": "Meteor shower",
	"transit": "Moon transit", "aurora": "Polar aurora", "comet": "Comet passage", "storm": "Space storm",
}
const OBSERVATIONS := {
	"clear": "A turquoise storm turns beneath the giant’s ivory cloud belts.",
	"eclipse": "Around midday the sun slips behind the giant, and a sliver of gold clings to its blue limb.",
	"gas_cloud": "Violet gas drifts across the star field in wisps. The brightest stars shine through.",
	"meteors": "Bright trails fall in little groups. A second shower follows the first.",
	"transit": "A small moon casts a dark silhouette against the bright cloud belts.",
	"aurora": "Green curtains of light ripple above the giant’s pole.",
	"comet": "A pale comet passes the giant, trailing two thin tails.",
	"storm": "An ion storm rolls past the glass. Lightning forks through the charged gas.",
}
# Each run follows the baked sill: world x, width, bottom y (exclusive), slope.
const SILL := [
	[144, 15, 367, -1],
	[159, 1, 344, 0],
	[160, 15, 335, -1],
	[175, 1, 312, 0],
	[176, 15, 303, -1],
	[191, 1, 280, 0],
	[192, 127, 271, -1],
	[319, 2, 145, -1],
	[321, 15, 144, 0],
	[336, 31, 143, -1],
	[367, 2, 113, -1],
	[369, 31, 112, 0],
	[400, 15, 111, -1],
	[415, 2, 97, -1],
	[417, 15, 96, 0],
	[432, 15, 95, -1],
	[447, 2, 81, -1],
	[449, 47, 80, 0],
	[496, 15, 79, -1],
	[511, 2, 65, -1],
	[513, 175, 64, 0],
	[688, 2, 65, 0],
	[690, 15, 66, 1],
	[705, 47, 80, 0],
	[752, 2, 81, 0],
	[754, 15, 82, 1],
	[769, 15, 96, 0],
	[784, 2, 97, 0],
	[786, 15, 98, 1],
	[801, 31, 112, 0],
	[832, 2, 113, 0],
	[834, 31, 114, 1],
	[865, 15, 144, 0],
	[880, 2, 145, 0],
	[882, 126, 146, 1],
	[1008, 1, 280, 0],
	[1009, 15, 289, 1],
	[1024, 1, 312, 0],
	[1025, 15, 321, 1],
	[1040, 1, 344, 0],
	[1041, 15, 353, 1],
]
var clock: Node
var elapsed := 0.0

static func sky_for(day: int) -> String:
	return EVENTS.get(posmod(maxi(day, 1) - 1, 28) + 1, "clear")

func setup(station: Node) -> void:
	clock = station
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var shader_material := ShaderMaterial.new()
	shader_material.shader = preload("res://scripts/lounge_sky.gdshader")
	material = shader_material
	texture = load("res://art/lunar/lounge_sky/frame.png")
	var vertices := PackedVector2Array()
	var coords := PackedVector2Array()
	var indices := PackedInt32Array()
	for run in SILL:
		for offset in int(run[1]):
			var x := int(run[0]) + offset
			var bottom := int(run[2]) + int(run[3]) * offset
			var top := bottom - HEIGHT
			var start := vertices.size()
			vertices.append_array([Vector2(x, top), Vector2(x+1, top), Vector2(x+1, bottom), Vector2(x, bottom)])
			var u := float(x - LEFT) / WIDTH
			var u_next := float(x + 1 - LEFT) / WIDTH
			coords.append_array([Vector2(u, 0), Vector2(u_next, 0), Vector2(u_next, 1), Vector2(u, 1)])
			indices.append_array([start, start+1, start+2, start, start+2, start+3])
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_TEX_UV] = coords
	arrays[Mesh.ARRAY_INDEX] = indices
	var glass := ArrayMesh.new()
	glass.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	mesh = glass
	visibility_changed.connect(_sync_visibility)

func _sync_visibility() -> void:
	set_process(is_visible_in_tree())
	if is_visible_in_tree():
		_process(0.0)

func _process(delta: float) -> void:
	# a long but finite loop for the twinkling and drifting, so the numbers stay small
	elapsed = fmod(elapsed + delta, 3600.0)
	var shader := material as ShaderMaterial
	shader.set_shader_parameter("minute", float(clock.get("minutes")))
	# a heart-event scene can ask for its own sky (scripts/cutscene.gd "sky"); otherwise the day's
	var wanted: String = str(clock.get("sky_override")) if clock.get("sky_override") != null else ""
	var sky: String = wanted if EVENT_IDS.has(wanted) else sky_for(int(clock.get("day")))
	shader.set_shader_parameter("event", int(EVENT_IDS.get(sky, 0)))
	shader.set_shader_parameter("clock_time", elapsed)
