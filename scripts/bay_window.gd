extends Node2D
## The two banks share a panorama. Coordinates follow the same 24-pixel art grid
## and 16-unit map tiles as the wall bake.
const TILE := 16
const ART_TILE := 24
const FRAME_HEIGHT := ART_TILE * 2
const FPS := 6.0
const EVENTS := {3: "eclipse", 7: "sunrise", 11: "impacts", 15: "moonrise", 22: "rover"}
const LABELS := {
	"eclipse": "Eclipse shadow", "sunrise": "Crater sunrise",
	"impacts": "Micrometeor impacts", "moonrise": "Companion moonrise", "rover": "Rover survey",
}
const OBSERVATIONS := {
	"quiet": "Three amber beacons blink in sequence across the near edge of the landing field.",
	"eclipse": "The eclipse shadow rolls over the crater. The landing lights are still visible in the dark.",
	"sunrise": "The high lip of the crater catches the sunlight first. A gold band creeps across the plain.",
	"impacts": "Pinpricks of light flicker on the plain. Tiny fans of dust arc out and settle.",
	"moonrise": "A small companion moon clears the far rim and passes beyond the launch doors.",
	"rover": "A survey rover rattles past the beacons on its way around the crater.",
}

var station: Node
var banks: Array[Rect2i] = []
var view := ""
var atlas: Texture2D
var elapsed := 0.0
var frame := 0

static func view_for(day: int) -> String:
	return EVENTS.get(posmod(maxi(day, 1) - 1, 28) + 1, "quiet")

func setup(clock: Node, rows: Array) -> void:
	station = clock
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	for y in rows.size():
		var row: String = rows[y]
		var x := 0
		while x < row.length():
			if row[x] != "w":
				x += 1
				continue
			var start := x
			while x < row.length() and row[x] == "w":
				x += 1
			banks.append(Rect2i(start, y - 1, x - start, 2))
	visibility_changed.connect(_sync_visibility)

func _sync_visibility() -> void:
	set_process(is_visible_in_tree())
	if is_processing():
		_process(0.0)

func _process(delta: float) -> void:
	var next := view_for(int(station.get("day")))
	if next != view:
		view = next
		atlas = load("res://art/lunar/bay_sky/%s.png" % view)
		elapsed = 0.0
		frame = -1
	var count := atlas.get_height() / FRAME_HEIGHT
	elapsed = fmod(elapsed + delta, count / FPS)
	var index := floori(elapsed * FPS)
	if index != frame:
		frame = index
		queue_redraw()

func _draw() -> void:
	if atlas == null:
		return
	for bank in banks:
		var dst := Rect2(bank.position * TILE, bank.size * TILE)
		var src := Rect2(bank.position.x * ART_TILE, frame * FRAME_HEIGHT, bank.size.x * ART_TILE, FRAME_HEIGHT)
		draw_texture_rect_region(atlas, dst, src)
