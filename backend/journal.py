"""Personal recipes, photos, complete portable backups and CSV export."""
import base64,csv,io,json,re,time,uuid
from html.parser import HTMLParser
from alerts import number
from workflows import label,steps
TABLES=['cooks','readings','events','settings','devices','channels','samples','cook_devices','foods','food_readings','meal_goals','plan_tasks','outcomes','recipes','alarm_rules','alarm_state','alarm_episodes','alarm_notices','delivery_attempts']

def migrate(db):
    db.executescript('CREATE TABLE IF NOT EXISTS recipes(id TEXT PRIMARY KEY,name TEXT NOT NULL,servings REAL NOT NULL,ingredients TEXT NOT NULL,steps TEXT NOT NULL,source TEXT NOT NULL,created REAL NOT NULL);')

def photo(value):
    if value in (None,''):return None
    if not isinstance(value,str) or len(value)>2000000:raise ValueError('Photo must be a JPEG, PNG or WebP under 1.4 MiB.')
    m=re.fullmatch(r'data:image/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)',value)
    if not m:raise ValueError('Photo must be a JPEG, PNG or WebP data image.')
    try:raw=base64.b64decode(m[2],validate=True)
    except ValueError:raise ValueError('Invalid photo encoding.')
    valid=raw.startswith(b'\xff\xd8\xff') if m[1]=='jpeg' else raw.startswith(b'\x89PNG\r\n\x1a\n') if m[1]=='png' else raw[:4]==b'RIFF' and raw[8:12]==b'WEBP'
    if not valid:raise ValueError('Photo bytes do not match its image type.')
    return value

class Scripts(HTMLParser):
    def __init__(self):super().__init__();self.record=False;self.current='';self.values=[]
    def handle_starttag(self,tag,attrs):
        if tag=='script':self.record=dict(attrs).get('type')=='application/ld+json';self.current=''
    def handle_data(self,data):
        if self.record:self.current+=data
    def handle_endtag(self,tag):
        if tag=='script' and self.record:self.values.append(self.current);self.record=False

def recipe_from_text(raw):
    if not isinstance(raw,str) or len(raw)>300000:raise ValueError('Recipe input exceeds 300 KB.')
    try:values=[json.loads(raw)]
    except ValueError:
        parser=Scripts();parser.feed(raw);values=[]
        for value in parser.values:
            try:values.append(json.loads(value))
            except ValueError:pass
    def find(value):
        if isinstance(value,list):
            for v in value:
                result=find(v)
                if result:return result
        elif isinstance(value,dict):
            types=value.get('@type',[]);types=[types] if isinstance(types,str) else types
            if 'Recipe' in types or ('ingredients' in value and 'steps' in value):return value
            return find(value.get('@graph',[]))
    found=find(values)
    if not found:raise ValueError('Paste a Recipe JSON/JSON-LD object or page HTML containing one.')
    ingredients=found.get('recipeIngredient',found.get('ingredients',[]));instructions=found.get('recipeInstructions',found.get('steps',[]))
    def lines(items):
        if isinstance(items,str):return [s.strip() for s in items.splitlines() if s.strip()]
        result=[]
        if not isinstance(items,list):raise ValueError('Invalid recipe steps.')
        for item in items:
            if isinstance(item,str):result.append(item)
            elif isinstance(item,dict):
                if 'itemListElement' in item:result+=lines(item['itemListElement'])
                elif item.get('text'):result.append(item['text'])
        return result
    servings=found.get('servings',found.get('recipeYield',1));servings=servings[0] if isinstance(servings,list) and servings else servings
    match=re.search(r'\d+(?:\.\d+)?',str(servings));servings=float(match[0]) if match else 1
    return {'name':found.get('name'),'servings':servings,'ingredients':ingredients,'steps':lines(instructions),'source':found.get('url','Imported recipe')}

