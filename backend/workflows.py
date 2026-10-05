"""Meal foods, explicit workflows and dependency-aware serving plans."""
import json,time,uuid
from datetime import datetime
from alerts import number
PRESETS={
 'quick':['Prep','Grill','Rest','Serve'],
 'poultry':['Prep','Cook','Rest','Serve'],
 'vegetables':['Prep','Grill','Serve'],
 'smoke':['Prep','Smoke','Wrap (optional)','Rest','Serve'],
 'manual':['Cook','Serve']}

def migrate(db):
    db.executescript('''CREATE TABLE IF NOT EXISTS foods(id TEXT PRIMARY KEY,cook TEXT NOT NULL,name TEXT NOT NULL,category TEXT NOT NULL,zone TEXT NOT NULL,target_f REAL NOT NULL,steps TEXT NOT NULL,stage INTEGER NOT NULL DEFAULT 0,device TEXT,role TEXT NOT NULL DEFAULT 'food',created REAL NOT NULL,finished REAL);
    CREATE TABLE IF NOT EXISTS food_readings(id INTEGER PRIMARY KEY,food TEXT NOT NULL,at REAL NOT NULL,value_f REAL NOT NULL,source TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS meal_goals(cook TEXT PRIMARY KEY,serve_at REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS plan_tasks(id TEXT PRIMARY KEY,cook TEXT NOT NULL,food TEXT,name TEXT NOT NULL,duration REAL NOT NULL,depends TEXT NOT NULL,completed REAL);
    CREATE TABLE IF NOT EXISTS outcomes(cook TEXT PRIMARY KEY,rating INTEGER,texture TEXT,taste TEXT,photo TEXT);
    CREATE INDEX IF NOT EXISTS food_readings_food ON food_readings(food,at);
    ''')

def label(value,name,limit=100):
    if not isinstance(value,str) or not 1<=len(value.strip())<=limit:raise ValueError(name+' is required.')
    return value.strip()

def steps(value):
    if isinstance(value,str):value=[v.strip() for v in value.splitlines() if v.strip()]
    if not isinstance(value,list) or not 1<=len(value)<=16:raise ValueError('Choose 1–16 steps.')
    return [label(v,'Step',80) for v in value]

def get_food(db,p):
    f=db.execute('SELECT f.*,c.source,c.finished AS cook_finished FROM foods f JOIN cooks c ON c.id=f.cook WHERE f.id=?',(p.get('id'),)).fetchone()
    if not f:raise ValueError('Food not found.')
    if f['cook_finished'] is not None or f['finished'] is not None:raise ValueError('Food is already completed.')
    return f

