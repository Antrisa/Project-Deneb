shader_type canvas_item;

uniform int frame = 0;

varying vec4 tint;

void vertex() {
	tint = COLOR;
}

void fragment() {
	vec2 atlas_uv = vec2(UV.x, (float(frame) + UV.y) / 32.0);
	COLOR = texture(TEXTURE, atlas_uv) * tint;
}
