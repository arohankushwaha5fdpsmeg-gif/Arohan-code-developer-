import os,secrets,datetime as dt,re,sqlite3
from flask import Flask,render_template_string as rt,request as req,redirect as red,url_for as url,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash as gh,check_password_hash as ch

app=Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY',secrets.token_hex(16)),SQLALCHEMY_DATABASE_URI='sqlite:///supreme.db',SQLALCHEMY_TRACK_MODIFICATIONS=False)
db=SQLAlchemy(app);lm=LoginManager(app);lm.login_view='login'

class LocalAI:
    def __init__(self):
        self.kb={
            "calculator":"def calculator():\\n    n1,n2=float(input('N1: ')),float(input('N2: '))\n    return n1+n2",
            "logic":"def logic():\\n    return [x for x in range(100) if x%2==0]",
            "loop":"for i in range(1,11): print(f'Loop Step: {i}')",
            "server":"from flask import Flask\\napp=Flask(__name__)\\napp.run(port=5000)"
        }
    def gen(self,p):
        q=re.sub(r'[^\w\s]','',p).lower().strip()
        for k,src in self.kb.items():
            if k in q or q in k:return f"# CodeX Engine Output\\n\\n"+src
        return f"# CodeX Engine Output\\n\\nclass Pipeline:\\n    def run(self): return '{p}'"

ai=LocalAI()

H="""<!DOCTYPE html><html><head><meta charset='UTF-8'><title>CodeX AI</title><style>:root{--bg:#030408;--panel:rgba(10,12,18,0.8);--neon:#00f2fe;--p:#ff007a;--t:#e2e8f0;}body{font-family:monospace;background:var(--bg);color:var(--t);margin:0;height:100vh;display:flex;flex-direction:column;overflow:hidden;position:relative;}body::before{content:'';position:absolute;top:0;left:0;width:100%;height:100%;background:radial-gradient(circle at 30% 20%,rgba(0,242,254,0.12) 0%,transparent 40%),radial-gradient(circle at 70% 80%,rgba(255,0,122,0.08) 0%,transparent 45%);z-index:-1;animation:pulse 8s infinite alternate;}@keyframes pulse{0%{opacity:0.7;}100%{opacity:1;}}header{background:var(--panel);backdrop-filter:blur(20px);padding:10px 20px;display:flex;justify-content:space-between;align-items:center;}.b{font-weight:700;font-size:16px;background:linear-gradient(135deg,var(--neon),var(--p));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}.w{display:flex;flex:1;height:calc(100vh - 55px);}.l,.r{flex:1;display:flex;flex-direction:column;padding:15px;box-sizing:border-box;}textarea{flex:1;padding:15px;background:rgba(5,6,10,0.85);color:#34d399;border:1px solid rgba(0,242,254,0.15);border-radius:8px;outline:none;font-family:inherit;}button{padding:12px;background:linear-gradient(135deg,var(--neon),#7928ca);border:none;font-weight:700;border-radius:6px;cursor:pointer;}pre{flex:1;margin:0;background:rgba(3,4,6,0.9);padding:15px;color:#a7f3d0;overflow:auto;border-radius:6px;white-space:pre-wrap;border:1px solid rgba(255,255,255,0.03);}.lo{color:#ef4444;text-decoration:none;font-size:12px;padding:4px 8px;background:rgba(239,68,68,0.05);border-radius:4px;}</style></head><body><header><div class='b'>CodeX Terminal 🌌</div><div style='display:flex;align-items:center;gap:12px;'><div style='font-size:12px;'>User: <b>{{current_user.username}}</b> | Quota: <span style='color:var(--neon);'><span id='tc'>{{current_user.tokens}}</span>/15 Tok</span></div><a href='/logout' class='lo'>Exit</a></div></header><div class='w'><div class='l'><textarea id='p' placeholder='Enter prompt... Press Enter.'></textarea><button onclick='g()' style='margin-top:10px;'>Execute ✨</button></div><div class='r'><pre id='o'># Standby...</pre><button onclick='cp()' style='margin-top:10px;background:#111;color:#fff;'>Copy 📋</button></div></div><script>document.getElementById('p').addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();g();}});function g(){const p=document.getElementById('p').value;if(!p.trim())return;const o=document.getElementById('o');o.innerText="# Processing...";fetch('/gen', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({p:p})}).then(r=>r.json()).then(d=>{if(d.c){o.innerText=d.c;const s=document.getElementById('tc');if(s)s.innerText=d.r;}});}function cp(){navigator.clipboard.writeText(document.getElementById('o').innerText);alert('Copied!');}</script></body></html>"""
P="""<!DOCTYPE html><html><head><title>Portal</title><meta charset='UTF-8'><style>body{font-family:sans-serif;background:#030407;position:relative;color:#fff;max-width:350px;margin:150px auto;padding:15px;height:100vh;overflow:hidden;}body::before{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle at 30% 30%,rgba(0,242,254,0.18) 0%,transparent 50%),radial-gradient(circle at 70% 70%,rgba(255,0,122,0.15) 0%,transparent 50%);z-index:-1;animation:spin 20s linear infinite;}@keyframes spin{100%{transform:rotate(360deg);}}.c{background:rgba(14,16,22,0.6);backdrop-filter:blur(30px);padding:30px;border-radius:14px;border:1px solid rgba(0,242,254,0.2);box-shadow:0 20px 50px rgba(0,242,254,0.15);}h2{text-align:center;background:linear-gradient(135deg,#00f2fe,#ff007a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-top:0;}input{width:100%;padding:13px;margin:8px 0;background:rgba(5,6,10,0.8);color:#fff;border:1px solid rgba(255,255,255,0.08);border-radius:8px;outline:none;}button{width:100%;padding:13px;background:linear-gradient(135deg,#00f2fe,#7928ca);border:none;font-weight:bold;border-radius:8px;cursor:pointer;margin-top:12px;}a{color:#00f2fe;text-decoration:none;display:block;text-align:center;margin-top:18px;font-size:13px;}</style></head><body><div class='c'><h2>CodeX {{t}}</h2>{%with m=get_flashed_messages()%}{%if m%}{%for msg in m%}<p style='color:#ff007a;text-align:center;font-size:12px;'>{{msg}}</p>{%endfor%}{%endif%}{%endwith%}<form method='POST'><input type='text' name='u' placeholder='Identifier' required><input type='password' name='p' placeholder='Access Key' required><button type='submit'>Verify</button></form>{%if t=='Login'%}<a href='/register'>Register</a>{%else%}<a href='/login'>Login</a>{%endif%}</div></body></html>"""

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True);username=db.Column(db.String(150),unique=True,nullable=False);password=db.Column(db.String(256),nullable=False)
    tokens=db.Column(db.Integer,default=15);last_reset=db.Column(db.DateTime,default=dt.datetime.utcnow)

