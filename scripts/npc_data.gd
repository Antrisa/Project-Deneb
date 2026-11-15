extends RefCounted
# Who lives on the Landing and what they say.
# "id" picks the art files: art/npc_<id>.png and art/portrait_<id>.png
# "pitch" is how high their talking blips sound (1.0 is normal).
# "first" plays the first time you meet them; "repeat" lines rotate after that.
# Keep each line under about 150 characters so it fits the dialogue box.
# Start a line with [happy], [sad], [surprised], [love] or [angry] to change the speaker's portrait for that line.

const PEOPLE = {
	"Sara": {
		"id": "sara",
		"pitch": 1.3,
		"first": [
			"Easy. You have been asleep for two days. You are on Echo Landing, and you are safe.",
			"These were the head officer's quarters. It is one of the few proper beds we have left, and I wanted you quarantined for a few days. No offence meant.",
			"I am Sara. I administer the station. Your ship is in the shuttle bay, down the south lift off the town square.",
			"Tikka, in the engineering bay, can tell you how bad your drive is. Bram, on the west wing of the square, knows who is paying for odd jobs.",
			"[happy] The spaceport is just outside these barracks. One day I hope to see it finished, and full of visitors. This building would make a fine hotel.",
		],
		"repeat": [
			"I was built to listen. These days I am mostly asked where the spare blankets are.",
			"The old listening room is an observatory lounge now. They put couches in it. I have decided I like the couches.",
			"[sad] You keep looking toward the shuttle bay. It will still be there tomorrow.",
			"[happy] Given the choice, I would have run a small hotel in France. I have read a great deal about them.",
			"[love] A port, then visitors, then a hotel for them to stay in. In that order. I have had four hundred years to plan it.",
		],
	},
	"Tar'Besh": {
		"id": "tarbesh",
		"pitch": 0.8,
		"first": [
			"Ah. The one who fell. I am Tar'Besh. A pilgrim, or an exile. It depends who you ask, and I advise you not to ask.",
			"These relics are older than your empire and mine. Someone left them. I intend to learn who.",
			"[angry] Do not touch the middle one. It has opinions.",
		],
		"repeat": [
			"[happy] The robe? It was magnificent once. It is still magnificent. You are simply seeing it late.",
			"I used to collect secrets for the Junta. Now I collect them for myself. The pay is worse and the sleep is better.",
			"[surprised] If these can be woken, the Landing will never want for power again. If.",
		],
	},
	"Bram": {
		"id": "bram",
		"pitch": 0.9,
		"first": [
			"[happy] Come in, come in. Bram Ollo. I buy, I sell, I introduce people who should meet.",
			"You want off this rock, yes? Everyone does, the first week.",
			"Work is how you get credits. Credits are how you get a ship. Talk to me again when you're ready to carry something heavy.",
		],
		"repeat": [
			"[angry] People say Moogli only care about money. Untrue. I also care about lunch.",
			"Nobody owns this zone, so everybody wants a discount.",
			"[happy] Sara listens to everything, you know. I find it restful.",
		],
	},
	"Jasper": {
		"id": "jasper",
		"pitch": 1.2,
		"first": [
			"[happy] Welcome, welcome! Jasper. Today's special is ration pack number six, but I have plated it beautifully.",
			"[love] Have you ever been to Paris? No? Nor have I. But I have watched every video of it that ever reached this moon.",
			"One day people will cross the sector to eat here. You will say you knew me when it was ration packs.",
		],
		"repeat": [
			"[sad] The secret of haute cuisine is butter. We have no butter. I am working around it.",
			"Evarra says I am her brother and she is stuck with me. We arrived in the same escape pod, so she has a point.",
			"[happy] Bon appetit! That means it is not my fault if you don't like it.",
		],
	},
	"Evarra": {
		"id": "evarra",
		"pitch": 1.1,
		"first": [
			"You must be the new arrival. I'm Evarra. I bake, when there is something to bake with.",
			"The herbs on the counter are mine. They make the rations taste like food. A little.",
			"[happy] Jasper is my brother. Don't let him talk you into the number six.",
		],
		"repeat": [
			"[sad] Someone brought in fresh greens last month. I still think about it.",
			"[love] A small farm. Flowers, and bees to go with them. It isn't much to ask of a galaxy.",
			"The agri dome past the east wing is mostly dust. One corner still grows, if you are gentle with it.",
		],
	},
	"Tikka": {
		"id": "tikka",
		"pitch": 1.7,
		"first": [
			"[surprised] Oh! You're the one who fell out of the sky. I'm Tikka. Arachnay. Engineer. Eight hands, no waiting.",
			"I looked at your fold drive. It is in... several places. Some of them are still on the moon.",
			"Bring me credits and I will make it one drive again. Hull first, then the drive, then the nav core.",
		],
		"repeat": [
			"The fabrication shop made rifles once. Now it makes kettles. The kettles are better built.",
			"[love] If you find coil wire out there, any coil wire, I am very interested.",
			"[angry] Freya fixes things by hitting them. I disapprove. It works more often than it should.",
		],
	},
	"Freya": {
		"id": "freya",
		"pitch": 1.25,
		"first": [
			"[happy] Hey, you're the pilot! Freya. I keep the heat running, mostly by hitting it.",
			"[sad] That bay your ship is sitting in was my dad's. He was shipwright here. Built half of what still works.",
			"One day I'm going to get the whole docking suite running again. Your wreck is good practice.",
		],
		"repeat": [
			"[angry] Heating pump four is dead again. Pump four is always dead. I think it likes the attention.",
			"[sad] Dad used to say a ship tells you what's wrong, if you shut up and listen.",
			"If Tikka says a part can't be saved, bring it to me anyway.",
		],
	},
	"Job": {
		"id": "job",
		"pitch": 0.6,
		"first": [
			"[happy] Well now. You the one fell out the sky? Name's Job. Mind your head, cher, ceilin's low.",
			"I dig what the station needs for fixin'. Don't get much done. One drill, and she's older than me.",
			"You need somethin' heavy moved, you come find me.",
		],
		"repeat": [
			"[sad] My people come from Louisiana. Never seen it. Mama kept the talk goin' so we wouldn't lose that too.",
			"Zaas keeps askin' me to dig him a tunnel to the sea. Ain't no sea. I dug him a little one anyhow.",
			"[sad] You eatin' enough? You look like you ain't eatin' enough.",
		],
	},
	"Zaas": {
		"id": "zaas",
		"pitch": 1.5,
		"first": [
			"[happy] Ahoy! Zaas, water reclamation officer, and captain of this expedition.",
			"[love] Below us lies an ocean. Vast. Uncharted. I have no proof yet, which is how you know it is a real discovery.",
			"If you see ice, any ice, report it to me. That is technically my entire job.",
		],
		"repeat": [
			"[angry] The others say there is no sea on a moon like this. The others said that about every sea, once.",
			"I have named the ocean already. I will not tell you the name until we find it.",
			"Job says he will dig toward it when he has a second drill. I am building him one out of hope.",
		],
	},
	"Vzz'ket": {
		"id": "vzzket",
		"pitch": 0.7,
		"first": [
			"[angry] Halt. ... You are the pilot. Sara said you would wander. I am Vzz'ket. I guard this gate.",
			"Things come up from the caverns. Small. Many legs. I kill them before they reach the dormitories.",
			"[surprised] They are not hunting. They are running. Ask yourself from what.",
		],
		"repeat": [
			"No one passes the barricade. When you are ready, I will tell you. You are not ready.",
			"[sad] Three this week. Last month it was three in the whole month.",
			"Sleep well. That is what I am for.",
		],
	},
}

