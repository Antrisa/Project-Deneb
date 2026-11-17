import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import SHEETS
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
wb = Workbook(); ws = wb.active; ws.title = "Overview"
over = [["Echo Landing: items, crafting and hotel meals (draft, 17 Nov)"], [],
 ["What this is", "Every resource, component, tool, machine, consumable, dish and hotel furniture piece proposed so far, with recipes and prices. Edit freely: it is the working list to merge with the economy bible."],
 ["Tiers", "Every tool, weapon, armour piece, chest and sprinkler goes basic, then steel, then titanium, then Precursor."],
 ["Cut", "No water purification and no battery/power system. Ice is sold, and made into ice cream and drinks."],
 ["Energy", "A Stardew-style energy bar: actions cost energy, food restores it."],
 ["Hotel meals", "Once a week you give the kitchen bot a recipe and stock the pantry for every guest for 7 days. A well-fed, varied week means happier guests, higher pay and a better star rating. See the Hotel meals tab."],
 ["Prices", "Sell prices are in station scrip and are first guesses for balancing."],
 ["Fixes to the bible", "Quartz (floors 1-15) and thermal quartz (vents 31-45) are now separate, with the precision lens using thermal quartz. Stone drops from every rock. 1 log = 4 planks. Lithium cells and high-density cores are made at the Arc Smelter."],
 [], ["Tab", "Rows"]] + [[t, len(r)] for t, h, r in SHEETS]
for row in over: ws.append(row)
ws["A1"].font = Font(bold=True, size=14)
for c in ("A3", "A4", "A5", "A6", "A7", "A8", "A9", "A11", "B11"): ws[c].font = Font(bold=True)
ws.column_dimensions["A"].width = 22; ws.column_dimensions["B"].width = 110
for r in range(3, 10): ws.cell(r, 2).alignment = Alignment(wrap_text=True, vertical="top")
fill = PatternFill("solid", fgColor="F3F3F3")
WIDE = {"Main uses": 46, "Used for": 46, "Upgrade bonus": 50, "Recipe": 46, "Notes": 40, "Effect": 40, "Detail": 110, "Where": 34,
        "Ingredients": 46, "Basic (start)": 38, "Steel": 38, "Titanium": 42, "Precursor": 38, "Takes": 30, "Makes": 34}
for title, head, rows in SHEETS:
    s = wb.create_sheet(title)
    s.append(head)
    for c in s[1]: c.font = Font(bold=True); c.fill = fill
    for r in rows: s.append(r)
    for i, h in enumerate(head, start=1):
        col = s.cell(1, i).column_letter
        s.column_dimensions[col].width = WIDE.get(h, max(14, min(30, len(h) + 4)))
        if WIDE.get(h, 0) >= 30:
            for r in range(2, len(rows) + 2): s.cell(r, i).alignment = Alignment(wrap_text=True, vertical="top")
    s.column_dimensions["A"].width = max(s.column_dimensions["A"].width, 26)
    s.freeze_panes = "B2"
wb.save(sys.argv[1] if len(sys.argv) > 1 else 'Echo_Landing_items_crafting.xlsx')
print("ok", sum(len(r) * len(h) for t, h, r in SHEETS))
