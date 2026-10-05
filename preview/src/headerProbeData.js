export function headerProbes(data, now, online=true) {
 const devices=(data?.devices||[]).filter(d=>d.source!=='replay');
 const selected=devices.find(d=>d.id===data?.selected_device);
 const ordered=selected?[selected,...devices.filter(d=>d!==selected)]:devices;
 return ordered.map(d=>({id:d.id,name:d.name||'Thermometer',channels:['food','ambient'].map(role=>{
 const c=d.channels?.[role],valid=Number.isFinite(c?.value)&&c?.quality!=='invalid';
 const age=Number.isFinite(c?.at)?Math.max(0,now-c.at):null;
 const fresh=valid&&online&&c.fresh===true&&age!==null&&age<=30;
 return {role,value:valid?c.value:null,age,state:!valid?'unavailable':!online?'offline':fresh?'live':'stale'};
 })}));
}
export function probeTemperature(value,unit) {return value==null?'—':(unit==='F'?value*9/5+32:value).toFixed(1);}
