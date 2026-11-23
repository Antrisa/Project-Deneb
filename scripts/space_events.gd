extends RefCounted
# Space events (21 Nov 2026): what happens at beacons and distress signals. Written in the same shape as the
# event template Zachary writes in (claude/echo-landing-space-events-template.md), so his events go in as they are.
#
# An event: title, text, and 2-4 choices. A choice may need something ("needs") and has one or more outcomes,
# each with a chance (percent; leave it out for a single outcome) and effects written like the template:
#   "+40 Scrip", "-20 Scrip", "+2 fuel", "-1 fuel", "+3 hull", "-2 hull", "+1 missiles", "+2 drone parts",
#   "item: hull_plate x2", "relic: <name>", "fight: rabble_cutter", "reveal: <special sector>", "nothing"
# Needs: "drone", "40 Scrip", "item: medpack", "missiles", "drone parts" (more kinds come with crew and ship parts).
# "item: medpack x-1" takes one away (for a choice that needs it).
# main.gd applies the effects (apply_space_effects); scripts/ship_event.gd shows the window.

# kind: beacon | distress. zones: any, Terran, Zaa'sh, Collective, Reach. rings: [from, to].
# story: true for the first flight's set events, which never turn up at random.
const EVENTS := {
	"ice_field": {
		"kind": "beacon", "zones": ["any"], "rings": [1, 1], "story": true,
		"title": "Ice field",
		"text": "Wreckage, frozen into a drift of ice. Most of it is scrap, but one old cargo pod is still sealed, its markings worn off.",
		"choices": [
			{"text": "Cut the cargo pod free.", "outcomes": [
				{"text": "The drone cuts through the ice and hauls the pod aboard. Inside: hull plating, still in its wrapping, and a forgotten credit chit.",
					"effects": ["item: hull_plate x1", "+15 Scrip"]}]},
			{"text": "Leave it.", "outcomes": [
				{"text": "You leave the ice field as you found it.", "effects": ["nothing"]}]},
		],
	},
	"patient_wren": {
		"kind": "distress", "zones": ["any"], "rings": [2, 2], "story": true,
		"title": "Distress signal: freighter Patient Wren",
		"text": "\"Collective freighter Patient Wren, drive dead, three aboard. The Rabble shot us up on their way past. They were heading for some moon station. Can you spare anything? A spark for the drive would do it.\"",
		"choices": [
			{"text": "Send the drone across to fix their drive.", "needs": "drone", "outcomes": [
				{"text": "The drone crawls into their engine bay and comes back singed but pleased. The Wren's drive turns over. The captain sends across fuel cells and a thank-you.",
					"effects": ["+2 fuel", "+30 Scrip"]}]},
			{"text": "Leave them.", "outcomes": [
				{"text": "You log their position for the next ship along and jump away.", "effects": ["nothing"]}]},
		],
	},
	# The two examples from the template, for normal runs (slice 2).
	"ninth_bell": {
		"kind": "distress", "zones": ["Zaa'sh", "Reach"], "rings": [2, 4],
		"title": "Distress signal: pilgrim skiff Ninth Bell",
		"text": "A Zaa'sh pilgrim skiff drifts with its hull split open. Two pilgrims in suits wave from the airlock. A third shape, half hidden behind the shrine-mast, holds something that might be a rifle.",
		"choices": [
			{"text": "Pull alongside and take them aboard.", "outcomes": [
				{"chance": 60, "text": "They are what they look like. The elder presses a bell into your hands.", "effects": ["relic: Pilgrim's bell", "+1 fuel"]},
				{"chance": 40, "text": "The third one is Rabble. The \"pilgrims\" draw too.", "effects": ["fight: rabble_cutter"]}]},
			{"text": "Send the drone to patch their hull from outside.", "needs": "drone", "outcomes": [
				{"text": "The drone seals the split. They limp off toward the shrines, singing.", "effects": ["+30 Scrip"]}]},
			{"text": "Hail the third one first.", "outcomes": [
				{"chance": 50, "text": "A young pilgrim with a broken prayer-staff. Embarrassed. Grateful.", "effects": ["+2 fuel"]},
				{"chance": 50, "text": "No answer. The rifle comes up. You pull away under fire.", "effects": ["-2 hull"]}]},
			{"text": "Leave them.", "outcomes": [
				{"text": "You log their position for the next ship along.", "effects": ["nothing"]}]},
		],
	},
	"customs_stop": {
		"kind": "beacon", "zones": ["Terran"], "rings": [1, 3],
		"title": "Terran patrol",
		"text": "A Terran patrol cutter hails you: routine inspection, hold position.",
		"choices": [
			{"text": "Hold position and let them scan you.", "outcomes": [
				{"chance": 70, "text": "Clean. The officer waves you on with a bored salute.", "effects": ["nothing"]},
				{"chance": 30, "text": "They find \"irregular salvage\" and fine you for it.", "effects": ["-25 Scrip"]}]},
			{"text": "Offer a \"processing fee\".", "needs": "15 Scrip", "outcomes": [
				{"text": "The officer pockets it and marks you cleared. He also mentions a wreck nearby.", "effects": ["-15 Scrip", "reveal: wreck field"]}]},
			{"text": "Run for it.", "outcomes": [
				{"text": "They don't chase. They do take a few shots.", "effects": ["-2 hull"]}]},
		],
	},
	# Placeholders for normal runs (Claude, 22 Nov), in the template's shape; Zachary's own events replace or join
	# them. Readable copy: claude/echo-landing-space-events.md in the Project.
	"tumbling_cache": {
		"kind": "beacon", "zones": ["any"], "rings": [1, 2],
		"title": "Tumbling supply cache",
		"text": "A supply crate tumbles end over end, its beacon still blinking. The seal is Terran; the scorch marks around the lock are not.",
		"choices": [
			{"text": "Grab it with the docking clamp.", "outcomes": [
				{"chance": 70, "text": "It comes aboard clean. Fuel cells and a missile, packed in foam.", "effects": ["+1 fuel", "+1 missiles"]},
				{"chance": 30, "text": "Someone rigged the lock. It goes off against your hull.", "effects": ["-2 hull"]},
			]},
			{"text": "Send the drone to open it out there.", "needs": "drone", "outcomes": [
				{"text": "The drone finds the tripwire, snips it, and brings the contents home.", "effects": ["+1 fuel", "+1 missiles", "+1 drone parts"]},
			]},
			{"text": "Leave it spinning.", "outcomes": [
				{"text": "Somebody else's problem.", "effects": ["nothing"]},
			]},
		],
	},
	"looping_beacon": {
		"kind": "beacon", "zones": ["any"], "rings": [1, 5],
		"title": "Old navigation beacon",
		"text": "A pre-war Terran beacon, still looping the same message: a docking schedule for a station that hasn't existed for forty years.",
		"choices": [
			{"text": "Pull its power cell.", "outcomes": [
				{"chance": 75, "text": "The cell is old but full.", "effects": ["+1 fuel"]},
				{"chance": 25, "text": "Pulling it trips a distress call on every channel. Something answers.", "effects": ["+1 fuel", "fight: rabble_cutter"]},
			]},
			{"text": "Copy its archive before you go.", "outcomes": [
				{"chance": 50, "text": "Mostly schedules. One file is a survey of a sector nobody charts any more.", "effects": ["reveal: old survey site"]},
				{"chance": 50, "text": "Mostly schedules. Tar'Besh might like the old station crest on the casing.", "effects": ["relic: Station crest plate"]},
			]},
			{"text": "Leave it singing.", "outcomes": [
				{"text": "You let it keep its schedule.", "effects": ["nothing"]},
			]},
		],
	},
	"escort_job": {
		"kind": "beacon", "zones": ["Terran"], "rings": [1, 3],
		"title": "A freighter wants an escort",
		"text": "A Terran ore hauler hails you. \"Pirates have been picking off haulers on this lane. Ride with us to the next beacon and the company pays.\"",
		"choices": [
			{"text": "Take the job.", "outcomes": [
				{"chance": 60, "text": "A quiet run. The company pays on arrival, and the captain throws in a crate of plating.", "effects": ["+45 Scrip", "item: hull_plate x1"]},
				{"chance": 40, "text": "Halfway there, a Rabble cutter drops out of fold right on top of you.", "effects": ["+20 Scrip", "fight: rabble_cutter"]},
			]},
			{"text": "Ask for the pay up front.", "outcomes": [
				{"text": "The captain laughs, then pays half. You fly the lane. Nothing happens.", "effects": ["+25 Scrip"]},
			]},
			{"text": "Turn it down.", "outcomes": [
				{"text": "They grumble and carry on alone.", "effects": ["nothing"]},
			]},
		],
	},
	"stolen_fighter": {
		"kind": "beacon", "zones": ["Terran"], "rings": [2, 4],
		"title": "A patrol with questions",
		"text": "\"Pilot, your fighter matches one reported scrapped twenty years ago. Explain that.\" The Terran patrol's guns are already warm.",
		"choices": [
			{"text": "Send them the Landing's repair records.", "outcomes": [
				{"chance": 70, "text": "S.A.R.A.'s paperwork is immaculate. They apologise, stiffly.", "effects": ["nothing"]},
				{"chance": 30, "text": "The records only make them more suspicious.", "effects": ["fight: terran_patrol"]},
			]},
			{"text": "Pay the \"re-registration fee\".", "needs": "30 Scrip", "outcomes": [
				{"text": "It is not a real fee. It works anyway.", "effects": ["-30 Scrip"]},
			]},
			{"text": "Run.", "outcomes": [
				{"text": "They fire twice and don't follow.", "effects": ["-2 hull"]},
			]},
		],
	},
	"duel_challenge": {
		"kind": "beacon", "zones": ["Zaa'sh"], "rings": [2, 4],
		"title": "A duellist's challenge",
		"text": "A Zaa'sh skiff turns broadside and rings its bell three times: a challenge. Its pilot bows on your screen, waiting.",
		"choices": [
			{"text": "Accept the duel.", "outcomes": [
				{"text": "The pilot bows again, lower, and opens fire.", "effects": ["fight: zaash_skiff"]},
			]},
			{"text": "Bow and decline.", "outcomes": [
				{"chance": 70, "text": "A long look. Then a nod. Declining honestly is allowed.", "effects": ["nothing"]},
				{"chance": 30, "text": "They take it as an insult and demand a shrine tithe for the slight.", "effects": ["-15 Scrip"]},
			]},
			{"text": "Offer quartz as a gift instead.", "needs": "item: quartz", "outcomes": [
				{"text": "The pilot accepts with both claws and gives you a bell from their mast.", "effects": ["item: quartz x-1", "relic: Duellist's bell"]},
			]},
		],
	},
	"prayer_buoy": {
		"kind": "beacon", "zones": ["Zaa'sh"], "rings": [1, 3],
		"title": "A prayer buoy",
		"text": "A Zaa'sh prayer buoy hangs in the dark, hung with bells and small offerings: coins, bright wire, a carved tooth.",
		"choices": [
			{"text": "Leave an offering.", "needs": "10 Scrip", "outcomes": [
				{"text": "Nothing happens. You feel slightly better about the next fight.", "effects": ["-10 Scrip", "+2 hull"]},
			]},
			{"text": "Take the coins.", "outcomes": [
				{"chance": 50, "text": "Nobody sees.", "effects": ["+30 Scrip"]},
				{"chance": 50, "text": "A pilgrim skiff was waiting behind the moon.", "effects": ["+30 Scrip", "fight: zaash_skiff"]},
			]},
			{"text": "Ring the bell and go.", "outcomes": [
				{"text": "It rings for a long time after you leave.", "effects": ["nothing"]},
			]},
		],
	},
	"refugee_convoy": {
		"kind": "distress", "zones": ["Collective"], "rings": [1, 3],
		"title": "Distress signal: refugee convoy",
		"text": "Six mismatched Collective hulls, lashed together. \"Our air scrubbers are failing. Anything you can spare.\" Children's drawings are taped inside the viewports.",
		"choices": [
			{"text": "Send the drone over to fix their scrubbers.", "needs": "drone", "outcomes": [
				{"text": "The drone rebuilds two scrubbers from parts of a third. The convoy's engineer sends back what they can spare.", "effects": ["+2 drone parts", "+10 Scrip"]},
			]},
			{"text": "Give them a fuel cell.", "outcomes": [
				{"text": "They'll make the next station now. An old woman sends a carved charm across.", "effects": ["-1 fuel", "relic: Convoy charm"]},
			]},
			{"text": "Sell them a fuel cell.", "outcomes": [
				{"text": "They pay. They don't look at you while they do it.", "effects": ["-1 fuel", "+35 Scrip"]},
			]},
			{"text": "Leave.", "outcomes": [
				{"text": "You log their position for a Terran patrol.", "effects": ["nothing"]},
			]},
		],
	},
	"smugglers": {
		"kind": "beacon", "zones": ["Collective"], "rings": [2, 4],
		"title": "Smugglers' offer",
		"text": "A Collective freighter with its transponder off. \"Missiles, cheap, no questions. Military surplus.\"",
		"choices": [
			{"text": "Buy a rack of missiles.", "needs": "30 Scrip", "outcomes": [
				{"chance": 80, "text": "Real missiles. Probably stolen.", "effects": ["-30 Scrip", "+3 missiles"]},
				{"chance": 20, "text": "Painted pipes. They're already gone.", "effects": ["-30 Scrip"]},
			]},
			{"text": "Report them to the Terran patrol.", "outcomes": [
				{"chance": 60, "text": "The patrol picks them up an hour later and sends you the bounty.", "effects": ["+25 Scrip"]},
				{"chance": 40, "text": "They hear you make the call.", "effects": ["fight: collective_freighter"]},
			]},
			{"text": "Ignore them.", "outcomes": [
				{"text": "Not your business.", "effects": ["nothing"]},
			]},
		],
	},
	"toll_gate": {
		"kind": "beacon", "zones": ["Reach"], "rings": [2, 5],
		"title": "Rabble toll",
		"text": "Two Rabble cutters block the lane, guns out. \"Toll's forty. Or we take it off your hull.\"",
		"choices": [
			{"text": "Pay the toll.", "needs": "40 Scrip", "outcomes": [
				{"text": "They wave you through, laughing.", "effects": ["-40 Scrip"]},
			]},
			{"text": "Bluff: claim you're with the Nest.", "outcomes": [
				{"chance": 50, "text": "They believe you, and even apologise.", "effects": ["nothing"]},
				{"chance": 50, "text": "\"The Nest doesn't fly Terran junk.\"", "effects": ["fight: rabble_cutter"]},
			]},
			{"text": "Refuse.", "outcomes": [
				{"text": "They take it off your hull.", "effects": ["fight: zaash_skiff_rabble"]},
			]},
		],
	},
	"captive_tow": {
		"kind": "distress", "zones": ["Reach"], "rings": [3, 5],
		"title": "A cargo pod on a tow line",
		"text": "A Rabble ship tows a sealed cargo pod. Something inside is knocking on the hull in a pattern: three short, three long, three short.",
		"choices": [
			{"text": "Attack the Rabble ship.", "outcomes": [
				{"text": "They cut the pod loose and turn to fight.", "effects": ["fight: arachnay_weaver_rabble"]},
			]},
			{"text": "Have the drone cut the tow line quietly.", "needs": "drone", "outcomes": [
				{"chance": 50, "text": "The pod drifts free and they never notice. The captives inside pay you with everything they have.", "effects": ["+40 Scrip", "+1 fuel"]},
				{"chance": 50, "text": "The line sparks as it parts. They notice.", "effects": ["fight: arachnay_weaver_rabble"]},
			]},
			{"text": "Leave it.", "outcomes": [
				{"text": "The knocking stops before you jump.", "effects": ["nothing"]},
			]},
		],
	},
	"pirate_market": {
		"kind": "beacon", "zones": ["Reach"], "rings": [2, 5],
		"title": "A pirate market",
		"text": "A hollowed asteroid strung with lights. Rabble, Ervani couriers and a Moogli or two haggle under a sign that reads NO SHOOTING INSIDE.",
		"choices": [
			{"text": "Buy hull plating.", "needs": "25 Scrip", "outcomes": [
				{"text": "Stolen, but it's good plating.", "effects": ["-25 Scrip", "item: hull_plate x2"]},
			]},
			{"text": "Sell a spare drone part.", "needs": "drone parts", "outcomes": [
				{"text": "A Moogli tinkerer buys it for more than it's worth.", "effects": ["-1 drone parts", "+30 Scrip"]},
			]},
			{"text": "Ask about the Nest.", "needs": "15 Scrip", "outcomes": [
				{"text": "An Ervani courier, for a price, tells you where the Rabble keep a stronghold.", "effects": ["-15 Scrip", "reveal: pirate stronghold"]},
			]},
			{"text": "Leave before anyone remembers your face.", "outcomes": [
				{"text": "Probably wise.", "effects": ["nothing"]},
			]},
		],
	},
	"moogli_spill": {
		"kind": "distress", "zones": ["any"], "rings": [1, 3],
		"title": "Distress signal: Moogli trader",
		"text": "\"Help! Help, help! Our cargo racks came open and everything is floating away!\" A cloud of crates, fruit and very small hats drifts around a round Moogli ship.",
		"choices": [
			{"text": "Send the drone to round it all up.", "needs": "drone", "outcomes": [
				{"text": "The drone herds the crates back like a sheepdog. The Moogli insist on paying.", "effects": ["+40 Scrip"]},
			]},
			{"text": "Nudge crates back with your hull.", "outcomes": [
				{"chance": 70, "text": "Slow work, but they're grateful.", "effects": ["+20 Scrip"]},
				{"chance": 30, "text": "One crate held fireworks.", "effects": ["+20 Scrip", "-1 hull"]},
			]},
			{"text": "Leave them to it.", "outcomes": [
				{"text": "They wave sadly. One waves a small hat.", "effects": ["nothing"]},
			]},
		],
	},
	"garden_ship": {
		"kind": "beacon", "zones": ["any"], "rings": [2, 4],
		"title": "A Vuultam garden ship",
		"text": "A Vuultam garden ship drifts by, its petals open to the starlight. Its gardener, all moss and long hair, invites you aboard for tea.",
		"choices": [
			{"text": "Accept the tea.", "outcomes": [
				{"text": "You leave rested, and the gardener's people have patched your hull while you sat.", "effects": ["+3 hull"]},
			]},
			{"text": "Trade a medpack for seeds.", "needs": "item: medpack", "outcomes": [
				{"text": "Strange seeds, warm to the touch. Someone at the Landing will know what they are.", "effects": ["item: medpack x-1", "relic: Garden-ship seeds"]},
			]},
			{"text": "Ask the way.", "outcomes": [
				{"text": "The gardener points you toward somewhere nobody else goes.", "effects": ["reveal: quiet sector"]},
			]},
		],
	},
	"derelict": {
		"kind": "beacon", "zones": ["any"], "rings": [3, 5],
		"title": "A derelict on emergency power",
		"text": "A Scyldar hull, dark except for a single blinking light. No answer on any channel.",
		"choices": [
			{"text": "Send the drone inside.", "needs": "drone", "outcomes": [
				{"chance": 60, "text": "Nobody aboard. The drone strips what it can carry.", "effects": ["+2 drone parts", "+1 fuel"]},
				{"chance": 40, "text": "Somebody was aboard. Rabble, waiting.", "effects": ["fight: scyldar_lantern_rabble"]},
			]},
			{"text": "Scan it from a distance.", "outcomes": [
				{"text": "The blinking light is a beacon tag, worth something to its owners.", "effects": ["+20 Scrip"]},
			]},
			{"text": "Leave it be.", "outcomes": [
				{"text": "Some wrecks are better left alone.", "effects": ["nothing"]},
			]},
		],
	},
	"solar_flare": {
		"kind": "beacon", "zones": ["any"], "rings": [2, 5],
		"title": "Solar flare",
		"text": "The star here is restless. Your sensors scream a warning: a flare, seconds out.",
		"choices": [
			{"text": "Burn hard for the edge of the system.", "outcomes": [
				{"text": "You clear it, at the cost of fuel.", "effects": ["-1 fuel"]},
			]},
			{"text": "Shelter behind the nearest moon.", "outcomes": [
				{"chance": 50, "text": "The moon takes most of it.", "effects": ["nothing"]},
				{"chance": 50, "text": "Not quite far enough behind it.", "effects": ["-2 hull"]},
			]},
			{"text": "Ride it out on shields.", "outcomes": [
				{"text": "The shields hold, mostly.", "effects": ["-1 hull"]},
			]},
		],
	},
	"burning_courier": {
		"kind": "distress", "zones": ["any"], "rings": [2, 4],
		"title": "Distress signal: Ervani courier",
		"text": "An Ervani courier ship trails smoke. \"Fire in the hold! We can't vent, the airlock jammed!\"",
		"choices": [
			{"text": "Send the drone to force their airlock.", "needs": "drone", "outcomes": [
				{"text": "The airlock pops, the air goes, the fire goes with it. They pay well.", "effects": ["+35 Scrip", "+1 fuel"]},
			]},
			{"text": "Take their package and deliver it for them.", "outcomes": [
				{"text": "A small sealed box. The address is a pirate market. You're paid in advance.", "effects": ["+40 Scrip", "reveal: pirate market"]},
			]},
			{"text": "Leave.", "outcomes": [
				{"text": "The smoke thins as you jump. You hope that's good news.", "effects": ["nothing"]},
			]},
		],
	},

}


# Picks one outcome of a choice by its chances (equal chances if none are given).
static func roll(choice: Dictionary) -> Dictionary:
	var outcomes: Array = choice["outcomes"]
	if outcomes.size() == 1:
		return outcomes[0]
	var total := 0
	for o in outcomes:
		total += int(o.get("chance", 100 / outcomes.size()))
	var pick: int = randi() % maxi(1, total)
	for o in outcomes:
		pick -= int(o.get("chance", 100 / outcomes.size()))
		if pick < 0:
			return o
	return outcomes[outcomes.size() - 1]
