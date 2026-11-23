extends Control

signal item_used(item_id: String)
signal craft_requested(recipe_index: int)
signal purchase_requested(item_id: String, unit_price: int)
# Echo Landing shops (23 Nov): a button on the Shop page was pressed; action is "<verb>/<key>" (scripts/shops.gd).
signal shop_action(action: String)
signal hotbar_changed(slots: Array, selected_slot: int)
signal menu_changed(page_name: String)
signal setting_changed(setting: String, enabled: bool)
signal dialogue_advanced
signal recap_closed
signal journal_tracked(index: int)
signal emote_selected(id: String)
signal equipment_changed(slots: Dictionary)
signal discard_requested(item_id: String, amount: int)
signal quit_requested
signal resume_requested
signal slots_swapped(a: int, b: int)
signal storage_moved(item_id: String, to_chest: bool)

const Art = preload("res://datapad/art.gd")
const Sample = preload("res://datapad/catalog.gd")
const PixelGrid = preload("res://ui/pixel_grid.gd")
const INK := "#373b36"
const MUTED := "#595e55"
const RULE := "#cbc7ba"
const IVORY := "#fffdf7"
const PAPER := "#f7f6f0"
const OCHRE := "#a45736"
const ORANGE := "#ac5c36"
const APRICOT := "#deaa80"
const DARK := "#363d36"
const TEAL := "#69877d"
const TABS := ["Inventory","Crafting","Skills","Crew","Map","Journal","System"]
const TAB_LINERS := {"Inventory":"inventory_liner","Crafting":"mod_workshop","Skills":"mod_training","Crew":"mod_residents","Map":"mod_navigation","Journal":"mod_requests","System":"mod_preferences","Relics":"mod_custodians"}
const TAB_NAMES := ["Inventory","Crafting","Skills","NPC relations","Map","Quests","Settings"]
const TAB_ICONS := ["inventory","craft","skills","crew","map","journal","system"]
# Weapons and tools live on the quick slots (the hotbar), so the gear page has no slots for them (22 Nov).
# Echo Landing (23 Nov): armour on the left (head, body, boots), clothes that show over it on the right (hat,
# outfit), the laser's parts below. The rings are gone. Wearables are in scripts/shop_data.gd WEAR.
const GEAR_SLOTS := [
	["head","Head","head","Head armour"],["armor","Armour","armor","Body armour"],["boots","Boots","boots","Boots"],
	["hat","Hat","hat","Hat (shows over your armour)"],["outfit","Outfit","outfit","Outfit (shows over your armour)"],
	["lens","Lens","lens","Laser lens"],["power","Power pack","power","Laser power pack"]]
var gear_types: Dictionary = Sample.GEAR_TYPES.duplicate()
var equipment: Dictionary = {}
var player_sprite := "player_front"
var skills: Array = Sample.SKILLS.duplicate(true)
var skill_index := 0
var custodians: Array = preload("res://datapad/relics.gd").CUSTODIANS.duplicate(true)
var relic_progress: Dictionary = {}
var relic_index := 0
var bundle_index := 0
var _relic_parent := "Inventory"
var _overlay := ""
var _overlay_id := ""
var _choice_page := 0
var _pressed_item := ""

var catalog: Dictionary = Sample.ITEMS.duplicate(true)
var recipes: Array = Sample.RECIPES.duplicate(true)
var crew: Array = Sample.CREW.duplicate(true)
var jobs: Array = Sample.JOBS.duplicate(true)
var places: Array = Sample.PLACES.duplicate(true)
var item_counts: Dictionary = {}
var hotbar: Array = ["","","","","","","",""]
var active_slot := 0
var health := 10
var max_health := 10
var energy := 100
var max_energy := 100
var station_scrip := 0:
	set(value):
		station_scrip = value
		if is_node_ready():
			refresh()
var minutes := 610
var calendar_day := 6
var season := "Spring"
var location_name := "Engineering"
var page := "HUD"
var bag_filter := "All"
var item_selection := ""
var recipe_filter := "All"
var material_page := 0
var nearby_crafting_stations: Variant = null
var produce_items: Array = ["berry"]
var known_gifts: Dictionary = {}
var gift_page := 0
var control_scheme := "Keys"
var _map_parent := "HUD"
var recipe_index := 0
var place_index := 1
# The sector map (the level you are on), set by the game: its picture is extra_textures["sector_map"].
var sector_title := ""
var sector_size := Vector2.ZERO          # the picture's size here, in datapad pixels
var sector_marks: Array = []             # [position on the picture, label]
var sector_people: Array = []            # [position, name]
var sector_you := Vector2(-1, -1)
var mark_index := -1
var mark_page := 0
var crew_index := 0
var job_index := 0
var tracked := -1
@export var hud_use_shortcut := false
var hints := true
var scenery := true
var bag_page := 0
var inventory_capacity := 24
# The bag as the game keeps it (main.gd slots): which item is in each slot, the first 8 being the quick
# slots. Click an item to pick it up, click another slot to put it there (swapping), as in Stardew.
var bag_slots: Array = []
var _held := -1              # the bag slot whose item is being carried by the pointer (-1: none)
var _mouse_ui := Vector2.ZERO
# Echo Landing shops (23 Nov): tabs of rows, filled by scripts/shops.gd. Each tab is [name, rows]; each row is
# [icon id, title, subtitle, price text, buttons], each button [action, label, enabled].
var shop_tabs: Array = []
var shop_tab := 0
# A chest you built (23 Nov): the Storage page lists your bag and the chest side by side, four rows a page;
# Store / Take move a whole stack across (main.gd chest_move).
var storage_name := ""
var storage_chest: Array = []     # [[item id, count], ...]
var storage_bag: Array = []
var storage_page_bag := 0
var storage_page_chest := 0
var shop_page := 0
var shop_name := "Station supplies"
var dialogue: Dictionary = {}
var recap: Dictionary = {}
var _toast := ""
var _toast_seconds := 0.0
var _layout := Transform2D.IDENTITY
var _bounds := Rect2i(0, 0, 768, 432)
var _target := SubViewport.new()
var _raster := Node2D.new()
var _focus_id := ""
var _hover_id := ""
var _return_page := "HUD"
var commands: Array = []
var hits: Array = []
var extra_textures: Dictionary = {}
# Echo Landing: text is drawn with a real font at the screen's own pixel size, so it stays sharp. The pack's
# bitmap fonts were smoothed at 7 to 9 pixels tall and looked fuzzy once enlarged; only the pixel-perfect
# "micro" font is still drawn from its bitmap. Sizes and baselines (UI pixels) match each bitmap font's capital
# height and baseline, and each glyph is centred in the bitmap font's advance, so every layout measurement
# (_width, _wrap_lines) still holds.
const TEXT_SIZE := {"label": 11.2, "body": 12.6, "strong": 14.0, "mid": 18.2, "title": 25.2, "clock": 21.0}
const TEXT_BASE := {"label": 12, "body": 14, "strong": 15, "mid": 20, "title": 27, "clock": 20}
const TEXT_BOLD := ["strong", "title", "clock"]
var _px := 1.0                 # screen pixels per UI pixel; the off-screen picture is drawn at this size
var _font: Font
var _font_bold: Font
const EMOTES := ["surprise","question","love","joy","sad","frustrated","hello","ready","no","wait","help","follow","cute"]
var _system_parent := "HUD"

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_ALL
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	# Compose all bitmap glyphs, strokes and thumbnail resizes on the same native grid.
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
	resized.connect(refresh)
	get_viewport().size_changed.connect(refresh)
	refresh()

func set_vitals(hp: int, hp_max: int, charge: int, charge_max: int) -> void:
	max_health = maxi(1,hp_max)
	health = clampi(hp,0,max_health)
	max_energy = maxi(1,charge_max)
	energy = clampi(charge,0,max_energy)
	refresh()

func set_clock(total_minutes: int, day: int, season_name: String) -> void:
	minutes = posmod(total_minutes,1440)
	calendar_day = maxi(1,day)
	season = season_name
	refresh()

func set_inventory(counts: Dictionary, slots: Array, selected: int = 0) -> void:
	item_counts = counts.duplicate()
	var before := equipment.duplicate()
	var reserved := {}
	for key in equipment.keys():
		var id:String=equipment[key]
		if int(item_counts.get(id,0))<=int(reserved.get(id,0)):
			equipment.erase(key)
		else:
			reserved[id]=int(reserved.get(id,0))+1
	if before!=equipment: equipment_changed.emit(equipment.duplicate())
	hotbar = slots.duplicate()
	hotbar.resize(8)
	for i in 8:
		if hotbar[i] == null or not catalog.has(hotbar[i]) or int(item_counts.get(hotbar[i],0)) <= 0:
			hotbar[i] = ""
	active_slot = clampi(selected,0,7)
	if int(item_counts.get(item_selection,0)) <= 0:
		item_selection = ""
	refresh()

func add_item_definition(id: String, name_text: String, category: String, kind: String, description: String, icon: Texture2D) -> void:
	catalog[id] = [name_text,category,kind,description]
	extra_textures[id] = icon
	refresh()

func show_page(key: String) -> void:
	key = {"Quests":"Journal","NPC relations":"Crew","Settings":"System"}.get(key,key)
	if key != "HUD" and key!="Relics" and not key in TABS and not key in ["Shop","Storage","Recap","Dialogue","Pause","Emotes"]:
		return
	_overlay=""
	_pressed_item=""
	_held=-1
	page = key
	_focus_id = ""
	_hover_id = ""
	if page == "Inventory":
		_ensure_item()
	refresh()
	menu_changed.emit(page)

func show_dialogue(speaker: String, message: String, portrait_key: String = "") -> void:
	_return_page = page if (page in TABS or page=="Relics") else "HUD"
	dialogue = {"speaker":speaker,"lines":_dialogue_pages(message),"index":0,"portrait":portrait_key}
	show_page("Dialogue")

