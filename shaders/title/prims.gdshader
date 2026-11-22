// Title scene: soft dots, lines and glows (scene.cpp dot, line and glow), drawn in the order given.
// Used for the lightning and shooting stars, the base's lamps and the drifting rocks, and the wing sparks.
shader_type canvas_item;

uniform int count;
uniform vec4 shape[64];   // kind (0 dot, 1 line, 2 glow), x1, y1, x2
uniform vec4 extra[64];   // y2, size (dot or line radius; glow x radius), glow y radius, alpha
uniform vec4 tint[64];    // colour

const vec2 CANVAS = vec2(960.0, 540.0);

void fragment() {
	vec2 p = floor(UV * CANVAS);
	vec3 acc = vec3(0.0);
	float acc_a = 0.0;
	for (int i = 0; i < count; i++) {
		vec4 s = shape[i];
		vec4 e = extra[i];
		float a = 0.0;
		if (s.x < 0.5) {
			vec2 d = p - s.yz;
			if (abs(d.x) > e.y + 1.0 || abs(d.y) > e.y + 1.0) {
				continue;
			}
			a = e.w * clamp(e.y + 0.55 - length(d), 0.0, 1.0);
		} else if (s.x < 1.5) {
			vec2 pa = s.yz;
			vec2 pb = vec2(s.w, e.x);
			float r = e.y + 1.0;
			if (p.x < min(pa.x, pb.x) - r || p.x > max(pa.x, pb.x) + r || p.y < min(pa.y, pb.y) - r || p.y > max(pa.y, pb.y) + r) {
				continue;
			}
			vec2 v = pb - pa;
			float k = clamp(dot(p - pa, v) / max(0.001, dot(v, v)), 0.0, 1.0);
			a = e.w * clamp(e.y + 0.6 - length(p - pa - k * v), 0.0, 1.0);
		} else {
			if (e.w < 0.002) {
				continue;
			}
			vec2 d = (p - s.yz) / e.yz;
			float v = 1.0 - dot(d, d);
			if (v <= 0.0) {
				continue;
			}
			a = e.w * v * v * v;
		}
		a = clamp(a, 0.0, 1.0);
		if (a <= 0.0) {
			continue;
		}
		acc = tint[i].rgb * a + acc * (1.0 - a);
		acc_a = a + acc_a * (1.0 - a);
	}
	COLOR = acc_a > 0.0 ? vec4(acc / acc_a, acc_a) : vec4(0.0);
}
