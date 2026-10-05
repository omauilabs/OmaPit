import pathlib,sys,tempfile,unittest,struct,time,json,sqlite3
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'backend'))
import omapit as store
import devices
from unittest.mock import patch
from types import SimpleNamespace
import asyncio
from adapters.chefiq import decode

def packet(major=5,food=73.2,ambient=120.5):
 if major>=3:return bytes([1,major<<4])+struct.pack('<hhhhhhh',round(ambient*10),round(food*10),700,701,702,703,1200)
 if major==2:return bytes([1,32,85,25])+struct.pack('<hhhhh',round(ambient*10),round(food*10),700,701,702)
 return bytes([1,16])+bytes(6)+bytes([85,25])+struct.pack('<hh',round(food*10),round(ambient*10))
class DeviceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.tmp.name)/'cook.db';self.db=store.database(self.path)
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def ingest(self,ident='ble:a',payload=None,**kw):
  with self.db:return devices.ingest(self.db,ident,payload or packet(),**kw)
 def test_all_layouts(self):
  for major in [1,2,5]:
   p=decode(packet(major));self.assertEqual(p['channels']['food'],73.2);self.assertEqual(p['channels']['ambient'],120.5)
  self.assertEqual(decode(packet(2))['evidence'],'experimental')
 def test_unknown_and_truncated(self):
  for p in [b'',b'\x01\x50\x01',packet(6),bytes(20)]:
   with self.assertRaises(ValueError):decode(p)
 def test_invalid_sensor_clears_previous(self):
  self.ingest(at=time.time()-1);self.ingest(payload=packet(food=3276.7));self.assertIsNone(devices.snapshot(self.db)['devices'][0]['channels']['food']['value'])
 def test_status_does_not_freshen_temperature(self):
  self.ingest(at=time.time()-60);self.ingest(payload=bytes([3,80])+bytes(6)+bytes([88,24]))
  d=devices.snapshot(self.db)['devices'][0];self.assertFalse(d['channels']['food']['fresh']);self.assertTrue(d['channels']['battery']['fresh'])
 def test_invalid_battery_unknown(self):
  self.ingest(payload=bytes([3,80])+bytes(6)+bytes([255,24]));self.assertIsNone(devices.snapshot(self.db)['devices'][0]['channels']['battery']['value'])
 def test_device_isolation_and_selection(self):
  self.ingest(name='CQ50');self.ingest(ident='ble:b',payload=packet(food=20))
  cook=store.dispatch(self.db,'create',{'name':'Real cook'})['active'];store.dispatch(self.db,'select_device',{'id':'ble:a'})
  self.ingest(ident='ble:b');self.assertEqual(store.state(self.db)['readings'],[])
  self.ingest();data=store.state(self.db);self.assertEqual(len(data['readings']),1);self.assertAlmostEqual(data['readings'][0]['meat'],163.76);self.assertEqual(data['readings'][0]['device'],'ble:a')
  store.dispatch(self.db,'finish',{});self.ingest();self.assertEqual(len(store.dispatch(self.db,'history',{'id':cook['id']})['readings']),1)
 def test_replay_cannot_select_or_record(self):
  store.dispatch(self.db,'create',{'name':'Cook'});self.ingest(ident='replay:a',source='replay',at=1)
  with self.assertRaises(ValueError):store.dispatch(self.db,'select_device',{'id':'replay:a'})
  self.assertEqual(store.state(self.db)['readings'],[]);self.assertEqual(devices.snapshot(self.db)['devices'][0]['status'],'replay')
 def test_stale_selection_rejected(self):
  self.ingest(at=time.time()-60);store.dispatch(self.db,'create',{'name':'Cook'})
  with self.assertRaises(ValueError):store.dispatch(self.db,'select_device',{'id':'ble:a'})
 def test_delayed_packets_do_not_overwrite(self):
  now=time.time();self.ingest(at=now);self.ingest(payload=packet(food=20),at=now-5);self.assertEqual(devices.snapshot(self.db)['devices'][0]['channels']['food']['value'],73.2)
 def test_manual_provenance_survives_switch(self):
  store.dispatch(self.db,'create',{'name':'Cook'});store.dispatch(self.db,'reading',{'meat':100,'pit':200,'unit':'F'});self.ingest();store.dispatch(self.db,'select_device',{'id':'ble:a'})
  with self.assertRaises(ValueError):store.dispatch(self.db,'reading',{'meat':100,'pit':200,'unit':'F'})
  self.assertEqual(store.state(self.db)['readings'][0]['source'],'manual');store.dispatch(self.db,'manual_mode',{});self.assertIsNone(store.state(self.db)['selected_device'])
 def test_capture_replay_atomic(self):
  path=pathlib.Path(self.tmp.name)/'capture.jsonl';row={'schema':1,'device':'one','relative_seconds':0,'payload_hex':packet().hex()};path.write_text(json.dumps(row)+'\n')
  with self.db:self.assertEqual(devices.replay(self.db,path),1)
  self.assertEqual(devices.snapshot(self.db)['devices'][0]['channels']['food']['value'],73.2)
 def test_missing_bluetooth_dependency_reported(self):
  with patch.dict(sys.modules,{'bleak':None}):asyncio.run(devices.scan(str(self.path),0))
  self.assertEqual(devices.scanner_state(self.db)['status'],'error')
 def test_transport_ingests_and_redacts_capture(self):
  capture=pathlib.Path(self.tmp.name)/'capture.jsonl'
  status=bytes([3,80])+bytes.fromhex('aabbccddeeff')+bytes([80,25])
  class Scanner:
   def __init__(self,detection_callback):self.callback=detection_callback
   async def __aenter__(self):
    d=SimpleNamespace(address='AA:BB:CC:DD:EE:FF',name='CQ60 private name')
    self.callback(d,SimpleNamespace(manufacturer_data={1485:status},local_name='CQ60 private name',rssi=-60))
    return self
   async def __aexit__(self,*a):pass
  with patch.dict(sys.modules,{'bleak':SimpleNamespace(BleakScanner=Scanner)}):asyncio.run(devices.scan(str(self.path),0,str(capture),'AA:BB:CC:DD:EE:FF'))
  row=json.loads(capture.read_text());self.assertNotIn('AA:BB',capture.read_text());self.assertNotIn('private',capture.read_text());self.assertEqual(bytes.fromhex(row['payload_hex'])[2:8],bytes(6))
  self.assertEqual(devices.snapshot(self.db)['devices'][0]['channels']['battery']['value'],80)
 def test_failed_replay_rolls_back_batch(self):
  path=pathlib.Path(self.tmp.name)/'bad.jsonl';good={'schema':1,'device':'one','relative_seconds':0,'payload_hex':packet().hex()};path.write_text(json.dumps(good)+'\n'+json.dumps({**good,'schema':99})+'\n')
  with self.assertRaises(ValueError):
   with self.db:devices.replay(self.db,path)
  self.assertEqual(devices.snapshot(self.db)['devices'],[])
 def test_original_store_backup_and_migration(self):
  old=pathlib.Path(self.tmp.name)/'old.db';db=sqlite3.connect(old)
  db.executescript("CREATE TABLE readings(id INTEGER PRIMARY KEY,cook TEXT,at REAL,meat REAL,pit REAL); CREATE TABLE cooks(id TEXT PRIMARY KEY,name TEXT,started REAL,target TEXT,stage INTEGER,source TEXT,finished REAL,bark INTEGER,dry INTEGER); INSERT INTO cooks VALUES('a','Old cook',1,'19:00',0,'demo',NULL,0,0); INSERT INTO readings VALUES(1,'a',2,164,248);");db.close()
  db=store.database(old);self.assertEqual(dict(db.execute('SELECT * FROM readings').fetchone())['source'],'demo');db.close()
  backup=sqlite3.connect(str(old)+'.before-devices-v1.bak');self.assertEqual(len(backup.execute('PRAGMA table_info(readings)').fetchall()),5);backup.close()
if __name__=='__main__':unittest.main()
