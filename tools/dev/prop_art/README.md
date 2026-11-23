# Prop art scripts (23 Nov 2026)

Drawn by Claude in code, in the warm "C" style Zachary chose: hue-shifted ramps (warm highlights, purple shadows),
faces lit along the top and darker toward the bottom and right, bevelled panels, straps and seams, a warm dark outline.
Each script writes into `<repo>/art/...` at the same sizes as the pieces it replaced.

- `home_machines.py <repo>`: home electric furnace (cold + 3 lit frames + glow), manufacturing hub, storage chest; also
  `beacon()` / `beacon_strip()` for the spaceport comms mast. Holds the shared palettes and helpers (`face`, `seam`, `bar_v`).
- `props_redo.py <repo> [names]`: street furniture, tables, Engineering furnace (8 frames + glow).
- `props_eng.py <repo> [names]`: Engineering machines (8-frame strips) and stock.
- `style_v2_demo.py`: the "C" test locker and fridge (used by the two scripts above).
- `couches.py <repo>`: sofa, armchair, view_bench.
- `depth_pass.py in.png out.png [--frames N]`: gives hand-drawn art the C colour and light without redrawing it.
- `make_icons.py <repo>`: item icons for the home machines; then run `tools/dev/relic_art.py` to rebuild `art/items.png`.
- `rocks6.py <outdir>` (+ `pix.py`): ore nodes, boulders and rocks.
