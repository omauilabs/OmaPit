import {meatBudget} from './meatBudget.js';
export const dinnerBudgetKey='omapit-meat-dinner-v1';
export function validDinnerLine(line){return line&&typeof line.id==='string'&&typeof line.cut==='string'&&['benchmark','quote'].includes(line.mode)&&meatBudget(line)!==null&&typeof line.region==='string'&&typeof line.quality==='string'&&typeof line.record==='string'&&typeof line.source==='string'&&typeof line.savedAt==='string'&&Number.isFinite(Date.parse(line.savedAt))}
export function readDinner(){try{const items=JSON.parse(localStorage.getItem(dinnerBudgetKey)||'[]');return Array.isArray(items)?items.filter(validDinnerLine).slice(0,100):[]}catch{return []}}
export function dinnerTotals(lines){return lines.reduce((sum,line)=>{const r=meatBudget(line);return r?{raw:sum.raw+r.raw,cooked:sum.cooked+r.cooked,total:sum.total+r.total}:sum},{raw:0,cooked:0,total:0})}
