"""Versioned temperature ingestion; optional HA polling and MQTT subscription."""
from http_util import open_request
import argparse,json,math,os,time,urllib.request
from pathlib import Path
from alerts import number
ROLES={'food','ambient','battery'}

def ingest(db,p,now=None):
    if not db.in_transaction:db.execute('BEGIN IMMEDIATE')
    now=time.time() if now is None else now
    if p.get('schema')!=1:raise ValueError('Bridge schema must be 1.')
    if p.get('source') not in ('home-assistant','mqtt','json'):raise ValueError('Unknown bridge source.')
    device=p.get('device')
    if not isinstance(device,str) or not 1<=len(device)<=120:raise ValueError('A stable device identity is required.')
    name=p.get('name',device)
    if not isinstance(name,str) or not 1<=len(name)<=100:raise ValueError('Device name must be 1–100 characters.')
    if not isinstance(p.get('retained',False),bool):raise ValueError('Retained must be a boolean.')
    at=number(p.get('sample_at'),0,now+5,'Sample timestamp')
    if p.get('retained') or now-at>30:raise ValueError('Historical / retained samples cannot update live channels. Use journal import.')
    channels=p.get('channels')
    if not isinstance(channels,dict) or not 1<=len(channels)<=3 or not set(channels)<=ROLES:raise ValueError('Use food, ambient or battery channels.')
    normalized={}
    for role,c in channels.items():
        if not isinstance(c,dict):raise ValueError('Channel must be an object.')
        unit=c.get('unit');value=c.get('value')
        if role=='battery':
            if unit!='%':raise ValueError('Battery unit must be %.')
            value=None if value is None else number(value,0,100,'Battery')
        else:
            if unit not in ('C','F'):raise ValueError('Temperature unit must be C or F.')
            value=None if value is None else number(value,-40,1000,'Temperature')
            if value is not None and unit=='F':value=(value-32)*5/9
            if value is not None and not -40<=value<=(1000-32)*5/9:raise ValueError('Temperature outside supported range.')
            unit='C'
        normalized[role]=(value,unit)
    ident='bridge:'+p['source']+':'+device
    previous=db.execute('SELECT last_seen FROM devices WHERE id=?',(ident,)).fetchone()
    normalized={role:pair for role,pair in normalized.items() if (lambda r: not r or at>r[0])(db.execute('SELECT at FROM channels WHERE device=? AND role=?',(ident,role)).fetchone())}
    if not normalized:return {'accepted':False,'reason':'duplicate or out of order','id':ident}
    model=str(p.get('model','Bridge entity'))[:100]
    db.execute('''INSERT INTO devices VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,model=excluded.model,last_seen=MAX(devices.last_seen,excluded.last_seen),error=NULL''',(ident,name,model,'bridge-v1','Contract-tested; live device unverified','bridge',at,None,None,'0.3.0'))
    for role,(v,u) in normalized.items():
        quality='invalid' if v is None else 'valid'
        db.execute('INSERT OR REPLACE INTO channels VALUES(?,?,?,?,?,?)',(ident,role,v,u,at,quality))
        db.execute('INSERT INTO samples(device,role,value,unit,at,source,quality) VALUES(?,?,?,?,?,?,?)',(ident,role,v,u,at,'bridge',quality))
    return {'accepted':True,'id':ident}

def ha_payload(state,role,device,now=None):
    from datetime import datetime
    now=time.time() if now is None else now
    attrs=state.get('attributes',{})
    try:at=datetime.fromisoformat(state.get('last_reported',state.get('last_updated','')).replace('Z','+00:00')).timestamp()
    except (KeyError,TypeError,ValueError):raise ValueError('Home Assistant entity needs last_updated.')
    try:value=float(state['state'])
    except (KeyError,TypeError,ValueError):value=None
    unit=attrs.get('unit_of_measurement','').replace('°','')
    return {'schema':1,'source':'home-assistant','device':device,'name':attrs.get('friendly_name',device),'sample_at':at,'retained':False,'channels':{role:{'value':value,'unit':unit}}}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db');sub=p.add_subparsers(dest='mode',required=True)
    j=sub.add_parser('json');j.add_argument('path')
    h=sub.add_parser('ha');h.add_argument('--url',required=True);h.add_argument('--entity',required=True);h.add_argument('--role',choices=sorted(ROLES),default='food');h.add_argument('--interval',type=int,default=15)
    m=sub.add_parser('mqtt');m.add_argument('--host',required=True);m.add_argument('--port',type=int,default=1883);m.add_argument('--topic',required=True);m.add_argument('--tls',action='store_true')
    args=p.parse_args();from omapit import database
    db=database(args.db)
    def accept(data):
        try:
            with db:result=ingest(db,data)
            print(json.dumps(result),flush=True)
        except ValueError as e:print(json.dumps({'error':str(e)}),flush=True)
    if args.mode=='json':
        raw=Path(args.path).read_bytes()
        if len(raw)>1024*1024:p.error('JSON input exceeds 1 MiB.')
        accept(json.loads(raw))
    elif args.mode=='ha':
        token=os.environ.get('OMAPIT_HA_TOKEN')
        if not token:p.error('Set OMAPIT_HA_TOKEN; tokens are never written to the journal.')
        if not 5<=args.interval<=3600:p.error('Choose interval 5–3600 seconds.')
        from urllib.parse import urlparse,quote
        u=urlparse(args.url)
        if u.scheme not in ('http','https') or not u.hostname or u.username:p.error('Choose an HTTP(S) Home Assistant URL without embedded credentials.')
        while True:
            try:
                req=urllib.request.Request(args.url.rstrip('/')+'/api/states/'+quote(args.entity,safe=''),headers={'Authorization':'Bearer '+token})
                with open_request(req,timeout=10) as response:state=json.loads(response.read(1048576))
                accept(ha_payload(state,args.role,args.entity))
            except Exception:print(json.dumps({'error':'Home Assistant unavailable or sample rejected; inspect local configuration.'}),flush=True)
            time.sleep(args.interval)
    else:
        try:import paho.mqtt.client as mqtt
        except ImportError:p.error('Install optional requirements-bridge.txt for MQTT.')
        if '#' in args.topic or '+' in args.topic:p.error('Use one exact topic, without wildcards.')
        client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if os.environ.get('OMAPIT_MQTT_USER'):client.username_pw_set(os.environ['OMAPIT_MQTT_USER'],os.environ.get('OMAPIT_MQTT_PASSWORD'))
        if args.tls:client.tls_set()
        def connected(client,userdata,flags,reason,properties):
            if reason==0:client.subscribe(args.topic)
        def message(client,userdata,msg):
            if len(msg.payload)>8192:return
            try:
                data=json.loads(msg.payload)
                if not isinstance(data,dict):return
                data['source']='mqtt';data['retained']=bool(msg.retain) or data.get('retained',False);accept(data)
            except (UnicodeDecodeError,ValueError):print('Invalid MQTT message',flush=True)
        client.on_connect=connected;client.on_message=message
        client.connect(args.host,args.port,60);client.loop_forever()
    db.close()
if __name__=='__main__':main()
