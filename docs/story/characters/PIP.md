# Pip: heart events and his week (24 Nov 2026)

**The family's story (Zachary, 24 Nov):** Pip's parents are dead. Their freighter's drive failed between stations in the Neutral Zone three years ago: "nobodys fault bad things happen somtimes." Pip knows they died, but not how. *(Claude's placeholders: his father is Maren and Owen's son **Tam**, his mother **Ines**, a pilot; the ship was the **Kestrel**; Pip was with his grandparents for that one run; Maren and Owen brought him to the Landing afterwards, for somewhere quiet, which is why the doctor "came here to retire".)* This replaces the old outline, where his parents were alive in Collective space (thread C, Decision 7).

**Decided with Zachary, 24 Nov:** an arc each, and a family side arc ([MAREN_OWEN_PIP.md](MAREN_OWEN_PIP.md)). His 8's reward (Zachary): **a toy rocketship, a piece of furniture**.

**The arc:** nine, knows where everything is, and is going to be a pilot.
- 2: up the archive shelves after closing, looking for the Kestrel in the ship register. He knows they died, not how. "Nine is older."
- 4: his secret Lost and Found (Quill's six tongue depressors, Jorvik's spanner, Tobbin's U), given back.
- 6: in your cockpit: Mum was a pilot, Dad fixed things, and he'll check the drive every single time.
- 8: a toy rocketship he made for your room, "so you remember to come back". CHECKED TWICE.

His first line already says "Gran says I can't ask if there was fire." It now means something, with no change to the line.

**What's whose:** the title of 2 is the NPC Master's; the reward and the background are Zachary's; the scenes and lines are Claude's drafts. Right answers +60, middle +30, wrong −20 (and in 4 the letter).

**Flags:** `pip_archive` (2), `pip_lost_and_found` (4), `pip_cockpit` (6), `pip_rocket` (8).

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | What he does |
|---|---|
| Weekdays (unchanged) | Lessons in the library, the plaza, the Medbay, holo-games, dinner, home by nine. Monday afternoons with the Scouts once Artie starts them. |
| **Saturday, before Maren's 6** | With Owen: breakfast, the West Terminal's star dome, the fountain, dinner, home. |
| **Saturday, after Maren's 6** (`maren_lets_go`) | His own: the star dome's telescope in the morning, then the Shuttle Bay's launch booth, where Tikka lets him watch. |
| First Saturday of a season | The Scouts' outing, as before (it wins over the two above). |

- **Day lines** for Saturday, before and after Maren lets him go (`npc_data.gd DAY_LINES`, with `"else"`).

## In the game (24 Nov)

All four are playable cutscenes (`pip_2` to `pip_8`), with his new heart-event sheet (`art/npc_pip_event.png`) and his action sheet (study, play). Not run in Godot yet.

- **Pip's toy rocket** (`toy_rocket`, icon 122, prop `art/lunar/toy_rocket.png`, both stand-ins by Claude): you set it down at home from the hotbar like a storage chest (`main.gd PLACEABLE`, a new `"decor"` kind: using it shows its description, and you can pick it up again).
- **Letter:** the morning after 4, "Found it", with a geode (not if you told him finders keepers).

---

## ♥2 Pip in the Archive

**Trigger:** The library after closing, 19:30–20:45. Owen comes to fetch him. *(The NPC Master's title; the scene is Claude's.)*

- *[The library after closing. The lights are low. Up in the top corner, the shelves Owen calls the archive, something small is rustling.]*
- **PIP:** "[surprised] It's you! Phew. I thought you were Grandad. Don't tell Grandad."
- **PIP:** "I'm looking for the ship register. Mum and Dad's ship was called the Kestrel. It'll say what happened."
- **PIP:** "[sad] I know they died. Everyone thinks I don't know things. I just don't know how. Gran and Grandad say 'when you're older'."
- **PIP:** "I'm nine. Nine is older."
- **CHOICE:**
  - **"Then ask them. Tell them nine is older."** (+High Friendship)
    - **PIP:** "...Ask them? Like, with words? [sad] ...Okay. Not tonight. Maybe soon."
  - **"I'll help you look."** (+Friendship)
    - *[You find the register. Under KESTREL there is one line: LOST, NEUTRAL ZONE. Nothing else.]*
    - **PIP:** "[sad] ...I knew that bit."
  - **"You shouldn't be up here. Bed."**
    - **PIP:** "[angry] Everybody says that."
    - *(-20 friendship with Pip)*
- **OWEN:** "Pip. Bed. ...Gently, I mean. Bed, gently."
- **OWEN:** "[sad] Thank you for being kind to him. He's been up there every night this week. I've been pretending not to notice."

---

## ♥4 Lost and Found

**Trigger:** The fountain plaza after lessons, 15:00–17:30, Monday to Friday, after 2. With Quill. *(Claude)*

- *[The fountain plaza. Pip is waiting for you behind a bench, with a crate he can barely carry and an expression of enormous secrecy.]*
- **PIP:** "[happy] This is my Lost and Found. Mostly Found. People drop things. I know where everything is, so I find them."
- *[Inside: six tongue depressors, a spanner with JORVIK scratched on the handle, a whetstone, a brass button and one very small wooden U.]*
- **PIP:** "[sad] I meant to give them back. Then I'd kept them too long, and now it's stealing. Quill's going to know it was me."
- **CHOICE:**
  - **"We'll give them back together. Quill first."** (+High Friendship)
    - **PIP:** "[sad] ...These are yours. I was keeping them safe. For a really long time."
    - **QUILL:** "[surprised] My tongue depressors! All six!"
    - **QUILL:** "[happy] ...Thank you for keeping them safe, Pip. Nobody's ever kept anything safe for me before."
    - *[The rest of the afternoon goes the same way. The spanner goes to Freya, who goes very quiet and then hugs him.]*
    - *[The whetstone goes to Ix'ali. Tobbin is delighted to have his U back.]*
  - **"Put them back where you found them. Nobody will know."** (+Friendship)
    - *[You spend the afternoon sneaking things back where they belong. It's harder than it sounds. Quill finds his tongue depressors and looks very confused.]*
  - **"Finders keepers."**
    - **PIP:** "[sad] ...That's what I thought too. It doesn't feel very good, though."
    - *(-20 friendship with Pip)*
- *[The next morning: a letter (`pip_found`, in [MAIL.md](../MAIL.md))]*

---

## ♥6 Except Mine Will Work

**Trigger:** The Shuttle Bay, Saturday 10:00–12:30 (with Owen), after 4. *(Claude)*

- *[The Shuttle Bay on a Saturday. Owen has brought Pip to see the ships, and is pretending to read by the door. Pip is staring up at yours.]*
- **PIP:** "[happy] Can I sit in it? Just sit. I won't touch anything. I'll touch one thing."
- *[You help him up into the cockpit. He sits in the pilot's seat with both hands flat on his knees, very carefully not touching anything.]*
- **PIP:** "[happy] It smells like Freya's bench. ...Mum was a pilot. Dad fixed things. Gran says I've got both kinds of hands."
- **PIP:** "[sad] It was the drive. I know that much. Kids hear things, even when grown-ups whisper."
- **PIP:** "When I grow up I'm going to have a ship like yours. Except mine will work. ...And I'm going to check the drive. Every single time."
- **CHOICE:**
  - **"Then you'll be a good pilot. The best ones check twice."** (+High Friendship)
    - **PIP:** "[happy] Twice! Tikka says three times. I'll do four."
  - **"Want to learn the pre-flight checklist?"** (+High Friendship)
    - *[You walk him through it, switch by switch, without turning anything on. He gets every one right on the second go.]*
    - **PIP:** "[happy] Fuel, seals, drive, nav, comms. Drive twice."
  - **"Maybe stay on the ground. Ships are dangerous."**
    - **PIP:** "[angry] That's what Gran says. Gran's wrong. Mostly wrong. A bit wrong."
    - *(-20 friendship with Pip)*
- **OWEN:** "[happy] Lunch, Captain. Your grandmother has opinions about lunch."

---

## ♥8 Checked Twice

**Trigger:** Your front door, Saturday or Sunday 08:00–11:00, after 6. Owen watches from the corridor. Reward: Pip's toy rocket. *(Zachary's reward; the scene is Claude's.)*

- *[Your front door, at the weekend. Pip is waiting on the porch, holding something behind his back with both hands.]*
- *[Down by the corridor, Owen is pretending to read the shipping crate.]*
- **PIP:** "[happy] I came by myself! Grandad only walked me to the corridor. That counts as by myself."
- **PIP:** "I made you something. Tobbin gave me the offcuts, Tikka gave me coil, and Sesska sewed the flags. I did everything else. Mostly."
- *[A toy rocketship, nearly as tall as Pip's arm: a tin nose, a red wooden body and coil-wire fins. On the side, in careful letters: CHECKED TWICE.]*
- *[+ Pip's toy rocket (set it down at home, like a chest)]*
- **PIP:** "It's for your room. So you remember to come back. Everyone has to come back. That's the rule."
- **CHOICE:**
  - **"I'll always come back. That's a promise."** (+High Friendship)
    - **PIP:** "[happy] Good. I'll check."
  - **"It's the best ship I've ever seen."** (+High Friendship)
    - **PIP:** "[happy] Better than yours?"
    - *[You consider your own ship, and all its repairs.]*
    - **PIP:** "[happy] I knew it."
  - **"Did you really make this yourself?"**
    - **PIP:** "[angry] Mostly! I said mostly!"
    - *(-20 friendship with Pip)*
