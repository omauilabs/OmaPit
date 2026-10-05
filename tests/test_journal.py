import pathlib,sys,tempfile,unittest,base64
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'backend'))
import omapit as s,journal
class Journal(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.db=s.database(pathlib.Path(self.tmp.name)/'c.db')
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def call(self,cmd,p=None):return s.dispatch(self.db,cmd,p or {})
 def test_jsonld_sections_and_attribution(self):
  raw='''<script type="application/ld+json">{"@graph":[{"@type":"Recipe","name":"Corn","recipeYield":"4 servings","url":"https://example.org/corn","recipeIngredient":["2 ears corn"],"recipeInstructions":[{"@type":"HowToSection","itemListElement":[{"text":"Grill"},{"text":"Serve"}]}]}]}</script>'''
  d=self.call('recipe_import',{'text':raw});r=d['recipes'][0];self.assertEqual(r['steps'],['Grill','Serve']);self.assertEqual(r['servings'],4);self.assertEqual(r['source'],'https://example.org/corn')
 def test_backup_restore_preserves_journal_and_pauses_live(self):
  c=self.call('create',{'name':'Dinner','target':'19:00'})['active'];self.call('note',{'note':'Oak'});self.call('alarm_add',{'label':'Timer','kind':'timer','seconds':60});self.call('outcome',{'cook':c['id'],'rating':4,'texture':'Tender','taste':'Smoky'})
  bundle=self.call('backup');other=s.database(pathlib.Path(self.tmp.name)/'other.db')
  try:
   restored=s.dispatch(other,'restore',bundle);self.assertEqual(restored['events'][0]['note'],'Oak');self.assertEqual(restored['alarm_rules'][0]['enabled'],0);self.assertEqual(restored['outcomes'][0]['rating'],4)
  finally:other.close()
  with self.assertRaises(ValueError):self.call('restore',bundle)
 def test_bad_backup_rolls_back(self):
  bundle=self.call('backup');bundle['tables']['cooks']=[{'bad':'data'}]
  with self.assertRaises(ValueError):self.call('restore',bundle)
  self.assertEqual(self.call('snapshot')['cooks'],[])
 def test_photo_rejects_svg_url_and_fake_bytes(self):
  for x in ['https://example.org/a.jpg','data:image/svg+xml;base64,abc','data:image/png;base64,'+base64.b64encode(b'not a png').decode()]:
   with self.assertRaises(ValueError):journal.photo(x)
 def test_csv_formula_injection_and_units(self):
  self.call('create',{'name':'Dinner','target':'19:00'});f=self.call('food_add',{'name':'=DANGER()','category':'manual','target':150,'unit':'F'})['foods'][0];self.call('food_reading',{'id':f['id'],'value':80,'unit':'C'});out=self.call('csv',{'id':f['cook']})['csv'];self.assertIn("'=DANGER()",out);self.assertIn('176.0',out)
if __name__=='__main__':unittest.main()
