import pathlib,sys,tempfile,time,unittest
from datetime import datetime,timezone
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'backend'))
import omapit as s,workflows,journal
class Planner(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.db=s.database(pathlib.Path(self.tmp.name)/'plan.db')
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def call(self,c,p=None):return s.dispatch(self.db,c,p or {})
 def setup(self,**changes):
  p={'name':'Dinner together','serve_at':datetime.fromtimestamp(time.time()+7200,timezone.utc).isoformat(),'unit':'F','preheat':15,'resources':[{'id':'main','name':'Kettle','capacity':2}],'foods':[{'name':'Chicken','category':'poultry','target':165,'pit':350,'minutes':30,'prep':10,'rest':10,'slots':1,'resource':'main'},{'name':'Corn','category':'vegetables','target':150,'pit':350,'minutes':15,'prep':5,'rest':0,'slots':1,'resource':'main'}]}
  p.update(changes);return self.call('guided_setup',p)
 def test_setup_atomic_and_persistent(self):
  d=self.setup();self.assertEqual(len(d['foods']),2);self.assertEqual(len(d['plan']['tasks']),7);self.assertEqual(len(d['alarm_rules']),2)
  self.assertEqual(self.call('snapshot')['plan']['resources'][0]['capacity'],2)
  with self.assertRaises(ValueError):self.setup()
 def test_invalid_setup_rolls_back_everything(self):
  with self.assertRaises(ValueError):self.setup(foods=[{'name':'Broken','target':165,'pit':350,'minutes':30,'resource':'missing'}])
  self.assertEqual(self.db.execute('SELECT COUNT(*) FROM cooks').fetchone()[0],0)
  self.assertEqual(self.db.execute('SELECT COUNT(*) FROM settings WHERE key LIKE "planner:%"').fetchone()[0],0)
 def test_capacity_serializes_and_temperature_compatibility(self):
  self.call('create',{'name':'Meal'});self.call('grill_config',{'resources':[{'id':'main','name':'Kettle','capacity':2}]})
  for name,pit,slots in [('A',350,1),('B',350,1),('C',225,1),('D',350,2)]:self.call('task_add',{'name':name,'minutes':20,'resource':'main','pit_f':pit,'slots':slots})
  d=self.call('snapshot')['plan'];a,b,c,e=d['tasks'];self.assertEqual(a['earliest_start'],b['earliest_start']);self.assertGreaterEqual(c['earliest_start'],a['earliest_finish']);self.assertGreaterEqual(e['earliest_start'],c['earliest_finish'])
  # Back-planned intervals also cannot exceed capacity or mix temperatures.
  for left in d['tasks']:
   for right in d['tasks']:
    if left['id']==right['id']:continue
    overlap=left['planned_start']<right['planned_finish'] and right['planned_start']<left['planned_finish']
    if overlap:self.assertLessEqual(left['slots']+right['slots'],2);self.assertLessEqual(abs(left['pit_f']-right['pit_f']),25)
 def test_dependency_and_running_reservation_guards(self):
  d=self.setup();cook=next(t for t in d['plan']['tasks'] if t['name']=='Cook Chicken')
  with self.assertRaises(ValueError):self.call('task_start',{'id':cook['id']})
  for ident in cook['depends']:self.call('task_done',{'id':ident,'done':True})
  self.call('task_start',{'id':cook['id']})
  self.call('task_add',{'name':'Different heat','minutes':20,'resource':'main','pit_f':225,'slots':1})
  t=self.call('snapshot')['plan']['tasks'][-1]
  with self.assertRaises(ValueError):self.call('task_start',{'id':t['id']})
  with self.assertRaises(ValueError):self.call('task_start',{'id':cook['id']})
 def test_overcapacity_edit_is_transactional(self):
  self.setup();before=self.call('snapshot')['plan']['resources']
  with self.assertRaises(ValueError):self.call('grill_config',{'resources':[{'id':'main','name':'Too small','capacity':1}]})
  self.assertEqual(before,self.call('snapshot')['plan']['resources'])
 def test_backup_roundtrip_preserves_reservations(self):
  self.setup();bundle=self.call('backup');other=s.database(pathlib.Path(self.tmp.name)/'restored.db')
  try:
   d=s.dispatch(other,'restore',bundle);self.assertEqual(d['plan']['resources'][0]['name'],'Kettle');self.assertEqual(len(d['plan']['tasks']),7)
  finally:other.close()
 def test_elapsed_estimate_does_not_release_running_space(self):
  self.call('create',{'name':'Meal'});self.call('grill_config',{'resources':[{'id':'main','name':'Kettle','capacity':1}]})
  self.call('task_add',{'name':'Still cooking','minutes':1,'resource':'main','pit_f':350,'slots':1});t=self.call('snapshot')['plan']['tasks'][0]
  self.call('task_start',{'id':t['id']})
  import planner
  c=planner.config(self.db,self.call('snapshot')['active']['id']);c['tasks'][t['id']]['started']=time.time()-120;planner.save(self.db,t['cook'],c);self.db.commit()
  self.call('task_add',{'name':'Waiting','minutes':10,'resource':'main','pit_f':350,'slots':1});waiting=self.call('snapshot')['plan']['tasks'][1]
  with self.assertRaises(ValueError):self.call('task_start',{'id':waiting['id']})
  with self.assertRaises(ValueError):self.call('task_edit',{'id':t['id'],'name':t['name'],'minutes':10,'resource':'','slots':1})
  self.assertTrue(self.call('snapshot')['plan']['tasks'][0]['estimate_elapsed'])
 def test_review_and_completed_timing_survive_restore(self):
  self.call('create',{'name':'Meal'});self.call('task_add',{'name':'Prep','minutes':10});d=self.call('snapshot');ident=d['active']['id'];t=d['plan']['tasks'][0]['id']
  self.call('task_start',{'id':t});self.call('task_done',{'id':t,'done':True});self.call('cook_review',{'cook':ident,'lesson':'Rest longer next time.'})
  self.assertEqual(self.call('history',{'id':ident})['review']['lesson'],'Rest longer next time.')
  other=s.database(pathlib.Path(self.tmp.name)/'roundtrip.db')
  try:
   result=s.dispatch(other,'restore',self.call('backup'));self.assertIsNotNone(result['plan']['tasks'][0]['started'])
  finally:other.close()
 def test_invalid_resource_and_food_shapes(self):
  for values in ([None],[1],[{'id':'main','name':'Bad','capacity':1.5}]):
   with self.assertRaises(ValueError):self.setup(resources=values)
  with self.assertRaises(ValueError):self.setup(foods=[None])
  self.assertIsNone(self.call('snapshot')['active'])
if __name__=='__main__':unittest.main()
