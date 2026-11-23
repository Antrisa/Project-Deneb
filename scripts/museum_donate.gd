extends CanvasLayer
# Donating relics, the Stardew Valley way (Zachary, 23 Nov: "like stardew when you talk to tarbesh, it kinda zooms out
# and you can move your mouse to select a case for item selected"). Talking to Tar'Besh (or using his desk) opens
# this: the camera pulls back to show every case, your relics sit in a bar along the bottom, and you place them
# with the mouse.
#   - Click a relic in the bar to hold it (the one selected on your hotbar starts held).
#   - Click an empty case to put the held relic in it.
#   - Click one of your own relics in a case to pick it up again (holding one swaps them), to regroup things.
#   - Tar'Besh's own pieces can't be moved.
#   - Right-click drops what you're holding (it stays in your bag); right-click again, Esc or E closes.
# main.gd owns the museum's state (museum_gifts, show_exhibit); this file only draws and takes clicks.

const ItemData = preload("res://scripts/item_data.gd")
const MapData = preload("res://scripts/map_data.gd")

const VIEW_ZOOM := 0.6                    # camera zoom while placing: the whole hall of cases fits the 640x360 view
const VIEW_CENTRE := Vector2(536, 366)    # world point in the middle of the cases (tiles 8-58 across, 8-36 down)
const BAR_H := 40.0                       # the relic bar along the bottom
const CELL := 30.0                        # one relic in the bar
const PANEL := Color("192c3b")            # as the station calendar
const EDGE := Color("6ebcc2")
const TEXT := Color("e4eee9")
const OK := Color("6ee08a")
const MINE := Color("f2c84b")
const NO := Color("d06060")

var world                                 # main.gd
var open := false
var held := ""                            # the relic id in your hand, or ""
var hover_slot := -1                      # the case under the mouse (index into MapData.MUSEUM_SLOTS)
var _canvas: Control
var _saved := {}                          # the camera as it was


func _ready() -> void:
	layer = 14
	_canvas = Control.new()
	_canvas.set_anchors_preset(Control.PRESET_FULL_RECT)
	_canvas.mouse_filter = Control.MOUSE_FILTER_STOP
	_canvas.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_canvas.draw.connect(_paint)
	_canvas.gui_input.connect(_on_gui)
	add_child(_canvas)
	visible = false


func start() -> void:
	var cam: Camera2D = world.player._cam
	_saved = {"zoom": cam.zoom, "pos": cam.position, "smooth": cam.position_smoothing_enabled,
		"limits": [cam.limit_left, cam.limit_top, cam.limit_right, cam.limit_bottom]}
	cam.limit_left = -100000
	cam.limit_top = -100000
	cam.limit_right = 100000
	cam.limit_bottom = 100000
	cam.position_smoothing_enabled = false
	cam.zoom = Vector2.ONE * VIEW_ZOOM
	cam.position = VIEW_CENTRE - world.player.global_position
	cam.reset_smoothing()
	held = world._relic_to_place()
	hover_slot = -1
	open = true
	visible = true


func close() -> void:
	if not open:
		return
	var cam: Camera2D = world.player._cam
	var lim: Array = _saved["limits"]
	cam.limit_left = int(lim[0])
	cam.limit_top = int(lim[1])
	cam.limit_right = int(lim[2])
	cam.limit_bottom = int(lim[3])
	cam.zoom = _saved["zoom"]
	cam.position = _saved["pos"]
	cam.position_smoothing_enabled = bool(_saved["smooth"])
	cam.reset_smoothing()
	open = false
	visible = false
	held = ""
	world._save_game()


func _process(_delta: float) -> void:
	if open:
		_canvas.queue_redraw()


# Keys come from main.gd's _unhandled_input while this is open.
func handle_input(ev: InputEvent) -> void:
	if ev.is_action_pressed("cancel") or ev.is_action_pressed("interact"):
		close()


