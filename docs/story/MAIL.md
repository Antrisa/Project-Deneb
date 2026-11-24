# Letters from the residents (23 Nov 2026)

Zachary added a mailbox, the message pad by your front door on the agri complex's porch, so that residents can send you mail and gifts, as in Stardew Valley. Then he asked: "if it makes sense in any of the previous arcs add and next morning get mail from the person or gifts. and keep in mind for future arcs."

So sixteen heart events now send a letter that comes with the next morning's post, and five of the letters have a gift in them. Bram's arc (written the same day, after the rule) added one more, with a gift, Tikka & Sesska's (24 Nov) three more, two with gifts, Maren, Owen & Pip's (24 Nov) four more, one with a gift, Tobbin, Merrow & Nub's (24 Nov) four more, three with gifts, and Garrick, Saffi & Kit's (24 Nov) four more, two with gifts: thirty-two in all. The wording is a first draft by Claude, for Zachary to change: the letters live in `scripts/mail_data.gd`.

## How it works

- **Your name:** `{name}` in a letter (or any line of dialogue) becomes the name you gave your character, or Pilot (upstream, 24 Nov).

- **Sending:** a heart event sends a letter with a `["mail", id, days]` step (`scripts/cutscene.gd`), which calls `main.gd send_mail(id, days)`. `days` 1 is the next morning. A letter only ever comes once, however often the event plays (F3).
- **A letter sent from inside a choice** only comes if you made that choice. Six do this: Zaas writes after Job's 4 only if you dug out his crate, Tar'Besh writes after his 4 only if you told him he lived anyway, Freya writes after Tikka's 4 only if you let her take the lamp, Sesska's cap after her 2 doesn't come if you told her it was only a jacket, Maren's after her 4 not if you told her it was only tea, and Pip's geode after his 4 not if you told him finders keepers. Missing a letter is the minor consequence.
- **Gifts:** a letter's optional `"gift": {item: count}` goes in your pack the first time you open it (`main.gd read_letter`), with a toast ("In the envelope: Medpack x2"). The letter shows it along the foot of its page: ENCLOSED, the item's picture and count, and IN YOUR PACK (`scripts/mail_reader.gd _paint_gift`). Gifts are small and use items that already exist (Tobbin's planks are the one new item: his shop sells them too).
- **Fitting the page:** `python3 tests/check_mail.py` measures every letter with the datapad font's own widths at the smallest page (768 x 432), with room left for a gift. It also checks that every gift is an item, that every letter is sent by something and that letters use only plain ASCII (the datapad font has no curly quotes, long dashes or accents: Cafe, not Café). `-v` shows how much room each letter has left.
- **The Godot test** (`tests/heart_events_test.gd`) checks that every event sent its letter, that they all come with the next morning's post, and that Quill's medpacks come once.
- Not run in Godot yet.

## For future arcs

When writing a new arc, look for one event that would naturally leave something behind the next morning, and send a letter from it:

- a thank-you after the player helped with something practical;
- a recipe, a method or a tip the resident promised in the scene (Job's gumbo, Rusk's grape-growing);
- a few seeds or one small useful item, when it fits the person (Evarra's tomato seeds, Quill's medpacks);
- someone else's view of a big moment (Tikka after Freya's test flight, Merrow after Zaas's first splash);
- the morning after, when the scene ended on a change (Vzz'ket's first night's sleep).

About one letter per arc, rarely two. A gift shouldn't repeat the event's own perk or keepsake. Keep a letter to about four short paragraphs, and a little shorter with a gift. Each character doc notes its letters under the event that sends them.

## The letters

| Event | Letter | From | Title | Gift |
|---|---|---|---|---|
| Freya 2, The Stubborn Heating Pump | `freya_pump` | Freya | Two-person job | Copper bar x2 |
| Freya 6, Test Flight | `tikka_test_flight` | Tikka | A better memory | - |
| Jasper 2, The Butter Tin | `jasper_wheat` | Jasper | For the croissants | Moon wheat seeds x5 |
| Evarra 2, The Window-Box Herb | `evarra_lavender` | Evarra | Something that grows | Star tomato seeds x3 |
| Job 2, Gumbo in the Breakroom | `job_gumbo` | Job | Mama's gumbo | - |
| Job 4, Cave-In on Shaft Four | `zaas_hydrophones` | Zaas | Still listening | - |
| Quill 2, The Spilled Apothecary | `quill_spores` | Quill | Do not tell Maren | Medpack x2 |
| Ix'ali 6, Sparring at the Cavern Gate | `ixali_bout` | Ix'ali | The book of bouts | - |
| Artie 4, The Junior Scouts | `scouts_knots` | The Junior Scouts | From the Junior Scouts | Quartz x1 |
| Stu 6, A Name on the Door | `stu_address` | Stu | My own address | - |
| Ana 2, A Seat at the Table | `ana_seat` | Ana | The seat | - |
| S.A.R.A. 6, Walkabout | `sara_walk` | S.A.R.A. | Something to hold | - |
| Tar'Besh 4, Next Assignment | `tarbesh_letter` | Tar'Besh | A better letter | - |
| Zaas 6, First Splash | `merrow_plaque` | Merrow | About the plaque | - |
| Vzz'ket 8, The Watch Changes | `vzzket_sleep` | Vzz'ket | The box chirped | - |
| Rusk 8, The First Page | `rusk_ilsa_vine` | Rusk | How Ilsa grew them | - |
| Bram 4, Quiet Credit | `bram_seeds` | Bram | You heard nothing | Crater potato seeds x5 |
| Tikka 4, The Kettle Queue | `freya_lamp` | Freya | She let me | - |
| Sesska 2, Every Seam Giving Up | `sesska_offcuts` | Sesska | Offcuts | Knit cap x1 |
| Tikka & Sesska 6, The Anniversary | `forty_years` | Tikka and Sesska | Forty years and a day | Coil wire x2 |
| Maren 4, A Hot Cup of Tea | `maren_tea` | Maren | Hot tea | - |
| Owen 4, The Freighter Log | `owen_recorder` | Owen | Good company | - |
| Pip 4, Lost and Found | `pip_found` | Pip | Found it | Geode x1 |
| Maren, Owen & Pip 6, Lanterns | `pip_lanterns` | Pip | Green stars | - |
| Tobbin 4, First Real Wood | `tobbin_planks` | Tobbin | Two planks | Real wood plank x2 |
| Merrow 4, Star-Tomatoes | `merrow_seeds` | Merrow | For your beds | Star tomato seeds x6 |
| Nub 6, Junior Curator | `nub_curator` | Nub | JUNIOR CURATOR | Chitin x1 |
| Tobbin, Merrow & Nub 6, The First Tree | `moogli_tree` | Merrow | Tree | - |
| Garrick 4, The Rounds | `garrick_issue` | Garrick | Quartermaster's issue | Medpack x1 |
| Saffi 6, Every Name | `saffi_soup` | Saffi | The helmet soup | Crater potato x2 |
| Kit 4, The Beacon | `kit_coordinates` | Kit | THE BEACON | - |
| Garrick, Saffi & Kit 6, Brave Together | `guard_double` | Saffi | Double | - |
| The museum, 5 relics given | `tarbesh_museum_5` | Tar'Besh | Five cases | Cavern geode x3 |
| The museum, 10 relics given | `tarbesh_museum_10` | Tar'Besh | Ten | Void sapphire |

Upstream's own letters are unchanged: S.A.R.A.'s welcome (day 1), Vzz'ket's "The gate" (when Job's north tunnels are done), and S.A.R.A.'s notes on the storage dome and the fish ponds.

### Two-person job (`freya_pump`): after Freya's 2, The Stubborn Heating Pump

*From Freya, the next morning. Enclosed: Copper bar x2.*

> Boss!
>
> Sector Three's been warm all night. Garrick took his coat off on watch. First time all season, he says.
>
> Found these in Dad's offcut bin. He always said good copper's wasted sitting in a bin, so they're yours. Make something that turns.
>
> - Freya

### A better memory (`tikka_test_flight`): after Freya's 6, Test Flight

*From Tikka, the next morning.*

> Pilot,
>
> Since Jorvik's last run, every launch I've called has sounded like that one to me. Right up until the shaking.
>
> Last night one went right. A clean note, all the way out past the doors. I'm keeping that one instead.
>
> Thank you for easing off. And for taking her with you. Bring her back in one piece. The ship too, if you can manage both.
>
> - Tikka, launch control

### For the croissants (`jasper_wheat`): after Jasper's 2, The Butter Tin

*From Jasper, the next morning. Enclosed: Moon wheat seeds x5.*

> Mon ami,
>
> Madame Ooma has my Scrip and my button, and I have one season. But a croissant is only as good as its flour, and the flour on the supply run tastes of the crate it came in.
>
> So, enclosed: moon wheat, from Evarra's seed drawer. She says it wants water and patience. I have neither. You have a field.
>
> - Jasper

### Something that grows (`evarra_lavender`): after Evarra's 2, The Window-Box Herb

*From Evarra, the next morning. Enclosed: Star tomato seeds x3.*

> Dear neighbour,
>
> The seed bank won't part with lavender. I asked nicely, then S.A.R.A. asked even more nicely, and it still said no.
>
> So here are star tomatoes. They aren't flowers, but they're stubborn and they love a grow-lamp. A farm has to start with something that wants to grow.
>
> - Evarra

### Mama's gumbo (`job_gumbo`): after Job's 2, Gumbo in the Breakroom

*From Job, the next morning.*

> Cher,
>
> Wrote it down for you, near as I can. First, the roux: flour and oil, low heat, and stir till it's the colour of an old penny. Don't walk away. Don't you dare walk away.
>
> Then the holy trinity: onion, pepper, celery, whatever the hydroponics will spare. Then the spice. The spice I can't write down. It's in a tin, and the tin's mine.
>
> Bring a bowl to the breakroom any day after four. There's always a pot.
>
> - Job

### Still listening (`zaas_hydrophones`): after Job's 4, Cave-In on Shaft Four

*From Zaas, the next morning. Only if you picked "[Dig out the crate]".*

> To the one who dug,
>
> My hydrophones survived. Two dents and a great deal of shale, which I have been picking out with tweezers all night. Merrow says I am being sentimental. I am.
>
> I put them back on the rock to be sure they work. They do. And far down under the rock, there is still that sound. Water, moving.
>
> I will tell you about it one day, when I am sure.
>
> - Zaas

### Do not tell Maren (`quill_spores`): after Quill's 2, The Spilled Apothecary

*From Quill, the next morning. Enclosed: Medpack x2.*

> Dear friend,
>
> Thank you for not stepping in the spores. Only three vials were lost, which by my standards is a triumph.
>
> Enclosed: two medpacks, made by my own hands, which were steady the entire time. Please take them into the mine. Please do not need them.
>
> P.S. Maren found a glowing spot under the bench. I said it was a reflection.
>
> - Quill

### The book of bouts (`ixali_bout`): after Ix'ali's 6, Sparring at the Cavern Gate

*From Ix'ali, the next morning.*

> Honoured friend,
>
> The armoury keeps a book of every bout fought at the cavern gate since the gate was built. Last night I wrote ours in it.
>
> Yours is the first Terran name in the book. Garrick says my handwriting is too large. I say a first deserves large handwriting.
>
> Come to the armoury when you are ready. I have taken your measure, and the Aegis plate will not fold itself.
>
> - Ix'ali

### From the Junior Scouts (`scouts_knots`): after Artie's 4, The Junior Scouts

*From The Junior Scouts, the next morning. Enclosed: Quartz x1.*

> We practised the square knot 100 times. Kit says 200. Kit is wrong. - Pip
>
> Mine is better than Pip's now. We found a shiny rock by the fountain and voted you get it. - Kit
>
> NUB TIED THE ENVELOPE. NUB'S IS A REAL KNOT. - Nub
>
> - The Junior Scouts

### My own address (`stu_address`): after Stu's 6, A Name on the Door

*From Stu, the next morning.*

> Hi!
>
> This is the first letter I've ever sent. I didn't know who to send it to, and then I did.
>
> It's from East Home 2. That's me. I'm writing it at my own table, and I've been grinning at the return address for ten minutes.
>
> The U is still on. Tobbin came back after dark to check it anyway.
>
> - Stu

### The seat (`ana_seat`): after Ana's 2, A Seat at the Table

*From Ana, the next morning.*

> I don't write letters. Ivan read everything that came aboard, so nobody did.
>
> But you sat down. In front of everyone. You knew what it would cost you, and you did it anyway.
>
> On the way out, two more people nodded at me. I counted.
>
> That's all. Thank you.
>
> - Ana

### Something to hold (`sara_walk`): after S.A.R.A.'s 6, Walkabout

*From S.A.R.A., the next morning.*

> Good morning.
>
> I had my drones bring this, instead of saying it from a pad. A letter is something you can hold, and I wanted you to have something to hold.
>
> Last night I looked at the fountain from my usual camera. It is the same fountain. It looks different now that I have stood beside it.
>
> I am keeping a list of places to go. It is short. I am in no hurry.
>
> - S.A.R.A.

### A better letter (`tarbesh_letter`): after Tar'Besh's 4, Next Assignment

*From Tar'Besh, the next morning. Only if you picked "They meant you to die. You lived anyway."*

> Friend,
>
> The last letter I was sent told me where to go, and how long the rations would last. I keep it among the candles, so I will not forget it.
>
> It seemed to me tonight that a man should own at least one better letter. So I am writing one, to someone who listened.
>
> Out of spite, then out of habit. I have decided that is a respectable reason to be alive.
>
> - Tar'Besh, well fed

### About the plaque (`merrow_plaque`): after Zaas's 6, First Splash

*From Merrow, the next morning.*

> Tar'Besh put the plaque up on the shore last night. THE MERROW DEEP, in letters you can read from across the water. I asked him to take it down. He said a plaque is a prayer that stays put.
>
> The chief was in the water until dark. I keep every drop on this station clean, and he floated on his back in it, singing.
>
> Thank you for being there when he went in. Somebody had to see it who wasn't me. Don't tell him I wrote.
>
> - Merrow

### The box chirped (`vzzket_sleep`): after Vzz'ket's 8, The Watch Changes

*From Vzz'ket, the next morning.*

> Pilot.
>
> The machine's box chirped in the night. A rock-crawler, on the third landing. She told me what and where. I went down. It was.
>
> I went back to my bedroll. It chirped once more before morning. I did not get up. S.A.R.A. says that is the point.
>
> I slept until Tikka's drill woke me. Tell no one.
>
> - Vzz'ket

### How Ilsa grew them (`rusk_ilsa_vine`): after Rusk's 8, The First Page

*From Rusk, the next morning.*

> Pilot,
>
> Ilsa wrote this on the back of a menu. I'll keep the menu.
>
> Dig a bed or set down a hydroponic one, and keep it watered. Eight days to the first bunch, then a bunch every three days while you tend it. Plant a bunch and it grows you another vine.
>
> Bring me five and I'll fill the cask. Three days, and you've a bottle of Nebula wine. Ship it: Bram's cousins pay what it's worth, and it's worth a lot.
>
> - Rusk

### You heard nothing (`bram_seeds`): after Bram's 4, Quiet Credit

*From Bram, the next morning. Enclosed: Crater potato seeds x5.*

> Friend.
>
> About this morning. You heard nothing. I said nothing. The freighter flew, and that is the end of the matter.
>
> Enclosed: crater potato seeds. They were going stale. This is not generosity. This is stock control.
>
> Do not tell anyone about the seeds either.
>
> - Bram Ollo

### She let me (`freya_lamp`): after Tikka's 4, The Kettle Queue

*From Freya, the next morning. Only if you picked "Let her. You taught her, didn't you?"*

> Boss!
>
> Owen's lamp still works. I checked it this morning. Don't tell Tikka I checked it. She'd be so proud, and then she'd check it too.
>
> She watched me do a whole repair and only said 'hm' once. Once! I'm painting it on the bay wall.
>
> Thanks for saying it. I couldn't have.
>
> - Freya

### Offcuts (`sesska_offcuts`): after Sesska's 2, Every Seam Giving Up

*From Sesska, the next morning. Enclosed: Knit cap x1. Not if you told her it was only a jacket.*

> Dear {name},
>
> There were offcuts from your jacket. There are always offcuts. Offcuts become caps.
>
> I guessed the size of your head. My guesses are good. If it doesn't fit, your head is wrong.
>
> - Sesska

### Forty years and a day (`forty_years`): after Tikka & Sesska's 6, The Anniversary

*From both of them, the next morning. Enclosed: Coil wire x2.*

> {name},
>
> The music box played all night. Tikka checked it twice, then a third time, and then I hid it. - S.
>
> Enclosed, the highest honour I give: coil wire. Sesska says this is not how thanks work. Sesska is wrong. - T.
>
> - Tikka and Sesska

### Hot tea (`maren_tea`): after Maren's 4, A Hot Cup of Tea

*From Maren, the next morning. Not if you told her it was only tea.*

> {name},
>
> Thirty-one minutes of quiet. I timed it. The tea was hot the whole way down.
>
> Pip says you turned him round 'like a door'. He wants to know how you did it. I've told him it's a doctor's secret.
>
> - Maren

### Good company (`owen_recorder`): after Owen's 4, The Freighter Log

*From Owen, the next morning.*

> {name},
>
> I've put the recorder in the drawer with Tam's first school report and Ines's flight licence. It seemed like the right company.
>
> I listened once more, alone, for the green stars. Then I closed the drawer. That was enough for now.
>
> Thank you for staying.
>
> - Owen

### Found it (`pip_found`): after Pip's 4, Lost and Found

*From Pip, the next morning. Enclosed: Geode x1. Not if you told him finders keepers.*

> Dear {name},
>
> I found this by the bins. It's a geode. Job says you crack them. I didn't crack it. I thought you should.
>
> Finders keepers is a real rule. But Gran says giving things away is a better rule.
>
> - Pip (age 9)

### Green stars (`pip_lanterns`): after Maren, Owen & Pip's 6, Lanterns

*From Pip, the next morning.*

> Dear {name},
>
> Grandad played me the message. Dad sounds like Grandad but younger. Gran cried and then she laughed and then she made toast.
>
> I'm going to be a pilot and check the drive every time. You can come too. You can check it as well.
>
> - Pip

### Two planks (`tobbin_planks`): after Tobbin's 4, First Real Wood

*From Tobbin, the next morning. Enclosed: Real wood plank x2.*

> {name},
>
> The limb is drying in my workshop, and the whole shop smells like a forest. Nub says it smells like 'outside'. He's never been outside.
>
> Two planks from the first cut. Not for selling: for making something badly, the way everyone starts. Mind the grain. It goes where it wants.
>
> - Tobbin

### For your beds (`merrow_seeds`): after Merrow's 4, Star-Tomatoes

*From Merrow, the next morning. Enclosed: Star tomato seeds x6.*

> {name},
>
> Seeds from the scrubber corner. They grew on a cup of water a day and a borrowed socket, so a proper bed will spoil them rotten.
>
> Put this letter in the recycler when you've read it. It all comes through my fountain in the end, so I'll know.
>
> - Merrow

### JUNIOR CURATOR (`nub_curator`): after Nub's 6, Junior Curator

*From Nub, the next morning. Enclosed: Chitin x1 (a bug shell).*

> Dear {name},
>
> I am a JUNIOR CURATOR. Mr Tar'Besh gave me pins. Pins are better than tape but you can't put them in your mouth.
>
> This is a bug shell. It's for your museum. You haven't got a museum, so this is the first thing in it.
>
> - Nub (Junior Curator)

### Tree (`moogli_tree`): after Tobbin, Merrow & Nub's 6, The First Tree

*From Merrow, for all three, the next morning.*

> {name},
>
> Tree has a third leaf. Nub announced it at breakfast like a birth. Tobbin cried into his porridge, which he says was steam.
>
> Thank you for being there. A family's first tree needs witnesses.
>
> - Merrow, Tobbin and Nub (and Tree)

### Quartermaster's issue (`garrick_issue`): after Garrick's 4, The Rounds

*From Garrick, the next morning. Enclosed: Medpack x1.*

> {name},
>
> Signed out to you from stores: one medpack. You'll need it more than the shelf does.
>
> Same time tonight. Bring your own lamp.
>
> - G.

### The helmet soup (`saffi_soup`): after Saffi's 6, Every Name

*From Saffi, the next morning. Enclosed: Crater potato x2.*

> {name},
>
> One ginger root, two potatoes, a ration bar, and forty people. I've sent the potatoes. You bring the people.
>
> Sunday, at the fountain. I'm keeping you a seat by Rusk.
>
> - Saffi

### THE BEACON (`kit_coordinates`): after Kit's 4, The Beacon

*From Kit, the next morning.*

> Dear {name},
>
> Three long. Two short. Every night at 19:40. Mum helped me work out where: it's on the second ring, near the Reach.
>
> Take your ship. Bring me something back. Not treasure. Well. Treasure if there's treasure.
>
> - Kit (security chief, nearly)

### Double (`guard_double`): after Garrick, Saffi & Kit's 6, Brave Together

*From Saffi, for all three, the next morning.*

> {name},
>
> Kit is grounded until he's forty. Garrick says thirty. We've settled on Tuesday.
>
> Thank you for coming. And thank Vzz'ket for us again, if he'll let you. He won't let us.
>
> - Saffi, Garrick and Kit

## The museum's thanks (24 Nov)

Zachary: "every 5 relics you get something for donations." Not heart events: `main.gd _museum_thanks` sends these when the 5th and 10th relics go into the museum's cases (Tar'Besh also pays 250 and 500 Scrip there and then, a quarter more with his 8's Relic Appraisal; from 15 relics on, 50 Scrip a relic and no letter yet). Each comes once, even if you take a relic back out.

### Five cases (`tarbesh_museum_5`)

*From Tar'Besh, the morning after the fifth relic. In the envelope: three cavern geodes.*

> Friend,
>
> Five cases that were empty are not empty. I have stood in front of each one longer than a curator should admit.
>
> A museum is a promise that somebody will remember. You are keeping it for people you never met.
>
> Job says the caverns keep their best things wrapped in rock. Here are three. Take them to his bench.
>
> - Tar'Besh, curator

### Ten (`tarbesh_museum_10`)

*From Tar'Besh, the morning after the tenth relic. In the envelope: a void sapphire.*

> Friend,
>
> Ten. The children have begun arguing about which case is best. That is how you know a museum is alive.
>
> This sapphire came to me my first year here, in a pilgrim's offering bowl. I never knew what it was for. Now I do.
>
> Keep looking. The cases are patient, and so am I.
>
> - Tar'Besh
