# Stowaway Stu: heart events and his week (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **The hotel opens after the Ivan fight.** Stu arrives two days after Ivan falls (Wave 1), so it's open by the time he is, and none of his scenes have to wait for it (Decision 10 is settled).
- **Guests come Friday to Sunday** and stay three days.
- **His week:** Monday he cleans the hotel; Tuesday and Wednesday are his days off.
- "Change what you think is best": the rest of his week, and the changes below, are Claude's.

**What changed from the script:**
- **2:** the bag is hidden behind the potted fern, and S.A.R.A. now says so too (the script also had it "sitting by the terminal airlock"). Choice A drops "Stu," to fit the 64-character limit for choices.
- **6:** the nameplate goes on **his own door, East Home 2**, where he lives in the game (the script said the West Wing corridor, and the Master said the hotel staff room). It plays on **Sunday evening**, after the guests have checked out and tipped. It now has a choice.
- **8:** the lobby **after hours on a guest night** (Friday or Saturday, after his late shift).
- **10:** moved from the Observation Lounge to **the terminal airlock**, where he used to sit with his packed bag and watch for the next freighter (Decision 17: four of the 10s were night scenes under the stars).

**The arc:** a drifter who can't remember his name learns that staying isn't a trap.
- 2: his bag is packed. It always is.
- 4: a uniform made just for him.
- 6: a name on a door, and an empty duffel bag.
- 8: he stops running.
- 10: a freighter leaves without him, and he doesn't even look.

**What's whose:** lines marked *(Zachary)* are his, from "Heart Events: All Romances": the settings and all of Stu's and S.A.R.A.'s lines in 2 and the choices; the setting, Sesska's line, Stu's lines and the choices in 4; the setting and Stu's three lines in 6; the setting and both of Stu's lines in 8; and the outline of 10 (a candlelit picnic set up with S.A.R.A. and Jasper, and the silver bell). Everything else is a draft by Claude, for Zachary to change or approve: the closing beats of 2, the replies to 4 and Sesska's last line, Tobbin, the choice and replies in 6, the cocoa, the accept, decline and friendship endings and the tips line in 8, and all the lines of 10. Choices give +30 (Friendship) or +60 (High Friendship).

---

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | Where he goes |
|---|---|
| Monday | **Cleaning day:** the guest wings 07:00 and 11:00; lunch in the mess; sweeping the lobby 14:00; dinner; home |
| Tuesday (day off) | The terminal 09:00, watching the ships; the plaza 11:00; lunch; the common room 14:30; dinner; home |
| Wednesday (day off) | Bram's 09:30; the East complex 11:30; lunch; Ooma's stall 15:00; dinner; home |
| Thursday | **Getting ready:** polishing the bell at the front desk 07:00; lunch; the guest wings 13:00; dinner; home |
| Friday | **Transport day:** meets the guests at the terminal 07:00; carrying bags in the lobby 09:30; dinner; the front desk late shift 18:00–22:00; bed at 23:00 |
| Saturday | The lobby 07:00; dinner; the late shift 18:00–22:00; bed at 23:00 |
| Sunday | The lobby 07:00; sees the guests off at the terminal 15:00; dinner 17:30; home |

