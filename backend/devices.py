"""Device storage, replay and optional BLE transport for OmaPit."""
import argparse, asyncio, hashlib, json, math, subprocess, sys, time
from pathlib import Path
from adapters.chefiq import decode, MANUFACTURER_ID

STALE_SECONDS = 30

def migrate(db):
    version = db.execute('PRAGMA user_version').fetchone()[0]
    if version > 1: raise ValueError('Store was created by a newer OmaPit version.')
    if version < 1:
        # SQLite online backup preserves the original pre-device store.
        path = db.execute('PRAGMA database_list').fetchone()[2]
        if path and Path(path).exists():
            import sqlite3
            backup = Path(path + '.before-devices-v1.bak')
            if not backup.exists():
                target = sqlite3.connect(backup); db.backup(target); target.close()
        db.execute('BEGIN IMMEDIATE')
        if db.execute('PRAGMA user_version').fetchone()[0] >= 1:
            db.commit(); return
        migration='''
        CREATE TABLE IF NOT EXISTS devices(id TEXT PRIMARY KEY, name TEXT NOT NULL,
          model TEXT NOT NULL, protocol TEXT, evidence TEXT, source TEXT NOT NULL,
          last_seen REAL NOT NULL, rssi INTEGER, error TEXT, adapter_version TEXT);
        CREATE TABLE IF NOT EXISTS channels(device TEXT NOT NULL, role TEXT NOT NULL,
          value REAL, unit TEXT NOT NULL, at REAL NOT NULL, quality TEXT NOT NULL,
          PRIMARY KEY(device,role));
        CREATE TABLE IF NOT EXISTS samples(id INTEGER PRIMARY KEY, device TEXT NOT NULL,
          role TEXT NOT NULL, value REAL, unit TEXT NOT NULL, at REAL NOT NULL,
          source TEXT NOT NULL, quality TEXT NOT NULL, cook TEXT);
        CREATE INDEX IF NOT EXISTS samples_cook ON samples(cook,at);
        CREATE TABLE IF NOT EXISTS cook_devices(cook TEXT PRIMARY KEY, device TEXT NOT NULL);
        ALTER TABLE readings ADD COLUMN source TEXT NOT NULL DEFAULT 'manual';
        ALTER TABLE readings ADD COLUMN device TEXT;
        UPDATE readings SET source=COALESCE((SELECT source FROM cooks WHERE cooks.id=readings.cook),'manual');
        PRAGMA user_version=1;
        '''
        try:
            for statement in migration.split(';'):
                if statement.strip(): db.execute(statement)
            db.commit()
        except Exception:
            db.rollback(); raise

def setting(db, key, value):
    db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)', (key,json.dumps(value)))

def scanner_state(db):
    row=db.execute("SELECT value FROM settings WHERE key='scanner'").fetchone()
    value=json.loads(row[0]) if row else {'status':'idle'}
    if value.get('status')=='scanning' and time.time()-value.get('heartbeat',0)>15:
        value={**value,'status':'stopped','error':'Scanner stopped responding.'}
    return value

def snapshot(db):
    result=[]; now=time.time()
    for row in db.execute('SELECT * FROM devices ORDER BY last_seen DESC'):
        d=dict(row); d['channels']={r['role']:dict(r) for r in db.execute('SELECT * FROM channels WHERE device=?',(d['id'],))}
        d['status']='replay' if d['source']=='replay' else 'unsupported' if d['error'] else 'receiving' if now-d['last_seen']<=STALE_SECONDS else 'stale'
        for c in d['channels'].values(): c['fresh']=d['source'] in ('ble','bridge') and c['quality']=='valid' and now-c['at']<=STALE_SECONDS
        result.append(d)
    active=db.execute('SELECT id FROM cooks WHERE finished IS NULL ORDER BY started DESC LIMIT 1').fetchone()
    selected=db.execute('SELECT device FROM cook_devices WHERE cook=?',(active[0],)).fetchone() if active else None
    return {'devices':result,'selected_device':selected[0] if selected else None,'scanner':scanner_state(db),'stale_seconds':STALE_SECONDS}

