import test from 'node:test';
import assert from 'node:assert/strict';
import {hotSauces,hotIngredients} from '../src/hotSauceCatalog.js';
import {hotBatch,hotDinner,validateHotSaves,hotRecipeText} from '../src/hotSauceMaker.js';
import {sauceStyles,ingredients} from '../src/sauceCatalog.js';
import {rubs,rubIngredients,rubBatch} from '../src/mealExploreCatalog.js';
test('expanded libraries have distinct entries and usable documented context',()=>{
 for(const [list,count] of [[hotSauces,24],[sauceStyles,30],[rubs,30]]){assert.equal(list.length,count);assert.equal(new Set(list.map(x=>x.id)).size,count)}
 for(const s of hotSauces){assert.match(s.source,/^https:\/\//);assert.ok(s.provenance&&s.note&&s.description&&s.method);assert.ok(hotBatch(s.recipe,250));assert.ok(Object.keys(s.recipe).every(id=>Object.hasOwn(hotIngredients,id)))}
 for(const r of rubs){assert.ok(Object.keys(r.recipe).every(id=>Object.hasOwn(rubIngredients,id)));assert.ok(rubBatch(2,'kg',20,r.recipe))}
 for(const s of sauceStyles)assert.ok(Object.keys(s.recipe).every(id=>Object.hasOwn(ingredients,id)));
});
test('weighed batch conserves ingredient charge and reports pepper share separately from heat',()=>{const b=hotBatch({cayenne:2,vinegar:1,salt:0},300);assert.deepEqual(b.ingredients.map(x=>x.grams),[200,100,0]);assert.ok(Math.abs(b.pepperPercent-200/3)<1e-10);for(const s of hotSauces){assert.ok(Math.abs(hotBatch(s.recipe,431).ingredients.reduce((a,x)=>a+x.grams,0)-431)<1e-8)}});
test('invalid ingredients and quantities fail rather than silently changing a recipe',()=>{for(const r of [{unknown:1},{cayenne:-1},{cayenne:101},{cayenne:''},{cayenne:Infinity},{cayenne:0},[],null])assert.equal(hotBatch(r,200),null);for(const g of ['',0,9,10001,Infinity,NaN])assert.equal(hotBatch({cayenne:1},g),null);assert.ok(hotBatch({cayenne:1},10));assert.equal(hotBatch({constructor:2},200),null)});
test('dinner sizing allocates once per person and validates every input',()=>{assert.equal(hotDinner(8,5,10),44);assert.equal(hotDinner(12,3,0),36);for(const args of [[0,5,10],[2.5,5,10],[8,'',10],[8,5,101],[8,Infinity,0]])assert.equal(hotDinner(...args),null)});
test('saved recipes reject corrupt records and preserve batch and custom proportions',()=>{const good={id:'sample',name:'My Sauce',style:hotSauces[0].id,recipe:{cayenne:5,vinegar:8},total:250};assert.deepEqual(validateHotSaves([good]),[good]);assert.deepEqual(validateHotSaves([null,{...good,recipe:{unknown:10}},{...good,style:'missing'},{...good,total:0}]),[]);assert.equal(validateHotSaves(Array(50).fill(good)).length,30)});
test('exports retain provenance, preparation and the limits of customized formulas',()=>{const t=hotRecipeText({name:'My sauce',style:hotSauces.find(x=>x.id==='aged-red'),recipe:hotSauces.find(x=>x.id==='aged-red').recipe,total:300});for(const term of ['300 g','Original home interpretation','not an aged or fermented sauce','SHU is unknown','no validated shelf life','Flavor reference: https://'])assert.ok(t.includes(term),term)});
