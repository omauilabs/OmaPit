import pathlib,sys,tempfile,unittest,time
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'backend'))
import omapit as s,workflows
class Workflows(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.db=s.database(pathlib.Path(self.tmp.name)/'c.db');self.call('create',{'name':'Dinner','target':'19:00'})
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def call(self,cmd,p=None):return s.dispatch(self.db,cmd,p or {})
 def food(self,name='Corn'):
  return self.call('food_add',{'name':name,'category':'vegetables','target':70,'unit':'C','zone':'Gas grill'})['foods'][-1]
 def test_independent_foods_and_stages(self):
  a=self.food();b=self.food('Chicken');self.assertAlmostEqual(a['target_f'],158)
  self.call('food_advance',{'id':a['id'],'expected_stage':0});d=self.call('snapshot');self.assertEqual([f['stage'] for f in d['foods']],[1,0])
  with self.assertRaises(ValueError):self.call('food_advance',{'id':a['id'],'expected_stage':0})
  self.call('food_finish',{'id':a['id']});self.assertIsNone(self.call('snapshot')['foods'][1]['finished'])
 def test_manual_target_alarm_and_units(self):
  f=self.food();self.call('food_alarm',{'id':f['id']});d=self.call('food_reading',{'id':f['id'],'value':80,'unit':'C'})
  self.assertEqual(d['foods'][0]['reading']['value_f'],176);self.assertEqual(len(d['alarm_episodes']),1)
  self.call('food_finish',{'id':f['id']});self.assertIsNotNone(self.call('snapshot')['alarm_episodes'][0]['resolved'])
 def test_stages_edit_not_brisket_gated(self):
  f=self.food();self.call('food_edit',{'id':f['id'],'name':'Corn','zone':'Kettle','target':150,'unit':'F','steps':['Sear','Serve']})
  self.call('food_advance',{'id':f['id'],'expected_stage':0});self.assertEqual(self.call('snapshot')['foods'][0]['steps'],['Sear','Serve'])
 def test_schedule_dependencies_and_cycle_rollback(self):
  self.call('meal_goal',{'serve_at':__import__('datetime').datetime.fromtimestamp(time.time()+3600,__import__('datetime').timezone.utc).isoformat()})
  d=self.call('task_add',{'name':'Grill','minutes':20});a=d['plan']['tasks'][0]['id']
  d=self.call('task_add',{'name':'Rest','minutes':10,'depends':[a]});b=d['plan']['tasks'][1]['id']
  tasks=d['plan']['tasks'];self.assertEqual(tasks[0]['planned_finish'],tasks[1]['planned_start'])
  with self.assertRaises(ValueError):self.call('task_edit',{'id':a,'name':'Grill','minutes':20,'depends':[b]})
  self.assertEqual(self.call('snapshot')['plan']['tasks'][0]['depends'],[])
  with self.assertRaises(ValueError):self.call('task_delete',{'id':a})
 def test_task_delays_and_completion(self):
  self.call('task_add',{'name':'Vegetables','minutes':10});cook=self.call('snapshot')['active']['id']
  a=workflows.schedule(self.db,cook,now=100);b=workflows.schedule(self.db,cook,now=200)
  self.assertEqual(b['earliest_serve']-a['earliest_serve'],100)
  self.call('task_done',{'id':a['tasks'][0]['id'],'done':True});self.assertIsNotNone(self.call('snapshot')['plan']['tasks'][0]['completed'])
 def test_serving_date_requires_timezone(self):
  with self.assertRaises(ValueError):self.call('meal_goal',{'serve_at':'2026-10-03T19:00:00'})
if __name__=='__main__':unittest.main()
