#!/usr/bin/env python3
"""127.0.0.1上的记录API；Python标准库＋SQLite，nginx负责HTTPS。"""
import argparse, hashlib, hmac, json, math, os, re, secrets, sqlite3, threading, time
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from care import RULES, NAMES, classify, advice, dt

DATA=Path(os.environ.get('FISH_RECORDS_DATA','/var/lib/fish-records'))
DB=DATA/'records.sqlite3'
ORIGIN=os.environ.get('FISH_RECORDS_ORIGIN','https://dystudio.fun')
PREFIX='/fish/api/'
DEV=os.environ.get('FISH_RECORDS_DEV')=='1'
SESSION_DAYS=180
RATE={};RATE_LOCK=threading.Lock()

def now():return datetime.now(timezone.utc).isoformat()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def password_hash(password,salt):return hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt),n=16384,r=8,p=1).hex()
@contextmanager
def database():
    con=sqlite3.connect(DB,timeout=15);con.row_factory=sqlite3.Row
    try:
        with con:yield con
    finally:con.close()

def initialize():
    DATA.mkdir(parents=True,exist_ok=True)
    with database() as c:
        c.execute('PRAGMA journal_mode=WAL')
        c.executescript('''CREATE TABLE IF NOT EXISTS config(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS tanks(id TEXT PRIMARY KEY,name TEXT NOT NULL,phase TEXT NOT NULL,volume_l REAL,cycle_id TEXT NOT NULL,updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY,tank TEXT NOT NULL,observed_at TEXT NOT NULL,phase TEXT NOT NULL,cycle_id TEXT NOT NULL,payload TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,deleted_at TEXT);
        CREATE INDEX IF NOT EXISTS records_time ON records(tank,observed_at);
        CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,expires_at REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,at TEXT NOT NULL,action TEXT NOT NULL,record_id TEXT,payload TEXT);''')
        for key,t in RULES['tanks'].items():c.execute('INSERT OR IGNORE INTO tanks VALUES(?,?,?,?,?,?)',(key,t['name'],'cycling',t['volume_l'],secrets.token_hex(12),now()))
    os.chmod(DB,0o600)

def config(c,key):
    row=c.execute('SELECT value FROM config WHERE key=?',(key,)).fetchone();return row['value'] if row else None

def session(c,token):
    c.execute('DELETE FROM sessions WHERE expires_at<?',(time.time(),));c.execute('INSERT INTO sessions VALUES(?,?)',(digest(token),time.time()+SESSION_DAYS*86400))

def validate_record(body):
    if body.get('tank') not in RULES['tanks']:raise ValueError('缸的选择无效')
    date=dt(str(body.get('observed_at','')))
    if date>datetime.now(timezone.utc)+timedelta(minutes=5) or date.year<2020:raise ValueError('日期不能晚于当前时间，且须在2020年之后')
    m=body.get('measurements',{});a=body.get('actions',{})
    if not isinstance(m,dict) or not isinstance(a,dict):raise ValueError('记录格式无效')
    if set(m)-set(NAMES)-{'no2_diluted'}:raise ValueError('含不支持的测量项目')
    if set(a)-{'ammonium_ml','ammonium_kind','biodigest','water_change_l','prime_ml','note'}:raise ValueError('含不支持的操作项目')
    reagent=body.get('nh3_reagent','yier')
    if reagent not in ['yier','salifert']:raise ValueError('请选择NH3试剂')
    bounds={'nh3':(0,100),'no2':(0,100),'no2_diluted':(0,.5),'no3':(0,1000),'kh':(0,40),'ph':(0,14),'salinity':(1,1.1),'temperature':(0,60),'po4':(0,100)}
    for key,value in m.items():
        if isinstance(value,bool):raise ValueError('读数须为数字或色卡格子')
        if key=='nh3' and reagent=='salifert':
            if value not in RULES['cards']['nh3_salifert']:raise ValueError('NH3请选择色卡格子')
        elif key=='no2' and value=='between':continue
        else:
            if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or not bounds[key][0]<=value<=bounds[key][1]:raise ValueError(f'{NAMES.get(key,key)}读数超出可记录范围')
            if key in ['no2','no3','no2_diluted'] and value not in RULES['cards']['no2' if key=='no2_diluted' else key]:raise ValueError(f'{key}请选择色卡格子')
    if 'no2_diluted' in m and m.get('no2')!=RULES['cycling']['no2_top']:raise ValueError('原水到顶格时才填稀释样')
    for k in ['ammonium_ml','biodigest','water_change_l','prime_ml']:
        if k not in a:continue
        x=a[k]
        if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not 0<=x<=10000:raise ValueError('操作数量需为0～10000的数字')
        if k=='biodigest' and x!=int(x):raise ValueError('科迪按整支记录')
    if a.get('ammonium_ml',0)>0 and a.get('ammonium_kind') not in ['initial','feed','check']:raise ValueError('请选择首剂、补喂或检查量')
    if not isinstance(a.get('note',''),str) or len(a.get('note',''))>2000:raise ValueError('备注最多2000字')
    if not m and not any(a.get(k,0)>0 for k in ['ammonium_ml','biodigest','water_change_l','prime_ml']) and not a.get('note','').strip():raise ValueError('至少填一项读数、操作或备注')
    return {'tank':body['tank'],'observed_at':date.isoformat(),'nh3_reagent':reagent,'measurements':m,'actions':a}

