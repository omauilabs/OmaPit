import React,{useEffect,useRef} from 'react';
const glyphs=[
 ['0111110','1100011','1100011','1100011','1100011','1100011','1100011','1100011','0111110'],
 ['000000000','000000000','110110110','111111111','110010011','110010011','110010011','110010011','110010011'],
 ['0000000','0000000','0111100','0000110','0111110','1100110','1100110','1100110','0111111'],
 ['1111110','1100011','1100011','1100011','1111110','1100000','1100000','1100000','1100000'],
 ['110','110','000','110','110','110','110','110','110'],
 ['01100','01100','11111','01100','01100','01100','01100','01100','00111']
];
const cells=[];let cursor=0;
for(const glyph of glyphs){glyph.forEach((row,y)=>[...row].forEach((v,x)=>{if(v==='1')cells.push([cursor+x,y])}));cursor+=glyph[0].length+1;}
const hash=(x,y)=>{const v=Math.sin(x*127.1+y*311.7)*43758.5453;return v-Math.floor(v)};
function paint(ctx,t){
 ctx.clearRect(0,0,224,80);const size=4,startX=(224-(cursor-1)*size)/2,startY=31;
 const rect=(x,y,w,h,color)=>{ctx.fillStyle=color;ctx.fillRect(Math.round(x),Math.round(y),w,h)};
 // One continuous bed of fire rises behind the word; glyphs are painted last.
 const width=(cursor-1)*size;
 for(let x=-8;x<width+8;x+=2){
  const nx=x/width,envelope=Math.max(0,Math.sin(Math.PI*Math.max(0,Math.min(1,nx))));
  const height=21+envelope*19+Math.sin(x*.15+t*2.1)*5+Math.sin(x*.33-t*3.2)*3;
  const top=68-height;
  for(let y=Math.ceil(top);y<70;y++){
   const heat=(y-top)/Math.max(1,70-top),ripple=Math.sin(x*.27+y*.21-t*3.1)*.5+.5;
   const alpha=Math.min(.94,heat*1.5)*(.55+ripple*.4)*Math.min(1,envelope*3);
   rect(startX+x+Math.sin(y*.16+t*1.7)*1.2,y,2,1,`rgba(255,${Math.round(60+heat*150)},${Math.round(14+heat*66)},${alpha})`);
  }
 }
 for(let i=0;i<18;i++){
  const p=(t/6+i*.618)%1,x=startX+((i*31)%width)+Math.sin(p*5+i)*2,y=65-p*56;
  rect(x,y,1,1,`rgba(255,192,91,${Math.sin(p*Math.PI)*.65})`);
 }
 // Deep cast-iron extrusion and a warm bevel around every hand-drawn glyph.
 for(const [x,y] of cells){const px=startX+x*size,py=startY+y*size;rect(px+2,py+3,size+1,size+1,'#211916');rect(px-1,py-1,size+2,size+2,'#8a5d35');}
 for(const [x,y] of cells){
  const px=startX+x*size,py=startY+y*size,n=hash(x,y),heat=(Math.sin(t*1.2+x*.28+y*.4)+1)/2;
  rect(px,py,size,size,`rgb(${Math.round(95+n*45+heat*32)},${Math.round(53+n*35+heat*16)},${Math.round(31+n*18)})`);
  rect(px,py,size,1,n>.4?'#d5ac6c':'#a78050');rect(px,py+1,1,2,'#bc9458');rect(px+3,py+1,1,3,'#4e3525');
  rect(px+1,py+2,1,1,n>.68?'#2c2926':'#7c6143');
  if(n>.82){rect(px+2,py+1,1,2,`rgba(255,${Math.round(111+heat*70)},42,${.45+heat*.5})`);}
 }
 // A coal-bed underline, wandering sparks and faint pixel smoke.
 for(let x=17;x<208;x+=3){const glow=(Math.sin(t*1.1+x*.21)+1)/2;rect(x,72,2,1,`rgba(229,${Math.round(85+glow*70)},38,${.3+glow*.6})`);}

}
export function PixelWordmark({animate=true}){
 const ref=useRef(null);
 useEffect(()=>{
  const c=ref.current,ctx=c.getContext('2d');if(!ctx)return;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');let frame=0,visible=true,last=-1,elapsed=2.4,previous=performance.now();
  const tick=now=>{const delta=Math.min((now-previous)/1000,.1);previous=now;elapsed+=delta;const bucket=Math.floor(elapsed*60);if(bucket!==last){paint(ctx,elapsed);last=bucket}frame=requestAnimationFrame(tick)};
  const sync=()=>{cancelAnimationFrame(frame);previous=performance.now();if(animate&&!reduced.matches&&visible&&!document.hidden)frame=requestAnimationFrame(tick);else paint(ctx,elapsed)};
  const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync()});observer.observe(c);reduced.addEventListener('change',sync);document.addEventListener('visibilitychange',sync);paint(ctx,elapsed);sync();
  return()=>{cancelAnimationFrame(frame);observer.disconnect();reduced.removeEventListener('change',sync);document.removeEventListener('visibilitychange',sync)};
 },[animate]);
 return <canvas className="pixel-wordmark brand-logo" width="224" height="80" ref={ref} aria-hidden="true"/>;
}
