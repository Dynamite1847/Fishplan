import http.cookiejar,json,secrets,sqlite3,tempfile,threading,unittest
from datetime import datetime,timezone,timedelta
from urllib import request,error
from pathlib import Path
import server
class APITests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();server.DATA=Path(cls.temp.name);server.DB=server.DATA/'records.sqlite3';server.DEV=True;server.ORIGIN='http://127.0.0.1';server.RATE.clear();server.initialize()
  cls.token=secrets.token_urlsafe(32)
  with server.database() as c:
   c.execute('INSERT INTO config VALUES(?,?)',('setup_hash',server.digest(cls.token)));c.execute('INSERT INTO config VALUES(?,?)',('setup_expires','9999999999'))
  cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start();cls.base=f'http://127.0.0.1:{cls.http.server_port}/fish/api/';cls.jar=http.cookiejar.CookieJar();cls.client=request.build_opener(request.HTTPCookieProcessor(cls.jar))
 @classmethod
 def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.temp.cleanup()
 def call(self,path,method='GET',body=None,headers=None,anonymous=False):
  req=request.Request(self.base+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers={'Origin':server.ORIGIN,'Content-Type':'application/json',**(headers or {})})
  try:r=(request.build_opener() if anonymous else self.client).open(req)
  except error.HTTPError as e:r=e
  return r.status,json.loads(r.read()),r.headers
 def test_full_flow(self):
  code,data,_=self.call('state',anonymous=True);self.assertEqual(code,200);self.assertEqual(data['tanks'][0]['volume_l'],20.75)
  self.assertEqual(self.call('tanks/qt','PUT',{'phase':'animals'},anonymous=True)[0],401)
  self.assertEqual(self.call('setup','POST',{'password':'qa-test-9','token':'bad'})[0],401)
  self.assertEqual(self.call('setup','POST',{'password':'12345678','token':self.token})[0],400)
  code,_,headers=self.call('setup','POST',{'password':'qa-test-9','token':self.token});self.assertEqual(code,200);self.assertIn('HttpOnly',headers['Set-Cookie']);self.assertIn('SameSite=Strict',headers['Set-Cookie'])
  self.assertTrue(self.call('session')[1]['authenticated']);self.assertEqual(self.call('setup','POST',{'password':'qa-test-9','token':self.token})[0],409)
  self.assertEqual(self.call('records','POST',{},headers={'Origin':'https://evil.invalid'})[0],403)
  body={'tank':'qt','client_id':'test-record-0000001','observed_at':(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat(),'nh3_reagent':'yier','measurements':{'nh3':0,'no2':.5,'no2_diluted':.1},'actions':{'note':'<img src=x onerror=alert(1)>'}}
  self.assertEqual(self.call('records','POST',body)[0],200);self.assertEqual(self.call('records','POST',body)[0],200)
  data=self.call('state')[1];self.assertEqual(len(data['tanks'][0]['records']),1);self.assertEqual(len(data['tanks'][1]['records']),0)
  rid=data['tanks'][0]['records'][0]['id'];body['actions']['note']='修改后';self.assertEqual(self.call('records/'+rid,'PUT',body)[0],200)
  old_cycle=data['tanks'][0]['cycle_id'];self.assertEqual(self.call('tanks/qt','PUT',{'phase':'animals','volume_l':20.75})[0],200)
  body['client_id']='test-record-0000002';body['actions']={'ammonium_ml':7.9,'ammonium_kind':'feed'};self.assertEqual(self.call('records','POST',body)[0],400)
  self.assertNotEqual(self.call('state')[1]['tanks'][0]['cycle_id'],old_cycle)
  self.assertEqual(self.call('records/'+rid,'DELETE',{})[0],200);self.assertEqual(len(self.call('state')[1]['tanks'][0]['records']),0)
  with server.database() as c:self.assertIsNotNone(c.execute('SELECT deleted_at FROM records WHERE id=?',(rid,)).fetchone()[0]);self.assertGreater(c.execute('SELECT COUNT(*) FROM audit').fetchone()[0],0)
  self.assertEqual(self.call('logout','POST',{})[0],200);self.assertFalse(self.call('session')[1]['authenticated']);self.assertEqual(self.call('login','POST',{'password':'qa-test-9'})[0],200)
  server.DEV=False
  try:self.assertEqual(self.call('login','POST',{'password':'qa-test-9'},headers={'X-Forwarded-Proto':'http'})[0],403)
  finally:server.DEV=True
  self.assertEqual(self.call('state',anonymous=True)[0],200)
if __name__=='__main__':unittest.main()
