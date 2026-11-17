shader_type canvas_item;
void fragment(){
 vec4 c=texture(TEXTURE,UV);
 float teal=smoothstep(0.12,0.35,min(c.g,c.b)-c.r);
 float amber=smoothstep(0.25,0.65,c.r-c.b)*smoothstep(0.6,0.9,c.r);
 c.rgb*=1.0+teal*0.06*sin(TIME*1.4)+amber*0.025*sin(TIME*0.8);
 COLOR=c;
}