func show_shop(merchant: String, tabs: Array, keep_place := false) -> void:
	if page!="Shop":
		_return_page = page if (page in TABS or page=="Relics") else "HUD"
	shop_name = merchant
	shop_tabs = tabs.duplicate(true)
	if not keep_place:
		shop_tab=0
		shop_page=0
	shop_tab=clampi(shop_tab,0,maxi(0,shop_tabs.size()-1))
	shop_page=clampi(shop_page,0,maxi(0,ceili(_shop_rows().size()/4.0)-1))
	if page=="Shop": refresh()
	else: show_page("Shop")

func _shop_rows() -> Array:
	if shop_tab<0 or shop_tab>=shop_tabs.size(): return []
	return shop_tabs[shop_tab][1]

func show_storage(title: String, chest_list: Array, bag_list: Array) -> void:
	_return_page = page if (page in TABS or page=="Relics") else "HUD"
	storage_name = title
	storage_page_bag = 0
	storage_page_chest = 0
	set_storage(chest_list, bag_list)
	show_page("Storage")

func set_storage(chest_list: Array, bag_list: Array) -> void:
	storage_chest = chest_list.duplicate(true)
	storage_bag = bag_list.duplicate(true)
	storage_page_bag = clampi(storage_page_bag, 0, maxi(0, ceili(storage_bag.size()/4.0)-1))
	storage_page_chest = clampi(storage_page_chest, 0, maxi(0, ceili(storage_chest.size()/4.0)-1))
	if page == "Storage": refresh()

func show_recap(day_label: String, earned: int, spent: int) -> void:
	_return_page = page if (page in TABS or page=="Relics") else "HUD"
	recap = {"day":day_label,"earned":earned,"spent":spent}
	show_page("Recap")

func notify_player(message: String) -> void:
	_toast = message
	_toast_seconds = 2.0
	refresh()

func _process(delta: float) -> void:
	if _toast_seconds > 0:
		_toast_seconds -= delta
		if _toast_seconds <= 0:
			_toast = ""
			refresh()

func refresh() -> void:
	if not is_node_ready():
		return
	_layout = PixelGrid.layout(self)
	var extent := _layout.affine_inverse() * Rect2(Vector2.ZERO, size)
	var first := Vector2i(extent.position.floor())
	var last := Vector2i(extent.end.ceil())
	_bounds = Rect2i(first, (last - first).max(Vector2i.ONE))
	# Echo Landing: compose at the screen's pixel size (art still enlarged with hard edges), so text is sharp.
	_px = maxf(1.0, (get_viewport_transform() * get_global_transform() * _layout).get_scale().x)
	var native := Vector2i((Vector2(_bounds.size) * _px).ceil())
	if _target.size != native:
		_target.size = native
	_raster.scale = Vector2(_px, _px)
	_raster.position = -Vector2(_bounds.position) * _px
	commands.clear()
	hits.clear()
	if page in ["HUD","Dialogue","Pause","Emotes"]:
		_hud()
		if page == "Dialogue": _dialog()
		if page == "Pause": _pause_menu()
		if page == "Emotes": _emotes()
	else:
		_shell()
		match page:
			"Inventory": _inventory()
			"Skills": _skills_page()
			"Relics": _relic_page()
			"Crafting": _craft()
			"Map": _map_page()
			"Journal": _journal()
			"Crew": _crew()
			"System": _system()
			"Shop": _shop()
			"Storage": _storage()
			"Recap": _recap()
	if _toast != "" and page != "Dialogue" and _overlay=="":
		var tw := mini(500,_width(_toast,"label")+26)
		_rect((768-tw)/2,353,tw,20,DARK)
		_txt((768-tw)/2+13,355,_toast,"label",IVORY)
	if page=="Inventory" and _held>=0 and _overlay=="" and _bag_item(_held)!="":
		_img(_bag_item(_held),int(_mouse_ui.x)-14,int(_mouse_ui.y)-14,29,29)
	if _overlay!="": _overlay_draw()
	for h in hits:
		if h[0] == _focus_id or h[0] == _hover_id:
			_outline(h[1]+1,h[2]+1,h[3]-2,h[4]-2,ORANGE)
	_raster.queue_redraw()
	_target.render_target_update_mode = SubViewport.UPDATE_ONCE
	queue_redraw()

func _rect(x,y,w,h,col) -> void:
	if w>0 and h>0: commands.append(["r",int(x),int(y),int(w),int(h),col])
func _outline(x,y,w,h,col) -> void:
	_rect(x,y,w,1,col); _rect(x,y+h-1,w,1,col); _rect(x,y,1,h,col); _rect(x+w-1,y,1,h,col)
# A one-pixel inside bevel, shared by keycaps, recessed equipment slots and list rows.
func _bevel(x:int,y:int,w:int,h:int,top_left:String,bottom_right:String) -> void:
	_rect(x+1,y,w-2,1,top_left)
	_rect(x,y+1,1,h-2,top_left)
	_rect(x+1,y+h-1,w-2,1,bottom_right)
	_rect(x+w-1,y+1,1,h-2,bottom_right)

func _img(id,x,y,w,h,col="#ffffff") -> void:
	if Art.TEXTURES.has(id) or extra_textures.has(id):
		commands.append(["i",id,int(x),int(y),int(w),int(h),col])
func _txt(x,y,s,font="body",col=INK) -> void: commands.append(["t",int(x),int(y),str(s),font,col])
func _width(s: String,font: String) -> int:
	var total := 0
	for i in s.length():
		total += int(Art.FONTS[font].advance[clampi(s.unicode_at(i)-32,0,94)])
	return total
func _right(edge,y,s,font="body",col=INK) -> void: _txt(edge-_width(str(s),font),y,s,font,col)
func _wrap_lines(s: String, w: int, font: String) -> Array:
	var lines: Array = []
	for para in s.split("\n"):
		var ln := ""
		for word in para.split(" ", false):
			if ln!="" and _width(ln+" "+word,font)>w:
				lines.append(ln)
				ln=word
			else: ln=word if ln=="" else ln+" "+word
		lines.append(ln)
	return lines
func _wrap(x,y,w,s,font="body",col=INK,gap=18) -> void:
	for ln in _wrap_lines(s,w,font):
		_txt(x,y,ln,font,col)
		y+=gap
func _dialogue_pages(message: String) -> Array:
	var lines := _wrap_lines(message,410,"body")
	var pages: Array=[]
	for i in range(0,lines.size(),2):
		pages.append("\n".join(lines.slice(i,mini(i+2,lines.size()))))
	return pages
func _hit(id,x,y,w,h) -> void: hits.append([str(id),int(x),int(y),int(w),int(h)])
func _btn(id,x,y,w,h,label,primary=false,enabled=true) -> void:
	var color = ORANGE if primary else "#f1eee7"
	if not enabled: color = "#e6e4de"
	_rect(x,y,w,h,color)
	_outline(x,y,w,h,"#aa917c" if not primary else "#864c35")
	_bevel(x+1,y+1,w-2,h-2,"#e6ac84" if primary else "#fffdf5","#985434" if primary else "#d4ccbe")
	var col = IVORY if primary else INK
	if not enabled: col=MUTED
	_txt(x+(w-_width(label,"label"))/2,y+(h-16)/2,label,"label",col)
	if enabled: _hit(id,x,y,w,h)

func _draw() -> void:
	if not is_instance_valid(_target) or not _target.is_inside_tree():
		return
	draw_set_transform_matrix(_layout)
	draw_texture_rect(_target.get_texture(), Rect2(_bounds), false)

func _paint_native() -> void:
	for c in commands:
		match c[0]:
			"r": _raster.draw_rect(Rect2(c[1],c[2],c[3],c[4]),Color(c[5]))
			"i":
				# Echo Landing: pictures the game registers (add_item_definition, set_player_portrait) win over the
				# pack's sample art with the same name (laser, ration, quartz), so the game's own icons show.
				var tx: Texture2D=extra_textures.get(c[1],Art.TEXTURES.get(c[1]))
				_raster.draw_texture_rect(tx,Rect2(c[2],c[3],c[4],c[5]),false,Color(c[6]))
			"t":
				var x: int=c[1]
				var value: String=c[3]
				var f: Dictionary=Art.FONTS[c[4]]
				var color:=Color(c[5])
				if TEXT_SIZE.has(c[4]) and _font != null:
					var font: Font = _font_bold if c[4] in TEXT_BOLD else _font
					var font_size: int = maxi(1, roundi(float(TEXT_SIZE[c[4]]) * _px))
					var base_y: float = roundf((float(c[2]) + float(TEXT_BASE[c[4]])) * _px)
					_raster.draw_set_transform(Vector2.ZERO, 0.0, Vector2(1.0 / _px, 1.0 / _px))
					for i in value.length():
						var idx:=clampi(value.unicode_at(i)-32,0,94)
						var advance: int = int(f.advance[idx])
						if idx!=0:
							var w: float = font.get_char_size(value.unicode_at(i), font_size).x
							_raster.draw_char(font, Vector2(roundf(x * _px + (advance * _px - w) / 2.0), base_y), value[i], font_size, color)
						x+=advance
					_raster.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
				else:
					var atlas: Texture2D=Art.TEXTURES["f_"+c[4]]
					for i in value.length():
						var idx:=clampi(value.unicode_at(i)-32,0,94)
						if idx!=0:
							var area:=Rect2((idx%16)*f.cw,floori(idx/16.0)*f.ch,f.cw,f.ch)
							_raster.draw_texture_rect_region(atlas,Rect2(x,c[2],f.cw,f.ch),area,color)
						x+=int(f.advance[idx])

func _period() -> String:
	if minutes < 360 or minutes >= 1200: return "night"
	if minutes < 480: return "dawn"
	if minutes < 1020: return "day"
	return "dusk"
func _time() -> String:
	var h:= floori(minutes/60.0)%12
	return "%d:%02d" % [12 if h==0 else h, floori((minutes%60)/10.0)*10]
