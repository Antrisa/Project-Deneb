extends Node
# Which song plays when: Zachary's soundtrack (21 Nov), files in audio/music/. Like Stardew, a song plays through,
# then there's quiet for a while (Zachary: "there can be long breaks inbetween songs"): one to three minutes on the
# station, less where a place has its own songs, and only a few seconds on a flight. Then the next song is chosen
# for where and when you are. Each place and time has a small playlist; the song is picked at random from it,
# never the same one twice running.
#   character screen                   A New Path (it carries on into the first morning)
#   flying (launch to landing)         Next Beacon, Nebula Waltz
#   the Mine, North Cave, caverns      Crystal Seam
#   Bram's Sundries                    Bram's Stall Chirp
#   the Mess hall                      Lit Mess-Window
#   Survey Level (S.A.R.A.'s core)     The AI Core
#   Observation Lounge                 Nebula Waltz
#   Agri Complex, 06:00-21:00          Greenhouse Plucks, Tram Past Greenhouses
#   anywhere else on the station:
#     06:00                            Moonlit Morning (both takes), A New Path
#     09:00 and 15:00                  the season's songs, Station Beeps at Echo Landing, Echo Landing
#     12:00                            Lunch Ran Long, Station Beeps at Echo Landing
#     18:00                            Lit Window Across the Station
#     21:00                            Stary Night, Lit Window Across the Station
#   the season's songs                 Spring: Moon-Green Awakening, Spring Shift. Summer: Sun Under the Dome.
#                                      Autumn: Fall in the Landing. Winter: Frost on the Glass (and Winter in the
#                                      Station once that file is in).
# Walking into a place with its own songs plays one at once (fading out whatever was on). Coming back out onto the
# station picks up a song that visit cut short, from where it stopped, if it was within a minute and a half (a
# quick visit to Bram's); otherwise the station stays quiet until its next song is due. Walking about the station
# lets a song finish, so the hour changes the music gently. Waking on a new day starts a morning song.
# main.gd owns the player (`music`, which the title screen pauses while it is open), keeps `music_on` (M), and
# calls update() every frame.

const MUSIC_DIR := "res://audio/music/"
const BASE_DB := -6.0          # how loud the music sits under the sound effects
const QUIET := Vector2(60.0, 180.0)        # seconds of quiet after a song on the station (shortest, longest)
const PLACE_QUIET := Vector2(20.0, 45.0)   # ... where a place has its own songs (the mines, Bram's, the lounge)
const SPACE_QUIET := Vector2(4.0, 8.0)     # ... on a flight
const FADE := 1.2              # seconds to fade a song out when the place changes
const RESUME_FOR := 90.0       # seconds a cut-short song remembers where it was

# Song id -> file in audio/music/, and the gain (dB) that brings it to -16 LUFS like the others.
const SONGS := {
	"moonlit_morning": ["moonlit_morning.mp3", -0.6],
	"moonlit_morning_2": ["moonlit_morning_2.mp3", -0.6],      # the second, longer take
	"a_new_path": ["a_new_path.mp3", -0.6],
	"moon_green_awakening": ["moon_green_awakening.mp3", -0.4],
	"spring_shift": ["spring_shift.mp3", 0.2],
	"sun_under_the_dome": ["sun_under_the_dome.mp3", -0.8],
	"fall_in_the_landing": ["fall_in_the_landing.mp3", 0.5],
	"frost_on_the_glass": ["frost_on_the_glass.mp3", -1.2],
	"winter_in_the_station": ["winter_in_the_station.mp3", 0.0],   # not in yet: the upload was a copy of Lunch Ran Long
	"station_beeps": ["station_beeps.mp3", -0.3],
	"echo_landing": ["echo_landing.mp3", 0.2],             # added 22 Nov
	"lunch_ran_long": ["lunch_ran_long.mp3", -0.1],
	"lit_window_across_the_station": ["lit_window_across_the_station.mp3", 0.2],
	"stary_night": ["stary_night.mp3", -0.1],
	"crystal_seam": ["crystal_seam.mp3", 1.0],
	"brams_stall_chirp": ["brams_stall_chirp.mp3", 0.1],
	"lit_mess_window": ["lit_mess_window.mp3", -2.9],
	"the_ai_core": ["the_ai_core.mp3", 0.9],
	"nebula_waltz": ["nebula_waltz.mp3", -0.7],
	"greenhouse_plucks": ["greenhouse_plucks.mp3", 0.1],
	"tram_past_greenhouses": ["tram_past_greenhouses.mp3", -0.2],
	"next_beacon": ["next_beacon.mp3", -1.0],
}
const PLACE_SONGS := {
	"creator": ["a_new_path"],
	"space": ["next_beacon", "nebula_waltz"],
	"mines": ["crystal_seam"],
	"bram": ["brams_stall_chirp"],
	"mess": ["lit_mess_window"],
	"top": ["the_ai_core"],
	"lounge": ["nebula_waltz"],
}
const AGRI_SONGS := ["greenhouse_plucks", "tram_past_greenhouses"]
const MORNING_SONGS := ["moonlit_morning", "moonlit_morning_2", "a_new_path"]
const LUNCH_SONGS := ["lunch_ran_long", "station_beeps"]
const EVENING_SONGS := ["lit_window_across_the_station"]
const NIGHT_SONGS := ["stary_night", "lit_window_across_the_station"]
const DAY_SONGS := ["station_beeps", "echo_landing"]          # join the season's songs at 09:00 and 15:00
const SEASON_SONGS := {
	"Spring": ["moon_green_awakening", "spring_shift"],
	"Summer": ["sun_under_the_dome"],
	"Autumn": ["fall_in_the_landing"],
	"Winter": ["frost_on_the_glass", "winter_in_the_station"],
}
const Bridge = preload("res://scripts/datapad_bridge.gd")

