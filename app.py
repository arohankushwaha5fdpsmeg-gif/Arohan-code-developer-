import os,secrets,datetime as dt,time,requests as r
from flask import Flask,render_template_string as rt,request as req,redirect as red,url_for as url,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash as gh,check_password_hash as ch

SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(16))

app=Flask(__name__)
app.config.update(SECRET_KEY=SECRET_KEY,SQLALCHEMY_DATABASE_URI='sqlite:///supreme.db',SQLALCHEMY_TRACK_MODIFICATIONS=False)
db=SQLAlchemy(app);lm=LoginManager(app);lm.login_view='login'
E_URL="https://onrender.com"

H="""<!DOCTYPE html><html><head><meta charset='UTF-8'><title>CodeX AI Pro</title><style>:root{--bg:#030408;--panel:rgba(10,12,18,0.8);--border:rgba(0,242,254,0.15);--neon:#00f2fe;--p:#ff007a;--t:#e2e8f0;}body{font-family:monospace;background:var(--bg);color:var(--t);margin:0;height:100vh;display:flex;flex-direction:column;overflow:hidden;position:relative;}body::before{content:'';position:absolute;top:0;left:0;width:100%;height:100%;background:radial-gradient(circle at 30% 20%,rgba(0,242,254,0.12) 0%,transparent 40%),radial-gradient(circle at 70% 80%,rgba(255,0,122,0.08) 0%,transparent 45%);z-index:-1;animation:pulse 8s ease-in-out infinite alternate;}@keyframes pulse{0%{opacity:0.7;transform:scale(1);}100%{opacity:1;transform:scale(1.05);}}header{background:var(--panel);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,0.05);padding:10px 20px;display:flex;justify-content:space-between;align-items:center;z-index:10;}.b{font-weight:700;font-size:16px;background:linear-gradient(135deg,var(--neon),var(--p));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}.w{display:flex;flex:1;height:calc(100vh - 55px);}.l,.r{flex:1;display:flex;flex-direction:column;padding:15px;box-sizing:border-box;}.l{border-right:1px solid rgba(255,255,255,0.05);}textarea{flex:1;padding:15px;background:rgba(5,6,10,0.85);backdrop-filter:blur(10px);color:#34d399;border:1px solid var(--border);border-radius:8px;font-family:inherit;font-size:14px;resize:none;outline:none;line-height:1.5;}textarea:focus{border-color:var(--neon);box-shadow:0 0 12px rgba(0,242,254,0.25);}.bar{margin-top:10px;display:flex;gap:10px;}button{padding:12px 20px;background:linear-gradient(135deg,var(--neon),#7928ca);border:none;font-weight:700;border-radius:6px;cursor:pointer;font-size:14px;transition:0.2s;}button:hover{transform:translateY(-1px);box-shadow:0 5px 15px rgba(0,242,254,0.3);}.cb{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);color:#fff;}pre{flex:1;margin:0;background:rgba(3,4,6,0.9);backdrop-filter:blur(10px);padding:15px;color:#a7f3d0;overflow:auto;border-radius:6px;white-space:pre-wrap;border:1px solid rgba(255,255,255,0.03);line-height:1.5;}.lo{color:#ef4444;text-decoration:none;font-size:12px;padding:4px 8px;background:rgba(239,68,68,0.05);border-radius:4px;border:1px solid rgba(239,68,68,0.15);}</style></head><body><header><div class='b'>CodeX Quantum AI Terminal 🌌</div><div style='display:flex;align-items:center;gap:12px;'><div style='font-size:12px;'>User: <b>{{current_user.username}}</b> | Compute Quota: <span style='color:var(--neon);font-weight:bold;'><span id='tc'>{{current_user.tokens}}</span>/15 Free Tokens</span></div><a href='/logout' class='lo'>Exit Portal</a></div></header><div class='w'><div class='l'><textarea id='p' placeholder='# Enter computational prompts... Press Enter to Execute.'></textarea><div class='bar'><button onclick='g()' style='width:100%;'>Execute Runtime Array (Enter) ✨</button></div></div><div class='r'><pre id='o'># CodeX Engine Standby... Awaiting core instruction sequences.</pre><div class='bar'><button onclick='cp()' class='cb' style='width:100%; margin-top:10px;'>Copy Output Matrix Data 📋</button></div></div></div><script>document.getElementById('p').addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();g();}});function g(){const p=document.getElementById('p').value;if(!p.trim())return;const o=document.getElementById('o');o.innerText="# Initiating data pipelines...\\n# Fetching cluster compilation paths... ";fetch('/gen',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({p:p})}).then(r=>r.json()).then(d=>{if(d.c){o.innerText=d.c;const s=document.getElementById('tc');if(s&&d.r!==undefined)s.innerText=d.r;}else{o.innerText=d.message;}}).catch(()=>{o.innerText='# Compilation Timeout. Please click execute button again.';});}function cp(){const t=document.getElementById('o').innerText;navigator.clipboard.writeText(t);alert('Matrix parameters copied!');}</script></body></html>"""
P="""<!DOCTYPE html><html><head><title>CodeX Gateway</title><meta charset='UTF-8'><style>body{font-family:sans-serif;background:#030407;position:relative;color:#fff;max-width:350px;margin:150px auto;padding:15px;height:100vh;overflow:hidden;}body::before{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle at 30% 30%,rgba(0,242,254,0.18) 0%,transparent 50%),radial-gradient(circle at 70% 70%,rgba(255,0,122,0.15) 0%,transparent 50%);z-index:-1;animation:spin 20s linear infinite;}@keyframes spin{100%{transform:rotate(360deg);}}.c{background:rgba(14,16,22,0.6);backdrop-filter:blur(30px);-webkit-backdrop-filter:blur(30px);padding:30px;border-radius:14px;border:1px solid rgba(0,242,254,0.2);box-shadow:0 20px 50px rgba(0,242,254,0.15);}h2{text-align:center;background:linear-gradient(135deg,#00f2fe,#ff007a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-top:0;font-size:22px;letter-spacing:0.5px;}input{width:100%;padding:13px;margin:8px 0;background:rgba(5,6,10,0.8);color:#fff;border:1px solid rgba(255,255,255,0.08);border-radius:8px;box-sizing:border-box;outline:none;font-size:14px;}input:focus{border-color:#00f2fe;box-shadow:0 0 10px rgba(0,242,254,0.2);}button{width:100%;padding:13px;background:linear-gradient(135deg,#00f2fe,#7928ca);border:none;font-weight:bold;color:#000;border-radius:8px;cursor:pointer;margin-top:12px;font-size:14px;}button:hover{opacity:0.95;box-shadow:0 0 15px rgba(0,242,254,0.4);}a{color:#00f2fe;text-decoration:none;display:block;text-align:center;margin-top:18px;font-size:13px;opacity:0.8;}</style></head><body><div class='c'><h2>CodeX Gate {{t}}</h2>{%with m=get_flashed_messages()%}{%if m%}{%for msg in m%}<p style='color:#ff007a;text-align:center;font-size:12px;margin:0 0 10px 0;'>{{msg}}</p>{%endfor%}{%endif%}{%endwith%}<form method='POST'><input type='text' name='u' placeholder='Account Identifier' required><input type='password' name='p' placeholder='Secret Access Key' required><button type='submit'>Authenticate Identity</button></form>{%if t=='Login'%}<a href='/register'>Register New Credentials</a>{%else%}<a href='/login'>Return to Gate Login</a>{%endif%}</div></body></html>"""

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
        if User.query.filter_by(username=u).first():flash('Identity path occupied.');return red(url('register'))
        n=User(username=u,password=gh(p,method='scrypt'));db.session.add(n);db.session.commit();login_user(n);return red(url('dash'))
    return rt(P,t="Register")