func _on_gui(ev: InputEvent) -> void:
	var mb := ev as InputEventMouseButton
	if mb == null or not mb.pressed:
		return
	_canvas.accept_event()
	if mb.button_index == MOUSE_BUTTON_RIGHT:
		if held != "":
			held = ""
		else:
			close()
		return
	if mb.button_index != MOUSE_BUTTON_LEFT:
		return
	var p: Vector2 = mb.position
	# the bar: a relic, or Done
	if _done_rect().has_point(p):
		close()
		return
	var bag: Array = _bag()
	for i in bag.size():
		if _cell_rect(i).has_point(p):
			held = "" if held == bag[i] else str(bag[i])
			world.sfx("click")
			return
	var slot: int = _slot_at(p)
	if slot < 0:
		return
	var key := str(slot)
	if world.museum_gifts.has(key):
		# one of yours: pick it up, or swap it with the one in your hand
		var was: String = str(world.museum_gifts[key])
		world.museum_take(slot)
		if held != "":
			world.museum_place(held, slot)
		held = was
		world.sfx("click")
	elif str(MapData.MUSEUM_SLOTS[slot][4]) != "":
		world.sfx("deny")                 # Tar'Besh's own piece
	elif held != "":
		world.museum_place(held, slot)
		world.sfx("quest")
		held = held if world._count(held) > 0 else ""
	else:
		world.sfx("deny")


# ---------------------------------------------------------------- layout

# Your relics (in the bag), in item order.
func _bag() -> Array:
	var out: Array = []
	for id in ItemData.relics():
		if world._count(id) > 0:
			out.append(id)
	return out


func _bar_rect() -> Rect2:
	var s: Vector2 = _canvas.size
	return Rect2(8, s.y - BAR_H - 6, s.x - 16, BAR_H)


func _cell_rect(i: int) -> Rect2:
	var bar: Rect2 = _bar_rect()
	return Rect2(bar.position.x + 6 + i * (CELL + 4), bar.position.y + (BAR_H - CELL) * 0.5, CELL, CELL)


func _done_rect() -> Rect2:
	var bar: Rect2 = _bar_rect()
	return Rect2(bar.end.x - 58, bar.position.y + 9, 52, BAR_H - 18)


# A case's picture on screen (the camera does the zoom; the canvas transform maps world to screen).
func _case_rect(slot: int) -> Rect2:
	var at: Array = MapData.MUSEUM_SLOTS[slot]
	var sp: Sprite2D = world.museum_cases.get("%d:%d" % [int(at[0]), int(at[1])])
	if sp == null or sp.texture == null:
		return Rect2()
	var scl: Vector2 = sp.global_scale
	var top_left: Vector2 = sp.global_position + sp.offset * scl
	var size: Vector2 = Vector2(sp.texture.get_width(), sp.texture.get_height()) * scl
	var xf: Transform2D = sp.get_viewport().get_canvas_transform()
	var a: Vector2 = xf * top_left
	var b: Vector2 = xf * (top_left + size)
	return Rect2(a, b - a)


func _slot_at(p: Vector2) -> int:
	if _bar_rect().has_point(p):
		return -1
	for i in MapData.MUSEUM_SLOTS.size():
		if _case_rect(i).grow(2.0).has_point(p):
			return i
	return -1


# ---------------------------------------------------------------- drawing

