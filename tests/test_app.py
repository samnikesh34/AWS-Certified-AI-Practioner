import os,tempfile,unittest,re,json,time
from pathlib import Path
from werkzeug.datastructures import MultiDict
os.environ['DATABASE_PATH']=str(Path(tempfile.mkdtemp())/'test.sqlite3')
from app import app,db,DATA,is_correct
app.config['TESTING']=True
class AccountTests(unittest.TestCase):
 def setUp(self):self.a=app.test_client();self.b=app.test_client()
 def token(self,c):
  c.get('/auth')
  with c.session_transaction() as s:return s['csrf']
 def post(self,c,path,data=None):
  pairs=list((data or {}).items()) if isinstance(data or {},dict) else data
  return c.post(path,data=MultiDict([('csrf',self.token(c))]+pairs))
 def register(self,c,name):
  r=self.post(c,'/auth',{'action':'register','username':name,'password':'a-long-test-password','name':'Learner'})
  self.assertEqual(r.status_code,200);return re.search(rb'<code class="recovery">([^<]+)',r.data)[1].decode()
 def test_full_flow_and_isolation(self):
  recovery=self.register(self.a,'alice');self.register(self.b,'bob')
  self.assertEqual(self.a.get('/').status_code,200)
  self.post(self.a,'/topic/transfer');self.assertIn(b'Transfer learning',self.a.get('/activity').data);self.assertNotIn(b'Transfer learning',self.b.get('/activity').data)
  r=self.post(self.a,'/start/5',{'mode':'exam','minutes':'90'});path=r.location;attempt=int(path.split('/')[2]);page=self.a.get(path)
  self.assertEqual(page.status_code,200);self.assertNotIn(b'Every option explained',page.data);self.assertEqual(self.b.get(path).status_code,404);self.assertEqual(self.post(self.b,path,{'answer':'0'}).status_code,404)
  q=DATA['tests'][4]['questions'][0];reveal=self.post(self.a,path,{'action':'explain','answer':'0'});self.assertNotIn(b'Every option explained',reveal.data)
  self.post(self.a,path,{'action':'save','answer':str(q['correct'][0])})
  with app.app_context():self.assertEqual(json.loads(db().execute('SELECT answers FROM attempts WHERE id=?',(attempt,)).fetchone()[0])[q['id']],q['correct'])
  self.post(self.a,f'/attempt/{attempt}/finish');self.assertIn(b'Every option explained',self.a.get(f'/attempt/{attempt}/result').data);self.assertEqual(self.b.get(f'/attempt/{attempt}/result').status_code,404)
  old=app.test_client();self.post(old,'/auth',{'action':'login','username':'alice','password':'a-long-test-password'})
  self.post(self.a,'/logout');self.assertEqual(self.a.get('/').status_code,302)
  reset=self.post(self.a,'/recover',{'username':'alice','recovery':recovery,'password':'a-new-long-password'})
  self.assertEqual(reset.status_code,200);self.assertEqual(old.get('/').status_code,302);self.assertIn(b'Transfer learning',self.a.get('/activity').data)
 def test_security_and_expiry(self):
  self.register(self.a,'carol');self.assertEqual(self.a.post('/start/5').status_code,400)
  for path in ['/private/content.json','/app.py','/static/data.js','/.env','/instance/progress.sqlite3']:self.assertEqual(self.a.get(path).status_code,404)
  r=self.post(self.a,'/start/6',{'mode':'exam'});attempt=int(r.location.split('/')[2])
  with app.app_context():db().execute('UPDATE attempts SET deadline=? WHERE id=?',(time.time()-1,attempt));db().commit()
  self.post(self.a,r.location,{'answer':'0','action':'save'})
  with app.app_context():
   row=db().execute('SELECT * FROM attempts WHERE id=?',(attempt,)).fetchone();self.assertTrue(row['finished']);self.assertEqual(row['answers'],'{}')
  self.assertEqual(self.a.get('/').headers['Cache-Control'],'no-store')
 def test_all_content_and_grading(self):
  self.register(self.a,'dana')
  for path in ['/learn','/sources','/activity']:self.assertEqual(self.a.get(path).status_code,200)
  for lesson in DATA['lessons']:self.assertEqual(self.a.get('/reference/'+lesson['id']).status_code,200)
  for c in DATA['concepts']:self.assertEqual(self.a.get('/topic/'+c['id']).status_code,200)
  for test in DATA['tests']:
   r=self.post(self.a,f'/start/{test["id"]}',{'mode':'study'});attempt=int(r.location.split('/')[2])
   for i,q in enumerate(test['questions']):
    path=f'/attempt/{attempt}/question/{i}';self.assertEqual(self.a.get(path).status_code,200)
    r=self.post(self.a,path,[('answer',str(k)) for k in q['correct']]+[('action','explain')]);self.assertEqual(r.status_code,200);self.assertIn(b'Every option explained',r.data)
    self.assertTrue(is_correct(q,q['correct']));self.assertFalse(is_correct(q,[]))
   self.post(self.a,f'/attempt/{attempt}/finish');r=self.a.get(f'/attempt/{attempt}/result');self.assertEqual(r.status_code,200);self.assertIn(b'100%',r.data)
  self.assertIn(b'Test completed',self.a.get('/activity').data)
 def test_login_throttling(self):
  for _ in range(16):r=self.post(self.b,'/auth',{'username':'nonexistent','password':'wrong','action':'login'})
  self.assertEqual(r.status_code,429)
if __name__=='__main__':unittest.main()