@app.route('/login',methods=['GET','POST'])
def login():
    if req.method=='POST':
        u_name,p_plain=req.form.get('u'),req.form.get('p')
        u=User.query.filter_by(username=u_name).first()
        if not u:
            u=User(username=u_name,password=gh(p_plain,method='scrypt'));db.session.add(u);db.session.commit()
        if ch(u.password,p_plain):login_user(u);return red(url('dash'))
        flash('Invalid credentials.')
    return rt(P,t="Login")

@app.route('/logout')
@login_required
def logout():logout_user();return red(url('login'))

@app.route('/gen',methods=['POST'])
@login_required
def gen_code():
    v_tok(current_user)
    if current_user.tokens<=0:return jsonify({'message':'Compute tokens exhausted.'}),402
    p,cc=req.json.get('p','') if req.json else '',None
    for _ in range(2):
        try:
            res=r.post(E_URL+"/compute",json={'prompt':p},timeout=15)
            if res.status_code==200:
                cc=res.json().get('code')
                if cc:break
        except:time.sleep(2)
    if not cc:cc="# CodeX Core Engine waking up from deep server hibernation.\\n# Please re-trigger the verification run execution button in 10 seconds."
    if "waking up" not in cc:
        current_user.tokens-=1;db.session.commit()
    return jsonify({'c':cc,'r':current_user.tokens})

if __name__=='__main__':
    with app.app_context():db.create_all()
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
