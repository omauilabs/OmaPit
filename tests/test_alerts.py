import pathlib,sys,tempfile,unittest,time
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'backend'))
import omapit as s,alerts
class Alerts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.tmp.name)/'c.db';self.db=s.database(self.path)
  self.cook=s.dispatch(self.db,'create',{'name':'Chicken','target':'19:00'})['active'];self.now=time.time()
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def rule(self,kind='high',**kw):
  with self.db:return alerts.add(self.db,self.cook,{'kind':kind,'label':'Test','unit':'F','threshold':160,**kw},self.now)
 def read(self,value,at=None,source='manual'):
  with self.db:self.db.execute('INSERT INTO readings(cook,at,meat,pit,source) VALUES(?,?,?,?,?)',(self.cook['id'],at or self.now,value,250,source))
 def evaluate(self,now):
  with self.db:alerts.evaluate(self.db,now)
 def episodes(self):return alerts.snapshot(self.db)['alarm_episodes']
 def test_buffer_repeat_ack_and_recovery(self):
  self.rule(buffer=10,repeat=20);self.read(165);self.evaluate(self.now);self.assertEqual(self.episodes(),[])
  self.evaluate(self.now+10);e=self.episodes()[0];self.evaluate(self.now+15);self.assertEqual(len(alerts.snapshot(self.db)['alarm_notices']),1)
  self.evaluate(self.now+30);self.assertEqual(len(alerts.snapshot(self.db)['alarm_notices']),2)
  s.dispatch(self.db,'alarm_ack',{'id':e['id']});self.evaluate(self.now+60);self.assertEqual(len(alerts.snapshot(self.db)['alarm_notices']),2)
  self.read(150,self.now+61);self.evaluate(self.now+61);self.assertIsNotNone(self.episodes()[0]['resolved'])
  self.read(165,self.now+62);self.evaluate(self.now+62);self.evaluate(self.now+72);self.assertEqual(len(self.episodes()),2)
 def test_restart_does_not_duplicate(self):
  self.rule();self.read(170);self.evaluate(self.now);self.db.close();self.db=s.database(self.path);self.evaluate(self.now+1)
  self.assertEqual(len(self.episodes()),1);self.assertEqual(len(alerts.snapshot(self.db)['alarm_notices']),1)
 def test_replay_demo_and_old_readings_do_not_trigger(self):
  self.rule();self.read(180,source='replay');self.evaluate(self.now);self.assertEqual(self.episodes(),[])
  self.read(180,self.now-400);self.evaluate(self.now);self.assertEqual(self.episodes(),[])
  with self.db:self.db.execute("UPDATE cooks SET source='demo'")
  self.read(180);self.evaluate(self.now);self.assertEqual(self.episodes(),[])
 def test_stale_without_sample_and_timer(self):
  self.rule('stale',threshold=30);self.evaluate(self.now+29);self.assertEqual(self.episodes(),[]);self.evaluate(self.now+30);self.assertEqual(len(self.episodes()),1)
  self.rule('timer',seconds=60);self.evaluate(self.now+60);self.assertEqual(len(self.episodes()),2)
 def test_snooze_disable_and_finish(self):
  rid=self.rule(repeat=10);self.read(180);self.evaluate(self.now);e=self.episodes()[0]
  s.dispatch(self.db,'alarm_snooze',{'id':e['id'],'seconds':300});self.evaluate(self.now+20);self.assertEqual(len(alerts.snapshot(self.db)['alarm_notices']),1)
  s.dispatch(self.db,'alarm_rule',{'id':rid,'enabled':False});self.assertIsNotNone(self.episodes()[0]['resolved'])
  s.dispatch(self.db,'alarm_rule',{'id':rid,'enabled':True});s.dispatch(self.db,'finish',{});self.assertTrue(all(e['resolved'] for e in self.episodes()))
 def test_low_and_unit_normalization(self):
  self.rule('low',threshold=80,unit='C');self.read(150);self.evaluate(self.now);self.assertEqual(len(self.episodes()),1)
 def test_unknown_battery_cannot_trigger(self):
  with self.db:self.db.execute('INSERT INTO devices VALUES(?,?,?,?,?,?,?,?,?,?)',('ble:test','Test','Unknown',None,None,'ble',self.now,None,None,'x'))
  self.rule('battery',device='ble:test',threshold=20);self.evaluate(self.now);self.assertEqual(self.episodes(),[])

 def test_hysteresis_keeps_one_episode(self):
  self.rule();self.read(165);self.evaluate(self.now)
  self.read(159,self.now+1);self.evaluate(self.now+1);self.assertIsNone(self.episodes()[0]['resolved'])
  self.read(157,self.now+2);self.evaluate(self.now+2);self.assertIsNotNone(self.episodes()[0]['resolved'])

if __name__=='__main__':unittest.main()
