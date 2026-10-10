import io,json,os,pathlib,sqlite3,subprocess,sys,tempfile,time,unittest
from contextlib import redirect_stdout
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'backend'))
import omapit as store
import devices,diagnose
from test_devices import packet
BACKEND=pathlib.Path(__file__).parents[1]/'backend'

class DiagnoseTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.tmp.name)/'cooks.sqlite3'
 def tearDown(self):self.tmp.cleanup()
 def make(self):
  db=store.database(self.path)
  with db:store.seed_demo(db)
  return db
 def run_report(self,*args):
  out=io.StringIO()
  with redirect_stdout(out):code=diagnose.main(['--db',str(self.path),'--json',*args])
  return code,json.loads(out.getvalue())
 def statuses(self,data,area):return [c['status'] for c in data['checks'] if c['area']==area]

 def test_missing_store_is_not_created(self):
  self.path=pathlib.Path(self.tmp.name)/'new'/'cooks.sqlite3'
  code,data=self.run_report();self.assertEqual(code,0);self.assertFalse(self.path.parent.exists())
  self.assertIn('created on first launch',json.dumps(data))
 def test_never_writes_existing_store(self):
  self.make().close();before=self.path.read_bytes();files=sorted(os.listdir(self.tmp.name))
  code,data=self.run_report();self.assertEqual(code,0);self.assertFalse(data['failed'])
  self.assertEqual(self.path.read_bytes(),before);self.assertEqual(sorted(os.listdir(self.tmp.name)),files)
 def test_cli_entry_point_does_not_migrate_or_create(self):
  self.path=pathlib.Path(self.tmp.name)/'none'/'cooks.sqlite3'
  run=subprocess.run([sys.executable,str(BACKEND/'omapit.py'),'--db',str(self.path),'diagnose'],capture_output=True,text=True)
  self.assertEqual(run.returncode,0,run.stderr);self.assertIn('OmaPit diagnostics',run.stdout);self.assertFalse(self.path.parent.exists())
 def test_legacy_store_reported_not_migrated(self):
  db=sqlite3.connect(self.path);db.executescript('CREATE TABLE cooks(id TEXT PRIMARY KEY,name TEXT,started REAL,target TEXT,stage INTEGER,source TEXT,finished REAL);CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT);');db.close()
  before=self.path.read_bytes();code,data=self.run_report()
  self.assertEqual(code,0);self.assertIn('warn',self.statuses(data,'store'));self.assertEqual(self.path.read_bytes(),before)
  self.assertEqual(list(pathlib.Path(self.tmp.name).glob('*.bak')),[])
 def test_newer_store_fails(self):
  for change in ['PRAGMA user_version=2',"UPDATE settings SET value='2' WHERE key='workbench_schema'"]:
   with self.subTest(change):
    if self.path.exists():self.path.unlink()
    self.make().close();db=sqlite3.connect(self.path);db.execute(change);db.commit();db.close()
    code,data=self.run_report();self.assertEqual(code,1);self.assertTrue(data['failed']);self.assertIn('fail',self.statuses(data,'store'))
 def test_corrupt_store_fails_cleanly(self):
  self.path.write_bytes(b'not a database'*100)
  code,data=self.run_report();self.assertEqual(code,1);self.assertIn('fail',self.statuses(data,'store'))
 def test_private_data_never_reported(self):
  db=self.make()
  with db:store.dispatch(db,'note',{'note':'secret family recipe'})
  with db:devices.ingest(db,'ble:AA:BB:CC:DD:EE:FF',packet(food=63.1))
  db.close()
  with patch.dict(os.environ,{'OMAPIT_TOKEN':'tok-'+'z'*40,'OMAPIT_NTFY_URL':'https://example.invalid/private-topic'}):
   code,data=self.run_report()
  text=json.dumps(data)
  for private in ['Saturday brisket','secret family recipe','AA:BB','63.1','145.6','tok-','private-topic']:self.assertNotIn(private,text)
  self.assertIn('OMAPIT_TOKEN',text);self.assertIn('OMAPIT_NTFY_URL',text)
 def test_short_token_warned(self):
  with patch.dict(os.environ,{'OMAPIT_TOKEN':'short'}):code,data=self.run_report()
  self.assertIn('warn',self.statuses(data,'config'))
 def test_stale_live_probe_on_active_cook_warned(self):
  db=store.database(self.path)
  with db:store.dispatch(db,'create',{'name':'Cook'})
  with db:devices.ingest(db,'ble:a',packet(),at=time.time()-120)
  db.close();self.assertIn('warn',self.statuses(self.run_report()[1],'devices'))
  db=store.database(self.path)
  with db:devices.ingest(db,'ble:a',packet())
  db.close();self.assertEqual(self.statuses(self.run_report()[1],'devices'),['ok','info'])
 def test_unsupported_device_warned(self):
  db=store.database(self.path)
  with db:devices.ingest(db,'ble:a',b'\x01\x60\x00')
  db.close();self.assertIn('warn',self.statuses(self.run_report()[1],'devices'))
 def test_monitor_heartbeat(self):
  db=store.database(self.path)
  with db:db.execute("INSERT OR REPLACE INTO settings VALUES('service_heartbeat',?)",(json.dumps({'at':time.time(),'mode':'monitor'}),))
  db.close();self.assertEqual(self.statuses(self.run_report()[1],'alarms'),['ok'])
  db=store.database(self.path)
  with db:db.execute("INSERT OR REPLACE INTO settings VALUES('service_heartbeat','not json')")
  db.close();self.assertEqual(self.statuses(self.run_report()[1],'alarms'),['info'])
 def test_human_output(self):
  self.make().close();out=io.StringIO()
  with redirect_stdout(out):self.assertEqual(diagnose.main(['--db',str(self.path)]),0)
  self.assertIn('[ok  ] store',out.getvalue());self.assertIn('No problems found.',out.getvalue())

if __name__=='__main__':unittest.main()