func _ampm() -> String: return "PM" if minutes>=720 else "AM"
func _energy_color() -> String:
	if energy * 5 <= max_energy: return "#c3554a"
	if energy * 2 <= max_energy: return "#d2a138"
	return "#528666"

func _vital_bar(x: int, y: int, label: String, reading: String, current: int, maximum: int, fill: String) -> void:
	_txt(x+24,y-1,label,"label",INK)
	_right(x+145,y-1,reading,"label",INK)
	_rect(x+24,y+12,121,7,"#827f74")
	_rect(x+25,y+13,119,5,"#dfded4")
	var length := roundi(119.0 * current / maximum)
	if current > 0 and current < maximum:
		length = clampi(length,1,118)
	_rect(x+25,y+13,length,5,fill)

func _stack_count(right: int, y: int, count: int) -> void:
	var digits := str(count)
	var width := _width(digits,"micro")
	_rect(right-width-1,y+1,width+2,10,DARK)
	_right(right,y,digits,"micro",IVORY)

func _belt(x,y,small=false) -> void:
	var side:=32 if small else 36
	var step:=35 if small else 38
	for i in 8:
		var xx:int=x+i*step
		var selected:=i==active_slot
		_img("slot_selected" if selected else "slot_rest",xx,y,side,side)
		if selected:
			_rect(xx+1,y+1,3,4,ORANGE)
		var id=str(hotbar[i])
		if catalog.has(id):
			_img(id,xx+(side-26)/2,y+(side-26)/2,26,26)
			if int(item_counts.get(id,0))>1:
				_stack_count(xx+side-3,y+side-12,int(item_counts[id]))
		if hints: _txt(xx+3,y+1,str((i+1)%10),"micro",OCHRE if selected else MUTED)
		_hit("slot/"+str(i),xx,y,side,side)
func _hud() -> void:
	var left := _bounds.position.x
	var top := _bounds.position.y
	var right := _bounds.end.x - 768
	var bottom := _bounds.end.y - 432
	_img("case_vitalsplate",left+13,top+12,144,60)
	_vital_bar(left,top+18,"HEALTH","%d/%d" % [health,max_health],health,max_health,"#ac6359")
	var percent := ceili(100.0 * energy / max_energy)
	_vital_bar(left,top+41,"ENERGY","%d%%" % percent,energy,max_energy,_energy_color())

	_img("case_clockplate",right+601,top+12,154,63)
	if scenery:
		_img(_period(),right+612,top+20,32,27)
	else:
		_img("i_mark",right+619,top+23,18,18,OCHRE)
	_txt(right+652,top+15,_time(),"clock",INK)
	_right(right+744,top+24,_ampm(),"micro",MUTED)
	_txt(right+653,top+40,season.to_upper()+" "+str(calendar_day),"micro",MUTED)
	_rect(right+612,top+52,132,1,"#d9c2af")
	_img("i_scrip",right+612,top+55,13,13,OCHRE)
	_txt(right+630,top+55,"SCRIP","micro",MUTED)
	var balance := str(station_scrip)
	_right(right+744,top+(53 if balance.length()<11 else 55),balance,"label" if balance.length()<11 else "micro",INK)
	if page in ["HUD","Emotes"]:
		var shell_size := Vector2i(322,52)
		var grid_size := Vector2i(7*38+36,36)
		var housing := Vector2i((768-shell_size.x)/2,373+bottom)
		var inset := (shell_size-grid_size)/2
		_img("case_beltplate",housing.x,housing.y,shell_size.x,shell_size.y)
		_belt(housing.x+inset.x,housing.y+inset.y)
		if catalog.has(hotbar[active_slot]):
			var label:String=catalog[hotbar[active_slot]][0]
			var width:=_width(label,"label")+20
			_rect(384-width/2,353+bottom,width,19,"#394036ed");_txt(394-width/2,354+bottom,label,"label",IVORY)
func _shell() -> void:
	_rect(_bounds.position.x,_bounds.position.y,_bounds.size.x,_bounds.size.y,"#252a26aa")
	_img("housing_shadow",27,17,720,406)
	_img("housing",24,13,720,406)
	_img(TAB_LINERS.get(page,"page_liner"),53,94,662,284)
	_img("i_mark",51,28,18,18,OCHRE);_txt(76,27,"TERRAN","strong");_rect(140,31,1,11,"#9d927c")
	_txt(149,29,"FIELD DATAPAD","micro",MUTED)
	_rect(598,35,4,4,TEAL);_right(705,28,_time()+" "+_ampm()+"   "+season.to_upper()+" "+str(calendar_day),"micro",INK)
	var tabx:=55
	for i in TABS.size():
		var wid: int=[99,97,76,116,71,88,110][i]
		var selected: bool=page==TABS[i]
		_rect(tabx,61,wid-3,25,"#f0d4b9" if selected else "#f0eee7")
		_bevel(tabx,61,wid-3,25,"#f9e8d2" if selected else "#fffdf6","#bd8b67" if selected else "#d5cfc1")
		_img("i_"+TAB_ICONS[i],tabx+7,66,14,14,OCHRE if selected else MUTED)
		_txt(tabx+24,65,TAB_NAMES[i],"label",INK if selected else MUTED)
		if selected: _rect(tabx,84,wid-3,2,ORANGE)
		_hit("open/"+TABS[i],tabx,61,wid-3,25)
		tabx+=wid
	_rect(53,90,661,1,RULE)
	if hints: _txt(171,390,"1-8  QUICK SLOT     TAB  DATAPAD     ESC  BACK","micro",MUTED)
	_btn("back",642,388,65,19,"Close")
	_side_tab("relictab",142,"relic","Relics",page=="Relics")
	if page=="Inventory":
		_side_tab("trash",263,"trash","Trash",false,item_selection!="")

func _side_tab(id: String,y: int,icon: String,label: String,selected: bool,enabled: bool=true) -> void:
	_img("case_sidetab",718,y,48,47)
	_img("i_"+icon,733,y+7,19,19,OCHRE if enabled else "#a9a499")
	_txt(743-_width(label,"micro")/2,y+27,label,"micro",INK if enabled else MUTED)
	if selected: _rect(721,y+10,3,27,ORANGE)
	if enabled: _hit(id,718,y,48,47)
func _heading(title,meta="") -> void:
	_txt(68,97,title,"title")
	if meta!="":
		_right(697,112,meta,"micro",MUTED)
func _tab_titles(left:String,right:String,right_x:int) -> void:
	_txt(68,97,left,"title")
	_txt(right_x,103,right,"mid")
	_rect(69,130,right_x-98,1,RULE)
	_rect(right_x,130,697-right_x,1,RULE)

func _items() -> Array:
	var a:Array=[]
	for id in catalog:
		if int(item_counts.get(id,0))>0 and (bag_filter=="All" or catalog[id][1]==bag_filter):
			a.append(id)
	return a
func _ensure_item() -> void:
	var a:=_items()
	if not item_selection in a: item_selection="" if a.is_empty() else str(a[0])
	bag_page=clampi(bag_page,0,maxi(0,ceili(a.size()/24.0)-1))
func _inventory() -> void:
	_ensure_item()
	_txt(66,96,"Inventory","title")
	var used := 0
	for count in item_counts.values():
		if int(count)>0: used+=1
	_right(390,111,"%d / %d SLOTS"%[used,inventory_capacity],"micro",MUTED)
	_txt(421,101,"Player gear","mid")
	_img("i_scrip",619,111,13,13,OCHRE)
	_right(700,111,str(station_scrip)+" SCRIP","micro",MUTED)
	var fx := 66
	for group in ["All","Tools","Supplies","Materials","Gear"]:
		var fw := _width(group,"label")+16
		if bag_filter==group:
			_rect(fx,136,fw,19,"#eed8bf")
			_rect(fx,153,fw,2,ORANGE)
		_txt(fx+8,137,group,"label",OCHRE if group==bag_filter else MUTED)
		_hit("filter/"+group,fx,136,fw,19)
		fx += fw+2
	var items := _items()
	var by_slot := _by_slot()
	for k in 24:
		var index := bag_page*24+k
		var x := 66+(k%8)*41
		var y := 160+floori(k/8.0)*39
		var id := str(items[index]) if index<items.size() else ""
		if by_slot:
			id = _bag_item(k)
		var selected := (id!="" and id==item_selection and _held<0) or k==_held and by_slot
		_img("slot_selected" if selected else ("slot_empty" if id=="" else "slot_rest"),x,y,38,36)
		if by_slot and k<8 and hints:
			_txt(x+3,y+1,str(k+1),"micro",MUTED)
		if id!="" and not (by_slot and k==_held):
			_img(id,x+4,y+2,29,29)
			if equipment.values().has(id):
				_rect(x+2,y+2,4,4,"#688776")
			if int(item_counts[id])>1: _stack_count(x+35,y+23,int(item_counts[id]))
		if by_slot:
			_hit("bagslot/"+str(k),x,y,38,36)
		elif id!="":
			_hit("item/"+id,x,y,38,36)
	if items.size()>24 and not by_slot:
		_btn("bag/prev",260,275,60,18,"Previous",false,bag_page>0)
		_btn("bag/next",328,275,60,18,"Next",false,(bag_page+1)*24<items.size())
	var detail_y := 293 if items.size()>24 else 284
	_rect(66,detail_y-4,325,1,RULE)
	if item_selection!="":
		var obj:Array=catalog[item_selection]
		_img("slot_selected",66,detail_y+5,37,36)
		_img(item_selection,70,detail_y+8,29,29)
		_txt(112,detail_y,str(obj[2]).to_upper(),"micro",MUTED)
		_txt(111,detail_y+11,obj[0],"strong")
		var lines := _wrap_lines(obj[3],278,"body")
		for i in mini(2,lines.size()):
			_txt(112,detail_y+29+13*i,lines[i],"body",MUTED)
		_btn("equip",66,349,134,22,"Pin to slot "+str(active_slot+1),true)
		if item_selection in ["ration","stamina","healing"]:
			_btn("use",206,349,84,22,"Use item")
	else:
		_txt(66,detail_y+7,"No items in this group","body",MUTED)
	_img("gear_display",520,136,86,123)
	_img(player_sprite,539,146,48,96)
	# armour on the left of the figure, clothes on the right, the laser parts below
	for i in GEAR_SLOTS.size():
		var slot: Array=GEAR_SLOTS[i]
		var x: int=420 if i<3 else 613
		var y:=139+40*i if i<3 else 139+40*(i-3)
		var width:=94 if i<3 else 88
		if i>=5:
			x=420+(i-5)*141
			y=280
			width=138
		_gear_cell(slot,x,y,width,32 if i<5 else 26)
	_txt(421,264,"MINING LASER SOCKETS","micro",MUTED)
	_rect(420,316,280,1,RULE)
	_txt(421,320,"QUICK ACCESS","micro",MUTED)
	_belt(421,335,true)
	if _held>=0 and _bag_item(_held)!="":
		_txt(66,121,"Click a slot to put it there; right-click to put it back","micro",OCHRE)


