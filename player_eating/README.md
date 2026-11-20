# Player eating

Copy the `player_eating` folder to the Godot 4 project root. Add `eating.tscn` at the player's foot origin. Call `play_eating(&"south", food_icon)` to use any food texture. Omitting the texture uses Ration #6. The four facings are south, north, west and east.

The player lifts the food, holds it overhead with an open mouth, brings a hand to the lips and returns to idle in 0.58 seconds. The item disappears at the bite, 0.34 seconds in. The north-facing pose shows the action from behind. The scene emits `eating_started`, `bite` and `eating_finished`. Hide the usual character renderer on start, apply the inventory effect once on bite and restore the usual renderer on finish. Concurrent play requests return false.

The scene uses the existing character creator's separate styles and tint channels. Set body_type (1 or 2), hair_style, face_style, top_style, bottom_style (zero-based 0–9), and hair_color, eye_color, skin_color, top_color, bottom_color before playing. The default is Body 1 with chestnut long hair. Each art atlas uses 48 × 68 transparent cells, anchored at (24, 63) with four direction columns. Each style occupies four successive pose rows.
