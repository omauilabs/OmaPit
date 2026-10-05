import test from 'node:test';
import assert from 'node:assert/strict';
import {foodLibraries,rubs,portionTotal,rubBatch} from '../src/mealExploreCatalog.js';
test('portions scale by diners and reserve, with invalid amounts rejected',()=>{
 assert.equal(portionTotal(8,150,10),1320);
 assert.equal(portionTotal(8,100,10),880);
 assert.equal(portionTotal(8,1,25),10);
 for(const args of [['',150,10],[8,'',10],[2.5,150,10],[8,-2,0],[8,100,101],[201,100,0],[8,100,'']]) assert.equal(portionTotal(...args),null);
});
test('weight based rub sums exactly to batch; equivalent units produce equal amounts',()=>{
 const a=rubBatch(1,'kg',20,{salt:25,pepper:75});
 const b=rubBatch(1/.45359237,'lb',20,{salt:1,pepper:3});
 assert.equal(a.grams,20);assert.equal(a.saltGrams,5);
 assert.ok(Math.abs(a.grams-b.grams)<1e-10);
 assert.ok(Math.abs(a.ingredients.reduce((n,x)=>n+x.grams,0)-a.grams)<1e-10);
 const c=rubBatch(1,'kg',20,{salt:0,pepper:30});assert.equal(c.saltGrams,0);assert.equal(c.ingredients[1].grams,20);
});
test('rub invalid inputs cannot generate a usable recipe',()=>{
 for(const args of [[0,'kg',20,{salt:1}],['','kg',20,{salt:1}],[1,'oz',20,{salt:1}],[1,'kg','',{salt:1}],[1,'kg',20,{salt:''}],[1,'kg',20,{salt:0}],[1,'kg',20,{unknown:1}],[1,'kg',20,{salt:101}]])assert.equal(rubBatch(...args),null);
});
test('all explorer choices have usable quantities and no ambiguous ids within their catalog',()=>{
 for(const lib of Object.values(foodLibraries)){
 assert.equal(new Set(lib.items.map(x=>x.id)).size,lib.items.length);
 for(const x of lib.items){assert.ok(portionTotal(8,x.portion,10)>0);assert.ok(x.prep&&x.ready&&x.lead);assert.ok(x.source.startsWith('https://'));}
 }
 for(const r of rubs){const b=rubBatch(5,'lb',20,r.recipe);assert.ok(b);assert.ok(Math.abs(b.ingredients.reduce((n,x)=>n+x.percent,0)-100)<1e-10);}
});
