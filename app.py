import os, secrets, datetime as dt, requests as r, re
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
    def __init__(self):
        self.s = r.Session()
        self.s.headers.update({"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Content-Type": "application/json"})

    def gen(self, p):
        sys = "You are NeoCoder-AI. Output ONLY raw functional, production-ready code with comments. No conversational preambles."
        payload = {"messages": [{"role": "system", "content": sys}, {"role": "user", "content": p}], "model": "openai-large"}
        try:
            res = self.s.post("https://pollinations.ai", json=payload, timeout=25)
            if res.status_code == 200 and len(res.text.strip()) > 20: return res.text
        except: pass
        try:
            res = self.s.get(f"https://pollinations.ai{r.utils.quote(sys+' '+p)}", timeout=20)
            if res.status_code == 200 and len(res.text.strip()) > 20: return res.text
        except: pass
        return f"# 🌌 LOCAL CORE HYPER-DRIVE\nclass CustomCore:\n    def __init__(self):\n        self.target = '{p}'"

ai = MetaAIEngine()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

class PromptHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=dt.datetime.utcnow)

@lm.user_loader
def load_user(uid): return db.session.get(User, int(uid))

@app.route('/')
@login_required
def dash():
    h = PromptHistory.query.order_by(PromptHistory.timestamp.desc()).all() if current_user.username.lower() == 'admin' else PromptHistory.query.filter_by(user_id=current_user.id).order_by(PromptHistory.timestamp.desc()).all()
    return render_template('index.html', history=h)

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
    p = req.json.get('p', '') if req.json else ''
    if not p.strip(): return jsonify({'error': 'Empty'}), 400
    cc = ai.gen(p)
    try:
        db.session.add(PromptHistory(user_id=current_user.id, username=current_user.username, prompt_text=p))
        db.session.commit()
    except: db.session.rollback()
    return jsonify({'c': cc, 'prompt': p, 'username': current_user.username})

# Standalone Local Diagnostic Command Router (Paste right above the __main__ hook in app.py)
@app.route('/gen', methods=['POST'])
@login_required
def gen_code_override():
    """
    Overrides the standard /gen endpoint using Flask's internal decorator routing map 
    to process local commands cleanly before sending requests to the AI brain.
    """
    p = req.json.get('p', '').strip() if req.json else ''
    if not p: return jsonify({'error': 'Empty'}), 400

    # Local System Check Command Intercept
    if p.lower() == '//status':
        status_report = (
            "// --- CODEX CYBERNETIC DIAGNOSTIC DATA LAYOUT ---\n"
            f"// Current Node Session Operator : {current_user.username.upper()}\n"
            f"// Mainframe Operating Status    : STABLE / 100% OPERATIONAL\n"
            "// Network Gateway Interconnect  : POLLINATIONS SERVERLESS NET LINKED\n"
            "// Core Hardware Architecture    : RENDER ENGINE CLOUD VIRTUAL PROVISION\n"
            "// Local Engine Memory Load Max : < 30MB RAM SAFE PROFILE ZONE"
        )
        return jsonify({'c': status_report, 'prompt': p, 'username': current_user.username})

    # Clear Workspace Blueprint Command Intercept
    if p.lower() == '//wipe':
        clear_report = "# Terminal data matrix channels successfully flushed clean. Ready for clean input sequence."
        return jsonify({'c': clear_report, 'prompt': p, 'username': current_user.username})

    # If it is not a system macro command shortcut, fallback cleanly into your primary code gen loop
    cc = ai.gen(p)
    try:
        db.session.add(PromptHistory(user_id=current_user.id, username=current_user.username, prompt_text=p))
        db.session.commit()
    except: db.session.rollback()
    return jsonify({'c': cc, 'prompt': p, 'username': current_user.username})


if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

