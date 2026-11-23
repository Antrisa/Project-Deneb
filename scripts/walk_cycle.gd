extends RefCounted
# A character cell is twice as tall as it is wide. Directions run down, up, left, right.
# Row zero is the standing pose. Movement alternates contacts and passing poses.
const POSES := [1, 3, 2, 4]
const LEGACY_POSES := [1, 0, 2, 0]
const UNITS_PER_PHASE := 8.0
const STRIDE := UNITS_PER_PHASE * 4.0


static func rows(tex: Texture2D) -> int:
	return roundi(tex.get_height() / (tex.get_width() * 0.5))


static func phase(distance: float) -> int:
	return floori(distance / UNITS_PER_PHASE) % 4


static func pose(beat: int, row_count: int) -> int:
	return POSES[beat % 4] if row_count == 5 else LEGACY_POSES[beat % 4]
