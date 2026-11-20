# Echo Landing overhead emotes

Copy `overhead_emotes` to your Godot 4 project root. Add an instance of `overhead_emote.tscn` as a child of each player or speaking NPC, at the character's foot origin. The bubble follows that character in every facing. Adjust `head_clearance` for taller actors.

For a story beat, call `$OverheadEmote.show_story(&"question", 1.8)` on the speaker. Run this cue on each peer watching a synchronized cutscene. For a player signal, call `$OverheadEmote.send_coop(&"ready")` from the local player's input. It displays above that player on connected peers. Set the player's multiplayer authority before it enters the tree and use identical player and emote node paths on all peers. Emotes also work offline. A new cue immediately replaces the previous bubble. Use `clear_emote()` to dismiss it early.

The 24 × 24 px cells in `emotes.png` run left to right through pop, rise, hold and close. Row IDs from top to bottom are shown below. Either entry point accepts every ID.

| Row | ID | Symbol |
| --- | --- | --- |
| 0 | surprise | Exclamation mark |
| 1 | question | Question mark |
| 2 | love | Heart |
| 3 | joy | Sparkle |
| 4 | sad | Tear |
| 5 | frustrated | Red stress mark |
| 6 | hello | Waving glove |
| 7 | ready | Check mark |
| 8 | no | Cross |
| 9 | wait | Hourglass |
| 10 | help | Life ring |
| 11 | follow | Double chevron |
| 12 | cute | Upright cat smile with whiskers |
