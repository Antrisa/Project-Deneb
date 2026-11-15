extends Control
# The hotbar (always on screen) and the menu (Tab or I): Inventory, Crafting, Map, Friends.
# Everything is drawn in _draw(); main.gd passes key presses to handle_input() while the menu is open.

const ItemData = preload("res://scripts/item_data.gd")
const MapData = preload("res://scripts/map_data.gd")
const NpcData = preload("res://scripts/npc_data.gd")

const SLOT := 18
const COLS := 8
const TABS := ["Inventory", "Crafting", "Map", "Friends"]
const HELP := [
	"Click or E: pick up, then again to put down or swap.    Click a page name or press 1-4.    Esc: close",
	"Click a recipe or press E to craft it.    Click a page name or press 1-4.    Esc: close",
	"Click a page name or press 1-4.    Esc or click outside: close",
	"One heart is 5 friendship. Talk each day and do requests.    Esc or click outside: close",
]
const PANEL := Rect2(10, 10, 300, 162)
const MAP_ORIGIN := Vector2(16, 32)
const HEART_POINTS := 5
const DIM := Color(0.6, 0.7, 0.85)
const GOLD := Color(1.0, 0.824, 0.498)
const EDGE := Color(0.4, 0.5, 0.7)

var world                    # main.gd
var open := false
var tab := 0
var cursor := 0              # inventory slot under the cursor
var held := -1               # slot picked up to move, or -1
var craft_cursor := 0

var _font: Font
var _items_tex: Texture2D
var _hearts_tex: Texture2D
var _map_tex: Texture2D
var _panel_tex: Texture2D     # art/ui_panel.png: a 3x3 grid, stretched to fit
var _slot_tex: Texture2D      # art/ui_slot.png: empty, selected, being moved
var _tab_tex: Texture2D       # art/ui_tab.png: not chosen, chosen
var _blink := 0.0
var _last_mouse := Vector2(-1, -1)


func _ready() -> void:
	_font = ThemeDB.fallback_font
	_items_tex = load("res://art/items.png")
	_panel_tex = load("res://art/ui_panel.png")
	_slot_tex = load("res://art/ui_slot.png")
	_tab_tex = load("res://art/ui_tab.png")
	_hearts_tex = load("res://art/hearts.png")
	_map_tex = load("res://art/station_map.png")
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size = Vector2(320, 180)


func _process(delta: float) -> void:
	_blink += delta
	# Moving the mouse moves the cursor in the menu (the keyboard still works too).
	if open:
		var at: Vector2 = mouse()
		if at != _last_mouse:
			_last_mouse = at
			if tab == 0:
				var slot: int = _inventory_slot_at(at)
				if slot != -1:
					cursor = slot
			elif tab == 1:
				var recipe: int = _recipe_at(at)
				if recipe != -1:
					craft_cursor = recipe
	queue_redraw()


# ---------------------------------------------------------------- mouse

func mouse() -> Vector2:
	return get_local_mouse_position()


func _hotbar_origin() -> Vector2:
	return Vector2(320 - 4 - COLS * SLOT, 180 - 2 - SLOT)


func hotbar_slot_at(at: Vector2) -> int:
	var origin: Vector2 = _hotbar_origin()
	if at.y < origin.y or at.y >= origin.y + SLOT or at.x < origin.x:
		return -1
	var slot: int = int((at.x - origin.x) / SLOT)
	return slot if slot < COLS else -1


func _menu_button_rect() -> Rect2:
	var origin: Vector2 = _hotbar_origin()
	return Rect2(origin.x - 24, origin.y, 22, SLOT)


func menu_button_at(at: Vector2) -> bool:
	return _menu_button_rect().has_point(at)


func _inventory_slot_pos(i: int) -> Vector2:
	var col: int = i % COLS
	var row: int = i / COLS
	var gap: int = 6 if row > 0 else 0
	return Vector2(80, 38) + Vector2(col * 20, row * 20 + gap)


func _inventory_slot_at(at: Vector2) -> int:
	for i in world.slots.size():
		if Rect2(_inventory_slot_pos(i), Vector2(SLOT, SLOT)).has_point(at):
			return i
	return -1


func _recipe_at(at: Vector2) -> int:
	for i in ItemData.RECIPES.size():
		if Rect2(16, 36.0 + i * 26.0, 288, 22).has_point(at):
			return i
	return -1


