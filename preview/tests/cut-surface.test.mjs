import {test} from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {applyFaceRegions} from '../src/cutSurface.js';
test('adjacent surface regions cannot interpolate or overlap and preserve UVs/normals/groups',()=>{
 const source=new THREE.PlaneGeometry(2,2);source.clearGroups();source.addGroup(0,3,0);source.addGroup(3,3,1);
 const result=applyFaceRegions(source,new Uint8Array([1,2]));
 assert.equal(result.attributes.position.count,6);
 for(let i=0;i<6;i++){
  const original=source.index.getX(i),mapped=result.index.getX(i);
  assert.equal(result.attributes.regionId.getX(mapped),i<3?1:2);
  for(const name of ['position','normal','uv'])for(let k=0;k<source.attributes[name].itemSize;k++)assert.equal(result.attributes[name].array[mapped*source.attributes[name].itemSize+k],source.attributes[name].array[original*source.attributes[name].itemSize+k]);
 }
 assert.deepEqual(result.groups,source.groups);
});
test('unassigned seams stay unassigned; invalid sidecars fail rather than show incorrect masks',()=>{
 const source=new THREE.PlaneGeometry(2,2),result=applyFaceRegions(source,new Uint8Array([0,9]));
 assert.equal(result.attributes.regionId.getX(result.index.getX(0)),0);
 assert.equal(result.attributes.regionId.getX(result.index.getX(3)),9);
 assert.throws(()=>applyFaceRegions(source,new Uint8Array([1])),/face count/);
});
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
for(const animal of ['beef','pork','lamb','goat','deer-buck','deer-doe'])test(`${animal}: surface sidecar matches the exact GLB topology and has no invalid region IDs`,()=>{
 const root=new URL('../public/assets/cuts/',import.meta.url),model=readFileSync(new URL(animal+'.glb',root));
 const json=JSON.parse(model.subarray(20,20+model.readUInt32LE(12)).toString().trim());
 const primitive=json.meshes[0].primitives[0],meta=JSON.parse(readFileSync(new URL(animal+'.faces.json',root))),labels=readFileSync(new URL(animal+'.faces.bin',root));
 assert.equal(meta.version,2);assert.equal(meta.modelSha256,createHash('sha256').update(model).digest('hex'));
 assert.equal(meta.vertexCount,json.accessors[primitive.attributes.POSITION].count);
 assert.equal(labels.length,json.accessors[primitive.indices].count/3);
 assert.equal(labels.length,meta.faceCount);assert.ok(labels.includes(0));
 assert.ok(labels.every(id=>id<=meta.regions.length));
 for(let i=1;i<=meta.regions.length;i++)if(!(animal==='goat'&&meta.regions[i-1]==='loin'))assert.ok(labels.includes(i),`${meta.regions[i-1]} must have a selectable surface`);
});