func _paint() -> void:
	var font: Font = ThemeDB.fallback_font
	var mouse: Vector2 = _canvas.get_local_mouse_position()
	hover_slot = _slot_at(mouse)
	# every case: green if your held relic can go in, gold if it's one of yours
	for i in MapData.MUSEUM_SLOTS.size():
		var r: Rect2 = _case_rect(i)
		if r.size == Vector2.ZERO:
			continue
		var key := str(i)
		var own_piece: bool = str(MapData.MUSEUM_SLOTS[i][4]) != ""
		if world.museum_gifts.has(key):
			_canvas.draw_rect(r.grow(1), Color(MINE, 0.55), false, 1.0)
		elif not own_piece and held != "":
			_canvas.draw_rect(r.grow(1), Color(OK, 0.35), false, 1.0)
		if i == hover_slot:
			var c: Color = MINE if world.museum_gifts.has(key) else (NO if own_piece else (OK if held != "" else EDGE))
			_canvas.draw_rect(r.grow(2), c, false, 2.0)
	# the title along the top
	var top := Rect2(8, 6, _canvas.size.x - 16, 22)
	_canvas.draw_rect(top, Color(PANEL, 0.92))
	_canvas.draw_rect(top, EDGE, false, 1.0)
	var line := "Choose a case: click a relic below, then an empty case. Click yours to move them. Right-click or Esc when done."
	_canvas.draw_string(font, Vector2(top.position.x + 6, top.position.y + 15), line, HORIZONTAL_ALIGNMENT_LEFT, top.size.x - 12, 10, TEXT)
	# the bar of relics
	var bar: Rect2 = _bar_rect()
	_canvas.draw_rect(bar, Color(PANEL, 0.95))
	_canvas.draw_rect(bar, EDGE, false, 1.0)
	var bag: Array = _bag()
	if bag.is_empty() and held == "":
		_canvas.draw_string(font, Vector2(bar.position.x + 8, bar.position.y + 24), "No relics in your bag. You can still move the ones on show.",
				HORIZONTAL_ALIGNMENT_LEFT, bar.size.x - 80, 10, Color(TEXT, 0.7))
	for i in bag.size():
		var cr: Rect2 = _cell_rect(i)
		_canvas.draw_rect(cr, Color("223a4c"))
		_canvas.draw_rect(cr, MINE if bag[i] == held else Color(EDGE, 0.6), false, 2.0 if bag[i] == held else 1.0)
		_icon(str(bag[i]), cr.grow(-3))
	var done: Rect2 = _done_rect()
	_canvas.draw_rect(done, Color("2c5566") if not done.has_point(mouse) else Color("3d7488"))
	_canvas.draw_rect(done, EDGE, false, 1.0)
	_canvas.draw_string(font, Vector2(done.position.x, done.position.y + 15), "Done", HORIZONTAL_ALIGNMENT_CENTER, done.size.x, 11, TEXT)
	# what's under the mouse
	var tip := ""
	for i in bag.size():
		if _cell_rect(i).has_point(mouse):
			tip = str(ItemData.ITEMS[bag[i]]["name"])
	if hover_slot >= 0:
		var slot: Array = MapData.MUSEUM_SLOTS[hover_slot]
		var key := str(hover_slot)
		if world.museum_gifts.has(key):
			tip = "%s (yours: click to move)" % str(ItemData.ITEMS[str(world.museum_gifts[key])]["name"])
		elif str(slot[4]) != "":
			tip = "%s (Tar'Besh's)" % str(slot[3])
		else:
			tip = "Empty case: %s" % str(slot[2])
	if tip != "":
		var w: float = font.get_string_size(tip, HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x + 10
		var at := Vector2(clampf(mouse.x + 12, 4, _canvas.size.x - w - 4), clampf(mouse.y - 22, 32, bar.position.y - 20))
		_canvas.draw_rect(Rect2(at, Vector2(w, 16)), Color(PANEL, 0.95))
		_canvas.draw_rect(Rect2(at, Vector2(w, 16)), EDGE, false, 1.0)
		_canvas.draw_string(font, at + Vector2(5, 12), tip, HORIZONTAL_ALIGNMENT_LEFT, -1, 10, TEXT)
	# the held relic follows the mouse
	if held != "":
		_icon(held, Rect2(mouse - Vector2(12, 12), Vector2(24, 24)))


func _icon(id: String, r: Rect2) -> void:
	var tex: Texture2D = world.items_tex
	if tex == null or not ItemData.ITEMS.has(id):
		return
	var cell: int = tex.get_height()
	var icon: int = int(ItemData.ITEMS[id]["icon"])
	_canvas.draw_texture_rect_region(tex, r, Rect2(icon * cell, 0, cell, cell))