# A click while the menu is open.
func handle_click(button: int) -> void:
	if button != MOUSE_BUTTON_LEFT:
		return
	var at: Vector2 = mouse()
	if not PANEL.has_point(at):
		open = false
		held = -1
		world.sfx("click", 0.8)
		return
	if at.y >= 13.0 and at.y <= 26.0:
		for i in TABS.size():
			var x: float = 16.0 + i * 72.0
			if at.x >= x - 3.0 and at.x < x + 65.0:
				tab = i
				held = -1
				world.sfx("click", 1.2, -6.0)
		return
	if tab == 0:
		var slot: int = _inventory_slot_at(at)
		if slot != -1:
			cursor = slot
			_pick_or_put()
	elif tab == 1:
		var recipe: int = _recipe_at(at)
		if recipe != -1:
			craft_cursor = recipe
			world.craft(recipe)


func _pick_or_put() -> void:
	if held == -1:
		var item: String = world.slots[cursor]
		if item != "":
			held = cursor
			world.sfx("click", 1.2)
	else:
		world.swap_slots(held, cursor)
		held = -1
		world.sfx("click", 0.9)


func show_menu() -> void:
	open = true
	held = -1


# ---------------------------------------------------------------- input (menu open)

func handle_input(event: InputEvent) -> void:
	if event.is_action_pressed("menu") or event.is_action_pressed("cancel"):
		open = false
		held = -1
		world.sfx("click", 0.8)
		return
	var key_event := event as InputEventKey
	if key_event != null and key_event.pressed and not key_event.echo:
		var key: int = key_event.physical_keycode
		if key >= KEY_1 and key <= KEY_4:
			tab = key - KEY_1
			held = -1
			world.sfx("click", 1.2, -6.0)
			return
	if tab == 0:
		_inventory_input(event)
	elif tab == 1:
		_crafting_input(event)


func _inventory_input(event: InputEvent) -> void:
	var count: int = world.slots.size()
	if event.is_action_pressed("move_left", true):
		cursor = cursor - 1 if cursor % COLS > 0 else cursor + COLS - 1
	elif event.is_action_pressed("move_right", true):
		cursor = cursor + 1 if cursor % COLS < COLS - 1 else cursor - (COLS - 1)
	elif event.is_action_pressed("move_up", true):
		if cursor >= COLS:
			cursor -= COLS
	elif event.is_action_pressed("move_down", true):
		if cursor + COLS < count:
			cursor += COLS
	elif event.is_action_pressed("interact"):
		_pick_or_put()


func _crafting_input(event: InputEvent) -> void:
	var count: int = ItemData.RECIPES.size()
	if event.is_action_pressed("move_up", true):
		craft_cursor = (craft_cursor + count - 1) % count
	elif event.is_action_pressed("move_down", true):
		craft_cursor = (craft_cursor + 1) % count
	elif event.is_action_pressed("interact"):
		world.craft(craft_cursor)


# ---------------------------------------------------------------- drawing

func _draw() -> void:
	if world == null:
		return
	if open:
		_draw_menu()
	elif not world.dialogue.active:
		_draw_hotbar()


func _txt(pos: Vector2, s: String, color: Color = Color.WHITE, font_size: int = 8) -> void:
	draw_string(_font, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, color)


# Draws a picture laid out as a 3x3 grid so its corners stay sharp and the rest stretches.
func _nine(tex: Texture2D, r: Rect2, corner: float) -> void:
	var cw: float = tex.get_width() / 3.0
	var ch: float = tex.get_height() / 3.0
	var xs: Array = [r.position.x, r.position.x + corner, r.end.x - corner, r.end.x]
	var ys: Array = [r.position.y, r.position.y + corner, r.end.y - corner, r.end.y]
	for j in 3:
		for i in 3:
			var x0: float = xs[i]
			var x1: float = xs[i + 1]
			var y0: float = ys[j]
			var y1: float = ys[j + 1]
			draw_texture_rect_region(tex, Rect2(x0, y0, x1 - x0, y1 - y0), Rect2(i * cw, j * ch, cw, ch))


# Draws one picture of ui_tab.png (0 not chosen, 1 chosen); its middle third stretches sideways.
func _tab(r: Rect2, chosen: int) -> void:
	var fw: float = _tab_tex.get_width() / 2.0
	var third: float = fw / 3.0
	var h: float = _tab_tex.get_height()
	var xs: Array = [r.position.x, r.position.x + 4.0, r.end.x - 4.0, r.end.x]
	for i in 3:
		var x0: float = xs[i]
		var x1: float = xs[i + 1]
		draw_texture_rect_region(_tab_tex, Rect2(x0, r.position.y, x1 - x0, r.size.y), Rect2(chosen * fw + i * third, 0, third, h))


