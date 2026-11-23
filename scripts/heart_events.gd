extends RefCounted
# Heart events (22 Nov 2026), played by scripts/cutscene.gd. Written from docs/story/characters/<NAME>.md;
# Zachary's lines are kept as he wrote them, the rest are Claude's drafts for him to change.
#
# Each event:
#   who, hearts     whose hearts trigger it, and how many it needs (NPC Master 3.1: 100 points a heart)
#   area            the map you walk into to set it off (checked each time you arrive somewhere)
#   windows         [[weekdays or null, "from", "to"], ...] (0 = Monday ... 6 = Sunday; times can pass 24:00)
#   flags / not     story flags that must / must not be set (main.gd _flag())
#   seen            events that must have played first
#   partner         true: only while you're dating them
#   player          where you stand when it starts: [x, y, facing]
#   cast            who is there when it starts: [[who, x, y, facing, pose], ...] (pose optional)
#   steps           what happens (the step list is at the top of scripts/cutscene.gd)
# A resident who hasn't arrived on the station yet is left out, and their lines are skipped.

# The order they're checked in (and the order F4 plays them in debug builds).
const ORDER := ["freya_2", "freya_4", "freya_6", "freya_8", "freya_10"]

const EVENTS := {
	# ---------------------------------------------------------------- Freya (docs/story/characters/FREYA.md)
	"freya_2": {
		"who": "Freya", "hearts": 2, "title": "The Stubborn Heating Pump",
		"area": "eng", "windows": [[null, "16:30", "17:30"]],
		"player": [75, 22, "u"],
		"cast": [["Freya", 75, 19, "u", "weld u"]],
		"steps": [
			["wait", 0.6],
			["sfx", "hit"], ["shake", 0.3, 2.0],
			["say", "Freya", ["[angry] Come on, you rusty piece of Terran scrap—turn! (Clang!) Ow—my knuckles!"]],
			["pose", "Freya", ""], ["face", "Freya", "d"], ["emote", "Freya", "surprise"],
			["say", "Freya", [
				"[surprised] Oh, hey! Don't mind me—just losing a wrestling match with Sector Three's heating pump.",
				"My dad could tune these things by ear in five minutes flat.",
				"[sad] Ever since he passed, I feel like I'm just holding the station together with duct tape and stubbornness."]],
			["choose", [
				{"text": "Let me hold the brace while you torque it.", "friendship": 60, "steps": [
					["walk", "player", 74, 20], ["face", "player", "u"],
					["face", "Freya", "u"], ["pose", "Freya", "weld u"], ["wait", 1.0],
					["sfx", "hit"], ["shake", 0.25, 1.5],
					["say", "", ["You lean on the brace. She hauls on the wrench. The valve gives with a clunk, and warm air sighs through the vents."]],
					["pose", "Freya", ""], ["face", "Freya", "l"], ["pose", "Freya", "laugh"],
					["say", "Freya", ["[happy] Ha! Two people, one wrench. Dad always said a stuck valve is a two-person job pretending to be a one-person job."]]]},
				{"text": "You're keeping the whole station warm—your dad would be proud.", "friendship": 30, "steps": [
					["say", "Freya", ["[bashful] ...Yeah? He'd say I'm holding the wrench wrong."]],
					["face", "Freya", "u"], ["pose", "Freya", "weld u"], ["wait", 0.8], ["sfx", "hit"],
					["say", "", ["She shifts her grip. The valve gives with a clunk, and warm air sighs through the vents."]],
					["pose", "Freya", ""], ["face", "Freya", "d"], ["emote", "Freya", "surprise"],
					["say", "Freya", ["[surprised] Huh. I was holding the wrench wrong."]]]}]],
			["face", "Freya", "player"], ["pose", "Freya", "wave"],
			["say", "Freya", ["[happy] Thanks. Come find me in the bay sometime. I'll show you what real Terran scrap looks like."]],
			["pose", "Freya", ""],
		],
	},
	"freya_4": {
		"who": "Freya", "hearts": 4, "title": "Dad's Workbench",
		# at her bench at home: Saturday morning or Sunday afternoon (her weekend days, tools/build.py)
		"area": "home4", "windows": [[[5], "08:30", "11:00"], [[6], "15:30", "17:00"]],
		"player": [13, 8, "u"],
		"cast": [["Freya", 13, 5, "u", "rest u"]],
		"steps": [
			["wait", 0.8],
			["pose", "Freya", ""], ["face", "Freya", "d"], ["emote", "Freya", "surprise"],
			["say", "Freya", ["[surprised] Oh! Hey. Door was open? Sorry, I'm not really working."]],
			["walk", "player", 12, 6], ["face", "player", "u"],
			["face", "Freya", "u"], ["pose", "Freya", "rest u"],
			["say", "Freya", [
				"[sad] This was my dad's. Jorvik. He was the station's shipwright, before me. Before the Suite got locked up.",
				"[sad] He was testing a new FTL stabilizer. Two minutes past the launch doors, it shook itself apart. We never got him back.",
				"Tikka sealed the Suite after. I brought his toolbox home. I've never opened it."]],
			["say", "", ["She runs a thumb along a latch."]],
			["pose", "Freya", ""], ["face", "Freya", "l"],
			["say", "Freya", ["[bashful] Would you stay while I do?"]],
			["face", "Freya", "u"], ["pose", "Freya", "hammer u"], ["wait", 0.9], ["sfx", "click"], ["pose", "Freya", ""],
			["say", "", ["The latches snap. Inside, wrapped in an oilcloth: a roll of blueprints, every margin crowded with his handwriting."]],
			["face", "Freya", "l"], ["emote", "Freya", "surprise"],
			["say", "Freya", [
				"[shocked] These are the stabilizer plans. His last version. Look at the notes: 'Mount's too stiff. It has to give. Next one floats.'",
				"And here, underlined twice: 'If it sings, don't fight it. Ease off. Let it find its note.'",
				"[sad] He knew what was wrong. He was going to fix it after one more run. He always said that. 'One more run, then I'll fix it.'"]],
			["pose", "Freya", "sad"],
			["choose", [
				{"text": "Then let's fix it. Together.", "friendship": 60, "steps": [
					["pose", "Freya", ""], ["emote", "Freya", "surprise"],
					["say", "Freya", ["[surprised] Just like that?"]],
					["pose", "Freya", "laugh"],
					["say", "Freya", ["[happy] ...Yeah. Just like that. Okay."]]]},
				{"text": "You don't have to finish his work, you know.", "friendship": 60, "steps": [
					["say", "Freya", ["[sad] I know. Nobody's ever actually said that to me."]],
					["pose", "Freya", "talk"],
					["say", "Freya", ["[happy] That's kind of why I want to. Because now it's my choice."]]]}]],
			["pose", "Freya", "talk"],
			# the parts request (FREYA.md) isn't in: Zachary hasn't said whether to keep it
			["say", "Freya", ["[happy] Give me a few days with these. Next time your ship's in the bay, it's getting a floating mount."]],
			["pose", "Freya", ""],
			["flag", "freya_plans"],
		],
	},
	"freya_6": {
		"who": "Freya", "hearts": 6, "title": "Test Flight",
		"area": "bay", "windows": [[null, "18:00", "20:00"]],
		"flags": ["ship_flown"], "seen": ["freya_4"],
		"player": [22, 22, "u"],
		"cast": [["Freya", 22, 19, "d"]],
		"steps": [
			["wait", 0.5],
			["pose", "Freya", "talk"],
			["say", "Freya", [
				"[happy] Stabilizer's in. Floating mount, just like his note said. Short burn past the launch doors, three minutes at full, then home.",
				"[bashful] I'm riding along, in the duct behind your seat. Don't argue. I already measured it."]],
			["pose", "Freya", ""],
			["say", "Tikka", ["Launch control here. Same booth. Same chair.",
				"[sad] I was in this chair for his last run, Freya. I'd like a better memory of it."], "Tikka (comms)"],
			["say", "Freya", ["Then let's give you one."]],
			["fade", 1.0, 0.8], ["sfx", "warp"],
			["say", "", ["The launch doors open on the dark. The drive lights. For a minute the hum is clean."]],
			["say", "Sensors", ["Drive harmonic rising. Six tenths. Seven tenths."]],
			["sfx", "zap"], ["shake", 1.5, 3.0],
			["say", "", ["The cockpit starts to shake. Loose bolts rattle in the duct."]],
			["say", "Freya", ["[shocked] That's it. That's the sound."]],
			["say", "Tikka", ["[shocked] Freya? Freya, talk to me."], "Tikka (comms)"],
			["say", "Freya", ["'If it sings, don't fight it.' Ease off. Two-thirds. Let it find its note."]],
			["choose", [
				{"text": "[Ease off to two-thirds]", "friendship": 60, "steps": []},
				{"text": "[Hold full power]", "friendship": 0, "steps": [
					["sfx", "hit"], ["shake", 1.2, 5.0],
					["say", "", ["The shaking gets worse. Something cracks in the duct."]],
					["say", "Freya", ["[angry] Ease off! Please!"]],
					["say", "", ["You pull back to two-thirds."]]]}]],
			["say", "", ["The shaking fades. The hum drops, steadies, and settles into one clean sapphire note."]],
			["say", "Freya", ["[happy] Did you hear that purr?! Not a single harmonic wobble! Dad's design works—and it's flying on your ship!"]],
			["say", "Tikka", ["[happy] He'd have whooped so loud they'd hear it in the mine."], "Tikka (comms)"],
			["clock", 60],
			["place", "Freya", 22, 19, "d"], ["pose", "Freya", "rest d"],
			["fade", 0.0, 0.8],
			["say", "", ["The bay, later. Freya sits on a docking clamp with her helmet in her lap."]],
			["say", "Freya", ["I spent years in that booth listening to ships leave. I don't want to listen anymore.",
				"[bashful] Take me with you? On your runs. I can fix anything you break. Mostly."]],
			["choose", [
				{"text": "Welcome aboard.", "steps": []},
				{"text": "Best mechanic in the Neutral Zone? Obviously.", "steps": []}]],
			["pose", "Freya", "jump"], ["emote", "Freya", "joy"],
			["say", "Freya", ["[happy] Then I'm crew. I'll get my kit. And a cushion for that duct."]],
			["pose", "Freya", ""],
			["flag", "freya_crew"],
			["perk", "pioneer_stabilizer", "New: the Pioneer Stabilizer. Freya joined your crew."],
		],
	},
	"freya_8": {
		"who": "Freya", "hearts": 8, "title": "Under the Star Dome",
		"area": "west", "windows": [[null, "20:00", "26:00"]],
		"player": [57, 12, "u"],
		"cast": [["Freya", 57, 9, "d", "bench"]],
		"steps": [
			["wait", 0.6],
			["walk", "player", 57, 11], ["face", "player", "u"],
			["say", "Freya", ["[happy] Found me. I come here Sunday mornings. Dad used to watch the launches from this bench."]],
			["say", "Freya", ["For years I thought restoring this docking bay meant trying to become my dad.",
				"Working alongside you made me realize I don't have to be a copy of him—I get to build my own future here."]],
			["if", {"dating_other": "Freya"},
				# the friendship ending: you're dating someone else
				[["pose", "Freya", "laugh"],
				 ["say", "Freya", ["[happy] You're the best friend I've made on this station. Thought you should know."]],
				 ["pose", "Freya", "bench"]],
				[["pose", "Freya", "talk"],
				 ["say", "Freya", ["[bashful] And honestly? When we're out there together, I forget to be scared. When you fly without me, I count the minutes till you dock.",
					"[love] I like you—more than just as my favorite test pilot."]],
				 ["pose", "Freya", "bench"], ["emote", "Freya", "love"],
				 ["choose", [
					{"text": "I like you too, Freya.", "steps": [
						["partner", "Freya"],
						["emote", "Freya", "surprise"],
						["say", "Freya", ["[surprised] Wait. Really? You're not just being nice?",
							"[love] Okay. Okay! Um. I don't know what you do now. Sit with me a while?"]],
						["walk", "player", 56, 10], ["face", "player", "u"],
						["fade", 0.7, 1.2],
						["say", "", ["You sit with her on the bench and watch the stars wheel past the glass until the lamps dim."]],
						["fade", 0.0, 1.0]]},
					{"text": "You mean a lot to me, as a friend.", "steps": [
						["pose", "Freya", "sad"],
						["say", "Freya", ["[sad] Yeah. Okay. I had to say it, or I'd be asking 'what if' forever."]],
						["pose", "Freya", "bench"],
						["say", "Freya", ["[happy] You're still my favorite test pilot. That doesn't change."]]]}]]]],
			["pose", "Freya", "talk"],
			["say", "Freya", ["[happy] Oh, and from now on, anything you want upgraded, you bring it to me. Family rate."]],
			["pose", "Freya", "bench"],
			["perk", "master_mechanic", "Perk: Master Mechanic (20% off ship and tool upgrades)"],
		],
	},
	"freya_10": {
		"who": "Freya", "hearts": 10, "title": "Christening the Suite",
		"area": "bay", "windows": [[null, "09:00", "20:00"]],
		"partner": true, "seen": ["freya_8"],
		"player": [30, 29, "r"],
		"cast": [["Freya", 33, 29, "r"], ["Tikka", 34, 27, "d"], ["Sesska", 34, 31, "u"], ["Ana", 32, 31, "u"]],
		"steps": [
			["wait", 0.5],
			["face", "Tikka", "player"], ["face", "Freya", "player"],
			["say", "Tikka", ["[happy] There she is. And her favorite test pilot.",
				"[sad] This door's been shut since Jorvik's last run. I kept the code. Never had the heart to use it.",
				"[happy] It's yours, Freya. Should've been yours a long time ago."]],
			["face", "Freya", "r"], ["wait", 0.6], ["sfx", "warp"],
			["if", {"flag": "suite_restored"},
				[["say", "", ["The door slides open on clean benches, new lights and his old hull blueprints, framed."]]],
				[["say", "", ["The door grinds open on dust and dark."]],
				 ["face", "Freya", "player"], ["pose", "Freya", "laugh"],
				 ["say", "Freya", ["[happy] Okay. It needs work. We'll fix the rest together."]],
				 ["pose", "Freya", ""]]],
			["face", "Sesska", "Freya"],
			["say", "Sesska", ["[happy] Pull the sheet, dear. All four of my arms are tired of holding it up."]],
			["face", "Freya", "u"], ["wait", 0.5], ["sfx", "quest"],
			["say", "", ["The sheet falls: a brass sign reading ECHO LANDING SHIPWRIGHTS. Under it, smaller: JORVIK & FREYA."]],
			["if", {"arrived": "Ana"},
				[["face", "Ana", "Freya"],
				 ["say", "Ana", ["[happy] Fancy. Do I get a desk?"]],
				 ["face", "Freya", "Ana"],
				 ["say", "Freya", ["[happy] You get a stool. Earn the desk."]]]],
			["walk", "Freya", 31, 29], ["face", "player", "r"], ["pose", "Freya", "gift l"],
			["say", "Freya", ["[love] I made you something. From Dad's old wrench. The one he gave me when I was six."]],
			["say", "", ["A tiny wrench on a chain, polished bright."]],
			["pose", "Freya", ""], ["face", "Freya", "l"],
			["say", "Freya", ["[love] He built ships so people could come home. I think I finally get it. You're what I come home to."]],
			["emote", "Freya", "love"], ["emote", "player", "love"],
			["keepsake", "wrench_pendant", "Keepsake: Freya's wrench pendant"],
		],
	},
}
