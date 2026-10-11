"""Alarm delivery to a real local ntfy server over HTTPS with token auth.

Skipped unless an ntfy server binary is available (NTFY_BIN, or `ntfy` on
PATH) together with openssl. CI builds ntfy from source in the ntfy job.
"""
import json,os,pathlib,shutil,socket,ssl,subprocess,sys,tempfile,time,unittest,urllib.request
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'backend'))
import omapit as store
import alerts,delivery
from tls_fixture import make_certificates
NTFY=shutil.which(os.environ.get('NTFY_BIN','ntfy'))
TOPIC='omapit-alarms'

def free_port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]

@unittest.skipUnless(NTFY and shutil.which('openssl'),'needs an ntfy server binary and openssl')
class NtfyDeliveryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();d=cls.dir=pathlib.Path(cls.tmp.name);cls.port=free_port()
  run=lambda *a,**kw:subprocess.run(a,cwd=d,check=True,capture_output=True,text=True,**kw)
  make_certificates(d)
  cls.base=f'https://localhost:{cls.port}'
  (d/'server.yml').write_text('\n'.join([f'base-url: "{cls.base}"','listen-http: "-"',f'listen-https: "127.0.0.1:{cls.port}"',
   f'cert-file: "{d/"server.pem"}"',f'key-file: "{d/"server.key"}"',f'auth-file: "{d/"user.db"}"','auth-default-access: "deny-all"',f'cache-file: "{d/"cache.db"}"'])+'\n')
  cls.server=subprocess.Popen([NTFY,'serve','--config',str(d/'server.yml')],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
  for _ in range(100):
   try:socket.create_connection(('127.0.0.1',cls.port),0.2).close();break
   except OSError:time.sleep(0.1)
  else:raise RuntimeError('ntfy did not start: '+cls.server.stderr.read())
  # The server creates its user database on first start.
  ntfy=lambda *a:run(NTFY,*a[:1],'--config',str(d/'server.yml'),*a[1:],env={**os.environ,'NTFY_PASSWORD':'test-pass-123'})
  ntfy('user','add','omapit');ntfy('access','omapit',TOPIC,'rw')
  out=ntfy('token','add','omapit');cls.token=next(w for w in (out.stdout+out.stderr).split() if w.startswith('tk_'))
 @classmethod
 def tearDownClass(cls):
  cls.server.terminate();cls.server.wait(5);cls.server.stderr.close();cls.tmp.cleanup()
 def setUp(self):
  self.dbdir=tempfile.TemporaryDirectory();self.db=store.database(pathlib.Path(self.dbdir.name)/'cooks.sqlite3')
 def tearDown(self):self.db.close();self.dbdir.cleanup()

 def fire(self,label):
  store.dispatch(self.db,'create',{'name':'Dinner','target':'19:00'});store.dispatch(self.db,'alarm_add',{'label':label,'kind':'timer','seconds':1})
  with self.db:alerts.evaluate(self.db,time.time()+2)
 def deliver(self,**env):
  config={'OMAPIT_NTFY_URL':f'{self.base}/{TOPIC}','OMAPIT_NTFY_TOKEN':self.token,'SSL_CERT_FILE':str(self.dir/'ca.pem'),**env}
  with patch.dict(os.environ,{k:v for k,v in config.items() if v is not None},clear=True):delivery.deliver(self.db,time.time()+2)
  return [dict(r) for r in self.db.execute('SELECT status,attempts,error FROM delivery_attempts')]
 def received(self,label):
  context=ssl.create_default_context(cafile=str(self.dir/'ca.pem'))
  req=urllib.request.Request(f'{self.base}/{TOPIC}/json?poll=1&since=all',headers={'Authorization':'Bearer '+self.token})
  with urllib.request.urlopen(req,context=context,timeout=5) as r:
   messages=[json.loads(l) for l in r.read().decode().splitlines() if l.strip()]
  return [m for m in messages if m.get('event')=='message' and m.get('message')==label]

 def test_alarm_delivered_once_with_title_and_priority(self):
  self.fire('Brisket timer done')
  self.assertEqual(self.deliver(),[{'status':'sent','attempts':1,'error':None}])
  self.deliver()  # a second pass must not resend
  got=self.received('Brisket timer done');self.assertEqual(len(got),1)
  self.assertEqual((got[0]['title'],got[0]['priority']),('OmaPit alarm',4))
 def test_wrong_token_is_refused_and_recorded(self):
  self.fire('Wrong token alarm')
  self.assertEqual(self.deliver(OMAPIT_NTFY_TOKEN='tk_notarealtoken0000000000000000')[0]['status'],'failed')
  self.assertEqual(self.received('Wrong token alarm'),[])
 def test_missing_token_is_refused(self):
  self.fire('No token alarm')
  self.assertEqual(self.deliver(OMAPIT_NTFY_TOKEN=None)[0]['status'],'failed')
  self.assertEqual(self.received('No token alarm'),[])
 def test_untrusted_certificate_is_refused(self):
  self.fire('Untrusted alarm')
  self.assertEqual(self.deliver(SSL_CERT_FILE=str(self.dir/'server.key'))[0]['status'],'failed')
  self.assertEqual(self.received('Untrusted alarm'),[])
 def test_plain_http_url_is_refused_before_sending(self):
  self.fire('HTTP alarm')
  self.assertEqual(self.deliver(OMAPIT_NTFY_URL=f'http://localhost:{self.port}/{TOPIC}')[0]['status'],'failed')
  self.assertEqual(self.received('HTTP alarm'),[])

if __name__=='__main__':unittest.main()
