#!/usr/bin/env python3
"""Local cook journal shared by the QML plugin and its development preview."""
import argparse, json, math, os, sqlite3, sys, time, uuid
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0,str(Path(__file__).resolve().parent))
import devices
import alerts
import workflows
import bridges
import delivery
import journal
import prediction
import planner

STAGES = ['Smoke', 'Wrap', 'Rest', 'Serve']

def store_path(path=None):
    return Path(path or os.environ.get('OMAPIT_DB', Path(os.environ.get('XDG_DATA_HOME', Path.home()/'.local/share'))/'omapit/cooks.sqlite3'))

def database(path=None):
    path = store_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    db.executescript('''CREATE TABLE IF NOT EXISTS cooks(id TEXT PRIMARY KEY, name TEXT NOT NULL, started REAL NOT NULL, target TEXT NOT NULL, stage INTEGER NOT NULL DEFAULT 0, source TEXT NOT NULL, finished REAL, bark INTEGER NOT NULL DEFAULT 0, dry INTEGER NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS readings(id INTEGER PRIMARY KEY, cook TEXT NOT NULL, at REAL NOT NULL, meat REAL NOT NULL, pit REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, cook TEXT NOT NULL, at REAL NOT NULL, kind TEXT NOT NULL, note TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    INSERT OR IGNORE INTO settings VALUES('unit','F');''')
    db.commit()
    devices.migrate(db)
    feature=db.execute("SELECT value FROM settings WHERE key='workbench_schema'").fetchone()
    if feature and feature[0]!='1':raise ValueError('This workbench schema needs a newer OmaPit build.')
    if not feature:
        backup=Path(str(path)+'.before-workbench-v1.bak')
        if not backup.exists():
            target=sqlite3.connect(backup)
            db.backup(target);target.close()
    alerts.migrate(db)
    workflows.migrate(db)
    delivery.migrate(db)
    journal.migrate(db)
    db.execute("INSERT OR IGNORE INTO settings VALUES('workbench_schema','1')");db.commit()
    return db

def event(db, cook, kind, note):
    db.execute('INSERT INTO events VALUES(?,?,?,?,?)', (uuid.uuid4().hex, cook, time.time(), kind, note))

def seed_demo(db):
    now = time.time(); ident = uuid.uuid4().hex
    db.execute('INSERT INTO cooks(id,name,started,target,source) VALUES(?,?,?,?,?)', (ident,'Saturday brisket', now-23220,'19:00','demo'))
    for n in range(91):
        minutes = n * 4.3
        meat = min(164, 45 + minutes * .39) + math.sin(n*.8)*.7
        db.execute('INSERT INTO readings(cook,at,meat,pit,source) VALUES(?,?,?,?,?)',(ident,now-23220+n*258,round(meat,1),round(248+math.sin(n*.65)*2,1),'demo'))
    db.execute('INSERT INTO events VALUES(?,?,?,?,?)',(uuid.uuid4().hex,ident,now-2820,'note','Stall observed — check the bark before wrapping.'))
    db.execute('INSERT INTO events VALUES(?,?,?,?,?)',(uuid.uuid4().hex,ident,now-8520,'fuel','Fuel added'))
    return ident

def state(db):
    cooks = [dict(x) for x in db.execute('SELECT * FROM cooks ORDER BY started DESC')]
    active = next((x for x in cooks if x['finished'] is None),None)
    meal=workflows.snapshot(db,active)
    heartbeat=db.execute("SELECT value FROM settings WHERE key='service_heartbeat'").fetchone()
    health=json.loads(heartbeat[0]) if heartbeat else {}
    return {'service_health':{**health,'monitor_fresh':bool(health.get('at') and 0<=time.time()-health['at']<=5)},'predictions':prediction.snapshot(db,meal['foods']),**journal.snapshot(db),**delivery.snapshot(db),**meal,**alerts.snapshot(db),**devices.snapshot(db),'cooks':cooks,'active':active,'unit':db.execute("SELECT value FROM settings WHERE key='unit'").fetchone()[0], 'readings': [dict(x) for x in db.execute('SELECT at,meat,pit,source,device FROM readings WHERE cook=? ORDER BY at',(active['id'],))] if active else [], 'events':[dict(x) for x in db.execute('SELECT * FROM events WHERE cook=? ORDER BY at DESC',(active['id'],))] if active else []}

