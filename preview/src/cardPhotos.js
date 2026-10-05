import './card-photos.css';
// Each atlas is a reviewed, ordered collection of illustrative photographs.
const groups={
 hotSauces:['red','garlic','chipotle','orange','verde','herb','mustard','harissa','sambal','tamarind','creamy','roasted'],
 rubRegions:['black','bbq','garlic','cajun','jerk','ancho','coffee','lemon','ras','berbere','shichimi','zaatar'],
 equipment:['gas','charcoal','kamado','pellet','offset','water','drum','gravity','electric','propane','griddle','openfire','hibachi','infrared','pizza','contact'],
 peppers:['bell','anaheim','poblano','jalapeno','serrano','cayenne','thai','habanero','scotch-bonnet','ghost'],
 knives:['chef','boning','fillet','slicer','carving','breaker','cleaver','skinner','utility','saw'],
 wood:['alder','apple','cherry','maple','pecan','oak','hickory','mesquite'],
 rubs:['pepper','sweet','chili','herb','saltfree','mustard'],
 foods:['texas-toast','sourdough','flatbread','buns','cornbread','garlic-bread','pinto','potato-salad','bbq-beans','creamy-slaw','red-slaw','memphis-beans','corn','zucchini','asparagus','peppers'],
 veggies:['mushrooms','eggplant','onions','potato','cauliflower','cabbage'],
 extras:['hushpuppies','memphis-slaw']
};
const dimensions={hotSauces:[4,3],rubRegions:[4,3],equipment:[4,4],peppers:[4,3],knives:[4,3],wood:[4,2],rubs:[3,2],foods:[4,4],veggies:[3,2],extras:[2,1]};
export function cardPhoto(family,id){
 if(family==='market'){const names={brisket:'brisket',chuck:'chuck',strip:'beef-strip',ribeye:'ribeye',ribs:'beef-short-ribs',round:'beef-round'};const key=id.startsWith('brisket')?'brisket':id;return {'--card-photo':`url("/assets/cuts/${names[key]}.webp")`,'--photo-size':'cover','--photo-position':'center'};}
 let group=family;if(['bread','sides','veggies'].includes(family))group=groups.foods.includes(id)?'foods':groups.veggies.includes(id)?'veggies':'extras';
 const index=groups[group]?.indexOf(id);if(index==null||index<0)return {};
 const [cols,rows]=dimensions[group];return {'--card-photo':`url("/assets/cards/${group}.jpg")`,'--photo-size':`${cols*100}% ${rows*100}%`,'--photo-position':`${cols===1?0:index%cols/(cols-1)*100}% ${rows===1?0:Math.floor(index/cols)/(rows-1)*100}%`};
}
