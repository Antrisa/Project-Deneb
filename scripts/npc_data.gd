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
			"Bram asked me who the new one was. I said {they're} quiet, and {they} eat{s} what {they're} given. High praise, from me.",
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
			"Told Freya about you. Said {they} work{s} hard and {they} don't complain. She said give {them} a week.",
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
	"Maren": {
		"id": "maren",
		"pitch": 1.0,
		"first": [
			"So you're the one Sara had in quarantine. Sit. No? Fine, stand, but hold still. I'm Maren. I'm the doctor, which here means all of them.",
			"If the tunnels get the better of you, this is where you'll wake up. I'd rather you bought a medpack and didn't.",
			"[happy] My husband Owen keeps the library, and our grandson Pip keeps everyone else busy. You'll meet them. You won't have a choice.",
		],
		"repeat": [
			"Thirty years a ship's surgeon. I came here to retire. [angry] I have never been so busy.",
			"Quill is the best assistant I've had. He alphabetised the bandages. I didn't know bandages had an alphabet.",
			"[sad] Half this equipment is older than I am, and I am not telling you how old that is.",
			"[happy] Pip wants to be a miner this week. Last week it was pirate hunter. I prefer the miner.",
		],
	},
	"Quill": {
		"id": "quill",
		"pitch": 1.4,
		"first": [
			"[surprised] Oh. A patient? No. A visitor. Please stand on the mat. The mat is clean. I am Quill. I assist Doctor Maren.",
			"I am Vuultam. Yes, the glasses are necessary. No, I will not take them off so you can see.",
		],
		"repeat": [
			"I have catalogued every ache on this station. Job has eleven. He admits to none.",
			"[happy] Doctor Maren let me do the stitches yesterday. They were very even stitches.",
			"In the evenings I read in the library. Owen saves the medical journals for me. Some are only two hundred years out of date.",
			"[angry] Somebody has been taking the tongue depressors. I suspect a child. I suspect a specific child.",
		],
	},
	"Owen": {
		"id": "owen",
		"pitch": 0.85,
		"first": [
			"Mind the stack. And that one. Welcome to the library, such as it is. I'm Owen. I married the doctor and inherited the books.",
			"I teach our grandson Pip his letters in the mornings, and anyone else who wanders in. You look like you can read. That puts you ahead of the garrison who left these.",
		],
		"repeat": [
			"The Terrans left four hundred technical manuals and one novel. I have read the novel nine times. It is not good.",
			"[happy] Maren says I should charge for the books. I say nobody would pay, and then where would we be? Exactly here.",
			"If you find anything with pages out there, bring it to me. Old codexes especially. Every one fills in a little more of how we all got here.",
			"[love] Thirty years following a ship's surgeon from port to port. This is the first place the shelves have stayed put.",
		],
	},
	"Pip": {
		"id": "pip",
		"pitch": 1.9,
		"first": [
			"[surprised] You're the one who crashed! Did it hurt? Was there fire? Gran says I can't ask if there was fire.",
			"I'm Pip. I'm nine. I know where everything is. Ask me where something is.",
		],
		"repeat": [
			"[happy] Zaas says there's a sea under the station. Grandad says there isn't. I'm going with Zaas.",
			"I'm not allowed in the mine. I'm not allowed in the tunnels. I'm not allowed on the lift by myself. [angry] It's a very small station if you're me.",
			"Quill counts the tongue depressors. [happy] He's missing six. I don't know anything about that.",
			"When I grow up I'm going to have a ship like yours. Except mine will work.",
		],
	},
	"Sesska": {
		"id": "sesska",
		"pitch": 1.35,
		"first": [
			"Come in, come in, mind the warp threads. I am Sesska. I weave. Tikka is my wife, so if your ship is late, I already know why.",
			"That jacket of yours has been through a crash. I can see every seam giving up. One day soon I will have cloth to spare, and we will talk.",
		],
		"repeat": [
			"[happy] Eight hands and Tikka uses hers on engines. I use mine on a loom. Between us the station is held together twice over.",
			"I spin what Evarra grows and what the mine bugs leave behind. Bug silk is ugly. It is also the warmest thing on this moon.",
			"[love] Forty years married. She still brings me coil wire like other people bring flowers. I have made it into a very strange scarf.",
			"[sad] I had a shop on Arach Minor with a window onto the street. Here I have a window onto a corridor. I am told it is the nicer corridor.",
		],
	},
	"Rusk": {
		"id": "rusk",
		"pitch": 0.65,
		"first": [
			"Mind the third stool, it bites. I'm Rusk. This is my bar. Yes, all of it. No, the ceiling is meant to do that.",
			"I pour what the station can spare and a few things it can't. Come by of an evening. Half the Landing does.",
		],
		"repeat": [
			"Forty years behind bars. The good kind. [happy] Mostly the good kind.",
			"[sad] One day I'll have a proper counter, lights that stay on, and a sign. Sara says there are other priorities. Sara doesn't drink.",
			"People tell a barman things. I couldn't possibly repeat them. [happy] Not for free.",
			"Bram, Freya and Job are in most nights. Job has never once paid for the stool he broke.",
		],
	},
	"Ooma": {
		"id": "ooma",
		"pitch": 0.9,
		"first": [
			"Ahh. A new face on the little moon. I am Ooma. I sell what cannot be found, and a few things that should not be, to people who did not know they were looking.",
			"I am here when I am here. Twice in a week, perhaps. The tides decide. [happy] There are always tides, if you know where to feel for them.",
		],
		"repeat": [
			"This? From a market on a world with three suns and no word for 'refund'.",
			"[surprised] You have the look of someone who has been somewhere they should not. Good. Those are my best customers.",
			"I do not haggle. I simply wait until you agree.",
			"[love] One day I will bring a chair so fine that Tobbin will weep. I am saving it. Timing is everything.",
		],
	},
	"Tobbin": {
		"id": "tobbin",
		"pitch": 1.45,
		"first": [
			"Don't sit on that! It's not finished. Nothing's finished. I'm Tobbin. I make furniture, out of whatever this station will give me.",
			"Plastic and steel, plastic and steel. [sad] Do you know what I would give for one plank of real wood? I'd give the plastic. And the steel.",
		],
		"repeat": [
			"[happy] A chair is a promise that someone is staying. This station needs more chairs.",
			"My Merrow keeps the water running and the green things green. Zaas has the title. She has the wrench.",
			"Nub has started drawing on my blueprints. [happy] The additions are not structural, but I've kept them.",
			"[love] If that dome ever grows a tree, I will ask it very politely for a branch.",
		],
	},
	"Merrow": {
		"id": "merrow",
		"pitch": 1.5,
		"first": [
			"Careful, that valve's live. I'm Merrow. Hydroponics officer. If it's wet or green on this station, it's mine to worry about.",
			"Zaas is my chief. He's a fine chief. [angry] He's also been looking for an ocean for three weeks, so the fountain is me.",
		],
		"repeat": [
			"Every drop on the Landing has been through that fountain a hundred times. Don't think about it too hard.",
			"[happy] Evarra's herbs are coming in. One corner of one dome. Give me glass and pumps and I'll give you a garden.",
			"Tobbin wants a tree. I want a tree. [sad] The dome wants forty new panels first.",
			"Nub fell in the fountain again. [happy] At least one of us got an ocean.",
		],
	},
	"Nub": {
		"id": "nub",
		"pitch": 2.0,
		"first": [
			"[surprised] You're tall. Are you the crashed one? Pip said you were on fire. Were you on fire?",
			"I'm Nub. My dad makes chairs and my mum makes water. I make drawings.",
		],
		"repeat": [
			"[happy] Kit can jump off the fountain edge. I can nearly jump off the fountain edge.",
			"I drew you. You're the tall one with the sad ship.",
			"Dad says don't touch the saw. [angry] I only looked at the saw.",
		],
	},
	"Garrick": {
		"id": "garrick",
		"pitch": 0.75,
		"first": [
			"So you're Sara's guest. Garrick. Security chief, quartermaster, and the man who signs for anything sharp on this station.",
			"I've read what's left of your ship's log. Pirate hunter. [angry] Keep it outside the airlock and we'll get along.",
		],
		"repeat": [
			"Sara wants fewer weapons on the Landing. The tunnels want more. I split the difference and write it all down.",
			"[happy] My wife Saffi runs our home and our boy Kit runs everywhere else. I just run security.",
			"Ix'ali is the best armourer I've had. She's also the only one. [surprised] Don't tell her either of those.",
			"Rusk's is the only place I take the badge off. Don't make me put it back on in there.",
		],
	},
	"Saffi": {
		"id": "saffi",
		"pitch": 1.3,
		"first": [
			"Oh, you're the one! Garrick's been grumbling about you for days, which means he likes you. I'm Saffi.",
			"If you see a small fox going somewhere fast, that's Kit, and wherever he's going, he's not allowed.",
		],
		"repeat": [
			"[happy] Rusk is my uncle. Don't believe a word he says about me as a kit.",
			"I keep the house, the boy and the chief of security in order. [angry] Only one of them listens.",
			"The market is quiet most days. But when Ooma's stall is up, I always find something I didn't need.",
			"[love] Garrick came here to guard a station. He stayed because it turned into a town.",
		],
	},
	"Kit": {
		"id": "kit",
		"pitch": 1.95,
		"first": [
			"[surprised] You've got a real ship! Dad says it's a wreck. A real wreck!",
			"I'm Kit. I'm the fastest on the station. Pip says he is. Pip is wrong.",
		],
		"repeat": [
			"[happy] I'm going to be security chief. Or a pirate. Dad says I can't be both.",
			"Ix'ali let me hold a helmet. [happy] It went all the way down to my shoulders.",
			"Nub can't jump the fountain edge yet. I'm teaching. I'm a good teacher.",
		],
	},
	"Ix'ali": {
		"id": "ixali",
		"pitch": 1.6,
		"first": [
			"[surprised] A Terran! With Terran weapons? No? None? Not even a small one? ...I am Ix'ali. I am the armourer.",
			"Technically I assist the quartermaster. Practically, he signs the forms and I get to touch everything. It is the best job on the moon.",
		],
		"repeat": [
			"[love] Your people put a tiny explosion inside a tube and called it a sidearm. I think about this every day.",
			"Sara says there are enough weapons on the Landing. Sara has not seen what comes up out of the tunnels. Or she has, and she is being polite.",
			"In the evenings I spar with Vzz'ket by the cavern gate. [happy] He has only knocked me down nine times this week.",
			"[angry] Do not call it 'just a spear'. It has a balance point. It has a history. It has a name, which I will not tell you.",
		],
	},
}

