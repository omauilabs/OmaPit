import React,{useEffect,useRef,useState} from 'react';
const vertex=`attribute vec2 position; varying vec2 uv; void main(){uv=position*.5+.5;gl_Position=vec4(position,0.,1.);}`;
const fragment=`precision highp float;
varying vec2 uv; uniform float time; uniform vec2 resolution; uniform float mode;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<5;i++){v+=a*noise(p);p=p*2.03+vec2(13.1,7.7);a*=.5;}return v;}
void main(){
 vec2 p=uv;float t=time;
 if(mode<.5){
  // Buoyant, turbulent plume: wide fuel base, narrow intermittent tongues.
  float y=p.y;float drift=.055*sin(y*9.-t*2.)*y;
  float n=fbm(vec2((p.x-.5)*6.,y*5.-t*2.3));
  float detail=fbm(vec2(p.x*15.,y*12.-t*3.8));
  float width=.28*pow(max(0.,1.-y),.72);
  float field=width-abs(p.x-.5-drift)+(n-.5)*.23+(detail-.5)*.05;
  float envelope=smoothstep(.02,.13,y)*(1.-smoothstep(.78,.98,y));
  float body=smoothstep(-.025,.055,field)*envelope;
  float heat=clamp((field+.02)*4.6+(1.-y)*.27,0.,1.);
  vec3 color=mix(vec3(.95,.10,.012),vec3(1.,.57,.045),smoothstep(.08,.5,heat));
  color=mix(color,vec3(1.,.94,.64),smoothstep(.6,.95,heat));
  float glow=exp(-abs(p.x-.5-drift)*11.)*exp(-abs(y-.3)*4.)*.16;
  float alpha=clamp(body+glow,0.,1.);
  gl_FragColor=vec4((color*body+vec3(1.,.22,.035)*glow)/max(alpha,.001),alpha);
 }else{
  vec3 rgb=vec3(0.);float alpha=0.;
  // Smoke advects upward from the food, widening into irregular wisps.
  for(int i=0;i<3;i++){
   float k=float(i);float age=fract(t*.075+k*.333);float yy=.40+age*.52;
   float xx=.48+sin(age*5.+k*2.+t*.12)*.05+age*.11;
   vec2 q=(p-vec2(xx,yy))/vec2(.09+age*.13,.10+age*.14);
   float density=exp(-dot(q,q)*1.7);
   float curl=fbm(p*vec2(11.,16.)+vec2(k*3.,-t*.22));
   float smoke=density*smoothstep(.30,.72,curl)*sin(age*3.14159)*.46;
   rgb+=vec3(.57,.61,.68)*smoke;alpha+=smoke;
  }
  // Independent ballistic ember particles rise off the charcoal bed.
  for(int i=0;i<24;i++){
   float k=float(i),seed=hash(vec2(k,3.));float age=fract(t*(.13+seed*.12)+seed);
   vec2 origin=vec2(.36+hash(vec2(k,7.))*.075,.32+hash(vec2(k,9.))*.20);
   vec2 pos=origin+vec2(sin(age*6.+k)*.018+age*(seed-.35)*.16,age*(.36+seed*.20));
   vec2 delta=(p-pos)*resolution;delta.y*=.65;float radius=.6+seed*.8;
   float spark=exp(-dot(delta,delta)/(radius*radius))*pow(1.-age,1.5);
   float halo=exp(-dot(delta,delta)/(radius*radius*15.))*pow(1.-age,2.)*.20;
   rgb+=vec3(1.,.38+.4*(1.-age),.07)*(spark+halo);alpha+=spark+halo;
  }
  gl_FragColor=vec4(rgb/max(alpha,.001),clamp(alpha,0.,.8));
 }
}`;
/** Decorative GPU effect; never uses temperature data to imply a measured fire. */
export function FireEffect({kind='logo',className='',animate=true}){
 const canvasRef=useRef(null),[fallback,setFallback]=useState(false);
 useEffect(()=>{
  const canvas=canvasRef.current;let gl,program,buffer,raf,observer;let disposed=false,visible=true,lost=false,last=0,start=performance.now();
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const stop=()=>{if(raf)cancelAnimationFrame(raf);raf=0};
  const compile=(type,source)=>{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){const e=gl.getShaderInfoLog(s);gl.deleteShader(s);throw Error(e)}return s};
  const init=()=>{
   gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:false,antialias:false,powerPreference:'low-power'});
   if(!gl){setFallback(true);return false}
   const v=compile(gl.VERTEX_SHADER,vertex),f=compile(gl.FRAGMENT_SHADER,fragment);program=gl.createProgram();gl.attachShader(program,v);gl.attachShader(program,f);gl.linkProgram(program);gl.deleteShader(v);gl.deleteShader(f);
   if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));
   buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);gl.useProgram(program);const p=gl.getAttribLocation(program,'position');gl.enableVertexAttribArray(p);gl.vertexAttribPointer(p,2,gl.FLOAT,false,0,0);setFallback(false);return true;
  };
  const render=now=>{
   raf=0;if(disposed||lost||!gl||!visible||document.hidden)return;
   if(now-last>=33||reduced.matches||!animate){last=now;const r=canvas.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,matchMedia('(max-width:700px)').matches?1:1.5);const w=Math.max(1,Math.round(r.width*dpr)),h=Math.max(1,Math.round(r.height*dpr));if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h}gl.viewport(0,0,w,h);gl.useProgram(program);gl.uniform1f(gl.getUniformLocation(program,'time'),(reduced.matches||!animate)?3.2:(now-start)/1000);gl.uniform2f(gl.getUniformLocation(program,'resolution'),w,h);gl.uniform1f(gl.getUniformLocation(program,'mode'),kind==='logo'?0:1);gl.drawArrays(gl.TRIANGLES,0,6);canvas.dataset.rendered='true';canvas.dataset.motion=(reduced.matches||!animate)?'still':'animated';canvas.dataset.frames=String(Number(canvas.dataset.frames||0)+1);}
   if(!reduced.matches&&animate)raf=requestAnimationFrame(render);
  };
  const resume=()=>{stop();if(!disposed&&!lost)raf=requestAnimationFrame(render)};
  const onLost=e=>{e.preventDefault();lost=true;stop();setFallback(true)};
  const onRestored=()=>{lost=false;try{if(init())resume()}catch{setFallback(true)}};
  canvas.addEventListener('webglcontextlost',onLost);canvas.addEventListener('webglcontextrestored',onRestored);
  document.addEventListener('visibilitychange',resume);reduced.addEventListener('change',resume);
  observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;resume()});observer.observe(canvas);
  try{if(init())resume()}catch(e){console.warn('OmaPit fire effect unavailable:',e.message);setFallback(true)}
  return()=>{disposed=true;stop();observer.disconnect();document.removeEventListener('visibilitychange',resume);reduced.removeEventListener('change',resume);canvas.removeEventListener('webglcontextlost',onLost);canvas.removeEventListener('webglcontextrestored',onRestored);if(gl&&!lost){gl.deleteBuffer(buffer);gl.deleteProgram(program)}};
 },[kind,animate]);
 return <span className={`fire-effect ${kind} ${className} ${fallback?'effect-fallback':''}`} aria-hidden="true"><canvas ref={canvasRef}/>{kind==='logo'&&<svg className="fire-fallback" viewBox="0 0 32 40"><path d="M17 1C19 12 29 15 29 26a13 13 0 0 1-26 0C3 19 9 12 11 7c-1 9 4 11 6 3z" fill="#e0af68"/><path d="M16 20c4 5 7 7 6 11-1 7-12 7-13 0-1-4 4-7 7-11" fill="#fff0bf"/></svg>}</span>
}
