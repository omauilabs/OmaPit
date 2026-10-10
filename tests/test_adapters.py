import asyncio,copy,json,pathlib,sys,tempfile,time,unittest
from types import ModuleType,SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'backend'))
import omapit as store
import devices,adapters,compatibility
from adapters import chefiq
from test_devices import packet

def fake_adapter(**overrides):
 m=ModuleType('fake');m.ADAPTER_ID='fake';m.ADAPTER_VERSION='0.1.0';m.NAME='Fake';m.TRANSPORT='ble-advertisement';m.DEFAULT_NAME='Fake probe'
 m.payload_from=lambda data:data.get(0xFFFF)
 m.decode=lambda p:{'protocol':'1.0.0','format':'fake','evidence':'experimental','channels':{'food':p[0]/2},'adapter':'fake','adapter_version':'0.1.0'}
 m.model_from_name=lambda name:'F1';m.redact=lambda p:bytes(len(p))
 for k,v in overrides.items():setattr(m,k,v)
 return m

class RegistryTests(unittest.TestCase):
 def test_shipped_adapters_meet_contract(self):
  self.assertIn('chefiq',adapters.REGISTRY)
  for a in adapters.REGISTRY.values():self.assertEqual(adapters.problems(a),[],a.ADAPTER_ID)
  self.assertEqual(adapters.describe()[0]['version'],chefiq.ADAPTER_VERSION)
 def test_broken_adapters_rejected(self):
  missing=fake_adapter();del missing.decode
  self.assertIn('missing decode',adapters.problems(missing))
  self.assertTrue(adapters.problems(fake_adapter(ADAPTER_VERSION='1.0')))
  self.assertTrue(adapters.problems(fake_adapter(TRANSPORT='wifi')))
  self.assertTrue(adapters.problems(fake_adapter(redact='not callable')))
  with self.assertRaises(RuntimeError):adapters._build([missing])
  with self.assertRaises(RuntimeError):adapters._build([fake_adapter(),fake_adapter()])
 def test_match_by_company_id(self):
  self.assertEqual(adapters.match({chefiq.MANUFACTURER_ID:packet()})[0],chefiq)
  for data in [{},{0x004C:packet()},{chefiq.MANUFACTURER_ID:b'\x01'},{chefiq.MANUFACTURER_ID:bytes(19)}]:
   self.assertIsNone(adapters.match(data))
 def test_unknown_adapter_id(self):
  with self.assertRaises(ValueError):adapters.get('meater')
 def test_chefiq_contract_helpers(self):
  self.assertEqual(chefiq.model_from_name('my cq60'),'CQ60');self.assertEqual(chefiq.model_from_name(''),'Unknown')
  status=bytes([3,80])+bytes.fromhex('aabbccddeeff')+bytes([80,25])
  self.assertEqual(chefiq.redact(status)[2:8],bytes(6));self.assertEqual(chefiq.redact(packet()),packet())

class DispatchTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.tmp.name)/'cook.db';self.db=store.database(self.path)
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def test_unknown_adapter_creates_nothing(self):
  with self.assertRaises(ValueError):
   with self.db:devices.ingest(self.db,'ble:a',packet(),adapter='meater')
  self.assertEqual(devices.snapshot(self.db)['devices'],[])
 def test_unsupported_payload_keeps_adapter_version(self):
  with self.db:devices.ingest(self.db,'ble:a',b'\x01\x60\x00')
  d=devices.snapshot(self.db)['devices'][0];self.assertEqual(d['status'],'unsupported');self.assertEqual(d['adapter_version'],chefiq.ADAPTER_VERSION)
 def test_stale_via_registry(self):
  with self.db:devices.ingest(self.db,'ble:a',packet(),at=time.time()-60,adapter='chefiq')
  d=devices.snapshot(self.db)['devices'][0];self.assertEqual(d['status'],'stale');self.assertFalse(d['channels']['food']['fresh'])
 def test_replay_adapter_field(self):
  path=pathlib.Path(self.tmp.name)/'capture.jsonl'
  rows=[{'schema':1,'adapter':'chefiq','device':'one','relative_seconds':0,'payload_hex':packet().hex()},{'schema':1,'device':'two','relative_seconds':1,'payload_hex':packet(food=20).hex()}]
  path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
  with self.db:self.assertEqual(devices.replay(self.db,path),2)
  self.assertEqual(sorted(d['channels']['food']['value'] for d in devices.snapshot(self.db)['devices']),[20,73.2])
 def test_replay_unknown_adapter_rolls_back(self):
  path=pathlib.Path(self.tmp.name)/'capture.jsonl';good={'schema':1,'device':'one','relative_seconds':0,'payload_hex':packet().hex()}
  path.write_text(json.dumps(good)+'\n'+json.dumps({**good,'adapter':'meater'})+'\n')
  with self.assertRaises(ValueError):
   with self.db:devices.replay(self.db,path)
  self.assertEqual(devices.snapshot(self.db)['devices'],[])
 def test_scan_routes_each_advertisement_to_its_adapter(self):
  fake=fake_adapter();capture=pathlib.Path(self.tmp.name)/'capture.jsonl'
  class Scanner:
   def __init__(self,detection_callback):self.callback=detection_callback
   async def __aenter__(self):
    self.callback(SimpleNamespace(address='AA',name=None),SimpleNamespace(manufacturer_data={0xFFFF:bytes([150])},local_name=None,rssi=-50))
    self.callback(SimpleNamespace(address='BB',name=None),SimpleNamespace(manufacturer_data={chefiq.MANUFACTURER_ID:packet()},local_name='CQ60',rssi=-60))
    self.callback(SimpleNamespace(address='CC',name=None),SimpleNamespace(manufacturer_data={0x004C:b'\x01\x02'},local_name=None,rssi=-70))
    return self
   async def __aexit__(self,*a):pass
  with patch.dict(adapters.REGISTRY,{'fake':fake}),patch.dict(sys.modules,{'bleak':SimpleNamespace(BleakScanner=Scanner)}):
   asyncio.run(devices.scan(str(self.path),0))
   found={d['id']:d for d in devices.snapshot(self.db)['devices']}
   self.assertEqual(sorted(found),['ble:AA','ble:BB'])  # unclaimed CC is ignored
   self.assertEqual((found['ble:AA']['name'],found['ble:AA']['model'],found['ble:AA']['channels']['food']['value']),('Fake probe','F1',75))
   self.assertEqual((found['ble:BB']['model'],found['ble:BB']['channels']['food']['value']),('CQ60',73.2))
   asyncio.run(devices.scan(str(self.path),0,str(capture),'AA'))
  row=json.loads(capture.read_text());self.assertEqual((row['adapter'],row['payload_hex']),('fake','00'))

class ManifestTests(unittest.TestCase):
 def setUp(self):self.good=compatibility.load()
 def check(self,mutate):
  m=copy.deepcopy(self.good);mutate(m);return compatibility.problems(m,compatibility.app_version())
 def test_shipped_manifest_valid(self):
  self.assertEqual(compatibility.problems(self.good,compatibility.app_version()),[])
 def test_version_must_match_release(self):
  self.assertTrue(self.check(lambda m:m.update(app_version='0.0.1')))
 def test_unsupported_claims_rejected(self):
  def promote(m):m['devices'][0]['implementation']='implemented'
  self.assertTrue(any('live test' in p for p in self.check(promote)))
  self.assertTrue(self.check(lambda m:m.update(control_commands=True)))
  self.assertTrue(self.check(lambda m:m['devices'][0].update(adapter_version='9.0.0')))
 def test_malformed_and_missing_rows(self):
  for mutate in [lambda m:m['devices'][0].pop('adapter_version'),lambda m:m['devices'][0].update(adapter='meater'),
                 lambda m:m['devices'][0].update(roles=['fan']),lambda m:m['devices'][0].update(roles=[]),
                 lambda m:m['devices'][0].update(roles=['food'],unverified_roles=['food']),
                 lambda m:m['devices'][0].update(omapit_live_test='no'),lambda m:m['devices'][0].update(acceptance='MISSING.md'),
                 lambda m:m['bridges'][0].pop('evidence'),lambda m:m.update(devices=[]),lambda m:m.update(schema=2),
                 lambda m:m['devices'].append('row')]:
   self.assertTrue(self.check(mutate))
  self.assertEqual(compatibility.problems([]),['manifest must be a JSON object'])

if __name__=='__main__':unittest.main()