def unpack(row):
    p=json.loads(row['payload']);return {**p,**{k:row[k] for k in ['id','phase','cycle_id','created_at','updated_at']}}

class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    server_version='FishRecords'
    def log_message(self,format,*args):pass
    def send_json(self,status,body,cookie=None):
        raw=json.dumps(body,ensure_ascii=False,allow_nan=False).encode();self.send_response(status)
        for k,v in {'Content-Type':'application/json; charset=utf-8','Content-Length':str(len(raw)),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'}.items():self.send_header(k,v)
        if cookie:self.send_header('Set-Cookie',cookie)
        self.end_headers();self.wfile.write(raw)
    def cookie(self,token,logout=False):
        return f'fish_records_session={token}; Path=/fish/api/; Max-Age={0 if logout else SESSION_DAYS*86400}; HttpOnly; SameSite=Strict'+('' if DEV else '; Secure')
    def authenticated(self,c):
        try:
            jar=cookies.SimpleCookie();jar.load(self.headers.get('Cookie',''));token=jar.get('fish_records_session');token=token.value if token else ''
        except cookies.CookieError:return False
        return bool(token and c.execute('SELECT 1 FROM sessions WHERE token_hash=? AND expires_at>?',(digest(token),time.time())).fetchone())
    def do_GET(self):self.handle_request('GET')
    def do_POST(self):self.handle_request('POST')
    def do_PUT(self):self.handle_request('PUT')
    def do_DELETE(self):self.handle_request('DELETE')
    def handle_request(self,method):
        try:self.dispatch(method)
        except (ValueError,KeyError,TypeError,OverflowError) as e:self.send_json(400,{'error':str(e) or '输入有误'})
        except (BrokenPipeError,ConnectionResetError):pass
        except Exception:
            self.send_json(500,{'error':'暂时保存失败，请稍后重试；现有记录未丢失'})
    def dispatch(self,method):
        path=urlsplit(self.path).path
        if not path.startswith(PREFIX):return self.send_json(404,{'error':'页面不存在'})
        path=path[len(PREFIX):]
        if method=='GET':
            with database() as c:
                if path=='session':return self.send_json(200,{'authenticated':self.authenticated(c),'initialized':bool(config(c,'password_hash'))})
                if path=='state':
                    tanks=[]
                    for row in c.execute('SELECT * FROM tanks ORDER BY CASE id WHEN "qt" THEN 0 ELSE 1 END'):
                        tank=dict(row);records=[unpack(x) for x in c.execute('SELECT * FROM records WHERE tank=? AND deleted_at IS NULL ORDER BY observed_at,id',(tank['id'],))]
                        tanks.append({**tank,'records':records,'analysis':advice(tank,records)})
                    return self.send_json(200,{'tanks':tanks,'rules':RULES,'server_time':now()})
                return self.send_json(404,{'error':'接口不存在'})
        if not DEV and (self.headers.get('X-Forwarded-Proto')!='https' or self.headers.get('Host')!=urlsplit(ORIGIN).netloc):return self.send_json(403,{'error':'请使用https://dystudio.fun/fish/记录；HTTP入口只供查看'})
        if self.headers.get('Origin')!=ORIGIN:return self.send_json(403,{'error':'写入来源不正确，请刷新网页'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.send_json(415,{'error':'请从记录页提交'})
        size=int(self.headers.get('Content-Length','0'))
        if size<0 or size>16384:return self.send_json(413,{'error':'记录过长'})
        self.connection.settimeout(15)
        try:body=json.loads(self.rfile.read(size) or b'{}')
        except (json.JSONDecodeError,UnicodeDecodeError):raise ValueError('提交格式无效')
        if not isinstance(body,dict):raise ValueError('提交格式无效')
        with database() as c:
            if method=='POST' and path in ['login','setup']:
                ip=self.headers.get('X-Real-IP',self.client_address[0])
                with RATE_LOCK:
                    recent=[t for t in RATE.get(ip,[]) if t>time.time()-900];RATE[ip]=recent
                    if len(recent)>=10:return self.send_json(429,{'error':'尝试次数较多，15分钟后再试'})
                password=body.get('password','')
                if not isinstance(password,str) or not 9<=len(password)<=128:raise ValueError('密码须为9～128个字符')
                valid=False
                if path=='setup':
                    if config(c,'password_hash'):return self.send_json(409,{'error':'已设置密码，请直接登录'})
                    token=body.get('token','')
                    valid=isinstance(token,str) and hmac.compare_digest(digest(token),config(c,'setup_hash') or '') and float(config(c,'setup_expires') or '0')>time.time()
                    if valid:
                        salt=secrets.token_hex(16)
                        c.execute('INSERT INTO config VALUES(?,?)',('password_salt',salt));c.execute('INSERT INTO config VALUES(?,?)',('password_hash',password_hash(password,salt)));c.execute('DELETE FROM config WHERE key IN ("setup_hash","setup_expires")')
                else:
                    salt=config(c,'password_salt');stored=config(c,'password_hash')
                    valid=bool(salt and stored and hmac.compare_digest(password_hash(password,salt),stored))
                if not valid:
                    with RATE_LOCK:RATE[ip].append(time.time())
                    return self.send_json(401,{'error':'密码或首次设置链接无效，请核对'})
                token=secrets.token_urlsafe(32);session(c,token);return self.send_json(200,{'ok':True},self.cookie(token))
            if not self.authenticated(c):return self.send_json(401,{'error':'请先输入写入密码'})
            if method=='POST' and path=='logout':
                jar=cookies.SimpleCookie(self.headers.get('Cookie',''));c.execute('DELETE FROM sessions WHERE token_hash=?',(digest(jar['fish_records_session'].value),));return self.send_json(200,{'ok':True},self.cookie('',True))
            if method=='PUT' and path.startswith('tanks/'):
                tid=path.split('/')[-1];tank=c.execute('SELECT * FROM tanks WHERE id=?',(tid,)).fetchone()
                if not tank:raise ValueError('缸的选择无效')
                phase=body.get('phase',tank['phase']);volume=body.get('volume_l',tank['volume_l'])
                if phase not in ['cycling','animals']:raise ValueError('阶段无效')
                if volume is not None and (isinstance(volume,bool) or not isinstance(volume,(float,int)) or not math.isfinite(volume) or not 0<volume<=10000):raise ValueError('水量须为大于0的实际升数')
                cycle=secrets.token_hex(12) if phase!=tank['phase'] else tank['cycle_id']
                c.execute('UPDATE tanks SET phase=?,volume_l=?,cycle_id=?,updated_at=? WHERE id=?',(phase,volume,cycle,now(),tid));c.execute('INSERT INTO audit(at,action,record_id,payload) VALUES(?,?,?,?)',(now(),'tank',tid,json.dumps(body,ensure_ascii=False)));return self.send_json(200,{'ok':True})
            rid=path.split('/')[-1] if path.startswith('records/') else None
            old=c.execute('SELECT * FROM records WHERE id=? AND deleted_at IS NULL',(rid,)).fetchone() if rid else None
            if method=='DELETE' and old:
                c.execute('UPDATE records SET deleted_at=? WHERE id=?',(now(),rid));c.execute('INSERT INTO audit(at,action,record_id,payload) VALUES(?,?,?,?)',(now(),'delete',rid,old['payload']));return self.send_json(200,{'ok':True})
            if (method=='POST' and path=='records') or (method=='PUT' and old):
                p=validate_record(body);tank=c.execute('SELECT * FROM tanks WHERE id=?',(p['tank'],)).fetchone()
                client_id=body.get('client_id')
                if client_id is not None and (not isinstance(client_id,str) or not re.fullmatch(r'[a-zA-Z0-9-]{12,64}',client_id)):raise ValueError('记录编号无效，请刷新后重试')
                if method=='POST' and client_id:
                    saved=c.execute('SELECT * FROM records WHERE id=?',(client_id,)).fetchone()
                    if saved:
                        if saved['deleted_at'] is None and json.loads(saved['payload'])==p:return self.send_json(200,{'ok':True,'id':saved['id']})
                        return self.send_json(409,{'error':'这笔记录已保存，请刷新后修改原记录'})
                if old and old['tank']!=p['tank']:raise ValueError('不能把记录移到另一个缸')
                phase=old['phase'] if old else tank['phase'];cycle=old['cycle_id'] if old else tank['cycle_id']
                if phase=='animals' and p['actions'].get('ammonium_ml',0)>0:raise ValueError('有鱼或有动物时不可加氯化铵水')
                if p['actions'].get('water_change_l',0)>0 and tank['volume_l'] and p['actions']['water_change_l']>tank['volume_l']:raise ValueError('换水升数超过该缸设置的水量')
                rid=old['id'] if old else client_id or secrets.token_hex(12);payload=json.dumps(p,ensure_ascii=False)
                if old:c.execute('UPDATE records SET observed_at=?,payload=?,updated_at=? WHERE id=?',(p['observed_at'],payload,now(),rid))
                else:c.execute('INSERT INTO records VALUES(?,?,?,?,?,?,?,?,NULL)',(rid,p['tank'],p['observed_at'],phase,cycle,payload,now(),now()))
                c.execute('INSERT INTO audit(at,action,record_id,payload) VALUES(?,?,?,?)',(now(),'edit' if old else 'create',rid,old['payload'] if old else payload));return self.send_json(200,{'ok':True,'id':rid})
            return self.send_json(404,{'error':'接口或记录不存在'})

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8766);p.add_argument('--setup-token',action='store_true');p.add_argument('--backup',type=Path);args=p.parse_args();initialize()
    if args.backup:
        args.backup.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(DB) as source,sqlite3.connect(args.backup) as target:source.backup(target)
        os.chmod(args.backup,0o600);print('数据库备份完成');return
    if args.setup_token:
        with database() as c:
            if config(c,'password_hash'):print(json.dumps({'initialized':True}));return
            token=secrets.token_urlsafe(32)
            c.execute('INSERT OR REPLACE INTO config VALUES(?,?)',('setup_hash',digest(token)));c.execute('INSERT OR REPLACE INTO config VALUES(?,?)',('setup_expires',str(time.time()+7*86400)))
        print(json.dumps({'initialized':False,'setup_token':token}));return
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler);server.daemon_threads=True
    print(f'Fish records listening on 127.0.0.1:{args.port}',flush=True);server.serve_forever()
if __name__=='__main__':main()
