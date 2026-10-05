export const saucePourFragment=`precision highp float;
uniform vec2 resolution;
uniform float time;
uniform float cardRatio;
uniform float cardHeight;
uniform float landingRatio;
#define PI 3.14159265359
float smin(float a,float b,float k){float h=max(k-abs(a-b),0.)/k;return min(a,b)-h*h*k*.25;}
float ellipsoid(vec3 p,vec3 r){float a=length(p/r),b=length(p/(r*r));return a*(a-1.)/max(b,.001);}
float hash(vec3 p){p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);}
float noise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
float phase;float flow;float amount;float edge;float bottomY;
vec2 center(float y){float fall=4.-y;float bend=exp(-y*5.);return vec2(.014*sin(fall*3.4-time*2.8)+.075*bend*cos(time*3.7-y*17.),.011*sin(fall*4.-time*2.3)+.060*bend*sin(time*3.7-y*17.));}
float field(vec3 p){
 float radius=length(p.xz),angle=atan(p.z,p.x);
 float spread=.14+edge*1.025*amount;
 vec3 q=p-vec3(.015,.092,0.);
 // A contact meniscus with an irregular advancing rim, not a rigid disk.
 float rim=1.+.025*sin(angle*5.+1.)+.013*sin(angle*9.-2.);
 float wave=.008*sin(radius*30.-time*3.1)*exp(-radius*1.3)*flow;
 q.y-=wave+.012*sin(p.x*9.+p.z*6.)*amount;
 float pool=ellipsoid(q,vec3(spread*rim,.085+.025*amount,(.25+.06*amount)*rim));
 pool=max(pool,abs(p.x)-edge);
 float y=p.y;
 float r=(.195/sqrt(1.+max(0.,3.8-y)*.32))*(1.+.025*sin(y*9.-time*7.)+.012*sin(y*21.-time*13.));
 // The shut-off travels down the stream rather than shrinking its whole width.
 float bottom=3.85-min(3.85,max(0.,phase-.2)*5.);
 float top=6.;
 float stream=max(length(p.xz-center(y))-r,max(bottom-y,y-top));
 if(phase<.2||top<.06)stream=10.;
 float d=smin(pool,stream,.10);
 // Coiled syrup folds near impact; viscosity prevents a water-like splash.
 float coilAngle=atan(p.z,p.x),coilRadius=.18+.025*sin(coilAngle*2.-time*3.7);
 float foldY=.20+.035*sin(coilAngle-time*3.7)+.02*sin(coilAngle*2.-time*3.7);
 float fold=length(vec2(radius-coilRadius,p.y-foldY))-.055;
 d=smin(d,flow>.01?fold:10.,.045);
 float overflow=smoothstep(.86,.98,amount);
 for(int side=0;side<2;side++){
  float signX=side==0?-1.:1.;float offset=float(side)*1.73;
  float cycle=mod(max(0.,time-7.)+offset,2.8);
  float lengthDown=min(-bottomY+.05,max(0.,time-7.+offset*.3)*.7)*overflow;
  float sideX=signX*(edge*(1.+max(-p.y,0.)*.041)+.024*(1.-exp(-max(-p.y,0.)*8.))); 
  float thickness=(.029+.004*sin(p.y*5.+time*1.6+offset))*(.3+.7*overflow);
  vec2 sideCenter=vec2(sideX,.02);
  float ribbon=max(length(p.xz-sideCenter)-thickness,max(p.y-.11,-lengthDown-p.y));
  float bulb=ellipsoid(p-vec3(signX*(edge*(1.+lengthDown*.041)+.024),-lengthDown,.02),vec3(.055,.105,.052));
  if(overflow>.01){d=smin(d,ribbon,.06);d=smin(d,bulb,.035);}
  // Detached drops accelerate under gravity, outside the card gutters.
  float dropTime=mod(time+offset,1.45),dropY=bottomY-.15-dropTime*dropTime*1.7;
  vec3 drop=vec3(signX*(edge*(1.-dropY*.041)+.04),dropY,.02);
  if(time>7.-bottomY/.7)d=min(d,ellipsoid(p-drop,vec3(.035,.065,.035))); 
 }
 return d;
}
vec3 normalAt(vec3 p){const float e=.0009;return normalize(vec3(field(p+vec3(e,0,0))-field(p-vec3(e,0,0)),field(p+vec3(0,e,0))-field(p-vec3(0,e,0)),field(p+vec3(0,0,e))-field(p-vec3(0,0,e))));}
float rect(vec3 r,vec3 c,vec2 size,float softness){vec3 n=normalize(c),u=normalize(cross(vec3(0,1,0),n)),v=cross(n,u);float front=dot(r,n);vec2 pos=vec2(dot(r,u),dot(r,v))/max(front,.01);vec2 edge=abs(pos)-size;return (1.-smoothstep(-softness,softness,max(edge.x,edge.y)))*step(.0,front);}
vec3 environment(vec3 r){
 vec3 sky=mix(vec3(.016,.012,.010),vec3(.22,.18,.15),smoothstep(-.5,1.,r.y));
 sky+=vec3(16.,15.,13.)*rect(r,vec3(-1.1,1.4,1.8),vec2(.25,.75),.045);
 sky+=vec3(5.,5.3,5.8)*rect(r,vec3(1.5,.9,1.3),vec2(.15,.48),.035);
 sky+=vec3(.65,.34,.15)*rect(r,vec3(-1.,.3,-1.),vec2(.35,.55),.07);
 sky+=vec3(11.,10.,9.)*rect(r,vec3(.0,.48,-1.5),vec2(.7,.12),.045);
 return sky;
}
float shadow(vec3 p,vec3 l){float visibility=1.,t=.018;for(int i=0;i<22;i++){float h=field(p+l*t);visibility=min(visibility,12.*h/t);t+=clamp(h,.025,.13);}return clamp(visibility,.18,1.);}
void main(){
 phase=time;flow=smoothstep(.7,1.2,phase);amount=(1.-exp(-max(phase-.95,0.)*.35));
 edge=cardRatio*(resolution.x/resolution.y)*.5*8.827/1.15;
 float bottomV=.0973-cardHeight;bottomY=(bottomV*8.827-1.15*.747)/(1.15*.932+bottomV*.362);
 vec2 uv=(gl_FragCoord.xy-.5*resolution)/resolution.y;
 uv.y+=.0973-(.5-landingRatio);
 vec3 ro=vec3(0.,2.5,8.5),target=vec3(0.,-.8,0.);
 vec3 w=normalize(target-ro),u=normalize(cross(w,vec3(0.,1.,0.))),v=cross(u,w),rd=normalize(uv.x*u+uv.y*v+w*1.15);
 float travel=0.;vec3 p;bool hit=false;
 for(int i=0;i<128;i++){p=ro+travel*rd;float d=field(p);if(d<.00085){hit=true;break;}travel+=max(d*.82,.0005);if(travel>16.)break;}
 float fade=1.;
 if(!hit){float plane=-ro.y/rd.y;vec3 ground=ro+rd*plane;float contact=exp(-dot(ground.xz/vec2(1.15,.7),ground.xz/vec2(1.15,.7))*3.)*.24*amount;gl_FragColor=vec4(.015,.008,.005,contact*fade);return;}
 vec3 n=normalAt(p),view=-rd,light=normalize(vec3(-2.,4.,3.));
 float fleck=noise(vec3(p.x*135.,(p.y-time*.45)*135.,p.z*135.));
 float subtle=noise(p*22.+vec3(0,-time*.4,0));
 vec3 albedo=mix(vec3(.085,.005,.0015),vec3(.105,.008,.002),subtle);
 albedo*=1.-.12*smoothstep(.78,.9,fleck);
 float ndv=max(dot(n,view),.001),ndl=max(dot(n,light),0.);
 vec3 halfVector=normalize(light+view);float ndh=max(dot(n,halfVector),0.),vdh=max(dot(view,halfVector),0.);
 float roughness=.19+.025*fleck,alpha=roughness*roughness,a2=alpha*alpha;
 float D=a2/(PI*pow(ndh*ndh*(a2-1.)+1.,2.));float k=pow(roughness+1.,2.)/8.;float G=ndv/(ndv*(1.-k)+k)*ndl/(ndl*(1.-k)+k);
 float F=.035+.965*pow(1.-vdh,5.);float fr=.035+.965*pow(1.-ndv,5.);
 vec3 reflected=reflect(rd,n);vec3 specular=environment(reflected)*fr;
 float directSpec=D*G*F/max(4.*ndv*max(ndl,.001),.001);
 float occlusion=clamp(1.-max(0.,.11-field(p+n*.11))*.9,.72,1.);
 float visibility=shadow(p+n*.004,light);
 vec3 color=albedo*(.55+.9*ndl*visibility)*occlusion+specular+vec3(1.,.83,.65)*directSpec*ndl*.3;
 // Warm transmission at grazing edges gives the sauce its syrup-like depth.
 color+=vec3(.15,.025,.004)*pow(1.-ndv,3.)*max(dot(-n,light),0.);
 color=color/(1.+color);color=pow(color,vec3(1./2.2));
 gl_FragColor=vec4(color,fade);
}`;
