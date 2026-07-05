import os,secrets,datetime as dt,time,requests as r,re
from flask import Flask,render_template,request as req,redirect as red,url_for as url,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash as gh,check_password_hash as ch

SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(16))

app=Flask(__name__)
app.config.update(SECRET_KEY=SECRET_KEY,SQLALCHEMY_DATABASE_URI='sqlite:///supreme.db',SQLALCHEMY_TRACK_MODIFICATIONS=False)
db=SQLAlchemy(app);lm=LoginManager(app);lm.login_view='login'

class MetaAIEngine:
    def __init__(self):
        self.ai_blueprints = {
            "image": '"""\\n# 🎨 PYTORCH CONVOLUTIONAL GAN FOR IMAGE GENERATION\\nimport torch\\nimport torch.nn as nn\\nclass Generator(nn.Module):\\n    def __init__(self, z_dim=100, img_channels=3, features_g=64):\\n        super(Generator, self).__init__()\\n        self.gen = nn.Sequential(\\n            nn.ConvTranspose2d(z_dim, features_g * 16, 4, 1, 0, bias=False),\\n            nn.BatchNorm2d(features_g * 16),\\n            nn.ReLU(True),\\n            nn.ConvTranspose2d(features_g * 16, features_g * 8, 4, 2, 1, bias=False),\\n            nn.BatchNorm2d(features_g * 8),\\n            nn.ReLU(True),\\n            nn.ConvTranspose2d(features_g * 8, img_channels, 4, 2, 1, bias=False),\\n            nn.Tanh()\\n        )\\n    def forward(self, x): return self.gen(x)\\nif __name__ == "__main__":\\n    print("[Success] Sub-AI image generator compiled successfully.")"""',
            "network": '"""\\n# 🧠 DEEP NEURAL NETWORK (MLP) CLASSIFIER MODEL\\nimport torch\\nimport torch.nn as nn\\nclass DeepNeuralNetwork(nn.Module):\\n    def __init__(self, input_size=784, hidden_size=256, num_classes=10):\\n        super(DeepNeuralNetwork, self).__init__()\\n        self.network = nn.Sequential(\\n            nn.Linear(input_size, hidden_size),\\n            nn.ReLU(),\\n            nn.Dropout(0.2),\\n            nn.Linear(hidden_size, num_classes)\\n        )\\n    def forward(self, x): return self.network(x)\\nif __name__ == "__main__":\\n    print("[Success] Deep Neural Network compiled successfully.")"""',
            "chatbot": '"""\\n# 💬 NLP CHATBOT MODEL ROUTINE VIA HUGGINGFACE\\nfrom transformers import AutoModelForCausalLM, AutoTokenizer\\nimport torch\\ndef execute_chat_loop(model_name="microsoft/DialoGPT-medium"):\\n    tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")\\n    model = AutoModelForCausalLM.from_pretrained(model_name)\\n    print("[Success] HuggingFace NLP pipeline compiled successfully.")"""'
        }
    def gen(self,p):
        q=re.sub(r'[^\w\s]','',p).lower().strip()
        if "image" in q or "generator" in q or "gan" in q: return self.ai_blueprints["image"]
        elif "network" in q or "neural" in q or "deep" in q: return self.ai_blueprints["network"]
        elif "chat" in q or "bot" in q or "nlp" in q or "language" in q: return self.ai_blueprints["chatbot"]
        words = q.split()
        target_name = words[-1] if words else "custom_model"
        if len(target_name) < 3: target_name = "custom_model"
        return f'"""\\n# 🌌 AUTONOMOUS SUB-SYSTEM ARRAY METRIC GENERATOR\\nclass {target_name.capitalize()}Core:\\n    def __init__(self): self.context = "{p}"\\nif __name__ == "__main__":\\n    print("[System Running] Initiated model arrays successfully.")"""'

ai=MetaAIEngine()

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
        if u and ch(u.password,p_plain):login_user(u);return red(url('dash'))
        flash('Invalid Access.')
    return render_template('portal.html',t="Login")

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