# Things you can look at. Name must match the name in tools/build.py THINGS.
const LOOKS = {
	"Shuttered workshop": ["Sealed since before the refugees came. Something inside is still ticking."],
	"Telescope": ["The gas giant fills the eyepiece, blue and enormous.", "Somewhere past it, the signal is still coming."],
	"Sealed lab": ["TERRAN SIGNALS DIRECTORATE. AUTHORISED STAFF ONLY.", "The lock is still lit."],
	"Power core": ["The station's heart. It runs at a fraction of what it was built for, and it sounds tired."],
	"Barricade": ["Planks, hull plate and a lot of bolts. Past it the tunnel drops into the dark.", "Something down there is scratching."],
	"Villa door": ["Locked. Whoever built a private villa out here did not leave a forwarding address."],
	"Herb beds": ["Evarra's herbs, in the one corner of the dome that still holds air and water. It smells green here."],
	"Fountain": ["The officers' fountain. Zaas runs the station's reclaimed water through it now, and someone has planted the centrepiece.", "It is the closest thing the Landing has to a town square."],
	"Notice board": ["WANTED: coil wire, any length. - Tikka", "LOST: one left boot, sentimental value. FOUND: one ocean (pending). - Z."],
	"Market stall": ["A stall under a striped awning. Nobody is selling today, but the crates are full."],
	"Star dome": ["An old telescope under clear glass. The gas giant takes up half the sky."],
	"Locked apartment": ["Private quarters, shuttered. Guests could stay here one day, if anyone could find the keys."],
	"Hotel desk": ["The duty officer's desk. Dust it off, add a bell, and it is a front desk."],
	"Abandoned shop": ["A shop front, shuttered. The sign has been painted over twice in two different alphabets."],
	"Broken agri dome": ["Cracked panels, dry soil, dead machines. It was built to feed a garrison.", "With glass and water this could feed the whole Landing."],
	"Old bunks": ["Rows of bunks for soldiers who never came. Clear out the rubble and these would be guest rooms."],
	"Library shelves": ["Field manuals, mostly. Someone has added cookbooks, a few novels and a children's atlas of Earth."],
	"Landing pad": ["Painted lines for a spaceport that was never finished. One ship could set down here. Barely."],
}
