# Saffi: heart events and her week (24 Nov 2026)

**Decided with Zachary, 24 Nov:** "every character has own arc plus a short family shared arc": an arc each for Garrick, Saffi and Kit, and a two-scene family side arc ([GARRICK_SAFFI_KIT.md](GARRICK_SAFFI_KIT.md)). Claude's first suggestions for the rest, taken: **Garrick was security officer on the refugee transport that crash-landed here**, and a bounty hunter he let dock brought a Chernobog cutter down on it (so he distrusts your trade); **Perimeter Defence** is the station's guns softening up the first ship you fight on each run; **Potluck Buffs** is Saffi's Sunday potluck at the fountain; **Kit's beacon** leads to a smuggler's cache on the jump map, and **his 8 is a deputy badge** you set down at home; their weeks: the model ship and the seals on Saturdays, Saffi's Monday lunch with Rusk and the market.

**The family's story (Claude's drafts):** about forty refugees, Saffi and Kit (in a sling) among them, came down on this moon in a transport with its drive shot out, and S.A.R.A. talked them in. Every settler signed the scorched hull plate now in the museum; Kit's is a handprint. The first night, Saffi made soup for forty in a dented helmet. Most of the forty moved on later; they stayed.

**The arc:** the one who turns a station into a town, one plate at a time.
- 2: the welcome basket she's been adding to for weeks: bread, soup, socks, seeds, and everyone's birthdays.
- 4: her sign-up sheet for a Sunday potluck has one name on it. You build a town out of plates.
- 6: the scorched hull plate every settler signed, Kit's handprint, and the first night: soup for forty in a dented helmet.
- 8: the first potluck at the fountain. Jasper isn't allowed to cook and can't bear it. Every Sunday from now on.

**What's whose:** the title of 2 is the NPC Master's, and the reward (Potluck Buffs); her carrot-ginger soup is from Ana's 0; the scenes and lines are Claude's drafts. Right answers +60, middle +30, wrong −20.

**Flags:** `saffi_basket` (2), `saffi_signup` (4), `saffi_first_supper` (6), `saffi_potluck` and the perk `perk_potluck` (8).

## The potluck (her 8, Potluck Buffs)

`main.gd _potluck_talk`: from her 8 on, Saffi keeps a potluck table by the fountain on Sundays from 11:30. Talk to her there (11:00–16:00) with a cooked dish in your pack (anything the kitchenette cooks, `ShopData.COOKING`) and you can share it, once a Sunday: everyone you've met gets +20 friendship, and you wake up the next morning well fed, with 60 energy over full (`_next_day`; eating won't take the extra away). Saved as `potluck_day`. It doesn't count as one of the day's chats.

## Her week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | What she does |
|---|---|
| Monday to Saturday (unchanged) | Sweeping at home; the plaza; the fountain at lunch (Rusk comes up on Mondays); the market; home; dinner. |
| **Sunday, before her 8** | Cooking at home in the morning; the fountain; home; dinner. |
| **Sunday, after her 8** (`saffi_potluck`) | Cooking at home, then the potluck table by the fountain from 11:30 to 15:30; home; dinner. |

- **Day lines** for Monday (Rusk) and Sunday, before and after her 8 (`npc_data.gd DAY_LINES`, with `"else"`).

## In the game (24 Nov)

All four are playable cutscenes (`saffi_2` to `saffi_8`), with her new heart-event sheet (`art/npc_saffi_event.png`) and her action sheet (sweep, browse, watch). Not run in Godot yet.

- **Her 2's basket:** moon wheat bread, star tomato soup and five crater potato seeds go in your pack.
- **Letter:** the morning after 6, "The helmet soup", with two crater potatoes.

---

## ♥2 Welcome Basket

**Trigger:** Your front door, 08:00–10:30, Monday to Saturday. *(The NPC Master's title; the scene is Claude's.)*

