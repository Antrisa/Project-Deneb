shader_type canvas_item;
// Leaf sway for plants and trees (cozy art pass, 21 Nov 2026). The top of the picture leans by whole art
// pixels and the base stays put, so it reads as a breeze, not a wobble. Each piece starts at its own phase.
uniform float amount = 1.0;   // art pixels of lean at the very top
uniform float speed = 0.9;

void vertex() {
	float top = 1.0 - UV.y;
	float phase = MODEL_MATRIX[3].x * 0.05 + MODEL_MATRIX[3].y * 0.031;
	float lean = 0.65 * sin(TIME * speed + phase) + 0.35 * sin(TIME * speed * 0.41 + phase * 1.7);
	VERTEX.x += round(lean * amount) * top;
}