# The "All" view shows the bag slot by slot, so things can be moved; the others list what matches.
func _by_slot() -> bool:
	return bag_filter=="All" and not bag_slots.is_empty()


func _bag_item(k: int) -> String:
	if k<0 or k>=bag_slots.size() or bag_slots[k]==null: return ""
	var id:=str(bag_slots[k])
	return id if catalog.has(id) and int(item_counts.get(id,0))>0 else ""


func _move_held(to: int) -> void:
	if _held<0: return
	if to!=_held and to>=0 and to<bag_slots.size():
		var moved=bag_slots[_held]
		bag_slots[_held]=bag_slots[to]
		bag_slots[to]=moved
		slots_swapped.emit(_held,to)
		item_selection=_bag_item(to)
	_held=-1

func _gear_cell(slot: Array,x: int,y: int,w: int,h: int) -> void:
	var key:String=slot[0]
	var id:String=equipment.get(key,"")
	_rect(x,y,w,h,"#eae7df")
	_outline(x,y,w,h,"#baac9a")
	_bevel(x+1,y+1,w-2,h-2,"#fffcf3","#d7cec0")
	_rect(x+2,y+2,22,h-4,"#dce3d7" if id!="" else "#ded9cc")
	_bevel(x+2,y+2,22,h-4,"#c0b9a7","#efecdf")
	if id!="":
		_img(id,x+1,y+(h-22)/2,23,22)
	else:
		_img("i_"+slot[2],x+4,y+(h-16)/2,16,16,"#8c897d")
	_txt(x+28,y+(h-13)/2,slot[1],"micro",INK)
	_hit("gear/"+key,x,y,w,h)

func set_equipment(assignment: Dictionary) -> void:
	var desired := assignment.duplicate()
	equipment.clear()
	for slot in GEAR_SLOTS:
		var key: String=slot[0]
		var id: String=desired.get(key,"")
		if gear_types.get(id,"")==slot[2] and _spare_copies(id)>0:
			equipment[key]=id
	refresh()

func _spare_copies(id: String) -> int:
	return maxi(0,int(item_counts.get(id,0))-equipment.values().count(id))

func set_player_portrait(sprite: Texture2D) -> void:
	if sprite:
		extra_textures["equipped_player"]=sprite
		player_sprite="equipped_player"
	else:
		player_sprite="player_front"
	refresh()

func _toggle_relics() -> void:
	if page=="Relics":
		show_page(_relic_parent)
	else:
		_relic_parent=page
		show_page("Relics")

func _skills_page() -> void:
	_tab_titles("Skills","Experience",415)
	if skills.is_empty():
		_txt(69,153,"No skills recorded","body",MUTED)
		return
	skill_index=clampi(skill_index,0,skills.size()-1)
	var first:=floori(skill_index/4.0)*4
	for i in range(first,mini(first+4,skills.size())):
		var entry:Dictionary=skills[i]
		var x:=69+(i%2)*157
		var y:=146+floori((i-first)/2.0)*96
		var on:=i==skill_index
		_rect(x,y,148,84,"#eddbc7" if on else "#eae9df")
		_bevel(x,y,148,84,"#fffdf6","#c9c0ae")
		if on:_rect(x,y,3,84,ORANGE)
		_img(entry.icon,x+10,y+10,20,20,OCHRE if on else MUTED)
		_txt(x+38,y+10,entry.name,"strong")
		_txt(x+11,y+44,"LEVEL %d" % int(entry.level),"micro",MUTED)
		var ratio:=clampf(float(entry.xp)/maxi(1,int(entry.goal)),0,1)
		_rect(x+11,y+61,125,6,"#d3cfc0")
		_rect(x+11,y+61,roundi(125*ratio),6,"#688674")
		_hit("skill/"+str(i),x,y,148,84)
	_pager("skill_pages",69,349,skills.size(),floori(first/4.0),305)
	var chosen:Dictionary=skills[skill_index]
	var goal:=maxi(1,int(chosen.goal))
	var current:=clampi(int(chosen.xp),0,goal)
	_img("skill_display",414,146,68,61)
	_img(chosen.icon,429,159,37,36,"#e2e9d4")
	_txt(496,150,"LEVEL "+str(chosen.level),"micro",MUTED)
	_txt(495,168,chosen.name,"mid")
	_wrap(415,225,277,chosen.description,"body",INK,17)
	_rect(415,281,282,1,RULE)
	_txt(415,292,"NEXT LEVEL","micro",MUTED)
	_right(697,288,"%d / %d XP"%[current,goal],"label",INK)
	_rect(415,312,282,10,"#d6d3c5")
	_rect(415,312,roundi(282.0*current/goal),10,"#64836f")
	_txt(415,333,"%d XP to level %d"%[goal-current,int(chosen.level)+1],"body",MUTED)

func _relic_page() -> void:
	_tab_titles("Relic tasks","Restoration",332)
	_txt(69,135,"PRECURSOR CUSTODIANS","micro",MUTED)
	if custodians.is_empty():
		_txt(69,153,"No relic tasks discovered","body",MUTED)
		return
	relic_index=clampi(relic_index,0,custodians.size()-1)
	var first:=floori(relic_index/4.0)*4
	for i in range(first,mini(first+4,custodians.size())):
		var c:Dictionary=custodians[i]
		_listrow("relic/"+str(i),67,151+(i-first)*46,242,str(c.name).trim_prefix("The "),str(c.wing).to_upper(),i==relic_index)
	_pager("relic_pages",67,348,custodians.size(),floori(first/4.0),248)
	var selected:Dictionary=custodians[relic_index]
	var bundles:Array=selected.bundles
	if bundles.is_empty():return
	bundle_index=clampi(bundle_index,0,bundles.size()-1)
	var bundle:Dictionary=bundles[bundle_index]
	_txt(332,143,"RESTORATION BUNDLE","micro",MUTED)
	_right(700,143,"%d / %d"%[bundle_index+1,bundles.size()],"micro",MUTED)
	_txt(331,159,bundle.name,"mid")
	_txt(332,196,"REQUIRED MATERIAL","micro",MUTED)
	_right(699,196,"DELIVERED / NEEDED","micro",MUTED)
	for i in bundle.items.size():
		var mat:Array=bundle.items[i]
		var key:=str(selected.name)+"/"+str(bundle.name)+"/"+str(mat[0])
		var required:=int(mat[1])
		var supplied:=clampi(int(relic_progress.get(key,0)),0,required)
		var y:int=213+i*23
		_rect(332,y+19,367,1,RULE)
		_txt(332,y,mat[0],"body")
		_rect(587,y+6,49,4,"#d6d3c5")
		_rect(587,y+6,roundi(49.0*supplied/maxi(1,required)),4,"#64836f")
		_right(699,y,"%d / %d"%[supplied,required],"label",TEAL if supplied==required else INK)
	_txt(332,287,"RESTORATION","micro",MUTED)
	_wrap(332,300,362,bundle.reward,"label",INK,14)
	_btn("bundle/prev",332,346,83,21,"Previous",false,bundle_index>0)
	_btn("bundle/next",615,346,84,21,"Next",false,bundle_index+1<bundles.size())

func set_relic_progress(delivered: Dictionary) -> void:
	relic_progress=delivered.duplicate()
	refresh()

func _pager(prefix: String,x: int,y: int,total: int,current: int,wide: int) -> void:
	if total<=4:return
	var pages:=ceili(total/4.0)
	_btn(prefix+"/prev",x,y,53,19,"Prev",false,current>0)
	_txt(x+65,y+2,"%d / %d"%[current+1,pages],"micro",MUTED)
	_btn(prefix+"/next",x+wide-53,y,53,19,"Next",false,current+1<pages)

func _listrow(id,x,y,w,title,sub,selected,icon="") -> void:
	_rect(x,y,w,44,"#f2ddc8" if selected else "#f0eee7")
	_bevel(x,y,w,44,"#fffcf3","#d7c4ae" if selected else "#dad4c7")
	if selected:_rect(x,y,3,44,ORANGE)
	var off:=12
	if icon!="":
		_img(icon,x+8,y+5,32,32,OCHRE if str(icon).begins_with("i_") else "#ffffff")
		off=49
	_txt(x+off,y+4,title,"strong");_txt(x+off,y+24,sub,"micro",MUTED);_hit(id,x,y,w,44)
func recipe_materials(index:int) -> Dictionary:
	var recipe:Array=recipes[index]
	if recipe.size()>5 and recipe[5] is Dictionary:return recipe[5]
	return {recipe[1]:int(recipe[2])}

func _material_count(id:String) -> int:
	if id!="produce":return _spare_copies(id)
	var total:=0
	for crop in produce_items:total+=_spare_copies(crop)
	return total

func _station_available(index:int) -> bool:
	var station:String=recipes[index][4]
	return station=="Pocket" or nearby_crafting_stations==null or station in nearby_crafting_stations

