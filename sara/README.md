# S.A.R.A. hologram animation module

33 selectable clips, each 24 frames, built from 16 illustrated key poses plus baked pixel animation effects. This is a front-facing stationary hologram actor, not a four-direction walking NPC sheet. Her lower body fades into dithered light, with no feet. Body and projected objects are separate transparent PNG strips. These are shaded 2D sprites, not 3D meshes.

## Preview first

Open `SARA_Animation_Preview.html` in a browser. It works offline and lets you select all clips, pause, replay and hide object effects. The pack's root `project.godot` is a standalone Godot 4 demo. Import it as a separate project; do not overwrite your game's project.godot.

## Add to the current game

Copy `sara/` and `art/lunar/holo_dais.png` into the project's matching resource paths. Keep nearest-neighbour filtering. Instantiate `res://sara/sara_hologram.tscn`. Its origin is the projector center, and default art scale is 0.5 (the supplied Survey art contract). Adjust scale against the current NPCs if their rendering scale differs.

```gdscript
var sara = preload("res://sara/sara_hologram.tscn").instantiate()
sara.position = projector_location
# Set false before add_child if the map already has the projector art.
sara.show_projector = true
add_child(sara)
sara.play("greeting")
```

Use `play("summon_screen")`, for example, from a conversation or inspection event. `play()` returns false for an unknown name. Signals are `clip_finished(clip_name)`, `hologram_summoned(object_name)`, and `hologram_dismissed(object_name)`. Object events cover the central display interval; fading starts before the summon event and ends after dismissal. Starting another clip dismisses any active object.

Idle has occasional automatic blinking, glances and gestures. Set `automatic_idle = false` for scripted sequences. One-shot gestures return to idle. `dissolve` remains hidden; call `materialize` to return. `standby` loops dimly; call `wake` to brighten. Glitches are deliberate event animations, not constantly running idle effects.

## Clips

- Everyday: idle, blink, hair_sway, glance_left, glance_right, head_tilt, clasp_hands, stretch, greeting, explain, talk_both, nod, laugh, shrug, thinking.
- Objects: summon_screen, swipe_panels, rotate_moon, unfold_map, warning, conjure_teacup, admire_flower, paris_daydream.
- Glitches: glitch_scan, glitch_hand, glitch_echo, glitch_interrupt, glitch_recover.
- Projection: materialize, dissolve, reconnect, standby, wake.

## Asset contract

Body frames are 80 × 96; object frames are 128 × 96. Both use 24 horizontal frames, centered on the same bottom-center anchor. Body strip: 1920 × 96; object strip: 3072 × 96. `animations.json` contains FPS, loop flags and filenames. Alpha transparency and scanlines are baked into the frames. Keep the two layers at the same position; do not stretch them to the same width.

These clips use held expressive key poses, not hand-drawn in-betweens for every frame. The preview shows exactly how they play. The reusable scene includes visuals and playback; it does not install collision, interaction hotspots, dialogue triggers or map placement in the revised game. The latest full game project was not available for integration testing.

## Validation

Tested with Godot 4.6.3: import, all 33 playback clips, frame dimensions, one-shot/hidden transitions and eight paired object events. To repeat:

`godot --headless --path . --script res://sara/test_animations.gd`
