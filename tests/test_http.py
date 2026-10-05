"""Local HTTP acceptance: auth/origin guards and alarms without an open browser."""
import json,os,pathlib,socket,subprocess,sys,tempfile,time,unittest,urllib.request,urllib.error
ROOT=pathlib.Path(__file__).parents[1]
class HTTP(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();sock=socket.socket();sock.bind(('127.0.0.1',0));cls.port=sock.getsockname()[1];sock.close()
  cls.token='local-acceptance-token-'+'x'*32
  cls.proc=subprocess.Popen([sys.executable,str(ROOT/'backend/omapit.py'),'--db',str(pathlib.Path(cls.tmp.name)/'http.db'),'--static',str(ROOT/'preview/dist/client'),'--serve',str(cls.port)],env={**os.environ,'OMAPIT_TOKEN':cls.token,'OMAPIT_NTFY_URL':'','OMAPIT_DESKTOP_NOTIFY':'0'},stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  for _ in range(100):
   try:cls.request('/api/state');return
   except (OSError,urllib.error.URLError):time.sleep(.05)
  raise RuntimeError('Test service did not start')
 @classmethod
 def tearDownClass(cls):cls.proc.terminate();cls.proc.wait(timeout=5);cls.proc.stderr.close();cls.tmp.cleanup()
 @classmethod
 def request(cls,path,p=None,token=True,origin=None,host=None):
  headers={}
  if token:headers['Authorization']='Bearer '+cls.token
  if p is not None:headers.update({'Origin':origin or f'http://127.0.0.1:{cls.port}','Content-Type':'application/json'})
  if host:headers['Host']=host
  req=urllib.request.Request(f'http://127.0.0.1:{cls.port}'+path,data=json.dumps(p).encode() if p is not None else None,headers=headers)
  try:
   with urllib.request.urlopen(req,timeout=5) as r:return r.status,json.loads(r.read())
  except urllib.error.HTTPError as e:
   try:return e.code,json.loads(e.read())
   finally:e.close()
 def test_monitor_heartbeat_is_committed(self):
  for _ in range(20):
   health=self.request('/api/state')[1]['service_health']
   if health['monitor_fresh']:break
   time.sleep(.1)
  self.assertTrue(health['monitor_fresh']);self.assertEqual(health['mode'],'companion')
 def test_auth_and_host_guards(self):
  self.assertEqual(self.request('/api/state',token=False)[0],401)
  self.assertEqual(self.request('/api/state',host='attacker.example')[0],403)
  self.assertEqual(self.request('/api/state')[0],200)
 def test_cross_origin_rejected(self):self.assertEqual(self.request('/api/unit',{'unit':'C'},origin='https://attacker.example')[0],403)
 def test_timer_evaluates_without_browser_polling(self):
  code,d=self.request('/api/create',{'name':'HTTP test cook','target':'19:00'});self.assertEqual(code,200)
  self.assertEqual(self.request('/api/alarm_add',{'kind':'timer','label':'Server timer','seconds':1})[0],200)
  # Do not poll state: inspect the independent service's database after its timer.
  time.sleep(2.2)
  import sqlite3
  db=sqlite3.connect(pathlib.Path(self.tmp.name)/'http.db')
  try:self.assertEqual(db.execute('SELECT COUNT(*) FROM alarm_notices').fetchone()[0],1)
  finally:db.close()
 def test_invalid_bridge_request_is_atomic(self):
  code,d=self.request('/api/bridge_ingest',{'schema':1,'source':'json','device':'test','sample_at':time.time(),'channels':{'food':{'value':10,'unit':'X'}}})
  self.assertEqual(code,400);self.assertEqual(self.request('/api/state')[1]['devices'],[])
if __name__=='__main__':unittest.main()