def save_recipe(db,p):
    ingredients=p.get('ingredients',[])
    if isinstance(ingredients,str):ingredients=[s.strip() for s in ingredients.splitlines() if s.strip()]
    if not isinstance(ingredients,list) or not 1<=len(ingredients)<=100:raise ValueError('Add 1–100 ingredient lines.')
    ingredients=[label(s,'Ingredient',300) for s in ingredients]
    instructions=p.get('steps',[])
    if isinstance(instructions,str):instructions=[s.strip() for s in instructions.splitlines() if s.strip()]
    if not isinstance(instructions,list) or not 1<=len(instructions)<=100:raise ValueError('Add 1–100 recipe steps.')
    instructions=[label(s,'Recipe step',2000) for s in instructions]
    ident=p.get('id') or uuid.uuid4().hex
    if p.get('id') and not db.execute('SELECT 1 FROM recipes WHERE id=?',(ident,)).fetchone():raise ValueError('Recipe not found.')
    name=label(p.get('name'),'Recipe name');servings=number(p.get('servings'),.25,1000,'Servings');source=p.get('source','Personal recipe')
    if not isinstance(source,str) or len(source)>1000:raise ValueError('Invalid recipe source.')
    db.execute('INSERT INTO recipes VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,servings=excluded.servings,ingredients=excluded.ingredients,steps=excluded.steps,source=excluded.source',(ident,name,servings,json.dumps(ingredients),json.dumps(instructions),source,time.time()))
    return ident

def action(db,cmd,p):
    if cmd=='recipe_save':return save_recipe(db,p)
    if cmd=='recipe_import':return save_recipe(db,recipe_from_text(p.get('text')))
    if cmd=='recipe_delete':db.execute('DELETE FROM recipes WHERE id=?',(p.get('id'),));return
    if cmd=='cook_review':
        cook=p.get('cook')
        if not db.execute('SELECT 1 FROM cooks WHERE id=?',(cook,)).fetchone():raise ValueError('Cook not found.')
        lesson=p.get('lesson','')
        if not isinstance(lesson,str) or len(lesson)>1000:raise ValueError('Next-time note is limited to 1000 characters.')
        db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',('review:'+cook,json.dumps({'lesson':lesson.strip()})));return
    if cmd=='outcome':
        cook=p.get('cook')
        if not db.execute('SELECT 1 FROM cooks WHERE id=?',(cook,)).fetchone():raise ValueError('Cook not found.')
        rating=number(p.get('rating'),1,5,'Rating')
        if int(rating)!=rating:raise ValueError('Rating must be a whole number.')
        texture=p.get('texture','');taste=p.get('taste','')
        if any(not isinstance(v,str) or len(v)>1000 for v in (texture,taste)):raise ValueError('Outcome notes are limited to 1000 characters.')
        previous=db.execute('SELECT photo FROM outcomes WHERE cook=?',(cook,)).fetchone()
        image=photo(p['photo']) if 'photo' in p else previous[0] if previous else None
        db.execute('INSERT OR REPLACE INTO outcomes VALUES(?,?,?,?,?)',(cook,int(rating),texture,taste,image));return
    raise ValueError('Unknown journal action.')

def snapshot(db):
    return {'recipes':[{**dict(r),'ingredients':json.loads(r['ingredients']),'steps':json.loads(r['steps'])} for r in db.execute('SELECT * FROM recipes ORDER BY created DESC')],
      'outcomes':[{**dict(r),'photo':None,'has_photo':bool(r['photo'])} for r in db.execute('SELECT * FROM outcomes')]}

def export(db):return {'format':'omapit-backup','schema':1,'exported_at':time.time(),'tables':{t:[dict(r) for r in db.execute('SELECT * FROM '+t)] for t in TABLES}}