# Things you can look at. Name must match the name in tools/build.py THINGS.
const LOOKS = {
	# Survey Level (tools/survey.py)
	"Empty display": ["An empty case with a blank label. Tar'Besh has left a card in it: 'Waiting for something wonderful.'", "Things you find on the station and in the mine could go here."],
	"Audio guide": ["A little guide terminal. Press it and Tar'Besh's recorded voice begins, very slowly, at the beginning of time."],
	"Museum catalogue": ["Tar'Besh's catalogue: every piece numbered, described and cross-referenced in three languages."],
	"Sanctum banner": ["A violet banner sewn with the Precursor diamond. The thread shines faintly in the dark."],
	"Empty crystal cradle": ["An empty cradle on a pedestal, shaped to hold a crystal. There are more of them than crystals.", "Tar'Besh believes the rest are out there somewhere."],
	"Precursor mural": ["A carved mural: a great wing spread over a world, and figures bringing crystals up from under the ground."],
	"Crystal test rig": ["An arm of probes pointed at an empty sample cradle. The readings on its screen make no sense at all."],
	"Resonance spectrometer": ["It measures the crystals' hum. The line on the screen rises and falls, slow as breathing."],
	"Research console": ["Years of measurements. One note, in S.A.R.A.'s neat type: 'They are not decaying. They are waiting.'"],
	"Measurement log": ["A log of every test run on the crystals, every one signed by Tar'Besh and countersigned by S.A.R.A."],
	"Lounge bookshelf": ["Star atlases, travel guides and a well-thumbed copy of a Paris hotel brochure."],
	"Lounge table": ["A little table with two cups and a pot of tea, still warm."],
	"Fossil of a cave crawler": ["A fossil from the moon's own caverns: something with too many legs, a very long time ago."],
	"Zaa'sh prayer bell": ["A Zaa'sh temple bell, cast in the shape of a Sky-Weaver's wing.", "Tar'Besh rings it once a year."],
	"Precursor glass shard": ["A splinter of something that grew rather than being made.", "It is warm to the touch, through the glass."],
	"Hull plate from the first crash": ["Scorched plating from the refugee transport that crash-landed here.", "Every settler signed the back of it."],
	"Terran signal codebook": ["A listening-post codebook, every page stamped TOP SECRET.", "S.A.R.A. says most of it was guesswork."],
	"Moogli trade weights": ["Brass weights from three different Moogli trading houses. None of them agree."],
	"Star map on bone": ["An ancient star chart scratched on bone. One of the stars on it no longer exists."],
	"Pirate cutlass": ["Taken from a Chernobog raider.", "The label adds, firmly: not for sale."],
	"Hologram dais": ["S.A.R.A.'s projector. The light rings turn slowly even when she is somewhere else on the station.", "Everything in this room is part of her."],
	"Station map screen": ["The whole Landing, drawn in teal light. Little dots move along the corridors: everyone, wherever they are."],
	"Concierge desk": ["A polished desk with a brass bell and a vase of real flowers.", "There is no hotel up here. There is a concierge desk anyway."],
	"Pictures of Paris": ["Two framed pictures: a lattice tower at sunset, and a cafe with a striped awning.", "A note underneath, in neat print: ONE DAY."],
	"Signal tape archive": ["Reels from the listening-post years, every one labelled and dated.", "Most of them are static. Some of them are not."],
	"Deep-space sensor read-outs": ["Dials and read-outs from the long-range sensors. One needle keeps twitching toward the same patch of sky."],
	"Memory core": ["A tall rack of humming memory. Its lights blink in a pattern, almost like breathing."],
	"Operator console": ["An operator console facing the dais. The seat is worn: people come here to talk to her."],
	"Star chart": ["A chart of the nearby stars with trade lanes drawn in. Somebody has circled a blank patch and written 'why?'"],
	"The Weaver's Wing": ["A slab of carved stone, older than the Zaa'sh calendar. It shows a great wing spreading over a burning world.", "Tar'Besh says the Zaa'sh call them the Sky-Weavers."],
	"Tar'Besh's desk": ["Catalogue cards, a magnifying glass and three cups of cold tea."],
	"Sanctum door": ["A heavy door set with violet glass. It is locked, and something behind it hums.", "Tar'Besh keeps the key."],
	"Precursor crystal": ["A crystal the size of a forearm, glowing faintly violet. It feels like it is waiting."],
	"Tar'Besh's books": ["Histories, prayer books and a well-thumbed Terran novel about knights."],
	"Panoramic window": ["The gas giant hangs over the horizon, banded blue and white, so close it fills half the window."],
	"Shuttered workshop": ["Sealed since before the refugees came. Something inside is still ticking."],
	"Telescope": ["The gas giant fills the eyepiece, blue and enormous.", "Somewhere past it, the signal is still coming."],
	"Sealed lab": ["TERRAN SIGNALS DIRECTORATE. AUTHORISED STAFF ONLY.", "The lock is still lit."],
	"Power core": ["The station's heart. It runs at a fraction of what it was built for, and it sounds tired."],
	"The Harbinger": ["Something vast rises out of the black water, older than the station and maybe older than the moon.", "It has not noticed you. Yet."],
	"Underground ocean": ["Warm, dark water as far as the lamp reaches. Zaas would weep.", "Somewhere out there, the Harbinger is waiting."],
	"Barricade": ["Planks, hull plate and a lot of bolts. Past it the tunnel drops into the dark.", "Something down there is scratching."],
	"Villa door": ["Locked. Whoever built a private villa out here did not leave a forwarding address."],
	"Herb beds": ["Evarra's herbs, under the one small dome on the Landing that holds air, water and light. It smells green here."],
	"Fountain": ["The officers' fountain. Zaas runs the station's reclaimed water through it now, and someone has planted the centrepiece.", "It is the closest thing the Landing has to a town square."],
	"Notice board": ["WANTED: coil wire, any length. - Tikka", "LOST: one left boot, sentimental value. FOUND: one ocean (pending). - Z."],
	"Market stall": ["A stall under a striped awning. Nobody is selling today, but the crates are full."],
	"Star dome": ["An old telescope under clear glass. The gas giant takes up half the sky."],
	"Locked apartment": ["Private quarters, shuttered. Guests could stay here one day, if anyone could find the keys."],
	"Hotel desk": ["The duty officer's desk. Dust it off, add a bell, and it is a front desk."],
	"Abandoned shop": ["A shop front, shuttered. The sign has been painted over twice in two different alphabets."],
	"Half-built chair": ["Steel legs, a plastic seat, and a pencil note: 'IMAGINE THIS IN OAK.'"],
	"Weapon racks": ["Spears, blades, two dented helmets and a clipboard. Everything has a tag. Everything is signed for."],
	"Bar shelves": ["Bottles in six alphabets. Half are empty and kept for the look of the thing."],
	"Airlock": ["The outer door is sealed and the light above it is red.", "Sara: The pad is in hard vacuum. When you have a suit that holds air, I will open it. Not before."],
	"Customs gate": ["A customs gate for a port that has never had a visitor. The stamp pad is still wet. Sara keeps it that way."],
	"Old drill hall": ["A parade floor the garrison never marched on. It is the biggest empty room on the Landing.", "A hotel could use a room like this."],
	"Dry ponds": ["Cracked basins under broken glass. Somebody built fish ponds here, and a path to walk around them.", "With water and a roof it would be the prettiest place on the moon."],
	"Workbench": ["A workbench, a vice, and a wall of empty hooks. Sara says the room is yours if you can find a use for it."],
	"Air reclaimer": ["Rows of scrubbers, breathing for the whole station. Half of them rattle.", "Merrow has chalked a number on each one. The low numbers are the ones she trusts."],
	"East airlock": ["A maintenance airlock. The outer door is sealed and the light above it is red.", "Past it is bare rock. You would need a suit."],
	"Medbay beds": ["Three beds, clean sheets, and a chart on each. Two of the charts say JOB."],
	"Loom": ["Sesska's loom. It has more moving parts than your ship, and all of them work."],
	"Broken agri dome": ["Cracked panels, dry soil, dead machines. It was built to feed a garrison.", "With glass and water this could feed the whole Landing."],
	"Old bunks": ["Rows of bunks for soldiers who never came. Clear out the rubble and these would be guest rooms."],
	"Library shelves": ["Field manuals, mostly. Someone has added cookbooks, a few novels and a children's atlas of Earth."],
	"Landing pad": ["Through the airlock window: painted lines on bare rock, for a spaceport that was never finished.", "One day ships will set down there."],
}
