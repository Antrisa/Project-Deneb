// Title scene: the blue gas giant (scene.cpp drawPlanet). Its clouds turn round three storm centres and drift
// in bands; during the approach the night side gives way to day.
shader_type canvas_item;

uniform sampler2D world_tex : filter_nearest;
uniform vec2 corner;       // top-left of the planet on the canvas
uniform vec3 turn;         // the three storms' angles
uniform float zon;         // band drift
uniform float lat;         // meridian drift
uniform float t;           // seconds since the opening started
uniform float threshold;   // where night meets day
uniform bool day;

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

void fragment() {
	vec2 p = floor(UV * CANVAS);
	int size = textureSize(world_tex, 0).x;
	float D = float(size);
	COLOR = vec4(0.0);
	if (p.x >= max(0.0, trunc(corner.x)) && p.x < trunc(corner.x + D - 1.0) && p.y >= max(0.0, trunc(corner.y)) && p.y < trunc(corner.y + D - 1.0)) {
		float s = p.x - corner.x;
		float v = p.y - corner.y;
		int ix = clamp(int(s), 0, size - 1);
		int iy = clamp(int(v), 0, size - 1);
		vec4 orig = texelFetch(world_tex, ivec2(ix, iy), 0);
		if (orig.a >= 2.5 / 255.0) {
			float R = D * 0.5;
			float fx = float(ix);
			float fy = float(iy);
			float nx = (fx + 0.5 - R) / R;
			float ny = (fy + 0.5 - R) / R;
			float rr = sqrt(nx * nx + ny * ny);
			float z = sqrt(max(0.0, 1.0 - rr * rr));
			float edge = smoothstep(0.005, 0.19, 1.0 - rr);
			vec2 centres[3] = vec2[3](vec2(0.261, 0.235), vec2(0.474, 0.476), vec2(0.752, 0.752));
			float spread[3] = float[3](86.0, 111.0, 91.0);
			float best = 0.0;
			float wx = 0.0;
			float wy = 0.0;
			float angle = turn.x;
			for (int i = 0; i < 3; i++) {
				float qx = fx - centres[i].x * D;
				float qy = fy - centres[i].y * D;
				float w = exp(-(qx * qx + qy * qy) / (spread[i] * spread[i] * 0.98)) * edge;
				if (w > best) {
					best = w;
					wx = qx * w;
					wy = qy * w;
					angle = i == 0 ? turn.x : (i == 1 ? turn.y : turn.z);
				}
			}
			float band = sin(fy * 0.035 + 1.2 * sin(fx * 0.011)) * (1.0 - best) * edge;
			float mer = cos(fy * 0.047 + fx * 0.017) * edge * (1.0 - best);
			float co = cos(angle) - 1.0;
			float si = sin(angle);
			float dx = co * wx - si * wy + zon * band;
			float dy = si * wx + co * wy + lat * mer;
			vec3 c = sample_bilinear(world_tex, vec2(s + dx, v + dy)).rgb;
			if (!day) {
				float sun = nx * 0.80 - ny * 0.46 + 0.22 * z;
				float rim = pow(clamp((rr - 0.973) / 0.027, 0.0, 1.0), 2.0) * clamp((sun + 0.02) * 1.2, 0.0, 1.0);
				float amt = smoothstep(threshold - 0.31, threshold + 0.16, sun);
				float dark = 0.002 + 0.025 * smoothstep(4.0, 8.0, t);
				float rimk = rim * (0.22 + smoothstep(3.2, 11.0, t) * 0.49);
				vec3 k = c * 255.0;
				k = vec3(mix(2.0 + k.r * dark, k.r, amt) + mix(14.0 * rimk, 0.0, amt), mix(5.0 + k.g * dark, k.g, amt) + mix(32.0 * rimk, 0.0, amt), mix(11.0 + k.b * dark, k.b, amt) + mix(50.0 * rimk, 0.0, amt));
				c = clamp(k, 0.0, 255.0) / 255.0;
			}
			COLOR = vec4(c, orig.a >= 251.5 / 255.0 ? 1.0 : orig.a);
		}
	}
}
