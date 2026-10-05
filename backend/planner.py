"""Explicit grill reservations and atomic guided meal setup; no hardware control."""
import json,time,uuid
from workflows import label
from alerts import number

def config(db,cook):
    row=db.execute('SELECT value FROM settings WHERE key=?',('planner:'+cook,)).fetchone()
    if not row:return {'resources':[],'tasks':{}}
    try:
        c=json.loads(row[0]);c['resources']=resources(c['resources'])
        if not isinstance(c['tasks'],dict):raise ValueError()
        for ident,m in c['tasks'].items():
            if not isinstance(ident,str) or not isinstance(m,dict):raise ValueError()
            if m.get('resource','') and m['resource'] not in {r['id'] for r in c['resources']}:raise ValueError()
            slots=number(m.get('slots',1),1,20,'Space used')
            if slots!=int(slots):raise ValueError()
            m['slots']=int(slots)
            if m.get('pit_f') is not None:m['pit_f']=number(m['pit_f'],-40,1000,'Pit temperature')
            if m.get('started') is not None:m['started']=number(m['started'],0,time.time()+5,'Step start')
        return c
    except (ValueError,TypeError,KeyError):raise ValueError('Invalid saved grill plan.')

def save(db,cook,value):
    db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',('planner:'+cook,json.dumps(value)))

def resources(value):
    if not isinstance(value,list) or len(value)>8:raise ValueError('Choose up to eight grills / zones.')
    result=[]
    for r in value:
        if not isinstance(r,dict):raise ValueError('Invalid grill configuration.')
        ident=label(r.get('id'),'Grill identifier',80)
        slots=number(r.get('capacity'),1,20,'Grill capacity')
        if slots!=int(slots):raise ValueError('Capacity must be a whole number.')
        result.append({'id':ident,'name':label(r.get('name'),'Grill name'), 'capacity':int(slots)})
    if len({r['id'] for r in result})!=len(result):raise ValueError('Grill identifiers must be unique.')
    return result

def task_meta(db,cook,ident,p):
    c=config(db,cook);old=c['tasks'].get(ident,{})
    resource=p.get('resource',old.get('resource','')) or ''
    grill=next((r for r in c['resources'] if r['id']==resource),None)
    if resource and not grill:raise ValueError('Choose a configured grill.')
    slots=number(p.get('slots',old.get('slots',1)),1,20,'Space used')
    if slots!=int(slots) or grill and slots>grill['capacity']:raise ValueError('Space used exceeds grill capacity.')
    pit=p.get('pit_f',old.get('pit_f'))
    pit=None if pit in ('',None) else number(pit,-40,1000,'Pit temperature')
    running=db.execute('SELECT completed FROM plan_tasks WHERE id=?',(ident,)).fetchone()
    if old.get('started') and running and running[0] is None and (resource!=old.get('resource','') or int(slots)!=old.get('slots',1) or pit!=old.get('pit_f')):raise ValueError('Finish the running step before changing its grill reservation.')
    c['tasks'][ident]={**old,'resource':resource,'slots':int(slots),'pit_f':pit}
    save(db,cook,c)

def fit(start,duration,book,slots,capacity,pit,back=False):
    """Find a feasible interval; incompatible temperatures require separate time."""
    for _ in range(1000):
        end=start+duration
        overlap=[r for r in book if r['start']<end and r['end']>start]
        points=sorted({start,end}|{max(start,r['start']) for r in overlap}|{min(end,r['end']) for r in overlap})
        conflicts=[]
        for a,b in zip(points,points[1:]):
            running=[r for r in overlap if r['start']<b and r['end']>a]
            if slots+sum(r['slots'] for r in running)>capacity or any(pit is None or r['pit'] is None or abs(pit-r['pit'])>25 for r in running):conflicts+=running
        if not conflicts:return start
        start=min(r['start'] for r in conflicts)-duration if back else max(r['end'] for r in conflicts)
    raise ValueError('Could not fit the grill reservations.')

def schedule(tasks,order,goal,now,c):
    grills={r['id']:r for r in resources(c['resources'])};books={k:[] for k in grills};warnings=[]
    for ident in order:
        t=tasks[ident];m=c['tasks'].get(ident,{})
        t.update(resource=m.get('resource',''),slots=m.get('slots',1),pit_f=m.get('pit_f'),started=m.get('started'))
        t['effective_depends']=list(t['depends'])
        t['estimate_elapsed']=bool(t['started'] and now-t['started']>=t['duration'])
        t['remaining']=0 if t['completed'] is not None else max(60,t['duration']-(now-t['started'])) if t['started'] else t['duration']
        t['earliest_start']=max([now]+[tasks[d]['earliest_finish'] for d in t['depends']])
        if t['resource']:
            if t['resource'] not in grills:raise ValueError('A task references a missing grill.')
            grill=grills[t['resource']]
            if t['slots']>grill['capacity']:raise ValueError('Task space exceeds grill capacity.')
            initial=t['earliest_start']
            if not t['completed']:
                t['earliest_start']=fit(initial,t['remaining'],books[t['resource']],t['slots'],grill['capacity'],t['pit_f'])
                if t['earliest_start']>initial:warnings.append(t['name']+' waits for '+grill['name']+' space or a compatible temperature.')
                books[t['resource']].append({'start':t['earliest_start'],'end':t['earliest_start']+t['remaining'],'slots':t['slots'],'pit':t['pit_f']})
        t['earliest_finish']=t['completed'] if t['completed'] is not None else t['earliest_start']+t['remaining']
    earliest=max([now]+[t['earliest_finish'] for t in tasks.values()])
    ends={k:goal if goal is not None else earliest for k in tasks};books={k:[] for k in grills}
    for ident in reversed(order):
        t=tasks[ident];end=ends[ident];start=end-t['remaining']
        if t['completed'] is not None:start=end=t['completed']
        elif t['resource']:
            start=fit(start,t['remaining'],books[t['resource']],t['slots'],grills[t['resource']]['capacity'],t['pit_f'],back=True);end=start+t['remaining']
            books[t['resource']].append({'start':start,'end':end,'slots':t['slots'],'pit':t['pit_f']})
        t['planned_start']=start;t['planned_finish']=end;t['slack_seconds']=start-t['earliest_start']
        t['ready']=all(tasks[d]['completed'] is not None for d in t['depends'])
        for d in t['depends']:ends[d]=min(ends[d],start)
    return {'serve_at':goal,'tasks':[tasks[k] for k in order],'earliest_serve':earliest,'resources':list(grills.values()),'warnings':list(dict.fromkeys(warnings)),'assumption':'User estimates; explicit grill capacity. Temperatures within 25°F may overlap. Unknown temperatures reserve exclusive time. Review actual grill conditions.'}

