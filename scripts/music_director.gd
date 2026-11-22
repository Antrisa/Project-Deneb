extends Node
# Which song plays when: Zachary's soundtrack (21 Nov), files in audio/music/. Like Stardew, a song plays through,
# there is a short rest, then the next one is chosen for where and when you are:
#   flying (launch to landing)        Next Beacon
#   the Mine, North Cave, caverns     Crystal Seam
#   Bram's Sundries                   Bram's Stall Chirp
#   the Mess hall                     Lit Mess-Window
#   anywhere else on the station      06:00 Moonlit Morning, 09:00 the season's song, 12:00 Lunch Ran Long,
#                                     15:00 the season's song, 20:00 Stary Night
#   the season's song                 Spring Moon-Green Awakening, Summer Sun Under the Dome, Autumn Fall in the
#                                     Landing, Winter Winter in the Station (Moonlit Morning until that file is in)
# Going somewhere with a different song fades over to it at once; a song cut short that way picks up where it left
# off if you come back within a minute and a half (a quick visit to Bram's). Walking about the station lets the
# song finish, so the hour changes the music gently. Waking on a new day starts the morning song.
# main.gd owns the player (`music`, which the title screen pauses while it is open), keeps `music_on` (M), and
# calls update() every frame.

const MUSIC_DIR := "res://audio/music/"
const BASE_DB := -6.0          # how loud the music sits under the sound effects
const REST := 10.0             # seconds of quiet between songs
const FADE := 1.2              # seconds to fade a song out when the place changes
const RESUME_FOR := 90.0       # seconds a cut-short song remembers where it was

# Song id -> file in audio/music/, and the gain (dB) that brings it to -16 LUFS like the others.
const SONGS := {
	"moonlit_morning": ["moonlit_morning.mp3", -0.6],
	"moon_green_awakening": ["moon_green_awakening.mp3", -0.4],
	"sun_under_the_dome": ["sun_under_the_dome.mp3", -0.8],
	"fall_in_the_landing": ["fall_in_the_landing.mp3", 0.5],
	"winter_in_the_station": ["winter_in_the_station.mp3", 0.0],   # not in yet: the upload was a copy of Lunch Ran Long
	"lunch_ran_long": ["lunch_ran_long.mp3", -0.1],
	"stary_night": ["stary_night.mp3", -0.1],
	"crystal_seam": ["crystal_seam.mp3", 1.0],
	"brams_stall_chirp": ["brams_stall_chirp.mp3", 0.1],
	"lit_mess_window": ["lit_mess_window.mp3", -2.9],
	"next_beacon": ["next_beacon.mp3", -1.0],
}
const SEASON_SONGS := {"Spring": "moon_green_awakening", "Summer": "sun_under_the_dome", "Autumn": "fall_in_the_landing", "Winter": "winter_in_the_station"}
const PLACE_SONGS := {"space": "next_beacon", "mines": "crystal_seam", "bram": "brams_stall_chirp", "mess": "lit_mess_window"}
const Bridge = preload("res://scripts/datapad_bridge.gd")

var world                      # main.gd
var player: AudioStreamPlayer
var _place := ""               # space, mines, bram, mess or station
var _day := -1
var _state := "idle"           # idle, playing, fading, resting
var _song := ""                # the song in the player
var _next := ""                # the song to start when a fade ends
var _timer := 0.0
var _clock := 0.0              # real seconds, for _resume
var _resume := {}              # song -> [position, _clock when it was cut short]
var _streams := {}


func setup(main_world, music_player: AudioStreamPlayer) -> void:
	world = main_world
	player = music_player
	player.finished.connect(_on_finished)


func update(delta: float) -> void:
	_clock += delta
	if world.title != null and world.title.open:
		return                 # the title screen plays its own theme and pauses this player
	if not world.music_on:
		if _state != "idle":
			player.stop()
			_state = "idle"
			_song = ""
		return
	var place := _place_now()
	var day: int = int(world.day)
	if place != _place or day != _day:
		_place = place
		_day = day
		_switch_to(pick())
	if _state == "idle":
		_start(pick())
	elif _state == "fading":
		_timer -= delta
		player.volume_db = _level(_song) - 40.0 * (1.0 - maxf(_timer, 0.0) / FADE)
		if _timer <= 0.0:
			_start(_next)
	elif _state == "resting":
		_timer -= delta
		if _timer <= 0.0:
			_start(pick())


# The song for where and when the player is now.
func pick() -> String:
	if PLACE_SONGS.has(_place):
		return str(PLACE_SONGS[_place])
	var hour := float(world.minutes) / 60.0
	if hour < 9.0:
		return "moonlit_morning"
	if hour >= 20.0:
		return "stary_night"
	if hour >= 12.0 and hour < 15.0:
		return "lunch_ran_long"
	var date: Array = Bridge.season_date(int(world.day))
	var song: String = SEASON_SONGS.get(str(date[0]), "moonlit_morning")
	return song if _exists(song) else "moonlit_morning"


func _place_now() -> String:
	if (world.ship_map != null and world.ship_map.open) or (world.battle != null and world.battle.open):
		return "space"
	var area: String = world.current_area
	if area == "mine" or area == "tunnels" or area.begins_with("cav_"):
		return "mines"
	if area == "bram" or area == "mess":
		return area
	return "station"


# Fade over to `song` unless it is already playing.
func _switch_to(song: String) -> void:
	if _state == "playing" and song == _song:
		return
	if _state == "playing":
		_resume[_song] = [player.get_playback_position(), _clock]
		_state = "fading"
		_timer = FADE
		_next = song
	elif _state == "fading":
		_next = song
	else:
		_start(song)


func _start(song: String) -> void:
	player.stop()
	var stream := _stream(song)
	if stream == null:
		_song = ""
		_state = "resting"
		_timer = REST
		return
	player.stream = stream
	player.volume_db = _level(song)
	var start_at := 0.0
	if _resume.has(song):
		var saved: Array = _resume[song]
		if _clock - float(saved[1]) < RESUME_FOR:
			start_at = float(saved[0])
		_resume.erase(song)
	_song = song
	_state = "playing"
	player.play(start_at)


func _on_finished() -> void:
	_resume.erase(_song)
	_state = "resting"
	_timer = REST


func _level(song: String) -> float:
	if not SONGS.has(song):
		return BASE_DB
	var entry: Array = SONGS[song]
	return BASE_DB + float(entry[1])


func _exists(song: String) -> bool:
	if not SONGS.has(song):
		return false
	var entry: Array = SONGS[song]
	return ResourceLoader.exists(MUSIC_DIR + str(entry[0]))


func _stream(song: String) -> AudioStream:
	if _streams.has(song):
		return _streams[song]
	if not _exists(song):
		return null
	var entry: Array = SONGS[song]
	var stream: AudioStream = load(MUSIC_DIR + str(entry[0]))
	_streams[song] = stream
	return stream
