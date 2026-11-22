// Title scene: the sun behind the gas giant (scene.cpp drawSun). Glow, corona, turning surface and two
// prominences; every phase closes after exactly 120 s.
shader_type canvas_item;

uniform vec2 centre;
uniform float vis;
uniform float phase;          // TAU * loop time / 120
uniform vec4 prom[34];        // prominence segments: from x, y, to x, y
uniform vec4 prom_tint[34];   // colour, alpha

const vec2 CANVAS = vec2(960.0, 540.0);
const float RADIUS = 15.6;

void over(inout vec4 acc, vec3 tint, float alpha) {
	float a = clamp(alpha, 0.0, 1.0);
	acc.rgb = tint * a + acc.rgb * (1.0 - a);
	acc.a = a + acc.a * (1.0 - a);
}

void glow(inout vec4 acc, vec2 d, vec2 radius, vec3 tint, float alpha) {
	if (alpha < 0.002) {
		return;
	}
	vec2 k = d / radius;
	float v = 1.0 - k.x * k.x - k.y * k.y;
	if (v > 0.0) {
		over(acc, tint, alpha * v * v * v);
	}
}

void fragment() {
	vec2 p = floor(UV * CANVAS);
	vec2 d0 = p - centre;
	vec4 acc = vec4(0.0);
	if (vis > 0.0 && abs(d0.x) < 93.0 && abs(d0.y) < 86.0) {
		glow(acc, d0, vec2(91.0, 84.0), vec3(95.0, 125.0, 166.0) / 255.0, vis * 0.23);
		glow(acc, d0, vec2(59.0, 54.0), vec3(222.0, 137.0, 75.0) / 255.0, vis * 0.43);
		glow(acc, d0, vec2(38.0, 35.0), vec3(250.0, 168.0, 79.0) / 255.0, vis * 0.66);
		bool inside = p.x >= trunc(centre.x - 46.0) && p.x < trunc(centre.x + 47.0) && p.y >= trunc(centre.y - 46.0) && p.y < trunc(centre.y + 47.0);
		vec2 d = d0 / RADIUS;
		float rr = length(d);
		if (inside && rr <= 2.85) {
			if (rr > 1.0) {
				float aa = atan(d.y, d.x);
				float off = rr - 1.0;
				float fan = 0.5 + 0.5 * sin(aa * 11.0 + 0.72 * sin(aa * 4.0 + phase * 3.0) + phase * 2.0);
				float wisp = 0.5 + 0.5 * sin(aa * 25.0 + phase * 3.0 + 2.6 * off);
				float ray = exp(-off * (6.7 - 2.9 * fan)) * (0.38 + 0.39 * fan + 0.23 * wisp);
				over(acc, vec3(255.0, 177.0 + 41.0 * fan, 88.0) / 255.0, vis * ray * 0.90);
			} else {
				float z = sqrt(max(0.0, 1.0 - rr * rr));
				float lon = atan(d.x, max(z, 0.00001)) + phase;
				float lat = asin(clamp(d.y, -1.0, 1.0));
				float cell = 0.5 + 0.5 * sin(13.0 * lon + 2.1 * sin(lat * 7.0 + phase * 2.0)) * sin(lat * 14.0 + 2.0 * sin(lon * 6.0));
				float belt = 0.5 + 0.5 * sin(13.0 * lat + 1.6 * sin(lon * 3.0 + phase));
				float k = clamp(0.45 * z + 0.37 * cell + 0.18 * belt, 0.0, 1.0);
				vec3 c = vec3(255.0, 150.0 + 95.0 * k, 60.0 + 127.0 * k) / 255.0;
				float filament = exp(-pow((d.y + 0.24 + 0.26 * sin(lon * 2.1)) / 0.08, 2.0)) * smoothstep(0.05, 0.65, sin(lon + phase * 2.0));
				c = mix(c, vec3(192.0, 85.0, 45.0) / 255.0, clamp(filament * 0.51, 0.0, 1.0));
				over(acc, c, vis * clamp((1.04 - rr) * RADIUS, 0.0, 1.0));
			}
		}
		if (rr < 2.0) {
			for (int i = 0; i < 34; i++) {
				vec2 pa = prom[i].xy;
				vec2 v = prom[i].zw - pa;
				float k = clamp(dot(p - pa, v) / max(0.001, dot(v, v)), 0.0, 1.0);
				float a = prom_tint[i].a * clamp(1.28 - length(p - pa - k * v), 0.0, 1.0);
				if (a > 0.0) {
					over(acc, prom_tint[i].rgb, a);
				}
			}
		}
	}
	COLOR = acc.a > 0.0 ? vec4(acc.rgb / acc.a, acc.a) : vec4(0.0);
}
