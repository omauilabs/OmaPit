"""MQTT bridge against a real local Mosquitto broker.

Skipped unless the `mosquitto` binary and the optional paho-mqtt package
(backend/requirements-bridge.txt) are installed. CI runs it in the mqtt job.
"""
import importlib.util,json,os,pathlib,pwd,queue,shutil,socket,sqlite3,subprocess,sys,tempfile,threading,time,unittest
BRIDGE=pathlib.Path(__file__).parents[1]/'backend'/'bridges.py'
HAVE=shutil.which('mosquitto') and importlib.util.find_spec('paho')

def free_port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]

@unittest.skipUnless(HAVE,'needs mosquitto and paho-mqtt')
class BrokerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.dir=pathlib.Path(self.tmp.name);self.db=self.dir/'cooks.sqlite3'
  self.port=free_port();self.procs=[];self.topic='omapit/test/temperatures'
 def tearDown(self):
  for p in self.procs:
   if p.poll() is None:p.terminate();p.wait(5)
   for pipe in (p.stdout,p.stderr):
    if pipe:pipe.close()
  self.tmp.cleanup()

 def broker(self,extra='',tls=False):
  conf=self.dir/'mosquitto.conf'
  # Started as root, mosquitto would switch to its own user and lose access to these private temp files.
  user=f'user {pwd.getpwuid(os.geteuid()).pw_name}\n'
  conf.write_text(f'listener {self.port} 127.0.0.1\npersistence false\n'+user+('allow_anonymous true\n' if 'password_file' not in extra else '')+extra)
  p=subprocess.Popen(['mosquitto','-c',str(conf)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True);self.procs.append(p)
  for _ in range(50):
   try:socket.create_connection(('127.0.0.1',self.port),0.2).close();return p
   except OSError:time.sleep(0.1)
  self.fail('broker did not start: '+p.stderr.read())
 def bridge(self,*args,env=None):
  p=subprocess.Popen([sys.executable,str(BRIDGE),'--db',str(self.db),'mqtt','--host',args[0] if args else '127.0.0.1','--port',str(self.port),'--topic',self.topic,*args[1:]],
   stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,env={**os.environ,**(env or {})});self.procs.append(p)
  lines=queue.Queue();threading.Thread(target=lambda:[lines.put(l.strip()) for l in p.stdout],daemon=True).start()
  return lines
 def publish(self,payload,retain=False,auth=None,tls_ca=None,host='127.0.0.1'):
  import paho.mqtt.client as mqtt
  c=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
  if auth:c.username_pw_set(*auth)
  if tls_ca:c.tls_set(ca_certs=tls_ca)
  c.connect(host,self.port,10);c.loop_start()
  body=payload if isinstance(payload,(bytes,str)) else json.dumps(payload)
  c.publish(self.topic,body,qos=1,retain=retain).wait_for_publish(5);c.loop_stop();c.disconnect()
 def sample(self,device='grill-1',age=0,**channels):
  return {'schema':1,'device':device,'name':'Test publisher','sample_at':time.time()-age,'channels':channels or {'food':{'value':165,'unit':'F'}}}
 def ready(self,lines,**kw):
  """Publish until the bridge answers, so later messages are not lost before it subscribes."""
  for _ in range(60):
   self.publish(self.sample('warmup',food={'value':20,'unit':'C'}),**kw)
   try:return lines.get(timeout=0.25)
   except queue.Empty:pass
  self.fail('bridge never received a message')
 def next(self,lines,timeout=5):
  try:return lines.get(timeout=timeout)
  except queue.Empty:return None
 def channel(self,device,role):
  db=sqlite3.connect(self.db);row=db.execute('SELECT value,unit,quality FROM channels WHERE device=? AND role=?',('bridge:mqtt:'+device,role)).fetchone();db.close();return row

 def test_live_sample_recorded_in_celsius(self):
  self.broker();lines=self.bridge();self.ready(lines)
  self.publish(self.sample(food={'value':165,'unit':'F'},ambient={'value':None,'unit':'F'}))
  self.assertTrue(json.loads(self.next(lines))['accepted'])
  value,unit,quality=self.channel('grill-1','food');self.assertAlmostEqual(value,73.89,2);self.assertEqual((unit,quality),('C','valid'))
  self.assertEqual(self.channel('grill-1','ambient')[2],'invalid')
 def test_retained_message_cannot_become_live(self):
  self.broker();self.publish(self.sample('retained-1'),retain=True)
  lines=self.bridge()
  self.assertIn('retained',json.loads(self.next(lines,10))['error'].lower());self.assertIsNone(self.channel('retained-1','food'))
 def test_stale_malformed_oversized_and_out_of_order(self):
  self.broker();lines=self.bridge();self.ready(lines)
  self.publish(self.sample(age=120));self.assertIn('error',json.loads(self.next(lines)))
  self.publish(b'{not json');self.assertEqual(self.next(lines),'Invalid MQTT message')
  self.publish({**self.sample(),'schema':2});self.assertIn('schema',json.loads(self.next(lines))['error'])
  self.publish(json.dumps([1,2]));self.publish(json.dumps({**self.sample(),'pad':'x'*9000}))  # both ignored silently
  newer=self.sample(food={'value':70,'unit':'C'});older={**self.sample(food={'value':60,'unit':'C'}),'sample_at':newer['sample_at']-2}
  self.publish(newer);self.assertTrue(json.loads(self.next(lines))['accepted'])
  self.publish(older);self.assertFalse(json.loads(self.next(lines))['accepted'])
  self.assertEqual(self.channel('grill-1','food')[0],70)
 def test_recovers_after_broker_restart(self):
  broker=self.broker();lines=self.bridge();self.ready(lines)
  broker.terminate();broker.wait(5);time.sleep(1);self.broker()
  self.assertTrue(self.ready(lines),'bridge did not reconnect and resubscribe')
  self.publish(self.sample(food={'value':80,'unit':'C'}));self.assertTrue(json.loads(self.next(lines))['accepted'])
 def test_username_and_password(self):
  passwords=self.dir/'passwords';subprocess.run(['mosquitto_passwd','-b','-c',str(passwords),'omapit','s3cret-pass'],check=True,capture_output=True)
  os.chmod(passwords,0o600)
  self.broker(f'allow_anonymous false\npassword_file {passwords}\n')
  lines=self.bridge(env={'OMAPIT_MQTT_USER':'omapit','OMAPIT_MQTT_PASSWORD':'s3cret-pass'});self.ready(lines,auth=('omapit','s3cret-pass'))
  self.publish(self.sample(),auth=('omapit','s3cret-pass'));self.assertTrue(json.loads(self.next(lines))['accepted'])
 @unittest.skipUnless(shutil.which('openssl'),'needs openssl')
 def test_tls_verifies_the_broker_certificate(self):
  run=lambda *a:subprocess.run(a,cwd=self.dir,check=True,capture_output=True)
  run('openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','2','-subj','/CN=OmaPit test CA','-keyout','ca.key','-out','ca.pem')
  run('openssl','req','-newkey','rsa:2048','-nodes','-subj','/CN=localhost','-keyout','server.key','-out','server.csr')
  (self.dir/'ext').write_text('subjectAltName=DNS:localhost,IP:127.0.0.1\n')
  run('openssl','x509','-req','-in','server.csr','-CA','ca.pem','-CAkey','ca.key','-CAcreateserial','-days','2','-extfile','ext','-out','server.pem')
  self.broker(f'cafile {self.dir/"ca.pem"}\ncertfile {self.dir/"server.pem"}\nkeyfile {self.dir/"server.key"}\n')
  ca=str(self.dir/'ca.pem')
  untrusted=self.bridge('localhost','--tls',env={'SSL_CERT_FILE':str(self.dir/'server.key')})  # no CA it trusts
  lines=self.bridge('localhost','--tls',env={'SSL_CERT_FILE':ca})
  self.ready(lines,tls_ca=ca,host='localhost')
  self.publish(self.sample(),tls_ca=ca,host='localhost');self.assertTrue(json.loads(self.next(lines))['accepted'])
  self.assertIsNone(self.next(untrusted,1),'bridge accepted data from an untrusted broker')
 def test_wildcard_topics_refused(self):
  run=subprocess.run([sys.executable,str(BRIDGE),'--db',str(self.db),'mqtt','--host','127.0.0.1','--topic','omapit/#'],capture_output=True,text=True)
  self.assertEqual(run.returncode,2);self.assertIn('exact topic',run.stderr)

if __name__=='__main__':unittest.main()