func craft_costs(index:int) -> Dictionary:
	if index<0 or index>=recipes.size() or not _station_available(index):return {}
	var required:=recipe_materials(index)
	var costs:Dictionary={}
	for id in required:
		if int(required[id])<=0:return {}
		if id=="produce":continue
		if _spare_copies(id)<int(required[id]):return {}
		costs[id]=int(required[id])
	var left:=int(required.get("produce",0))
	for id in produce_items:
		if left<=0:break
		var take:=mini(left,maxi(0,_spare_copies(id)-int(costs.get(id,0))))
		if take>0:costs[id]=int(costs.get(id,0))+take
		left-=take
	return costs if left==0 else {}

func _recipe_indices() -> Array:
	var result:Array=[]
	for i in recipes.size():
		if recipe_filter=="Pocket" and recipes[i][4]!="Pocket":continue
		if recipe_filter=="Ready" and craft_costs(i).is_empty():continue
		result.append(i)
	return result

func _craft() -> void:
	var shown:=_recipe_indices()
	_tab_titles("Crafting","Blueprint",351)
	var x:=69
	for group in ["All","Pocket","Ready"]:
		var width:=_width(group,"label")+25
		_btn("recipe_filter/"+group,x,138,width,21,group,recipe_filter==group)
		x+=width+4
	if shown.is_empty():
		_txt(69,180,"No matching recipes","body",MUTED)
		return
	if recipe_index not in shown:
		recipe_index=shown[0]
		material_page=0
	var cursor:=shown.find(recipe_index)
	var first:=floori(cursor/4.0)*4
	_pager("recipes_pages",69,348,shown.size(),floori(first/4.0),252)
	for p in range(first,mini(first+4,shown.size())):
		var idx:int=shown[p]
		var recipe:Array=recipes[idx]
		var row_y:=166+(p-first)*43
		_rect(69,row_y,253,39,"#eddbc7" if idx==recipe_index else "#edece3")
		_bevel(69,row_y,253,39,"#fffdf7","#d1c6b3")
		if idx==recipe_index:_rect(69,row_y,3,39,ORANGE)
		_img(recipe[0],77,row_y+4,30,30)
		_txt(113,row_y+2,catalog[recipe[0]][0],"strong")
		_txt(114,row_y+22,str(recipe[4]).to_upper(),"micro",MUTED)
		_hit("recipe/"+str(idx),69,row_y,253,39)
	var r:Array=recipes[recipe_index]
	_img("blueprint",351,145,77,67)
	_img(r[0],366,155,48,48)
	_txt(440,146,str(r[4]).to_upper(),"micro",MUTED)
	_txt(440,163,catalog[r[0]][0],"mid")
	_txt(441,192,"Makes %d" % int(r[3]),"body",INK)
	_txt(352,226,"MATERIALS","micro",MUTED)
	_right(697,226,"HAVE / NEED","micro",MUTED)
	var required:=recipe_materials(recipe_index)
	var materials:=required.keys()
	var pages:=maxi(1,ceili(materials.size()/3.0))
	material_page=clampi(material_page,0,pages-1)
	if pages>1:
		_btn("materials/prev",473,219,28,18,"<",false,material_page>0)
		_txt(508,222,"%d/%d"%[material_page+1,pages],"micro",MUTED)
		_btn("materials/next",547,219,28,18,">",false,material_page+1<pages)
	var y:=241
	for id in materials.slice(material_page*3,material_page*3+3):
		var held:=_material_count(id)
		var needed:=int(required[id])
		_rect(351,y+22,346,1,RULE)
		_img("berry" if id=="produce" else id,351,y,21,21)
		_txt(380,y+1,"Crops or berries" if id=="produce" else catalog[id][0],"body")
		_right(697,y+2,"%d / %d"%[held,needed],"label",TEAL if held>=needed else OCHRE)
		y+=25
	var available:=not craft_costs(recipe_index).is_empty()
	var action:="Craft %d" % int(r[3])
	if not _station_available(recipe_index):action="Requires "+str(r[4])
	elif not available:action="Missing materials"
	_btn("craft",351,336,346,27,action,true,available)

func _current_place() -> int:
	for i in places.size():
		if str(places[i][0])==location_name:return i
	return -1

func _map_page() -> void:
	if extra_textures.has("sector_map") and sector_size.x > 0:
		_sector_page()
		return
	_tab_titles("Station map","Location details",458)
	if places.is_empty():
		_txt(69,152,"No locations charted","body",MUTED)
		return
	place_index=clampi(place_index,0,places.size()-1)
	var current:=_current_place()
	_img("station_plan",69,141,368,220)
	for i in places.size():
		var p:Array=places[i]
		var x:=69+int(p[1])
		var y:=141+int(p[2])
		var selected:=i==place_index
		var frame:="#e4a16d" if selected else "#96a48f"
		_rect(x-8,y-8,17,17,frame)
		_rect(x-6,y-6,13,13,"#79563f" if selected else "#52665a")
		var num:=str(i+1)
		_txt(x+1-_width(num,"micro")/2,y-5,num,"micro","#fff9e8")
		if i==current:
			_rect(x-3,y+9,7,2,"#c9edcf")
			_rect(x-1,y+11,3,2,"#c9edcf")
		_hit("place/"+str(i),x-9,y-9,19,22)
	_rect(79,343,6,5,"#d99866")
	_txt(91,340,"SELECTED","micro","#e4e8d9")
	_rect(145,343,6,5,"#c9edcf")
	_txt(157,340,"YOU ARE HERE","micro","#e4e8d9")
	var target:Array=places[place_index]
	_txt(459,142,str(target[3]).to_upper(),"micro",MUTED)
	_txt(458,156,target[0],"mid")
	_wrap(459,183,237,target[4],"body",INK,15)
	_rect(458,231,239,1,RULE)
	_txt(459,238,"DIRECTORY","micro",MUTED)
	var first:=floori(place_index/8.0)*8
	for i in range(first,mini(first+8,places.size())):
		var col:=i%2
		var row:=floori((i-first)/2.0)
		var x:=458+col*120
		var y:=254+row*20
		if i==place_index:_rect(x,y,117,18,"#ead5bc")
		_txt(x+3,y+3,str(i+1),"micro",OCHRE)
		_txt(x+17,y,places[i][0],"label",INK)
		_hit("maprow/"+str(i),x,y,117,18)
	if places.size()>8:
		_btn("map_pages/prev",458,343,48,20,"Prev",false,first>0)
		_btn("map_pages/next",511,343,48,20,"Next",false,first+8<places.size())
	_btn("locate",572,343,125,20,"Locate player",false,current>=0)

func _sector_page() -> void:
	_tab_titles(sector_title,"Places here",458)
	var bx:=69
	var by:=141
	_rect(bx,by,368,220,"#2f352f")
	var mx:=bx+int((368-sector_size.x)/2.0)
	var my:=by+int((220-sector_size.y)/2.0)
	_img("sector_map",mx,my,int(sector_size.x),int(sector_size.y))
	_outline(mx-1,my-1,int(sector_size.x)+2,int(sector_size.y)+2,"#596055")
	for person in sector_people:
		var at:Vector2=person[0]
		_rect(mx+int(at.x)-2,my+int(at.y)-2,5,5,"#2b4f63")
		_rect(mx+int(at.x)-1,my+int(at.y)-1,3,3,"#8fd6f2")
		_hit("person/"+str(person[1]),mx+int(at.x)-4,my+int(at.y)-4,9,9)
	for i in sector_marks.size():
		var at:Vector2=sector_marks[i][0]
		var x:=mx+int(at.x)
		var y:=my+int(at.y)
		var selected:=i==mark_index
		_rect(x-6,y-6,13,13,"#e4a16d" if selected else "#96a48f")
		_rect(x-5,y-5,11,11,"#79563f" if selected else "#52665a")
		var num:=str(i+1)
		_txt(x+1-_width(num,"micro")/2,y-5,num,"micro","#fff9e8")
		_hit("mark/"+str(i),x-7,y-7,15,15)
	if sector_you.x>=0:
		var yx:=mx+int(sector_you.x)
		var yy:=my+int(sector_you.y)
		_rect(yx-4,yy-4,9,9,"#fff9e8")
		_rect(yx-3,yy-3,7,7,"#c74b3c")
		_txt(yx+7,yy-6,"YOU","micro","#fff9e8")
	# the name of the place picked (or the person or place pointed at) over the map
	var shown:=""
	var shown_at:=Vector2.ZERO
	if _hover_id.begins_with("mark/") or _hover_id.begins_with("person/"):
		if _hover_id.begins_with("mark/"):
			var k:=_hover_id.trim_prefix("mark/").to_int()
			if k<sector_marks.size(): shown=str(sector_marks[k][1]); shown_at=sector_marks[k][0]
		else:
			shown=_hover_id.trim_prefix("person/")
			for person in sector_people:
				if str(person[1])==shown: shown_at=person[0]
	elif mark_index>=0 and mark_index<sector_marks.size():
		shown=str(sector_marks[mark_index][1])
		shown_at=sector_marks[mark_index][0]
	if shown!="":
		var tw:=_width(shown,"label")+10
		var tx:=clampi(mx+int(shown_at.x)-tw/2,bx,bx+368-tw)
		var ty:=clampi(my+int(shown_at.y)-26,by,by+220-18)
		_rect(tx,ty,tw,17,DARK)
		_txt(tx+5,ty+1,shown,"label",IVORY)
	# the directory: every labelled place on this level
	_txt(459,142,"%d PLACES  /  %d PEOPLE" % [sector_marks.size(),sector_people.size()],"micro",MUTED)
	var per:=16
	mark_page=clampi(mark_page,0,maxi(0,ceili(sector_marks.size()/float(per))-1))
	var first:=mark_page*per
	for i in range(first,mini(first+per,sector_marks.size())):
		var col:=(i-first)%2
		var row:=floori((i-first)/2.0)
		var x:=458+col*120
		var y:=158+row*20
		if i==mark_index:_rect(x,y,117,18,"#ead5bc")
		_txt(x+3,y+3,str(i+1),"micro",OCHRE)
		var label:=str(sector_marks[i][1])
		while label.length()>3 and _width(label,"label")>96: label=label.substr(0,label.length()-2)
		if label!=str(sector_marks[i][1]): label+="."
		_txt(x+17,y,label,"label",INK)
		_hit("mark/"+str(i),x,y,117,18)
	if sector_marks.is_empty():
		_txt(459,160,"Nothing labelled on this level","body",MUTED)
	if sector_marks.size()>per:
		_btn("mark_pages/prev",458,343,48,20,"Prev",false,mark_page>0)
		_btn("mark_pages/next",511,343,48,20,"Next",false,first+per<sector_marks.size())
	_rect(79,343,6,5,"#d99866")
	_txt(91,340,"PLACE","micro","#e4e8d9")
	_rect(135,343,6,5,"#8fd6f2")
	_txt(147,340,"RESIDENT","micro","#e4e8d9")
	_rect(209,343,6,5,"#c74b3c")
	_txt(221,340,"YOU","micro","#e4e8d9")