def ingest(db, ident, payload, *, source='ble', at=None, name='', rssi=None):
    if not db.in_transaction:db.execute('BEGIN IMMEDIATE')
    if source not in ('ble','replay'): raise ValueError('Invalid source.')
    if not isinstance(ident,str) or not 1<=len(ident)<=160: raise ValueError('Invalid device identity.')
    if source=='replay' and not ident.startswith('replay:'): raise ValueError('Replay needs its own identity namespace.')
    if source=='ble' and not ident.startswith('ble:'): raise ValueError('BLE needs its own identity namespace.')
    at=time.time() if at is None else float(at)
    if not math.isfinite(at) or at<0 or at>time.time()+5: raise ValueError('Invalid sample timestamp.')
    known=db.execute('SELECT last_seen FROM devices WHERE id=?',(ident,)).fetchone()
    if known and at<known[0]: return False  # delayed data cannot overwrite latest state
    name=str(name or 'CHEF iQ probe')[:80]
    model=next((m for m in ['CQ50','CQ60'] if m in name.upper()),'Unknown')
    try: decoded=decode(payload); error=None
    except ValueError as e: decoded={'protocol':None,'evidence':'unsupported','adapter_version':'0.2.0','channels':{}}; error=str(e)
    db.execute('''INSERT INTO devices VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
      name=excluded.name,model=excluded.model,protocol=excluded.protocol,evidence=excluded.evidence,
      last_seen=excluded.last_seen,rssi=excluded.rssi,error=excluded.error,adapter_version=excluded.adapter_version''',
      (ident,name,model,decoded['protocol'],decoded['evidence'],source,at,rssi,error,decoded['adapter_version']))
    if error: return False
    cook=db.execute('''SELECT c.id FROM cooks c JOIN cook_devices d ON c.id=d.cook
      WHERE c.finished IS NULL AND c.source='ble' AND d.device=?''',(ident,)).fetchone() if source=='ble' else None
    for role,value in decoded['channels'].items():
        unit='%' if role=='battery' else 'C'; quality='valid' if value is not None else 'invalid'
        previous=db.execute('SELECT at FROM channels WHERE device=? AND role=?',(ident,role)).fetchone()
        if previous and at<=previous[0]: continue
        db.execute('INSERT OR REPLACE INTO channels VALUES(?,?,?,?,?,?)',(ident,role,value,unit,at,quality))
        db.execute('INSERT INTO samples(device,role,value,unit,at,source,quality,cook) VALUES(?,?,?,?,?,?,?,?)',
          (ident,role,value,unit,at,source,quality,cook[0] if cook else None))
    # Legacy chart compatibility: only a same-packet, valid food/ambient pair.
    channels=decoded['channels']
    if cook and all(channels.get(k) is not None for k in ['food','ambient']):
        db.execute('INSERT INTO readings(cook,at,meat,pit,source,device) VALUES(?,?,?,?,?,?)',
          (cook[0],at,channels['food']*9/5+32,channels['ambient']*9/5+32,'ble',ident))
    return True

def select(db, ident, cook):
    if not cook or cook['source']=='demo': raise ValueError('Start a manual cook before selecting a live probe.')
    d=db.execute('SELECT * FROM devices WHERE id=?',(ident,)).fetchone()
    if not d or d['source']!='ble' or d['error']: raise ValueError('Select a supported live BLE probe. Replay cannot record a cook.')
    if time.time()-d['last_seen']>STALE_SECONDS: raise ValueError('Probe is stale. Scan nearby before selecting it.')
    db.execute('INSERT OR REPLACE INTO cook_devices VALUES(?,?)',(cook['id'],ident))
    db.execute("UPDATE cooks SET source='ble' WHERE id=?",(cook['id'],))

