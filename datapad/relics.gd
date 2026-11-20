extends RefCounted
# Restoration requirements from the Custodian Restoration Bundles & Seasonal Equipment Bible.
const CUSTODIANS := [
	{
		"name": "The Sovereign of Hydro-Flora",
		"wing": "Agridomes",
		"bundles": [
			{
				"name": "Mineral Soil Base",
				"items": [
					[
						"Silica Sand",
						15
					],
					[
						"Water-Ice Chunks",
						10
					],
					[
						"Copper Ingots",
						5
					]
				],
				"reward": "Restores irrigation pipes & unlocks Basic Sprinkler blueprint"
			},
			{
				"name": "Mycelial & Bio-Starter",
				"items": [
					[
						"Bioluminescent Spores",
						8
					],
					[
						"Glow-Moss",
						5
					],
					[
						"Tree Resin",
						3
					]
				],
				"reward": "Repairs Agridome soil beds & grants 5 Lunar Birch Saplings"
			},
			{
				"name": "First Harvest Offering",
				"items": [
					[
						"Moon-Wheat",
						10
					],
					[
						"Star-Tomatoes",
						5
					],
					[
						"Aromatic Steam-Herbs",
						3
					]
				],
				"reward": "Unlocks Evarra's Apiary & Fruit Orchard tier"
			}
		]
	},
	{
		"name": "The Chancellor of Hearths",
		"wing": "Hotel & plaza",
		"bundles": [
			{
				"name": "Structural Framing",
				"items": [
					[
						"Wood Planks",
						20
					],
					[
						"Iron Ingots",
						10
					],
					[
						"Polymer Sealant",
						4
					]
				],
				"reward": "Rebuilds Rusk's Bar (unlocks evening buff drinks)"
			},
			{
				"name": "Hearth & Lighting Grid",
				"items": [
					[
						"Thermal Quartz",
						6
					],
					[
						"Lithium Cells",
						3
					],
					[
						"Copper Ingots",
						5
					]
				],
				"reward": "Relights the station's grow-lamps and unlocks the UV Hydroponic Bed blueprint"
			},
			{
				"name": "Hospitality Comforts",
				"items": [
					[
						"Woven Void-Silk",
						4
					],
					[
						"Wooden Guest Beds",
						2
					],
					[
						"French Pastries or Bread",
						3
					]
				],
				"reward": "Opens Echo Landing Hotel (4 Guest Suites)"
			}
		]
	},
	{
		"name": "The Forgemaster of Keels",
		"wing": "Shuttle bay",
		"bundles": [
			{
				"name": "Hull & Gantry Alloy",
				"items": [
					[
						"Iron Ingots",
						15
					],
					[
						"Titanium Ingots",
						8
					],
					[
						"Pirate Scrap",
						10
					]
				],
				"reward": "Repairs docking clamps & unlocks Tier 2 Alloy Tools"
			},
			{
				"name": "FTL Drive Core",
				"items": [
					[
						"Lithium Cells",
						4
					],
					[
						"Optical Focusing Lenses",
						2
					],
					[
						"Circuit Boards",
						2
					]
				],
				"reward": "Opens the shipyard: new ships to buy"
			},
			{
				"name": "Dockyard Foundry",
				"items": [
					[
						"Cobalt-60 Shards",
						5
					],
					[
						"Wood Planks",
						10
					],
					[
						"Chitin Plates",
						5
					]
				],
				"reward": "Unlocks Shipwright's Suite (custom hulls & shields)"
			}
		]
	},
	{
		"name": "The Harbinger of Destruction",
		"wing": "Hot springs & ocean",
		"bundles": [
			{
				"name": "Thermal Containment",
				"items": [
					[
						"Titanium Ingots",
						12
					],
					[
						"Copper Ingots",
						10
					],
					[
						"Polymer Sealant",
						6
					]
				],
				"reward": "Reinforces cavern walls against seismic shockwaves"
			},
			{
				"name": "Geothermal Catalyst",
				"items": [
					[
						"Basalt Cores",
						8
					],
					[
						"Sulfur Crystals",
						8
					],
					[
						"Cobalt-60 Shards",
						5
					]
				],
				"reward": "Primes the Harbinger's controlled magma-vent charge"
			},
			{
				"name": "Aquatic Seeding",
				"items": [
					[
						"Water-Ice Chunks",
						15
					],
					[
						"Wild Plankton",
						5
					],
					[
						"Aromatic Steam-Herbs",
						3
					]
				],
				"reward": "Unlocks Hot Springs, Undersea Ocean & Fish Hatchery"
			}
		]
	}
]
