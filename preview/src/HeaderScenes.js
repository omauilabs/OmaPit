const smokeBuffers=new WeakMap();
const fract=v=>v-Math.floor(v);
function cloudNoise(x,y){const ix=Math.floor(x),iy=Math.floor(y),u=x-ix,v=y-iy,a=u*u*(3-2*u),b=v*v*(3-2*v);const hash=(x,y)=>fract(Math.sin(x*127.1+y*311.7)*43758.5453);const top=hash(ix,iy)*(1-a)+hash(ix+1,iy)*a,bottom=hash(ix,iy+1)*(1-a)+hash(ix+1,iy+1)*a;return top*(1-b)+bottom*b;}
// Tiny stage sets drawn at native pixel resolution, with periodic choreography.
const tau=Math.PI*2;
function steam(ctx,x,y,t,shade='198,208,213',count=8){
 for(let i=0;i<count;i++){const p=((t/5+i/count)%1+1)%1,drift=Math.sin(p*5+i)*3;ctx.fillStyle=`rgba(${shade},${(1-p)*.25})`;const size=2+p*6;ctx.fillRect(Math.round(x+drift-size/2),Math.round(y-p*24),Math.ceil(size),Math.ceil(size*.65));}
}
function person(ctx,x,y,t,{chef=false,shirt='#9c563e',skin='#c3906c',action=0,flip=1,walking=false}={}){
 ctx.save();ctx.translate(Math.round(x),Math.round(y));ctx.scale(flip,1);
 const r=(a,b,w,h,c)=>{ctx.fillStyle=c;ctx.fillRect(Math.round(a),Math.round(b),w,h)},arm=Math.round(Math.sin(t*tau/6+action)*2);
 const stride=walking?Math.sin(t*tau/1.2)*3:0;
 r(-5-stride,28,4,15,'#252c35');r(2+stride,28,4,15,'#303844');r(-7-stride,41,7,3,'#131a21');r(2+stride,41,7,3,'#131a21');
 r(-7,11,14,19,chef?'#e4ded0':shirt);r(-6,13,3,15,chef?'#b8bdb7':'#ffffff18');r(5,13,2,16,'#0003');
 r(-4,2,9,10,skin);r(-5,0,10,4,'#39312b');r(3,4,3,3,skin);r(3,4,1,1,'#292c2d');r(-2,10,5,3,skin);
 if(chef){r(-5,-3,11,5,'#e5e5db');r(-6,-7,5,5,'#f5f0e1');r(-1,-9,5,7,'#fff6e5');r(4,-6,3,4,'#d7dbd4');r(0,14,1,1,'#6c7374');r(0,18,1,1,'#6c7374');r(0,22,1,1,'#6c7374');}
 else{r(-5,19,10,12,'#d4bd8b');r(-4,20,1,10,'#a49373');r(-5,18,10,2,'#685748');}
 r(-10,13,4,11,chef?'#cbd0c7':shirt);r(-9,24,4,3,skin);
 r(6,13,4,8,chef?'#f3eddf':shirt);r(8,18+arm,8,3,skin);r(15,17+arm,3,3,skin);r(17,13+arm,1,7,'#8e9ca2');r(16,11+arm,4,2,'#c2ccd0');
 ctx.restore();
}
function kitchen(ctx,w,h,t){
 const r=(x,y,a,b,c)=>{ctx.fillStyle=c;ctx.fillRect(Math.round(x),Math.round(y),a,b)};
 r(0,0,w,h,'#243338');
 for(let x=0;x<w;x+=12)for(let y=0;y<54;y+=8){r(x,y,11,7,(x+y)%24?'#354348':'#3c4d51');r(x,y,11,1,'#4b5b5b');}
 r(0,68,w,h-68,'#19262c');
 r(0,58,w,17,'#52676c');r(0,78,w,3,'#a6b5b3');r(0,81,w,9,'#34464d');
 for(const x of [w*.12,w*.31,w*.68]){
  r(x+6,2,147,19,'#5a676a');r(x+9,3,140,2,'#91a2a3');r(x+6,18,147,3,'#27383d');
  for(let s=15;s<145;s+=6)r(x+s,6,2,9,'#344449');
  r(x+19,22,108,2,'#e5c788');r(x+20,24,105,1,'#b99e60');
  r(x+6,58,145,17,'#6b797b');r(x+6,58,145,3,'#b1c0bb');r(x+6,62,145,1,'#293a40');
  for(let s=12;s<140;s+=27){r(x+s,65,23,8,'#46575d');r(x+s+7,66,10,1,'#91a29f');}
  for(let s=20;s<120;s+=38){r(x+s,55,19,3,'#142127');r(x+s+3,50,12,5,'#536166');r(x+s+2,49,14,1,'#b7c5bd');r(x+s+16,52,10,1,'#a4b1ac');steam(ctx,x+s+9,48,t+s/40);}
  person(ctx,x+35,27,t,{chef:true,action:x*.02});person(ctx,x+111,28,t,{chef:true,skin:'#976b4f',action:2+x*.02,flip:-1});
  // Foreground pass: stacked plates, herbs, plated food, steel countertop.
  r(x,78,160,3,'#a6b5b3');r(x,81,160,9,'#34464d');r(x,81,160,1,'#627b80');
  for(let j=0;j<3;j++)r(x+13,73+j*2,21,1,'#d9ddd0');
  r(x+63,76,27,2,'#e6e0ca');r(x+69,74,14,2,'#a76138');r(x+78,73,4,2,'#63844c');r(x+73,73,2,1,'#d9bc6d');
  r(x+133,72,10,6,'#455657');r(x+132,70,12,2,'#798b79');for(let j=0;j<4;j++)r(x+133+j*3,66-(j%2)*2,2,5,'#819268');
 }
}
function backyard(ctx,w,h,t){
 const r=(x,y,a,b,c)=>{ctx.fillStyle=c;ctx.fillRect(Math.round(x),Math.round(y),a,b)};
 r(0,0,w,h,'#273d47');r(0,28,w,62,'#283e32');
 for(let x=0;x<w;x+=12){r(x,39,10,24,x%24?'#655544':'#78624a');r(x+1,37,8,2,'#806a50');r(x+3,42,1,18,'#8e7453');}r(0,58,w,3,'#453e32');
 for(const x of [w*.12,w*.31,w*.68]){
  // Leaves and soft evening string lights.
  for(let j=0;j<18;j++){const px=x+(j*37)%180,py=(j*13)%30;r(px,py,9,5,j%2?'#314b39':'#3b5942');r(px+2,py-2,5,2,'#496349');}
  ctx.strokeStyle='#111e25';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(x,7);ctx.quadraticCurveTo(x+90,29,x+180,7);ctx.stroke();
  for(let j=0;j<7;j++){const px=x+j*28+6,py=8+Math.sin(j/6*Math.PI)*10;r(px,py,2,4,'#e9c97e');r(px-1,py+1,4,2,'#bbaa6550');}
  // Kettle, food and a cook tending the grate.
  person(ctx,x+41,31,t,{shirt:'#9c6849',action:x*.03});r(x+64,66,2,18,'#889092');r(x+90,66,2,18,'#8a9495');r(x+61,82,6,4,'#17262a');r(x+88,82,6,4,'#17262a');
  r(x+59,55,38,8,'#26373d');r(x+62,63,32,7,'#1b2b32');r(x+66,70,24,3,'#13232a');r(x+60,54,36,2,'#9ba39a');
  for(let j=0;j<6;j++)r(x+63+j*5,55,1,6,'#7b8986');r(x+67,53,10,2,'#ac6e45');r(x+82,53,8,2,'#b58155');steam(ctx,x+77,49,t, '185,204,199');
  person(ctx,x+127,31,t,{shirt:'#677f8a',skin:'#996e50',flip:-1,action:3});
  // Patio table with serving dishes, two chatting guests and an umbrella.
  r(x+140,31,1,45,'#978875');r(x+115,29,53,3,'#b09663');r(x+121,25,41,4,'#bfa877');r(x+131,22,21,3,'#d0b784');
  r(x+143,66,32,3,'#9a7853');r(x+148,69,2,18,'#574b39');r(x+169,69,2,18,'#574b39');r(x+148,64,12,2,'#d4d8c1');r(x+151,62,6,2,'#956039');r(x+164,61,3,5,'#cfb77d');
  person(ctx,x+163,36,t,{shirt:'#ad765c',skin:'#d6aa82',action:1});
  for(let j=0;j<20;j++)r(x+(j*23)%180,87+(j%3),2,1,'#56704b');
 }
}
export function renderHeaderScene(ctx,w,h,t,variant){
 ctx.clearRect(0,0,w,h);
 if(variant==='smoke'){
  let image=smokeBuffers.get(ctx);if(!image||image.width!==w||image.height!==h){image=ctx.createImageData(w,h);smokeBuffers.set(ctx,image);}
  const data=image.data;
  // Continuous turbulent density field: no particle rectangles or isolated puffs.
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
   const warp=Math.sin(x*.013+t*.22)*5+Math.sin(y*.07-t*.31)*4;
   const a=cloudNoise(x*.027-t*.42,(y+warp)*.055-t*.19);
   const b=cloudNoise(x*.067-t*.65,y*.11-t*.28);
   const density=Math.min(1,.19+a*.66+b*.15),light=104+a*79+b*24,index=(y*w+x)*4;
   data[index]=light*.94;data[index+1]=light;data[index+2]=light*1.045;
   data[index+3]=Math.round(density*180*(.7+.3*y/h));
  }ctx.putImageData(image,0,0);return;
 }
 ctx.save();const scale=h/90;ctx.scale(scale,scale);const width=w/scale;
 if(variant==='kitchen')kitchen(ctx,width,90,t);else backyard(ctx,width,90,t);
 // A runner/guest crosses the continuous room, turns naturally, and returns.
 const route=Math.sin(t*tau/48),x=width*.5+route*(width*.43),direction=Math.cos(t*tau/48)>=0?1:-1;
 person(ctx,x,43+Math.sin(t*tau/1.2)*.4,t,{chef:variant==='kitchen',shirt:'#8f7779',skin:'#c59b76',flip:direction,walking:true,action:2});
 ctx.restore();
}
