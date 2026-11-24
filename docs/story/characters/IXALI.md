# Ix'ali: heart events, and her and Garrick's weeks (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **Ix'ali and Garrick stagger their days off**, two each, so the armoury always has one of them: Ix'ali is off **Tuesdays and Thursdays**, Garrick **Saturdays and Sundays** (with Saffi and Kit). Both have lines for their days off and for the days they cover.
- **4** moves to the museum's Precursor gallery with Tar'Besh, and **needs no item** (the script had you bring "a Zaa'sh or Terran metal artifact").
- **6** is at the mine's cavern gate in the evening, where she spars every night (the script's Shuttle Bay training mat doesn't exist). Renamed "Sparring at the Cavern Gate" (was "Sparring Under the Dome").
- **10** is in the museum after hours, in the gallery of the first settlers' Terran relics (not the Observation Lounge).

**The arc:** Junta steel, Earth chivalry: honour means protecting the weak.
- 2: Earth knights who swore to shield the weak, and a Zaa'sh armourer who wants to be one.
- 4: Sky-Weaver armour that bends instead of breaking, and why she left the Junta.
- 6: crossing blades without malice; you have a knight's spirit.
- 8: a knight offers her shield, and her heart.
- 10: a matched pair of pauldrons: not right alone.

**What's whose:** lines marked *(Zachary)* are his, from "Heart Events: All Romances": the setting and line of 2 and its choices, the setting of 4 (Ix'ali and Tar'Besh with the Sky-Weaver shard and folded lunar titanium), her line in 6 and Garrick watching, and the oath in 8. Everything else is a draft by Claude, for Zachary to change or approve: the replies to 2's choice, all the dialogue of 4 (including **one line of backstory**: she made armour on a Junta dreadnought, then left), Vzz'ket and the duel in 6, the replies to 8 (accept, decline, friendship ending), and all of 10. Long lines of his are split in two for the dialogue box. Choices give +30 (Friendship) or +60 (High Friendship).

---

## Her week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | Where she goes |
|---|---|
| Monday, Wednesday, Friday, Saturday, Sunday (unchanged) | The armoury from 06:30; dinner; sparring with Vzz'ket at the cavern gate 19:15; home 22:00. On Saturdays and Sundays she has the armoury alone. |
| Tuesday and Thursday (days off) | Breakfast 08:30; the museum's Precursor gallery with Tar'Besh 10:00; lunch; Bram's salvage 14:00; dinner; sparring at the cavern gate 19:15, as every night |

## Garrick's week

| Day | Where he goes |
|---|---|
| Monday to Friday (unchanged) | The armoury from 07:00; his midday round on the plaza; the armoury 14:00; dinner; Rusk's bar 19:15; home 21:30. On Tuesdays and Thursdays he has the armoury alone. |
| Saturday (day off) | Home with Saffi and Kit; a walk round the plaza 11:00 ("not a patrol"); lunch; the little park in the East complex 14:30; dinner; the bar |
| Sunday (day off) | Home; the plaza at noon; lunch; home; dinner; the bar |

**What they say on those days** (`scripts/npc_data.gd`, `DAY_LINES`): Ix'ali on her days off stares at old swords until Tar'Besh asks her to leave, and on Garrick's has "the whole armoury... I am being very responsible. Mostly."; Garrick on his days off is "not patrolling. I'm walking. In a circle.", and on hers "nobody's asked me to sign for a sword with a name." The station calendar lists both.

**Flags this arc sets:** `ixali_folded_titanium` (4), the perks `perk_star_knight_aegis` (6) and `perk_chivalric_guard` (8), `ixali_star_pendant` (8, either way), the keepsake `keepsake_pauldron` (10), and `partner` = Ix'ali if you accept at 8.

## In the game (23 Nov)

All five are playable cutscenes in `scripts/heart_events.gd`. She poses from her new heart-event sheet (`art/npc_ixali_event.png`) and her action sheet (polishing at the forge, her sparring stance); Tar'Besh studies; Garrick and Vzz'ket only turn and get emote bubbles. Not run in Godot yet.

