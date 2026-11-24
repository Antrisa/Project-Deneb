# Garrick, Saffi & Kit: the family's side arc (24 Nov 2026)

**Decided with Zachary, 24 Nov:** "every character has own arc plus a short family shared arc": an arc each for Garrick, Saffi and Kit, and a two-scene family side arc ([GARRICK_SAFFI_KIT.md](GARRICK_SAFFI_KIT.md)). Claude's first suggestions for the rest, taken: **Garrick was security officer on the refugee transport that crash-landed here**, and a bounty hunter he let dock brought a Chernobog cutter down on it (so he distrusts your trade); **Kit's beacon** leads to a smuggler's cache on the jump map, and **his 8 is a deputy badge** you set down at home; their weeks: the model ship and the seals on Saturdays, Saffi's Monday lunch with Rusk and the market. **Then (Zachary, 24 Nov):** "garriks 8 heart is too powerful, change to self defense class, attacking boarders take extra damage on your ship" (it was Perimeter Defence: the station's guns softening up the first ship you fought on each run); "saffi increase max energy perk" (it was a Sunday potluck: share a dish for friendship with everyone and a well-fed morning).

**The family's story (Claude's drafts):** about forty refugees, Saffi and Kit (in a sling) among them, came down on this moon in a transport with its drive shot out, and S.A.R.A. talked them in. Every settler signed the scorched hull plate now in the museum; Kit's is a handprint. The first night, Saffi made soup for forty in a dented helmet. Most of the forty moved on later; they stayed.

**Two scenes** (side arcs are 2–3 scenes). All three need the hearts. Each of them also has an arc of their own ([GARRICK.md](GARRICK.md), [SAFFI.md](SAFFI.md), [KIT.md](KIT.md)), which carry the rewards.

- 4: Saturday morning, a model of your ship, mostly glue. Which way does the cockpit go?
- 6: Kit didn't come home. He went to the cavern gate to see a crawler, so he wouldn't be scared; Vzz'ket kept him by his camp stove. Brave together counts double.

**What's whose:** the model ship is from Garrick's Saturday day line; the scenes and lines are Claude's drafts. Right answers give +60 to the event's resident and some to the other two.

**Flags:** `guard_model_ship` (4), `guard_brave_together` (6).

## In the game (24 Nov)

Both are playable cutscenes (`guard_4` on Garrick's hearts with Saffi and Kit, `guard_6` on Saffi's with Garrick and Kit; Vzz'ket is in 6). Not run in Godot yet.

- **Letter:** the morning after 6, "Double", from all three.

---

## ♥4 The Model Ship

**Trigger:** Their flat, Saturday 09:00–12:00. *(Claude)*

- *[Saturday at Garrick and Saffi's. On the table: a model starship, mostly glue. Garrick holds a wing. Kit holds the other. They don't match.]*
- **KIT:** "[happy] It's YOUR ship! We're making your ship! Dad did the engines. I did the fire."
- **GARRICK:** "Your ship had fire coming out of it when it landed. Kit insists on accuracy."
- **SAFFI:** "[happy] They've been at it since breakfast. There's glue on the ceiling. I don't know how."
- **GARRICK:** "{name}. You've seen the real one up close. Which way round does the cockpit go?"
- **CHOICE:**
  - **"Cockpit forward, wings level."** (+High Friendship)
    - *[You turn the cockpit round and hold the wings level while the glue sets. Kit gasps. It looks like a ship.]*
    - *(+30 friendship with Kit)*
    - *(+30 friendship with Saffi)*
  - **"Leave it. It's perfect as it is."** (+Friendship)
    - **KIT:** "[happy] SEE, Dad?"
    - **GARRICK:** "[sad] ...It has three wings, Kit."
    - *(+30 friendship with Kit)*
  - **"Let me do it. You're doing it wrong."**
    - **KIT:** "[angry] It's OUR ship. You fly the real one."
    - *(-20 friendship with Kit)*
- *[It takes until lunch. When it's done it has two wings, one engine, a great deal of fire, and a cockpit pointing the right way.]*
- **KIT:** "[happy] It's going on the shelf! Next to the photo! The one from the crash!"
- **SAFFI:** "The photo where we're all filthy. [love] My favourite."

---

## ♥6 Brave Together

**Trigger:** The mine, by the cavern gate, 18:45–20:15, after 4. With Vzz'ket. *(Claude)*

- *[Kit didn't come home for dinner. Saffi tried the fountain; Garrick tried every airlock. It was Vzz'ket's comm that found him: the cavern gate.]*
- *[Kit sits by Vzz'ket's camp stove with a blanket round him and a cup of something hot. Vzz'ket sits beside him, spear across his knees.]*
- **KIT:** "[sad] I wanted to see a crawler. Just one. So I'd know what they look like. So I wouldn't be scared any more."
- **VZZ'KET:** "The small one reached the gate. I asked him to wait with me. He has waited very well."
- **GARRICK:** "[angry] Kit. Do you know what's down there? Do you know what I thought when..."
- *[Garrick stops. His hands are shaking. Saffi looks at you.]*
- **CHOICE:**
  - **"Kit, being scared is how you know to come home."** (+High Friendship)
    - **KIT:** "[sad] ...I did want to come home. I didn't know how to stop being brave."
    - *(+30 friendship with Garrick)*
    - *(+30 friendship with Kit)*
  - **"Let Garrick hold him first. Talk later."** (+Friendship)
    - *[Garrick picks Kit up, blanket and all, and doesn't say anything for a long time.]*
    - *(+30 friendship with Garrick)*
  - **"He's fine. No harm done."**
    - **SAFFI:** "[angry] He's fine because Vzz'ket was here. Not because it was fine."
    - *(-20 friendship with Saffi)*
- **SAFFI:** "[sad] Next time you want to be brave, come and find one of us first. Brave together counts double."
- **KIT:** "...Double?"
- **GARRICK:** "[sad] Double. House rule."
- **GARRICK:** "Thank you. I owe you."
- **VZZ'KET:** "You owe me nothing, chief. You hold your gates. I hold mine."
- *[The next morning: a letter (`guard_double`, in [MAIL.md](../MAIL.md))]*
