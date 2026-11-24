extends RefCounted
# Letters that come to your mailbox (Zachary, 23 Nov: "a message system like in stardew you can get mail from the
# NPCs"). The post comes every morning (scripts/main.gd _deliver_mail). A letter waits in your mailbox, the message
# pad on the agri complex's front porch, until you read it (an envelope bobs over the pad), and
# you can read it again any time after: the pad keeps them all (scripts/mail_reader.gd).
#
# LETTERS: id -> {"from": who sent it, "title": what the list of letters shows, "body": [paragraphs],
#                 "sign": the sign-off, "gift": {item: count} (optional)}. Keep a letter to about four short
#                 paragraphs, so it fits on the page, and a little shorter with a gift (the gift takes the foot of
#                 the page). tests/check_mail.py measures every letter against the smallest page.
#   A gift goes in your pack the first time you open its letter (main.gd read_letter), as Stardew's do.
#   Plain ASCII only: the datapad font has no curly quotes, long dashes or accents (Cafe, not Café).
# DATED: letters that come on a fixed day (day 1 is the first morning of the game).
# Everything else is sent by the story, with main.gd send_mail(id, days): it comes with the post that many
# mornings later. "vzzket_caverns" is sent when you finish Job's north tunnels (job_quest 5); "sara_ponds" when the
# Leviathan is slain (the fish ponds can be repaired then: scripts/station_repair.gd).
#
# Heart events send letters with a ["mail", id, days] step (scripts/heart_events.gd; 23 Nov, Zachary: "if it makes
# sense in any of the previous arcs add and next morning get mail from the person or gifts. and keep in mind for
# future arcs"). Most come the next morning: a thank-you, a recipe, a few seeds. The ones below are grouped by
# the event that sends them; a letter sent from inside a choice only comes if you made that choice.
#
# The wording of these letters is a first draft by Claude, for Zachary to change.