- *[Someone is coming up the corridor to your door, carrying a basket so full the cloth on top won't lie flat.]*
- **SAFFI:** "[happy] Finally! I've been bringing you this for weeks. Then I'd add something, and it wasn't ready, so I'd add something else."
- *[Bread, still warm. A jar of soup. Spare socks. A packet of seeds. A list of everyone's birthdays, in Saffi's neat hand.]*
- *[]*
- *[]*
- *[]*
- *[+ Moon wheat bread, star tomato soup, 5 crater potato seeds]*
- **SAFFI:** "The birthdays are the important part. Nobody on this station remembers anyone's. Except Rusk, and he only remembers mine."
- **CHOICE:**
  - **"Come in for a cup of tea?"** (+High Friendship)
    - **SAFFI:** "[happy] Oh, I'd love to. I can't. Kit's got lessons and Garrick's got his socks on the wrong feet. Another day. Hold me to it."
  - **"This is too much, Saffi."** (+Friendship)
    - **SAFFI:** "[happy] It's exactly enough. That's what a welcome is for."
  - **"I don't really do soup."**
    - **SAFFI:** "[sad] ...Oh. Well. Everyone does soup eventually. I'll wait."
    - *(-20 friendship with Saffi)*
- **SAFFI:** "Garrick says you're trouble. [happy] He says that about everyone he likes. Welcome to the Landing, {name}."

---

## ♥4 Bring a Plate

**Trigger:** The market, 13:00–14:30, Monday to Friday, after 2. *(Claude)*

- *[The market after lunch. Saffi stands by the stalls with a clipboard and a pencil, and the look of someone ignored very politely all morning.]*
- **SAFFI:** "{name}! You've got a pencil hand. Sign this. It's a potluck. Sundays, at the fountain. Everyone brings one plate."
- *[The sheet has one name on it: SAFFI. Under it, very small: Kit (maybe).]*
- **SAFFI:** "[sad] Jasper says he cooks all week. Bram says he'll bring 'a surprise', which means he won't come. Garrick says he's on duty."
- **CHOICE:**
  - **"Sign it. First, in big letters."** (+High Friendship)
    - *[You write your name under hers, big enough to read from the fountain.]*
    - **SAFFI:** "[happy] Now it's a list. People sign lists. Nobody signs a sheet with one name on it."
  - **"What if the cook gets the day off?"** (+Friendship)
    - **SAFFI:** "...A potluck where Jasper isn't allowed to cook. [happy] Oh, he'd hate that. He'd come just to complain. Perfect."
  - **"Maybe people are just busy."**
    - **SAFFI:** "[sad] Everyone's busy. That's how a station stays a station and never turns into a town."
    - *(-20 friendship with Saffi)*
- **SAFFI:** "When we landed, nobody knew anybody. The first thing we did that wasn't fixing something was sit down and eat."
- **SAFFI:** "[happy] You can build a town out of plates. I've seen it done."

---

## ♥6 Every Name

**Trigger:** The museum, at the hull plate from the first crash, 14:00–16:30, Tuesday to Saturday (it shuts on Mondays), after 4. *(Claude)*

- *[The museum. Saffi stands in front of the scorched hull plate from the first crash, the one every settler signed. She hasn't seen you yet.]*
- **SAFFI:** "Oh. Hello. I come and look at this sometimes. Garrick won't. He says he remembers it fine without help."
- *[Up close, the plate is covered in names, scratched in with whatever was to hand. In one corner is a tiny handprint in grey sealant.]*
- **SAFFI:** "[happy] That's Kit. He wouldn't hold still, so S.A.R.A. said a handprint counted."
- **SAFFI:** "The first night, we had nothing. Ration bars, and a ginger root I'd carried from home in my pocket for luck."
- **SAFFI:** "S.A.R.A. found a hot plate that worked. I made soup in a dented helmet. Forty people, one helmet of soup."
- **SAFFI:** "[sad] It wasn't enough. Not nearly enough. [happy] But everyone sat down together, and that was the first night it felt like somewhere."
- **CHOICE:**
  - **"That's why the potluck matters to you."** (+High Friendship)
    - **SAFFI:** "[happy] Yes. A plate in the middle, and everyone reaching for it. That's a town."
  - **"What was in the soup?"** (+Friendship)
    - **SAFFI:** "Ginger, hope, and a ration bar crumbled in at the end. [happy] I've made it better since. Never quite as good."
  - **"Forty people on one helmet? Sounds grim."**
    - **SAFFI:** "[angry] It was grim. That was rather the point, {name}."
    - *(-20 friendship with Saffi)*
- **SAFFI:** "Come on Sunday. Bring a plate. Bring anything. [happy] Just come and sit down."
- *[The next morning: a letter (`saffi_soup`, in [MAIL.md](../MAIL.md))]*

---

## ♥8 The First Potluck

**Trigger:** The fountain, Sunday 12:00–15:00, after 6. With half the station. Reward: the potluck. *(The NPC Master's reward; the scene is Claude's.)*

- *[Sunday by the fountain. Two tables pushed together, and on them every kind of plate the Landing owns. Half the station is here. More are coming.]*
- **SAFFI:** "[happy] {name}! You came! Look at it. Fourteen names on the sheet, and nineteen people at the table."
- **JASPER:** "I brought nothing. Saffi says the cook gets the day off. [sad] I have never been so uncomfortable in my life."
- **BRAM:** "[happy] The surprise is that I came."
- **KIT:** "Dad brought a ration bar. He says it's for tradition."
- **GARRICK:** "[happy] It is for tradition."
- **SAFFI:** "Sit, sit. There's a space by Rusk. There's always a space by Rusk."
- **CHOICE:**
  - **"Sit down with everyone."** (+High Friendship)
    - *[You sit. A plate comes your way, then another. Nobody asks you to fix anything. Somebody passes you the salt.]*
  - **"Help Saffi serve first."** (+Friendship)
    - **SAFFI:** "[happy] Oh no you don't. The host serves; guests sit. ...Fine. You can carry the bread."
  - **"I'll just grab a plate and go."**
    - **SAFFI:** "[sad] Oh. Well. Take some for later, then."
    - *(-20 friendship with Saffi)*
- **SAFFI:** "Every Sunday from now on. And if you bring a plate, everyone gets a taste of it. That's the rule. The only rule."
- *[Potluck: on Sundays, bring Saffi a cooked dish at the fountain. Friendship with everyone, and you wake up well fed]*
- **RUSK:** "[happy] A toast, then. To the host."
- **GARRICK:** "[love] To the host."
