@tool
extends TextureButton

@export var active_texture: Texture2D
var resting_texture: Texture2D

func _ready() -> void:
	resting_texture = texture_normal
	focus_entered.connect(_update_state)
	focus_exited.connect(_update_state)
	_update_state()

func _update_state() -> void:
	texture_normal = active_texture if has_focus() else resting_texture

func _gui_input(event: InputEvent) -> void:
	# A project may leave the south face button unbound in its UI input map.
	if event is InputEventJoypadButton and event.button_index == JOY_BUTTON_A:
		if event.pressed and not event.is_action("ui_accept") and has_focus():
			accept_event()
			pressed.emit()
