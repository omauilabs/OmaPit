"""Opt-in notification transports; isolated from temperature evaluation."""
from http_util import open_request
import os,time,subprocess,urllib.request

def migrate(db):
    db.executescript('CREATE TABLE IF NOT EXISTS delivery_attempts(notice INTEGER,transport TEXT,attempts INTEGER NOT NULL,last_at REAL NOT NULL,status TEXT NOT NULL,error TEXT,PRIMARY KEY(notice,transport));')

def transports():
    result=[]
    if os.environ.get('OMAPIT_DESKTOP_NOTIFY')=='1':result.append('desktop')
    if os.environ.get('OMAPIT_NTFY_URL'):result.append('ntfy')
    return result

def deliver(db,now=None):
    now=time.time() if now is None else now
    for transport in transports():
        notices=db.execute('''SELECT n.*,e.label,e.resolved,e.acknowledged,e.snoozed_until FROM alarm_notices n JOIN alarm_episodes e ON e.id=n.episode WHERE n.at>? ORDER BY n.id''',(now-60,)).fetchall()
        for n in notices:
            if n['resolved'] or n['acknowledged'] or n['snoozed_until']>now:continue
            with db:
                db.execute('BEGIN IMMEDIATE')
                a=db.execute('SELECT * FROM delivery_attempts WHERE notice=? AND transport=?',(n['id'],transport)).fetchone()
                if a and (a['status'] in ('sent','sending') or a['attempts']>=3 or now-a['last_at']<10):continue
                episode=db.execute('SELECT * FROM alarm_episodes WHERE id=?',(n['episode'],)).fetchone()
                if episode['resolved'] or episode['acknowledged'] or episode['snoozed_until']>now:continue
                attempts=a['attempts']+1 if a else 1
                db.execute('INSERT OR REPLACE INTO delivery_attempts VALUES(?,?,?,?,?,?)',(n['id'],transport,attempts,now,'sending',None))
            try:
                if transport=='desktop':subprocess.run(['notify-send','--app-name=OmaPit','--urgency=critical','--','OmaPit alarm',n['label']],timeout=5,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                else:
                    from urllib.parse import urlparse
                    url=os.environ['OMAPIT_NTFY_URL'];parts=urlparse(url)
                    if parts.scheme!='https' or not parts.hostname or parts.username or not parts.path.strip('/'):raise ValueError('Use an HTTPS topic URL without embedded credentials.')
                    headers={'Title':'OmaPit alarm','Priority':'high','Content-Type':'text/plain; charset=utf-8'}
                    token=os.environ.get('OMAPIT_NTFY_TOKEN')
                    if token:headers['Authorization']='Bearer '+token
                    req=urllib.request.Request(url,data=n['label'].encode(),headers=headers,method='POST')
                    with open_request(req,timeout=5) as response:
                        if not 200<=response.status<300:raise ValueError('Notification rejected.')
                status,error='sent',None
            except Exception:status,error='failed','Delivery failed; check transport configuration and permissions.'
            with db:db.execute('UPDATE delivery_attempts SET status=?,error=? WHERE notice=? AND transport=?',(status,error,n['id'],transport))

def snapshot(db):
    return {'notification_transports':transports(),'delivery_attempts':[dict(r) for r in db.execute('SELECT * FROM delivery_attempts ORDER BY last_at DESC LIMIT 30')]}
