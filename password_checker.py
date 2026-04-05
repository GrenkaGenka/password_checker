#!/usr/bin/env python3
"""
Сервис проверки пароля по настраиваемым правилам.
Запуск: python password_checker.py
Откройте браузер: http://localhost:8080
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json, re, urllib.parse

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Проверка пароля</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Unbounded:wght@400;700&display=swap');

  :root {
    --bg: #0e0e11;
    --surface: #17171c;
    --border: #2a2a35;
    --accent: #7c6af7;
    --accent2: #f76a8a;
    --pass: #4ade80;
    --fail: #f87171;
    --text: #e8e8f0;
    --muted: #6b6b80;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    min-height: 100vh;
    padding: 40px 20px;
  }

  h1 {
    font-family: 'Unbounded', sans-serif;
    font-size: clamp(18px, 4vw, 28px);
    font-weight: 700;
    letter-spacing: -0.5px;
    margin-bottom: 8px;
  }

  .subtitle { font-size: 13px; color: var(--muted); margin-bottom: 36px; }

  .layout {
    max-width: 860px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }

  @media (max-width: 640px) { .layout { grid-template-columns: 1fr; } }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
  }

  .card h2 {
    font-family: 'Unbounded', sans-serif;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--muted);
    margin-bottom: 20px;
  }

  .field { margin-bottom: 16px; }

  label {
    display: block;
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 6px;
  }

  input[type=number], input[type=password], input[type=text] {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    outline: none;
    transition: border-color .15s;
  }

  input:focus { border-color: var(--accent); }

  .toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    user-select: none;
  }
  .toggle-row:last-child { border-bottom: none; }
  .toggle-label { font-size: 13px; }

  .toggle {
    width: 36px; height: 20px;
    background: var(--border);
    border-radius: 10px;
    position: relative;
    transition: background .2s;
    flex-shrink: 0;
  }
  .toggle.on { background: var(--accent); }
  .toggle::after {
    content: '';
    position: absolute;
    width: 14px; height: 14px;
    background: #fff;
    border-radius: 50%;
    top: 3px; left: 3px;
    transition: transform .2s;
  }
  .toggle.on::after { transform: translateX(16px); }

  .pwd-wrap { position: relative; }
  .pwd-wrap input { padding-right: 44px; }
  .eye-btn {
    position: absolute;
    right: 12px; top: 50%;
    transform: translateY(-50%);
    background: none; border: none;
    color: var(--muted); cursor: pointer;
    font-size: 16px; padding: 4px;
  }

  button.check-btn {
    width: 100%;
    padding: 14px;
    background: var(--accent);
    border: none;
    border-radius: 8px;
    color: #fff;
    font-family: 'Unbounded', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: .5px;
    cursor: pointer;
    transition: opacity .15s, transform .1s;
    margin-top: 8px;
  }
  button.check-btn:hover { opacity: .85; }
  button.check-btn:active { transform: scale(.98); }

  .result-card { display: none; }
  .result-card.visible { display: block; }

  .verdict {
    font-family: 'Unbounded', sans-serif;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
  }
  .verdict.pass { color: var(--pass); }
  .verdict.fail { color: var(--fail); }

  .rule-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
    line-height: 1.5;
  }
  .rule-item:last-child { border-bottom: none; }

  .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-top: 4px;
    flex-shrink: 0;
  }
  .dot.pass { background: var(--pass); }
  .dot.fail { background: var(--fail); }

  .rule-text { flex: 1; }
  .rule-status { font-size: 11px; font-weight: 600; }
  .rule-status.pass { color: var(--pass); }
  .rule-status.fail { color: var(--fail); }
</style>
</head>
<body>

<div style="max-width:860px;margin:0 auto 28px">
  <h1>// Проверка пароля</h1>
  <p class="subtitle">Настройте правила слева — введите пароль справа</p>
</div>

<div class="layout">

  <!-- Настройки -->
  <div>
    <div class="card" style="margin-bottom:20px">
      <h2>Числовые правила</h2>

      <div class="field">
        <label>Минимальная длина</label>
        <input type="number" id="minLen" value="8" min="0" max="128">
      </div>
      <div class="field">
        <label>Минимум цифр</label>
        <input type="number" id="minDigits" value="1" min="0" max="64">
      </div>
      <div class="field">
        <label>Минимум букв</label>
        <input type="number" id="minLetters" value="1" min="0" max="64">
      </div>
      <div class="field">
        <label>Минимум заглавных букв</label>
        <input type="number" id="minUpper" value="0" min="0" max="64">
      </div>
      <div class="field">
        <label>Минимум спецсимволов (!@#$...)</label>
        <input type="number" id="minSpec" value="0" min="0" max="64">
      </div>
      <div class="field">
        <label>Макс. одинаковых символов подряд (0 = выкл.)</label>
        <input type="number" id="maxRepeat" value="0" min="0" max="32">
      </div>
    </div>

    <div class="card">
      <h2>Запреты</h2>
      <div class="toggle-row" onclick="toggle('blockAlpha')">
        <span class="toggle-label">Алф. последовательности (abc, 123)</span>
        <div class="toggle" id="blockAlpha"></div>
      </div>
      <div class="toggle-row" onclick="toggle('blockKbd')">
        <span class="toggle-label">Клав. последовательности (qwer, qaz)</span>
        <div class="toggle" id="blockKbd"></div>
      </div>
      <div class="toggle-row" onclick="toggle('blockYear')">
        <span class="toggle-label">Год рождения (1900–2999)</span>
        <div class="toggle" id="blockYear"></div>
      </div>
    </div>
  </div>

  <!-- Проверка + результат -->
  <div>
    <div class="card" style="margin-bottom:20px">
      <h2>Пароль</h2>
      <div class="field">
        <label>Введите пароль</label>
        <div class="pwd-wrap">
          <input type="password" id="pwd" placeholder="••••••••••••" autocomplete="off">
          <button class="eye-btn" onclick="toggleEye()" id="eyeBtn">👁</button>
        </div>
      </div>
      <button class="check-btn" onclick="check()">Проверить →</button>
    </div>

    <div class="card result-card" id="resultCard">
      <div class="verdict" id="verdict"></div>
      <div id="rules"></div>
    </div>
  </div>

</div>

<script>
const toggles = { blockAlpha: false, blockKbd: false, blockYear: false };

function toggle(id) {
  toggles[id] = !toggles[id];
  document.getElementById(id).classList.toggle('on', toggles[id]);
}

function toggleEye() {
  const p = document.getElementById('pwd');
  p.type = p.type === 'password' ? 'text' : 'password';
}

async function check() {
  const params = {
    password:    document.getElementById('pwd').value,
    minLen:      +document.getElementById('minLen').value,
    minDigits:   +document.getElementById('minDigits').value,
    minLetters:  +document.getElementById('minLetters').value,
    minUpper:    +document.getElementById('minUpper').value,
    minSpec:     +document.getElementById('minSpec').value,
    maxRepeat:   +document.getElementById('maxRepeat').value,
    blockAlpha:  toggles.blockAlpha,
    blockKbd:    toggles.blockKbd,
    blockYear:   toggles.blockYear,
  };

  const res  = await fetch('/check', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(params) });
  const data = await res.json();

  const card = document.getElementById('resultCard');
  card.classList.add('visible');

  const vEl = document.getElementById('verdict');
  vEl.textContent = data.passed ? '✓ Пароль подходит' : '✗ Пароль не подходит';
  vEl.className = 'verdict ' + (data.passed ? 'pass' : 'fail');

  document.getElementById('rules').innerHTML = data.rules.map(r => `
    <div class="rule-item">
      <div class="dot ${r.ok ? 'pass' : 'fail'}"></div>
      <span class="rule-text">${r.label}</span>
      <span class="rule-status ${r.ok ? 'pass' : 'fail'}">${r.ok ? 'OK' : 'FAIL'}</span>
    </div>
  `).join('');
}

document.getElementById('pwd').addEventListener('keydown', e => { if(e.key === 'Enter') check(); });
</script>
</body>
</html>
"""