def restore(db,bundle):
    if db.execute('SELECT 1 FROM cooks LIMIT 1').fetchone() or db.execute('SELECT 1 FROM recipes LIMIT 1').fetchone():raise ValueError('Restore requires an empty journal. Your existing cooks will not be overwritten.')
    if not isinstance(bundle,dict) or bundle.get('format')!='omapit-backup' or bundle.get('schema')!=1:raise ValueError('Unsupported backup format.')
    tables=bundle.get('tables')
    if not isinstance(tables,dict) or set(tables)!=set(TABLES):raise ValueError('Backup table manifest does not match this version.')
    # Validate shape and values before applying. Backups are archival, not live input.
    for table,rows in tables.items():
        columns=[r[1] for r in db.execute('PRAGMA table_info('+table+')')]
        if not isinstance(rows,list) or len(rows)>200000:raise ValueError('Backup exceeds table limits.')
        for row in rows:
            if not isinstance(row,dict) or set(row)!=set(columns):raise ValueError('Backup row shape does not match '+table+'.')
            if any(not isinstance(v,(str,int,float,type(None))) or isinstance(v,float) and not __import__('math').isfinite(v) for v in row.values()):raise ValueError('Invalid backup scalar.')
            if table=='foods':steps(json.loads(row['steps']))
            if table=='outcomes':photo(row['photo'])
            if table=='recipes':
                for key in ('ingredients','steps'):
                    value=json.loads(row[key])
                    if not isinstance(value,list) or any(not isinstance(v,str) for v in value):raise ValueError('Invalid archived recipe.')
    for table in reversed(TABLES):db.execute('DELETE FROM '+table)
    for table,rows in tables.items():
        columns=[r[1] for r in db.execute('PRAGMA table_info('+table+')')]
        for row in rows:db.execute('INSERT INTO '+table+' ('+','.join(columns)+') VALUES('+','.join('?' for _ in columns)+')',[row[c] for c in columns])
    # Pause recovered sessions: importing a backup must never sound old alarms or revive old radios.
    db.execute('UPDATE alarm_rules SET enabled=0');db.execute('DELETE FROM alarm_state')
    db.execute('UPDATE alarm_episodes SET resolved=COALESCE(resolved,?)',(time.time(),))
    db.execute("UPDATE channels SET quality='historical'");db.execute('UPDATE devices SET last_seen=0')
    db.execute('DELETE FROM cook_devices');db.execute('UPDATE foods SET device=NULL')
    db.execute("UPDATE cooks SET source='manual' WHERE finished IS NULL AND source!='demo'")
    db.execute("DELETE FROM settings WHERE key IN ('scanner','service_heartbeat')")
    import planner
    for cook in db.execute('SELECT id FROM cooks'):
        c=planner.config(db,cook[0])
        for ident,task in c['tasks'].items():
            row=db.execute('SELECT completed FROM plan_tasks WHERE id=?',(ident,)).fetchone()
            if row and row[0] is None:task.pop('started',None)
        planner.save(db,cook[0],c)
        __import__('workflows').schedule(db,cook[0])
    db.execute("INSERT OR IGNORE INTO settings VALUES('unit','F')")

def csv_export(db,cook):
    out=io.StringIO();w=csv.writer(out);w.writerow(['timestamp_utc','food','temperature_F','pit_F','source'])
    def safe(v):return "'"+v if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r','\n')) else v
    from datetime import datetime,timezone
    for r in db.execute('SELECT * FROM readings WHERE cook=? ORDER BY at',(cook,)):
        w.writerow([datetime.fromtimestamp(r['at'],timezone.utc).isoformat(),'Cook food',r['meat'],r['pit'],safe(r['source'])])
    for r in db.execute('SELECT r.*,f.name FROM food_readings r JOIN foods f ON f.id=r.food WHERE f.cook=? ORDER BY r.at',(cook,)):
        w.writerow([datetime.fromtimestamp(r['at'],timezone.utc).isoformat(),safe(r['name']),r['value_f'],'',safe(r['source'])])
    return out.getvalue()
