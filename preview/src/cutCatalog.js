export const species = {
 beef:{name:'Beef',source:'https://www.beefitswhatsfordinner.com/cuts',regions:['chuck','rib','loin','sirloin','round','brisket','plate','flank','shank']},
 pork:{name:'Pork',source:'https://new.pork.org/cuts/',regions:['shoulder','loin','ham','belly','hock']},
 lamb:{name:'Lamb',source:'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/meat-catfish/lamb-farm-table',regions:['shoulder','rack','loin','leg','breast','shank']},
 goat:{name:'Goat',source:'https://cals.cornell.edu/nys-4-h-animal-science-programs/livestock/goats/goat-educational-resources/goat-product-id-study-guide',regions:['shoulder','rack','loin','leg','breast','shank']},
 deer:{name:'Deer',source:'https://extension.psu.edu/how-do-you-break-down-your-venison-carcass',regions:['neck','shoulder','loin','ribs','flank','leg','shank']},
 chicken:{name:'Chicken',modelReady:false,source:'https://national4hpoultry.mgcafe.uky.edu/marketpoultry/partsID',regions:['breast','wing','thigh','drumstick']},
 turkey:{name:'Turkey',modelReady:false,source:'https://www.eatturkey.org/cooking-turkey/',regions:['breast','wing','thigh','drumstick']}
};
const cut=(id,name,region,description,category='quick',image=null)=>({id,name,region,description,category,image});
export const catalog={
 beef:[
 cut('brisket','Brisket','brisket','The lower chest. A whole brisket contains the flat and point; they can also be sold separately.','smoke','brisket'),
 cut('chuck-roast','Chuck roast','chuck','A shoulder cut, often sold boneless. Ask your butcher which chuck roast you have.','smoke','chuck'),
 cut('ribeye','Ribeye','rib','A steak from the rib primal. Boneless and bone-in versions share the same origin.','quick','ribeye'),
 cut('flank-steak','Flank steak','flank','A broad, lean cut from the flank, behind the short plate.','quick','flank'),
 cut('strip','Strip steak','loin','A steak from the short loin. Also called a New York strip.'),
 cut('tenderloin','Tenderloin','loin','An interior muscle of the loin. This exterior model highlights its parent region.'),
 cut('sirloin','Sirloin steak','sirloin','From the sirloin, between the short loin and round.'),
 cut('round','Eye of round','round','A lean roast from the hind leg.','manual'),
 cut('short-ribs','Plate short ribs','plate','Ribs from the short plate. Chuck short ribs are a different cut.','smoke'),
 cut('shank','Beef shank','shank','A lower-leg cut commonly sold cross-cut with the bone.','manual')],
 pork:[
 cut('shoulder','Pork shoulder','shoulder','The front shoulder. Boston butt and picnic shoulder are different portions of this region.','smoke','pork-shoulder'),
 cut('butt','Boston butt','shoulder','The upper shoulder, despite its name.','smoke'),
 cut('picnic','Picnic shoulder','shoulder','The lower portion of the front shoulder.','smoke'),
 cut('loin','Pork loin','loin','A long back cut; sold as a roast or sliced into chops.'),
 cut('tenderloin','Pork tenderloin','loin','The smaller interior loin muscle. It is not the same as a pork loin roast.'),
 cut('ribs','Spare ribs','belly','Ribs from the belly side. Baby back ribs come from the loin.' ,'smoke'),
 cut('back-ribs','Baby back ribs','loin','The rib section adjacent to the loin.','smoke'),
 cut('belly','Pork belly','belly','The underside of the animal. Fresh belly and cured bacon are different preparations.','smoke'),
 cut('ham','Fresh ham','ham','The rear leg, uncured. A cured or fully cooked ham requires a different workflow.','manual'),
 cut('hock','Pork hock','hock','The lower leg; sold fresh, cured or smoked.','manual')],
};
for(const kind of ['lamb','goat']) {const label=species[kind].name;catalog[kind]=[
 cut('leg',`${label} leg`,'leg','The hind leg. Bone-in, boneless and butterflied versions share this origin.','manual',`${kind}-leg`),
 cut('shoulder',`${label} shoulder`,'shoulder','The front shoulder; available as a roast or shoulder chops.','smoke'),
 cut('rack',`Rack of ${kind}`,'rack','The rib section, commonly sold as a rack or individual rib chops.'),
 cut('loin',`${label} loin chops`,'loin','From the back behind the rack. Exterior highlighting shows the parent region.'),
 cut('breast',`${label} breast`,'breast','The lower chest and underside.','manual'),
 cut('shank',`${label} shank`,'shank','The lower portion of a leg.','manual')];}
