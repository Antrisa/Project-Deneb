extends RefCounted
# Sample content for the review project. The host can replace all of these collections.
const ITEMS := {
	"laser":["Mining laser","Tools","Mining tool", "A handheld beam for breaking ore seams."],
	"hoe":["Field hoe","Tools","Agriculture","Turns a patch of soil before planting."],
	"water":["Watering can","Tools","Agriculture","A compact can for tending the agri dome."],
	"scythe":["Scythe","Tools","Agriculture","Cuts ripe grain in one short sweep."],
	"rod":["Fishing rod","Tools","Fishing","A collapsible rod for the station ponds."],
	"ration":["Ration #6","Supplies","Food","A foil-wrapped field ration. Restores 5 HP."],
	"healing":["Healing flask","Supplies","Consumable","A small flask of restorative medicine."],
	"stamina":["Stamina flask","Supplies","Consumable","An energy tonic for a long station shift."],
	"fertiliser":["Fertiliser","Supplies","Agriculture","A growing medium for cultivated soil."],
	"ore":["Copper ore","Materials","Raw material","Copper-bearing rock with flecks of green patina."],
	"ingot":["Copper ingot","Materials","Refined material","Refined copper, ready for the workshop."],
	"vest":["Chitin-lined vest","Gear","Body armor","Chitin plates stitched into a padded vest."],
	"optics":["Precision lens","Gear","Laser lens","Focusing optics for the mining laser."],
	"cell":["Power pack","Gear","Laser power pack","A modular cell for the mining laser."],
	"band":["Alloy ring","Gear","Ring","An alloy band with a polished stone."],
	"wire":["Copper wire","Materials","Component","Conductive wire wound onto a small spool."],
	"quartz":["Thermal quartz","Materials","Mineral","Warm mineral crystals from the geothermal vents."],
	"silicon":["Refined silicon","Materials","Component","Silicon refined for circuit boards and optical equipment."],
	"lithium":["Lithium cell","Materials","Component","A cell used in rechargeable power packs."],
	"board":["Circuit board","Materials","Component","A printed board for the station's electronics."],
	"planks":["Wood planks","Materials","Timber","Cut boards for storage and furniture."],
	"spore":["Bioluminescent spore","Materials","Organic material","A softly luminous cavern spore."],
	"resin":["Tree resin","Materials","Organic material","A sticky binder for field supplies."],
	"berry":["Berries","Supplies","Produce","A handful of berries for field rations."],
	"flare":["Glow-flare","Tools","Light","A portable light made from a spore and resin."],
	"wood_chest":["Wooden chest","Supplies","Storage","A wooden chest with 24 storage slots."]
}
const RECIPES := [
	["ingot","ore",3,1,"Arc smelter"],
	["wire","ingot",1,2,"Workbench"],
	["board","ingot",2,1,"Manufacturing hub",{"ingot":2,"silicon":2}],
	["optics","quartz",2,1,"Manufacturing hub",{"quartz":2,"ingot":1,"silicon":1}],
	["cell","lithium",2,1,"Manufacturing hub",{"lithium":2,"ingot":2,"board":1}],
	["flare","spore",1,1,"Pocket",{"spore":1,"resin":1}],
	["wood_chest","planks",15,1,"Pocket"],
	["ration","produce",2,1,"Pocket"]]
const CREW := [
	["Jasper","Head chef","Jasper dreams of bringing a Parisian bistro menu to the Landing.",3,{"birthday":"Spring 3"}],
	["Freya","Junior shipwright","Freya is bringing the damaged Terran fighter back into service.",2,{"birthday":"Summer 2"}],
	["Ana","Flight navigator","Ana reads flight paths and navigates the frontier.",1,{"birthday":"Winter 23"}],
	["Stu","Hotel lobby boy","Stu meets the Landing's newest guests in the hotel lobby.",1,{"birthday":"Spring 17"}],
	["Artie","Junior Scouts leader","Artie leads the station's Junior Scouts after waking from stasis.",2,{"birthday":"Autumn 18"}],
	["Eshu","Courier and bounty pilot","Eshu runs the Post & Privateer Dispatch and keeps in touch with every empire.",1,{"birthday":"Spring 27"}]
]
const JOBS := [
	["First ore","Jasper","Use the mining laser to collect copper ore for the station.","Gather copper ore","ore",{"needed":6,"place":"Mine"}],
	["Ship repairs","Freya","Visit the repair bay and check the damage to the Terran fighter.","Visit the repair bay","",{"place":"Spaceport"}]
]
const PLACES := [
	["Town square",181,102,"Main level","The central plaza links the station's shops and residential passages."],
	["Engineering",74,117,"Service deck","Furnaces, machinery and workbenches for processing ore."],
	["Spaceport",84,53,"West complex","Reception, the landing pad and the old barracks."],
	["Agri dome",192,38,"West complex","Cultivated beds, water reclaimers and the old garden."],
	["East complex",284,82,"East complex","The herb dome and air reclamation plant share this passage."],
	["Apartments",253,151,"Main level","Residential blocks along the outer ring."],
	["Mine",49,31,"Mining sector","Ore seams and analyzers surround the conveyor to ore processing."]
]

const GEAR_TYPES := {"hoe":"tool","water":"tool","scythe":"tool","rod":"tool","vest":"armor","optics":"lens","cell":"power","band":"ring"}
const SKILLS := [
	{"name":"Mining","icon":"i_mining","level":3,"xp":80,"goal":150,"description":"Extract minerals and ore from the caverns."},
	{"name":"Farming","icon":"i_farming","level":2,"xp":35,"goal":100,"description":"Tend crops and harvest grain in the Agridome."},
	{"name":"Fishing","icon":"i_fishing","level":1,"xp":12,"goal":60,"description":"Catch fish in the station ponds and deeper waters."},
	{"name":"Crafting","icon":"i_craft","level":2,"xp":55,"goal":100,"description":"Refine materials and assemble equipment at the workshop."}]