- **To test:** in a debug build, **F12** plays the next event in order, **Ctrl+F12** all of them in a row (Ix'ali's 2 is the twenty-sixth press).
- **Checked offline:** `python3 tests/check_heart_events.py`.
- **In play since 24 Nov:** Chivalric Guard (a fifth less of the damage that gets through, `shops.gd damage_taken`). **Not in yet:** the Star-Knight Aegis tier, the duel itself (it plays under a fade, with hits and a shake), the pendant and pauldron as items you can hold.
- **Still open:** Decision 12: is the star pendant at 8 an Oath-Crest you could later propose with? The scene gives it either way and sets `ixali_star_pendant`. And her backstory line in 4 is a Claude placeholder.

---

## ♥2 Steel & Chivalry

**Trigger:** enter the armoury while Garrick is out (12:00–14:00 on Monday, Wednesday or Friday; 09:00–17:00 on Saturday or Sunday) with Ix'ali at 2 hearts. (Script: "the Security & Armoury forge in the East Wing".)

- *[Sparks fly from an arc-anvil. Ix'ali is hammering a curved steel plate. An open holo-book of medieval Earth knights rests on her workbench.]* *(Zachary)*
- *[Her amber eyes gleam. Her crest flares with enthusiasm.]* *(Zachary)*
- **IX'ALI** *(Zachary)*: "[happy] Look at the articulation on these 15th-century Terran gauntlets!"
- **IX'ALI** *(Zachary)*: "Back in Junta space, commanders think strength is only plasma cannons and conquest. Yet these Earth 'knights' swore oaths to shield the weak!"
- **CHOICE:**
  - **"True strength is always about who you protect."** *(Zachary)* (+High Friendship)
    - **IX'ALI:** "[surprised] ...Yes. Yes! That is exactly it. You say it like it is simple. Where I come from, it is nearly heresy."
  - **"You should forge a set of space-knight armor!"** *(Zachary)* (+Friendship)
    - **IX'ALI:** "[happy] Space-knight armour! With a cape! Garrick will say capes are a safety hazard. Garrick is wrong."
- **IX'ALI:** "[happy] Come back when you have a weapon worth looking at. Or no weapon. I will lend you one."

---

## ♥4 The Relic Blade

**Trigger:** enter the museum 10:00–12:30 on her day off (Tuesday or Thursday) with Ix'ali at 4 hearts, after Steel & Chivalry. No item needed.

- *[In the Precursor gallery, Ix'ali and Tar'Besh lean over a shard of ancient Sky-Weaver alloy, so close their crests nearly touch.]*
- **TAR'BESH:** "Careful, armourer. That shard has outlived three empires. It can outlive your enthusiasm."
- **IX'ALI:** "[happy] You came! Look at this. No, closer. Look."
- **IX'ALI:** "The Sky-Weavers folded lunar titanium over and over, hundreds of times. Thin as cloth. It bends instead of breaking. It drinks the blow."
- **TAR'BESH:** "The Junta would melt it down for hull plate. That is why it is here, and not there."
- **IX'ALI:** "[sad] ...They would."
- **IX'ALI:** "I made armour on a Junta dreadnought. Beautiful armour, for officers who never asked who it was meant to protect."
- **IX'ALI:** "One day I stopped making it. Then I stopped being there. That is the whole story. It is a short story."
- **CHOICE:**
  - **"You made the right choice."** (+High Friendship)
    - **IX'ALI:** "[bashful] Tar'Besh says the same. From two people, it is almost convincing."
  - **"What would you make with it?"** (+High Friendship)
    - **IX'ALI:** "[happy] Armour that bends. For someone who does not want to hurt anyone. That is the hardest kind to make."
- **TAR'BESH:** "[happy] Then bring me your sketches. The shard stays here. Its secret may go home with you."

---

## ♥6 Sparring at the Cavern Gate (was "Sparring Under the Dome")

**Trigger:** enter the mine 19:15–22:00 with Ix'ali at 6 hearts, after The Relic Blade.

- *[The cavern gate in the evening. Ix'ali is running through spear forms with a blunted practice blade. Vzz'ket and Garrick are watching.]*
- **IX'ALI:** "[happy] You came! Good. Vzz'ket is tired of losing to me."
- **VZZ'KET:** "I am not tired. I am bored."
- **GARRICK:** "Blunted blades. Nobody bleeds on my watch. Go on, then."
- **IX'ALI:** "[happy] In Zaa'sh tradition you bow first. Then you try very hard to knock the other person over. Ready?"
- **CHOICE:**
  - **"[Feint left, then strike]"** (+High Friendship)
    - *[You feint. She takes it, laughing, and still catches your blade on hers.]*
    - **IX'ALI:** "[surprised] A feint! Who taught you that?"
  - **"[Hold your ground]"** (+High Friendship)
    - *[She comes at you in a blur. You don't give an inch.]*
    - **IX'ALI:** "[happy] Stubborn! Good!"
- *[A fast exchange: blade on blade, sparks off the old rock, Vzz'ket hissing advice to both of you.]*
- *[Ix'ali laughs and claps your shoulder.]* *(Zachary)*
- **IX'ALI** *(Zachary)*: "[happy] Ha! Fast footwork for a soft-skinned Terran!"
- **IX'ALI** *(Zachary)*: "In Zaa'sh tradition, crossing blades without malice is how warriors prove trust. You have a knight's spirit."
- **GARRICK:** "[happy] Not bad. Not bad at all."
- **IX'ALI:** "[happy] And now, with what Tar'Besh showed me, I can make you something. Folded plate. Star-Knight armour."
- **New: the Star-Knight Aegis armour tier (Ix'ali can forge it)**
- **The next morning** *(Claude, 23 Nov)***:** a letter from Ix'ali, "The book of bouts" (`ixali_bout` in `scripts/mail_data.gd`). The text is in [MAIL.md](../MAIL.md).

---

## ♥8 The Oath (confession)

**Trigger:** enter the armoury 21:30–24:00 with Ix'ali at 8 hearts.

- *[The armoury is dark except for the forge, its embers glowing softly. Ix'ali turns something small over in her hands.]*
- **IX'ALI:** "[surprised] Oh! It is late. You came anyway. Good. I need... a witness. No. Not a witness. You."
- **If you are dating someone else (the friendship ending):**
  - *[She holds out a hand-forged pendant shaped like a cresting star.]*
  - **IX'ALI:** "[happy] For the one who taught me what a knight is for. As my friend. My sworn friend."
  - **IX'ALI:** "In the old tales, knights swore to their companions too. Consider it sworn."
- **Otherwise:**
  - *[She drops onto one knee, earnest and a little formal, her scales warm. In her hand is a hand-forged pendant shaped like a cresting star.]* *(Zachary)*
  - **IX'ALI** *(Zachary)*: "In the old Terran tales, a knight offers their shield to the one who holds their heart."
  - **IX'ALI** *(Zachary)*: "I am no longer a soldier of the Junta—I am Ix'ali of Echo Landing."
  - **IX'ALI** *(Zachary)*: "[love] And if you will have me... my shield, and my heart, are yours."
  - **CHOICE:**
    - **"I will. Shield and heart."**
      - *(Ix'ali is now your partner.)*
      - **IX'ALI:** "[surprised] You... will? Truly?"
      - **IX'ALI:** "[happy] Then I swear it. By the forge, by the old tales, and by my spear's name, which I will tell you. Later. Privately."
      - *[The forge burns down to embers. Neither of you notices.]*
    - **"You mean a lot to me, as a friend."**
      - **IX'ALI:** "[sad] I understand. A knight asks once, and honours the answer."
      - **IX'ALI:** "[happy] My shield is still yours, as a friend. That part was never a question."
- **IX'ALI:** "[happy] And from now on, you are not walking into those tunnels without proper plate. I will see to it."
- **Perk: Chivalric Guard (take 20% less damage)**

---

## ♥10 Forged in Starlight

**Trigger:** enter the museum 20:00–24:00 while you're dating Ix'ali, with her at 10 hearts.

- *[The museum after hours. The lights are low over the gallery of the first settlers, where the oldest Terran relics sleep in their cases.]*
- *[A note is pinned to the door in Tar'Besh's careful hand: CLOSED. FOR MOST PEOPLE.]*
- **IX'ALI:** "[happy] You found the note. Tar'Besh writes notes like a poet. A very grumpy poet."
- *[On a stand between the cases sit two ceremonial pauldrons of starlight-silver, each etched with a cresting star.]*
- **IX'ALI:** "Folded lunar titanium, the Sky-Weaver way. I made two. They are a pair. They are not right alone."
- **IX'ALI:** "[love] The old knights wore the colours of the one they loved. I wanted us to wear each other's."
- **IX'ALI:** "[bashful] This one is yours. It bends instead of breaking. Like us, I think. I am not good at speeches. I am good at armour."
- *[The pauldron is lighter than it looks, and still warm from the forge.]*
- **Keepsake: Ix'ali's ceremonial pauldron**
