# Bram & Ooma: the side arc, Merchant Guild of Two (23 Nov 2026)

**Their own arcs:** [`BRAM.md`](BRAM.md) and [`OOMA.md`](OOMA.md). This is the side arc they share: three scenes (Zachary, 23 Nov: side arcs are 2–3 scenes), from the NPC Master's four shared outlines (the fourth, Quiet Credit, is Bram's own 4 now).

**The arc:** two traders who can't stand each other's prices, and can't do without each other.
- 2: the price war over a genuine pre-war toaster.
- 5: the tip-off. Ooma trades Bram a wreck's coordinates for a hot meal from Jasper, and you have the ship.
- 8: the Merchant Guild of Two, and Ooma's catalogue for you.

**Both need the hearts** (`"who": "Bram", "with": ["Ooma"]`), and every scene is on Ooma's days. Right answers give +60 (High Friendship) to each; wrong ones −20 with Bram. In 8 both answers are good ones (+60 or +30).

**What's whose:** the outlines are the NPC Master's; the scenes and every line are drafts by Claude. Bram's half of the old 8 reward (+10% on salvage) is replaced by his own 8's trade beacon (Zachary).

**Flags this arc sets:** `guild_toaster` (2), `guild_tip_wreck` (5), `guild_partners` and the perk `perk_ooma_catalogue` (8).

---

## In the game (23 Nov)

All three are playable cutscenes in `scripts/heart_events.gd` (`guild_2`, `guild_5`, `guild_8`, after both their own arcs). Not run in Godot yet.

- **The tip-off (5):** your next free flight has a hidden stop on the first ring, **Ooma's wreck**: a wreck field nobody else knows, which salvages like one three rings further out. It happens once (`main.gd _start_run`, `guild_tip_used`).
- **Ooma's catalogue (8, the NPC Master's "VIP Contraband Catalog"):** each visit, talking to Ooma shows you one rare item to order, paid then and there. She brings it the next time she comes. One order at a time, and the offer changes every visit: a void sapphire (260 Scrip), 2 helium-3 (380), 2 cobalt-60 (340), 3 circuit boards (300), 4 rare earths (220) or 3 lithium cells (240). Prices are about twice what the things are worth (`ShopData.VALUE`), Claude's placeholders (`main.gd OOMA_CATALOGUE`, `_ooma_order_talk`; saved as `ooma_order`).
- **Letter:** the morning after 8, Bram's "Guild business", on how the catalogue works.
- **The old outline's exotic seeds** aren't in: there's no exotic crop yet (it would need its own crop art).

---

## ♥2 Price War on Aisle One

**Trigger:** between his canopy and her kiosk, Saturday 08:00–11:00. Job has the toaster. *(The NPC Master's outline; the scene is Claude's.)*

- *[Saturday market. Job stands between Bram's canopy and Ooma's kiosk, holding a chrome toaster like a newborn.]*
- **JOB:** "Bram says this toaster's scrap. Ooma sold it me for half what Bram pays for scrap."
- **JOB:** "[happy] So I can't lose, cher. I think. I never could do the arithmetic."
- **BRAM:** "[angry] Half my scrap rate! You are selling scrap for less than scrap! That is not trade, Ooma. That is vandalism!"
- **OOMA:** "It is a genuine pre-war toaster, Bram. It has toasted through two wars."
- **BRAM:** "[angry] Which war? Which side?"
- **OOMA:** "It did not ask. Very professional."
- **JOB:** "Does it make toast, though?"
- **CHOICE:**
  - **"Split it: scrap for Bram, a sale for Ooma, toast for Job."** (+High Friendship)
    - **BRAM:** "...That is a terrible deal for me."
    - **OOMA:** "[happy] It is a wonderful deal for me."
    - **JOB:** "[happy] And I get toast!"
    - **BRAM:** "[happy] Fine. A truce. For one day."
    - **OOMA:** "For one day."
    - *(+60 friendship with Ooma)*
  - **"Bram, just lower your prices."**
    - **BRAM:** "[shocked] Lower...? I will lower my prices when this moon lowers its gravity."
    - **OOMA:** "[happy] Nothing lowers its gravity, Bram. That is rather the point of gravity."
    - *(-20 friendship with Bram)*