def action(db,cmd,p,cook):
    if cmd=='food_add':
        if not cook or cook['source']=='demo':raise ValueError('Start a real cook first.')
        category=p.get('category','manual')
        if category not in PRESETS:raise ValueError('Choose a food category.')
        target=number(p.get('target'),-40,1000,'Target temperature')
        if p.get('unit')=='C':target=target*9/5+32
        elif p.get('unit')!='F':raise ValueError('Choose F or C.')
        if not -40<=target<=1000:raise ValueError('Target outside allowed range.')
        path=steps(p.get('steps') or PRESETS[category])
        ident=uuid.uuid4().hex
        db.execute('INSERT INTO foods(id,cook,name,category,zone,target_f,steps,created) VALUES(?,?,?,?,?,?,?,?)',(ident,cook['id'],label(p.get('name'),'Food name'),category,label(p.get('zone','Main grill'),'Zone'),target,json.dumps(path),time.time()))
        return ident
    if cmd in ('food_edit','food_advance','food_finish','food_map','food_reading','food_alarm'):
        f=get_food(db,p)
        if cmd=='food_edit':
            path=steps(p.get('steps'));target=number(p.get('target'),-40,1000,'Target temperature')
            if p.get('unit')=='C':target=target*9/5+32
            elif p.get('unit')!='F':raise ValueError('Choose F or C.')
            if not -40<=target<=1000:raise ValueError('Target outside allowed range.')
            if f['stage']>=len(path):raise ValueError('Keep enough steps for the current stage.')
            db.execute('UPDATE foods SET name=?,zone=?,target_f=?,steps=? WHERE id=?',(label(p.get('name'),'Food name'),label(p.get('zone'),'Zone'),target,json.dumps(path),f['id']))
        elif cmd=='food_advance':
            if p.get('expected_stage')!=f['stage']:raise ValueError('Food stage changed. Refresh before advancing.')
            path=json.loads(f['steps'])
            if f['stage']>=len(path)-1:raise ValueError('Finish this food instead.')
            db.execute('UPDATE foods SET stage=stage+1 WHERE id=?',(f['id'],))
        elif cmd=='food_finish':db.execute('UPDATE foods SET finished=? WHERE id=?',(time.time(),f['id']))
        elif cmd=='food_map':
            device=p.get('device') or None;role=p.get('role','food')
            if role not in ('food','ambient'):raise ValueError('Choose food or ambient.')
            if device:
                d=db.execute('SELECT * FROM devices WHERE id=?',(device,)).fetchone()
                if not d or d['source'] not in ('ble','bridge') or d['error']:raise ValueError('Choose a supported live device.')
            db.execute('UPDATE foods SET device=?,role=? WHERE id=?',(device,role,f['id']))
        elif cmd=='food_alarm':
            import alerts
            alerts.add(db,{'id':f['cook']},{'kind':'high','label':f['name']+' target','food':f['id'],'device':f['device'],'role':f['role'],'threshold':f['target_f'],'unit':'F'})
        else:
            if f['device']:raise ValueError('Unmap the device before entering a manual reading.')
            v=number(p.get('value'),-40,1000,'Temperature')
            if p.get('unit')=='C':v=v*9/5+32
            elif p.get('unit')!='F':raise ValueError('Choose F or C.')
            if not -40<=v<=1000:raise ValueError('Temperature outside allowed range.')
            db.execute('INSERT INTO food_readings(food,at,value_f,source) VALUES(?,?,?,?)',(f['id'],time.time(),v,'manual'))
        return f['id']
    if not cook or cook['source']=='demo':raise ValueError('Start a real cook first.')
    if cmd=='meal_goal':
        try:
            date=datetime.fromisoformat(p['serve_at'])
            if date.tzinfo is None:raise ValueError()
            at=date.timestamp()
            number(at,time.time()-86400,time.time()+366*86400,'Serving date')
        except (KeyError,TypeError,ValueError):raise ValueError('Choose a serving date with a time zone.')
        db.execute('INSERT OR REPLACE INTO meal_goals VALUES(?,?)',(cook['id'],at))
    elif cmd in ('task_add','task_edit'):
        duration=number(p.get('minutes'),0,10080,'Task duration')*60
        depends=p.get('depends',[])
        if not isinstance(depends,list) or len(depends)>100 or any(not isinstance(x,str) for x in depends):raise ValueError('Invalid dependencies.')
        valid={r[0] for r in db.execute('SELECT id FROM plan_tasks WHERE cook=?',(cook['id'],))}
        if not set(depends)<=valid:raise ValueError('Dependencies must belong to this meal.')
        food=p.get('food') or None
        if food and not db.execute('SELECT 1 FROM foods WHERE id=? AND cook=?',(food,cook['id'])).fetchone():raise ValueError('Food must belong to this meal.')
        ident=p.get('id') if cmd=='task_edit' else uuid.uuid4().hex
        if cmd=='task_edit':
            if ident not in valid:raise ValueError('Task not found.')
            db.execute('UPDATE plan_tasks SET name=?,duration=?,depends=?,food=? WHERE id=?',(label(p.get('name'),'Task'),duration,json.dumps(list(dict.fromkeys(depends))),food,ident))
        else:db.execute('INSERT INTO plan_tasks VALUES(?,?,?,?,?,?,?)',(ident,cook['id'],food,label(p.get('name'),'Task'),duration,json.dumps(list(dict.fromkeys(depends))),None))
        import planner
        planner.task_meta(db,cook['id'],ident,p)
        schedule(db,cook['id']) # Reject cycles transactionally.
        return ident
    elif cmd=='task_done':
        import planner
        cfg=planner.config(db,cook['id'])
        if p.get('done') is False:
            if any(p.get('id') in t['depends'] and (t['completed'] is not None or cfg['tasks'].get(t['id'],{}).get('started')) for t in schedule(db,cook['id'])['tasks']):raise ValueError('Reopen later dependent steps first.')
            cfg['tasks'].setdefault(p.get('id'),{}).pop('started',None);planner.save(db,cook['id'],cfg)
        if p.get('done') and any(t['id']==p.get('id') and not t['ready'] for t in schedule(db,cook['id'])['tasks']):raise ValueError('Finish dependency steps first.')
        if not isinstance(p.get('done'),bool):raise ValueError('Done must be true or false.')
        if not db.execute('UPDATE plan_tasks SET completed=? WHERE id=? AND cook=?',(time.time() if p['done'] else None,p.get('id'),cook['id'])).rowcount:raise ValueError('Task not found.')
    elif cmd=='task_delete':
        task=p.get('id')
        if any(t['id']==task and t['started'] and t['completed'] is None for t in schedule(db,cook['id'])['tasks']):raise ValueError('Finish the running step before removing it.')
        if any(task in json.loads(r[0]) for r in db.execute('SELECT depends FROM plan_tasks WHERE cook=?',(cook['id'],))):raise ValueError('Remove this task from dependent steps first.')
        db.execute('DELETE FROM plan_tasks WHERE id=? AND cook=?',(task,cook['id']))
        import planner
        cfg=planner.config(db,cook['id']);cfg['tasks'].pop(task,None);planner.save(db,cook['id'],cfg)
    else:raise ValueError('Unknown workflow action.')

