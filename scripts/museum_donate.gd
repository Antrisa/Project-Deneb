extends CanvasLayer
# Donating relics, the Stardew Valley way (Zachary, 23 Nov: "like stardew when you talk to tarbesh, it kinda zooms out
# and you can move your mouse to select a case for item selected"), drawn in the Terran datapad style like the
# ship screens (Zachary: "every new thing have UI ... terran datapad style"). Talking to Tar'Besh (or using his
# desk) opens this: the camera pulls back to show every case, a datapad strip along the top says what to do, your
# relics sit in a datapad tray along the bottom, and you place them with the mouse.
#   - Click a relic in the tray to hold it (the one selected on your hotbar starts held).
#   - Click an empty case to put the held relic in it.
#   - Click one of your own relics in a case to pick it up again (holding one swaps them), to regroup things.
#   - Tar'Besh's own pieces can't be moved.
#   - Right-click drops what you're holding (it stays in your bag); right-click again, Esc, E or Done closes.
# main.gd owns the museum's state (museum_gifts, show_exhibit); this file only draws and takes clicks. The page is a
# ShipScreen without its case, so the museum shows through; cases are found by mapping their sprites onto the page.

const ItemData = preload("res://scripts/item_data.gd")
const MapData = preload("res://scripts/map_data.gd")
const ShipScreen = preload("res://ui/ship_screen.gd")

const VIEW_ZOOM := 0.6                    # camera zoom while placing: the whole hall of cases fits the view
const VIEW_CENTRE := Vector2(536, 366)    # world point in the middle of the cases (tiles 8-58 across, 8-36 down)
const CELL := 30.0                        # one relic in the tray
const OK := Color("5a9a68")
const MINE := Color("c9932f")
const NO := Color("b0473a")
const PAPER := Color("f4f1e8")

var world                                 # main.gd
var open := false
var held := ""                            # the relic id in your hand, or ""
var hover_slot := -1                      # the case under the mouse (index into MapData.MUSEUM_SLOTS)
var screen: ShipScreen
var _saved := {}                          # the camera as it was


func _ready() -> void:
	layer = 14
	screen = ShipScreen.new()
	add_child(screen)
	screen.fill = true
	screen.paint = Callable(self, "_paint")
	screen.on_click = Callable(self, "_click")
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
	screen.redraw()


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
		screen.redraw()


# Keys come from main.gd's _unhandled_input while this is open.
func handle_input(ev: InputEvent) -> void:
	if ev.is_action_pressed("cancel") or ev.is_action_pressed("interact"):
		close()


func _click(id: String, p: Vector2, button: int) -> void:
	if button == MOUSE_BUTTON_RIGHT:
		if held != "":
			held = ""
		else:
			close()
		return
	if button != MOUSE_BUTTON_LEFT:
		return
	if id == "done":
		close()
		return
	if id.begins_with("relic/"):
		var rid: String = id.get_slice("/", 1)
		held = "" if held == rid else rid
		world.sfx("click")
		return
	if id != "":
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
		held = held if world._count(held) > 0 else ""
	else:
		world.sfx("deny")


# ---------------------------------------------------------------- layout (page pixels)

# Your relics (in the bag), in item order.
func _bag() -> Array:
	var out: Array = []
	for id in ItemData.relics():
		if world._count(id) > 0:
			out.append(id)
	return out


func _top_rect() -> Rect2:
	return Rect2(10, 8, screen.page.x - 20, 30)


func _tray_rect() -> Rect2:
	return Rect2(10, screen.page.y - 54, screen.page.x - 20, 46)


func _cell_rect(i: int) -> Rect2:
	var tray: Rect2 = _tray_rect()
	return Rect2(tray.position.x + 10 + i * (CELL + 4), tray.position.y + 8, CELL, CELL)


func _done_rect() -> Rect2:
	var tray: Rect2 = _tray_rect()
	return Rect2(tray.end.x - 92, tray.position.y + 11, 82, 24)


# A case's picture on the page: its sprite on screen (the camera does the zoom), mapped back onto the page.
func _case_rect(slot: int) -> Rect2:
	var at: Array = MapData.MUSEUM_SLOTS[slot]
	var sp: Sprite2D = world.museum_cases.get("%d:%d" % [int(at[0]), int(at[1])])
	if sp == null or sp.texture == null:
		return Rect2()
	var scl: Vector2 = sp.global_scale
	var top_left: Vector2 = sp.global_position + sp.offset * scl
	var size: Vector2 = Vector2(sp.texture.get_width(), sp.texture.get_height()) * scl
	var to_view: Transform2D = sp.get_viewport().get_canvas_transform()
	var to_page: Transform2D = screen._layout.affine_inverse() * screen.get_global_transform().affine_inverse()
	var a: Vector2 = to_page * (to_view * top_left)
	var b: Vector2 = to_page * (to_view * (top_left + size))
	return Rect2(a, b - a).abs()


