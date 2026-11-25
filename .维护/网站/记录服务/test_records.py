import copy,json,tempfile,unittest
from datetime import datetime,timezone,timedelta
from care import RULES,advice,challenge_progress,classify
from server import validate_record

NOW=datetime(2026,11,6,4,tzinfo=timezone.utc)
def row(hours=0,m=None,a=None,reagent='yier',i='1'):
 return {'id':i,'tank':'qt','observed_at':(NOW+timedelta(hours=hours)).isoformat(),'phase':'cycling','cycle_id':'cycle','measurements':m or {},'actions':a or {},'nh3_reagent':reagent}
def tank(phase='cycling',volume=20.75):return {'id':'qt','phase':phase,'volume_l':volume,'cycle_id':'cycle'}
def text(result):return '\n'.join(x['title']+' '+x['text'] for x in result['tips'])
class RulesTests(unittest.TestCase):
 def test_boundaries(self):
  cases=[('nh3',2,'cycling','green'),('nh3','>2','cycling','yellow'),('nh3','<0.15','animals','green'),('nh3',.25,'animals','red'),('no2',.1,'cycling','green'),('no2',.5,'cycling','yellow'),('no2',.005,'animals','red'),('no3',100,'cycling','neutral'),('no3',10,'animals','green'),('no3',25,'animals','yellow'),('no3',50,'animals','red'),('kh',7,'cycling','green'),('kh',6,'cycling','yellow'),('kh',5.9,'cycling','red'),('ph',7.8,'animals','green'),('ph',7.79,'animals','red'),('salinity',1.025,'cycling','green'),('salinity',1.024,'cycling','yellow'),('salinity',1.023,'cycling','red'),('temperature',24,'cycling','green'),('temperature',29,'cycling','green'),('temperature',22,'cycling','yellow'),('temperature',30,'cycling','yellow'),('temperature',25,'animals','green'),('temperature',24,'animals','yellow'),('temperature',27,'animals','yellow'),('temperature',28,'animals','red')]
  for key,v,phase,want in cases:
   with self.subTest(key=key,v=v,phase=phase):self.assertEqual(classify(key,v,phase)['level'],want)
 def test_optional_missing_and_dose(self):
  self.assertIn('先测',text(advice(tank(),[row(m={'temperature':28})],NOW)))
  self.assertIn('15.85mL',text(advice(tank(),[row(m={'nh3':0,'no2':.1})],NOW)))
  self.assertNotIn('15.85mL',text(advice(tank(volume=None),[row(m={'nh3':0,'no2':.1})],NOW)))
 def test_reference_not_clearance(self):
  self.assertIn('先用可靠NH3',text(advice(tank(),[row(m={'nh3':'<0.15','no2':0},reagent='salifert')],NOW)))
 def test_no_repeat_dosing(self):
  records=[row(-1,m={'nh3':0,'no2':0},a={'ammonium_ml':7.93,'ammonium_kind':'feed'})]
  self.assertIn('不重复加',text(advice(tank(),records,NOW)))
 def test_diluted(self):
  for diluted,want in [(None,'测稀释样'),(.1,'补喂一次'),(.5,'继续等')]:
   m={'nh3':0,'no2':.5}
   if diluted is not None:m['no2_diluted']=diluted
   self.assertIn(want,text(advice(tank(),[row(m=m)],NOW)))
 def test_three_distinct_consecutive_days(self):
  daily=[row(-48,m={'nh3':0,'no2':'between'},i='1'),row(-24,m={'nh3':0,'no2':'between'},i='2'),row(m={'nh3':0,'no2':'between'},i='3')]
  self.assertIn('补喂一次',text(advice(tank(),daily,NOW)))
  same_day=[row(-2,m={'nh3':0,'no2':'between'},i='1'),row(-1,m={'nh3':0,'no2':'between'},i='2'),row(m={'nh3':0,'no2':'between'},i='3')]
  self.assertIn('等NO2下降',text(advice(tank(),same_day,NOW)))
 def test_two_checks_no_reuse_of_results(self):
  records=[row(-49,a={'ammonium_ml':15.85,'ammonium_kind':'check'},i='1'),row(-25,m={'nh3':0,'no2':.1},a={'ammonium_ml':15.85,'ammonium_kind':'check'},i='2'),row(-1,m={'nh3':0,'no2':.1},i='3')]
  result=advice(tank(),records,NOW);self.assertEqual(result['progress']['passed'],2);self.assertIn('养好了',text(result))
  self.assertEqual(advice(tank(),records[:2],NOW-timedelta(hours=24))['progress']['passed'],1)
 def test_failed_dilution_reference_and_changes_not_passed(self):
  base=[row(-25,a={'ammonium_ml':15.85,'ammonium_kind':'check'})]
  for measurement,reagent,actions in [({'nh3':.25,'no2':0},'yier',{}),({'nh3':'<0.15','no2':0},'salifert',{}),({'nh3':0,'no2':.5,'no2_diluted':0},'yier',{}),({'temperature':28},'yier',{})]:
   self.assertEqual(advice(tank(),base+[row(m=measurement,reagent=reagent,a=actions,i='2')],NOW)['progress']['passed'],0)
  for action in [{'water_change_l':5},{'prime_ml':.5},{'ammonium_ml':7.93,'ammonium_kind':'feed'}]:
   records=base+[row(-12,a=action,i='2'),row(m={'nh3':0,'no2':0},i='3')]
   self.assertEqual(advice(tank(),records,NOW)['progress']['passed'],0)
 def test_window_stale_stage(self):
  self.assertNotIn('开始24',text(advice(tank(),[row(-26,m={'nh3':0,'no2':0})],NOW)))
  records=[row(-40,a={'ammonium_ml':15.85,'ammonium_kind':'check'}),row(m={'nh3':0,'no2':0},i='2')]
  self.assertEqual(advice(tank(),records,NOW)['progress']['passed'],0)
  old=records[0].copy();old['cycle_id']='old';self.assertIsNone(advice(tank(),[old],NOW)['progress']['pending'])
 def test_prime_and_low_kh(self):
  records=[row(-1,a={'prime_ml':.5}),row(m={'nh3':0,'no2':0},i='2')]
  self.assertNotIn('开始24',text(advice(tank(),records,NOW)))
  self.assertNotIn('开始24',text(advice(tank(),[row(m={'kh':5.5,'nh3':0,'no2':0})],NOW)))
 def test_animals_and_liters(self):
  out=text(advice(tank('animals'),[row(m={'nh3':1})],NOW));self.assertIn('10.38L',out);self.assertIn('0.52mL',out);self.assertNotIn('开始24',out)
 def test_validation(self):
  base=row(-48,m={'nh3':0,'no2':.5,'no2_diluted':.1});self.assertEqual(validate_record(base)['measurements']['no2_diluted'],.1)
  for m in [{'no2':.2},{'no2':.1,'no2_diluted':.1},{'nh3':float('nan')},{'ph':15},{'nh3':True}]:
   with self.assertRaises(ValueError):validate_record(row(-48,m=m))
if __name__=='__main__':unittest.main()
