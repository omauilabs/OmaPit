// Draw at a fixed pixel-art resolution; integer raster details survive square-pixel scaling.
export function makeHeaderSprite(kind){
 const c=document.createElement('canvas');c.width=72;c.height=72;const g=c.getContext('2d');
 const path=(points,color,stroke='#251c19',width=2)=>{g.beginPath();points.forEach(([x,y],i)=>i?g.lineTo(x,y):g.moveTo(x,y));g.closePath();g.fillStyle=color;g.fill();g.strokeStyle=stroke;g.lineWidth=width;g.stroke()};
 const line=(points,color,width=2)=>{g.beginPath();points.forEach(([x,y],i)=>i?g.lineTo(x,y):g.moveTo(x,y));g.strokeStyle=color;g.lineWidth=width;g.lineCap='square';g.stroke()};
 const steel=()=>{const a=g.createLinearGradient(18,0,49,0);a.addColorStop(0,'#657684');a.addColorStop(.35,'#eff4ef');a.addColorStop(.55,'#9caeb9');a.addColorStop(.8,'#f5f1df');a.addColorStop(1,'#536675');return a};
 const handle=()=>{path([[31,38],[41,38],[42,65],[39,68],[33,68],[30,65]],'#86542f');line([[34,42],[34,61]],'#c59157');g.fillStyle='#d3c6a5';g.fillRect(35,45,3,3);g.fillRect(35,60,3,3)};
 if(kind==='steak'){
 path([[10,23],[17,12],[35,8],[54,15],[63,28],[60,47],[48,60],[28,61],[13,50],[7,35]],'#c28653');
 path([[14,24],[22,16],[36,13],[53,21],[57,33],[53,48],[43,54],[28,55],[17,47],[12,34]],'#8f392b');
 line([[27,18],[30,29],[22,38],[29,51]],'#efd0a0',3);line([[30,29],[46,32],[53,41]],'#efd0a0',3);line([[31,29],[38,43],[42,53]],'#dba17a',2);
 for(let i=0;i<5;i++)line([[17+i*7,23],[14+i*7,44]],'#3c211c',3);
 }else if(kind==='ribs'){
 path([[9,18],[56,11],[63,49],[17,59]],'#64301e');path([[12,21],[53,15],[58,45],[19,53]],'#a5512b');
 for(let i=0;i<6;i++){const x=15+i*7;line([[x,21-i],[x+7,48-i]],'#38241b',4);line([[x+3,49-i],[x+4,57-i]],'#f0d8a6',5);line([[x+2,23-i],[x+7,42-i]],'#d18a4e',2)}
 }else if(kind==='drumstick'){
 path([[40,42],[46,39],[61,56],[63,55],[67,58],[67,64],[63,67],[58,65],[56,60]],'#eee0bd');
 path([[10,23],[18,12],[31,10],[44,16],[51,28],[46,43],[35,48],[21,43],[11,34]],'#b86a31');
 path([[16,22],[23,16],[33,16],[43,24],[41,31],[31,30],[23,36],[16,30]],'#dfa15b', '#bd793f',1);
 for(let i=0;i<24;i++){g.fillStyle=i%3?'#8d4928':'#f1bd71';g.fillRect(16+(i*13%27),20+(i*7%19),2,2)}
 }else if(kind==='sausage'){
 g.lineCap='round';line([[13,48],[17,31],[28,20],[43,19],[56,28]],'#36241c',18);g.lineCap='round';g.beginPath();g.moveTo(13,48);g.quadraticCurveTo(13,8,43,19);g.quadraticCurveTo(51,22,56,28);g.strokeStyle='#ba6334';g.lineWidth=13;g.stroke();line([[19,28],[24,23],[34,22]],'#e8a263',3);for(let i=0;i<5;i++)line([[13+i*9,29-i*2],[19+i*9,36-i*2]],'#502a1e',3);
 }else if(kind==='spatula'){
 handle();path([[21,7],[51,7],[49,31],[39,38],[32,38],[23,31]],steel(),'#394754');for(let i=0;i<4;i++)line([[27+i*6,13],[27+i*6,27]],'#293641',2);line([[24,8],[48,8]],'#fff5df');
 }else if(kind==='fork'){
 handle();path([[33,18],[39,18],[39,40],[33,40]],steel(),'#394754');for(let i=0;i<3;i++)path([[24+i*10,5],[28+i*10,5],[28+i*10,23],[24+i*10,23]],steel(),'#394754',1);line([[25,24],[47,24]],'#dce8e8',5);
 }else if(kind==='tongs'){
 line([[25,9],[31,49],[36,64],[41,49],[47,9]],'#394754',8);line([[25,9],[31,49],[36,64],[41,49],[47,9]],'#c7d5db',5);
 path([[18,5],[29,5],[30,18],[20,21],[16,16]],steel(),'#394754');path([[43,5],[54,5],[56,16],[52,21],[42,18]],steel(),'#394754');line([[31,35],[33,47]],'#93592f',6);line([[41,35],[39,47]],'#93592f',6);line([[27,9],[27,15]],'#f5f5df');
 }else if(kind==='brush'){
 handle();path([[23,8],[49,8],[48,29],[24,29]],'#d69452');for(let i=0;i<9;i++)line([[24+i*3,9],[25+i*3,26]],i%2?'#f0c88c':'#91542e',1);path([[24,29],[48,29],[45,38],[27,38]],steel(),'#394754');
 }
 // Quantize the antialiased drawing to genuine hard-edged pixel clusters.
 const small=document.createElement('canvas');small.width=36;small.height=36;small.getContext('2d').drawImage(c,0,0,36,36);g.clearRect(0,0,72,72);g.imageSmoothingEnabled=false;g.drawImage(small,0,0,72,72);return c;
}
export function renderFalling(ctx,w,h,t,sprites){
 ctx.clearRect(0,0,w,h);ctx.imageSmoothingEnabled=false;const count=Math.max(9,Math.ceil(w/60));
 for(let i=0;i<count;i++){const seed=(i*.61803398875)%1,speed=9+(i%5)*1.7,size=32+(i%4)*3;const y=((t*speed+seed*(h+size*2))%(h+size*2))-size;const x=(i+.5)*w/count+Math.sin(t*.6+i*2.7)*7;
 ctx.save();ctx.translate(Math.round(x),Math.round(y));ctx.rotate(Math.sin(t*.32+i)*.32+(i%3-1)*.25);ctx.globalAlpha=.95;ctx.drawImage(sprites[i%sprites.length],-size/2,-size/2,size,size);ctx.restore();
 }
}
