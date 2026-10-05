import test from 'node:test';
import assert from 'node:assert/strict';
import {meatBudget} from '../src/meatBudget.js';
test('converts cooked portions to raw purchase weight with yield and reserve',()=>{const r=meatBudget({guests:8,portion:6,yieldPercent:60,reserve:10,price:5.60});assert.ok(Math.abs(r.raw-5.5)<1e-10);assert.ok(Math.abs(r.total-30.8)<1e-10);assert.ok(Math.abs(r.perGuest-3.85)<1e-10)});
test('full yield and no reserve retain cooked weight',()=>{assert.equal(meatBudget({guests:4,portion:8,yieldPercent:100,reserve:0,price:10}).total,20)});
test('rejects zero yield and non-finite prices rather than showing a false cost',()=>{assert.equal(meatBudget({guests:8,portion:6,yieldPercent:0,reserve:0,price:5}),null);assert.equal(meatBudget({guests:8,portion:6,yieldPercent:60,reserve:0,price:NaN}),null)});
import {dinnerTotals,validDinnerLine} from '../src/dinnerBudgetStore.js';
test('combined shopping list adds raw weight and cost, not overlapping guest counts',()=>{const sum=dinnerTotals([{guests:8,portion:3,yieldPercent:50,reserve:0,price:5},{guests:8,portion:3,yieldPercent:75,reserve:0,price:10}]);assert.equal(sum.raw,5);assert.equal(sum.total,35);assert.equal(sum.cooked,3);assert.equal(sum.guests,undefined)});
test('malformed saved records are rejected before rendering',()=>{assert.equal(validDinnerLine({id:'bad',cut:'Brisket',region:'National',quality:'Choice',mode:'quote',guests:8,portion:6,yieldPercent:60,reserve:0,price:5}),false)});
