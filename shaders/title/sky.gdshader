// Title scene, layer 1: the starfield, the green cloud's light and the twinkling stars (scene.cpp drawSky and
// the stars of starsAndStorm). Drawn on a ColorRect that fills the 960x540 title canvas.
shader_type canvas_item;

uniform sampler2D sky_tex : filter_nearest;
uniform sampler2D mask_tex : filter_nearest;   // nebula_light.png: three light masks in R, G and B
uniform vec2 offset;                           // where the canvas's top-left corner falls on the starfield
uniform bool settled;                          // the station loop: the sky holds still on whole pixels
uniform float vis;                             // fade in from the dark during the approach
uniform vec3 power;                            // light in the three gas knots
uniform float u;                               // loop time, seconds
uniform float show;                            // stars fade in during the approach
uniform vec4 stars[84];                        // one per 83x80 cell (12 x 7): x, y, phase, twinkle count; x < 0: none

const vec2 CANVAS = vec2(960.0, 540.0);

// Bilinear sampling with 1/256 steps, as the original renderer does it.
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

vec3 emit(vec3 base, vec3 mask) {
	vec3 k = mask * power;
	vec3 added = vec3(0.13 * k.x + 0.23 * k.y + 0.13 * k.z, 0.41 * k.x + 0.43 * k.y + 0.42 * k.z, 0.24 * k.x + 0.19 * k.y + 0.30 * k.z);
	return min(base + added, vec3(1.0));
}

vec3 glow(vec3 col, vec2 d, vec2 radius, vec3 tint, float alpha) {
	if (alpha < 0.002) {
		return col;
	}
	vec2 k = d / radius;
	float v = 1.0 - k.x * k.x - k.y * k.y;
	if (v <= 0.0) {
		return col;
	}
	return mix(col, tint, clamp(alpha * v * v * v, 0.0, 1.0));
}

void fragment() {
	vec2 p = floor(UV * CANVAS);
	vec3 col;
	if (settled) {
		ivec2 q = ivec2(p + floor(offset));
		col = texelFetch(sky_tex, q, 0).rgb;
		vec3 m = texelFetch(mask_tex, q, 0).rgb;
		if (m.r + m.g + m.b > 2.5 / 255.0) {
			col = emit(col, m);
		}
	} else {
		vec3 s = sample_bilinear(sky_tex, offset + p).rgb;
		if (p.y > 100.0 && vis > 0.07) {
			s = emit(s, texelFetch(mask_tex, ivec2(floor(offset + p)), 0).rgb);
		}
		col = mix(vec3(10.0, 16.0, 29.0) / 255.0, s, vis);
	}
	if (show > 0.0) {
		vec2 q = p + offset;    // this pixel on the starfield, where the stars are pinned
		int ci = int(floor((q.x - 220.0) / 83.0));
		int cj = int(floor((q.y - 20.0) / 80.0));
		for (int j = cj - 1; j <= cj + 1; j++) {
			for (int i = ci - 1; i <= ci + 1; i++) {
				if (i < 0 || i > 11 || j < 0 || j > 6) {
					continue;
				}
				vec4 star = stars[j * 12 + i];
				vec2 d = q - star.xy;
				if (star.x < 0.0 || abs(d.x) > 6.0 || abs(d.y) > 5.0) {
					continue;
				}
				float phase = TAU * u * star.w / 120.0 + star.z;
				float wave = 0.5 + 0.5 * sin(phase + 0.55 * sin(TAU * u / 24.0 + star.z));
				float peak = wave * wave * wave;
				float dist = length(d);
				col = mix(col, vec3(7.0, 12.0, 29.0) / 255.0, clamp(0.52 * (1.0 - wave) * show * clamp(1.8 - dist, 0.0, 1.0), 0.0, 1.0));
				col = mix(col, vec3(218.0, 228.0, 240.0) / 255.0, clamp(peak * 0.84 * show * clamp(1.33 - dist, 0.0, 1.0), 0.0, 1.0));
				if (peak > 0.45) {
					float flare = (peak - 0.45) * show;
					col = glow(col, d, vec2(4.4, 1.05), vec3(166.0, 198.0, 226.0) / 255.0, flare * 0.74);
					col = glow(col, d, vec2(1.05, 3.5), vec3(166.0, 198.0, 226.0) / 255.0, flare * 0.68);
				}
			}
		}
	}
	COLOR = vec4(col, 1.0);
}
