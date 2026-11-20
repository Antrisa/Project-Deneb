extends Node2D

## Instance once per character. The node origin is at the character's feet.
## Each peer should use identical player node paths and player authorities.
const EMOTES: Array[StringName] = [
	&"surprise", &"question", &"love", &"joy", &"sad", &"frustrated",
	&"hello", &"ready", &"no", &"wait", &"help", &"follow", &"cute"
]
const POP_SECONDS := 0.08
const RISE_SECONDS := 0.10
const CLOSE_SECONDS := 0.10

## Distance above the foot origin to the bottom of the bubble.
@export_range(0, 160, 1) var head_clearance := 48
@export_range(0.3, 6.0, 0.1) var coop_hold_seconds := 1.4
@onready var bubble: Sprite2D = $Bubble

var active_emote: StringName = &""
var _elapsed := 0.0
var _hold := 0.0

func _ready() -> void:
	set_multiplayer_authority(get_parent().get_multiplayer_authority())
	clear_emote()

## Call from dialogue or a cutscene. Run on every peer viewing that story beat.
func show_story(emote_id: StringName, hold_seconds := 1.4) -> bool:
	var row := EMOTES.find(emote_id)
	if row < 0:
		return false
	active_emote = emote_id
	_elapsed = 0.0
	_hold = clampf(hold_seconds, 0.1, 30.0)
	bubble.frame_coords = Vector2i(0, row)
	bubble.position = Vector2(-12, -head_clearance - 24)
	bubble.show()
	set_process(true)
	return true

## Call from the owning player's input or emote menu.
func send_coop(emote_id: StringName) -> bool:
	if not EMOTES.has(emote_id) or not is_multiplayer_authority():
		return false
	if not multiplayer.has_multiplayer_peer() or multiplayer.multiplayer_peer is OfflineMultiplayerPeer:
		return show_story(emote_id, coop_hold_seconds)
	if multiplayer.multiplayer_peer.get_connection_status() != MultiplayerPeer.CONNECTION_CONNECTED:
		return false
	return rpc(&"_receive_coop", emote_id) == OK

@rpc("authority", "call_local", "reliable")
func _receive_coop(emote_id: StringName) -> void:
	show_story(emote_id, coop_hold_seconds)

func clear_emote() -> void:
	active_emote = &""
	bubble.hide()
	set_process(false)

func _process(delta: float) -> void:
	_elapsed += delta
	var column := 0
	if _elapsed >= POP_SECONDS + RISE_SECONDS + _hold + CLOSE_SECONDS:
		clear_emote()
		return
	elif _elapsed >= POP_SECONDS + RISE_SECONDS + _hold:
		column = 3
	elif _elapsed >= POP_SECONDS + RISE_SECONDS:
		column = 2
	elif _elapsed >= POP_SECONDS:
		column = 1
	bubble.frame_coords = Vector2i(column, bubble.frame_coords.y)
