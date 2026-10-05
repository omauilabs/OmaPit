import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
const base=new URL('../public/assets/sauce-fluid/',import.meta.url);
test('fluid cache is complete, finite and indexed correctly, with side drops below the card',()=>{
 const manifest=JSON.parse(readFileSync(new URL('manifest.json',base),'utf8')),packed=readFileSync(new URL('pour.bin.gz',base));
 assert.equal(createHash('sha256').update(packed).digest('hex'),manifest.sha256);
 const raw=gunzipSync(packed);assert.equal(raw.subarray(0,8).toString(),'OMAFLD01');assert.equal(raw.readUInt32LE(8),manifest.frames);assert.equal(raw.readUInt32LE(12),manifest.fps);assert.ok(manifest.loopStart>=0&&manifest.loopStart<manifest.frames-1);
 let offset=16,sideFall=false;
 for(let f=0;f<manifest.frames;f++){
  const count=raw.readUInt32LE(offset),indices=raw.readUInt32LE(offset+4);offset+=8;assert.ok(count>0);assert.equal(indices%3,0);
  for(let i=0;i<count;i++){const x=raw.readFloatLE(offset+i*12),y=raw.readFloatLE(offset+i*12+4),z=raw.readFloatLE(offset+i*12+8);assert.ok([x,y,z].every(Number.isFinite));assert.ok(Math.abs(x)<4&&Math.abs(y)<1&&z>-5&&z<2);if(Math.abs(x)>3&&z< -2.7)sideFall=true;}
  offset+=count*12;for(let i=0;i<indices;i++)assert.ok(raw.readUInt32LE(offset+i*4)<count);offset+=indices*4;
 }
 assert.equal(offset,raw.length);assert.ok(sideFall,'Simulation must include side overflow falling below the card collider');
});
