import React,{useEffect,useRef} from 'react';

const saucePalettes={
 herb:['#172b12','#304322','#506238','#708849','#8aa563','#b1c783'],
 kc:['#431a12','#642318','#84301c','#a84222','#c56230','#ec9950'],
 east:['#54341a','#84572a','#ac7839','#c49852','#deb774','#f4d59b'],
 lexington:['#492016','#71331d','#974729','#b66038','#d17d4e','#eca778'],
 gold:['#64420a','#956710','#bc8b19','#dba82e','#edc455','#ffe497'],
 white:['#817666','#aaa18e','#d0c7b4','#e4ddcb','#f3eddc','#fffbed'],
 memphis:['#3e1711','#601f15','#802b1b','#a13a24','#c05636','#e18456'],
 texas:['#38251a','#593b25','#7d5432','#a07548','#bf9866','#dfbf8d'],
 kentucky:['#170e0b','#2c1a13','#43291d','#61402b','#86603f','#b18a5c']
};

// Fine square-pixel rendering: preserve the silhouette while adding surface detail.
function drawSauce(ctx,w,h,edge,left,right,time,palette,streamX){
 ctx.clearRect(0,0,w,h);left=Math.round(left);right=Math.round(right);edge=Math.round(edge);
 const pixel=(x,y,shade)=>{ctx.fillStyle=palette[Math.max(0,Math.min(5,shade))];ctx.fillRect(Math.round(x),Math.round(y),1,1)};
 const center=Math.round(streamX??(left+right)/2),spread=Math.min(Math.max(center-left,right-center),16+time*38);
 for(let y=0;y<=edge;y++){
  const bend=Math.sin(y*.035-time*1.4)*1.5,radius=10+Math.sin(y*.045-time*2)*1.2;
  for(let dx=-Math.ceil(radius);dx<=radius;dx++){
   const u=dx/radius;if(Math.abs(u)>1)continue;
   const ribbon=Math.sin(y*.075-time*5+dx*.11),grain=Math.sin(y*1.71+dx*2.19);
   let shade=Math.abs(u)>.87?0:u>.55?1:u<-.55?3:2;
   if(u>-.55&&u<-.28)shade=ribbon>.25?5:4;
   if(u>.1&&u<.3&&ribbon>.8)shade=3;
   if(grain>.96&&Math.abs(u)<.7)shade=Math.min(4,shade+1);
   pixel(center+dx+bend,y,shade);
  }
 }
 const start=Math.ceil(Math.max(left+7,center-spread)),end=Math.floor(Math.min(right-7,center+spread));
 for(let x=start;x<=end;x++){
  const distance=Math.abs(x-center)/Math.max(1,spread),depth=Math.max(3,Math.round(4+7*(1-distance)+Math.sin(x*.085-time*1.7)*1.2));
  for(let y=-depth;y<=3;y++){
   const wave=Math.sin(Math.abs(x-center)*.14-time*4+y*.6);
   pixel(x,edge+y,y===-depth?4:y>1?0:y===-depth+1?3:wave>.85&&y<0?3:2);
  }
 }
 // Low viscous impact mound, concentric ripples and small airborne flecks.
 for(let x=-15;x<=15;x++)for(let y=-7;y<=0;y++)if(x*x/225+y*y/49<1)pixel(center+x,edge+y,y===-6?4:x<-5?3:2);
 for(const side of [-1,1]){
  const phase=(time*1.4+(side>0?.47:0))%1;
  const x=center+side*(12+phase*19),y=edge-5-Math.sin(phase*Math.PI)*11;
  for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++)if(dx*dx+dy*dy<=1)pixel(x+dx,y+dy,dx<0?4:2);
  if(side<0?center-spread>left+2:center+spread<right-2)continue;
  const boundary=side<0?left:right,offset=side<0?0:.46,xrun=boundary+side;
  // One continuous quarter-annulus: the top lip bends into the vertical runoff.
  // Mirror the same geometry on both sides; no square patch or diagonal wedge.
  const cornerX=boundary-side*7,cornerY=edge+7;
  for(let dy=-12;dy<=0;dy++)for(let dx=0;dx<=12;dx++){
   const radius=Math.hypot(dx,dy);
   if(radius<4||radius>12)continue;
   pixel(cornerX+side*dx,cornerY+dy,radius>10.5?0:radius<6?4:2);
  }
  const length=35+Math.sin(time*1.7+offset*6)*11;
  for(let y=7;y<length;y++){
   const radius=4+Math.sin(y*.09-time*2)*.8;
   for(let dx=-Math.ceil(radius);dx<=radius;dx++)if(Math.abs(dx)<=radius)pixel(xrun+dx,edge+y,dx<-2?4:dx>2?0:2);
  }
  for(let dy=-5;dy<=8;dy++){
   const radius=Math.sqrt(Math.max(0,1-((dy-1)/8)**2))*6;
   for(let dx=-Math.ceil(radius);dx<=radius;dx++)if(Math.abs(dx)<=radius)pixel(xrun+dx,edge+length+dy,dx<-2?4:dx>3?1:2);
  }
  for(let drop=0;drop<3;drop++){
   const phase=(time*.48+offset+drop/3)%1,fall=phase*phase,dy=edge+length+17+fall*Math.max(0,h-edge-length-26),cx=xrun+side*fall*3;
   for(let yy=-4;yy<=5;yy++)for(let xx=-3;xx<=3;xx++)if(xx*xx/10+yy*yy/26<=1)pixel(cx+xx,dy+yy,xx<-1?4:xx>1?1:2);
  }
 }
}
export default function SaucePourTest({sauceId,animate=true}){
 const reduced=useRef(window.matchMedia('(prefers-reduced-motion: reduce)').matches),canvas=useRef(null),clock=useRef({elapsed:12,running:animate&&!reduced.current});

 useEffect(()=>{
  const c=canvas.current,scene=c.parentElement,card=c.closest('.sauce-story'),nav=document.querySelector('.context-nav'),ctx=c.getContext('2d');
  let visible=true,frame=0,previous=performance.now(),last=-1,geometry;
  const media=window.matchMedia('(prefers-reduced-motion: reduce)');
  const motionChanged=()=>{reduced.current=media.matches;clock.current.running=animate&&!media.matches;previous=performance.now();last=-1};motionChanged();media.addEventListener('change',motionChanged);
  const measure=()=>{
   const box=card.getBoundingClientRect(),navBox=nav?.getBoundingClientRect();
   const top=Math.min(-32,(navBox?.bottom??box.top-110)-box.top),padding=20,height=-top+Math.min(box.height+45,460);
   scene.style.top=`${top}px`;scene.style.left=`-${padding}px`;scene.style.width=`${box.width+padding*2}px`;scene.style.height=`${height}px`;
   const cell=1.25; c.width=Math.ceil((box.width+padding*2)/cell);c.height=Math.ceil(height/cell);
   geometry={edge:-top/cell,left:padding/cell,right:(padding+box.width)/cell,streamX:innerWidth<700?(padding+box.width-26)/cell:undefined};last=-1;
  };
  const resize=new ResizeObserver(measure);resize.observe(card);if(nav)resize.observe(nav);measure();
  const intersection=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;previous=performance.now();last=-1});intersection.observe(c);
  const draw=now=>{
   const dt=Math.min((now-previous)/1000,.1);previous=now;
   if(clock.current.running&&visible&&!document.hidden)clock.current.elapsed+=dt;
   const tick=Math.floor(clock.current.elapsed*60);
   if(visible&&!document.hidden&&tick!==last&&geometry){drawSauce(ctx,c.width,c.height,geometry.edge,geometry.left,geometry.right,clock.current.elapsed,saucePalettes[sauceId]||saucePalettes.kc,geometry.streamX);last=tick;}
   frame=requestAnimationFrame(draw);
  };frame=requestAnimationFrame(draw);
  return()=>{cancelAnimationFrame(frame);resize.disconnect();intersection.disconnect();media.removeEventListener('change',motionChanged)};
 },[sauceId,animate]);
 return <div className="sauce-pour-scene pixel-sauce-pour" aria-hidden="true"><canvas ref={canvas}/></div>;
}
