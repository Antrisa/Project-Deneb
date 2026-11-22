// Title scene: the Needle fighter (scene.cpp fighter). The 72x49 sprite is drawn turned and scaled, with
// flickering engine plumes behind it and glowing nozzles. Easter egg: `part` draws the whole ship (0), the ship
// without the outer panel of its intact wing, with a dark cut along the orange stripe (1), or that panel alone
// once it has come off (2) (scripts/title_scene.gd).
shader_type canvas_item;

uniform sampler2D ship_tex : filter_nearest;
uniform sampler2D wing_tex : filter_nearest;   // fighter_wing.png: red on the panel that comes off, green on the cut
uniform int part;
uniform vec2 centre;
uniform float scale;
uniform vec2 rot;          // cos, sin of the fighter's angle
uniform vec2 engines;      // the two nozzles' brightness
uniform float ambient;
uniform float plume_len;
uniform float sway;

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

vec4 sprite_pixel(sampler2D tex, vec2 q, float k) {
	vec2 i = floor(q);
	vec2 f = clamp(0.5 + (q - i - 0.5) * k, 0.0, 1.0);
	return sample_bilinear(tex, i + f);
}

// A pixel of the ship, without the broken-off panel (part 1) or only that panel (part 2).
vec4 ship_texel(ivec2 q) {
	vec4 c = texelFetch(ship_tex, q, 0);
	if (part != 0) {
		float piece = texelFetch(wing_tex, q, 0).r;
		c.a *= part == 1 ? 1.0 - piece : piece;
	}
	return c;
}

// sprite_pixel on the ship, with the part chosen pixel by pixel before blending, so no ghost edge is left.
vec4 ship_sample(vec2 q, float k) {
	vec2 i = floor(q);
	vec2 p = i + clamp(0.5 + (q - i - 0.5) * k, 0.0, 1.0);
	p = clamp(p, vec2(0.0), vec2(textureSize(ship_tex, 0)) - 2.0);
	vec2 base = floor(p);
	vec2 w = floor((p - base) * 256.0) / 256.0;
	ivec2 b = ivec2(base);
	return mix(mix(ship_texel(b), ship_texel(b + ivec2(1, 0)), w.x), mix(ship_texel(b + ivec2(0, 1)), ship_texel(b + ivec2(1, 1)), w.x), w.y);
}

void over(inout vec4 acc, vec3 tint, float alpha) {
	float a = clamp(alpha, 0.0, 1.0);
	acc.rgb = tint * a + acc.rgb * (1.0 - a);
	acc.a = a + acc.a * (1.0 - a);
}

void fragment() {
	vec2 p = floor(UV * CANVAS);
	vec4 acc = vec4(0.0);
	float x0 = max(0.0, trunc(centre.x - scale * 163.0));
	float x1 = min(CANVAS.x, trunc(centre.x + scale * 163.0 + 1.0));
	float y0 = max(0.0, trunc(centre.y - scale * 143.0));
	float y1 = min(CANVAS.y, trunc(centre.y + scale * 143.0 + 1.0));
	if (p.x >= x0 && p.x < x1 && p.y >= y0 && p.y < y1) {
		float ox = (p.x - centre.x) / scale;
		float oy = (p.y - centre.y) / scale;
		float su = 130.0 + rot.x * ox - rot.y * oy;
		float sv = 87.0 + rot.y * ox + rot.x * oy;
		vec2 nozzles[2] = vec2[2](vec2(13.66 * 260.0 / 72.0, 29.18 * 174.0 / 49.0), vec2(21.48 * 260.0 / 72.0, 35.08 * 174.0 / 49.0));
		for (int i = 0; i < 2 && part != 2; i++) {
			float du = su - nozzles[i].x;
			float dv = sv - nozzles[i].y;
			float along = -0.879 * du + 0.477 * dv;
			float across = 0.477 * du + 0.879 * dv;
			float power = i == 0 ? engines.x : engines.y;
			float reach = plume_len * (i == 0 ? 1.0 : 0.83);
			if (along > 0.0 && along < reach && abs(across) < 15.0) {
				float z = along / reach;
				float width = mix(6.4, 1.2, z);
				float w = (across - sway * z * z) / width;
				float plume = exp(-2.65 * w * w) * (1.0 - z) * (1.0 - z);
				over(acc, vec3(131.0, 165.0, 211.0) / 255.0, plume * (0.09 + 0.73 * power));
				over(acc, vec3(255.0, 192.0, 104.0) / 255.0, plume * plume * power * 0.85);
			}
		}
		vec2 tsize = vec2(textureSize(ship_tex, 0));
		if (su >= 0.0 && su < 260.0 && sv >= 0.0 && sv < 174.0) {
			vec2 q = vec2((su + 0.5) * tsize.x / 260.0 - 0.5, (sv + 0.5) * tsize.y / 174.0 - 0.5);
			vec4 tex = ship_sample(q, scale * 260.0 / tsize.x);
			float cut = part == 1 ? sprite_pixel(wing_tex, q, scale * 260.0 / tsize.x).g : 0.0;
			if (tex.a >= 1.5 / 255.0) {
				vec3 k = tex.rgb * 255.0;
				float cool = clamp((k.g - k.r + 10.0) * 0.02, 0.0, 1.0) * clamp((105.0 - sv) * 0.02, 0.0, 1.0);
				float dim = 1.0 - ambient;
				vec3 lit = vec3(k.r * ambient + cool * dim * 4.0, k.g * (ambient + 0.055 * dim) + cool * dim * 17.0, k.b * (ambient + 0.16 * dim) + cool * dim * 18.0);
				lit = clamp(lit, 0.0, 255.0) / 255.0;
				lit = mix(lit, vec3(56.0, 41.0, 63.0) / 255.0, 0.75 * cut);
				for (int i = 0; i < 2; i++) {
					float du = su - nozzles[i].x;
					float dv = sv - nozzles[i].y;
					float eu = (0.80 * du + 0.60 * dv) / 9.5;
					float ev = (-0.60 * du + 0.80 * dv) / 4.25;
					float d2 = eu * eu + ev * ev;
					if (d2 < 1.0) {
						float bowl = (1.0 - d2) * (1.0 - d2);
						float power = i == 0 ? engines.x : engines.y;
						lit = mix(lit, vec3(177.0, 88.0, 58.0) / 255.0, clamp((0.28 + 0.52 * power) * bowl, 0.0, 1.0));
						lit = mix(lit, vec3(255.0, 194.0, 116.0) / 255.0, clamp(bowl * power * 0.93, 0.0, 1.0));
					}
				}
				if (tex.a > 0.99) {
					acc = vec4(lit, 1.0);
				} else {
					over(acc, lit, tex.a);
				}
			}
		}
	}
	COLOR = acc.a > 0.0 ? vec4(acc.rgb / acc.a, acc.a) : vec4(0.0);
}
