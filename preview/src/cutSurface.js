import * as THREE from 'three';

// Each triangle owns exactly one region. Split only vertices shared by different
// regions, retaining the original normals, UVs and material groups. This avoids
// interpolated vertex votes producing wedges, holes and ambiguous picking.
export function applyFaceRegions(source, labels) {
 const indices=source.index?.array || Uint32Array.from({length:source.attributes.position.count},(_,i)=>i);
 if(indices.length%3 || labels.length!==indices.length/3)throw new Error('Cut mapping face count mismatch');
 const vertices=[],regions=[],index=new Uint32Array(indices.length),remap=new Map();
 for(let i=0;i<indices.length;i++){
  const original=indices[i],region=labels[Math.floor(i/3)],key=original*256+region;
  let mapped=remap.get(key);
  if(mapped===undefined){mapped=vertices.length;remap.set(key,mapped);vertices.push(original);regions.push(region)}
  index[i]=mapped;
 }
 const result=new THREE.BufferGeometry();
 for(const [name,attribute] of Object.entries(source.attributes)){
  if(attribute.isInterleavedBufferAttribute)throw new Error('Interleaved cut geometry requires offline unpacking');
  const data=new attribute.array.constructor(vertices.length*attribute.itemSize);
  vertices.forEach((original,i)=>{for(let k=0;k<attribute.itemSize;k++)data[i*attribute.itemSize+k]=attribute.array[original*attribute.itemSize+k]});
  result.setAttribute(name,new THREE.BufferAttribute(data,attribute.itemSize,attribute.normalized));
 }
 result.setAttribute('regionId',new THREE.Uint8BufferAttribute(regions,1,false));
 result.setIndex(new THREE.BufferAttribute(index,1));
 source.groups.forEach(g=>result.addGroup(g.start,g.count,g.materialIndex));
 result.computeBoundingBox();result.computeBoundingSphere();return result;
}