func _journal() -> void:
	_tab_titles("Quests","Objective",319)
	if jobs.is_empty():
		_txt(69,153,"No active quests","body",MUTED)
		return
	job_index=clampi(job_index,0,jobs.size()-1)
	var first:=floori(job_index/4.0)*4
	_txt(69,140,"%d ACTIVE" % jobs.size(),"micro",MUTED)
	for i in range(first,mini(first+4,jobs.size())):
		var job:Array=jobs[i]
		var y:=158+44*(i-first)
		var selected:=i==job_index
		_rect(69,y,219,39,"#efdbc4" if selected else "#eeede4")
		_bevel(69,y,219,39,"#fffaf2","#d1c6b4")
		if selected:_rect(69,y,3,39,ORANGE)
		_img("i_journal",78,y+10,17,17,OCHRE if selected else MUTED)
		_txt(103,y+2,job[0],"strong")
		var subtitle:=str(job[1]).to_upper()
		if tracked==i:subtitle+=" / TRACKED"
		_txt(104,y+22,subtitle,"micro",MUTED)
		_hit("job/"+str(i),69,y,219,39)
	_pager("jobs_pages",69,348,jobs.size(),floori(first/4.0),219)
	var j:Array=jobs[job_index]
	var info:Dictionary=j[5] if j.size()>5 else {}
	var giver:String=j[1]
	var image_id:="p_"+giver
	if not Art.TEXTURES.has(image_id) and not extra_textures.has(image_id):image_id="i_crew"
	_img("crew_photo",320,146,52,53)
	_img(image_id,322,148,48,48,"#ffffff" if image_id!="i_crew" else "#c7cbbd")
	_txt(383,146,"REQUEST FROM "+giver.to_upper(),"micro",MUTED)
	_txt(382,165,j[0],"mid")
	_wrap(320,208,372,j[2],"body",INK,16)
	_rect(320,252,377,1,RULE)
	_txt(320,259,"OBJECTIVE","micro",MUTED)
	_txt(320,274,j[3],"strong")
	var item:String=j[4]
	if item!="" and info.has("needed"):
		var required:=maxi(1,int(info.needed))
		var held:=maxi(0,int(item_counts.get(item,0)))
		_txt(320,299,"%d / %d in pack"%[held,required],"label",TEAL if held>=required else MUTED)
	elif info.has("place"):
		_txt(320,299,info.place,"label",MUTED)
	_btn("track",320,337,173,26,"Untrack quest" if tracked==job_index else "Track quest",true)
	if _quest_place(j)>=0:_btn("quest_map",503,337,194,26,"View on map")

func _quest_place(job:Array) -> int:
	if job.size()<=5:return -1
	var target:String=job[5].get("place","")
	for i in places.size():
		if places[i][0]==target:return i
	return -1

func _crew() -> void:
	_tab_titles("NPC relations","Resident file",313)
	if crew.is_empty():
		_txt(69,155,"No residents met yet","body",MUTED)
		return
	crew_index=clampi(crew_index,0,crew.size()-1)
	var first:=floori(crew_index/4.0)*4
	for i in range(first,mini(first+4,crew.size())):
		var c:Array=crew[i]
		_listrow("crew/"+str(i),69,144+(i-first)*48,213,c[0],str(c[1]).to_upper(),crew_index==i,"p_"+c[0])
	_pager("crew_pages",69,347,crew.size(),floori(first/4.0),213)
	var resident:Array=crew[crew_index]
	var name_text:String=resident[0]
	var info:Dictionary=resident[4] if resident.size()>4 else {}
	_img("crew_photo",313,145,78,85)
	_img("p_"+name_text,315,154,74,70)
	_txt(405,143,name_text,"mid")
	_txt(406,171,resident[1],"body")
	_txt(406,202,"BIRTHDAY","micro",MUTED)
	_txt(467,199,info.get("birthday","Unknown"),"label")
	var cap:=10 if info.get("dating",false) else 8
	var hearts:=clampi(int(resident[3]),0,cap)
	_txt(405,233,"FRIENDSHIP","micro",MUTED)
	for i in cap:
		_img("i_heart",406+i*16,249,14,14,"#b56548" if i<hearts else "#c9c6b8")
	_right(698,249,"%d / %d"%[hearts,cap],"micro",MUTED)
	_wrap(313,269,381,resident[2],"body",INK,15)
	_rect(313,306,385,1,RULE)
	_txt(313,314,"DISCOVERED GIFTS","micro",MUTED)
	var known:Dictionary=known_gifts.get(name_text,{})
	var pages:=maxi(known.get("Loved",[]).size(),known.get("Hated",[]).size())
	gift_page=clampi(gift_page,0,maxi(0,pages-1))
	if pages>1:
		_btn("gifts/prev",591,310,30,18,"<",false,gift_page>0)
		_txt(627,313,"%d/%d"%[gift_page+1,pages],"micro",MUTED)
		_btn("gifts/next",668,310,30,18,">",false,gift_page+1<pages)
	for i in 2:
		var tone:String=["Loved","Hated"][i]
		var entries:Array=known.get(tone,[])
		var value:String="Unknown" if entries.is_empty() else (str(entries[gift_page]) if gift_page<entries.size() else "-")
		var y:=332+i*18
		_txt(313,y,tone,"label",OCHRE if i==0 else MUTED)
		_txt(364,y,value,"body",MUTED if entries.is_empty() else INK)

func _system() -> void:
	_tab_titles("Settings","Controls",402)
	_txt(69,145,"DISPLAY","micro",MUTED)
	for i in 2:
		var y:=164+i*49
		var enabled:=hints if i==0 else scenery
		var id:="hints" if i==0 else "scenery"
		_txt(69,y+3,"Control hints" if i==0 else "Orbital clock icon","strong")
		_btn("opt/"+id,295,y,70,26,"On" if enabled else "Off",enabled)
		_rect(69,y+35,296,1,RULE)
	_txt(69,279,"GAME SESSION","micro",MUTED)
	_btn("quit",69,306,157,31,"Quit game")
	_btn("controls/Keys",402,143,112,22,"Keyboard",control_scheme=="Keys")
	_btn("controls/Pad",519,143,112,22,"Controller",control_scheme=="Pad")
	var keys:=["1-8","Tab","V","Esc","Arrows","Enter"] if control_scheme=="Keys" else ["Select","Y","Start","B","D-pad","A"]
	var actions:=["Select hotbar slot","Open datapad","Open emotes","Back / station menu","Move focus","Activate selection"] if control_scheme=="Keys" else ["Open datapad","Open emotes","Station menu / back","Back","Move focus","Activate selection"]
	for i in keys.size():
		var y:=181+30*i
		_rect(402,y,65,21,"#e7e3d8")
		_bevel(402,y,65,21,"#fffaf1","#c6bba8")
		_txt(434-_width(keys[i],"label")/2,y+1,keys[i],"label")
		_txt(478,y,actions[i],"body")

# Echo Landing (23 Nov): a tab per kind of business (Buy, Sell, Crack, Cook), four rows a page, up to two buttons
# a row. scripts/shops.gd builds the rows and acts on the buttons (shop_action), then sends the rows again.
func _shop() -> void:
	_heading(shop_name,str(station_scrip)+" SCRIP")
	for t in shop_tabs.size():
		_btn("shoptab/"+str(t),69+t*104,139,98,21,str(shop_tabs[t][0]),t==shop_tab)
	var rows:=_shop_rows()
	_pager("shop_pages",69,350,rows.size(),shop_page,625)
	if rows.is_empty():
		_txt(70,180,"Nothing here right now.","body",MUTED)
	var first:=shop_page*4
	for i in range(first,mini(first+4,rows.size())):
		var v:Array=rows[i]
		var y:=166+(i-first)*45
		_rect(69,y,627,40,"#f0eee7")
		_bevel(69,y,627,40,"#fffdf5","#d8d1c3")
		if catalog.has(str(v[0])) or extra_textures.has(str(v[0])): _img(str(v[0]),80,y+3,33,33)
		_txt(126,y+3,str(v[1]),"strong")
		_txt(126,y+22,str(v[2]),"micro",MUTED)
		_right(476,y+11,str(v[3]),"label",MUTED)
		var buttons:Array=v[4]
		for b in buttons.size():
			var bt:Array=buttons[b]
			_btn("shop/"+str(bt[0]),486+b*105,y+7,100,25,str(bt[1]),b==0,bool(bt[2]))
func _storage() -> void:
	_heading(storage_name,"STORAGE")
	_txt(70,146,"YOUR BAG","micro",MUTED)
	_txt(392,146,"IN THE CHEST","micro",MUTED)
	_storage_column(storage_bag,storage_page_bag,69,"store","Store","store_pages")
	_storage_column(storage_chest,storage_page_chest,391,"take","Take","take_pages")

