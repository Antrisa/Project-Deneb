extends RefCounted
# Space events (21 Nov 2026): what happens at beacons and distress signals. Written in the same shape as the
# event template Zachary writes in (claude/echo-landing-space-events-template.md), so his events go in as they are.
#
# An event: title, text, and 2-4 choices. A choice may need something ("needs") and has one or more outcomes,
# each with a chance (percent; leave it out for a single outcome) and effects written like the template:
#   "+40 Scrip", "-20 Scrip", "+2 fuel", "-1 fuel", "+3 hull", "-2 hull", "+1 missiles", "+2 drone parts",
#   "item: hull_plate x2", "relic: <name>", "fight: rabble_cutter", "reveal: <special sector>", "nothing"
# Needs: "drone", "40 Scrip", "item: medpack", "missiles" (more kinds come with crew and ship parts).
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
