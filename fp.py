from flask import Flask, request, render_template_string, redirect, session, url_for, send_from_directory, jsonify
import os
from datetime import datetime
import unicodedata
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

app = Flask(__name__)
app.secret_key = "chave_secreta_ponto_rh"

# =========================
# CONFIGURAÇÕES
# =========================
PROJETOS = ["FÁBRICA AQA", "BAYGORRIA", "BRACELL", "ARAUCO", "CERAN"]

# Configuração de e-mail — preencha com seus dados reais
EMAIL_CONFIG = {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "usuario": "kauanmarin16@gmail.com",       # e-mail remetente
    "senha": "rigr lnyn tels aqbf",           # senha de app do Gmail (não a senha normal)
    "destinatario_rh": "valcristinamarin@gmail.com",   # e-mail do RH
}

USUARIOS = {
    "kleiton.delfino": ("28956", "FÁBRICA AQA"),
    "fabricio.azevedo": ("27525", "FÁBRICA AQA"),
    "claudemar.nunes": ("27492", "FÁBRICA AQA"),
    "jonattas.macedo": ("29036", "FÁBRICA AQA"),
    "gleuvailton.marques": ("27529", "FÁBRICA AQA"),
    "carlos.antonio": ("27529", "FÁBRICA AQA"),
    "carlos.goncalves": ("28909", "FÁBRICA AQA"),
    "josemir.batista": ("28987", "FÁBRICA AQA"),
    "samuel.souza": ("28901", "FÁBRICA AQA"),
    "jose.bartolomeu": ("27672", "FÁBRICA AQA"),
    "mauri.almeida": ("27974", "BAYGORRIA"),
    "roberto.fidelis": ("27676", "BAYGORRIA"),
    "luciano.franca": ("27844", "BAYGORRIA"),
    "marcelo.candido": ("28958", "BAYGORRIA"),
    "alexandro.soares": ("27846", "BAYGORRIA"),
    "clodoaldo.silva": ("27835", "BRACELL"),
    "jair.santana": ("28967", "ARAUCO"),
    "kauan.adm": ("33419", "ADMIN")
}

COLABORADORES = {
    "FÁBRICA AQA": ["KLEITON DELFINO FERREIRA", "CLAUDEMAR NUNES", "JOSEMIR BATISTA DOS SANTOS", "CARLOS ANTONIO LOPES FERNANDES", "CARLOS GONÇALVES DE OLIVEIRA", "FABRICIO DE LIMA AZEVEDO", "SAMUEL DE SOUZA BARBOSA", "JONATTAS DE MACEDO CAMPOS", "GLEUVAILTON MARQUES", "JOSE BARTOLOMEU DE NOLETO AMORIM"],
    "BAYGORRIA": ["MAURI ALMEIDA", "ROBERTO FIDELIS", "ALEXANDRO SOARES", "LUCIANO FRANCA MESSIAS", "MARCELO CANDIDO DE MAGALHÃES"],
    "ARAUCO": ["JAIR SANT ANA ALMEIDA"],
    "BRACELL": ["CLODOALDO"],
    "CERAN": []
}

BASE = "uploads"
os.makedirs(BASE, exist_ok=True)

def normalizar(txt):
    if not txt: return ""
    txt = txt.upper()
    return ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')

def get_mes_atual():
    return datetime.now().strftime("%Y-%m")

def arquivo_do_login(projeto, login_user):
    """Retorna o nome do arquivo encontrado para um login, ou None."""
    mes = get_mes_atual()
    pasta = os.path.join(BASE, projeto, mes)
    if not os.path.exists(pasta):
        return None
    for f in os.listdir(pasta):
        if f.upper().startswith(login_user.upper() + ".") or f.upper().startswith(login_user.upper() + "_"):
            return f
    # fallback: qualquer arquivo que comece com o login
    for f in os.listdir(pasta):
        if f.upper().startswith(login_user.upper()):
            return f
    return None

def get_login_por_nome(nome):
    """Retorna o login do colaborador pelo nome completo."""
    return next((u for u in USUARIOS if normalizar(u.split('.')[0]) in normalizar(nome)), None)

