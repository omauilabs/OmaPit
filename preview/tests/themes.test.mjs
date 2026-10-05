import test from 'node:test';
import assert from 'node:assert/strict';
import {themes,readTheme,applyTheme} from '../src/themes.js';
const luminance=hex=>{const rgb=hex.slice(1).match(/../g).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722};
const contrast=(a,b)=>{const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
test('all theme text and buttons meet normal text contrast on base and panel',()=>{for(const t of themes){for(const surface of [t.base,t.panel])for(const ink of [t.ink,t.muted,t.accent,t.secondary])assert.ok(contrast(ink,surface)>=4.5,`${t.id} ${ink} on ${surface}: ${contrast(ink,surface)}`);}});
test('unknown preferences and unavailable storage safely restore Omarchy',()=>{assert.equal(readTheme({getItem:()=> 'lost-theme'}),'omarchy');assert.equal(readTheme({getItem:()=>{throw Error()}}),'omarchy');assert.equal(readTheme({getItem:()=> 'christmas'}),'christmas')});
test('applying a theme only changes appearance roles; registry is unique',()=>{assert.equal(new Set(themes.map(t=>t.id)).size,6);const properties={};const root={dataset:{},style:{setProperty:(k,v)=>properties[k]=v}};applyTheme('backyard',root);assert.equal(root.dataset.omapitTheme,'backyard');assert.equal(root.style.colorScheme,'light');assert.equal(properties['--background'],'#eee6d5');applyTheme('unknown',root);assert.equal(root.dataset.omapitTheme,'omarchy')});
