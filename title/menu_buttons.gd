extends Control
## Place this overlay above the game's own animated or static title artwork.
signal play_requested
signal coop_requested
signal settings_requested
signal quit_requested

const PixelGrid = preload("res://ui/pixel_grid.gd")

@onready var actions: Array[TextureButton] = [%Play, %Coop, %Settings, %Quit]

func _ready() -> void:
	resized.connect(_place_stack)
	get_viewport().size_changed.connect(_place_stack)
	$Stack.resized.connect(_place_stack)
	_place_stack()
	for i in actions.size():
		var button := actions[i]
		var previous := button.get_path_to(actions[posmod(i - 1, actions.size())])
		var following := button.get_path_to(actions[(i + 1) % actions.size()])
		button.focus_neighbor_top = previous
		button.focus_previous = previous
		button.focus_neighbor_bottom = following
		button.focus_next = following
		button.mouse_entered.connect(button.grab_focus)
	%Play.pressed.connect(play_requested.emit)
	%Coop.pressed.connect(coop_requested.emit)
	%Settings.pressed.connect(settings_requested.emit)
	%Quit.pressed.connect(quit_requested.emit)
	%Play.grab_focus()

func restore_focus(button_name: StringName) -> void:
	var button := get_node_or_null(NodePath("%" + str(button_name))) as TextureButton
	if button:
		button.grab_focus()

func _place_stack() -> void:
	PixelGrid.place_left(self, $Stack)
