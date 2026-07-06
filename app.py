import os, secrets, datetime as dt, re
from flask import Flask, render_template, request as req, redirect as red, url_for as url, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash as gh, check_password_hash as ch

SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(16))
B_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.update(
    SECRET_KEY=SECRET_KEY, 
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(B_DIR, 'supreme.db'), 
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
db = SQLAlchemy(app); lm = LoginManager(app); lm.login_view = 'login'

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
    if current_user.username.lower() == 'admin':
        h = PromptHistory.query.order_by(PromptHistory.timestamp.desc()).all()
    else:
        h = PromptHistory.query.filter_by(user_id=current_user.id).order_by(PromptHistory.timestamp.desc()).all()
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
    try:
        db.session.add(PromptHistory(user_id=current_user.id, username=current_user.username, prompt_text=p))
        db.session.commit()
    except: 
        db.session.rollback()
    return jsonify({'status': 'logged', 'prompt': p, 'username': current_user.username})

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

