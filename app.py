import os, json, sqlite3, secrets, hashlib, time, re
from pathlib import Path
from functools import wraps
from flask import Flask, request, session, redirect, url_for, render_template, abort, g, flash
from werkzeug.security import generate_password_hash, check_password_hash

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT/'private/content.json').read_text())
TESTS = {t['id']:t for t in DATA['tests']}
app = Flask(__name__)
production = os.environ.get('APP_ENV') == 'production'
secret = os.environ.get('SECRET_KEY')
if production and (not secret or len(secret)<32):
    raise RuntimeError('Set SECRET_KEY to a random value of at least 32 characters.')
app.config.update(SECRET_KEY=secret or secrets.token_hex(32), SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=production,
    MAX_CONTENT_LENGTH=32768, DATABASE=os.environ.get('DATABASE_PATH',str(ROOT/'instance/progress.sqlite3')))

def db():
    if 'db' not in g:
        Path(app.config['DATABASE']).parent.mkdir(parents=True,exist_ok=True)
        g.db=sqlite3.connect(app.config['DATABASE'],timeout=20)
        g.db.row_factory=sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db

@app.teardown_appcontext
def close(error):
    conn=g.pop('db',None)
    if conn: conn.close()

def init_db():
    db().executescript('''
    PRAGMA journal_mode=WAL;
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, name TEXT NOT NULL, password TEXT NOT NULL, recovery TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id),expires REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS learned(user_id INTEGER NOT NULL REFERENCES users(id),topic TEXT NOT NULL,PRIMARY KEY(user_id,topic));
    CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id),test_id INTEGER NOT NULL,mode TEXT NOT NULL,started REAL NOT NULL,deadline REAL,finished REAL,answers TEXT NOT NULL DEFAULT '{}',seen TEXT NOT NULL DEFAULT '[]',flags TEXT NOT NULL DEFAULT '[]',position INTEGER NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS activity(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id),action TEXT NOT NULL,detail TEXT NOT NULL,at REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS limits(key TEXT PRIMARY KEY,count INTEGER NOT NULL,until REAL NOT NULL);
    ''');db().commit()

with app.app_context(): init_db()

def event(action,detail):
    db().execute('INSERT INTO activity(user_id,action,detail,at) VALUES(?,?,?,?)',(g.user['id'],action,detail,time.time()))

def limit(key,maximum=10):
    now=time.time(); c=db();c.execute('DELETE FROM limits WHERE until<?',(now,))
    c.execute('INSERT INTO limits VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET count=count+1',(key,now+900))
    row=c.execute('SELECT count FROM limits WHERE key=?',(key,)).fetchone();c.commit()
    if row['count']>maximum: abort(429,description='Too many attempts. Try again in 15 minutes.')

def sign_in(user):
    old=session.get('auth')
    if old: db().execute('DELETE FROM sessions WHERE token=?',(old,))
    session.clear();token=secrets.token_urlsafe(32);session['auth']=token
    session['csrf']=secrets.token_urlsafe(32)
    db().execute('INSERT INTO sessions VALUES(?,?,?)',(token,user['id'],time.time()+7*86400));db().commit()

@app.before_request
def protect():
    g.user=None
    token=session.get('auth')
    if token:
        g.user=db().execute('SELECT users.* FROM users JOIN sessions ON sessions.user_id=users.id WHERE sessions.token=? AND sessions.expires>?',(token,time.time())).fetchone()
    if 'csrf' not in session: session['csrf']=secrets.token_urlsafe(32)
    if request.method=='POST':
        if not secrets.compare_digest(request.form.get('csrf',''),session['csrf']): abort(400,description='Form expired. Reload the page and try again.')

def login_required(fn):
    @wraps(fn)
    def wrapped(*a,**kw):
        if not g.user:return redirect(url_for('auth'))
        return fn(*a,**kw)
    return wrapped

@app.after_request
def headers(r):
    r.headers['Cache-Control']='no-store'
    r.headers['X-Content-Type-Options']='nosniff'
    r.headers['Referrer-Policy']='same-origin'
    r.headers['Content-Security-Policy']="default-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; script-src 'none'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    if production:r.headers['Strict-Transport-Security']='max-age=31536000'
    return r

@app.context_processor
def context():return {'csrf':session.get('csrf'),'user':g.user,'domains':DATA['domains']}

@app.template_filter('date')
def date(v):return time.strftime('%d %b %Y, %H:%M UTC',time.gmtime(v)) if v else ''

