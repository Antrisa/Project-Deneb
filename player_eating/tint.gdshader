shader_type canvas_item;
render_mode unshaded;
uniform sampler2D tint_mask : filter_nearest, repeat_disable;
uniform vec4 fabric : source_color;
uniform vec4 skin : source_color;
uniform vec4 eyes : source_color;
varying vec4 sprite_modulate;
void vertex() {
    sprite_modulate = COLOR;
}
void fragment() {
    vec4 pixel = texture(TEXTURE, UV);
    vec4 mask = texture(tint_mask, UV);
    if (mask.a > 0.5) {
        // Echo Landing: the same recolouring as scripts/player_maker.gd, so the eating frames match the walk
        // sheet. Brightness over a "full colour" level of 140 for the layer's own colour, 185 for skin and
        // 150 for eyes (out of 255). The pack's version used the red channel over 128 for all three, which
        // made skin about 45 percent brighter while eating.
        float lum = dot(pixel.rgb, vec3(0.2126, 0.7152, 0.0722));
        vec3 dye = mask.r > 0.5 ? fabric.rgb : (mask.g > 0.5 ? skin.rgb : eyes.rgb);
        float full = mask.r > 0.5 ? 140.0 : (mask.g > 0.5 ? 185.0 : 150.0);
        bool painted = mask.b > 0.24 && mask.b < 0.26 && (mask.r > 0.5 || mask.g > 0.5);
        vec3 shades = painted ? pixel.rgb : vec3(lum);
        pixel.rgb = clamp(dye * shades * (255.0 / full), vec3(0.0), vec3(1.0));
    }
    COLOR = pixel * sprite_modulate;
}
