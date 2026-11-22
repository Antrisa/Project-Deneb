shader_type canvas_item;
// Sharp scaling for pictures shown at a size that isn't a whole multiple of their pixels, such as the
// 960x540 title movie on a 1440p screen (2.67x). Nearest-neighbour there makes some rows and columns
// 2 screen pixels and others 3, and in motion that pattern crawls and shimmers. Here every picture pixel
// stays one solid colour and only a one-screen-pixel band at its edge is blended, so it looks crisp without
// the crawl. At whole-number scales (2x at 1080p) it is exactly nearest-neighbour.
// The node using this must have linear texture filtering.

varying vec4 tint;

void vertex() {
	tint = COLOR;                       // the node's modulate (the title's fade-in uses it)
}

void fragment() {
	vec2 size = 1.0 / TEXTURE_PIXEL_SIZE;
	vec2 texel = UV * size;
	vec2 scale = 1.0 / max(fwidth(texel), vec2(1e-4));       // screen pixels per picture pixel
	vec2 edge = max(vec2(0.5) - vec2(0.5) / scale, vec2(0.0));
	vec2 f = fract(texel) - 0.5;
	f = (f - clamp(f, -edge, edge)) * scale + 0.5;
	COLOR = texture(TEXTURE, (floor(texel) + f) / size) * tint;
}