# state: 0 empty slot look, 1 selected, 2 being moved
func _draw_slot(pos: Vector2, item: String, state: int) -> void:
	var fw: float = _slot_tex.get_width() / 3.0
	draw_texture_rect_region(_slot_tex, Rect2(pos, Vector2(SLOT, SLOT)), Rect2(state * fw, 0, fw, _slot_tex.get_height()))
	if item == "":
		return
	var info: Dictionary = ItemData.ITEMS[item]
	var icon: int = info["icon"]
	draw_texture_rect_region(_items_tex, Rect2(pos + Vector2(1, 1), Vector2(16, 16)), Rect2(icon * _items_tex.get_height(), 0, _items_tex.get_height(), _items_tex.get_height()))
	var n: int = world.count_of(item)
	if n > 1:
		var label: String = str(n)
		var w: float = 4.0 * label.length() + 1.0
		draw_rect(Rect2(pos + Vector2(SLOT - 1 - w, SLOT - 8), Vector2(w, 7)), Color(0, 0, 0, 0.65))
		_txt(pos + Vector2(SLOT - w, SLOT - 2), label, Color.WHITE, 6)


func _draw_hotbar() -> void:
	var origin: Vector2 = _hotbar_origin()
	for i in COLS:
		var item: String = world.slots[i]
		_draw_slot(origin + Vector2(i * SLOT, 0), item, 1 if i == world.selected else 0)
	# Health: ten hearts above the hotbar.
	for h in 10:
		draw_texture_rect_region(_hearts_tex, Rect2(316 - 80 + h * 8, origin.y - 9, 7, 6), Rect2(0.0 if h < world.hp else _hearts_tex.get_width() / 2.0, 0, _hearts_tex.get_width() / 2.0, _hearts_tex.get_height()))
	# A small button to open the menu with the mouse.
	var button: Rect2 = _menu_button_rect()
	_tab(button, 0)
	_txt(button.position + Vector2(3, 12), "Menu", DIM, 6)
	var chosen: String = world.slots[world.selected]
	if chosen != "":
		var info: Dictionary = ItemData.ITEMS[chosen]
		var item_name: String = info["name"]
		_txt(origin + Vector2(1, -3), item_name, GOLD, 6)


func _draw_menu() -> void:
	_nine(_panel_tex, PANEL, 8.0)
	for i in TABS.size():
		var x: float = 16.0 + i * 72.0
		_tab(Rect2(x - 3, 13, 68, 13), 1 if i == tab else 0)
		var tab_name: String = TABS[i]
		_txt(Vector2(x, 22), "%d %s" % [i + 1, tab_name], Color.WHITE if i == tab else DIM)
	draw_line(Vector2(10, 27), Vector2(310, 27), Color("7fd4ff"), 1.0)
	var help: String = HELP[tab]
	_txt(Vector2(16, 169), help, DIM, 6)
	if tab == 0:
		_draw_inventory()
	elif tab == 1:
		_draw_crafting()
	elif tab == 2:
		_draw_map()
	else:
		_draw_friends()


func _draw_inventory() -> void:
	_txt(Vector2(16, 50), "Hotbar", DIM, 6)
	_txt(Vector2(16, 76), "Pack", DIM, 6)
	_txt(Vector2(246, 50), "%d credits" % world.credits, GOLD)
	for i in world.slots.size():
		var state := 0
		if i == held:
			state = 2
		if i == cursor:
			state = 1
		var item: String = world.slots[i]
		_draw_slot(_inventory_slot_pos(i), item, state)
	var under: String = world.slots[cursor]
	if under != "":
		var info: Dictionary = ItemData.ITEMS[under]
		_txt(Vector2(16, 122), "%s   x%d" % [info["name"], world.count_of(under)], GOLD)
		var desc: String = info["desc"]
		draw_multiline_string(_font, Vector2(16, 132), desc, HORIZONTAL_ALIGNMENT_LEFT, 288, 6, 3, Color.WHITE)
	elif held != -1:
		_txt(Vector2(16, 122), "Choose where to put it, then press E.", DIM, 6)


