extends RefCounted
# Native 24 × 48 cells, foot pivot (12,45), directions south, north, west, east.
# Rows 0–4 follow the walking legs while carrying.
enum { CARRY, CARRY_LEFT_CONTACT, CARRY_RIGHT_CONTACT, CARRY_LEFT_PASS, CARRY_RIGHT_PASS, GRIP, LIFT, STRIKE, POUR, WINDUP, SWEEP, FOLLOW, REACH, SHOW_ITEM, BRACE, RECOIL, RECOVER, WATER_GATHER, WATER_RAISE, WATER_READY, COUNT }
# Row 19 was called WATER_OVERHEAD on the preceding atlas.
const WATER_OVERHEAD := WATER_READY
const WATER_ROWS := [WATER_GATHER, WATER_RAISE, WATER_READY, POUR]

class ActionSheet extends ImageTexture:
	var watering_arms: Texture2D

const LEGACY_COUNT := 8
const PREVIOUS_COUNT := 17
const SIZE := Vector2i(24, 48)
const FOOT := Vector2i(12, 45)
const ART_SCALE := 2.0 / 3.0
const LEGACY_ROWS := [0, 1, 2, 3, 4, 5, 6, 7, 7, 6, 7, 7, 7, 0, 5, 5, 5]

# Head and hair displacement from the selected standing frame.
const HEAD := [
	[Vector2i(0, 0), Vector2i(0, 0), Vector2i(0, 0)], # grip
	[Vector2i(-1, -1), Vector2i(1, -1), Vector2i(-1, -1)], # lift
	[Vector2i(1, 3), Vector2i(-1, 1), Vector2i(2, 2)], # strike
	[Vector2i(0, 0), Vector2i(0, 0), Vector2i(0, 0)], # pour
	[Vector2i(-1, 0), Vector2i(1, 0), Vector2i(-2, 0)], # windup
	[Vector2i(1, 1), Vector2i(-1, 1), Vector2i(1, 1)], # sweep
	[Vector2i(2, 1), Vector2i(-2, 1), Vector2i(2, 1)], # follow
	[Vector2i(0, 3), Vector2i(0, 2), Vector2i(2, 3)], # reach
	[Vector2i(0, -1), Vector2i(0, -1), Vector2i(0, -1)], # show_item
	[Vector2i(1, 1), Vector2i(0, 0), Vector2i(1, 0)], # brace
	[Vector2i(-1, 1), Vector2i(0, 1), Vector2i(-1, 1)], # recoil
	[Vector2i(0, 1), Vector2i(0, 0), Vector2i(1, 1)], # recover
	[Vector2i(0, 0), Vector2i(0, 0), Vector2i(0, 0)], # gather the can
	[Vector2i(0, 0), Vector2i(0, 0), Vector2i(0, 0)], # raise the can
	[Vector2i(0, 0), Vector2i(0, 0), Vector2i(0, 0)], # hold the can forward
]

# The actual contact pixel on the primary hand, facing south, north or east.
const PALM := [
	[Vector2i(14, 29), Vector2i(13, 26), Vector2i(17, 28)], # grip
	[Vector2i(10, 14), Vector2i(14, 12), Vector2i(10, 13)], # lift
	[Vector2i(14, 33), Vector2i(12, 23), Vector2i(21, 31)], # strike
	[Vector2i(17, 23), Vector2i(4, 22), Vector2i(21, 21)], # pour
	[Vector2i(6, 21), Vector2i(17, 21), Vector2i(6, 18)], # windup
	[Vector2i(15, 28), Vector2i(8, 25), Vector2i(18, 26)], # sweep
	[Vector2i(19, 30), Vector2i(4, 26), Vector2i(21, 29)], # follow
	[Vector2i(14, 36), Vector2i(13, 31), Vector2i(20, 35)], # reach
	[Vector2i(15, 4), Vector2i(14, 4), Vector2i(16, 4)], # show_item
	[Vector2i(14, 28), Vector2i(12, 23), Vector2i(19, 26)], # brace
	[Vector2i(13, 27), Vector2i(12, 26), Vector2i(16, 26)], # recoil
	[Vector2i(13, 30), Vector2i(12, 26), Vector2i(16, 30)], # recover
	[Vector2i(16, 27), Vector2i(6, 26), Vector2i(18, 26)], # gather the can
	[Vector2i(16, 23), Vector2i(5, 23), Vector2i(19, 22)], # raise the can
	[Vector2i(16, 20), Vector2i(4, 20), Vector2i(20, 18)], # hold the can forward
]

# The preceding 17-row atlas used a waist-height pour. Its other native grips match.
const PREVIOUS_POUR_PALM := [Vector2i(15, 27), Vector2i(13, 23), Vector2i(20, 27)]

# Rear handle attachment and nozzle in the tier textures, relative to the native (48,48) centre.
const CAN_RIM: Array[Vector2] = [Vector2(4, 2), Vector2(4, 2), Vector2(6, 8), Vector2(-6, 8)]
const CAN_SPOUT: Array[Vector2] = [Vector2(0, 12), Vector2(0, -11), Vector2(-14, 3), Vector2(14, 3)]


static func head_offset(row: int, facing: int, _rows: int = COUNT) -> Vector2i:
	if row < GRIP:
		return Vector2i.ZERO
	var poses: Array = HEAD[row - GRIP]
	var v: Vector2i = poses[mini(facing, 2)]
	return Vector2i(-v.x, v.y) if facing == 2 else v


static func hand(row: int, facing: int, rows: int = COUNT) -> Vector2i:
	var grips: Array = PREVIOUS_POUR_PALM if row == POUR and rows == PREVIOUS_COUNT else PALM[row - GRIP]
	var v: Vector2i = grips[mini(facing, 2)]
	return Vector2i(SIZE.x - 1 - v.x, v.y) if facing == 2 else v


static func world_grip(row: int, facing: int, rows: int = COUNT) -> Vector2:
	return Vector2(hand(row, facing, rows) - FOOT) * ART_SCALE


static func tool_row(kind: String, t: float, rows: int = COUNT) -> int:
	match kind:
		"hoe":
			if t < 0.13: return GRIP
			if t < 0.45: return LIFT
			if t < 0.79: return STRIKE
		"water":
			if rows < COUNT:
				if t < 0.20: return GRIP
				return POUR if t < 0.82 else GRIP
			if t < 0.14 or t >= 0.92: return WATER_GATHER
			if t < 0.29 or t >= 0.79: return WATER_RAISE
			return WATER_READY if t < 0.46 else POUR
		"scythe":
			if t < 0.28: return WINDUP
			if t < 0.53: return SWEEP
			if t < 0.83: return FOLLOW
		"pickup":
			if t < 0.26: return REACH
			if t < 0.43: return GRIP
			if t < 0.91: return SHOW_ITEM
		"laser":
			return RECOIL if t >= 0.12 and t < 0.38 else BRACE
	return RECOVER
