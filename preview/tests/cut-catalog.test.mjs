import test from 'node:test';
import assert from 'node:assert/strict';
import {catalog,species,regionAt} from '../src/cutCatalog.js';
import {readFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
test('all cuts have unique identities and a selectable region in their animal',()=>{
 for(const [kind,cuts] of Object.entries(catalog)){
  assert.equal(new Set(cuts.map(c=>c.id)).size,cuts.length);
  for(const c of cuts){
   if(c.region==='whole'){assert.equal(c.category,'poultry');assert.deepEqual(c.regions,species[kind].regions)}
   else assert.ok(species[kind].regions.includes(c.region));
   assert.ok(c.description);if(c.image)assert.ok(existsSync(resolve('public/assets/cuts',c.image+'.webp')))
  }
 }
});
test('front chest, belly, back and hind leg remain distinct',()=>{
 assert.equal(regionAt('beef',.64,.53),'brisket');
 assert.equal(regionAt('beef',.48,.53),'plate');
 assert.equal(regionAt('beef',.33,.53),'flank');
 assert.equal(regionAt('beef',.48,.75),'rib');
 assert.equal(regionAt('pork',.63,.7),'shoulder');
 assert.equal(regionAt('pork',.43,.53),'belly');
 assert.equal(regionAt('pork',.43,.75),'loin');
 for(const kind of ['lamb','goat'])assert.equal(regionAt(kind,.20,.65),'leg');
 assert.equal(regionAt('beef',.9,.7),null);
});
test('bundled animal assets are real glTF binary geometry',()=>{
 for(const kind of ['beef','pork','lamb','goat','deer-buck','deer-doe']){
  const bytes=readFileSync(resolve('public/assets/cuts',kind+'.glb'));
  assert.equal(bytes.toString('utf8',0,4),'glTF');
  const json=JSON.parse(bytes.toString('utf8',20,20+bytes.readUInt32LE(12)));
  assert.ok(json.meshes.length);assert.ok(json.accessors.some(a=>a.type==='VEC3'&&a.count>100));
 }
});