def text(value, label, maxlen=500):
    if not isinstance(value,str) or not value.strip() or len(value)>maxlen: raise ValueError(f'{label} is required (up to {maxlen} characters).')
    return value.strip()

def dispatch(db, command, payload):
    with db:
        db.execute('BEGIN IMMEDIATE')
        current = state(db)['active']
        if command == 'snapshot':
            workflows.record_channels(db)
            alerts.evaluate(db)
            return state(db)
        if command=='evaluate':return prediction.journal_evaluation(db)
        if command=='backup':return journal.export(db)
        if command=='csv':return {'csv':journal.csv_export(db,payload.get('id'))}
        if command=='restore':journal.restore(db,payload)
        elif command.startswith('recipe_') or command in ('outcome','cook_review'):journal.action(db,command,payload)
        elif command=='bridge_ingest':
            bridges.ingest(db,payload)
            workflows.record_channels(db)
        elif command in ('guided_setup','grill_config','task_start'):
            step=db.execute('SELECT name FROM plan_tasks WHERE id=?',(payload.get('id'),)).fetchone() if command=='task_start' else None
            ident=planner.action(db,command,payload,current)
            event(db,ident if command=='guided_setup' else current['id'],'workflow',('Started '+step[0]) if step else ('Meal plan created · '+payload['name']) if command=='guided_setup' else 'Grill configuration updated')
        elif command.startswith('food_') or command.startswith('task_') or command=='meal_goal':
            named=db.execute('SELECT name FROM '+('foods' if command.startswith('food_') else 'plan_tasks')+' WHERE id=?',(payload.get('id'),)).fetchone() if command!='meal_goal' else None
            result=workflows.action(db,command,payload,current)
            if current:
                detail=payload.get('name') or (named[0] if named else 'Meal serving goal')
                event(db,current['id'],'workflow',command.replace('_',' ')+' · '+str(detail)[:120])
        elif command == 'alarm_add':
            if not current or current['source']=='demo':raise ValueError('Start a real cook for alarms.')
            alerts.add(db,current,payload)
        elif command in ('alarm_ack','alarm_snooze','alarm_rule'):
            alerts.action(db,command,payload)
        elif command == 'scan':
            dbpath=db.execute('PRAGMA database_list').fetchone()[2]
            devices.start_scan(db,dbpath)
        elif command == 'select_device':
            devices.select(db,payload.get('id'),current)
            event(db,current['id'],'device','CHEF iQ probe selected for automatic readings')
        elif command == 'manual_mode':
            if not current or current['source']=='demo':raise ValueError('Start a real cook first.')
            db.execute('DELETE FROM cook_devices WHERE cook=?',(current['id'],))
            db.execute("UPDATE cooks SET source='manual' WHERE id=?",(current['id'],))
            event(db,current['id'],'device','Manual readings selected')
        elif command == 'unit':
            if payload.get('unit') not in ['C','F']: raise ValueError('Choose C or F.')
            db.execute("UPDATE settings SET value=? WHERE key='unit'", (payload['unit'],))
        elif command in ['create','demo']:
            if current: raise ValueError('Finish the current cook before starting another.')
            if command == 'demo': seed_demo(db)
            else:
                name=text(payload.get('name'),'Cook name',80);target=payload.get('target','19:00')
                import re
                if not isinstance(target,str) or not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d',target): raise ValueError('Use a valid serving time.')
                db.execute('INSERT INTO cooks(id,name,started,target,source) VALUES(?,?,?,?,?)',(uuid.uuid4().hex,name,time.time(),target,'manual'))
        elif command == 'history':
            ident=payload.get('id');cook=db.execute('SELECT * FROM cooks WHERE id=?',(ident,)).fetchone()
            if not cook: raise ValueError('Cook not found.')
            review=db.execute('SELECT value FROM settings WHERE key=?',('review:'+ident,)).fetchone()
            return {'review':json.loads(review[0]) if review else {},'cook':dict(cook),'readings':[dict(x) for x in db.execute('SELECT at,meat,pit,source,device FROM readings WHERE cook=? ORDER BY at',(ident,))], 'events':[dict(x) for x in db.execute('SELECT * FROM events WHERE cook=? ORDER BY at DESC',(ident,))], 'outcome':dict(db.execute('SELECT * FROM outcomes WHERE cook=?',(ident,)).fetchone() or {}),'foods':[{**workflows.food_data(db,f,time.time()),'readings':[dict(r) for r in db.execute('SELECT * FROM food_readings WHERE food=? ORDER BY at',(f['id'],))]} for f in db.execute('SELECT * FROM foods WHERE cook=?',(ident,))], 'plan':workflows.schedule(db,ident), 'samples':[dict(x) for x in db.execute('SELECT * FROM samples WHERE cook=? ORDER BY at',(ident,))]}
        else:
            if not current: raise ValueError('Start a cook first.')
            ident=current['id']
            if command == 'note': event(db,ident,'note',text(payload.get('note'),'Note'))
            elif command == 'fuel': event(db,ident,'fuel','Fuel added')
            elif command == 'check':
                key=payload.get('key')
                if key not in ['bark','dry'] or not isinstance(payload.get('value'),bool):raise ValueError('Invalid checklist update.')
                db.execute(f'UPDATE cooks SET {key}=? WHERE id=?',(int(payload['value']),ident))
            elif command == 'advance':
                expected=payload.get('expected_stage')
                if expected != current['stage']:raise ValueError('The cook changed. Refresh and try again.')
                if current['stage'] == 0 and not (current['bark'] and current['dry']):raise ValueError('Check the bark and surface before logging the wrap.')
                if current['stage'] >= 3:raise ValueError('This cook is already at Serve.')
                stage=current['stage']+1
                db.execute('UPDATE cooks SET stage=? WHERE id=?',(stage,ident));event(db,ident,'stage',STAGES[stage]+' started')
            elif command == 'finish':
                db.execute('UPDATE cooks SET finished=? WHERE id=?',(time.time(),ident));event(db,ident,'finish','Cook finished')
            elif command == 'reading':
                if current['source']!='manual':raise ValueError('Select manual mode before logging manual temperatures.')
                vals=[]
                unit=payload.get('unit')
                if unit not in ['C','F']:raise ValueError('Choose a temperature unit.')
                for key in ['meat','pit']:
                    try:v=float(payload[key])
                    except (ValueError,TypeError,KeyError):raise ValueError('Enter both temperatures.')
                    if unit=='C':v=v*9/5+32
                    if not math.isfinite(v) or not -40<=v<=1000:raise ValueError('Temperature must be between -40°F and 1000°F.')
                    vals.append(v)
                db.execute('INSERT INTO readings(cook,at,meat,pit) VALUES(?,?,?,?)',(ident,time.time(),*vals))
            else:raise ValueError('Unknown action.')
    with db: alerts.evaluate(db)
    return state(db)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--db');parser.add_argument('--payload-file',help='Read a JSON payload from a local file instead of command-line text');parser.add_argument('--monitor',action='store_true',help='Run persistent alarm monitoring without HTTP');parser.add_argument('--listen',default='127.0.0.1');parser.add_argument('--public-origin',help='Exact HTTPS origin of an optional private reverse proxy');parser.add_argument('--public-host',help='Exact LAN hostname/IP for phone access');parser.add_argument('--static',help='Serve a built browser preview directory');parser.add_argument('--serve',type=int);parser.add_argument('--seed-demo',action='store_true');parser.add_argument('command',nargs='?',default='snapshot');parser.add_argument('payload',nargs='?',default='{}');args=parser.parse_args()
    if args.command=='diagnose':
        # Before database(): diagnostics must never migrate or create the store.
        import diagnose
        sys.exit(diagnose.main(['--db',args.db] if args.db else []))
    db=database(args.db)
    if args.seed_demo and not db.execute('SELECT 1 FROM cooks LIMIT 1').fetchone():
        with db: seed_demo(db)
    db.close()
    import threading
    def deliver_notifications():
        while True:
            if delivery.transports():
                connection=database(args.db)
                try:delivery.deliver(connection)
                except Exception:print('Notification worker failed; check local configuration.',file=sys.stderr)
                finally:connection.close()
            time.sleep(1)
    if args.monitor:
        threading.Thread(target=deliver_notifications,daemon=True).start()
        while True:
            connection=database(args.db)
            try:
                with connection:
                    connection.execute('BEGIN IMMEDIATE')
                    workflows.record_channels(connection)
                    alerts.evaluate(connection)
                    connection.execute("INSERT OR REPLACE INTO settings VALUES('service_heartbeat',?)",(json.dumps({'at':time.time(),'pid':os.getpid(),'mode':'monitor' if args.monitor else 'companion'}),))
            except Exception as error:print('Monitor error: '+str(error),file=sys.stderr)
            finally:connection.close()
            time.sleep(1)
    elif args.serve:
        import threading,hmac
        token=os.environ.get('OMAPIT_TOKEN','')
        remote=args.listen not in ('127.0.0.1','localhost')
        if remote and (len(token)<32 or not args.public_host):parser.error('LAN access needs OMAPIT_TOKEN (32+ characters) and --public-host.')
        hosts={f'127.0.0.1:{args.serve}',f'localhost:{args.serve}'}
        origins={f'http://{host}' for host in hosts}|{'http://127.0.0.1:4173','http://localhost:4173'}
        if args.public_host:
            hosts.add(f'{args.public_host}:{args.serve}');origins.add(f'http://{args.public_host}:{args.serve}')
        if args.public_origin:
            from urllib.parse import urlparse
            origin=urlparse(args.public_origin)
            if origin.scheme!='https' or not origin.hostname or origin.username or origin.path not in ('','/') or origin.query or origin.fragment or len(token)<32:parser.error('Private proxy needs an exact HTTPS origin and a 32+ character OMAPIT_TOKEN.')
            hosts.add(origin.netloc);origins.add('https://'+origin.netloc)
        def monitor():
            while True:
                connection=database(args.db)
                try:
                    with connection:
                        connection.execute('BEGIN IMMEDIATE')
                        workflows.record_channels(connection)
                        alerts.evaluate(connection)
                        connection.execute("INSERT OR REPLACE INTO settings VALUES('service_heartbeat',?)",(json.dumps({'at':time.time(),'pid':os.getpid(),'mode':'monitor' if args.monitor else 'companion'}),))
                except Exception as error: print('Alarm monitor error: '+str(error),file=sys.stderr)
                finally: connection.close()
                time.sleep(1)
        threading.Thread(target=monitor,daemon=True).start()
        threading.Thread(target=deliver_notifications,daemon=True).start()
        class Handler(SimpleHTTPRequestHandler):
            def __init__(self,*a,**kw):super().__init__(*a,directory=args.static,**kw)
            def valid_host(self):return self.headers.get('Host') in hosts
            def authenticated(self):return not token or hmac.compare_digest(self.headers.get('Authorization',''),'Bearer '+token)
            def do_GET(self):
                if not self.valid_host():return self.respond(403,{'error':'Host rejected'})
                if self.path != '/api/state':
                    if args.static and not self.path.startswith('/api/'):return super().do_GET()
                    return self.respond(404,{'error':'Not found'})
                if not self.authenticated():return self.respond(401,{'error':'Enter your companion access token.'})
                self.handle_command('snapshot',{})
            def do_POST(self):
                if not self.valid_host():return self.respond(403,{'error':'Host rejected'})
                if not self.authenticated():return self.respond(401,{'error':'Enter your companion access token.'})
                # Same-origin Vite proxy preserves Origin. No remote origins or wildcard CORS.
                if self.headers.get('Origin') not in origins:
                    return self.respond(403,{'error':'Origin rejected'})
                try:
                    length=int(self.headers.get('Content-Length','0'))
                    if length<1 or length>16*1024*1024:raise ValueError('Invalid request size')
                    payload=json.loads(self.rfile.read(length))
                    if not isinstance(payload,dict):raise ValueError('Object expected')
                except (ValueError,json.JSONDecodeError):return self.respond(400,{'error':'Invalid request'})
                if not self.path.startswith('/api/'):return self.respond(404,{'error':'Not found'})
                self.handle_command(self.path[5:],payload)
            def handle_command(self,action,payload):
                db=database(args.db)
                try:self.respond(200,dispatch(db,action,payload))
                except ValueError as e:self.respond(400,{'error':str(e)})
                except Exception:self.respond(500,{'error':'Local storage could not be accessed.'})
                finally:db.close()
            def respond(self,status,data):
                body=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
            def log_message(self,*args):pass
        print(f'OmaPit API on {args.listen}:{args.serve}',flush=True)
        ThreadingHTTPServer((args.listen,args.serve),Handler).serve_forever()
    else:
        db=database(args.db)
        try: print(json.dumps(dispatch(db,args.command,json.loads(Path(args.payload_file).read_text() if args.payload_file else args.payload))))
        except (ValueError,json.JSONDecodeError) as e:print(json.dumps({'error':str(e)}));sys.exit(1)
        finally:db.close()
if __name__=='__main__':main()
