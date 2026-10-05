import importlib.util, tempfile, unittest, pathlib, concurrent.futures
spec=importlib.util.spec_from_file_location('store',pathlib.Path(__file__).parents[1]/'backend/omapit.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class StoreTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.tmp.name)/'cooks.db';self.db=s.database(self.path)
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def call(self,a,p=None):return s.dispatch(self.db,a,p or {})
 def create(self):return self.call('create',{'name':'Pork shoulder','target':'19:00'})
 def test_complete_cook_survives_reopen(self):
  ident=self.create()['active']['id'];self.call('reading',{'meat':80,'pit':120,'unit':'C'});self.call('note',{'note':'Added oak'})
  with self.assertRaises(ValueError):self.call('advance',{'expected_stage':0})
  for k in ['bark','dry']:self.call('check',{'key':k,'value':True})
  for stage in range(3):self.call('advance',{'expected_stage':stage})
  self.call('finish');self.db.close();self.db=s.database(self.path)
  self.assertIsNone(self.call('snapshot')['active']);h=self.call('history',{'id':ident});self.assertEqual(h['readings'][0]['meat'],176);self.assertEqual(len(h['events']),5);self.assertIsNotNone(h['cook']['finished'])
 def test_no_live_data_fabricated(self):
  data=self.create();self.assertEqual(data['readings'],[]);self.assertEqual(data['active']['source'],'manual')
 def test_duplicate_cook_rejected(self):
  self.create()
  with self.assertRaises(ValueError):self.create()
 def test_demo_is_explicit_and_separate(self):
  demo=self.call('demo');self.assertEqual(demo['active']['source'],'demo');self.assertEqual(len(demo['readings']),91)
  with self.assertRaises(ValueError):self.call('reading',{'meat':80,'pit':120,'unit':'C'})
  self.call('finish');self.assertEqual(self.create()['readings'],[])
 def test_invalid_readings_rollback(self):
  self.create()
  for value in [float('nan'),float('inf'),-41,1001,'bad',None]:
   with self.assertRaises(ValueError):self.call('reading',{'meat':value,'pit':250,'unit':'F'})
  self.assertEqual(self.call('snapshot')['readings'],[])
 def test_units_persist_without_rewriting_data(self):
  self.create();self.call('reading',{'meat':164,'pit':248,'unit':'F'});self.call('unit',{'unit':'C'});self.assertEqual(self.call('snapshot')['readings'][0]['meat'],164)
 def test_stale_stage_rejected(self):
  self.create()
  for k in ['bark','dry']:self.call('check',{'key':k,'value':True})
  self.call('advance',{'expected_stage':0})
  with self.assertRaises(ValueError):self.call('advance',{'expected_stage':0})
  self.assertEqual(self.call('snapshot')['active']['stage'],1)
 def test_invalid_metadata(self):
  for p in [{'name':'','target':'19:00'},{'name':'x','target':'25:00'}]:
   with self.assertRaises(ValueError):self.call('create',p)
  self.assertEqual(self.call('snapshot')['cooks'],[])
 def test_simultaneous_start_is_atomic(self):
  def create():
   db=s.database(self.path)
   try:s.dispatch(db,'create',{'name':'Concurrent cook','target':'19:00'});return True
   except ValueError:return False
   finally:db.close()
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:results=list(ex.map(lambda _:create(),range(2)))
  self.assertEqual(sum(results),1)
if __name__=='__main__':unittest.main()