- **Days off:** Tuesday and Wednesday (`NpcData.DAYS_OFF`); the station calendar shows "Day off: Stu".
- **His day lines** (the first thing he says when you talk to him; they alternate week by week): Monday (Gloria the mop), Tuesday (watching the ships "just to watch"), Wednesday (Ooma's lost-and-found crate), Friday (transport day) and Sunday (waving the guests off). Thursday and Saturday use his usual lines.

**Flags this arc sets:** `stu_uniform` (4), `stu_nameplate` (6), the perk `perk_five_star_partner` (8), the keepsake `keepsake_silver_bell` (10), and `partner` = Stu if you accept at 8.

## In the game (23 Nov)

All five are playable cutscenes in `scripts/heart_events.gd`. He poses from his new heart-event sheet (`art/npc_stu_event.png`) and his action sheet (the bell, the luggage). S.A.R.A. speaks in 2; Sesska is in 4 and Tobbin in 6. Not run in Godot yet.

- **He only appears once he's arrived** (Wave 1, two days after Ivan falls), so his scenes wait for that.
- **You used to wake in the hotel,** so 2 could play on a Saturday or Sunday morning without leaving and coming back. Since 23 Nov you live in your own flat by the farm, and 2 plays when you walk into the hotel on those mornings. (The game still checks your home's events when you wake.)
- **To test:** in a debug build, **F3** plays the next event in order (Stu's 2 is the thirty-seventh press); it brings Wave 1 in if it hasn't arrived.
- **Checked offline:** `python3 tests/check_heart_events.py`.
- **In play since 24 Nov:** Five-Star Partner (guests pay a fifth more, `hotel.gd base_pay`; it was upstream's S.A.R.A. 8-heart bonus, which counted hearts on the old scale). **Not in yet:** the nameplate as a prop on East Home 2's door (narrated), the uniform as a new outfit, the bell as an item you can hold.

---

## ♥2 Packed Bags by the Airlock

**Trigger:** the hotel lobby with Stu at 2 hearts: Friday 09:30–11:00 (once the transport's guests are in), or Saturday or Sunday 06:00–11:00.

- *[The hotel lobby, open for the weekend. Stu is polishing the brass reception bell.]* *(Zachary)*
- *[A small, worn canvas duffel bag sits half hidden behind the potted fern.]* *(Zachary)*
- *[He jumps when you walk in, then grins sheepishly.]* *(Zachary)*
- **STU** *(Zachary)*: "[surprised] Oh! Hey, Boss! Just, uh, testing the acoustics on the lobby bell! Crisp, right? Very Parisian, just like Sara ordered!"
- **S.A.R.A.** *(Zachary, changed)*: "Indeed, Stu. Though I do wonder why your duffel bag is packed and hiding behind the fern."
- *[Stu rubs the back of his neck.]* *(Zachary)*
- **STU** *(Zachary)*: "[sad] Old habit! Look, I'm grateful you didn't space me when you found me in that hydroponics crate, Sara, really."
- **STU** *(Zachary)*: "It's just... I don't even remember my real name."
- **STU** *(Zachary)*: "Every port I've ever docked at, I work a few shifts, keep my head down, and hop the next freighter before anyone starts expecting things."
- **CHOICE:**
  - **"No pressure—stay as long as you want, leave when you're ready."** *(Zachary, shortened)* (+High Friendship)
  - **"You're actually great at this job. The guests love you."** *(Zachary)* (+Friendship)
- *[He blinks in surprise.]* *(Zachary)*
- **STU** *(Zachary)*: "Huh. Nobody's ever told me I was 'great' at anything except hiding in cargo vents."
- **STU** *(Zachary)*: "[happy] Tell you what—I'll stick around through the next transport cycle."
- *[He nudges the duffel bag a little further behind the fern. He doesn't unpack it. Not yet.]*

---

## ♥4 The Burgundy Suit

**Trigger:** Sesska's weaver shop 10:00–16:00 on his day off (Tuesday or Wednesday), after 2.

- *[Sesska's tailoring counter. Stu stands on a fitting stool, mortified and secretly thrilled, in a crisp burgundy-and-gold bellhop uniform.]* *(Zachary)*
- *[Sesska adjusts his cuffs with two arms while pinning his hem with the other two.]* *(Zachary)*
- **SESSKA** *(Zachary)*: "Stop fidgeting, young man. Void-silk lining breathes better than those greasy coveralls you arrived in."
- **STU** *(Zachary)*: "[surprised] It's... it's got gold buttons. Nobody ever made anything just for my measurements before."
- **STU** *(Zachary)*: "[shocked] Don't laugh! Sara insisted the hotel needed 'proper presentation.'"
- **STU** *(Zachary)*: "How do I look—ridiculous, or almost like I actually work here?"
- **CHOICE:**
  - **"Sharpest bellhop in the Alpha Sector."** *(Zachary)* (+High Friendship)
    - **STU:** "[happy] The Alpha Sector! I'm going to have that embroidered on something."
  - **"It suits you—you look like you belong here."** *(Zachary)* (+High Friendship)
    - **STU:** "[bashful] ...Belong here. Huh. Say that again sometime. Not now. Later."
- **SESSKA:** "[happy] Hold still. One more pin. There. Now go and carry something heavy, beautifully."

---

## ♥6 A Name on the Door

**Trigger:** the East complex 17:30–21:00 on a Sunday, after 4. Outside East Home 2, his home.

- *[Outside East Home 2, Tobbin is screwing a freshly carved wooden nameplate onto the door: STU.]* *(Zachary, moved)*
- **TOBBIN:** "[happy] There. Took me three goes to get the U straight. Don't look too close at the U."
- *[Stu stares at the nameplate, visibly emotional.]* *(Zachary)*
- **STU** *(Zachary)*: "I used to think not remembering my name meant I didn't matter—like I was just a stray cargo tag floating between stars."
- **STU** *(Zachary)*: "Today a Collective diplomat tipped me ten Scrip and told me, 'Thank you, Stu, this is the warmest welcome I've had in twenty years.'"
- **STU** *(Zachary)*: "[happy] I unpacked my duffel bag this morning. All the way to the bottom."
- **CHOICE:**
  - **"Welcome home, Stu."** (+High Friendship)
    - **STU:** "[happy] ...Home. Okay. Yeah. Welcome home, me."
  - **"The diplomat was right."** (+High Friendship)
    - **STU:** "[bashful] Twenty years! I've only been doing this a season!"
- **TOBBIN:** "[happy] If the U falls off, I'll make you a better U."
- **The next morning** *(Claude, 23 Nov)***:** a letter from Stu, "My own address" (`stu_address` in `scripts/mail_data.gd`). The text is in [MAIL.md](../MAIL.md).

---

## ♥8 After-Hours Lobby Shift (confession)

**Trigger:** the hotel lobby 21:00–midnight on a Friday or Saturday (after his late shift), with Stu at 8 hearts. Perk, whether or not you accept: Five-Star Partner.

- *[Dim lantern light in the lobby. The guests have gone to bed. Stu is on the velvet lobby sofa with two mugs of cocoa.]* *(Zachary)*
- **STU:** "[happy] Boss! I made two. I always make two. In case."
- *[He hands you a mug.]*
- **STU** *(Zachary)*: "I spent my whole life sneaking onto ships trying to find somewhere better."
- **STU** *(Zachary)*: "Funny thing is, the second I stopped running, everything I was looking for was standing right in front of me."
- **If you are dating someone else (the friendship ending):**
  - **STU:** "[happy] A home. A job. A door with my name on it. And a best friend. That's you, by the way. It's official."
  - **STU** *(Zachary, changed)*: "[happy] I don't care what my old name was anymore. Being Stu is plenty."
- **Otherwise:**
  - *[He grins nervously, his cheeks flushing a deeper green.]* *(Zachary)*
  - **STU** *(Zachary)*: "I don't care what my old name was anymore. Being 'Stu, the guy who gets to be with you' is more than enough for me."
  - **STU** *(Zachary)*: "[love] What do you say?"
  - **CHOICE:**
    - **"Yes, Stu. Stay with me."**
      - *(Stu is now your partner.)*
      - **STU:** "[surprised] Really? Really really? Okay. I'm going to ring the bell. I'm ringing the bell."
      - *[The bell rings once in the empty lobby. Somewhere upstairs, a guest mutters and goes back to sleep.]*
    - **"You mean a lot to me, as a friend."**
      - **STU:** "[sad] Best friends. Yeah. Best friends is good. Best friends is great, actually."
      - **STU:** "[happy] Drink your cocoa. I put the little marshmallows in. The good ones."
- **STU:** "[happy] Oh! And Sara says you get a share of the tips, for all the guests you send our way. Don't tell her I said 'tips'."
- **Perk: Five-Star Partner (+20% hotel income and tips)** *(Zachary)*

---

## ♥10 Suite for Two

**Trigger:** the terminal 20:00–midnight while you're dating Stu, with him at 10 hearts.

*(Zachary's outline: with help from S.A.R.A. and Jasper, Stu sets up a private candlelit picnic, with a tiny silver hotel bell he gives you as a keepsake. The lines are Claude's.)*

- *[The terminal at night. By the airlock window, someone has laid a tablecloth on the floor, lit two candles and set out a picnic with hotel silver.]*
- *[Beyond the glass, a freighter is loading at the far pad.]*
- **STU:** "[happy] Welcome to the best suite on the station! Space view. Jasper did the food. Sara did the candles. I did the tablecloth. It's a bedsheet."
- **STU:** "This is where I used to sit with my bag. Every day off. Watching the freighters, picking which one I'd hop."
- *[The freighter's engines light. It lifts, turns, and slides away into the dark.]*
- **STU:** "[happy] There goes one. Didn't even look at it."
- **STU:** "[love] Funny. I always thought staying would feel like a trap. It feels like the opposite. Like I finally got off the ship."
- **STU:** "[bashful] This is for you. A little silver bell, like the one on the desk. Sesska made it. Ring it and I'll come running."
- *[A tiny silver bell, polished bright.]*
- **Keepsake: Stu's little silver hotel bell** *(Zachary)*

---

## Still open

- **His real name:** does the game ever give it back? His 8 says he doesn't care any more ("Being Stu is plenty"), so it can stay lost. (Optional.)
- **The brass bell:** it's on the hotel's front desk in 2 and 10. Settled 23 Nov: it's just the hotel's (S.A.R.A.'s new arc no longer gives the station a bell).
- **The Five-Star Partner perk** needs hotel income to exist first.
