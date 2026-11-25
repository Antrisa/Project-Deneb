shader_type canvas_item;
// The Survey Level lounge's glazing (23 Nov). The view is drawn here rather than played from a loop:
// the stars and the gas giant stay where they are, the giant's cloud belts drift and its storm turns
// slowly, the sun crosses the sky with the time of day and sets behind the giant in the evening, and
// shooting stars and the day's sky event (scripts/lounge_sky.gd) come and go. TEXTURE is the window
// frame, drawn over the view. Pixel for pixel the same as tools/dev/lounge_sky_preview.py.

uniform float minute = 720.0;   // the station clock, minutes after midnight (runs past 1440 till 02:00)
uniform int event = 0;          // 0 clear, 1 eclipse, 2 gas cloud, 3 meteors, 4 transit, 5 aurora, 6 comet, 7 storm
uniform float clock_time = 0.0; // seconds, for twinkling, drifting and shooting stars

const vec2 SIZE = vec2(912.0, 64.0);
const vec2 GIANT = vec2(455.0, 43.0);
const float GIANT_R = 36.0;
// PI is built into Godot 4.6's shading language; defining it again stopped this shader compiling (25 Nov)

varying vec4 tint;

void vertex() {
	tint = COLOR;
}

// Hashes without sin(), which goes ragged on some graphics cards for large numbers.
float hash2(vec2 p, float s) {
	vec3 p3 = fract(vec3(p.x, p.y, p.x) * 0.1031 + s * 0.1379);
	p3 += dot(p3, p3.yzx + 33.33);
	return fract((p3.x + p3.y) * p3.z);
}

float hash1(float n) {
	float p = fract(n * 0.1031);
	p *= p + 33.33;
	p *= p + p;
	return fract(p);
}

