import * as THREE from 'three';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
export async function loadSauceFrames(signal){
 const [metaResponse,dataResponse]=await Promise.all([fetch('/assets/sauce-fluid/manifest.json',{signal}),fetch('/assets/sauce-fluid/pour.bin.gz',{signal})]);
 if(!metaResponse.ok||!dataResponse.ok)throw Error('Sauce animation assets unavailable');
 const meta=await metaResponse.json(),packed=await dataResponse.arrayBuffer();
 const raw=await new Response(new Blob([packed]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
 const view=new DataView(raw);if(new TextDecoder().decode(new Uint8Array(raw,0,8))!=='OMAFLD01')throw Error('Invalid sauce animation');
 const count=view.getUint32(8,true),fps=view.getUint32(12,true);if(count!==meta.frames||fps!==meta.fps||count<2||count>1000)throw Error('Invalid sauce frame count');
 let offset=16;const frames=[];
 for(let i=0;i<count;i++){const vertices=view.getUint32(offset,true),indices=view.getUint32(offset+4,true);offset+=8;if(vertices>1000000||indices>6000000||offset+vertices*12+indices*4>raw.byteLength)throw Error('Invalid sauce mesh');const positions=new Float32Array(raw,offset,vertices*3);offset+=vertices*12;const triangles=new Uint32Array(raw,offset,indices);offset+=indices*4;frames.push({positions,triangles});}
 if(offset!==raw.byteLength)throw Error('Invalid sauce animation length');return {frames,fps,loopStart:meta.loopStart};
}
export function createSauceRenderer(canvas,card,subnav){
 const renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true});renderer.setClearColor(0,0);renderer.localClippingEnabled=true;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.9;
 const scene=new THREE.Scene(),camera=new THREE.OrthographicCamera();camera.position.set(0,0,1000);camera.near=.1;camera.far=2000;
 const environment=new RoomEnvironment(),pmrem=new THREE.PMREMGenerator(renderer),env=pmrem.fromScene(environment,.18);scene.environment=env.texture;environment.dispose();pmrem.dispose();
 const textureCanvas=document.createElement('canvas');textureCanvas.width=textureCanvas.height=256;const context=textureCanvas.getContext('2d'),pixels=context.createImageData(256,256);let seed=4176;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
 for(let i=0;i<pixels.data.length;i+=4){const fleck=random(),variation=random()*8-4;const rgb=fleck<.009?[22,8,3]:fleck>.986?[65,31,12]:[43+variation,16+variation*.5,6+variation*.2];pixels.data.set([...rgb,255],i);}context.putImageData(pixels,0,0);const texture=new THREE.CanvasTexture(textureCanvas);texture.colorSpace=THREE.SRGBColorSpace;texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.repeat.set(3,3);texture.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());
 const faceMask=[new THREE.Plane(),new THREE.Plane(),new THREE.Plane()];
 const material=new THREE.MeshPhysicalMaterial({clippingPlanes:faceMask,clipIntersection:true,color:0xffffff,map:texture,bumpMap:texture,bumpScale:.75,roughness:.3,metalness:0,specularIntensity:.25,clearcoat:.08,clearcoatRoughness:.3,envMapIntensity:.22});
 const key=new THREE.DirectionalLight(0xffe6c5,1.1);key.position.set(-200,300,400);scene.add(key);const fill=new THREE.DirectionalLight(0xffdec4,.35);fill.position.set(300,50,300);scene.add(fill);scene.add(new THREE.HemisphereLight(0xffe7d0,0x251108,.8));
 const mesh=new THREE.Mesh(new THREE.BufferGeometry(),material);mesh.frustumCulled=false;scene.add(mesh);let width=0,height=0,landing=0,cardWidth=0,cardHeight=0,current=null;
 const resize=()=>{landing=Math.max(0,card.getBoundingClientRect().top-subnav.getBoundingClientRect().bottom);cardWidth=card.clientWidth;cardHeight=card.clientHeight;canvas.parentElement.style.top=(-landing-parseFloat(getComputedStyle(card).borderTopWidth||0))+'px';canvas.parentElement.style.height=landing+cardHeight+160+'px';width=canvas.clientWidth;height=canvas.clientHeight;renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setSize(width,height,false);camera.left=-width/2;camera.right=width/2;camera.top=height/2;camera.bottom=-height/2;camera.updateProjectionMatrix();faceMask[0].set(new THREE.Vector3(-1,0,0),-cardWidth/2+3);faceMask[1].set(new THREE.Vector3(1,0,0),-cardWidth/2+3);faceMask[2].set(new THREE.Vector3(0,1,0),-(height/2-landing));if(current)setFrame(current);};
 const setFrame=frame=>{current=frame;const original=frame.positions,positions=new Float32Array(original.length),uv=new Float32Array(original.length/3*2),scale=cardWidth/6;
  for(let i=0;i<original.length;i+=3){const x=original[i],depth=original[i+1],z=original[i+2];positions[i]=(Math.abs(x)<=3?x:Math.sign(x)*(3+(Math.abs(x)-3)*.3))*scale;positions[i+1]=height/2-landing+(z>0?(z<=.25?z*scale*.35:.25*scale*.35+(z-.25)*(landing-.25*scale*.35)/.6):z*cardHeight/2.7)+depth*scale*.035;positions[i+2]=-depth*scale;uv[i/3*2]=x/3;uv[i/3*2+1]=(z+depth)*.8;}
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));geometry.setAttribute('uv',new THREE.BufferAttribute(uv,2));geometry.setIndex(new THREE.BufferAttribute(frame.triangles,1));geometry.computeVertexNormals();mesh.geometry.dispose();mesh.geometry=geometry;renderer.render(scene,camera);
 };
 const observer=new ResizeObserver(resize);observer.observe(card);observer.observe(subnav);resize();
 return {setFrame,dispose(){observer.disconnect();mesh.geometry.dispose();material.dispose();texture.dispose();env.dispose();renderer.dispose();}};
}
