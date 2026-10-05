import test from 'node:test';
import assert from 'node:assert/strict';
import {headerProbes,probeTemperature} from '../src/headerProbeData.js';
const device={id:'a',name:'Probe',source:'ble',channels:{food:{value:30,at:99,fresh:true},ambient:{value:200,at:99,fresh:true,quality:'invalid'}}};
test('real food stays live independently of invalid ambient and demo cook',()=>{const p=headerProbes({active:{source:'demo'},devices:[device]},100)[0];assert.equal(p.channels[0].state,'live');assert.equal(p.channels[1].value,null)});
test('old and offline readings never claim live',()=>{assert.equal(headerProbes({devices:[device]},140)[0].channels[0].state,'stale');assert.equal(headerProbes({devices:[device]},100,false)[0].channels[0].state,'offline')});
test('replays are excluded and unknown timestamps cannot be live',()=>{assert.equal(headerProbes({devices:[{...device,source:'replay'}]},100).length,0);assert.equal(headerProbes({devices:[{...device,channels:{food:{value:0,fresh:true}}}]},100)[0].channels[0].state,'stale')});
test('selected device first without dropping other probes; units retain tenths',()=>{assert.equal(headerProbes({devices:[device,{...device,id:'b'}],selected_device:'b'},100)[0].id,'b');assert.equal(probeTemperature(30,'F'),'86.0');assert.equal(probeTemperature(0,'C'),'0.0');assert.equal(probeTemperature(null,'F'),'—')});
