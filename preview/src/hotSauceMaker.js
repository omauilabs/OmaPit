import {hotIngredients,hotSauces} from './hotSauceCatalog.js';
export const hotStorageKey='omapit-hot-sauce-lab-v1';
export function hotBatch(recipe,total){
 if(total===''||!Number.isFinite(Number(total))||total<10||total>10000||!recipe||typeof recipe!=='object'||Array.isArray(recipe))return null;
 const entries=Object.entries(recipe);
 if(!entries.length||entries.some(([id,v])=>!Object.hasOwn(hotIngredients,id)||v===''||!Number.isFinite(Number(v))||v<0||v>100))return null;
 const sum=entries.reduce((s,[,v])=>s+Number(v),0);if(!sum)return null;
 return {grams:Number(total),ingredients:entries.map(([id,v])=>({id,...hotIngredients[id],percent:100*Number(v)/sum,grams:Number(total)*Number(v)/sum})),pepperPercent:entries.reduce((s,[id,v])=>s+(hotIngredients[id].role==='Pepper'?Number(v):0),0)/sum*100};
}
export function hotDinner(guests,portion,reserve){
 if([guests,portion,reserve].some(x=>x===''))return null;
 const [g,p,r]=[guests,portion,reserve].map(Number);
 return Number.isInteger(g)&&g>=1&&g<=200&&Number.isFinite(p)&&p>=1&&p<=50&&Number.isFinite(r)&&r>=0&&r<=100?g*p*(1+r/100):null;
}
export function validateHotSaves(value){
 return Array.isArray(value)?value.filter(x=>x&&typeof x.id==='string'&&x.id.length<=100&&typeof x.name==='string'&&x.name.trim()&&x.name.length<=80&&hotSauces.some(s=>s.id===x.style)&&hotBatch(x.recipe,x.total)).slice(0,30):[];
}
export function hotRecipeText({name,style,recipe,total}){
 const batch=hotBatch(recipe,total);if(!batch)return '';
 return [`OmaPit · ${name.trim()||style.name}`,`Inspired by ${style.name} · ${style.region}`,`Original home interpretation; not a copied brand or source formula. Kitchen testing pending.`, `Ingredient charge: ${batch.grams} g. Cooking, straining and transfer losses change finished yield.`,...batch.ingredients.filter(x=>x.grams>0).map(x=>`${x.name}: ${x.grams.toFixed(2)} g (${x.percent.toFixed(2)}%)`),style.method,style.note,'Weigh prepared ingredients after cooking, peeling or rehydrating. Changing ingredients may require a different method. Qualitative heat labels describe the reference style; customized batch SHU is unknown.','Wear gloves for hot chilies, avoid eye contact, and ventilate when heating. Use clean utensils and reserve a serving portion before any raw-meat contact.','Refrigerate promptly at 40°F / 4.4°C or below. Make a small batch for near-term use. This formula has no validated shelf life, fermentation, canning or shelf-stability claim. Vinegar percentage is not a pH measurement.',`Flavor reference: ${style.source}`,'Handling: https://ask.fsis.usda.gov/article/How-do-I-handle-leftovers-safely'].join('\n\n');
}
