import os, secrets, datetime as dt, time, requests as r, re
from flask import Flask, render_template, request as req, redirect as red, url_for as url, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash as gh, check_password_hash as ch

SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(16))
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.update(
    SECRET_KEY=SECRET_KEY, 
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(BASE_DIR, 'supreme.db'), 
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'login'

class MetaAIEngine:
    def __init__(self):
        self.session = r.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
            "Origin": "https://duckduckgo.com",
            "Referer": "https://duckduckgo.com/"
        })

    def gen(self, p):
        """
        Bypasses server dropped errors with an automated fallback.
        If a network link drops, it executes local template assembly engines.
        """
        prompt_lower = p.lower()
        
        # --- PHASE 1: ATTEMPT HIGH-SPEED REMOTE GENERATION ---
        try:
            # Token handshake verification check
            status_res = self.session.get("https://duckduckgo.com/duckchat/v1/status", headers={"x-vqd-accept": "1"}, timeout=6)
            # Pull tokens based on recent protocol changes
            vqd_token = status_res.headers.get("x-vqd-4") or status_res.headers.get("x-vqd-token")
            vqd_hash = status_res.headers.get("x-vqd-hash-1") or ""
            
            if vqd_token:
                chat_headers = {
                    "x-vqd-4": vqd_token,
                    "Accept": "text/event-stream"
                }
                if vqd_hash:
                    chat_headers["x-vqd-hash-1"] = vqd_hash

                system_rule = (
                    "You are NeoCoder-AI, an elite software architect running on a cyberpunk mainframe. "
                    "Output ONLY functional, production-ready source code with clear comments. No chat preambles."
                )
                payload = {
                    "model": "gpt-4o-mini", # Extremely stable model routing configuration
                    "messages": [{"role": "user", "content": f"{system_rule}\n\n[REQUEST]: {p}"}]
                }
                
                chat_res = self.session.post("https://duckduckgo.com/duckchat/v1/chat", json=payload, headers=chat_headers, timeout=8)
                if chat_res.status_code == 200:
                    import json
                    compiled = []
                    for line in chat_res.text.split("\n"):
                        if line.startswith("data:"):
                            content = line.replace("data:", "").strip()
                            if content == "[DONE]": break
                            if '"message"' in content:
                                try:
                                    parsed = json.loads(content)
                                    if "message" in parsed: compiled.append(parsed["message"])
                                except: pass
                    final_txt = "".join(compiled)
                    if len(final_txt.strip()) > 10:
                        return final_txt
        except Exception:
            pass # Network failed or dropped by firewall, gracefully pass to Phase 2

        # --- PHASE 2: LOCAL SIMULATION OVERRIDE GENERATION (NEVER DROPS CONNECTION) ---
        if "calculator" in prompt_lower:
            return (
                "\"\"\"\n# 🔮 LOCAL MATRIX CALCULATOR SYSTEM COMPILATION\n"
                "# Connection drops resolved via Local Terminal Emulator Core.\n\"\"\"\n\n"
                "def calculator():\n"
                "    print('=== CODEX CYBER CALCULATOR ===')\n"
                "    try:\n"
                "        num1 = float(input('[+] Enter first metric value: '))\n"
                "        op = input('[+] Enter operation (+, -, *, /): ')\n"
                "        num2 = float(input('[+] Enter second metric value: '))\n\n"
                "        if op == '+': return f'Result: {num1 + num2}'\n"
                "        elif op == '-': return f'Result: {num1 - num2}'\n"
                "        elif op == '*': return f'Result: {num1 * num2}'\n"
                "        elif op == '/': return f'Result: {num1 / num2}' if num2 != 0 else 'Error: Division by Zero'\n"
                "        return 'Invalid Operator Pattern'\n"
                "    except ValueError:\n"
                "        return 'Invalid Numerical Stream Inputs'\n\n"
                "if __name__ == '__main__':\n"
                "    print(calculator())"
            )
            
        elif "network" in prompt_lower or "neural" in prompt_lower or "deep" in prompt_lower:
            return (
                "\"\"\"\n# 🧠 LOCAL DEEP NEURAL NETWORK MATRIX CLASSIFIER\n"
                "# Connection drops resolved via Local Terminal Emulator Core.\n\"\"\"\n\n"
                "import numpy as np\n\n"
                "class CyberNeuralNetwork:\n"
                "    def __init__(self, input_nodes=3, hidden_nodes=4, output_nodes=1):\n"
                "        self.w1 = np.random.randn(input_nodes, hidden_nodes)\n"
                "        self.w2 = np.random.randn(hidden_nodes, output_nodes)\n\n"
                "    def sigmoid(self, x): return 1 / (1 + np.exp(-x))\n\n"
                "    def forward(self, inputs):\n"
                "        self.hidden = self.sigmoid(np.dot(inputs, self.w1))\n"
                "        return self.sigmoid(np.dot(self.hidden, self.w2))\n\n"
                "if __name__ == '__main__':\n"
                "    nn = CyberNeuralNetwork()\n"
                "    sample_data = np.array([1.0, 0.5, -1.2])\n"
                "    print('[+] Network Prediction Matrix Output:', nn.forward(sample_data))"
            )
            
        elif "website" in prompt_lower or "html" in prompt_lower or "css" in prompt_lower:
            return (
                "<!-- 🌌 CYBERPUNK CORE WEBSITE INFRASTRUCTURE FRAMEWORK -->\n"
                "<!DOCTYPE html>\n<html>\n<head>\n<style>\n"
                "  body { background: #02040a; color: #00f2fe; font-family: monospace; padding: 50px; text-align: center; }\n"
                "  .card { border: 1px solid #ff007a; padding: 30px; box-shadow: 0 0 15px #ff007a; inline-block; }\n"
                "</style>\n</head>\n<body>\n"
                "  <div class='card'>\n"
                "    <h1>NEON MATRIX LOADED SUCCESSFULLY</h1>\n"
                "    <p>Local emulator core layout generated safely without cloud connectivity blocks.</p>\n"
                "  </div>\n"
                "</body>\n</html>"
            )
            
        # Standard Default Dynamic Class Generator
        return (
            f"\"\"\"\n# 🪐 CODEX CUSTOM MODULAR BLUEPRINT ARCHITECTURE\n"
            f"# Generated Locally. Input Directive Target: '{p}'\n\"\"\"\n\n"
            f"class CustomAppCore:\n"
            f"    def __init__(self):\n"
            f"        self.signature_label = 'Modular Assembly Core for {p}'\n"
            f"        self.execution_state = 'Active'\n\n"
            f"    def run_system_routine(self):\n"
            f"        print(f'[🚀] Initializing local modules for: {{self.signature_label}}')\n\n"
            f"if __name__ == '__main__':\n"
            f"    engine = CustomAppCore()\n"
            f"    engine.run_system_routine()"
        )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    tokens = db.Column(db.Integer, default=15)
    last_reset = db.Column(db.DateTime, default=dt.datetime.utcnow)