var world                      # main.gd
var player: AudioStreamPlayer
var _place := ""               # creator, space, mines, bram, mess, top, lounge, agri or station
var _day := -1
var _state := "idle"           # idle, playing, fading, resting
var _song := ""                # the song in the player
var _last := ""                # the song heard last, not to be picked again straight away
var _next := ""                # the song to start when a fade ends
var _timer := 0.0
var _clock := 0.0              # real seconds, for _resume
var _resume := {}              # song -> [position, _clock when it was cut short]
var _streams := {}
var _rng := RandomNumberGenerator.new()


func setup(main_world, music_player: AudioStreamPlayer) -> void:
	world = main_world
	player = music_player
	player.finished.connect(_on_finished)
	_rng.randomize()


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
		var first := _place == ""
		var new_day := day != _day
		_place = place
		_day = day
		var songs := playlist()
		if not (_state == "playing" and songs.has(_song)):
			var song := _choose(songs)
			if first or new_day or _has_own_songs() or _resumable(song):
				_switch_to(song)
			else:
				_quiet()       # back out onto the station: no new song until one is due
	if _state == "idle":
		_start(_choose(playlist()))
	elif _state == "fading":
		_timer -= delta
		player.volume_db = _level(_song) - 40.0 * (1.0 - maxf(_timer, 0.0) / FADE)
		if _timer <= 0.0:
			if _next == "":
				player.stop()
				_song = ""
				_rest()
			else:
				_start(_next)
	elif _state == "resting":
		_timer -= delta
		if _timer <= 0.0:
			_start(_choose(playlist()))


# The songs that suit where and when the player is now (only those whose files are in).
func playlist() -> Array:
	var hour := float(world.minutes) / 60.0
	var names: Array = []
	if PLACE_SONGS.has(_place):
		names = PLACE_SONGS[_place]
	elif _place == "agri" and hour >= 6.0 and hour < 21.0:
		names = AGRI_SONGS
	elif hour < 9.0:
		names = MORNING_SONGS
	elif hour >= 21.0:
		names = NIGHT_SONGS
	elif hour >= 18.0:
		names = EVENING_SONGS
	elif hour >= 12.0 and hour < 15.0:
		names = LUNCH_SONGS
	else:
		var date: Array = Bridge.season_date(int(world.day))
		var season: Array = SEASON_SONGS.get(str(date[0]), [])
		names = season + DAY_SONGS
	var songs: Array = []
	for song: String in names:
		if _exists(song):
			songs.append(song)
	if songs.is_empty():
		songs.append("moonlit_morning")
	return songs


# A song cut short a moment ago comes back first; otherwise any but the one just heard.
func _choose(songs: Array) -> String:
	for song: String in songs:
		if _resumable(song):
			return song
	var options: Array = []
	for song: String in songs:
		if song != _last and song != _song:
			options.append(song)
	if options.is_empty():
		options = songs
	return str(options[_rng.randi_range(0, options.size() - 1)])


func _resumable(song: String) -> bool:
	if not _resume.has(song):
		return false
	var saved: Array = _resume[song]
	return _clock - float(saved[1]) < RESUME_FOR


# Somewhere with its own songs (Bram's, the mines, a flight, the greenhouse by day...) rather than the station's.
func _has_own_songs() -> bool:
	if PLACE_SONGS.has(_place):
		return true
	var hour := float(world.minutes) / 60.0
	return _place == "agri" and hour >= 6.0 and hour < 21.0


func _place_now() -> String:
	if world.creator != null and world.creator.open:
		return "creator"
	if (world.ship_map != null and world.ship_map.open) or (world.battle != null and world.battle.open):
		return "space"
	var area: String = world.current_area
	if area == "mine" or area == "tunnels" or area.begins_with("cav_"):
		return "mines"
	if area == "bram" or area == "mess" or area == "top" or area == "lounge" or area == "agri":
		return area
	return "station"


# Fade out whatever is playing, then be quiet for a while.
func _quiet() -> void:
	if _state == "playing":
		_resume[_song] = [player.get_playback_position(), _clock]
		_state = "fading"
		_timer = FADE
		_next = ""
	elif _state == "fading":
		_next = ""
	else:
		var left := _timer if _state == "resting" else 0.0
		_rest()                # a station-length quiet, or what was left of the old one if longer
		_timer = maxf(_timer, left)


func _rest() -> void:
	var span := QUIET
	if _place == "space":
		span = SPACE_QUIET
	elif _has_own_songs():
		span = PLACE_QUIET
	_state = "resting"
	_timer = _rng.randf_range(span.x, span.y)


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
		_rest()
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
	_last = song
	_state = "playing"
	player.play(start_at)


func _on_finished() -> void:
	_resume.erase(_song)
	_song = ""
	_rest()


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
