shader_type canvas_item;
// The animated surface of the lake and the underground ocean (23 Nov 2026). Drawn over the baked water, masked
// by art/lunar/watermask_<key>.png (white where there is water). Everything is worked out per art pixel, so it stays
// crisp pixel art: slow drifting swells, short light streaks sliding along, and the odd sparkle.
uniform vec2 art_size = vec2(1024.0, 1024.0);   // the mask's size in art pixels
uniform vec4 light : source_color = vec4(0.62, 0.90, 0.92, 1.0);
uniform vec4 dark : source_color = vec4(0.02, 0.06, 0.10, 1.0);

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

void fragment() {
	float m = texture(TEXTURE, UV).r;
	if (m < 0.5) { discard; }
	vec2 px = floor(UV * art_size);
	float t = TIME;
	// broad swells: a slow darker band drifting across
	float swell = sin(px.x * 0.045 + px.y * 0.11 - t * 0.9) * sin(px.y * 0.07 - px.x * 0.02 + t * 0.6);
	// light streaks: every fourth row, short dashes sliding sideways at a speed of their own
	float row = floor(px.y / 4.0);
	float on_row = step(3.0, mod(px.y, 4.0));
	float speed = 4.0 + hash(vec2(row, 1.0)) * 6.0;
	float dash = fract((px.x + t * speed + hash(vec2(row, 2.0)) * 300.0) / 46.0);
	float streak = on_row * step(0.82, dash) * step(0.25, swell + 0.6);
	// sparkles: a few cells blink for an instant
	float cell = hash(floor(px / 3.0) + floor(t * 3.0) * 17.0);
	float sparkle = step(0.9975, cell);
	vec4 c = vec4(0.0);
	c = mix(c, vec4(dark.rgb, 0.22), step(0.55, swell));
	c = mix(c, vec4(light.rgb, 0.5), streak);
	c = mix(c, vec4(1.0, 1.0, 1.0, 0.85), sparkle);
	COLOR = c;
}