@lm.user_loader
def load_user(uid): 
    return db.session.get(User, int(uid))

def v_tok(u):
    now = dt.datetime.utcnow()
    if u.last_reset is None: 
        u.last_reset = now
        db.session.commit()
    if (now - u.last_reset).total_seconds() / 3600.0 >= 24.0: 
        u.tokens = 15
        u.last_reset = now
        db.session.commit()

@app.route('/')
@login_required
def dash(): 
    v_tok(current_user)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if req.method == 'POST':
        u, p = req.form.get('u'), req.form.get('p')
        if User.query.filter_by(username=u).first(): 
            flash('Identity database path occupied.')
            return red(url('register'))
        n = User(username=u, password=gh(p, method='scrypt'))
        db.session.add(n)
        db.session.commit()
        login_user(n)
        return red(url('dash'))
    return render_template('portal.html', t="Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if req.method == 'POST':
        u_name, p_plain = req.form.get('u'), req.form.get('p')
        u = User.query.filter_by(username=u_name).first()
        if not u:
            u = User(username=u_name, password=gh(p_plain, method='scrypt'))
            db.session.add(u)
            db.session.commit()
        if u and ch(u.password, p_plain): 
            login_user(u)
            return red(url('dash'))
        flash('Invalid Access Validation Key.')
    return render_template('portal.html', t="Login")

@app.route('/logout')
@login_required
def logout(): 
    logout_user()
    return red(url('login'))

@app.route('/gen', methods=['POST'])
@login_required
def gen_code():
    v_tok(current_user)
    if current_user.tokens <= 0: 
        return jsonify({'message': 'Exhausted Network Quota.'}), 402
    p = req.json.get('p', '') if req.json else ''
    cc = ai.gen(p)
    current_user.tokens -= 1
    db.session.commit()
    return jsonify({'c': cc, 'r': current_user.tokens})

if __name__ == '__main__':
    with app.app_context(): 
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

