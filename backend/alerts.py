"""Persistent, source-aware alarm episodes. No network delivery is implied."""
import json, math, time, uuid

def migrate(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS alarm_rules(id TEXT PRIMARY KEY,cook TEXT NOT NULL,label TEXT NOT NULL,kind TEXT NOT NULL,role TEXT NOT NULL,device TEXT,threshold REAL,buffer REAL NOT NULL,repeat REAL NOT NULL,enabled INTEGER NOT NULL,created REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS alarm_state(rule TEXT PRIMARY KEY,pending REAL,episode TEXT,last_notice REAL);
    CREATE TABLE IF NOT EXISTS alarm_episodes(id TEXT PRIMARY KEY,rule TEXT NOT NULL,cook TEXT NOT NULL,label TEXT NOT NULL,opened REAL NOT NULL,resolved REAL,acknowledged REAL,snoozed_until REAL NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS alarm_notices(id INTEGER PRIMARY KEY,episode TEXT NOT NULL,at REAL NOT NULL,kind TEXT NOT NULL);
    ''')
    if 'food' not in [r[1] for r in db.execute('PRAGMA table_info(alarm_rules)')]:
        db.execute('ALTER TABLE alarm_rules ADD COLUMN food TEXT')
        db.commit()
    if 'hysteresis' not in [r[1] for r in db.execute('PRAGMA table_info(alarm_rules)')]:
        db.execute('ALTER TABLE alarm_rules ADD COLUMN hysteresis REAL NOT NULL DEFAULT 2')
        db.commit()

def number(value, low, high, label):
    if isinstance(value,bool):raise ValueError(label+' must be a number.')
    try:value=float(value)
    except (ValueError,TypeError):raise ValueError(label+' must be a number.')
    if not math.isfinite(value) or not low<=value<=high:raise ValueError(label+' is outside its allowed range.')
    return value

def add(db,cook,p,now=None):
    now=time.time() if now is None else now
    kind=p.get('kind');role=p.get('role','food');label=p.get('label','')
    if not isinstance(label,str):raise ValueError('Alarm label must be text.')
    label=label.strip()
    if kind not in ('high','low','stale','battery','timer'):raise ValueError('Unknown alarm type.')
    if role not in ('food','ambient','battery'):raise ValueError('Unknown sensor role.')
    if not 1<=len(label)<=100:raise ValueError('Alarm label is required (100 characters maximum).')
    food=p.get('food') or None
    if food and not db.execute('SELECT 1 FROM foods WHERE id=? AND cook=? AND finished IS NULL',(food,cook['id'])).fetchone():raise ValueError('Choose an active food in this cook.')
    device=p.get('device') or None
    if device:
        d=db.execute('SELECT source FROM devices WHERE id=?',(device,)).fetchone()
        if not d or d[0] not in ('ble','bridge'):raise ValueError('Choose a live device. Replay cannot trigger alarms.')
    if kind=='battery':
        if not device:raise ValueError('Battery alarms require a device.')
        role='battery'
    if kind in ('high','low'):
        threshold=number(p.get('threshold'),-40,1000,'Temperature')
        if p.get('unit')=='C':threshold=threshold*9/5+32
        elif p.get('unit')!='F':raise ValueError('Choose F or C.')
        if not -40<=threshold<=1000:raise ValueError('Temperature outside allowed range.')
        if role=='battery':raise ValueError('Use a battery alarm for battery channels.')
    elif kind=='stale':threshold=number(p.get('threshold',300 if not device else 30),5,86400,'Sample age')
    elif kind=='battery':threshold=number(p.get('threshold',20),1,100,'Battery threshold')
    else:threshold=now+number(p.get('seconds'),1,604800,'Timer duration')
    repeat=number(p.get('repeat',300),10,86400,'Repeat interval')
    buffer=number(p.get('buffer',0),0,3600,'Condition buffer')
    ident=uuid.uuid4().hex
    db.execute('INSERT INTO alarm_rules(id,cook,label,kind,role,device,threshold,buffer,repeat,enabled,created,food,hysteresis) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(ident,cook['id'],label,kind,role,device,threshold,buffer,repeat,1,now,food,number(p.get('hysteresis',2),0,100,'Hysteresis')))
    return ident

def sample(db,r):
    if r.get('food'):
        f=db.execute('SELECT * FROM foods WHERE id=?',(r['food'],)).fetchone()
        if not f or f['finished'] is not None:return None
        if f['device']:r={**r,'device':f['device'],'role':f['role']}
        else:
            row=db.execute("SELECT * FROM food_readings WHERE food=? AND source='manual' ORDER BY at DESC LIMIT 1",(f['id'],)).fetchone()
            return {'value':row['value_f'],'at':row['at'],'unit':'F','source':'manual'} if row else None
    if not r['device'] and not r.get('food'):
        selected=db.execute('SELECT device FROM cook_devices WHERE cook=?',(r['cook'],)).fetchone()
        if selected:r={**r,'device':selected[0]}
    if r['device']:
        row=db.execute('''SELECT c.*,d.source,d.error FROM channels c JOIN devices d ON d.id=c.device WHERE c.device=? AND c.role=?''',(r['device'],r['role'])).fetchone()
        if not row or row['source'] not in ('ble','bridge'):return None
        return {'value':None if row['error'] or row['quality']!='valid' else row['value'],'at':row['at'],'unit':row['unit'],'source':row['source']}
    row=db.execute("SELECT * FROM readings WHERE cook=? AND source IN ('manual','ble','bridge') ORDER BY at DESC LIMIT 1",(r['cook'],)).fetchone()
    return {'value':row['meat'] if r['role']=='food' else row['pit'],'at':row['at'],'unit':'F','source':row['source']} if row else None

def evaluate(db,now=None):
    now=time.time() if now is None else now
    for row in db.execute('SELECT r.*,c.finished,c.source FROM alarm_rules r JOIN cooks c ON c.id=r.cook'):
        r=dict(row);s=sample(db,r);condition=False
        food_done=r.get('food') and db.execute('SELECT finished FROM foods WHERE id=?',(r['food'],)).fetchone()[0] is not None
        if r['enabled'] and not food_done and r['finished'] is None and r['source']!='demo':
            if r['kind']=='timer':condition=now>=r['threshold']
            elif r['kind']=='stale':condition=now-(s['at'] if s else r['created'])>=r['threshold'] or (s is not None and s['value'] is None)
            elif s and s['value'] is not None and 0<=now-s['at']<= (300 if s['source']=='manual' else 30):
                v=s['value']*9/5+32 if s['unit']=='C' else s['value']
                in_episode=db.execute('SELECT episode FROM alarm_state WHERE rule=?',(r['id'],)).fetchone()
                h=r['hysteresis'] if in_episode and in_episode[0] and r['kind'] in ('high','low') else 0
                condition=v>=r['threshold']-h if r['kind']=='high' else v<=r['threshold']+h
        state=db.execute('SELECT * FROM alarm_state WHERE rule=?',(r['id'],)).fetchone()
        pending=state['pending'] if state else None;episode=state['episode'] if state else None;last=state['last_notice'] if state else None
        if not condition:
            if episode:db.execute('UPDATE alarm_episodes SET resolved=? WHERE id=? AND resolved IS NULL',(now,episode))
            pending=episode=last=None
        else:
            if pending is None:pending=now
            if now-pending>=r['buffer']:
                if not episode:
                    episode=uuid.uuid4().hex
                    db.execute('INSERT INTO alarm_episodes(id,rule,cook,label,opened) VALUES(?,?,?,?,?)',(episode,r['id'],r['cook'],r['label'],now))
                e=db.execute('SELECT * FROM alarm_episodes WHERE id=?',(episode,)).fetchone()
                if e['acknowledged'] is None and now>=e['snoozed_until'] and (last is None or now-last>=r['repeat']):
                    db.execute('INSERT INTO alarm_notices(episode,at,kind) VALUES(?,?,?)',(episode,now,'initial' if last is None else 'repeat'));last=now
        db.execute('INSERT OR REPLACE INTO alarm_state VALUES(?,?,?,?)',(r['id'],pending,episode,last))

def action(db,command,p):
    if command=='alarm_rule':
        if not isinstance(p.get('enabled'),bool):raise ValueError('Enabled must be true or false.')
        if not db.execute('UPDATE alarm_rules SET enabled=? WHERE id=?',(int(p['enabled']),p.get('id'))).rowcount:raise ValueError('Alarm not found.')
        return
    e=db.execute('SELECT * FROM alarm_episodes WHERE id=?',(p.get('id'),)).fetchone()
    if not e:raise ValueError('Alarm episode not found.')
    if command=='alarm_ack':db.execute('UPDATE alarm_episodes SET acknowledged=? WHERE id=?',(time.time(),e['id']))
    elif command=='alarm_snooze':db.execute('UPDATE alarm_episodes SET snoozed_until=? WHERE id=?',(time.time()+number(p.get('seconds',300),10,86400,'Snooze duration'),e['id']))
    else:raise ValueError('Unknown alarm action.')

def snapshot(db):
    return {'alarm_rules':[dict(r) for r in db.execute('SELECT * FROM alarm_rules ORDER BY created DESC')],
      'alarm_episodes':[dict(r) for r in db.execute('SELECT * FROM alarm_episodes ORDER BY opened DESC LIMIT 100')],
      'alarm_notices':[dict(r) for r in db.execute('SELECT n.*,e.label,e.cook FROM alarm_notices n JOIN alarm_episodes e ON n.episode=e.id ORDER BY n.id DESC LIMIT 100')]}
