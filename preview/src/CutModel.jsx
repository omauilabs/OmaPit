import React,{useEffect,useRef,useState} from 'react';
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {ArrowClockwise} from '@phosphor-icons/react/dist/csr/ArrowClockwise';
import {MagnifyingGlassPlus} from '@phosphor-icons/react/dist/csr/MagnifyingGlassPlus';
import {MagnifyingGlassMinus} from '@phosphor-icons/react/dist/csr/MagnifyingGlassMinus';
import {ArrowsClockwise} from '@phosphor-icons/react/dist/csr/ArrowsClockwise';
import {regionName,species} from './cutCatalog';
import {applyFaceRegions} from './cutSurface';
export function CutModel({animal,variant,region,onRegion}){
 const modelKey=animal==='deer'?`deer-${variant||'buck'}`:animal;
 const host=useRef(null),runtime=useRef(null),selection=useRef(region),callback=useRef(onRegion);
 const [status,setStatus]=useState('loading'),[hover,setHover]=useState(null);
 selection.current=region;callback.current=onRegion;
 useEffect(()=>{runtime.current?.paint()},[region]);
 useEffect(()=>{
  const el=host.current;let disposed=false,root=null;setStatus('loading');setHover(null);
  if(species[animal].modelReady===false){setStatus('pending');return;}
  let renderer;try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});}catch{setStatus('unavailable');return;}
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor(0x151922,0);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.3;
  el.appendChild(renderer.domElement);renderer.domElement.setAttribute('aria-label',`${species[animal].name} 3D cut model. Use the cut cards or region buttons for keyboard selection.`);
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(34,1,.01,100);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.enablePan=false;controls.minDistance=2;controls.maxDistance=8;controls.maxPolarAngle=Math.PI*.60;controls.minPolarAngle=Math.PI*.20;
  scene.add(new THREE.HemisphereLight(0xd9e2ff,0x202128,1.3));
  const key=new THREE.DirectionalLight(0xffedcf,2.5);key.position.set(3,5,3);scene.add(key);
  const rim=new THREE.DirectionalLight(0x829dff,1.7);rim.position.set(-3,2,-2);scene.add(rim);
  const fill=new THREE.DirectionalLight(0xffffff,1.5);fill.position.set(1,1,-3);scene.add(fill);
  const meshes=[],materials=new Map();let currentHover=null,textureUniforms=null,modelBox=null,modelScale=1,modelCenter=null;
  const draw=()=>{if(!disposed)renderer.render(scene,camera)};
  const panelId=id=>modelKey==='goat'&&id==='loin'?'rack':id;
  const regionIndex=id=>id==='whole'?-1:species[animal].regions.indexOf(panelId(id))+1;
  const paint=()=>{if(textureUniforms){textureUniforms.selected.value=regionIndex(selection.current);textureUniforms.hovered.value=regionIndex(currentHover);draw();return;}for(const [id,mat] of materials){const selected=id===selection.current;mat.color.set(selected?0xe0af68:id===currentHover?0x8c8490:0x343742);mat.emissive.set(selected?0x4e2c0b:id===currentHover?0x171620:0x000000);mat.emissiveIntensity=selected?.55:.25;}draw()};
  const fitFrame=()=>{if(!modelBox)return;if(camera.aspect>=1.2){camera.position.sub(controls.target).setLength(3.82).add(controls.target);controls.update();return;}const direction=camera.position.clone().sub(controls.target).normalize(),right=new THREE.Vector3(0,1,0).cross(direction).normalize(),up=direction.clone().cross(right),tan=Math.tan(THREE.MathUtils.degToRad(camera.fov/2));let distance=3.82;for(const x of [modelBox.min.x,modelBox.max.x])for(const y of [modelBox.min.y,modelBox.max.y])for(const z of [modelBox.min.z,modelBox.max.z]){const corner=new THREE.Vector3(x,y,z).sub(modelCenter).multiplyScalar(modelScale);distance=Math.max(distance,Math.abs(corner.dot(right))/(tan*camera.aspect)*1.12+corner.dot(direction),Math.abs(corner.dot(up))/tan*1.12+corner.dot(direction));}camera.position.copy(direction.multiplyScalar(distance).add(controls.target));controls.update();};
  const reset=()=>{camera.aspect=el.clientWidth/el.clientHeight||1;camera.updateProjectionMatrix();camera.position.set(3.5,1.05,1.1);controls.target.set(0,0,0);fitFrame();controls.update();draw()};reset();
  const resize=()=>{const w=el.clientWidth,h=el.clientHeight;if(!w||!h)return;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();fitFrame();draw()};const observer=new ResizeObserver(resize);observer.observe(el);
  const ray=new THREE.Raycaster(),mouse=new THREE.Vector2();let down=null;
  const hit=e=>{const r=renderer.domElement.getBoundingClientRect();mouse.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);ray.setFromCamera(mouse,camera);const intersection=ray.intersectObjects(meshes,false)[0];if(!intersection)return null;const mesh=intersection.object,face=intersection.face,positions=mesh.geometry.attributes.position,ids=mesh.geometry.attributes.regionId;
   if(!face||!ids)return null;
   const id=ids.getX(face.a);return id>0?species[animal].regions[id-1]:null};
  const move=e=>{const id=hit(e);if(id!==currentHover){currentHover=id;setHover(id);paint()}renderer.domElement.style.cursor=id?'pointer':'grab'};
  const leave=()=>{currentHover=null;setHover(null);paint()};
  const start=e=>{down={x:e.clientX,y:e.clientY}};
  const end=e=>{if(down&&Math.hypot(e.clientX-down.x,e.clientY-down.y)<6){const id=hit(e);if(id)callback.current(id)}down=null};
  const lost=e=>{e.preventDefault();setStatus('unavailable')};
  renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerleave',leave);renderer.domElement.addEventListener('pointerdown',start);renderer.domElement.addEventListener('pointerup',end);renderer.domElement.addEventListener('webglcontextlost',lost);controls.addEventListener('change',draw);
  runtime.current={paint,reset,zoom:factor=>{const distance=THREE.MathUtils.clamp(camera.position.distanceTo(controls.target)*factor,controls.minDistance,controls.maxDistance);camera.position.sub(controls.target).setLength(distance).add(controls.target);controls.update();draw()},rotate:()=>{const delta=camera.position.clone().sub(controls.target);delta.applyAxisAngle(new THREE.Vector3(0,1,0),Math.PI/6);camera.position.copy(delta.add(controls.target));controls.update();draw()}};
  const asset=async suffix=>{const response=await fetch(`/assets/cuts/${modelKey}.${suffix}?surface=2`);if(!response.ok)throw new Error('Cut mapping unavailable');return suffix==='faces.json'?response.json():response.arrayBuffer()};
  Promise.all([new GLTFLoader().loadAsync(`/assets/cuts/${modelKey}.glb`),asset('faces.json'),asset('faces.bin')]).then(([gltf,regionInfo,regionBuffer])=>{
   if(disposed){const abandoned=new Set();gltf.scene.traverse(o=>{o.geometry?.dispose();for(const mat of (Array.isArray(o.material)?o.material:o.material?[o.material]:[])){for(const value of Object.values(mat))if(value?.isTexture)abandoned.add(value);mat.dispose();}});abandoned.forEach(t=>t.dispose());return}
   root=new THREE.Group();gltf.scene.updateMatrixWorld(true);const box=new THREE.Box3().setFromObject(gltf.scene),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());const scale=2.65/(animal==='chicken'||animal==='turkey'?Math.max(size.z,size.y):size.z);
   {
    const labels=new Uint8Array(regionBuffer);if(regionInfo.model!==modelKey||labels.length!==regionInfo.faceCount||regionInfo.version!==2||regionInfo.regions.join()!==species[animal].regions.join())throw new Error('Cut mapping does not match model');
    modelBox=box;modelCenter=center;modelScale=scale;
    textureUniforms={selected:{value:regionIndex(selection.current)},hovered:{value:0}};
    gltf.scene.traverse(o=>{if(!o.isMesh)return;
     if(o.geometry.attributes.position.count!==regionInfo.vertexCount)throw new Error('Cut mapping vertex count mismatch');
     const geo=applyFaceRegions(o.geometry,labels);geo.applyMatrix4(o.matrixWorld);
     geo.translate(-center.x,-center.y,-center.z);geo.scale(scale,scale,scale);
     const originals=Array.isArray(o.material)?o.material:[o.material];
     const preserved=originals.map(original=>{const mat=original.clone();mat.onBeforeCompile=shader=>{
      shader.uniforms.selected=textureUniforms.selected;shader.uniforms.hovered=textureUniforms.hovered;
      shader.vertexShader='attribute float regionId;uniform float selected;uniform float hovered;varying float vCutSelected;varying float vCutHovered;\n'+shader.vertexShader;
      shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvCutSelected=regionId>0.0&&(selected<0.0||abs(regionId-selected)<.1)?1.0:0.0;vCutHovered=regionId>0.0&&abs(regionId-hovered)<.1?1.0:0.0;');
      shader.fragmentShader='varying float vCutSelected;varying float vCutHovered;\n'+shader.fragmentShader;
      shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`#include <map_fragment>
       float grain=clamp(dot(diffuseColor.rgb,vec3(.2126,.7152,.0722))*4.0,.40,1.0);
       if(vCutSelected>.5)diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.82,.44,.09)*grain,.88);
       else if(vCutHovered>.5)diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.32,.37,.46)*grain,.5);
      `);
     };mat.customProgramCacheKey=()=> 'omapit-surface-labels-'+modelKey+'-faces-v2';materials.set(String(materials.size),mat);return mat;});
     const mesh=new THREE.Mesh(geo,Array.isArray(o.material)?preserved:preserved[0]);root.add(mesh);meshes.push(mesh);o.geometry.dispose();originals.forEach(m=>m.dispose());
    });scene.add(root);setStatus('ready');paint();resize();return;
   }
  }).catch(()=>{if(!disposed)setStatus('unavailable')});
  return()=>{disposed=true;observer.disconnect();controls.dispose();renderer.domElement.removeEventListener('webglcontextlost',lost);root?.traverse(o=>{o.geometry?.dispose();if(o.isLineSegments)o.material.dispose()});const textures=new Set();for(const m of materials.values()){for(const value of Object.values(m))if(value?.isTexture)textures.add(value);m.dispose();}textures.forEach(t=>t.dispose());renderer.dispose();renderer.domElement.remove();runtime.current=null;};
 },[animal,modelKey]);
 return <div className="cut-model-block"><div className={'cut-model '+(status==='pending'?'cut-model-pending':'')} ref={host} data-model-status={status}>{status==='pending'?<><img src={`/assets/cuts/${animal}-reference.webp`} alt={`${species[animal].name} sculpture reference; static image, not the interactive model`}/><div className="model-import-note">Sculpture reference · 3D import pending</div></>:status!=='ready'&&<div className="model-message">{status==='loading'?'Loading your 3D model…':'3D view unavailable. Select a cut below.'}</div>}<div className="model-selection" aria-live="polite">{hover?`Preview · ${regionName(hover)}`:`Selected · ${regionName(region)}`}</div></div><div className="model-controls"><button onClick={()=>runtime.current?.rotate()} disabled={status!=='ready'}><ArrowsClockwise size={18}/>Rotate</button><button aria-label="Zoom in on animal" onClick={()=>runtime.current?.zoom(.85)} disabled={status!=='ready'}><MagnifyingGlassPlus size={18}/></button><button aria-label="Zoom out from animal" onClick={()=>runtime.current?.zoom(1.15)} disabled={status!=='ready'}><MagnifyingGlassMinus size={18}/></button><button onClick={()=>runtime.current?.reset()} disabled={status!=='ready'}><ArrowClockwise size={18}/>Reset</button></div><p className="model-hint">{status==='pending'?'Cut cards are ready. Interactive regions will appear after the GLB import.':'Drag to orbit · scroll to zoom · select a region'}</p></div>
}