def action(db,cmd,p,current):
    import workflows
    if cmd=='guided_setup':
        if current:raise ValueError('Finish your active cook before starting a guided meal.')
        name=label(p.get('name'),'Meal name',80);items=p.get('foods')
        if not isinstance(items,list) or not 1<=len(items)<=8:raise ValueError('Add one to eight foods.')
        grills=resources(p.get('resources',[]))
        if not grills:raise ValueError('Add a grill or cooking zone.')
        ident=uuid.uuid4().hex
        db.execute('INSERT INTO cooks(id,name,started,target,source) VALUES(?,?,?,?,?)',(ident,name,time.time(),'19:00','manual'))
        current=db.execute('SELECT * FROM cooks WHERE id=?',(ident,)).fetchone()
        workflows.action(db,'meal_goal',p,current);save(db,ident,{'resources':grills,'tasks':{}})
        for g in grills:
            minutes=number(p.get('preheat',15),0,180,'Preheat duration')
            t=workflows.action(db,'task_add',{'name':'Preheat '+g['name'],'minutes':minutes},current)
            task_meta(db,ident,t,{'resource':g['id'],'slots':g['capacity']})
            g['preheat_task']=t
        for item in items:
            if not isinstance(item,dict):raise ValueError('Invalid food configuration.')
            grill=next((g for g in grills if g['id']==item.get('resource')),None)
            if not grill:raise ValueError('Choose a grill for every food.')
            food=workflows.action(db,'food_add',{**item,'zone':grill['name'],'unit':p.get('unit','F')},current)
            if item.get('device'):workflows.action(db,'food_map',{'id':food,'device':item['device'],'role':'food'},current)
            prep=workflows.action(db,'task_add',{'food':food,'name':'Prep '+item['name'],'minutes':number(item.get('prep',10),0,1440,'Prep duration')},current)
            cook=workflows.action(db,'task_add',{'food':food,'name':'Cook '+item['name'],'minutes':number(item.get('minutes'),1,10080,'Cook duration'),'depends':[prep,grill['preheat_task']]},current)
            pit=number(item.get('pit'),-40,1000,'Pit temperature')
            if p.get('unit')=='C':pit=pit*9/5+32
            task_meta(db,ident,cook,{'resource':grill['id'],'slots':item.get('slots',1),'pit_f':pit})
            rest=workflows.action(db,'task_add',{'food':food,'name':'Rest '+item['name'],'minutes':number(item.get('rest',10),0,1440,'Rest duration'),'depends':[cook]},current)
            hold=number(item.get('hold',0),0,1440,'Hold duration')
            if hold:workflows.action(db,'task_add',{'food':food,'name':'Hold '+item['name']+' (check conditions)','minutes':hold,'depends':[rest]},current)
            if item.get('alarm',True):workflows.action(db,'food_alarm',{'id':food},current)
        return ident
    if not current or current['source']=='demo':raise ValueError('Start a real cook first.')
    ident=current['id'];c=config(db,ident)
    if cmd=='grill_config':
        c['resources']=resources(p.get('resources'));save(db,ident,c);workflows.schedule(db,ident)
    elif cmd=='task_start':
        t=next((t for t in workflows.schedule(db,ident)['tasks'] if t['id']==p.get('id')),None)
        if not t or t['completed']:raise ValueError('Choose an unfinished task.')
        if not t['ready']:raise ValueError('Finish dependency steps before starting this one.')
        if t['started']:raise ValueError('This step is already running.')
        # A physical reservation cannot start while space/temperature conflicts remain.
        if t['resource']:
            running=[]
            for other in workflows.schedule(db,ident)['tasks']:
                if other['id']!=t['id'] and other['resource']==t['resource'] and other['started'] and other['completed'] is None:
                    running.append({'start':0,'end':1,'slots':other['slots'],'pit':other['pit_f']})
            capacity=next(r['capacity'] for r in c['resources'] if r['id']==t['resource'])
            if fit(0,1,running,t['slots'],capacity,t['pit_f'])>0:raise ValueError('Finish the conflicting grill step before starting this one.')
        c['tasks'].setdefault(t['id'],{})['started']=time.time();save(db,ident,c)
    else:raise ValueError('Unknown planner command.')
