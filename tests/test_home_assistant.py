"""Home Assistant bridge against a real local Home Assistant Core instance.

Skipped unless HA_PYTHON names a Python interpreter with the homeassistant
package (and its pinned frontend) installed. CI installs it in the
home-assistant job. Entity states are written through Home Assistant's REST
API, as an integration would; no real thermometer integration is involved.
"""
import json,os,pathlib,queue,socket,sqlite3,subprocess,sys,tempfile,threading,time,unittest,urllib.parse,urllib.request
BRIDGE=pathlib.Path(__file__).parents[1]/'backend'/'bridges.py'
HA_PYTHON=os.environ.get('HA_PYTHON')

def free_port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]

def post(url,data,headers=None,form=False):
 body=urllib.parse.urlencode(data).encode() if form else json.dumps(data).encode()
 req=urllib.request.Request(url,data=body,headers={'Content-Type':'application/x-www-form-urlencoded' if form else 'application/json',**(headers or {})},method='POST')
 with urllib.request.urlopen(req,timeout=10) as r:return json.loads(r.read())

@unittest.skipUnless(HA_PYTHON and pathlib.Path(HA_PYTHON).is_file(),'set HA_PYTHON to a Python with homeassistant installed')
class HomeAssistantTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();config=pathlib.Path(cls.tmp.name)/'ha';config.mkdir();cls.port=free_port();cls.url=f'http://127.0.0.1:{cls.port}'
  (config/'configuration.yaml').write_text(f'''homeassistant:
  name: OmaPit test
  unit_system: metric
  time_zone: UTC
  latitude: 0
  longitude: 0
  elevation: 0
  auth_providers:
    - type: homeassistant
http:
  server_host: 127.0.0.1
  server_port: {cls.port}
api:
auth:
''')
  subprocess.run([HA_PYTHON,'-m','homeassistant','--script','auth','-c',str(config),'add','omapit','test-pass-123'],check=True,capture_output=True)
  cls.ha=subprocess.Popen([HA_PYTHON,'-m','homeassistant','-c',str(config),'--skip-pip'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for _ in range(180):
   try:urllib.request.urlopen(cls.url+'/api/',timeout=2)
   except urllib.error.HTTPError as e:
    if e.code==401:break
   except OSError:pass
   time.sleep(1)
  else:raise RuntimeError('Home Assistant did not start')
  client=cls.url+'/'
  flow=post(cls.url+'/auth/login_flow',{'client_id':client,'handler':['homeassistant',None],'redirect_uri':client})
  code=post(f"{cls.url}/auth/login_flow/{flow['flow_id']}",{'client_id':client,'username':'omapit','password':'test-pass-123'})['result']
  cls.token=post(cls.url+'/auth/token',{'grant_type':'authorization_code','code':code,'client_id':client},form=True)['access_token']
 @classmethod
 def tearDownClass(cls):
  cls.ha.terminate();cls.ha.wait(30);cls.tmp.cleanup()
 def setUp(self):
  self.dir=tempfile.TemporaryDirectory();self.db=pathlib.Path(self.dir.name)/'cooks.sqlite3';self.procs=[]
 def tearDown(self):
  for p in self.procs:
   if p.poll() is None:p.terminate();p.wait(5)
   p.stdout.close();p.stderr.close()
  self.dir.cleanup()

 def set_state(self,entity,state,unit='°F'):
  post(f'{self.url}/api/states/{entity}',{'state':state,'attributes':{'unit_of_measurement':unit,'friendly_name':'Test probe','device_class':'temperature'}},{'Authorization':'Bearer '+self.token})
 def bridge(self,entity,token=None,url=None):
  env={**os.environ,'OMAPIT_HA_TOKEN':self.token if token is None else token}
  p=subprocess.Popen([sys.executable,str(BRIDGE),'--db',str(self.db),'ha','--url',url or self.url,'--entity',entity,'--role','food','--interval','5'],
   stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env);self.procs.append(p)
  lines=queue.Queue();threading.Thread(target=lambda:[lines.put(json.loads(l)) for l in p.stdout],daemon=True).start()
  return lines
 def channel(self,entity):
  db=sqlite3.connect(self.db)
  try:return db.execute('SELECT value,unit,quality FROM channels WHERE device=?',('bridge:home-assistant:'+entity,)).fetchone()
  except sqlite3.OperationalError:return None
  finally:db.close()

 def test_live_and_updated_readings(self):
  self.set_state('sensor.live_probe','165.2')
  lines=self.bridge('sensor.live_probe')
  self.assertTrue(lines.get(timeout=15)['accepted'])
  value,unit,quality=self.channel('sensor.live_probe');self.assertAlmostEqual(value,74.0,1);self.assertEqual((unit,quality),('C','valid'))
  self.assertFalse(lines.get(timeout=15)['accepted'])  # unchanged state is not recorded twice
  self.set_state('sensor.live_probe','68.5','°C')
  for _ in range(3):
   if lines.get(timeout=15).get('accepted'):break
  self.assertEqual(self.channel('sensor.live_probe')[0],68.5)
 def test_unavailable_sensor_clears_reading(self):
  self.set_state('sensor.flaky_probe','unavailable')
  self.assertTrue(self.bridge('sensor.flaky_probe').get(timeout=15)['accepted'])
  value,_,quality=self.channel('sensor.flaky_probe');self.assertIsNone(value);self.assertEqual(quality,'invalid')
 def test_stale_entity_is_not_live(self):
  self.set_state('sensor.old_probe','150')
  time.sleep(32)  # Home Assistant stamps states with the current time; let this one age past 30 s.
  self.assertIn('error',self.bridge('sensor.old_probe').get(timeout=15));self.assertIsNone(self.channel('sensor.old_probe'))
 def test_wrong_token_records_nothing(self):
  self.set_state('sensor.private_probe','150')
  self.assertIn('error',self.bridge('sensor.private_probe',token='not-a-real-token').get(timeout=15))
  self.assertIsNone(self.channel('sensor.private_probe'))
 def test_unsafe_configuration_refused(self):
  for env,url,message in [({'OMAPIT_HA_TOKEN':''},self.url,'OMAPIT_HA_TOKEN'),({'OMAPIT_HA_TOKEN':'x'},f'http://user:pass@127.0.0.1:{self.port}','credentials')]:
   run=subprocess.run([sys.executable,str(BRIDGE),'--db',str(self.db),'ha','--url',url,'--entity','sensor.x'],capture_output=True,text=True,env={**os.environ,**env},timeout=20)
   self.assertEqual(run.returncode,2);self.assertIn(message,run.stderr)

if __name__=='__main__':unittest.main()
