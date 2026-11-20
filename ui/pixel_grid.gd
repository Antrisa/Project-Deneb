extends RefCounted

const DESIGN := Vector2(768, 432)

# Godot can keep Controls at a fixed logical size during a physical window resize.
# Include the viewport stretch exactly once, including its letterbox translation.
static func to_pixels(surface: Control) -> Transform2D:
	return surface.get_viewport_transform() * surface.get_global_transform()

static func layout(surface: Control) -> Transform2D:
	var device := to_pixels(surface)
	var available := surface.size * device.get_scale().abs()
	var fit := minf(available.x / DESIGN.x, available.y / DESIGN.y)
	if fit <= 0.0:
		return Transform2D.IDENTITY
	# Small windows retain fit-to-window scaling. Desktop targets can use whole pixels.
	var step := floorf(fit + 0.00001) if fit >= 1.99999 else fit
	var start := (device.origin + (available - DESIGN * step) * 0.5).round()
	return device.affine_inverse() * Transform2D(0.0, Vector2.ONE * step, 0.0, start)

static func place_left(surface: Control, child: Control) -> void:
	var device := to_pixels(surface)
	child.scale = layout(surface).get_scale()
	var anchor := surface.size * Vector2(0.05, 0.46)
	var top_left := anchor - Vector2(0.0, 0.5 * child.size.y * child.scale.y)
	child.position = device.affine_inverse() * (device * top_left).round()
