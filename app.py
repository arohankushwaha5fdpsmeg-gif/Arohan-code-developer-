import os,secrets,datetime as dt,time,requests as r,stripe
from flask import Flask,render_template,request as req,redirect as red,url_for as url,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash as gh,check_password_hash as ch

SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(16))
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "sk_test_placeholder")

app=Flask(__name__)
app.config.update(SECRET_KEY=SECRET_KEY,SQLALCHEMY_DATABASE_URI='sqlite:////tmp/s.db',SQLALCHEMY_TRACK_MODIFICATIONS=False)
db=SQLAlchemy(app);lm=LoginManager(app);lm.login_view='login'

E_URL="https://onrender.com"
stripe.api_key=STRIPE_SECRET_KEY

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True);username=db.Column(db.String(150),unique=True,nullable=False);password=db.Column(db.String(256),nullable=False)
    tokens=db.Column(db.Integer,default=15);is_premium=db.Column(db.Boolean,default=False);is_premium_plus=db.Column(db.Boolean,default=False);last_reset=db.Column(db.DateTime,default=dt.datetime.utcnow)

@lm.user_loader
def load_user(uid):return db.session.get(User,int(uid))

def v_tok(u):
    if u.is_premium or u.is_premium_plus:return
    now=dt.datetime.utcnow()
    if u.last_reset is None:u.last_reset=now;db.session.commit()
    if (now-u.last_reset).total_seconds()/3600.0>=24.0:u.tokens=15;u.last_reset=now;db.session.commit()

@app.route('/')
@login_required
def dash():v_tok(current_user);return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if req.method=='POST':
        u,p=req.form.get('u'),req.form.get('p')
        if User.query.filter_by(username=u).first():flash('Identity path occupied.');return red(url('register'))
        n=User(username=u,password=gh(p,method='scrypt'));db.session.add(n);db.session.commit();login_user(n);return red(url('dash'))
    return render_template('portal.html',t="Register")

@app.route('/login',methods=['GET','POST'])
def login():
    if req.method=='POST':
        u_name,p_plain=req.form.get('u'),req.form.get('p')
        u=User.query.filter_by(username=u_name).first()
        if not u:
            u=User(username=u_name,password=gh(p_plain,method='scrypt'));db.session.add(u);db.session.commit()
        if ch(u.password,p_plain):login_user(u);return red(url('dash'))
        flash('Invalid credentials.')
    return render_template('portal.html',t="Login")

@app.route('/logout')
@login_required
def logout():logout_user();return red(url('login'))

@app.route('/gen',methods=['POST'])
@login_required
def gen_code():
    v_tok(current_user)
    if current_user.tokens<=0 and not current_user.is_premium and not current_user.is_premium_plus:return jsonify({'message':'Compute tokens exhausted.'}),402
    p,cc=req.json.get('p','') if req.json else '',None
    for _ in range(2):
        try:
            res=r.post(E_URL+"/compute",json={'prompt':p},timeout=15)
            if res.status_code==200:
                cc=res.json().get('code')
                if cc:break
        except:time.sleep(2)
    if not cc:cc="# CodeX Core Engine waking up from deep server hibernation.\\n# Please re-trigger the verification run execution button in 10 seconds."
    if not current_user.is_premium and not current_user.is_premium_plus and "waking up" not in cc:
        current_user.tokens-=1;db.session.commit()
    return jsonify({'c':cc,'r':current_user.tokens})

def create_checkout(name,amt,tier):
    s=stripe.checkout.Session.create(line_items=[{ 'price_data':{ 'currency':'usd','product_data':{ 'name':name},'unit_amount':amt},'quantity':1}],mode='payment',success_url=req.host_url,cancel_url=req.host_url,customer_email=current_user.username,metadata={ 'tier':tier})
    return red(s.url,code=303)

@app.route('/pay/premium',methods=['POST'])
@login_required
def pay_premium():return create_checkout('Premium Access',2500,'premium')

@app.route('/pay/plus',methods=['POST'])
@login_required
def pay_plus():return create_checkout('Premium Plus Access',4900,'plus')

if __name__=='__main__':
    with app.app_context():db.create_all()
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
