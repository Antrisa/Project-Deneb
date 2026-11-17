shader_type canvas_item;
render_mode unshaded;

// Frame-local UVs support the existing four-direction, three-row NPC atlas.
uniform vec2 sheet_grid = vec2(4.0, 3.0);
uniform float fade_start : hint_range(0.0, 1.0) = 0.43;
uniform float fade_end : hint_range(0.0, 1.0) = 0.81;
uniform float opacity : hint_range(0.0, 1.0) = 0.83;
uniform float scan_speed = 0.32;
uniform float phase = 0.0;
uniform vec4 hologram_color : source_color = vec4(0.35, 0.90, 1.0, 1.0);

void fragment() {
    vec2 local_uv = fract(UV * sheet_grid);
    vec4 source = texture(TEXTURE, UV);
    float t = TIME + phase;
    float fade = 1.0 - smoothstep(fade_start, max(fade_start + 0.01, fade_end), local_uv.y);
    float rows = 1.0 / (TEXTURE_PIXEL_SIZE.y * sheet_grid.y);
    float scan = mix(0.79, 1.0, step(0.28, fract(local_uv.y * rows * 0.5 - t * 1.8)));
    float sweep_pos = fract(t * scan_speed);
    float sweep = 1.0 - smoothstep(0.0, 0.055, abs(local_uv.y - sweep_pos));
    float pulse = 0.96 + 0.04 * sin(t * 3.2);
    float luminance = dot(source.rgb, vec3(0.2126, 0.7152, 0.0722));
    vec3 tint = mix(source.rgb, hologram_color.rgb * (0.40 + 0.75 * luminance), 0.68);
    tint += hologram_color.rgb * sweep * 0.13;
    COLOR = vec4(tint, source.a * fade * scan * pulse * opacity);
}