@app.route('/auth',methods=['GET','POST'])
def auth():
    if request.method=='POST':
        username=request.form.get('username','').strip().lower();password=request.form.get('password','')
        limit('auth-ip:'+str(request.remote_addr),60);limit('auth-user:'+username,15)
        action=request.form.get('action')
        if not re.fullmatch(r'[a-z0-9_]{3,30}',username):flash('Use 3–30 letters, numbers or underscores for your username.');return redirect(url_for('auth'))
        if action=='register':
            if len(password)<12 or len(password)>256:flash('Choose a password between 12 and 256 characters.');return redirect(url_for('auth'))
            name=request.form.get('name','').strip()[:60] or username
            recovery=secrets.token_urlsafe(24)
            try:
                db().execute('INSERT INTO users(username,name,password,recovery) VALUES(?,?,?,?)',(username,name,generate_password_hash(password),hashlib.sha256(recovery.encode()).hexdigest()));db().commit()
            except sqlite3.IntegrityError:flash('That username is unavailable.');return redirect(url_for('auth'))
            user=db().execute('SELECT * FROM users WHERE username=?',(username,)).fetchone();sign_in(user);g.user=user;event('Account created','Welcome to your learning account');db().commit()
            return render_template('recovery.html',recovery=recovery)
        user=db().execute('SELECT * FROM users WHERE username=?',(username,)).fetchone()
        valid=check_password_hash(user['password'] if user else DUMMY_HASH,password[:257])
        if not user or not valid:flash('Incorrect username or password.');return redirect(url_for('auth'))
        sign_in(user);g.user=user;event('Signed in','Account accessed');db().commit();return redirect(url_for('home'))
    return render_template('auth.html')
DUMMY_HASH=generate_password_hash('not-a-real-user-password')

@app.route('/recover',methods=['GET','POST'])
def recover():
    if request.method=='POST':
        username=request.form.get('username','').lower().strip();limit('recover-ip:'+str(request.remote_addr),20);limit('recover-user:'+username)
        user=db().execute('SELECT * FROM users WHERE username=?',(username,)).fetchone()
        digest=hashlib.sha256(request.form.get('recovery','').strip().encode()).hexdigest();password=request.form.get('password','')
        if not user or not secrets.compare_digest(user['recovery'],digest) or not 12<=len(password)<=256:
            flash('Check your username, recovery key and password (12–256 characters).');return redirect(url_for('recover'))
        recovery=secrets.token_urlsafe(24)
        db().execute('UPDATE users SET password=?,recovery=? WHERE id=?',(generate_password_hash(password),hashlib.sha256(recovery.encode()).hexdigest(),user['id']))
        db().execute('DELETE FROM sessions WHERE user_id=?',(user['id'],));db().commit();sign_in(user);g.user=user;event('Password reset','Recovery key rotated');db().commit()
        return render_template('recovery.html',recovery=recovery)
    return render_template('recover.html')

@app.post('/logout')
@login_required
def logout():
    db().execute('DELETE FROM sessions WHERE token=?',(session.get('auth'),));db().commit();session.clear();return redirect(url_for('auth'))

@app.get('/')
@login_required
def home():
    attempts=db().execute('SELECT * FROM attempts WHERE user_id=? ORDER BY id DESC',(g.user['id'],)).fetchall()
    learned=[r['topic'] for r in db().execute('SELECT topic FROM learned WHERE user_id=?',(g.user['id'],))]
    return render_template('home.html',tests=TESTS,attempts=attempts,learned=learned)

@app.get('/learn')
@login_required
def learn():
    query=request.args.get('q','').lower();concepts=[c for c in DATA['concepts'] if query in (c['label']+' '+c['meaning']).lower()]
    return render_template('learn.html',concepts=concepts,lessons=DATA['lessons'])

@app.route('/topic/<topic>',methods=['GET','POST'])
@login_required
def topic(topic):
    c=next((c for c in DATA['concepts'] if c['id']==topic),None)
    if not c:abort(404)
    if request.method=='POST':
        db().execute('INSERT OR IGNORE INTO learned VALUES(?,?)',(g.user['id'],topic));event('Lesson completed',c['label']);db().commit();flash('Lesson marked understood.');return redirect(url_for('topic',topic=topic))
    return render_template('topic.html',c=c)

@app.get('/reference/<lesson>')
@login_required
def reference(lesson):
    item=next((c for c in DATA['lessons'] if c['id']==lesson),None)
    if not item:abort(404)
    return render_template('reference.html',lesson=item)

@app.post('/start/<int:test_id>')
@login_required
def start(test_id):
    if test_id not in TESTS:abort(404)
    mode='exam' if request.form.get('mode')=='exam' else 'study';minutes=120 if request.form.get('minutes')=='120' else 90
    now=time.time();cur=db().execute('INSERT INTO attempts(user_id,test_id,mode,started,deadline) VALUES(?,?,?,?,?)',(g.user['id'],test_id,mode,now,now+minutes*60 if mode=='exam' else None))
    event('Test started',f'Test {test_id} · {mode}');db().commit();return redirect(url_for('question',attempt=cur.lastrowid,index=0))

def owned(attempt):
    a=db().execute('SELECT * FROM attempts WHERE id=? AND user_id=?',(attempt,g.user['id'])).fetchone()
    if not a:abort(404)
    if not a['finished'] and a['deadline'] and time.time()>=a['deadline']:
        db().execute('UPDATE attempts SET finished=? WHERE id=?',(a['deadline'],attempt));event('Test completed',f'Test {a["test_id"]} · time expired');db().commit()
        a=db().execute('SELECT * FROM attempts WHERE id=?',(attempt,)).fetchone()
    return a