catalog.deer=[
 cut('backstrap','Venison backstrap','loin','The long muscles along the spine. Buck and doe share the same cut locations.','quick','venison-backstrap'),
 cut('tenderloin','Venison tenderloin','loin','An interior muscle beneath the spine. Highlighting shows its parent loin region.'),
 cut('shoulder','Venison shoulder','shoulder','The front shoulder; a lean cut often used for slow cooking.','manual'),
 cut('hindquarter','Venison hindquarter','leg','The rear leg, containing several distinct roast muscles.','manual'),
 cut('ribs','Venison ribs','ribs','The rib section. Meat coverage varies with the animal.','manual'),
 cut('flank','Venison flank','flank','The thin abdominal muscle behind the ribs.','manual'),
 cut('neck','Venison neck','neck','The neck muscles, often prepared with moist heat.','manual'),
 cut('shank','Venison shank','shank','The lower legs, with connective tissue suited to slow cooking.','manual')];
for(const kind of ['chicken','turkey']) {const label=species[kind].name;catalog[kind]=[
 cut('whole',`Whole ${kind}`,'whole',`A dressed whole ${kind}, with head, feet and feathers removed. Whole-bird selection highlights all four mapped meat regions; head, neck, back and tail are not separate cut panels.`,'poultry'),
 cut('breast',`${label} breast`,'breast','The breast portion of the bird. Bone-in, boneless, skin-on and skinless versions share this origin.','poultry'),
 cut('wing',`${label} wings`,'wing','The wing contains the drumette, flat and tip. A wing drumette is different from a leg drumstick.','poultry'),
 cut('thigh',`${label} thighs`,'thigh','The upper portion of the leg, separated from the drumstick at the joint. Available bone-in or boneless.','poultry'),
 cut('drumstick',`${label} drumsticks`,'drumstick','The lower meaty portion of the leg, below the thigh. Feet are not part of this cut.','poultry')];
 catalog[kind][0].regions=[...species[kind].regions];}
// AI illustrative cut photos; source-linked text remains the anatomical reference.
for (const [kind,cuts] of Object.entries(catalog)) for (const item of cuts) {
 if (!item.image) item.image=`${kind==='deer'?'venison':kind}-${item.id}`;
}
export const regionName=id=>id==='whole'?'Whole bird':id.charAt(0).toUpperCase()+id.slice(1);
// Overview boundaries on the shared +Z-forward CC0 meshes, not a carcass dissection.
// z is normalized along animal length, y by standing height. Hide/head/tail stay unassigned.
export function regionAt(kind,z,y,x=0){
 if(z>.75||z<.09||y>.92)return null;
 if(kind==='beef'){
  if(y<.40)return (z>.56||z<.30)?'shank':null;
  if(z<.29)return 'round';
  if(z>.56)return y<.62?'brisket':'chuck';
  if(y<.62)return z>.40?'plate':'flank';
  return z>.43?'rib':z>.34?'loin':'sirloin';
 }
 if(kind==='pork'){
  if(y<.32)return (z>.55||z<.29)?'hock':null;
  if(z<.28)return 'ham';
  if(z>.55)return 'shoulder';
  return y>.62?'loin':'belly';
 }
 if(y<.38)return (z>.53||z<.28)?'shank':null;
 if(z<.29)return 'leg';
 if(z>.56)return 'shoulder';
 if(y<.58)return 'breast';
 return z>.40?'rack':'loin';
}
