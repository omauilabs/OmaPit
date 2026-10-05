import React,{useEffect,useRef} from 'react';
import './visual-polish.css';
import {renderHeaderScene} from './HeaderScenes';
import {makeHeaderSprite,renderFalling} from './HeaderSprites';
const fract=n=>n-Math.floor(n),mix=(a,b,t)=>a+(b-a)*t;
function noise(x,y){const ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy,sx=fx*fx*(3-2*fx),sy=fy*fy*(3-2*fy);const h=(a,b)=>fract(Math.sin(a*127.1+b*311.7)*43758.5453);return mix(mix(h(ix,iy),h(ix+1,iy),sx),mix(h(ix,iy+1),h(ix+1,iy+1),sx),sy)}
export function HeaderFire({animate=true,variant='fire'}){
 const ref=useRef(null);
 useEffect(()=>{const canvas=ref.current,ctx=canvas.getContext('2d',{alpha:true});if(!ctx)return;let frame=0,last=-1,elapsed=2.4,previous=0,visible=true,disposed=false,buffer;const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const sprites=!['meats','utensils'].includes(variant)?[]:(variant==='meats'?['steak','ribs','drumstick','sausage']:['spatula','tongs','fork','brush']).map(makeHeaderSprite);
 function resize(){const rect=canvas.getBoundingClientRect();canvas.width=Math.max(1,Math.ceil(rect.width/2));canvas.height=Math.max(1,Math.ceil(rect.height/2));buffer=ctx.createImageData(canvas.width,canvas.height);render(elapsed)}
 function render(t){if(!buffer)return;if(['kitchen','smoke','backyard'].includes(variant)){renderHeaderScene(ctx,canvas.width,canvas.height,t,variant);return;}if(variant!=='fire'){renderFalling(ctx,canvas.width,canvas.height,t,sprites);return;}const w=canvas.width,h=canvas.height,p=buffer.data;
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){const z=1-y/h,n=noise(x*.085+Math.sin(t*.3),z*5+t*.85),fine=noise(x*.22,z*13+t*1.9),rise=noise(x*.036,z*3+t*.48);const tongues=.14+.24*noise(x*.095,t*.8)+.34*Math.pow(Math.max(0,Math.sin(x*.19+t*.9+n*4)),5)+.12*noise(x*.28,t*1.2);const edge=tongues-z+(n-.5)*.12+(fine-.5)*.085;let a=0,r=0,g=0,b=0;
   if(edge>0){const heat=Math.min(1,Math.max(0,edge*2.8+(1-z)*.14));r=235+heat*20;g=75+heat*180;b=12+Math.pow(heat,3)*110;a=Math.min(240,95+edge*720)*(0.55+fine*.45);const crease=Math.max(0,noise(x*.3+z*4,z*20+t*2.8)-.64);g*=1-crease*1.3;b*=1-crease*1.8}
   else{const smoke=Math.max(0,rise-.53)*Math.max(0,1-z)*22;r=111;g=91;b=82;a=smoke}
   if(z<.065){r=190+fine*60;g=35+fine*80;b=9;a=Math.max(a,70+fine*100)}const i=(y*w+x)*4;p[i]=r;p[i+1]=g;p[i+2]=b;p[i+3]=a;
  }ctx.putImageData(buffer,0,0);for(let i=0;i<42;i++){const progress=fract(t*(.075+(i%7)*.008)+i*.618),x=(fract(i*.754877)+Math.sin(t*.7+i)*.01)*w,y=h*(1-progress);ctx.fillStyle=`rgba(255,${Math.round(120+70*(1-progress))},55,${(1-progress)*.7})`;ctx.fillRect(Math.round(x),Math.round(y),i%9===0?2:1,1)}
 }
 function tick(time){frame=0;if(disposed||!animate||reduced.matches||document.hidden||!visible)return;elapsed+=previous?Math.min((time-previous)/1000,.05):0;previous=time;
  const fps=['kitchen','backyard','meats','utensils'].includes(variant)?60:30,bucket=Math.floor(elapsed*fps);
  if(bucket!==last){render(elapsed);last=bucket}frame=requestAnimationFrame(tick)}
 function sync(){cancelAnimationFrame(frame);frame=0;previous=0;if(animate&&!reduced.matches&&!document.hidden&&visible)frame=requestAnimationFrame(tick);else render(elapsed)}
 const observer=new ResizeObserver(resize),intersection=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync()});observer.observe(canvas.parentElement);intersection.observe(canvas);reduced.addEventListener('change',sync);document.addEventListener('visibilitychange',sync);resize();sync();return()=>{disposed=true;cancelAnimationFrame(frame);observer.disconnect();intersection.disconnect();reduced.removeEventListener('change',sync);document.removeEventListener('visibilitychange',sync)};
 },[animate,variant]);return <canvas ref={ref} className="header-pixel-fire" aria-hidden="true"/>;
}
