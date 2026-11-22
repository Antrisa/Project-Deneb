// Title scene: the moon base at 2x (scene.cpp drawMoon). While it slides in, pixels stay flat inside and only
// a pixel edge that falls through a screen pixel is blended; once settled it sits on whole pixels.
shader_type canvas_item;

uniform sampler2D moon_tex : filter_nearest;
uniform vec2 corner;        // top-left of the art (at 2x) on the canvas
uniform bool settled;
uniform float daylight;

const vec2 CANVAS = vec2(960.0, 540.0);

vec4 sample_bilinear(sampler2D tex, vec2 p) {
	vec2 size = vec2(textureSize(tex, 0));
	p = clamp(p, vec2(0.0), size - 2.0);
	vec2 i = floor(p);
	vec2 f = floor((p - i) * 256.0) / 256.0;
	ivec2 q = ivec2(i);
	vec4 a = texelFetch(tex, q, 0);
	vec4 b = texelFetch(tex, q + ivec2(1, 0), 0);
	vec4 c = texelFetch(tex, q + ivec2(0, 1), 0);
	vec4 d = texelFetch(tex, q + ivec2(1, 1), 0);
	return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

vec4 sprite_pixel(sampler2D tex, vec2 q, float scale) {
	vec2 i = floor(q);
	vec2 f = clamp(0.5 + (q - i - 0.5) * scale, 0.0, 1.0);
	return sample_bilinear(tex, i + f);
}

void fragment() {
	vec2 p = floor(UV * CANVAS);
	vec2 sp = p - corner;
	vec2 size = vec2(textureSize(moon_tex, 0)) * 2.0;
	COLOR = vec4(0.0);
	if (sp.x >= 0.0 && sp.y >= 0.0 && sp.x < size.x && sp.y < size.y) {
		vec4 c = settled ? texelFetch(moon_tex, ivec2(int(sp.x) / 2, int(sp.y) / 2), 0) : sprite_pixel(moon_tex, (sp + 0.5) / 2.0 - 0.5, 2.0);
		if (c.a >= 1.5 / 255.0) {
			if (!settled && daylight < 1.0) {
				vec3 k = c.rgb * 255.0;
				float warm = clamp((k.r - k.b - 12.0) * 0.009, 0.0, 1.0) * clamp((k.r - 65.0) * 0.008, 0.0, 1.0);
				float li = 0.105 + 0.895 * daylight;
				float local = li + 0.48 * warm * (1.0 - li);
				c.rgb = clamp(vec3(k.r * local, k.g * (local + 0.022 * (1.0 - local)), k.b * (local + 0.09 * (1.0 - local))), 0.0, 255.0) / 255.0;
			}
			COLOR = vec4(c.rgb, c.a > 0.99 ? 1.0 : c.a);
		}
	}
}