func _draw_crafting() -> void:
	for i in ItemData.RECIPES.size():
		var recipe: Dictionary = ItemData.RECIPES[i]
		var makes: String = recipe["makes"]
		var needs: Dictionary = recipe["needs"]
		var y: float = 36.0 + i * 26.0
		_draw_slot(Vector2(18, y), makes, 1 if i == craft_cursor else 0)
		var info: Dictionary = ItemData.ITEMS[makes]
		var item_name: String = info["name"]
		_txt(Vector2(42, y + 8), item_name, Color.WHITE if i == craft_cursor else DIM)
		var ok := true
		var parts := PackedStringArray()
		for item in needs:
			var need: int = needs[item]
			var have: int = world.count_of(item)
			if have < need:
				ok = false
			var need_info: Dictionary = ItemData.ITEMS[item]
			parts.append("%d %s (you have %d)" % [need, need_info["name"], have])
		_txt(Vector2(42, y + 16), "Needs " + ", ".join(parts), Color("b8f0b0") if ok else Color("f08a80"), 6)
	_txt(Vector2(16, 150), "Ore becomes bars in ore processing on the Engineering Level. Bars become parts here.", DIM, 6)


func _map_point(area_name: String, tx: float, ty: float) -> Vector2:
	var layout: Array = MapData.MAP_LAYOUT[area_name]
	var scale_px: float = layout[2]
	return MAP_ORIGIN + Vector2(float(layout[0]) + tx * scale_px, float(layout[1]) + ty * scale_px)


func _draw_map() -> void:
	draw_texture(_map_tex, MAP_ORIGIN)
	for t in MapData.MAP_TITLES:
		var title: String = t[0]
		_txt(MAP_ORIGIN + Vector2(float(t[1]), float(t[2])), title, Color("9fdcff"), 6)
	var line := 0
	for mark in MapData.MAP_MARKS:
		var mark_area: String = mark[1]
		var p: Vector2 = _map_point(mark_area, float(mark[2]), float(mark[3]))
		var label: String = str(int(mark[0]))
		var place: String = mark[4]
		draw_rect(Rect2(p + Vector2(-1, -6), Vector2(4.0 * label.length() + 1.0, 7)), Color(0, 0, 0, 0.7))
		_txt(p, label, GOLD, 6)
		_txt(Vector2(218, 38 + line * 7), label, GOLD, 6)
		_txt(Vector2(230, 38 + line * 7), place, Color.WHITE, 6)
		line += 1
	for r in world.residents:
		var r_area: String = r.area
		var r_tile: Vector2i = r.tile
		var rp: Vector2 = _map_point(r_area, r_tile.x, r_tile.y)
		draw_rect(Rect2(rp - Vector2(1, 1), Vector2(2, 2)), Color("7fd4ff"))
	var here: Vector2i = world.player_tile()
	var area_now: String = world.current_area
	var pp: Vector2 = _map_point(area_now, here.x, here.y)
	if int(_blink * 3.0) % 2 == 0:
		draw_rect(Rect2(pp - Vector2(2, 2), Vector2(4, 4)), Color.WHITE)
	draw_rect(Rect2(pp - Vector2(1, 1), Vector2(2, 2)), Color("ff6b6b"))
	_txt(Vector2(218, 158), "You: red     Residents: blue", DIM, 6)


func _draw_friends() -> void:
	var i := 0
	for who in NpcData.PEOPLE:
		if not world.persons.has(who):
			continue
		var st: Dictionary = world.persons[who]
		var x: float = 12.0 + (i / 5) * 100.0
		var y: float = 32.0 + (i % 5) * 26.0
		var portrait: Texture2D = st["portrait"]
		var side: float = portrait.get_height()      # each picture is square; the first is neutral
		draw_texture_rect_region(portrait, Rect2(x, y, 24, 24), Rect2(0, 0, side, side))
		draw_rect(Rect2(x - 0.5, y - 0.5, 25, 25), EDGE, false, 1.0)
		var met: bool = st["met"]
		var shown_name: String = who if met else "???"
		_txt(Vector2(x + 30, y + 9), shown_name, Color.WHITE if met else DIM)
		var points: int = st["friendship"]
		var hearts: int = mini(10, points / HEART_POINTS)
		for h in 10:
			draw_texture_rect_region(_hearts_tex, Rect2(x + 30 + h * 6.5, y + 14, 6, 5), Rect2(0.0 if h < hearts else _hearts_tex.get_width() / 2.0, 0, _hearts_tex.get_width() / 2.0, _hearts_tex.get_height()))
		if st["talked_today"]:
			draw_rect(Rect2(x + 19, y + 1, 4, 4), Color("7ee07a"))      # green dot: talked to today
		i += 1
