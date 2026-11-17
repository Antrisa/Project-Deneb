shader_type canvas_item;
uniform float opening = 0.0;
void fragment(){
 vec2 uv=UV;
 vec4 c=texture(TEXTURE,uv);
 // Only glass leaves slide. Frame, sign and pilasters remain stationary.
 if(uv.x>0.21 && uv.x<0.82 && uv.y>0.42 && uv.y<0.94){
  float center=0.515;
  float travel=opening*0.305;
  if(abs(uv.x-center)<travel)c=vec4(0.12,0.17,0.20,1.0);
  else {uv.x+=uv.x<center?travel:-travel;c=texture(TEXTURE,uv);}
 }
 COLOR=c;
}
