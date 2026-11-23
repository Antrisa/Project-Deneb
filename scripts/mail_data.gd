extends RefCounted
# Letters that come to your mailbox (Zachary, 23 Nov: "a message system like in stardew you can get mail from the
# NPCs"). The post comes every morning (scripts/main.gd _deliver_mail). A letter waits in your mailbox, the message
# pad on the agri complex's front porch, until you read it (an envelope bobs over the pad), and
# you can read it again any time after: the pad keeps them all (scripts/mail_reader.gd).
#
# LETTERS: id -> {"from": who sent it, "title": what the list of letters shows, "body": [paragraphs],
#                 "sign": the sign-off}. Keep a letter to about four short paragraphs, so it fits on the page.
# DATED: letters that come on a fixed day (day 1 is the first morning of the game).
# Everything else is sent by the story, with main.gd send_mail(id, days): it comes with the post that many
# mornings later. "vzzket_caverns" is sent when you finish Job's north tunnels (job_quest 5).
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
}

const DATED := {"welcome": 1}
