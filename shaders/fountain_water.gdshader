shader_type canvas_item;
uniform float strength = 0.10;
void fragment() {
    vec4 c = texture(TEXTURE, UV);
    float water = smoothstep(0.08, 0.22, min(c.b, c.g) - c.r);
    float wave = sin(UV.y * 62.0 - TIME * 3.0) * sin(UV.x * 39.0 + TIME * 1.7);
    c.rgb += vec3(0.15, 0.7, 0.9) * wave * strength * water;
    COLOR = c;
}