float vnoise(vec2 p, float s) {
	vec2 i = floor(p);
	vec2 f = p - i;
	f = f * f * (3.0 - 2.0 * f);
	float a = hash2(i, s);
	float b = hash2(i + vec2(1.0, 0.0), s);
	float c = hash2(i + vec2(0.0, 1.0), s);
	float d = hash2(i + vec2(1.0, 1.0), s);
	return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fbm(vec2 p, float s) {
	return 0.55 * vnoise(p, s) + 0.3 * vnoise(p * 2.1, s + 3.0) + 0.15 * vnoise(p * 4.3, s + 7.0);
}

vec3 rgb(float r, float g, float b) {
	return vec3(r, g, b) / 255.0;
}

vec3 band_colour(int i) {
	if (i == 0) return rgb(30.0, 49.0, 139.0);
	if (i == 1) return rgb(45.0, 69.0, 180.0);
	if (i == 2) return rgb(49.0, 108.0, 190.0);
	if (i == 3) return rgb(89.0, 138.0, 209.0);
	if (i == 4) return rgb(98.0, 162.0, 228.0);
	if (i == 5) return rgb(166.0, 216.0, 250.0);
	if (i == 6) return rgb(235.0, 239.0, 221.0);
	if (i == 7) return rgb(253.0, 248.0, 215.0);
	if (i == 8) return rgb(161.0, 189.0, 213.0);
	if (i == 9) return rgb(102.0, 190.0, 234.0);
	if (i == 10) return rgb(46.0, 133.0, 195.0);
	return rgb(45.0, 86.0, 178.0);
}

// 06:00 the sun comes in at the left and sets behind the giant at 19:00. On an eclipse day it passes
// behind the giant at about 12:45 and goes on to the right-hand edge by 19:00.
vec3 sun_at(float m, bool eclipse) {
	float k = clamp((m - 360.0) / 780.0, 0.0, 1.0);
	float x = eclipse ? 24.0 + 864.0 * k : 24.0 + (GIANT.x - 24.0) * k;
	float y = eclipse ? 36.0 - 22.0 * sin(PI * k) : 40.0 - 18.0 * sin(PI * k * 0.9);
	float up = (m >= 360.0 && m <= 1170.0) ? 1.0 : 0.0;
	return vec3(x, y, up);
}

void fragment() {
	vec2 p = floor(UV * SIZE);
	float t = clock_time;
	float m = minute;
	// sky: darker rows at the top
	float row = clamp(p.y, 3.0, 59.0);
	vec3 col = row < 12.0 ? rgb(10.0, 15.0, 34.0) : row < 27.0 ? rgb(13.0, 21.0, 44.0) : row < 42.0 ? rgb(17.0, 28.0, 54.0) : row < 57.0 ? rgb(22.0, 35.0, 63.0) : rgb(26.0, 40.0, 69.0);
	float day = 1.0 - clamp((abs(m - 750.0) - 390.0) / 90.0, 0.0, 1.0);
	float night = 1.0 - day;
	// stars: fixed, some twinkling, a few more at night
	if (hash2(p, 1.0) > 0.985 - 0.006 * night) {
		float tw = 0.75 + 0.25 * sin(t * (1.0 + 3.0 * hash2(p, 2.0)) + 6.28 * hash2(p, 3.0));
		float bright = (hash2(p, 4.0) > 0.85 ? 1.0 : 0.55) * (hash2(p, 5.0) > 0.6 ? tw : 1.0);
		vec3 sc = hash2(p, 6.0) > 0.7 ? rgb(190.0, 215.0, 255.0) : rgb(235.0, 240.0, 255.0);
		col = mix(col, sc, bright * 0.8);
	}
	if (event == 2) {   // violet gas cloud, drifting very slowly
		float g = fbm(vec2(p.x / 40.0 + t * 0.01, p.y / 18.0), 11.0) * clamp((p.x - 520.0) / 200.0, 0.0, 1.0) * clamp((880.0 - p.x) / 80.0, 0.0, 1.0);
		g = floor(clamp(g - 0.35, 0.0, 1.0) * 8.0) / 8.0 * 1.6;
		col = mix(col, rgb(120.0, 70.0, 170.0), g * 0.6);
	}
	if (event == 7) {   // space storm: charged gas rolling past, lightning forking through it
		float s = fbm(vec2(p.x / 50.0 - t * 0.03, p.y / 20.0 + t * 0.01), 21.0);
		s = floor(clamp(s - 0.3, 0.0, 1.0) * 6.0) / 6.0;
		col = mix(col, rgb(40.0, 160.0, 150.0), s * 0.55);
		float beat = floor(t * 3.0);
		bool flash = hash1(beat * 12.9898) > 0.8;
		float lx = 100.0 + 700.0 * hash1(beat * 78.233);
		if (flash) {
			col += 0.05 * s;
			if (abs(p.x - lx - 6.0 * sin(p.y * 0.7 + beat)) < 0.8 && p.y > 6.0 && p.y < 40.0) col = rgb(220.0, 250.0, 255.0);
		}
	}
	if (event == 6) {   // a comet, fixed, its tail shimmering
		vec2 d = p - vec2(690.0, 22.0);
		float across = d.y - d.x * 0.12;
		if (d.x > 0.0 && d.x < 70.0 && abs(across) < 1.0 + d.x * 0.06) {
			float fade = clamp(1.0 - d.x / 70.0, 0.0, 1.0) * (0.7 + 0.3 * sin(d.x * 0.5 - t * 2.0));
			col += rgb(150.0, 190.0, 220.0) * fade * 0.6;
		}
		if (dot(d, d) < 3.0) col = rgb(240.0, 250.0, 255.0);
	}
	vec3 sun = sun_at(m, event == 1);
	if (sun.z > 0.5) {
		float d = length(p - sun.xy);
		float glow = floor(clamp(1.0 - d / 18.0, 0.0, 1.0) * 4.0) / 4.0;
		col += rgb(255.0, 130.0, 50.0) * glow * 0.6;
		if (d < 7.5) col = rgb(255.0, 190.0, 90.0);
		if (d < 5.0) col = rgb(255.0, 236.0, 190.0);
	}
	// the giant
	vec2 q = (p - GIANT) / GIANT_R;
	float rr = dot(q, q);
	if (rr < 1.0) {
		float z = sqrt(max(1.0 - rr, 0.0));
		float lon = atan(q.x, z) + t * 0.02;
		float lat = q.y;
		float turb = fbm(vec2(lon * 3.0, lat * 9.0), 31.0) - 0.5;
		float b = lat * 5.0 + turb * 1.6 + 0.4 * sin(lon * 2.0 + lat * 7.0);
		vec3 pc = band_colour(int(floor(fract(b * 0.5) * 12.0)) % 12);
		float slon = fract((lon - 0.6) / 6.2832 + 0.5) - 0.5;
		float sd = pow(slon * 6.2832 / 0.35, 2.0) + pow((lat - 0.32) / 0.12, 2.0);
		if (sd < 1.0) pc = sd < 0.45 ? rgb(102.0, 190.0, 234.0) : rgb(46.0, 133.0, 195.0);
		float lit = -1.0;
		float rim = 0.0;
		if (sun.z > 0.5) {
			float k = clamp((m - 360.0) / 780.0, 0.0, 1.0);
			float depth = event == 1 ? 70.0 * cos(PI * clamp(k * 2.0, 0.0, 2.0)) : 70.0 * cos(PI * k);
			vec3 L = normalize(vec3(sun.x - GIANT.x, sun.y - GIANT.y, depth));
			lit = q.x * L.x + q.y * L.y + z * L.z;
			vec2 sd2 = sun.xy - GIANT;
			float sl = length(sd2);
			float near = clamp(1.0 - (sl - GIANT_R) / 60.0, 0.0, 1.0);
			float facing = clamp(dot(q, sd2) / sl, 0.0, 1.0);
			rim = floor(clamp(1.0 - z * 3.0, 0.0, 1.0) * facing * near * 3.0) / 3.0;
		}
		float shade = floor(clamp(lit * 1.4 + 0.3, 0.0, 1.0) * 5.0) / 5.0 * 0.82 + 0.18;
		pc = pc * shade + rgb(10.0, 20.0, 50.0) * (1.0 - shade) * 0.6 + rgb(255.0, 190.0, 110.0) * rim * 0.9;
		if (event == 5 && night > 0.2) {   // aurora over the pole
			float a = clamp(1.0 - abs(lat + 0.62 + 0.05 * sin(lon * 9.0 + t * 0.8)) / 0.08, 0.0, 1.0);
			pc += rgb(90.0, 255.0, 160.0) * a * 0.7 * night;
		}
		if (event == 4) {   // the small moon's shadow
			vec2 mo = vec2(GIANT.x - 40.0 + 80.0 * clamp((m - 600.0) / 360.0, 0.0, 1.0), 22.0);
			vec2 ds = p - mo - vec2(3.0, 4.0);
			if (dot(ds, ds) < 9.0) pc *= 0.35;
		}
		col = pc;
	}
	if (event == 4) {   // a small moon crossing in front, 10:00 to 16:00
		vec2 mo = vec2(GIANT.x - 40.0 + 80.0 * clamp((m - 600.0) / 360.0, 0.0, 1.0), 22.0);
		vec2 dm = p - mo;
		if (dot(dm, dm) < 9.0) col = (dm.x < -1.0 && dm.y < -1.0) ? rgb(120.0, 115.0, 125.0) : rgb(60.0, 58.0, 70.0);
	}
	// shooting stars: now and then all day, more at night, showers on meteor days
	float period = event == 3 ? 1.6 : (night > 0.5 ? 7.0 : 14.0);
	int layers = event == 3 ? 2 : 1;
	for (int layer = 0; layer < 2; layer++) {
		if (layer >= layers) break;
		float fl = float(layer);
		float slot = floor(t / period + fl * 0.5);
		float ph = fract(t / period + fl * 0.5);
		bool go = hash1(slot * 91.7 + fl * 13.0) < (event == 3 ? 0.9 : 0.6);
		if (go && ph < 0.3) {
			vec2 start = vec2(40.0 + 820.0 * hash1(slot * 12.3 + fl), 4.0 + 16.0 * hash1(slot * 45.1 + fl));
			float dirx = hash1(slot * 7.7 + 3.0) < 0.5 ? -1.0 : 1.0;
			float prog = ph / 0.3 * 40.0;
			vec2 a = p - (start + vec2(dirx * prog, prog * 0.45));
			float along = -(a.x * dirx + a.y * 0.45) / sqrt(1.2025);
			float across = abs(a.x * 0.45 - a.y * dirx) / sqrt(1.2025);
			if (along >= 0.0 && along < 12.0 && across < 0.7) {
				col += rgb(220.0, 235.0, 255.0) * clamp(1.0 - along / 12.0, 0.0, 1.0) * clamp(1.0 - (ph / 0.3 - 0.7) / 0.3, 0.0, 1.0);
			}
		}
	}
	vec4 frame = texture(TEXTURE, UV);
	COLOR = vec4(mix(clamp(col, 0.0, 1.0), frame.rgb, frame.a), 1.0) * tint;
}