func _slot_at(p: Vector2) -> int:
	if _tray_rect().has_point(p) or _top_rect().has_point(p):
		return -1
	for i in MapData.MUSEUM_SLOTS.size():
		if _case_rect(i).grow(2.0).has_point(p):
			return i
	return -1


# ---------------------------------------------------------------- drawing

func _paint() -> void:
	var s := screen
	var mouse: Vector2 = s.mouse
	hover_slot = _slot_at(mouse)
	# every case: green if your held relic can go in, gold if it's one of yours
	for i in MapData.MUSEUM_SLOTS.size():
		var r: Rect2 = _case_rect(i)
		if r.size == Vector2.ZERO:
			continue
		var key := str(i)
		var own_piece: bool = str(MapData.MUSEUM_SLOTS[i][4]) != ""
		if world.museum_gifts.has(key):
			s.outline(r.grow(1), Color(MINE, 0.8))
		elif not own_piece and held != "":
			s.outline(r.grow(1), Color(OK, 0.7))
		if i == hover_slot:
			var c: Color = MINE if world.museum_gifts.has(key) else (NO if own_piece else (OK if held != "" else ShipScreen.ORANGE))
			s.outline(r.grow(3), c, 2.0)
	# the strip along the top: the datapad's header, and what to do
	var top: Rect2 = _top_rect()
	s.frame(top, PAPER)
	s.img("i_mark", Rect2(top.position.x + 8, top.position.y + 8, 13, 13), ShipScreen.OCHRE)
	s.text(top.position.x + 27, top.position.y + 7, "MUSEUM DONATIONS", "strong", ShipScreen.INK)
	var how := "Click a relic below, then an empty case. Click yours to move them. Right-click or Esc when done."
	s.text_fit(top.position.x + 190, top.position.y + 10, top.size.x - 200, how, "label", ShipScreen.MUTED)
	# the tray of relics
	var tray: Rect2 = _tray_rect()
	s.frame(tray, PAPER)
	var bag: Array = _bag()
	if bag.is_empty() and held == "":
		s.text(tray.position.x + 12, tray.position.y + 16, "No relics in your bag. You can still move the ones you've given.", "label", ShipScreen.MUTED)
	for i in bag.size():
		var cr: Rect2 = _cell_rect(i)
		var id: String = bag[i]
		var on: bool = id == held
		s.frame(cr, Color("fffdf5") if on else Color("ece9e0"), ShipScreen.ORANGE if on else Color("b5ac9e"))
		if on:
			s.outline(cr, ShipScreen.ORANGE, 2.0)
		_icon(id, cr.grow(-3))
		s.hit("relic/" + id, cr)
	if not bag.is_empty():
		s.text(_cell_rect(bag.size()).position.x + 4.0, tray.position.y + 17,
				"%d IN YOUR BAG   %d ON SHOW" % [bag.size(), world.museum_gifts.size()], "micro", ShipScreen.MUTED)
	s.solid_button("done", _done_rect(), "Done")
	# what's under the mouse
	var tip := ""
	for i in bag.size():
		if _cell_rect(i).has_point(mouse):
			tip = str(ItemData.ITEMS[bag[i]]["name"])
	if hover_slot >= 0:
		var slot: Array = MapData.MUSEUM_SLOTS[hover_slot]
		var key := str(hover_slot)
		if world.museum_gifts.has(key):
			tip = "%s  (yours: click to move)" % str(ItemData.ITEMS[str(world.museum_gifts[key])]["name"])
		elif str(slot[4]) != "":
			tip = "%s  (Tar'Besh's)" % str(slot[3])
		else:
			tip = "Empty case  -  %s" % str(slot[2])
	if tip != "":
		var w: float = s.width(tip, "label") + 14.0
		var at := Vector2(clampf(mouse.x + 12, 4, s.page.x - w - 4), clampf(mouse.y - 26, top.end.y + 4, tray.position.y - 24))
		s.frame(Rect2(at, Vector2(w, 20)), PAPER)
		s.text(at.x + 7, at.y + 4, tip, "label", ShipScreen.INK)
	# the held relic follows the mouse
	if held != "":
		_icon(held, Rect2(mouse - Vector2(12, 12), Vector2(24, 24)))


func _icon(id: String, r: Rect2) -> void:
	var tex: Texture2D = world.items_tex
	if tex == null or not ItemData.ITEMS.has(id):
		return
	var cell: int = tex.get_height()
	screen.texture(tex, r, Rect2(int(ItemData.ITEMS[id]["icon"]) * cell, 0, cell, cell))