- *[Job plugs the toaster into Bram's counter. It toasts. Then it plays a tinny little anthem nobody recognises.]*
- **OOMA:** "I did say pre-war."

---

## ♥5 The Tip-Off

**Trigger:** Rusk's bar, Saturday 20:00–22:30, after 2. Rusk at the counter; Jasper brings the stew. *(The NPC Master's outline; the scene is Claude's.)*

- *[Rusk's bar on a Saturday night. Bram and Ooma sit two stools apart, which for them is very close.]*
- **OOMA:** "Coordinates. An unclaimed wreck, close in, and full of things you would like. Nobody else has them."
- **BRAM:** "[surprised] Why would you give me coordinates?"
- **OOMA:** "Give? Nothing is given. I want a hot meal. A real one, from the fox."
- **BRAM:** "Jasper? That is extortion. Jasper's meals are priceless."
- **RUSK:** "Jasper's meals are eight Scrip."
- **BRAM:** "Shh."
- **JASPER:** "[happy] One cavern-truffle stew, as ordered by Bram, who says he will pay me in spirit."
- **OOMA:** "[love] ...Worth it."
- *[Ooma slides a folded slip along the counter to Bram. Bram slides it on to you without unfolding it.]*
- **BRAM:** "Pilot. You have the ship. My coordinates, her stew... no. Her coordinates, my stew. Split three ways."
- **OOMA:** "He takes a third."
- **BRAM:** "A quarter."
- **CHOICE:**
  - **"Deal. And whatever's in that wreck, Bram gets first offer."** (+High Friendship)
    - **BRAM:** "[happy] First offer! Ooma, did you hear? A customer with manners."
    - **OOMA:** "I heard. Do not let it go to your head, pilot. It goes straight to his."
    - *(+60 friendship with Ooma)*
  - **"Why should I share? I'm the one flying out there."**
    - **BRAM:** "[sad] Because the coordinates are hers and the stew was mine. The arithmetic is mine too."
    - **OOMA:** "Keep it all, then. The wreck does not care who loots it."
    - *(-20 friendship with Bram)*
- *[Ooma's coordinates: a wreck waits on the first ring of your next free flight]*

---

## ♥8 Merchant Guild of Two

**Trigger:** between the stalls, Wednesday 15:00–16:45. Tobbin hangs the sign. Reward: Ooma's catalogue. *(The NPC Master's outline; the scene is Claude's.)*

- *[Between Bram's canopy and Ooma's kiosk, Tobbin is up a stepladder hanging a hand-lettered sign: OLLO & OOMA, PURVEYORS.]*
- *[Underneath, in smaller letters: OF EVERYTHING.]*
- **TOBBIN:** "[happy] I made the ampersand twice. Don't look too close at the ampersand."
- **BRAM:** "We have formed a guild. The Merchant Guild of Two."
- **OOMA:** "He sells what the station needs. I bring what the station does not know it needs. Between us: everything."
- **BRAM:** "She brings my family's seed past the blockades. I keep her shelf warm on the days the tides take her."
- **OOMA:** "And you, pilot, get the catalogue. Each time I come, one thing in it, for you. Order it, and I bring it next time."
- **CHOICE:**
  - **"To the guild!"** (+High Friendship)
    - **BRAM:** "[happy] To the guild! Tobbin, the ampersand is perfect."
    - **TOBBIN:** "[happy] It is not."
    - *(+60 friendship with Ooma)*
  - **"Isn't a guild of two just a partnership?"** (+Friendship)
    - **BRAM:** "A partnership splits the profits. A guild splits the blame. Much better."
    - **OOMA:** "[happy] He has been practising that one all week."
    - *(+30 friendship with Ooma)*
- *[Perk: Ooma's Catalogue (each visit, one rare item to order; she brings it next time)]*
- *[The next morning: a letter (`guild_catalogue`, in [MAIL.md](../MAIL.md))]*

---

## Still open

- **Art** (on the Art Fix List): the OLLO & OOMA, PURVEYORS (OF EVERYTHING) sign between the stalls, and the toaster (narrated).
- **Exotic seeds** from the old outline: a new crop, if Zachary wants one.