func _storage_column(list: Array, current: int, x: int, action: String, label: String, pager: String) -> void:
	_pager(pager,x,350,list.size(),current,305)
	if list.is_empty():
		_txt(x+4,170,"Nothing here","body",MUTED)
		return
	var first:=current*4
	for i in range(first,mini(first+4,list.size())):
		var v:Array=list[i]
		var y:=166+(i-first)*45
		_rect(x,y,305,40,"#f0eee7")
		_bevel(x,y,305,40,"#fffdf5","#d8d1c3")
		_img(str(v[0]),x+9,y+3,33,33)
		_txt(x+50,y+9,str(catalog[v[0]][0]) if catalog.has(v[0]) else str(v[0]),"strong")
		_right(x+226,y+10,"x"+str(int(v[1])),"label",MUTED)
		_btn(action+"/"+str(i),x+232,y+7,64,25,label,true)

func _recap() -> void:
	_heading("Day summary",recap.get("day","").to_upper())
	_txt(71,150,"STATION ACCOUNT","micro",MUTED)
	var earned=int(recap.get("earned",0));var spent=int(recap.get("spent",0))
	for i in 3:
		var y:=180+40*i
		_rect(70,y+31,626,1,RULE)
		_txt(71,y,["Earned","Spent","Net change"][i],"strong")
		var val:int=[earned,-spent,earned-spent][i]
		_right(694,y,("%+d" % val)+" scrip","strong",OCHRE if val<0 else INK)
	_btn("back",502,316,194,29,"Continue",true)
func _dialog() -> void:
	hits.clear()
	var bottom := _bounds.end.y - 432
	_img("case_talkplate",96,339+bottom,575,77)
	var portrait=str(dialogue.get("portrait",""))
	if portrait!="":_img(portrait,109,346+bottom,64,59)
	_txt(183,345+bottom,dialogue.get("speaker",""),"strong",OCHRE)
	var lines:Array=dialogue.get("lines",[""])
	_wrap(184,368+bottom,421,str(lines[int(dialogue.get("index",0))]),"body",INK,16)
	_img("i_mark",643,386+bottom,12,12,OCHRE);_hit("advance",96,339+bottom,575,77)

func _pause_menu() -> void:
	hits.clear()
	_rect(_bounds.position.x,_bounds.position.y,_bounds.size.x,_bounds.size.y,"#20272290")
	_img("case_pauseplate",265,132,238,168)
	_img("i_mark",284,153,18,18,OCHRE)
	_txt(309,154,"TERRAN DATAPAD","label",MUTED)
	_txt(284,176,"Station menu","title")
	_btn("resume",285,217,198,26,"Resume",true)
	_btn("settings",285,250,96,24,"Settings")
	_btn("relictab",387,250,96,24,"Relic tasks")

func _emotes() -> void:
	hits.clear()
	_img("case_emoteplate",212,185,345,180)
	_txt(233,199,"Emotes","mid")
	_btn("back",483,201,52,21,"Close")
	for i in EMOTES.size():
		var x:=232+(i%7)*44;var y:=237+floori(i/7.0)*52
		_img("emote_"+str(i),x+7,y,28,28)
		_txt(x+(43-_width(EMOTES[i].capitalize(),"micro"))/2,y+29,EMOTES[i].capitalize(),"micro",MUTED)
		_hit("emote/"+str(i),x,y,43,44)

func select_slot(index: int) -> void:
	active_slot=clampi(index,0,7)
	refresh()
	hotbar_changed.emit(hotbar.duplicate(),active_slot)
func _back() -> void:
	if _held>=0:
		_held=-1
		refresh()
		return
	if _overlay!="":
		_close_overlay()
		return
	match page:
		"Map": show_page(_map_parent);_map_parent="HUD"
		"Relics": show_page(_relic_parent)
		"HUD": show_page("Pause")
		"System":show_page(_system_parent);_system_parent="HUD"
		"Pause","Emotes":show_page("HUD")
		"Dialogue": _advance()
		"Shop","Storage": show_page(_return_page)
		"Recap":
			show_page(_return_page)
			recap_closed.emit()
		_: show_page("HUD")
func _advance() -> void:
	if int(dialogue.get("index",0))+1 < dialogue.get("lines",[]).size():
		dialogue.index+=1
		refresh()
	else:
		show_page(_return_page)
		dialogue_advanced.emit()
func _open_overlay(kind:String,id:String="") -> void:
	_overlay=kind
	_overlay_id=id
	_choice_page=0
	_focus_id="modal/cancel"
	_hover_id=""
	refresh()

func _close_overlay() -> void:
	_overlay=""
	_overlay_id=""
	_focus_id=""
	_hover_id=""
	refresh()

func _overlay_draw() -> void:
	hits.clear()
	_rect(_bounds.position.x,_bounds.position.y,_bounds.size.x,_bounds.size.y,"#272c2999")
	_img("case_dialogbox",206,115,356,205)
	_btn("modal/cancel",473,135,69,23,"Cancel")
	if _overlay=="gear":
		var slot:Array=GEAR_SLOTS.filter(func(v):return v[0]==_overlay_id)[0]
		_txt(229,139,slot[3],"mid")
		var fitted:String=equipment.get(slot[0],"")
		_txt(229,169,"Equipped: "+str(catalog[fitted][0]) if catalog.has(fitted) else "Slot empty","body",MUTED)
		var choices:Array=[]
		for id in catalog:
			if gear_types.get(id,"")==slot[2] and _spare_copies(id)>0 and fitted!=id:
				choices.append(id)
		var num_pages:=maxi(1,ceili(choices.size()/2.0))
		_choice_page=clampi(_choice_page,0,num_pages-1)
		if choices.is_empty():
			_txt(229,205,"No other compatible gear in your pack.","body",MUTED)
		for i in range(_choice_page*2,mini(_choice_page*2+2,choices.size())):
			var id:String=choices[i]
			var y:=195+31*(i%2)
			_img(id,230,y,25,25)
			_btn("modal/wear/"+id,263,y,278,24,catalog[id][0])
		if num_pages>1:
			_btn("modal/prev",229,259,66,19,"Previous",false,_choice_page>0)
			_btn("modal/next",303,259,60,19,"Next",false,_choice_page+1<num_pages)
		_btn("modal/remove",229,282,97,21,"Unequip",false,fitted!="")
	elif _overlay=="trash":
		var available:=_spare_copies(_overlay_id)
		_img("i_trash",228,138,22,22,OCHRE)
		_txt(258,136,"Discard item","mid")
		_img(_overlay_id,229,185,48,48)
		_txt(291,184,catalog[_overlay_id][0],"strong")
		_txt(291,208,"%d available"%available if available>0 else "Unequip first to discard.","body",MUTED)
		_btn("modal/discard_one",229,266,145,27,"Discard one",true,available>0)
		_btn("modal/discard_all",382,266,159,27,"Discard stack",false,available>1)
	elif _overlay=="quit":
		_txt(229,139,"Quit game?","mid")
		_txt(229,197,"Leave this play session?","body")
		_btn("modal/quit",390,266,151,27,"Quit game",true)

func _modal_action(action:String) -> void:
	match action:
		"cancel":
			_close_overlay()
		"quit":
			if _overlay=="quit":
				_close_overlay()
				quit_requested.emit()
		"prev","next":
			_choice_page+=1 if action=="next" else -1
			refresh()
		"discard_one","discard_all":
			if _overlay!="trash":return
			var id:=_overlay_id
			var amount:=mini(1,_spare_copies(id)) if action=="discard_one" else _spare_copies(id)
			_close_overlay()
			if amount>0:discard_requested.emit(id,amount)
		_:
			if _overlay!="gear":return
			var key:=_overlay_id
			if action=="remove":
				equipment.erase(key)
			elif action.begins_with("wear/"):
				var id:=action.trim_prefix("wear/")
				for slot in GEAR_SLOTS:
					if slot[0]==key and gear_types.get(id,"")==slot[2] and _spare_copies(id)>0:
						equipment[key]=id
						break
			_close_overlay()
			equipment_changed.emit(equipment.duplicate())