def replay(db, path):
    path=Path(path); digest=hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    rows=[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if len(rows)>10000: raise ValueError('Capture exceeds 10000 packets.')
    for row in rows:
        if row.get('schema')!=1: raise ValueError('Unsupported capture schema.')
        at=float(row['relative_seconds'])
        if not math.isfinite(at) or at<0: raise ValueError('Invalid relative timestamp.')
        ident='replay:'+digest+':'+str(row['device'])
        ingest(db,ident,bytes.fromhex(row['payload_hex']),source='replay',at=at,name=row.get('name','CHEF iQ replay'),rssi=row.get('rssi'))
    return len(rows)

async def scan(dbpath, seconds, capture=None, address=None):
    from omapit import database
    db=database(dbpath); start=time.time(); alias={}; output=None
    try:
        from bleak import BleakScanner
        if capture and not address: raise ValueError('Capture requires --address to select one probe.')
        if capture: output=open(capture,'x')
        def received(device, advert):
            payload=advert.manufacturer_data.get(MANUFACTURER_ID)
            if payload is None or not 2<=len(payload)<=18: return
            if address and device.address.lower()!=address.lower(): return
            with db:
                ingest(db,'ble:'+device.address,payload,name=advert.local_name or device.name or 'CHEF iQ probe',rssi=advert.rssi)
            if output:
                label=alias.setdefault(device.address,'probe-'+str(len(alias)+1))
                safe=bytearray(payload)
                if (payload[0]&15)==3 or ((payload[0]&15)==1 and (payload[1]>>4)<2):safe[2:8]=bytes(min(6,len(safe)-2))
                output.write(json.dumps({'schema':1,'device':label,'name':'CHEF iQ probe','relative_seconds':round(time.time()-start,3),'payload_hex':safe.hex(),'rssi':advert.rssi})+'\n');output.flush()
        async with BleakScanner(detection_callback=received):
            while True:
                recording=db.execute("SELECT 1 FROM cooks c JOIN cook_devices d ON c.id=d.cook WHERE c.finished IS NULL AND c.source='ble' LIMIT 1").fetchone() is not None
                if time.time()-start>=seconds and not recording: break
                with db: setting(db,'scanner',{'status':'scanning','heartbeat':time.time(),'ends':None if recording else start+seconds,'recording':recording})
                await asyncio.sleep(1)
        with db: setting(db,'scanner',{'status':'idle','heartbeat':time.time()})
    except Exception as e:
        message='Bluetooth support needs the optional bleak package.' if isinstance(e,ImportError) else 'Bluetooth scan failed: '+str(e)[:200]
        with db: setting(db,'scanner',{'status':'error','error':message,'heartbeat':time.time()})
    finally:
        if output: output.close()
        db.close()

def start_scan(db, dbpath):
    if scanner_state(db).get('status')=='scanning': return
    setting(db,'scanner',{'status':'scanning','heartbeat':time.time(),'ends':time.time()+60})
    db.commit()
    try:
        subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--db',str(dbpath),'scan','--seconds','60'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    except OSError:
        setting(db,'scanner',{'status':'error','error':'Cannot start Bluetooth worker.'});db.commit()

def main():
    p=argparse.ArgumentParser();p.add_argument('--db');sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('scan');s.add_argument('--seconds',type=int,default=60);s.add_argument('--capture');s.add_argument('--address')
    r=sub.add_parser('replay');r.add_argument('path');args=p.parse_args()
    if args.command=='scan':
        if not 1<=args.seconds<=3600:p.error('seconds must be between 1 and 3600')
        asyncio.run(scan(args.db,args.seconds,args.capture,args.address))
    else:
        from omapit import database
        db=database(args.db)
        try:
            with db: count=replay(db,args.path)
            print(json.dumps({'packets':count,**snapshot(db)}))
        finally: db.close()
if __name__=='__main__':main()
