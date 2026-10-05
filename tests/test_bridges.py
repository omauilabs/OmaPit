import pathlib,sys,tempfile,unittest,time
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'backend'))
import omapit as s,bridges,delivery
class Bridges(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.db=s.database(pathlib.Path(self.tmp.name)/'c.db');self.now=time.time()
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def packet(self,**kw):return {'schema':1,'source':'json','device':'test','name':'Kettle','sample_at':self.now,'channels':{'food':{'value':176,'unit':'F'}},**kw}
 def test_fahrenheit_partial_duplicate_and_old(self):
  with self.db:r=bridges.ingest(self.db,self.packet())
  self.assertEqual(self.db.execute('SELECT value FROM channels').fetchone()[0],80)
  with self.db:self.assertFalse(bridges.ingest(self.db,self.packet())['accepted'])
  self.assertEqual(self.db.execute('SELECT COUNT(*) FROM samples').fetchone()[0],1)
  for p in [self.packet(sample_at=self.now-40),self.packet(retained=True),self.packet(sample_at=self.now+10)]:
   with self.assertRaises(ValueError):bridges.ingest(self.db,p)
 def test_null_and_bad_data(self):
  with self.db:bridges.ingest(self.db,self.packet(channels={'food':{'value':None,'unit':'C'}}))
  self.assertEqual(self.db.execute('SELECT quality FROM channels').fetchone()[0],'invalid')
  for p in [self.packet(schema=2),self.packet(channels={'food':{'value':float('nan'),'unit':'C'}}),self.packet(channels={'foo':{'value':10,'unit':'F'}})]:
   with self.assertRaises(ValueError):bridges.ingest(self.db,p)
 def test_food_mapping_and_alarms(self):
  s.dispatch(self.db,'create',{'name':'Dinner','target':'19:00'});f=s.dispatch(self.db,'food_add',{'name':'Chicken','category':'poultry','target':170,'unit':'F'})['foods'][0]
  with self.db:r=bridges.ingest(self.db,self.packet(sample_at=time.time()))
  s.dispatch(self.db,'food_map',{'id':f['id'],'device':r['id']});s.dispatch(self.db,'food_alarm',{'id':f['id']})
  d=s.dispatch(self.db,'snapshot',{});self.assertTrue(d['foods'][0]['reading']['fresh']);self.assertEqual(len(d['alarm_episodes']),1)
 def test_ha_preserves_source_timestamp(self):
  p=bridges.ha_payload({'state':'unavailable','last_updated':'2026-10-03T20:00:00Z','attributes':{'unit_of_measurement':'°C'}},'food','sensor.food')
  self.assertIsNone(p['channels']['food']['value']);self.assertEqual(p['sample_at'],1791057600)
 def test_notification_default_is_off(self):
  with patch.dict('os.environ',{},clear=True):self.assertEqual(delivery.transports(),[]);delivery.deliver(self.db)
 def test_desktop_delivery_deduplicates(self):
  s.dispatch(self.db,'create',{'name':'Dinner','target':'19:00'});s.dispatch(self.db,'alarm_add',{'label':'Timer','kind':'timer','seconds':1})
  import alerts
  with self.db:alerts.evaluate(self.db,time.time()+2)
  with patch.dict('os.environ',{'OMAPIT_DESKTOP_NOTIFY':'1'},clear=True),patch('delivery.subprocess.run') as run:
   delivery.deliver(self.db,time.time()+2);delivery.deliver(self.db,time.time()+3);self.assertEqual(run.call_count,1)

 def test_same_timestamp_different_channels(self):
  with self.db:
   bridges.ingest(self.db,self.packet())
   r=bridges.ingest(self.db,self.packet(channels={'ambient':{'value':250,'unit':'F'}}))
  self.assertTrue(r['accepted']);self.assertEqual(self.db.execute('SELECT COUNT(*) FROM channels').fetchone()[0],2)

if __name__=='__main__':unittest.main()