def status_projeto(projeto):
    """Retorna lista de (nome, status, login) para um projeto."""
    mes = get_mes_atual()
    pasta = os.path.join(BASE, projeto, mes)
    arquivos_na_pasta = [f.upper() for f in os.listdir(pasta)] if os.path.exists(pasta) else []
    lista = []
    for n in COLABORADORES.get(projeto, []):
        login_u = get_login_por_nome(n) or "desconhecido"
        arq = arquivo_do_login(projeto, login_u)
        lista.append((n, "ok" if arq else "pendente", login_u))
    return lista

def enviar_email_projeto(projeto):
    """Envia e-mail com todas as folhas do projeto como anexo."""
    mes = get_mes_atual()
    pasta = os.path.join(BASE, projeto, mes)
    if not os.path.exists(pasta):
        return False, "Pasta não encontrada."

    arquivos = [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]
    if not arquivos:
        return False, "Nenhum arquivo encontrado."

    try:
        msg = MIMEMultipart()
        msg['From'] = f"Controle Folha de Ponto <{EMAIL_CONFIG['usuario']}>"
        msg['To'] = EMAIL_CONFIG['destinatario_rh']
        msg['Subject'] = f"Envio de folhas de Ponto - {projeto} - {mes}"

        corpo = f"""Olá, 
        

Segue as folhas de pontos de {projeto} 
referentes ao período {mes}.
        

Quantidade total de Arquivos: {len(arquivos)}, 
        

Mensagem enviada automáticamente pelo sistema em RH. 
        

Atenciosamente,
"""
        msg.attach(MIMEText(corpo, 'plain'))

        for nome_arq in arquivos:
            caminho = os.path.join(pasta, nome_arq)
            with open(caminho, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{nome_arq}"')
            msg.attach(part)

        with smtplib.SMTP(EMAIL_CONFIG['smtp_host'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['usuario'], EMAIL_CONFIG['senha'])
            server.send_message(msg)

        return True, f"{len(arquivos)} arquivo(s) enviado(s) com sucesso."
    except Exception as e:
        return False, str(e)

@app.before_request
def verificar_sessao():
    rotas_abertas = ['login', 'static']
    if 'usuario' not in session and request.endpoint not in rotas_abertas:
        return redirect(url_for('login'))

# =========================
# CSS (inalterado)
# =========================
ESTILO = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    :root { --primary: #0075BE; --bg: #f4f7f9; }
    body { background: var(--bg); font-family: 'Inter', sans-serif; margin: 0; }
    .nav-bar { background: white; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; padding: 30px; }
    .project-card { background: var(--primary); border-radius: 24px; padding: 25px; color: white; display: flex; flex-direction: column; height: 520px; }
    .checklist { background: rgba(255,255,255,0.1); border-radius: 16px; flex-grow: 1; overflow-y: auto; padding: 15px; margin: 20px 0; }
    .check-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .func-nome { flex: 1; font-size: 12px; font-weight: 700; text-align: left; color: #ffffff; }
    .btn-enviar { padding: 16px; border-radius: 14px; width: 100%; font-weight: 700; text-align: center; text-decoration: none; display: block; border: none; }
    .btn-ativo { background: white; color: var(--primary); cursor: pointer; transition: 0.3s; }
    .btn-bloqueado { background: rgba(255,255,255,0.2); color: rgba(255,255,255,0.4); cursor: not-allowed; }
@media (max-width: 768px) {

    .nav-bar {
        padding: 15px 20px;
        flex-direction: column;
        gap: 10px;
        text-align: center;
    }

    .dashboard-grid {
        grid-template-columns: 1fr;
        padding: 15px;
    }

    .project-card {
        height: auto;
    }

    .checklist {
        max-height: 300px;
    }

    .func-nome {
        font-size: 11px;
    }

    .btn-enviar {
        padding: 14px;
        font-size: 14px;
    }

    form {
        width: 100%;
    }

    input {
        width: 100% !important;
        box-sizing: border-box;
    }

}
</style>
"""

@app.route("/")
def index():
    if 'usuario' not in session: return redirect(url_for("login"))
    if session.get("projeto") == "ADMIN": return redirect(url_for("admin"))
    return redirect(url_for("upload_colaborador"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("usuario", "").lower().strip()
        senha = request.form.get("senha", "").strip()
        if user in USUARIOS and USUARIOS[user][0] == senha:
            session.clear()
            session["usuario"] = user
            session["projeto"] = USUARIOS[user][1]
            return redirect(url_for("index"))
    return render_template_string(ESTILO + """
    <div style="display:flex; align-items:center; justify-content:center; min-height:100vh;">
        <div style="background:var(--primary); padding:35px; border-radius:25px; width:260px; text-align:center; color:white;">
            <h1>Bem Vindo(a)</h1>
            <form method="POST">
                <input type="text" name="usuario" style="width:100%; padding:12px; margin-bottom:12px; border-radius:10px; border:none; box-sizing:border-box;" placeholder="Usuário" required>
                <input type="password" name="senha" style="width:100%; padding:12px; margin-bottom:20px; border-radius:10px; border:none; box-sizing:border-box;" placeholder="Senha" required>
                <button type="submit" style="width:100%; padding:14px; border-radius:10px; border:none; background:white; color:var(--primary); font-weight:800;">ENTRAR</button>
            </form>
        </div>
    </div>
    """)

# =========================
# ADMIN — dashboard principal
# =========================
@app.route("/admin")
def admin():
    if session.get("projeto") != "ADMIN": return redirect(url_for("login"))

    res = {}
    for p in PROJETOS:
        res[p] = status_projeto(p)

    return render_template_string(ESTILO + """
    <div class="nav-bar">
        <h2 style="margin:0; color:var(--primary); font-size:1.2rem;">CONTROLE DE PONTO - RH</h2>
        <a href="/logout" style="color:#fa5252; font-weight:700; text-decoration:none;">SAIR</a>
    </div>

    <!-- Toast de notificação -->
    <div id="toast" style="display:none; position:fixed; top:20px; right:20px; z-index:9999;
         padding:14px 22px; border-radius:12px; font-weight:700; font-size:13px;
         background:#51cf66; color:white; box-shadow:0 4px 20px rgba(0,0,0,0.15);">
    </div>

    <div class="dashboard-grid">
        {% for p in projetos %}
        {% set lista = dados[p] %}
        {% set total = lista|length %}
        {% set prontos = namespace(c=0) %}
        {% for nome, status, login_u in lista %}
            {% if status == 'ok' %}{% set prontos.c = prontos.c + 1 %}{% endif %}
        {% endfor %}

        <div class="project-card" id="card-{{ p|replace(' ', '_')|replace('Á','A')|replace('É','E')|replace('Ã','A') }}">
            <h3 style="margin:0;">{{ p }}</h3>
            <div class="checklist" id="checklist-{{ loop.index }}">
                {% for nome, status, login_u in lista %}
                <div class="check-item" id="item-{{ login_u }}">
                    <div class="func-nome">{{ nome }}</div>
                    <div style="display:flex; align-items:center; gap:10px;">
                        {% if status == 'ok' %}
                            <a href="/ver_arquivo/{{ p }}/{{ login_u }}" target="_blank" style="text-decoration:none;" title="Ver arquivo">ℹ️</a>
                            <span id="check-{{ login_u }}" style="color:#00ff00;">✔</span>
                        {% else %}
                            <span id="check-{{ login_u }}" style="color:#ff0000;">✖</span>
                        {% endif %}
                        <a href="/remover/{{ p }}/{{ login_u }}" onclick="return confirm('Remover folha de {{ nome }}?')" style="text-decoration:none;" title="Remover">🗑️</a>
                    </div>
                </div>
                {% endfor %}
            </div>

            {% if prontos.c == total and total > 0 %}
                <button class="btn-enviar btn-ativo"
                    onclick="enviarEmail('{{ p }}', this)"
                    id="btn-{{ loop.index }}">
                    Enviar Folhas ({{ prontos.c }}/{{ total }})
                </button>
            {% else %}
                <button class="btn-enviar btn-bloqueado"
                    id="btn-{{ loop.index }}"
                    disabled>
                    Aguardando ({{ prontos.c }}/{{ total }})
                </button>
            {% endif %}
        </div>
        {% endfor %}
    </div>

    <script>
    function mostrarToast(msg, erro) {
        const t = document.getElementById('toast');
        t.textContent = msg;
        t.style.background = erro ? '#ff6b6b' : '#51cf66';
        t.style.display = 'block';
        setTimeout(() => t.style.display = 'none', 4000);
    }

    function enviarEmail(projeto, btn) {
        btn.disabled = true;
        btn.textContent = 'Enviando...';
        fetch('/enviar_email', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({projeto: projeto})
        })
        .then(r => r.json())
        .then(data => {
            mostrarToast(data.msg, !data.ok);
            btn.disabled = false;
            btn.textContent = data.ok ? '✔ Enviado!' : 'Tentar novamente';
        })
        .catch(() => {
            mostrarToast('Erro de conexão.', true);
            btn.disabled = false;
        });
    }

    // Polling: atualiza checklist a cada 10 segundos sem recarregar a página
    function atualizarChecklist() {
        fetch('/status_projetos')
            .then(r => r.json())
            .then(dados => {
                for (const [projeto, lista] of Object.entries(dados)) {
                    let total = lista.length;
                    let prontos = 0;
                    lista.forEach(([nome, status, login]) => {
                        const span = document.getElementById('check-' + login);
                        if (!span) return;
                        if (status === 'ok') {
                            prontos++;
                            if (span.textContent === '✖') {
                                // Atualiza o item sem reload
                                span.textContent = '✔';
                                span.style.color = '#00ff00';
                                // Adiciona botão de ver arquivo se não existir
                                const itemDiv = document.getElementById('item-' + login);
                                if (itemDiv && !itemDiv.querySelector('a[href*="/ver_arquivo/"]')) {
                                    const acoes = itemDiv.querySelector('div[style]');
                                    const link = document.createElement('a');
                                    link.href = '/ver_arquivo/' + encodeURIComponent(projeto) + '/' + login;
                                    link.target = '_blank';
                                    link.style.textDecoration = 'none';
                                    link.title = 'Ver arquivo';
                                    link.textContent = 'ℹ️';
                                    acoes.insertBefore(link, span);
                                }
                            }
                        } else {
                            span.textContent = '✖';
                            span.style.color = '#ff0000';
                        }
                    });

                    // Atualiza o botão de cada projeto
                    // Encontra o índice do projeto na lista
                    const projetos = """ + str([p for p in PROJETOS]) + """;
                    const idx = projetos.indexOf(projeto);
                    if (idx === -1) continue;
                    const btn = document.getElementById('btn-' + (idx + 1));
                    if (!btn) continue;
                    if (prontos === total && total > 0) {
                        btn.className = 'btn-enviar btn-ativo';
                        btn.disabled = false;
                        btn.onclick = function() { enviarEmail(projeto, this); };
                        if (!btn.textContent.includes('✔')) {
                            btn.textContent = 'Enviar Folhas (' + prontos + '/' + total + ')';
                        }
                    } else {
                        btn.className = 'btn-enviar btn-bloqueado';
                        btn.disabled = true;
                        btn.onclick = null;
                        if (!btn.textContent.includes('Enviando') && !btn.textContent.includes('✔')) {
                            btn.textContent = 'Aguardando (' + prontos + '/' + total + ')';
                        }
                    }
                }
            });
    }

    setInterval(atualizarChecklist, 10000);
    </script>
    """, projetos=PROJETOS, dados=res)

# =========================
# API: status em tempo real
# =========================
@app.route("/status_projetos")
def status_projetos():
    if session.get("projeto") != "ADMIN":
        return jsonify({}), 403
    res = {}
    for p in PROJETOS:
        res[p] = status_projeto(p)
    return jsonify(res)

# =========================
# API: envio de e-mail
# =========================
@app.route("/enviar_email", methods=["POST"])
def enviar_email():
    if session.get("projeto") != "ADMIN":
        return jsonify({"ok": False, "msg": "Acesso negado."}), 403
    data = request.get_json()
    projeto = data.get("projeto", "")
    if projeto not in PROJETOS:
        return jsonify({"ok": False, "msg": "Projeto inválido."})

    ok, msg = enviar_email_projeto(projeto)
    return jsonify({"ok": ok, "msg": msg})

# =========================
# Ver arquivo do colaborador
# =========================
@app.route("/ver_arquivo/<projeto>/<login_user>")
def ver_arquivo(projeto, login_user):
    if session.get("projeto") != "ADMIN":
        return "Acesso negado.", 403
    arq = arquivo_do_login(projeto, login_user)
    if arq:
        pasta = os.path.join(BASE, projeto, get_mes_atual())
        return send_from_directory(os.path.abspath(pasta), arq)
    return f"Arquivo de '{login_user}' não encontrado.", 404

# =========================
# Remover arquivo
# =========================
@app.route("/remover/<projeto>/<login_user>")
def remover(projeto, login_user):
    if session.get("projeto") != "ADMIN":
        return redirect(url_for("login"))
    arq = arquivo_do_login(projeto, login_user)
    if arq:
        pasta = os.path.join(BASE, projeto, get_mes_atual())
        try:
            os.remove(os.path.join(pasta, arq))
        except Exception:
            pass
    return redirect(url_for("admin"))

# =========================
# Upload do colaborador
# =========================
@app.route("/upload", methods=["GET", "POST"])
def upload_colaborador():
    if request.method == "POST":
        file = request.files.get("arquivo")
        if file and file.filename:
            pasta = os.path.join(BASE, session["projeto"], get_mes_atual())
            os.makedirs(pasta, exist_ok=True)
            ext = os.path.splitext(file.filename)[1]
            nome_arq = f"{session['usuario']}{ext}"
            file.save(os.path.join(pasta, nome_arq))
            return redirect(url_for('upload_colaborador', sucesso=True))

    nome_exibicao = session.get("usuario", "").split('.')[0].capitalize()
    return render_template_string(ESTILO + """

    <style>
    .upload-container {
        display:flex;
        align-items:center;
        justify-content:center;
        min-height:80vh;
    }

    .upload-box {
        background: var(--primary);
        padding:45px 35px;
        border-radius:30px;
        width:350px;
        text-align:center;
        color:white;
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }

    .upload-box h3 {
        margin-bottom:10px;
        font-size: 2.3rem;
    }

    .upload-box p {
        margin-bottom:25px;
        opacity:0.9;
        font-size: 1.3rem;                         
    }

    .file-label {
        display:block;
        background:#ff5c4d;
        padding:16px;
        border-radius:14px;
        font-weight:700;
        cursor:pointer;
        transition:0.3s;
        widht: 60%;
        margin: 0 auto;                         
    }

    .file-label:hover {
        background:#ff3b2e;
        transform: scale(1.03);
    }

    .file-name {
        margin:15px 0;
        font-size:13px;
        opacity:0.85;
    }

    .btn-submit {
        margin-top:10px;
        width:60%;
        padding:15px;
        border-radius:14px;
        border:none;
        font-weight:800;
        background:white;
        color:var(--primary);
        cursor:pointer;
        transition:0.3s;
    }

    .btn-submit:hover {
        transform: scale(1.03);
        box-shadow:0 5px 20px rgba(0,0,0,0.2);
    }
    </style>

    <div class="nav-bar">
        <h2 style="margin:0; color:var(--primary); font-size:1.2rem;">
            CONTROLE DE PONTO - RH
        </h2>
        <a href="/logout" style="color:#fa5252; font-weight:700; text-decoration:none;">
            SAIR
        </a>
    </div>

    <div class="upload-container">
        <div class="upload-box">

            {% if request.args.get('sucesso') %}
                <div style="background:#d4edda; color:#155724; padding:10px; border-radius:10px; margin-bottom:20px;">
                    ✔ Folha enviada com sucesso!
                </div>
            {% endif %}

            <h3>{{ projeto }}</h3>
            <p>Olá, {{ nome }}</p>

            <form method="POST" enctype="multipart/form-data">

                <label class="file-label">
                    SELECIONAR FOLHA
                    <input type="file" name="arquivo" required 
                           style="display:none;" 
                           onchange="mostrarNome(this)">
                </label>

                <div class="file-name" id="file-name">
                    Nenhum arquivo selecionado
                </div>

                <button type="submit" class="btn-submit">
                    SALVAR FOLHA
                </button>
            </form>

        </div>
    </div>

    <script>
    function mostrarNome(input) {
        const nome = input.files[0]?.name || "Nenhum arquivo selecionado";
        document.getElementById("file-name").textContent = nome;
    }
    </script>

    """, projeto=session["projeto"], nome=nome_exibicao)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)