@lm.user_loader
def load_user(uid):return db.session.get(User,int(uid))

def v_tok(u):
    now=dt.datetime.utcnow()
    if u.last_reset is None:u.last_reset=now;db.session.commit()
    if (now-u.last_reset).total_seconds()/3600.0>=24.0:u.tokens=15;u.last_reset=now;db.session.commit()

@app.route('/')
@login_required
def dash():v_tok(current_user);return rt(H)

@app.route('/register',methods=['GET','POST'])
def register():
    if req.method=='POST':
        u,p=req.form.get('u'),req.form.get('p')
        if User.query.filter_by(username=u).first():flash('Occupied.');return red(url('register'))
        n=User(username=u,password=gh(p,method='scrypt'));db.session.add(n);db.session.commit();login_user(n);return red(url('dash'))
    return rt(P,t="Register")

@app.route('/login',methods=['GET','POST'])
def login():
    if req.method=='POST':
        u_name,p_plain=req.form.get('u'),req.form.get('p')
        u=User.query.filter_by(username=u_name).first()
        if not u:
            u=User(username=u_name,password=gh(p_plain,method='scrypt'));db.session.add(u);db.session.commit()
        if u and ch(u.password,p_plain):login_user(u);return red(url('dash'))
        flash('Invalid Access.')
    return rt(P,t="Login")

@app.route('/logout')
@login_required
def logout():logout_user();return red(url('login'))

@app.route('/gen',methods=['POST'])
@login_required
def gen_code():
    v_tok(current_user)
    if current_user.tokens<=0:return jsonify({'message':'Exhausted.'}),402
    p=req.json.get('p','') if req.json else ''
    cc=ai.gen(p)
    current_user.tokens-=1;db.session.commit()
    return jsonify({'c':cc,'r':current_user.tokens})

if __name__=='__main__':
    with app.app_context():db.create_all()
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))