def schedule(db,cook,now=None):
    now=time.time() if now is None else now
    goal=db.execute('SELECT serve_at FROM meal_goals WHERE cook=?',(cook,)).fetchone()
    tasks={r['id']:{**dict(r),'depends':json.loads(r['depends'])} for r in db.execute('SELECT * FROM plan_tasks WHERE cook=?',(cook,))}
    if len(tasks)>200:raise ValueError('A meal supports up to 200 tasks.')
    order=[];visiting=set();visited=set()
    def visit(ident):
        if ident in visiting:raise ValueError('Task dependencies contain a cycle.')
        if ident in visited:return
        if ident not in tasks:raise ValueError('Task dependency missing.')
        visiting.add(ident)
        for d in tasks[ident]['depends']:visit(d)
        visiting.remove(ident);visited.add(ident);order.append(ident)
    import planner
    cfg=planner.config(db,cook)
    for ident in sorted(tasks,key=lambda k:0 if cfg['tasks'].get(k,{}).get('started') and not tasks[k]['completed'] else 1):visit(ident)
    import planner
    return planner.schedule(tasks,order,goal[0] if goal else None,now,planner.config(db,cook))

def food_data(db,f,now):
    f=dict(f);f['steps']=json.loads(f['steps'])
    if f['device']:
        c=db.execute('SELECT c.*,d.source,d.error FROM channels c JOIN devices d ON d.id=c.device WHERE c.device=? AND role=?',(f['device'],f['role'])).fetchone()
        f['reading']={'value_f':c['value']*9/5+32 if c['unit']=='C' and c['value'] is not None else c['value'],'at':c['at'],'source':c['source'],'fresh':c['quality']=='valid' and not c['error'] and 0<=now-c['at']<=30} if c else None
    else:
        r=db.execute('SELECT * FROM food_readings WHERE food=? ORDER BY at DESC LIMIT 1',(f['id'],)).fetchone()
        f['reading']={**dict(r),'fresh':0<=now-r['at']<=300} if r else None
    return f

def record_channels(db):
    for f in db.execute('SELECT f.* FROM foods f JOIN cooks c ON c.id=f.cook WHERE f.finished IS NULL AND c.finished IS NULL AND f.device IS NOT NULL'):
        c=db.execute('SELECT c.*,d.source,d.error FROM channels c JOIN devices d ON d.id=c.device WHERE c.device=? AND role=?',(f['device'],f['role'])).fetchone()
        if not c or c['source'] not in ('ble','bridge') or c['error'] or c['quality']!='valid' or c['value'] is None:continue
        last=db.execute('SELECT MAX(at) FROM food_readings WHERE food=?',(f['id'],)).fetchone()[0]
        if c['at']<f['created'] or (last is not None and c['at']<=last):continue
        v=c['value']*9/5+32 if c['unit']=='C' else c['value']
        db.execute('INSERT INTO food_readings(food,at,value_f,source) VALUES(?,?,?,?)',(f['id'],c['at'],v,c['source']))

def snapshot(db,cook):
    now=time.time()
    return {'foods':[food_data(db,r,now) for r in db.execute('SELECT * FROM foods WHERE cook=? ORDER BY created',(cook['id'],))] if cook else [],'plan':schedule(db,cook['id'],now) if cook else {'tasks':[],'serve_at':None}}
