import os, secrets, datetime as dt, re
from flask import Flask, render_template, request as req, redirect as red, url_for as url, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash as gh, check_password_hash as ch

SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(16))
B_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.update(SECRET_KEY=SECRET_KEY, SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(B_DIR, 'supreme.db'), SQLALCHEMY_TRACK_MODIFICATIONS=False)
db = SQLAlchemy(app); lm = LoginManager(app); lm.login_view = 'login'

class MetaAIEngine:
    def gen(self, p):
        q = re.sub(r'[^\w\s]', '', p).lower().strip()
        if "calculator" in q or "calc" in q or "math" in q:
            return "# 🔮 MATRIX CALCULATOR\nclass Calc:\n    def run(self):\n        n1 = float(input('Num 1: '))\n        op = input('Op (+,-,*,/): ')\n        n2 = float(input('Num 2: '))\n        if op=='+': print(n1+n2)\n        elif op=='-': print(n1-n2)\n        elif op=='*': print(n1*n2)\n        elif op=='/': print(n1/n2 if n2!=0 else 'Error')"
        elif "network" in q or "neural" in q or "deep" in q or "ai code" in q:
            return "# 🧠 DEEP NEURAL NETWORK MOCK TENSOR\nimport numpy as np\nclass CyberNN:\n    def __init__(self):\n        self.w = np.random.randn(3, 1)\n    def forward(self, x):\n        return 1 / (1 + np.exp(-np.dot(x, self.w)))\nprint('[+] Cyber Core Loaded.')"
        elif "website" in q or "html" in q or "css" in q:
            return "<!DOCTYPE html><html><head><style>body{background:#02040a;color:#00f2fe;font-family:monospace;padding:50px;text-align:center;}</style></head><body><h1>CYBER MAINFRAME ACTIVE</h1><p>Local build architecture compiled.</p></body></html>"
        elif "image" in q or "gan" in q or "vision" in q:
            return "# 🎨 IMAGE GENERATIVE PIPELINE\nclass ImageGen:\n    def render(self):\n        print('[+] Constructing canvas matrix layers...')\n        print('[Success] Render completed.')"
        return f"# 🪐 CODEX LOCAL COMPILER MATRIX\nclass CustomApp:\n    def __init__(self):\n        self.info = 'Local compilation for {p}'"

ai = MetaAIEngine()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    tokens = db.Column(db.Integer, default=15)
    last_reset = db.Column(db.DateTime, default=dt.datetime.utcnow)

@lm.user_loader
def load_user(uid): return db.session.get(User, int(uid))

def v_tok(u):
    now = dt.datetime.utcnow()
    if u.last_reset is None: u.last_reset = now; db.session.commit()
    if (now - u.last_reset).total_seconds() / 3600.0 >= 24.0: u.tokens = 15; u.last_reset = now; db.session.commit()

@app.route('/')
@login_required
def dash(): v_tok(current_user); return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if req.method == 'POST':
        u, p = req.form.get('u'), req.form.get('p')
        if User.query.filter_by(username=u).first(): flash('Occupied.'); return red(url('register'))
        n = User(username=u, password=gh(p, method='scrypt')); db.session.add(n); db.session.commit(); login_user(n); return red(url('dash'))
    return render_template('portal.html', t="Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if req.method == 'POST':
        u_name, p_plain = req.form.get('u'), req.form.get('p')
        u = User.query.filter_by(username=u_name).first()
        if not u: u = User(username=u_name, password=gh(p_plain, method='scrypt')); db.session.add(u); db.session.commit()
        if u and ch(u.password, p_plain): login_user(u); return red(url('dash'))
        flash('Invalid Access.')
    return render_template('portal.html', t="Login")

@app.route('/logout')
@login_required
def logout(): logout_user(); return red(url('login'))

@app.route('/gen', methods=['POST'])
@login_required
def gen_code():
    v_tok(current_user)
    if current_user.tokens <= 0: return jsonify({'message': 'Exhausted.'}), 402
    p = req.json.get('p', '') if req.json else ''
    cc = ai.gen(p)
    current_user.tokens -= 1; db.session.commit()
    return jsonify({'c': cc, 'r': current_user.tokens})

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

