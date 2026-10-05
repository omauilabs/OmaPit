import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'backend'))
import prediction as p
class Prediction(unittest.TestCase):
 def rows(self,rate=.5,count=20):return [{'at':1000+i*60,'value_f':140+i*rate,'source':'manual'} for i in range(count)]
 def test_linear_range_and_no_false_confidence(self):
  r=p.estimate(self.rows(),160,now=2140);self.assertEqual(r['status'],'estimate');self.assertFalse(r['validated']);self.assertLess(r['earliest'],3400);self.assertGreater(r['latest'],3400)
 def test_stall_cooling_stale_and_far_target(self):
  for rate in (0,-.2):self.assertEqual(p.estimate(self.rows(rate),160,now=2140)['status'],'stall_or_cooling')
  self.assertEqual(p.estimate(self.rows(),160,now=2500)['status'],'insufficient')
  self.assertEqual(p.estimate(self.rows(),220,now=2140)['status'],'insufficient')
 def test_small_sample_gap_replay(self):
  self.assertEqual(p.estimate(self.rows(count=7),160,now=1360)['status'],'insufficient')
  rows=self.rows();rows[10:]=[{**r,'at':r['at']+1000} for r in rows[10:]];self.assertEqual(p.estimate(rows,160,now=3140)['status'],'insufficient')
  self.assertEqual(p.estimate([{**r,'source':'replay'} for r in self.rows()],160,now=2140)['status'],'insufficient')
 def test_acceleration_abstains(self):
  rows=[{'at':1000+i*60,'value_f':140+.3*i+.006*i*i,'source':'manual'} for i in range(20)]
  self.assertEqual(p.estimate(rows,160,now=2140)['status'],'insufficient')
 def test_held_out_prefix_and_metrics(self):
  a={'id':'synthetic','category':'quick','target_f':159.5,'readings':self.rows(count=40)};b={'id':'flat','category':'smoke','target_f':160,'readings':self.rows(rate=0,count=40)}
  r=p.evaluate([a,b]);self.assertEqual(r['sessions'],2);self.assertEqual(r['scored'],1);self.assertEqual(r['abstained'],1);self.assertEqual(r['range_coverage'],1)
if __name__=='__main__':unittest.main()
