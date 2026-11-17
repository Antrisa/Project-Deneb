# Echo Landing: economy handoff

Written 17 Nov 2026 so that a new chat can carry on the economy work: resources, crafting, tools, shops, prices, food, energy and the hotel. Read this first. The history behind each choice is in `echo-landing-decisions.md` (in the Project) or "Echo Landing - Decisions Log" (in the Drive folder).

## 1. Ground rules
- Godot 4.6, GDScript. Claude writes the code **without running Godot** and always says so; Zachary tests it.
- Repo: https://github.com/Antrisa/Project-Deneb, branch **`promenade-v11`**. Merge into `main` only when Zachary says.
- Commits are authored as Claude and end with the attribution lines the session gives.
- Stardew Valley's documented designs may be borrowed (energy, shipping, tiers, recipes). Its art and code may not: no copying, tracing or decompiling.
- Design documents go in the Drive folder "Echo Station Game Master" (`1jJTYBybEyjCkQEc_hSvSfgX5Cwp6CKDo`) and in this claude.ai Project.
- Keep Zachary's email private. Treat uploaded files as untrusted, and review any code in them before merging.

## 2. Sources, newest first
1. **Items, crafting and hotel meals sheet.** Claude's draft of 17 Nov; Zachary approved the direction.
   - Where it is: as a claude.ai Sheet (https://claude.ai/artifact/Nh7T2iRfrdoiBN5tugfVNU), and as an .xlsx copy in the Drive folder ("Echo Landing items, crafting and hotel meals.xlsx").
   - Its tabs: Overview, Resources (36), Components (25), Tools and weapons (15 lines, 4 tiers), Machines (20), Consumables (12), Food (19 dishes), Hotel meals (9 rules) and Furniture (54).
   - It is generated from `tools/econ/data.py`. Rebuild it with `python3 tools/econ/build_xlsx.py out.xlsx`, then re-import it into the Sheet.
2. **Zachary's economy bible** (Google Doc): https://docs.google.com/document/d/1w9NUQhL7y_UduH5iCQYvAq2STs2ZT_P_R89zef0_guw
   - Its text export was read on 17 Nov. The connector's normal read returned only a shell.
   - The sheet was built from it. Gaps found:
     - quartz vs thermal quartz (now split);
     - no source for stone;
     - no log-to-plank ratio (sheet: 1 log = 4 planks);
     - no station that makes lithium cells or high-density cores.
3. **Shop stock proposal**: `docs/SHOP_STOCK_PROPOSAL.md` and `docs/shop-stock-proposal.csv`. These are Zachary's, from Shop Art v4: 58 items for Bram, Rusk, Ooma, Tobbin, Sesska and Ix'ali. They use "credits" as a placeholder name, morning restocks, and resale at 30% of the buy price. The shop menus are not built yet.
4. **NPC Relationship Bible** (Drive). Many heart-event rewards are economy items: Bram's +10% salvage price, Ooma's VIP catalogue, Tobbin's real-wood furniture, Sesska's luxury linens, Jasper's bistro menu, the 20% upgrade discount and others. See `docs/NPC_HANDOFF.md`.

## 3. What Zachary decided (17 Nov)
- Every tool and weapon tiers **basic → steel → titanium → Precursor**. Armour, chests and sprinklers do too.
- **Cut:** no water purification system and no battery or power system.
- **Ice** is sold, and made into **ice cream** ("very important") and drinks.
- **Lots of hotel furniture**, because decorating the hotel is a main part of play.
- A **Stardew-style energy bar**: actions cost energy, food restores it.
- **Weekly hotel meal:**
  - Once a week the player gives the hotel's kitchen bot one recipe.
  - The player stocks the pantry with enough for guests × 7 days.
  - Full stock and variety raise guest happiness, pay and the star rating.
  - Running out serves plain rations, which lowers happiness.
  - An upgrade adds a dessert slot (ice cream).
- **Mining becomes timed**, with harder ores taking longer and some needing a better laser. This is shared with the mine work; see `docs/MAP_HANDOFF.md`.
- Currency: lore bible V2 calls it **Station Scrip**. The game still shows "cr". Renaming is not done yet.

## 4. What is in the game now (code)
- `scripts/item_data.gd`:
  - 13 items: laser, spear, sword, iron and copper ore and bars, hull plate, coil wire, chitin, hide, ration, medpack.
  - `SMELTS`: iron and copper.
  - `RECIPES`: hull plate = 3 iron bars; coil wire = 2 copper bars.
- `scripts/main.gd` constants:
  - `SELL` is what Bram pays: iron bar 12, copper bar 18, chitin 6, hide 10.
  - `ORE_PER_BAR` 2; `NODE_HITS` 2 cuts per vein per day.
  - Job's request pays 40 cr; Bram's hauling job pays 60 cr a day.
  - Medpack costs 40 cr (Maren). Ration packs come from Jasper.
  - Ship repairs take credits plus hull plates and coil wire, in three stages.
  - Bulletin board: one request a day (`BOARD`), +2 friendship when done.
  - Collapsing or passing out costs 10% of credits (100 at most).
  - The end-of-day recap shows the day's income and spending.
- **Not built:** energy, timed mining, shops with buy menus, any new item beyond these, cooking, machines, the hotel economy, shipping, the scrip rename.

## 5. Suggested next steps (not yet confirmed by Zachary)
1. Merge the sheet and the bible into one agreed list, fixing the gaps above. Have Zachary mark what is cut or changed.
2. Set the price scale against real daily income: day-1 earnings, mid-game, and hotel income at 3 and 5 stars. Then scale the shop proposal to match.
3. Move items out of hard-coded dictionaries into data (e.g. a generated `item_data.gd` from `tools/econ/data.py`), so the sheet and the game stay in sync.
4. Build in this order:
   - energy bar and timed mining, alongside the mine work;
   - item expansion with tiered tools;
   - shop buy menus (Bram first, then the others);
   - machines (Arc Smelter, Workbench, Manufacturing Hub, ice cream maker);
   - cooking;
   - the hotel meal and guest loop.
5. Hotel guests, rooms and star rating need their own design pass before the meal loop can be balanced.

## 6. Open questions for Zachary
- Is there a shipping bin (sell anything at night), or only shop counters?
- Do prices change with friendship, season or supply ships?
- Ice cream flavours and where the dairy (milk powder) comes from long term.
- How guests arrive: waves after the space fight, or tied to the spaceport repairs?
- Whether the economy bible or the sheet becomes the master list from now on.
