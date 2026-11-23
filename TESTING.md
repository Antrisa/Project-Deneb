# Checking this build

Run from the project folder:

```
python3 tests/check_routes.py
python3 tests/check_heart_events.py
python3 tests/check_mail.py
godot --headless --editor --import --quit
godot --headless --script res://tests/concourse_test.gd
godot --headless --script res://tests/player_art_test.gd
godot --headless --script res://tests/player_model_test.gd
godot --headless --script res://tests/walk_cycle_test.gd
godot --headless --script res://tests/social_test.gd
godot --headless --script res://tests/paving_test.gd
godot --headless --script res://tests/heart_events_test.gd
```

For a visual review, run the game and press F11 to cycle the promenade landmarks at 14:35. F10 toggles the overview. Close the overview for interaction checks. Test both sides of each entrance, chair direction, board/calendar selection and the elevator return journeys. Normal movement must not trigger the new portals automatically.

The new exterior art is a first integrated implementation of the approved moon-base layout. Other districts and room interiors have not received this art pass.