const LETTERS := {
	"welcome": {
		"from": "S.A.R.A.",
		"title": "Welcome home",
		"body": [
			"Good morning, and welcome to Echo Landing.",
			"The apartment on the right of this porch is yours for as long as you stay. It belonged to the agri keeper, before the dome broke, and nobody has lived in it since. I aired it out. Twice.",
			"This pad is your mailbox. The post comes every morning; until the station has a courier again, my maintenance drones carry it. They are punctual, and they do not read your letters. I have asked.",
			"The crate across the porch is Bram's. Put in anything he buys and he collects it overnight, and pays in the morning. The workbench in your workshop, along the west link, is yours too.",
		],
		"sign": "S.A.R.A.",
	},
	"vzzket_caverns": {
		"from": "Vzz'ket",
		"title": "The gate",
		"body": [
			"Pilot.",
			"Job says the north tunnels are quiet. I went up and listened. He is right.",
			"Come to the cavern gate, at the bottom of the mine. I will tell you what is under it. Then I will open it.",
			"Come rested. Bring food.",
		],
		"sign": "Vzz'ket",
	},
	"sara_storage": {
		"from": "S.A.R.A.",
		"title": "The storage dome",
		"body": [
			"A small matter of housekeeping.",
			"Between your field and your workshop is the agri dome's old storage dome. A pressure seal failed there years ago, and I closed the doors on it. It has been full of broken glass ever since.",
			"My drones can repair it, for Scrip and a few materials. Ask at either of its doors and I will show you what it needs.",
			"You will want somewhere to keep things. Everyone does, eventually.",
		],
		"sign": "S.A.R.A.",
	},
	"sara_ponds": {
		"from": "S.A.R.A.",
		"title": "The springs are quiet",
		"body": [
			"Since the Leviathan went down, the pressure in the spring pipes has held. Nothing is cracking them any more.",
			"That means I can repair the hot springs and the fish ponds, east of your porch. They have been sealed since long before you came.",
			"Ask at either of their doors and I will tell you what it costs.",
			"I would very much like a warm bath on this station again. Not for me. I have no use for one. For the station.",
		],
		"sign": "S.A.R.A.",
	},
	# ---- from heart events (the next morning)
	# Freya 2, The Stubborn Heating Pump
	"freya_pump": {
		"from": "Freya",
		"title": "Two-person job",
		"body": [
			"Boss!",
			"Sector Three's been warm all night. Garrick took his coat off on watch. First time all season, he says.",
			"Found these in Dad's offcut bin. He always said good copper's wasted sitting in a bin, so they're yours. Make something that turns.",
		],
		"sign": "Freya",
		"gift": {"copper_bar": 2},
	},
	# Freya 6, Test Flight: Tikka was in the launch booth for Jorvik's last run, and for this one
	"tikka_test_flight": {
		"from": "Tikka",
		"title": "A better memory",
		"body": [
			"{name},",
			"Since Jorvik's last run, every launch I've called has sounded like that one to me. Right up until the shaking.",
			"Last night one went right. A clean note, all the way out past the doors. I'm keeping that one instead.",
			"Thank you for easing off. And for taking her with you. Bring her back in one piece. The ship too, if you can manage both.",
		],
		"sign": "Tikka, launch control",
	},
	# Jasper 2, The Butter Tin
	"jasper_wheat": {
		"from": "Jasper",
		"title": "For the croissants",
		"body": [
			"Mon ami,",
			"Madame Ooma has my Scrip and my button, and I have one season. But a croissant is only as good as its flour, and the flour on the supply run tastes of the crate it came in.",
			"So, enclosed: moon wheat, from Evarra's seed drawer. She says it wants water and patience. I have neither. You have a field.",
		],
		"sign": "Jasper",
		"gift": {"moon_wheat_seeds": 5},
	},
	# Evarra 2, The Window-Box Herb
	"evarra_lavender": {
		"from": "Evarra",
		"title": "Something that grows",
		"body": [
			"Dear neighbour,",
			"The seed bank won't part with lavender. I asked nicely, then S.A.R.A. asked even more nicely, and it still said no.",
			"So here are star tomatoes. They aren't flowers, but they're stubborn and they love a grow-lamp. A farm has to start with something that wants to grow.",
		],
		"sign": "Evarra",
		"gift": {"star_tomato_seeds": 3},
	},
	# Job 2, Gumbo in the Breakroom
	"job_gumbo": {
		"from": "Job",
		"title": "Mama's gumbo",
		"body": [
			"Cher,",
			"Wrote it down for you, near as I can. First, the roux: flour and oil, low heat, and stir till it's the colour of an old penny. Don't walk away. Don't you dare walk away.",
			"Then the holy trinity: onion, pepper, celery, whatever the hydroponics will spare. Then the spice. The spice I can't write down. It's in a tin, and the tin's mine.",
			"Bring a bowl to the breakroom any day after four. There's always a pot.",
		],
		"sign": "Job",
	},
	# Job 4, Cave-In on Shaft Four: only if you dug out Zaas's crate
	"zaas_hydrophones": {
		"from": "Zaas",
		"title": "Still listening",
		"body": [
			"To the one who dug,",
			"My hydrophones survived. Two dents and a great deal of shale, which I have been picking out with tweezers all night. Merrow says I am being sentimental. I am.",
			"I put them back on the rock to be sure they work. They do. And far down under the rock, there is still that sound. Water, moving.",
			"I will tell you about it one day, when I am sure.",
		],
		"sign": "Zaas",
	},
	# Quill 2, The Spilled Apothecary
	"quill_spores": {
		"from": "Quill",
		"title": "Do not tell Maren",
		"body": [
			"Dear friend,",
			"Thank you for not stepping in the spores. Only three vials were lost, which by my standards is a triumph.",
			"Enclosed: two medpacks, made by my own hands, which were steady the entire time. Please take them into the mine. Please do not need them.",
			"P.S. Maren found a glowing spot under the bench. I said it was a reflection.",
		],
		"sign": "Quill",
		"gift": {"medpack": 2},
	},
	# Ix'ali 6, Sparring at the Cavern Gate
	"ixali_bout": {
		"from": "Ix'ali",
		"title": "The book of bouts",
		"body": [
			"Honoured friend,",
			"The armoury keeps a book of every bout fought at the cavern gate since the gate was built. Last night I wrote ours in it.",
			"Yours is the first Terran name in the book. Garrick says my handwriting is too large. I say a first deserves large handwriting.",
			"Come to the armoury when you are ready. I have taken your measure, and the Aegis plate will not fold itself.",
		],
		"sign": "Ix'ali",
	},
	# Artie 4, The Junior Scouts: from Pip, Kit and Nub
	"scouts_knots": {
		"from": "The Junior Scouts",
		"title": "From the Junior Scouts",
		"body": [
			"We practised the square knot 100 times. Kit says 200. Kit is wrong. - Pip",
			"Mine is better than Pip's now. We found a shiny rock by the fountain and voted you get it. - Kit",
			"NUB TIED THE ENVELOPE. NUB'S IS A REAL KNOT. - Nub",
		],
		"sign": "The Junior Scouts",
		"gift": {"quartz": 1},
	},
	# Stu 6, A Name on the Door
	"stu_address": {
		"from": "Stu",
		"title": "My own address",
		"body": [
			"Hi!",
			"This is the first letter I've ever sent. I didn't know who to send it to, and then I did.",
			"It's from East Home 2. That's me. I'm writing it at my own table, and I've been grinning at the return address for ten minutes.",
			"The U is still on. Tobbin came back after dark to check it anyway.",
		],
		"sign": "Stu",
	},
	# Ana 2, A Seat at the Table
	"ana_seat": {
		"from": "Ana",
		"title": "The seat",
		"body": [
			"I don't write letters. Ivan read everything that came aboard, so nobody did.",
			"But you sat down. In front of everyone. You knew what it would cost you, and you did it anyway.",
			"On the way out, two more people nodded at me. I counted.",
			"That's all. Thank you.",
		],
		"sign": "Ana",
	},
	# S.A.R.A. 6, Walkabout
	"sara_walk": {
		"from": "S.A.R.A.",
		"title": "Something to hold",
		"body": [
			"Good morning.",
			"I had my drones bring this, instead of saying it from a pad. A letter is something you can hold, and I wanted you to have something to hold.",
			"Last night I looked at the fountain from my usual camera. It is the same fountain. It looks different now that I have stood beside it.",
			"I am keeping a list of places to go. It is short. I am in no hurry.",
		],
		"sign": "S.A.R.A.",
	},
	# Tar'Besh 4, Next Assignment: only if you told him they meant him to die and he lived anyway
	"tarbesh_letter": {
		"from": "Tar'Besh",
		"title": "A better letter",
		"body": [
			"Friend,",
			"The last letter I was sent told me where to go, and how long the rations would last. I keep it among the candles, so I will not forget it.",
			"It seemed to me tonight that a man should own at least one better letter. So I am writing one, to someone who listened.",
			"Out of spite, then out of habit. I have decided that is a respectable reason to be alive.",
		],
		"sign": "Tar'Besh, well fed",
	},
	# Zaas 6, First Splash: Merrow, about the sea he named after her
	"merrow_plaque": {
		"from": "Merrow",
		"title": "About the plaque",
		"body": [
			"Tar'Besh put the plaque up on the shore last night. THE MERROW DEEP, in letters you can read from across the water. I asked him to take it down. He said a plaque is a prayer that stays put.",
			"The chief was in the water until dark. I keep every drop on this station clean, and he floated on his back in it, singing.",
			"Thank you for being there when he went in. Somebody had to see it who wasn't me. Don't tell him I wrote.",
		],
		"sign": "Merrow",
	},
	# Vzz'ket 8, The Watch Changes: his first night's sleep
	"vzzket_sleep": {
		"from": "Vzz'ket",
		"title": "The box chirped",
		"body": [
			"Pilot.",
			"The machine's box chirped in the night. A rock-crawler, on the third landing. She told me what and where. I went down. It was.",
			"I went back to my bedroll. It chirped once more before morning. I did not get up. S.A.R.A. says that is the point.",
			"I slept until Tikka's drill woke me. Tell no one.",
		],
		"sign": "Vzz'ket",
	},
	# Rusk 8, The First Page: how Ilsa grew her vine (scripts/main.gd CROPS nebula_grape, _rusk_cask_fill)
	"rusk_ilsa_vine": {
		"from": "Rusk",
		"title": "How Ilsa grew them",
		"body": [
			"{name},",
			"Ilsa wrote this on the back of a menu. I'll keep the menu.",
			"Dig a bed or set down a hydroponic one, and keep it watered. Eight days to the first bunch, then a bunch every three days while you tend it. Plant a bunch and it grows you another vine.",
			"Bring me five and I'll fill the cask. Three days, and you've a bottle of Nebula wine. Ship it: Bram's cousins pay what it's worth, and it's worth a lot.",
		],
		"sign": "Rusk",
	},
	# Bram 4, Quiet Credit
	"bram_seeds": {
		"from": "Bram",
		"title": "You heard nothing",
		"body": [
			"Friend.",
			"About this morning. You heard nothing. I said nothing. The freighter flew, and that is the end of the matter.",
			"Enclosed: crater potato seeds. They were going stale. This is not generosity. This is stock control.",
			"Do not tell anyone about the seeds either.",
		],
		"sign": "Bram Ollo",
		"gift": {"crater_potato_seeds": 5},
	},
	# Maren's 4, her hot cup of tea (not if you told her it was only tea)
	"maren_tea": {
		"from": "Maren",
		"title": "Hot tea",
		"body": [
			"{name},",
			"Thirty-one minutes of quiet. I timed it. The tea was hot the whole way down.",
			"Pip says you turned him round 'like a door'. He wants to know how you did it. I've told him it's a doctor's secret.",
		],
		"sign": "Maren",
	},
	# Owen's 4, the morning after the Kestrel's recorder
	"owen_recorder": {
		"from": "Owen",
		"title": "Good company",
		"body": [
			"{name},",
			"I've put the recorder in the drawer with Tam's first school report and Ines's flight licence. It seemed like the right company.",
			"I listened once more, alone, for the green stars. Then I closed the drawer. That was enough for now.",
			"Thank you for staying.",
		],
		"sign": "Owen",
	},
	# Pip's 4, Lost and Found (not if you told him finders keepers)
	"pip_found": {
		"from": "Pip",
		"title": "Found it",
		"body": [
			"Dear {name},",
			"I found this by the bins. It's a geode. Job says you crack them. I didn't crack it. I thought you should.",
			"Finders keepers is a real rule. But Gran says giving things away is a better rule.",
		],
		"sign": "Pip (age 9)",
		"gift": {"geode": 1},
	},
	# the family's side arc 6, Lanterns
	"pip_lanterns": {
		"from": "Pip",
		"title": "Green stars",
		"body": [
			"Dear {name},",
			"Grandad played me the message. Dad sounds like Grandad but younger. Gran cried and then she laughed and then she made toast.",
			"I'm going to be a pilot and check the drive every time. You can come too. You can check it as well.",
		],
		"sign": "Pip",
	},
	# Tikka's 4, if you let Freya take Owen's lamp
	"freya_lamp": {
		"from": "Freya",
		"title": "She let me",
		"body": [
			"Boss!",
			"Owen's lamp still works. I checked it this morning. Don't tell Tikka I checked it. She'd be so proud, and then she'd check it too.",
			"She watched me do a whole repair and only said 'hm' once. Once! I'm painting it on the bay wall.",
			"Thanks for saying it. I couldn't have.",
		],
		"sign": "Freya",
	},
	# Sesska's 2, unless you told her it was only a jacket
	"sesska_offcuts": {
		"from": "Sesska",
		"title": "Offcuts",
		"body": [
			"Dear {name},",
			"There were offcuts from your jacket. There are always offcuts. Offcuts become caps.",
			"I guessed the size of your head. My guesses are good. If it doesn't fit, your head is wrong.",
		],
		"sign": "Sesska",
		"gift": {"knit_cap": 1},
	},
	# Tikka & Sesska's anniversary (the side arc's 6): both write, and Tikka's idea of thanks is coil wire
	"forty_years": {
		"from": "Tikka and Sesska",
		"title": "Forty years and a day",
		"body": [
			"{name},",
			"The music box played all night. Tikka checked it twice, then a third time, and then I hid it. - S.",
			"Enclosed, the highest honour I give: coil wire. Sesska says this is not how thanks work. Sesska is wrong. - T.",
		],
		"sign": "Tikka and Sesska",
		"gift": {"coil_wire": 2},
	},
	# Tobbin's 4, the morning after the garden dome's first limb
	"tobbin_planks": {
		"from": "Tobbin",
		"title": "Two planks",
		"body": [
			"{name},",
			"The limb is drying in my workshop, and the whole shop smells like a forest. Nub says it smells like 'outside'. He's never been outside.",
			"Two planks from the first cut. Not for selling: for making something badly, the way everyone starts. Mind the grain. It goes where it wants.",
		],
		"sign": "Tobbin",
		"gift": {"real_wood": 2},
	},
	# Merrow's 4, the morning after her star-tomatoes
	"merrow_seeds": {
		"from": "Merrow",
		"title": "For your beds",
		"body": [
			"{name},",
			"Seeds from the scrubber corner. They grew on a cup of water a day and a borrowed socket, so a proper bed will spoil them rotten.",
			"Put this letter in the recycler when you've read it. It all comes through my fountain in the end, so I'll know.",
		],
		"sign": "Merrow",
		"gift": {"star_tomato_seeds": 6},
	},
	# Nub's 6, the morning after Tar'Besh makes him Junior Curator
	"nub_curator": {
		"from": "Nub",
		"title": "JUNIOR CURATOR",
		"body": [
			"Dear {name},",
			"I am a JUNIOR CURATOR. Mr Tar'Besh gave me pins. Pins are better than tape but you can't put them in your mouth.",
			"This is a bug shell. It's for your museum. You haven't got a museum, so this is the first thing in it.",
		],
		"sign": "Nub (Junior Curator)",
		"gift": {"chitin": 1},
	},
	# Tobbin, Merrow & Nub's side arc 6, The First Tree
	"moogli_tree": {
		"from": "Merrow",
		"title": "Tree",
		"body": [
			"{name},",
			"Tree has a third leaf. Nub announced it at breakfast like a birth. Tobbin cried into his porridge, which he says was steam.",
			"Thank you for being there. A family's first tree needs witnesses.",
		],
		"sign": "Merrow, Tobbin and Nub (and Tree)",
	},
	# Garrick's 4, the morning after his rounds
	"garrick_issue": {
		"from": "Garrick",
		"title": "Quartermaster's issue",
		"body": [
			"{name},",
			"Signed out to you from stores: one medpack. You'll need it more than the shelf does.",
			"Same time tonight. Bring your own lamp.",
		],
		"sign": "G.",
		"gift": {"medpack": 1},
	},
	# Saffi's 6, the morning after the hull plate
	"saffi_soup": {
		"from": "Saffi",
		"title": "The helmet soup",
		"body": [
			"{name},",
			"One ginger root, two potatoes, a ration bar, and forty people. I've sent the potatoes. You bring the people.",
			"Sunday, at the fountain. I'm keeping you a seat by Rusk.",
		],
		"sign": "Saffi",
		"gift": {"crater_potato": 2},
	},
	# Kit's 4, the morning after the beacon
	"kit_coordinates": {
		"from": "Kit",
		"title": "THE BEACON",
		"body": [
			"Dear {name},",
			"Three long. Two short. Every night at 19:40. Mum helped me work out where: it's on the second ring, near the Reach.",
			"Take your ship. Bring me something back. Not treasure. Well. Treasure if there's treasure.",
		],
		"sign": "Kit (security chief, nearly)",
	},
	# Garrick, Saffi & Kit's side arc 6, Brave Together
	"guard_double": {
		"from": "Saffi",
		"title": "Double",
		"body": [
			"{name},",
			"Kit is grounded until he's forty. Garrick says thirty. We've settled on Tuesday.",
			"Thank you for coming. And thank Vzz'ket for us again, if he'll let you. He won't let us.",
		],
		"sign": "Saffi, Garrick and Kit",
	},
}

const DATED := {"welcome": 1, "sara_storage": 3}
