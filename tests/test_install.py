import importlib.util,json,os,pathlib,shutil,subprocess,sys,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('installer',ROOT/'packaging'/'install.py');installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)

class InstallTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.home=pathlib.Path(self.tmp.name)
  self.env=patch.dict(os.environ,{'HOME':str(self.home),'XDG_CONFIG_HOME':str(self.home/'config'),'XDG_DATA_HOME':str(self.home/'data')});self.env.start()
  self.target=installer.default_target();self.store=self.home/'data'/'omapit'/'cooks.sqlite3'
 def tearDown(self):self.env.stop();self.tmp.cleanup()
 def source(self,version):
  src=self.home/('src-'+version)
  for rel in installer.payload(ROOT):(src/rel).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,src/rel)
  manifest=json.loads((src/'manifest.json').read_text());manifest['version']=version;(src/'manifest.json').write_text(json.dumps(manifest))
  return src
 def run_install(self,**kw):return installer.install(log=lambda *a:None,**kw)

 def test_payload_is_complete_and_clean(self):
  files={str(f) for f in installer.payload(ROOT)}
  for needed in ['manifest.json','Main.qml','Widget.qml','Bridge.qml','backend/omapit.py','backend/adapters/__init__.py','backend/adapters/CHEFIQ-LICENSE.txt','assets/grill.png','assets/compatibility.json','LICENSE','CHEFIQ-HARDWARE-TEST.md']:self.assertIn(needed,files)
  self.assertFalse([f for f in files if '__pycache__' in f or f.endswith('.pyc') or f.startswith(('preview','tests','.git'))])
 def test_fresh_install(self):
  self.assertIsNone(self.run_install())
  record=json.loads((self.target/installer.RECORD).read_text())
  self.assertEqual(record['version'],installer.version_of(ROOT));self.assertEqual(sorted(record['files']),sorted(map(str,installer.payload(ROOT))))
  self.assertEqual((self.target/'backend'/'omapit.py').read_bytes(),(ROOT/'backend'/'omapit.py').read_bytes())
  self.assertFalse(self.store.exists());self.assertEqual(installer.edited_files(self.target),[])
 def test_dry_run_changes_nothing(self):
  self.run_install(dry_run=True);self.assertFalse(self.target.exists());self.assertFalse((self.home/'data').exists())
 def test_refuses_unmanaged_folder(self):
  self.target.mkdir(parents=True);(self.target/'mine.qml').write_text('keep')
  with self.assertRaises(SystemExit):self.run_install()
  self.assertEqual(os.listdir(self.target),['mine.qml'])
 def test_update_backs_up_outside_plugins_and_removes_stale_files(self):
  self.run_install(source=self.source('0.4.1'))
  # Simulate a file that 0.4.1 shipped and 0.4.2 no longer does.
  record=json.loads((self.target/installer.RECORD).read_text());record['files']['backend/retired.py']=installer._sha(self.target/'LICENSE')
  shutil.copy2(self.target/'LICENSE',self.target/'backend'/'retired.py');(self.target/installer.RECORD).write_text(json.dumps(record))
  self.store.parent.mkdir(parents=True,exist_ok=True);self.store.write_bytes(b'journal')
  backup=self.run_install(source=self.source('0.4.2'))
  self.assertEqual(json.loads((self.target/installer.RECORD).read_text())['version'],'0.4.2')
  self.assertFalse((self.target/'backend'/'retired.py').exists())
  self.assertEqual(json.loads((backup/'manifest.json').read_text())['version'],'0.4.1');self.assertTrue((backup/'backend'/'retired.py').exists())
  self.assertNotIn(installer.default_target().parent,backup.parents);self.assertEqual(os.listdir(self.target.parent),['local.omapit'])
  self.assertEqual(self.store.read_bytes(),b'journal')
 def test_refuses_downgrade_unless_allowed(self):
  self.run_install(source=self.source('0.5.0'))
  with self.assertRaises(SystemExit):self.run_install(source=self.source('0.4.2'))
  self.assertEqual(json.loads((self.target/'manifest.json').read_text())['version'],'0.5.0')
  self.run_install(source=self.source('0.4.2'),allow_downgrade=True)
  self.assertEqual(json.loads((self.target/'manifest.json').read_text())['version'],'0.4.2')
 def test_edited_files_protected(self):
  self.run_install();(self.target/'Main.qml').write_text('// my tweak');(self.target/'Chart.qml').unlink()
  self.assertEqual(installer.edited_files(self.target),['Chart.qml','Main.qml'])
  with self.assertRaises(SystemExit):self.run_install()
  self.assertEqual((self.target/'Main.qml').read_text(),'// my tweak')
  backup=self.run_install(force=True);self.assertEqual((backup/'Main.qml').read_text(),'// my tweak');self.assertEqual(installer.edited_files(self.target),[])
 def test_failed_swap_restores_previous_install(self):
  self.run_install(source=self.source('0.4.1'));real=shutil.move;calls=[]
  def flaky(src,dst):
   calls.append(dst)
   if len(calls)==2:raise OSError('disk full')
   return real(src,dst)
  with patch.object(installer.shutil,'move',flaky),self.assertRaises(OSError):self.run_install(source=self.source('0.4.2'))
  self.assertEqual(json.loads((self.target/installer.RECORD).read_text())['version'],'0.4.1')
  self.assertEqual([p.name for p in installer.backup_root().iterdir() if p.name.startswith('.staging')],[])
 def test_installed_copy_runs(self):
  self.run_install()
  run=subprocess.run([sys.executable,str(self.target/'backend'/'diagnose.py'),'--db',str(self.home/'none.sqlite3'),'--json'],capture_output=True,text=True,cwd=self.home)
  self.assertEqual(run.returncode,0,run.stderr);checks=json.loads(run.stdout)['checks']
  self.assertEqual([c['status'] for c in checks if c['area'] in ('install','adapters')],['ok','ok','ok'])

if __name__=='__main__':unittest.main()