def is_correct(q,answer):
    return answer==q['correct'] if q['type'] in ('ordering','matching') else sorted(answer)==sorted(q['correct'])

@app.route('/attempt/<int:attempt>/question/<int:index>',methods=['GET','POST'])
@login_required
def question(attempt,index):
    a=owned(attempt);test=TESTS[a['test_id']]
    if not 0<=index<len(test['questions']):abort(404)
    if a['finished']:return redirect(url_for('result',attempt=attempt))
    q=test['questions'][index];answers=json.loads(a['answers']);seen=json.loads(a['seen']);flags=json.loads(a['flags']);reveal=False
    if request.method=='POST':
        action=request.form.get('action');answer=[]
        try: answer=[int(v) for v in request.form.getlist('answer') if v!='']
        except ValueError:abort(400)
        if any(v<0 or v>=len(q['options']) for v in answer):abort(400)
        if q['type']=='single' and len(answer)>1:abort(400)
        if q['type'] in ('matching','ordering') and answer and len(answer)!=len(q['correct']):flash('Select every position before saving.');return redirect(url_for('question',attempt=attempt,index=index))
        if q['type']=='ordering' and len(answer)!=len(set(answer)):flash('Use each step once.');return redirect(url_for('question',attempt=attempt,index=index))
        if q['type'] not in ('matching','ordering') and len(answer)!=len(set(answer)):abort(400)
        if answer:answers[q['id']]=answer
        else:answers.pop(q['id'],None)
        if action=='explain' and a['mode']=='study':
            reveal=True
            if q['id'] not in seen:seen.append(q['id']);event('Explanation viewed',f'Test {test["id"]}, question {index+1}')
        if action=='flag':
            if q['id'] in flags:flags.remove(q['id'])
            else:flags.append(q['id'])
        newindex=min(index+1,len(test['questions'])-1) if action=='next' else max(0,index-1) if action=='previous' else index
        db().execute('UPDATE attempts SET answers=?,seen=?,flags=?,position=? WHERE id=?',(json.dumps(answers),json.dumps(seen),json.dumps(flags),newindex,attempt));db().commit()
        if action=='finish':return redirect(url_for('finish',attempt=attempt))
        if not reveal:return redirect(url_for('question',attempt=attempt,index=newindex))
    remaining=max(0,int((a['deadline']-time.time())/60)) if a['deadline'] else None
    return render_template('question.html',a=a,test=test,q=q,index=index,answer=answers.get(q['id'],[]),seen=seen,flags=flags,reveal=reveal,remaining=remaining)

@app.route('/attempt/<int:attempt>/finish',methods=['GET','POST'])
@login_required
def finish(attempt):
    a=owned(attempt)
    if a['finished']:return redirect(url_for('result',attempt=attempt))
    if request.method=='POST':
        db().execute('UPDATE attempts SET finished=? WHERE id=?',(time.time(),attempt));event('Test completed',f'Test {a["test_id"]}');db().commit();return redirect(url_for('result',attempt=attempt))
    return render_template('finish.html',a=a,answered=len(json.loads(a['answers'])))

@app.get('/attempt/<int:attempt>/result')
@login_required
def result(attempt):
    a=owned(attempt)
    if not a['finished']:return redirect(url_for('question',attempt=attempt,index=a['position']))
    t=TESTS[a['test_id']];answers=json.loads(a['answers']);seen=json.loads(a['seen']);flags=json.loads(a['flags'])
    rows=[{'q':q,'answer':answers.get(q['id'],[]),'right':is_correct(q,answers.get(q['id'],[])),'flag':q['id'] in flags,'assisted':q['id'] in seen} for q in t['questions']]
    scored=[r for r in rows if not r['q'].get('unscored')];right=sum(r['right'] for r in scored)
    groups=[{'name':name,'total':sum(r['q']['domain']==i+1 for r in scored),'right':sum(r['q']['domain']==i+1 and r['right'] for r in scored)} for i,name in enumerate(DATA['domains'])]
    return render_template('result.html',a=a,rows=rows,right=right,total=len(scored),percent=round(right/len(scored)*100) if scored else 0,groups=groups)

@app.get('/activity')
@login_required
def activity():
    page=max(1,request.args.get('page',1,type=int));rows=db().execute('SELECT * FROM activity WHERE user_id=? ORDER BY id DESC LIMIT 50 OFFSET ?',(g.user['id'],(page-1)*50)).fetchall()
    return render_template('activity.html',rows=rows,page=page)

@app.get('/sources')
@login_required
def sources():return render_template('sources.html',data=DATA)

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(429)
def error(e):return render_template('error.html',error=e),e.code

@app.get('/health')
def health():return {'status':'ok'}

if __name__=='__main__':app.run(host='127.0.0.1',port=8000,debug=False)