def check_password(data):
    pwd        = data.get("password", "")
    min_len    = int(data.get("minLen",     8))
    min_digits = int(data.get("minDigits",  1))
    min_letters= int(data.get("minLetters", 1))
    min_upper  = int(data.get("minUpper",   0))
    min_spec   = int(data.get("minSpec",    0))
    max_repeat = int(data.get("maxRepeat",  0))
    block_alpha= bool(data.get("blockAlpha", False))
    block_kbd  = bool(data.get("blockKbd",   False))
    block_year = bool(data.get("blockYear",  False))

    digits  = sum(c.isdigit()           for c in pwd)
    letters = sum(c.isalpha()           for c in pwd)
    upper   = sum(c.isupper()           for c in pwd)
    spec    = sum(not c.isalnum()       for c in pwd)

    rules = []

    def rule(label, ok):
        rules.append({"label": label, "ok": ok})

    rule(f"Длина ≥ {min_len} (сейчас: {len(pwd)})",           len(pwd) >= min_len)
    rule(f"Цифр ≥ {min_digits} (сейчас: {digits})",           digits  >= min_digits)
    rule(f"Букв ≥ {min_letters} (сейчас: {letters})",         letters >= min_letters)

    if min_upper > 0:
        rule(f"Заглавных ≥ {min_upper} (сейчас: {upper})",    upper >= min_upper)

    if min_spec > 0:
        rule(f"Спецсимволов ≥ {min_spec} (сейчас: {spec})",   spec  >= min_spec)

    if max_repeat > 0:
        max_run = max((len(list(g)) for _, g in __import__('itertools').groupby(pwd)), default=0)
        rule(f"Повторов подряд ≤ {max_repeat} (макс: {max_run})", max_run <= max_repeat)

    if block_alpha:
        sequences = ["abc","bcd","cde","def","efg","fgh","ghi","hij","ijk","jkl","klm",
                     "lmn","mno","nop","opq","pqr","qrs","rst","stu","tuv","uvw","vwx",
                     "wxy","xyz","cba","dcb","edc","fed","gfe","hgf","ihg","jih","kjh",
                     "123","234","345","456","567","678","789","321","432","543","654"]
        found = any(s in pwd.lower() for s in sequences)
        rule("Нет алф./цифр. последовательностей (abc, 123...)", not found)

    if block_kbd:
        kbd_seqs = ["qwer","wert","erty","rtyu","tyui","yuio","uiop",
                    "asdf","sdfg","dfgh","fghj","ghjk","hjkl",
                    "zxcv","xcvb","cvbn","vbnm",
                    "qaz","wsx","edc","rfv","tgb","yhn","ujm",
                    "qwerty","asdfgh","zxcvbn"]
        found = any(s in pwd.lower() for s in kbd_seqs)
        rule("Нет клав. последовательностей (qwer, qaz...)", not found)

    if block_year:
        found = bool(re.search(r'(19|2[0-9])\d{2}', pwd))
        rule("Нет года рождения (1900–2999)", not found)

    passed = all(r["ok"] for r in rules)
    return {"passed": passed, "rules": rules}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # отключить логи в консоль

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        if self.path != "/check":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        data   = json.loads(body)
        result = check_password(data)
        resp   = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(resp))
        self.end_headers()
        self.wfile.write(resp)


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    server = HTTPServer((HOST, PORT), Handler)
    print(f"Сервер запущен → http://{HOST}:{PORT}")
    print("Остановить: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")