extends Node
# Which song plays when: Zachary's soundtrack (21 Nov), files in audio/music/. Like Stardew, a song plays through,
# then there's quiet for a while (Zachary: "there can be long breaks inbetween songs"): one to three minutes on the
# station, less where a place has its own songs, and only a few seconds on a flight. Then the next song is chosen
# for where and when you are. Each place and time has a small playlist; the song is picked at random from it,
# never the same one twice running.
#   character screen                   A New Path (it carries on into the first morning)
#   flying (launch to landing)         Next Beacon, Nebula Waltz
#   a space battle                     the combat songs (audio/music/combat_1.mp3, combat_2.mp3) once they're in;
#                                      until then the flying songs carry on through fights
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
	"combat_1": ["combat_1.mp3", 0.0],        # not in yet (23 Nov): battle music to come
	"combat_2": ["combat_2.mp3", 0.0],
	"greenhouse_plucks": ["greenhouse_plucks.mp3", 0.1],
	"tram_past_greenhouses": ["tram_past_greenhouses.mp3", -0.2],
	"next_beacon": ["next_beacon.mp3", -1.0],
	"space_battle": ["space_battle.mp3", 0.2],          # 25 Nov: the prologue's ambush (a scene score, below)
	"lunar_discovery": ["lunar_discovery.mp3", 0.6],    # 25 Nov: the prologue's Mother-Drone (a scene score)
}
# Scene scores (25 Nov, Zachary: "not the whole songs but the ends fit to the end of each scene"). A cutscene plays
# the end of a song timed to it: from a starting point, holding on a stretch while the player reads (it loops, whole
# bars), then jumping on to a cue the scene needs on time: Space Battle's breakdown and last big hit under the FTL
# jump, Lunar Discovery's wind-down ending as the Mother-Drone dies. Jumps land on the next bar (a song with a beat
# grid here) or at once, cross-faded (one without). Where the score is keeps counting even with the music turned
# off, so the scene keeps its timing. Steps: scripts/cutscene.gd "score", "score_cue", "score_wait", "score_end".
# Beat grids measured from the files (25 Nov): beat length and the time of a downbeat, in seconds; bars of four.
const SCORE_GRID := {
	"space_battle": [0.39535, 0.0939, 4],     # 151.8 bpm
}
const PLACE_SONGS := {
	"creator": ["a_new_path"],
	"space": ["next_beacon", "nebula_waltz"],
	"battle": ["combat_1", "combat_2"],
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
# Ambient beds under the music (24 Nov): the station's hum, fans and drips in the agri dome, water dripping in the
# caverns and at the lake, the ship's drone in space. They loop, and fade across when the place changes.
const AMB_DB := -6.0
var amb: AudioStreamPlayer
var _amb_name := ""
var _amb_streams := {}
var _sc := ""                 # the scene score playing ("": none)
var _sc_pos := 0.0            # where it is, in seconds into the song
var _sc_len := 0.0
var _sc_loop := Vector2(-1.0, -1.0)
var _sc_cue := -1.0           # jump here at the next bar (or at once)
var _sc_players: Array = []   # two players, so a jump can cross-fade
var _sc_live := 0
var _sc_fade := 0.0           # seconds of cross-fade left
var _sc_fade_len := 0.03
var _sc_off := false          # the music was off: start the score again where it is when it comes back on


func setup(main_world, music_player: AudioStreamPlayer) -> void:
	world = main_world
	player = music_player
	player.finished.connect(_on_finished)
	_rng.randomize()
	amb = AudioStreamPlayer.new()
	amb.volume_db = -60.0
	add_child(amb)
	amb.finished.connect(func(): if _amb_name != "": amb.play())     # loop the bed
	for i in 2:
		var sp := AudioStreamPlayer.new()
		sp.bus = player.bus
		add_child(sp)
		_sc_players.append(sp)


func update(delta: float) -> void:
	_clock += delta
	_update_ambient(delta)
	if _sc != "":
		var mode: String = str(world.cutscene.music_mode) if world.cutscene != null and world.cutscene.running else ""
		if mode == "score":
			_score_update(delta)
			return
		score_stop()
	if world.title != null and world.title.open:
		return                 # the title screen plays its own theme and pauses this player
	if not world.music_on:
		if _state != "idle":
			player.stop()
			_state = "idle"
			_song = ""
		return
	# A cutscene can hush the music or choose its own (scripts/cutscene.gd "music", 24 Nov: the prologue)
	var scene_music: String = str(world.cutscene.music_mode) if world.cutscene != null and world.cutscene.running else ""
	if scene_music != "":
		_scene_music(scene_music, delta)
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


func _scene_music(mode: String, delta: float) -> void:
	if mode == "silence":
		if player.playing:
			player.volume_db -= 40.0 * delta
			if player.volume_db <= -45.0:
				player.stop()
		if not player.playing:
			_song = ""
			_state = "resting"
			_timer = 3.0
		return
	if _song != mode or not player.playing:
		_start(mode)


# ---------------------------------------------------------------- scene scores

# Starts song at from (seconds); loop: hold on [x, y) until a cue (x < 0: no hold).
func score_play(song: String, from: float, loop: Vector2 = Vector2(-1.0, -1.0)) -> void:
	player.stop()
	_song = ""
	_state = "resting"
	_timer = 3.0
	for sp in _sc_players:
		sp.stop()
	var stream := _stream(song)
	_sc = song
	_sc_pos = from
	_sc_loop = loop
	_sc_cue = -1.0
	_sc_fade = 0.0
	_sc_len = stream.get_length() if stream != null else from + 30.0
	_sc_live = 0
	_sc_off = not world.music_on
	if stream != null:
		for sp in _sc_players:
			sp.stream = stream
		if world.music_on:
			_sc_players[0].volume_db = _level(song)
			_sc_players[0].play(from)


# Moves the score on to `to` at the next bar (straight away, cross-faded, for a song without a beat grid), and lets
# go of any hold. Nothing happens if it's already there or past it.
func score_cue(to: float) -> void:
	if _sc != "" and _sc_pos < to:
		_sc_cue = to


func score_pos() -> float:
	return _sc_pos if _sc != "" else 1e9


func score_done() -> bool:
	return _sc == "" or _sc_pos >= _sc_len - 0.05


func score_stop() -> void:
	for sp in _sc_players:
		sp.stop()
	_sc = ""


func _score_next_bar(t: float) -> float:
	if not SCORE_GRID.has(_sc):
		return t
	var g: Array = SCORE_GRID[_sc]
	var bar: float = float(g[0]) * float(g[2])
	return float(g[1]) + ceilf((t - float(g[1])) / bar - 0.0001) * bar


func _score_update(delta: float) -> void:
	var live: AudioStreamPlayer = _sc_players[_sc_live]
	var audible: bool = world.music_on and live.playing
	if world.music_on and _sc_off and _sc_pos < _sc_len - 0.1 and live.stream != null:
		_sc_off = false
		live.volume_db = _level(_sc)          # the music came back on: pick the score up where it is
		live.play(_sc_pos)
		audible = true
	elif not world.music_on:
		_sc_off = true
		for sp in _sc_players:
			sp.stop()
	var pos: float = (live.get_playback_position() + AudioServer.get_time_since_last_mix()) if audible else _sc_pos + delta
	if audible and pos < _sc_pos - 1.0 and _sc_loop.x < 0.0:
		pos = _sc_pos + delta                 # the player wrapped round at the song's end
	if _sc_cue >= 0.0:
		var at := _score_next_bar(_sc_pos)
		if pos >= at:
			var to := _sc_cue + (pos - at)
			_sc_cue = -1.0
			_sc_loop = Vector2(-1.0, -1.0)
			_score_jump(to, 0.03 if SCORE_GRID.has(_sc) else 0.6)
			pos = to
	elif _sc_loop.x >= 0.0 and pos >= _sc_loop.y:
		pos = _sc_loop.x + (pos - _sc_loop.y)
		_score_jump(pos, 0.03 if SCORE_GRID.has(_sc) else 0.35)     # on the bar, or a soft seam
	_sc_pos = minf(pos, _sc_len)
	if _sc_fade > 0.0:
		_sc_fade = maxf(0.0, _sc_fade - delta)
		var k := _sc_fade / _sc_fade_len
		_sc_players[_sc_live].volume_db = _level(_sc) - 40.0 * k
		var old: AudioStreamPlayer = _sc_players[1 - _sc_live]
		old.volume_db = _level(_sc) - 40.0 * (1.0 - k)
		if _sc_fade <= 0.0:
			old.stop()


func _score_jump(to: float, fade: float) -> void:
	if not world.music_on:
		return
	_sc_live = 1 - _sc_live
	var sp: AudioStreamPlayer = _sc_players[_sc_live]
	sp.volume_db = _level(_sc) - 40.0
	sp.play(to)
	_sc_fade = fade
	_sc_fade_len = fade


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
	if world.battle != null and world.battle.open and (_exists("combat_1") or _exists("combat_2")):
		return "battle"
	if (world.ship_map != null and world.ship_map.open) or (world.battle != null and world.battle.open):
		return "space"
	var area: String = world.current_area
	if area == "mine" or area == "tunnels" or area.begins_with("cav_"):
		return "mines"
	if area == "aptPlayer" or area == "aptCoop":
		return "agri"          # the apartments open onto the farm's porch: the farm's songs carry on indoors
	if area == "bram" or area == "mess" or area == "top" or area == "lounge" or area == "agri":
		return area
	return "station"


func _ambient_now() -> String:
	if world.title != null and world.title.open:
		return ""
	if world.cutscene != null and world.cutscene.running and str(world.cutscene.amb_mode) != "":
		return "" if str(world.cutscene.amb_mode) == "none" else str(world.cutscene.amb_mode)
	var place := _place_now()
	if place == "creator":
		return ""
	if place == "space" or place == "battle":
		return "amb_space"
	var area: String = world.current_area
	if place == "mines" or area == "lake":
		return "amb_caves"
	# No bed on the station or in the Agri Complex (Zachary, 24 Nov: "a static noise in the background ... very
	# annoying, find and remove"). amb_station and amb_agri were made-up noise placeholders; the cave and space beds
	# are cut from his recordings and stay.
	return ""


func _amb_stream(bed: String):
	if not _amb_streams.has(bed):
		var found = null
		for ext in ["ogg", "wav"]:
			var path := "res://audio/%s.%s" % [bed, ext]
			if ResourceLoader.exists(path):
				found = load(path)
				break
		_amb_streams[bed] = found
	return _amb_streams[bed]


func _update_ambient(delta: float) -> void:
	var want := _ambient_now()
	if want != _amb_name:
		amb.volume_db = maxf(-60.0, amb.volume_db - 40.0 * delta)        # fade the old bed out first
		if amb.volume_db <= -59.0 or not amb.playing:
			_amb_name = want
			amb.stop()
			var bed_stream = _amb_stream(want) if want != "" else null
			if bed_stream != null:
				amb.stream = bed_stream
				amb.volume_db = -60.0
				amb.play()
	elif amb.playing:
		amb.volume_db = minf(AMB_DB, amb.volume_db + 20.0 * delta)


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
	if _place == "space" or _place == "battle":
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
	return _path(song) != ""


# The song's file: as named in SONGS, or the same name as .ogg or .wav (free music often comes as those).
func _path(song: String) -> String:
	if not SONGS.has(song):
		return ""
	var named: String = MUSIC_DIR + str(SONGS[song][0])
	for p in [named, named.get_basename() + ".ogg", named.get_basename() + ".wav"]:
		if ResourceLoader.exists(p):
			return p
	return ""


func _stream(song: String) -> AudioStream:
	if _streams.has(song):
		return _streams[song]
	if not _exists(song):
		return null
	var stream: AudioStream = load(_path(song))
	_streams[song] = stream
	return stream