func _activate(id: String) -> void:
	if _overlay!="":
		if id.begins_with("modal/"): _modal_action(id.trim_prefix("modal/"))
		return
	var pair:=id.split("/",true,1)
	var arg:=pair[1] if pair.size()>1 else ""
	match pair[0]:
		"open":
			_map_parent="HUD"
			_system_parent="HUD"
			show_page(arg)
			return
		"relictab": _toggle_relics();return
		"trash":
			_held=-1
			if page=="Inventory" and catalog.has(item_selection):_open_overlay("trash",item_selection)
			return
		"quit":
			if page=="System":_open_overlay("quit")
			return
		"gear": _open_overlay("gear",arg);return
		"skill": skill_index=arg.to_int()
		"relic": relic_index=arg.to_int();bundle_index=0
		"bundle": bundle_index+=1 if arg=="next" else -1
		"skill_pages":skill_index=clampi((floori(skill_index/4.0)+(1 if arg=="next" else -1))*4,0,skills.size()-1)
		"relic_pages":
			relic_index=clampi((floori(relic_index/4.0)+(1 if arg=="next" else -1))*4,0,custodians.size()-1)
			bundle_index=0
		"resume": show_page("HUD");resume_requested.emit();return
		"settings": _system_parent="Pause";show_page("System");return
		"emote":
			show_page("HUD")
			emote_selected.emit(EMOTES[arg.to_int()])
			return
		"back": _back();return
		"advance": _advance();return
		"slot":
			if page=="Inventory" and _held>=0:
				_move_held(arg.to_int())
			else:
				select_slot(arg.to_int());return
		"bagslot":
			var k:=arg.to_int()
			if _held>=0:
				_move_held(k)
			elif _bag_item(k)!="":
				_held=k
				item_selection=_bag_item(k)
		"item": item_selection=arg
		"filter":
			_held=-1
			bag_filter=arg
			bag_page=0
			_ensure_item()
		"bag":
			bag_page+=1 if arg=="next" else -1
			_ensure_item()
			var shown:=_items()
			if bag_page*24<shown.size(): item_selection=shown[bag_page*24]
		"equip":
			if catalog.has(item_selection) and int(item_counts.get(item_selection,0))>0:
				hotbar[active_slot]=item_selection
				hotbar_changed.emit(hotbar.duplicate(),active_slot)
				notify_player("Pinned to slot "+str(active_slot+1))
		"use":
			if catalog.has(item_selection) and int(item_counts.get(item_selection,0))>0:item_used.emit(item_selection)
		"recipe_filter":
			recipe_filter=arg
			material_page=0
		"recipes_pages":
			material_page=0
			var shown:=_recipe_indices()
			if not shown.is_empty():
				var first:=floori(shown.find(recipe_index)/4.0)*4
				recipe_index=shown[clampi(first+(4 if arg=="next" else -4),0,shown.size()-1)]
		"jobs_pages":job_index=clampi((floori(job_index/4.0)+(1 if arg=="next" else -1))*4,0,jobs.size()-1)
		"crew_pages":
			gift_page=0
			crew_index=clampi((floori(crew_index/4.0)+(1 if arg=="next" else -1))*4,0,crew.size()-1)
		"shop_pages":shop_page=clampi(shop_page+(1 if arg=="next" else -1),0,maxi(0,ceili(_shop_rows().size()/4.0)-1))
		"store_pages":storage_page_bag=clampi(storage_page_bag+(1 if arg=="next" else -1),0,maxi(0,ceili(storage_bag.size()/4.0)-1))
		"take_pages":storage_page_chest=clampi(storage_page_chest+(1 if arg=="next" else -1),0,maxi(0,ceili(storage_chest.size()/4.0)-1))
		"store","take":
			var lst:Array=storage_bag if pair[0]=="store" else storage_chest
			var si:=arg.to_int()
			if si>=0 and si<lst.size():storage_moved.emit(str(lst[si][0]),pair[0]=="store")
		"materials": material_page+=1 if arg=="next" else -1
		"recipe":
			recipe_index=arg.to_int()
			material_page=0
		"craft":
			if not craft_costs(recipe_index).is_empty():craft_requested.emit(recipe_index)
		"place","maprow": place_index=arg.to_int()
		"mark": mark_index=-1 if mark_index==arg.to_int() else arg.to_int()
		"mark_pages": mark_page+=1 if arg=="next" else -1
		"person": pass
		"map_pages": place_index=clampi((floori(place_index/8.0)+(1 if arg=="next" else -1))*8,0,maxi(0,places.size()-1))
		"locate":
			var current:=_current_place()
			if current>=0:place_index=current
		"quest_map":
			if job_index<jobs.size():
				var target:=_quest_place(jobs[job_index])
				if target>=0:
					place_index=target
					_map_parent="Journal"
					show_page("Map")
					return
		"controls": control_scheme=arg
		"gifts": gift_page+=1 if arg=="next" else -1
		"crew": crew_index=arg.to_int();gift_page=0
		"job": job_index=arg.to_int()
		"track":
			tracked=-1 if tracked==job_index else job_index
			journal_tracked.emit(tracked)
		"opt":
			if arg=="hints": hints=not hints
			elif arg=="scenery": scenery=not scenery
			setting_changed.emit(arg,hints if arg=="hints" else scenery)
		"shop": shop_action.emit(arg)
		"shoptab":
			shop_tab=clampi(arg.to_int(),0,maxi(0,shop_tabs.size()-1))
			shop_page=0
	refresh()

func _at(p: Vector2) -> String:
	var local: Vector2 = _layout.affine_inverse() * p
	for j in range(hits.size()-1,-1,-1):
		var h:Array=hits[j]
		if Rect2(h[1],h[2],h[3],h[4]).has_point(local):return str(h[0])
	return ""
func _focus_step(d: Vector2) -> void:
	if hits.is_empty():return
	var here: Array=[]
	for h in hits:
		if h[0]==_focus_id:here=h;break
	if here.is_empty():
		_focus_id=hits[0][0]
	else:
		var origin:=Vector2(here[1]+here[3]*0.5,here[2]+here[4]*0.5)
		var best:=INF
		for h in hits:
			var delta:=Vector2(h[1]+h[3]*0.5,h[2]+h[4]*0.5)-origin
			var forward:=delta.dot(d)
			if forward<1:continue
			var lateral:=absf(delta.cross(d))
			var score:=forward+lateral*3.5
			if score<best:
				best=score
				_focus_id=h[0]
	_hover_id=""
	refresh()
func _pointer(event: InputEvent) -> bool:
	var found := _at(get_global_transform_with_canvas().affine_inverse() * event.position)
	_mouse_ui = _layout.affine_inverse() * (get_global_transform_with_canvas().affine_inverse() * event.position)
	if event is InputEventMouseButton and event.pressed and event.button_index==MOUSE_BUTTON_RIGHT and _held>=0:
		_held=-1
		refresh()
		return true
	if event is InputEventMouseMotion:
		if found != _hover_id or _held>=0:
			_hover_id = found
			refresh()
	elif event is InputEventMouseButton and event.button_index==MOUSE_BUTTON_LEFT and not event.pressed:
		if _pressed_item!="" and found=="trash" and page=="Inventory" and _overlay=="" and item_counts.get(_pressed_item,0)>0:
			_held=-1
			item_selection=_pressed_item
			_open_overlay("trash",_pressed_item)
		elif _held>=0 and _pressed_item!="" and page=="Inventory" and _overlay=="":
			# dragged and let go over another slot: it goes there too
			var to:=-1
			if found.begins_with("bagslot/"): to=found.trim_prefix("bagslot/").to_int()
			elif found.begins_with("slot/"): to=found.trim_prefix("slot/").to_int()
			if to>=0 and to!=_held:
				_move_held(to)
				refresh()
		_pressed_item=""
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT and found != "":
			_pressed_item=found.trim_prefix("item/") if found.begins_with("item/") else (_bag_item(found.trim_prefix("bagslot/").to_int()) if found.begins_with("bagslot/") else "")
			_focus_id = ""
			_activate(found)
			return true
		if page == "HUD" and found.begins_with("slot/") and event.button_index in [MOUSE_BUTTON_WHEEL_UP,MOUSE_BUTTON_WHEEL_DOWN]:
			select_slot(posmod(active_slot+(1 if event.button_index==MOUSE_BUTTON_WHEEL_DOWN else -1),8))
			return true
	return page != "HUD" or found != ""

func _input(event: InputEvent) -> void:
	if not is_visible_in_tree():return
	var handled:=true
	if event is InputEventMouse:
		if _pointer(event):get_viewport().set_input_as_handled()
		return
	if event is InputEventKey and event.pressed and not event.echo:
		if page=="HUD" and event.keycode in [KEY_LEFT,KEY_RIGHT,KEY_UP,KEY_DOWN]:return
		if page=="HUD" and event.keycode in [KEY_ENTER,KEY_SPACE] and not hud_use_shortcut:return
		match event.keycode:
			KEY_TAB:
				if _overlay!="" or page in ["Dialogue","Shop","Storage","Recap"]: _back()
				else: show_page("Inventory" if page=="HUD" else "HUD")
			KEY_ESCAPE: _back()
			KEY_V:
				if page=="HUD": show_page("Emotes")
				elif page=="Emotes":show_page("HUD")
				else:handled=false
			KEY_1,KEY_2,KEY_3,KEY_4,KEY_5,KEY_6,KEY_7,KEY_8:
				if _overlay=="" and page in ["HUD","Inventory"]:select_slot(event.keycode-KEY_1)
				else:handled=false
			KEY_RIGHT: _focus_step(Vector2.RIGHT)
			KEY_LEFT: _focus_step(Vector2.LEFT)
			KEY_UP: _focus_step(Vector2.UP)
			KEY_DOWN: _focus_step(Vector2.DOWN)
			KEY_ENTER,KEY_SPACE:
				if page=="Dialogue":_advance()
				elif _focus_id!="":_activate(_focus_id)
				elif page=="HUD" and hotbar[active_slot]!="":item_used.emit(str(hotbar[active_slot]))
				else: _focus_step(Vector2.ZERO)
			_: handled=false
	elif event is InputEventJoypadButton and event.pressed:
		if page=="HUD" and event.button_index in [JOY_BUTTON_DPAD_RIGHT,JOY_BUTTON_DPAD_LEFT,JOY_BUTTON_DPAD_UP,JOY_BUTTON_DPAD_DOWN]:return
		if page=="HUD" and event.button_index==JOY_BUTTON_A and not hud_use_shortcut:return
		match event.button_index:
			JOY_BUTTON_BACK:
				if page=="HUD":show_page("Inventory")
				elif _overlay!="":_close_overlay()
				elif page in TABS or page=="Relics":show_page("HUD")
				else:handled=false
			JOY_BUTTON_Y:
				if page=="HUD":show_page("Emotes")
				elif page=="Emotes":show_page("HUD")
				else:handled=false
			JOY_BUTTON_START: _back()
			JOY_BUTTON_B: _back()
			JOY_BUTTON_DPAD_RIGHT: _focus_step(Vector2.RIGHT)
			JOY_BUTTON_DPAD_LEFT: _focus_step(Vector2.LEFT)
			JOY_BUTTON_DPAD_UP: _focus_step(Vector2.UP)
			JOY_BUTTON_DPAD_DOWN: _focus_step(Vector2.DOWN)
			JOY_BUTTON_A:
				if page=="Dialogue": _advance()
				elif _focus_id!="": _activate(_focus_id)
				elif page=="HUD" and hotbar[active_slot]!="":item_used.emit(str(hotbar[active_slot]))
				else: _focus_step(Vector2.ZERO)
			_:handled=false
	else:handled=false
	if handled:get_viewport().set_input_as_handled()
