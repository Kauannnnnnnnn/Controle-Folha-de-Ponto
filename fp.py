from flask import Flask, request, render_template_string, redirect, session, url_for, send_from_directory, jsonify
import os
from datetime import datetime, timedelta
import unicodedata
import smtplib
import secrets
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

app = Flask(__name__)

# =========================================================
# CONFIGURAÇÃO
# =========================================================
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

app.config.update(
 SESSION_COOKIE_HTTPONLY=True,
 SESSION_COOKIE_SAMESITE="Lax",
 SESSION_COOKIE_SECURE=os.environ.get("PRODUCTION", "0") == "1",
 PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
)

PROJETOS = ["FÁBRICA AQA", "BAYGORRIA", "BRACELL", "ARAUCO", "BELO MONTE"]

EMAIL_CONFIG = {
 "smtp_host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
 "smtp_port": int(os.environ.get("SMTP_PORT", "587")),
 "usuario": os.environ.get("SMTP_USER", "kauanmarin16@gmail.com"),
 "senha": os.environ.get("SMTP_PASSWORD", "rigr lnyn tels aqbf"),
 "destinatario_rh": os.environ.get("RH_EMAIL", "beatrizfg07@icloud.com"),
 "copia": [email.strip() for email in os.environ.get("CC_EMAILS", "").split(",") if email.strip()]
}

USUARIOS = {
 "kleiton.delfino": {"nome": "KLEITON DELFINO FERREIRA", "matricula": "28956", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "fabricio.azevedo": {"nome": "FABRICIO DE LIMA AZEVEDO", "matricula": "27525", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "claudemar.nunes": {"nome": "CLAUDEMAR NUNES", "matricula": "27492", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "jonattas.macedo": {"nome": "JONATTAS DE MACEDO CAMPOS", "matricula": "29036", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "gleuvailton.marques": {"nome": "GLEUVAILTON MARQUES", "matricula": "27529", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "carlos.antonio": {"nome": "CARLOS ANTONIO LOPES FERNANDES", "matricula": "27529", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "carlos.goncalves": {"nome": "CARLOS GONÇALVES DE OLIVEIRA", "matricula": "28909", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "josemir.batista": {"nome": "JOSEMIR BATISTA DOS SANTOS", "matricula": "28987", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "samuel.souza": {"nome": "SAMUEL DE SOUZA BARBOSA", "matricula": "28901", "projeto": "BELO MONTE", "perfil": "COLABORADOR"},
 "jose.bartolomeu": {"nome": "JOSE BARTOLOMEU DE NOLETO AMORIM", "matricula": "27672", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "adilson.almeida": {"nome": "ADILSON ALMEIDA DE BASTOS", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "jorismar.martins": {"nome": "JORISMAR MARTINS DA SILVA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "jose.lopes": {"nome": "JOSE LOPES FERNANDES", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "rosinaldo.medeiros": {"nome": "ROSINALDO JOSE DE MEDEIROS", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "jailson.santos": {"nome": "JAILSON NORBETO DOS SANTOS", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "janilton.campos": {"nome": "JANILTON MARTINS CAMPOS", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "adam.samuel": {"nome": "ADAM SAMUEL FERNANDES DA SILVA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "bruno.souza": {"nome": "BRUNO RODRIGUES SOUZA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "davi.feitosa": {"nome": "DAVI DA SILVA FEITOSA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "eric.vinicius": {"nome": "ERIC VINICIUS DIAS DA PAZ", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "josue.costa": {"nome": "JOSUE VINICIUS CLEMENTE COSTA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "reidiner.silva": {"nome": "REIDINER SANTANA DA SILVA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "vitor.valentim": {"nome": "VITOR VALENTIM SANTOS SILVA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "aldissandro.santos": {"nome": "ALDISSANDRO MATOS DOS SANTOS", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "deodoro.delfino": {"nome": "DEODORO CARLOS DELFINO", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "joelson.inocencio": {"nome": "JOELSON INOCENCIO DA SILVA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "roseanderson.lino": {"nome": "ROSEANDERSON LINO DE SOUSA OLIVEIRA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "josivan.inocencio": {"nome": "JOSIVAN INOCENCIO DA SILVA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "jose.vani": {"nome": "JOSE VANI CORDEIRO DE OLIVEIRA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "josias.batista": {"nome": "JOSIAS BATISTA DOS SANTOS", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "josiel.monteiro": {"nome": "JOSIEL MONTEIRO RODRIGUES", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "luiz.carlos": {"nome": "LUIZ CARLOS DE LIMA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "diego.medeiros": {"nome": "DIEGO RAFAEL DE MEDEIROS SANTOS", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "lucrecio.santos": {"nome": "LUCRECIO DOS SANTOS", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "sebastiao.souza": {"nome": "SEBASTIAO DE SOUZA", "matricula": "", "projeto": "FÁBRICA AQA", "perfil": "COLABORADOR"},
 "pedro.duarte": {"nome": "PEDRO DUARTE DA SILVA", "matricula": "", "projeto": "BELO MONTE", "perfil": "COLABORADOR"},
 "jose.raimundo": {"nome": "JOSE RAIMUNDO DE SOUZA NETO", "matricula": "", "projeto": "BELO MONTE", "perfil": "COLABORADOR"},
 "elias.silveira": {"nome": "ELIAS SILVEIRA DE MEDEIROS NETO", "matricula": "", "projeto": "BELO MONTE", "perfil": "COLABORADOR"},
 "filipe.inocencio": {"nome": "FILIPE INOCENCIO DE SOUZA", "matricula": "", "projeto": "BELO MONTE", "perfil": "COLABORADOR"},
 "jose.dias": {"nome": "JOSE DIAS DE SOUSA", "matricula": "", "projeto": "BELO MONTE", "perfil": "COLABORADOR"},
 "miguel.santana": {"nome": "MIGUEL TEIXEIRA SANTANA", "matricula": "", "projeto": "BELO MONTE", "perfil": "COLABORADOR"},
 "diego.pacheco": {"nome": "DIEGO PACHECO DA SILVA", "matricula": "", "projeto": "BELO MONTE", "perfil": "COLABORADOR"},
 "venancio.lima": {"nome": "VENANCIO PEREIRA LIMA", "matricula": "", "projeto": "BELO MONTE", "perfil": "COLABORADOR"},
 "saulo.tacio": {"nome": "SAULO DE TACIO DE OLIVEIRA COSTA", "matricula": "", "projeto": "BELO MONTE", "perfil": "COLABORADOR"},
 "adriano.azevedo": {"nome": "ADRIANO DE LIMA DE AZEVEDO", "matricula": "", "projeto": "BELO MONTE", "perfil": "COLABORADOR"},
 "mauri.almeida": {"nome": "MAURI ALMEIDA", "matricula": "27974", "projeto": "BAYGORRIA", "perfil": "COLABORADOR"},
 "luciano.franca": {"nome": "LUCIANO FRANCA MESSIAS", "matricula": "27844", "projeto": "BAYGORRIA", "perfil": "COLABORADOR"},
 "marcelo.candido": {"nome": "MARCELO CANDIDO DE MAGALHÃES", "matricula": "28958", "projeto": "BAYGORRIA", "perfil": "COLABORADOR"},
 "romenito.calvancante": {"nome": "ROMENITO CALVACANTE", "matricula": "", "projeto": "BAYGORRIA", "perfil": "COLABORADOR"},
 "clodoaldo.silva": {"nome": "CLODOALDO JOSE DE ALMEIDA", "matricula": "27835", "projeto": "BRACELL", "perfil": "COLABORADOR"},
 "jair.santana": {"nome": "JAIR SANT ANA ALMEIDA", "matricula": "28967", "projeto": "ARAUCO", "perfil": "COLABORADOR"},
}

COLABORADORES = {
 "FÁBRICA AQA": [
 "CARLOS ANTONIO LOPES FERNANDES",
 "CLAUDEMAR NUNES",
 "ADILSON ALMEIDA DE BASTOS",
 "JORISMAR MARTINS DA SILVA",
 "JOSE LOPES FERNANDES",
 "ROSINALDO JOSE DE MEDEIROS",
 "KLEITON DELFINO FERREIRA",
 "JAILSON NORBETO DOS SANTOS",
 "JANILTON MARTINS CAMPOS",
 "ADAM SAMUEL FERNANDES DA SILVA",
 "BRUNO RODRIGUES SOUZA",
 "DAVI DA SILVA FEITOSA",
 "ERIC VINICIUS DIAS DA PAZ",
 "JOSUE VINICIUS CLEMENTE COSTA",
 "JONATTAS DE MACEDO CAMPOS",
 "REIDINER SANTANA DA SILVA",
 "VITOR VALENTIM SANTOS SILVA",
 "ALDISSANDRO MATOS DOS SANTOS",
 "DEODORO CARLOS DELFINO",
 "JOELSON INOCENCIO DA SILVA",
 "ROSEANDERSON LINO DE SOUSA OLIVEIRA",
 "GLEUVAILTON MARQUES",
 "JOSEMIR BATISTA DOS SANTOS",
 "JOSIVAN INOCENCIO DA SILVA",
 "JOSE VANI CORDEIRO DE OLIVEIRA",
 "JOSIAS BATISTA DOS SANTOS",
 "JOSIEL MONTEIRO RODRIGUES",
 "LUIZ CARLOS DE LIMA",
 "FABRICIO DE LIMA AZEVEDO",
 "CARLOS GONÇALVES DE OLIVEIRA",
 "JOSE BARTOLOMEU DE NOLETO AMORIM",
 "DIEGO RAFAEL DE MEDEIROS SANTOS",
 "LUCRECIO DOS SANTOS",
 "SEBASTIAO DE SOUZA"
 ],
 "BELO MONTE": [
 "PEDRO DUARTE DA SILVA",
 "JOSE RAIMUNDO DE SOUZA NETO",
 "ELIAS SILVEIRA DE MEDEIROS NETO",
 "FILIPE INOCENCIO DE SOUZA",
 "JOSE DIAS DE SOUSA",
 "MIGUEL TEIXEIRA SANTANA",
 "DIEGO PACHECO DA SILVA",
 "VENANCIO PEREIRA LIMA",
 "SAMUEL DE SOUZA BARBOSA",
 "ADRIANO DE LIMA DE AZEVEDO",
 "SAULO DE TACIO DE OLIVEIRA COSTA"
 ],
 "BAYGORRIA": [
 "MAURI ALMEIDA",
 "LUCIANO FRANCA MESSIAS",
 "MARCELO CANDIDO DE MAGALHÃES",
 "ROMENITO CALVACANTE"
 ],
 "ARAUCO": [
 "JAIR SANT ANA ALMEIDA"
 ],
 "BRACELL": [
 "CLODOALDO JOSE DE ALMEIDA"
 ]
}

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "33419")

BASE = "uploads"
os.makedirs(BASE, exist_ok=True)

# =========================================================
# FUNÇÕES
# =========================================================
def normalizar(txt):
 if not txt:
  return ""
 txt = txt.upper()
 return "".join(
  c for c in unicodedata.normalize("NFD", txt)
  if unicodedata.category(c) != "Mn"
 )

def get_mes_atual():
 return datetime.now().strftime("%Y-%m")

def arquivo_do_login(projeto, login_user):
 mes = get_mes_atual()
 pasta = os.path.join(BASE, projeto, mes)

 if not os.path.exists(pasta):
  return None

 for f in os.listdir(pasta):
  if f.upper().startswith(login_user.upper() + ".") or f.upper().startswith(login_user.upper() + "_"):
   return f

 for f in os.listdir(pasta):
  if f.upper().startswith(login_user.upper()):
   return f

 return None

def get_login_por_nome(nome):
 alvo = normalizar(nome)
 for login, dados in USUARIOS.items():
  if normalizar(dados["nome"]) == alvo:
   return login
 return None

def status_projeto(projeto):
 lista = []

 for nome in COLABORADORES.get(projeto, []):
  login_u = get_login_por_nome(nome) or "desconhecido"
  arq = arquivo_do_login(projeto, login_u)

  lista.append({
   "nome": nome,
   "status": "ok" if arq else "pendente",
   "login": login_u,
   "arquivo": arq
  })

 return lista

def exigir_admin():
 return session.get("perfil") == "ADMIN"

def enviar_email_projeto(projeto, emails_cc=None):
 mes = get_mes_atual()
 pasta = os.path.join(BASE, projeto, mes)

 if not os.path.exists(pasta):
  return False, "Pasta do projeto não encontrada."

 arquivos = [
  f for f in os.listdir(pasta)
  if os.path.isfile(os.path.join(pasta, f))
 ]

 if not arquivos:
  return False, "Nenhum arquivo encontrado para envio."

 if not EMAIL_CONFIG["senha"]:
  return False, "Senha SMTP não configurada. Configure SMTP_PASSWORD."

 try:
  msg = MIMEMultipart()
  msg["From"] = EMAIL_CONFIG["usuario"]
  msg["To"] = EMAIL_CONFIG["destinatario_rh"]
  msg["Subject"] = f"Folhas de Ponto | {projeto} | {mes}"

  lista_cc = []
  if emails_cc and isinstance(emails_cc, list):
   lista_cc = [e.strip() for e in emails_cc if e.strip()]
  elif EMAIL_CONFIG["copia"]:
   lista_cc = EMAIL_CONFIG["copia"]

  if lista_cc:
   msg["Cc"] = ", ".join(lista_cc)

  corpo = f"""Olá,

Segue o envio das folhas de ponto referentes ao projeto {projeto},
período {mes}.

Quantidade total de arquivos anexados: {len(arquivos)}

Mensagem enviada automaticamente pelo sistema Controle de Ponto.

Atenciosamente,
"""
  msg.attach(MIMEText(corpo, "plain", "utf-8"))

  for nome_arq in arquivos:
   caminho = os.path.join(pasta, nome_arq)

   with open(caminho, "rb") as f:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(f.read())

   encoders.encode_base64(part)
   part.add_header(
    "Content-Disposition",
    f'attachment; filename="{nome_arq}"'
   )
   msg.attach(part)

  destinatarios_totais = [EMAIL_CONFIG["destinatario_rh"]] + lista_cc

  with smtplib.SMTP(
   EMAIL_CONFIG["smtp_host"],
   EMAIL_CONFIG["smtp_port"],
   timeout=30
  ) as server:
   server.ehlo()
   server.starttls()
   server.ehlo()
   server.login(
    EMAIL_CONFIG["usuario"],
    EMAIL_CONFIG["senha"]
   )
   server.sendmail(
    EMAIL_CONFIG["usuario"],
    destinatarios_totais,
    msg.as_string()
   )

  return True, f"{len(arquivos)} arquivo(s) enviado(s) com sucesso."

 except Exception as e:
  print("ERRO SMTP:", repr(e))
  return False, f"Falha no envio: {e}"

# =========================================================
# HTML / CSS
# =========================================================
STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
 --blue:#0284c7;
 --blue-dark:#0369a1;
 --blue-soft:#e0f2fe;
 --ink:#0f172a;
 --muted:#64748b;
 --bg:#f8fafc;
 --card:#ffffff;
 --line:#e2e8f0;
 --green:#10b981;
 --green-dark:#059669;
 --green-soft:#d1fae5;
 --red:#ef4444;
 --red-soft:#fee2e2;
 --shadow:0 12px 32px -8px rgba(15, 23, 42, 0.06);
}

* { box-sizing:border-box; }

body {
 margin:0;
 min-height:100vh;
 background:
  radial-gradient(circle at 0% 0%, rgba(2, 132, 199, 0.04), transparent 40%),
  radial-gradient(circle at 100% 100%, rgba(16, 185, 129, 0.03), transparent 40%),
  var(--bg);
 color:var(--ink);
 font-family:'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
 -webkit-font-smoothing: antialiased;
}

button, input { font:inherit; }
button { cursor:pointer; }

.page {
 min-height:100vh;
 display:flex;
 align-items:center;
 justify-content:center;
 padding:16px;
}

.login-shell {
 width:min(1000px, 100%);
 min-height:600px;
 display:grid;
 grid-template-columns:1.05fr .95fr;
 background:#fff;
 border:1px solid var(--line);
 border-radius:24px;
 overflow:hidden;
 box-shadow:var(--shadow);
}

.login-brand {
 position:relative;
 overflow:hidden;
 padding:44px;
 color:#fff;
 background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
 display:flex;
 flex-direction:column;
 justify-content:space-between;
}

.brand-logo {
 width:48px;
 height:48px;
 border-radius:14px;
 background:rgba(255,255,255,.2);
 backdrop-filter:blur(8px);
 border:1px solid rgba(255,255,255,.3);
 display:flex;
 align-items:center;
 justify-content:center;
 font-weight:800;
 font-size:20px;
}

.brand-copy h1 {
 margin:0 0 14px;
 font-size:38px;
 line-height:1.1;
 letter-spacing:-1px;
 font-weight:800;
}

.brand-copy p {
 margin:0;
 line-height:1.6;
 color:rgba(255,255,255,.85);
 font-size:14px;
}

.brand-footer {
 font-size:12px;
 color:rgba(255,255,255,.7);
 font-weight:500;
}

.login-panel {
 padding:44px;
 display:flex;
 flex-direction:column;
 justify-content:center;
}

.login-panel h2 {
 margin:0;
 font-size:24px;
 letter-spacing:-.5px;
 font-weight:800;
}

.login-panel .subtitle {
 margin:6px 0 20px;
 color:var(--muted);
 font-size:13px;
 line-height:1.5;
}

.mode-tabs {
 display:grid;
 grid-template-columns:1fr 1fr;
 gap:4px;
 background:#f1f5f9;
 border-radius:12px;
 padding:4px;
 margin-bottom:18px;
}

.mode-tab {
 border:0;
 background:transparent;
 color:var(--muted);
 padding:9px;
 border-radius:8px;
 font-weight:700;
 font-size:13px;
 transition: all .2s;
}

.mode-tab.active {
 background:#fff;
 color:var(--blue);
 box-shadow:0 2px 6px rgba(15,23,42,.06);
}

.field { margin-bottom:14px; }

.field label {
 display:block;
 font-size:11px;
 font-weight:800;
 margin-bottom:6px;
 color:#475569;
 letter-spacing:.4px;
}

.field input, .search-input {
 width:100%;
 border:1px solid var(--line);
 background:#f8fafc;
 border-radius:12px;
 padding:11px 14px;
 outline:none;
 transition:.2s;
 color:var(--ink);
 font-size:14px;
}

.field input:focus, .search-input:focus {
 border-color:var(--blue);
 box-shadow:0 0 0 3px rgba(2,132,199,.12);
 background:#fff;
}

.primary-btn {
 width:100%;
 border:0;
 border-radius:12px;
 padding:13px;
 color:#fff;
 background:linear-gradient(135deg,var(--blue),var(--blue-dark));
 font-weight:700;
 font-size:14px;
 box-shadow:0 4px 12px rgba(2,132,199,.25);
 transition:.2s ease;
 display:inline-flex;
 align-items:center;
 justify-content:center;
 gap:8px;
}

.primary-btn:hover {
 transform:translateY(-1px);
 box-shadow:0 6px 16px rgba(2,132,199,.3);
}

.primary-btn.btn-enviado {
 background: linear-gradient(135deg, var(--green), var(--green-dark)) !important;
 box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
}

.error {
 background:var(--red-soft);
 color:#b91c1c;
 border:1px solid #fca5a5;
 border-radius:12px;
 padding:10px 12px;
 font-size:13px;
 margin-bottom:14px;
 font-weight:600;
}

.employee-search {
 position:relative;
 margin-bottom:10px;
}

.employee-search span {
 position:absolute;
 left:12px;
 top:10px;
 color:var(--muted);
}

.employee-search input { padding-left:36px; }

.employee-list {
 max-height:280px;
 overflow-y:auto;
 display:flex;
 flex-direction:column;
 gap:6px;
 padding-right:2px;
}

.employee-btn {
 width:100%;
 text-align:left;
 border:1px solid var(--line);
 background:#fff;
 border-radius:12px;
 padding:10px 12px;
 display:flex;
 align-items:center;
 gap:10px;
 transition:.15s ease;
}

.employee-btn:hover {
 border-color:#bae6fd;
 background:var(--blue-soft);
}

.avatar {
 flex:0 0 34px;
 width:34px;
 height:34px;
 border-radius:10px;
 display:flex;
 align-items:center;
 justify-content:center;
 background:var(--blue-soft);
 color:var(--blue-dark);
 font-size:12px;
 font-weight:800;
}

.employee-name { font-size:13px; font-weight:700; color:var(--ink); }
.employee-project { color:var(--muted); font-size:11px; margin-top:1px; font-weight:500; }

.app-shell {
 min-height:100vh;
 display:grid;
 grid-template-columns:240px 1fr;
}

.sidebar {
 background:#fff;
 border-right:1px solid var(--line);
 padding:20px 14px;
 display:flex;
 flex-direction:column;
 height:100vh;
 position:sticky;
 top:0;
}

.side-brand {
 display:flex;
 align-items:center;
 gap:10px;
 padding:4px 6px 20px;
}

.side-logo {
 width:36px;
 height:36px;
 border-radius:10px;
 background:linear-gradient(135deg,var(--blue),var(--blue-dark));
 color:#fff;
 display:flex;
 align-items:center;
 justify-content:center;
 font-weight:800;
 font-size:16px;
}

.side-brand strong { font-size:12px; display:block; }
.side-brand span { display:block; color:var(--muted); font-size:11px; font-weight:500; }

.nav-title {
 color:#94a3b8;
 font-size:10px;
 font-weight:800;
 padding:10px 8px 6px;
 text-transform:uppercase;
 letter-spacing:1px;
}

.nav-item {
 border:0;
 width:100%;
 text-align:left;
 background:transparent;
 padding:10px 12px;
 border-radius:10px;
 color:#64748b;
 font-size:13px;
 font-weight:600;
 margin-bottom:2px;
 transition:.15s;
 display:flex;
 align-items:center;
 gap:8px;
}

.nav-item.active, .nav-item:hover {
 background:var(--blue-soft);
 color:var(--blue-dark);
}

.side-bottom {
 margin-top:auto;
 padding-top:12px;
 border-top:1px solid var(--line);
}

.nav-logout {
 color:#dc2626 !important;
 background:#fee2e2 !important;
 font-weight:700 !important;
}

.nav-logout:hover {
 background:#fca5a5 !important;
}

.content {
 padding:24px 32px;
 max-width:1300px;
 width:100%;
 margin:0 auto;
}

.topbar {
 display:flex;
 justify-content:space-between;
 align-items:center;
 margin-bottom:24px;
}

.topbar-mobile-logout {
 display:none;
}

.eyebrow {
 color:var(--muted);
 font-size:11px;
 font-weight:700;
 letter-spacing:.8px;
 margin-bottom:4px;
}

.topbar h1 {
 margin:0;
 font-size:24px;
 letter-spacing:-.5px;
 font-weight:800;
}

.user-pill {
 background:#fff;
 border:1px solid var(--line);
 border-radius:14px;
 padding:6px 12px 6px 8px;
 display:flex;
 align-items:center;
 gap:10px;
}

.user-pill strong { font-size:12px; color:var(--ink); }
.user-pill small { display:block; color:var(--muted); font-weight:500; }

.mobile-user-card {
 display: none;
}

.stats {
 display:grid;
 grid-template-columns:repeat(4,1fr);
 gap:12px;
 margin-bottom:24px;
}

.stat {
 background:#fff;
 border:1px solid var(--line);
 border-radius:16px;
 padding:16px;
 box-shadow:var(--shadow);
}

.stat-label { color:var(--muted); font-size:10px; font-weight:800; letter-spacing:.5px; }
.stat-value { font-size:24px; font-weight:800; margin-top:4px; color:var(--ink); letter-spacing:-.5px; }
.stat-foot { color:var(--muted); font-size:11px; margin-top:2px; font-weight:500; }

.projects {
 display:grid;
 grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
 gap:16px;
}

.project {
 background:#fff;
 border:1px solid var(--line);
 border-radius:18px;
 padding:18px;
 box-shadow:var(--shadow);
 display:flex;
 flex-direction:column;
}

.project-head {
 display:flex;
 justify-content:space-between;
 align-items:center;
 margin-bottom:12px;
}

.project-head h3 { margin:0; font-size:14px; font-weight:800; }

.badge {
 padding:4px 8px;
 border-radius:12px;
 font-size:10px;
 font-weight:800;
}

.badge.ok { color:#065f46; background:#d1fae5; }
.badge.pending { color:#92400e; background:#fef3c7; }
.badge.empty { color:#475569; background:#f1f5f9; }

.progress {
 height:6px;
 border-radius:99px;
 background:#f1f5f9;
 overflow:hidden;
 margin:10px 0;
}

.progress > div {
 height:100%;
 background:linear-gradient(90deg,var(--blue),var(--green));
 border-radius:99px;
}

.project-count {
 font-size:11px;
 color:var(--muted);
 display:flex;
 justify-content:space-between;
 font-weight:600;
}

.employee-mini {
 display:flex;
 align-items:center;
 gap:8px;
 padding:8px 0;
 border-bottom:1px solid #f1f5f9;
}

.employee-mini:last-child { border-bottom:0; }

.mini-dot {
 width:7px;
 height:7px;
 border-radius:50%;
 background:var(--red);
 flex-shrink:0;
}

.mini-dot.ok { background:var(--green); }

.mini-name { flex:1; font-size:12px; font-weight:600; color:var(--ink); }

.item-actions { display:flex; align-items:center; gap:4px; }

.icon-btn {
 border:1px solid var(--line);
 background:#fff;
 border-radius:6px;
 padding:4px 7px;
 color:var(--muted);
 font-size:11px;
 transition:.15s ease;
}

.icon-btn:hover { border-color:var(--blue); color:var(--blue-dark); background:var(--blue-soft); }
.icon-btn.delete-btn:hover { border-color:var(--red); color:#b91c1c; background:var(--red-soft); }

.actions { display:flex; gap:6px; margin-top:auto; padding-top:12px; }

.action-btn {
 flex:1;
 border:0;
 border-radius:10px;
 padding:10px;
 font-size:11px;
 font-weight:800;
 transition:.2s;
}

.action-main { background:var(--blue); color:#fff; }
.action-main:hover { background:var(--blue-dark); }

.toast {
 position:fixed;
 right:20px;
 top:20px;
 z-index:9999;
 background:var(--ink);
 color:#fff;
 padding:12px 18px;
 border-radius:12px;
 box-shadow:0 12px 24px rgba(15,23,42,.15);
 font-size:12px;
 font-weight:700;
 opacity:0;
 transform:translateY(-10px);
 pointer-events:none;
 transition:.25s ease;
}

.toast.show { opacity:1; transform:translateY(0); }

.upload-card {
 max-width:500px;
 background:#fff;
 border:1px solid var(--line);
 border-radius:20px;
 padding:24px;
 box-shadow:var(--shadow);
 margin:0 auto;
}

.dropzone {
 border:2px dashed #cbd5e1;
 border-radius:16px;
 padding:28px 16px;
 text-align:center;
 background:#fafafa;
 cursor:pointer;
 transition:all .2s ease;
 display:block;
}

.dropzone:hover { background:var(--blue-soft); border-color:var(--blue); }

.dropzone .big-icon {
 width:44px;
 height:44px;
 margin:0 auto 12px;
 border-radius:12px;
 background:#fff;
 display:flex;
 align-items:center;
 justify-content:center;
 font-size:20px;
 color:var(--blue);
 border:1px solid var(--line);
}

.dropzone strong { display:block; font-size:14px; color:var(--ink); font-weight:700; }
.dropzone span { display:block; color:var(--muted); font-size:11px; margin-top:4px; font-weight:500; }

.file-status-box {
 padding:12px 14px;
 background:var(--green-soft);
 border:1px solid #a7f3d0;
 border-radius:14px;
 margin-bottom:16px;
 display:flex;
 align-items:center;
 gap:10px;
}

.file-status-icon {
 width:32px;
 height:32px;
 border-radius:8px;
 background:#10b981;
 color:#fff;
 display:flex;
 align-items:center;
 justify-content:center;
 font-weight:800;
 font-size:13px;
}

.modal-overlay {
 position: fixed;
 top: 0;
 left: 0;
 width: 100vw;
 height: 100vh;
 background: rgba(15, 23, 42, 0.5);
 backdrop-filter: blur(4px);
 display: flex;
 align-items: center;
 justify-content: center;
 z-index: 10000;
 opacity: 0;
 pointer-events: none;
 transition: opacity .2s ease;
}

.modal-overlay:not(.hidden) { opacity: 1; pointer-events: auto; }

.modal-card {
 background: #fff;
 border-radius: 18px;
 padding: 24px;
 width: min(400px, 92%);
 box-shadow: 0 20px 40px -10px rgba(0,0,0,0.2);
 text-align: center;
}

.modal-icon {
 width: 44px;
 height: 44px;
 background: var(--red-soft);
 color: var(--red);
 border-radius: 50%;
 display: flex;
 align-items: center;
 justify-content: center;
 font-size: 18px;
 margin: 0 auto 12px;
}

.modal-icon.email-icon { background: var(--blue-soft); color: var(--blue); }

.modal-card h3 { margin: 0 0 6px; font-size: 16px; font-weight: 800; }
.modal-card p { margin: 0 0 16px; font-size: 12px; color: var(--muted); line-height: 1.5; }

.modal-actions { display: flex; gap: 8px; margin-top: 16px; }

.modal-btn {
 flex: 1;
 padding: 10px;
 border-radius: 10px;
 border: 0;
 font-weight: 700;
 font-size: 12px;
}

.btn-cancel { background: #f1f5f9; color: var(--muted); }
.btn-danger { background: var(--red); color: #fff; }
.btn-primary-modal { background: var(--blue); color: #fff; }

.hidden { display:none !important; }

@media(max-width:768px) {
 body { font-size: 16px; }
 .app-shell { grid-template-columns:1fr; }
 .sidebar { display:none; }
 
 .content { padding:16px; }
 .topbar { margin-bottom:16px; flex-wrap:wrap; gap:12px; justify-content:space-between; align-items:center; }
 .topbar h1 { font-size:22px; }
 
 .topbar-mobile-logout {
  display:inline-flex;
  align-items:center;
  gap:6px;
  background:#dc3545;
  color:#ffffff;
  padding:10px 18px;
  border-radius:8px;
  text-decoration:none;
  font-size:14px;
  font-weight:800;
  border:2px solid #a71d2a;
  box-shadow:0 2px 4px rgba(0,0,0,0.15);
 }

 .mobile-user-card {
  display: block;
  background-color: #0056b3;
  color: #ffffff;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
 }

 .mobile-user-card .user-name {
  font-size: 1.35rem;
  font-weight: 800;
  display: block;
  margin-bottom: 4px;
  color: #ffffff;
 }

 .mobile-user-card .user-role {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
 }

 .user-pill { display:none; }
 
 .stats { grid-template-columns:1fr 1fr; gap:8px; margin-bottom:16px; }
 .stat { padding:12px; border-radius:14px; }
 .stat-value { font-size:20px; }
 
 .upload-card { padding:16px; border-radius:16px; }
 .dropzone { padding:20px 12px; }
 .dropzone .big-icon { width:36px; height:36px; font-size:16px; margin-bottom:8px; }
 .dropzone strong { font-size:13px; }
 
 .login-shell { grid-template-columns:1fr; border-radius:18px; }
 .login-brand { padding:24px; min-height:180px; }
 .brand-copy h1 { font-size:26px; }
 .login-panel { padding:20px; }
}
</style>
"""

LOGIN_HTML = STYLE + """
<div class="page">
 <div class="login-shell">

 <section class="login-brand">
 <div class="brand-logo">A</div>

 <div class="brand-copy">
 <h1>Controle<br>de Ponto.</h1>
 <p>
 Aplicativo para controle de Folha de Ponto dos projetos Andritz.
 </p>
 </div>

 <div class="brand-footer">Controle de Ponto • Ambiente interno</div>
 </section>

 <section class="login-panel">
 <h2 id="title">Acesso do colaborador</h2>
 <div class="subtitle" id="subtitle">
 Selecione seu nome para continuar. Não é necessário senha.
 </div>

 <div class="mode-tabs">
 <button class="mode-tab active" id="tabFuncionario" onclick="modoFuncionario()">
 Colaborador
 </button>
 <button class="mode-tab" id="tabAdmin" onclick="modoAdmin()">
 Administrador
 </button>
 </div>

 <div id="funcionarioBox">
 <div class="employee-search">
 <span>⌕</span>
 <input class="search-input" id="busca" placeholder="Pesquisar seu nome..." oninput="filtrar()">
 </div>

 <div class="employee-list" id="lista">
 {% for login, dados in colaboradores %}
 <button class="employee-btn" onclick="entrarFuncionario('{{ login }}')">
 <div class="avatar">{{ dados.nome[:2] }}</div>
 <div>
 <div class="employee-name">{{ dados.nome }}</div>
 <div class="employee-project">{{ dados.projeto }}</div>
 </div>
 </button>
 {% endfor %}
 </div>
 </div>

 <form id="adminBox" class="hidden" method="POST">
 {% if erro %}
 <div class="error">{{ erro }}</div>
 {% endif %}
 <div class="field">
 <label>USUÁRIO ADMINISTRATIVO</label>
 <input name="usuario" value="kauan.adm" autocomplete="username" required>
 </div>
 <div class="field">
 <label>SENHA</label>
 <input type="password" name="senha" autocomplete="current-password" required>
 </div>
 <button class="primary-btn" type="submit">Entrar no painel</button>
 </form>

 <form id="funcForm" method="POST" action="/login_funcionario">
 <input type="hidden" name="login_funcionario" id="loginFuncionario">
 </form>
 </section>
 </div>
</div>

<script>
function modoFuncionario() {
 document.getElementById('funcionarioBox').classList.remove('hidden');
 document.getElementById('funcForm').classList.remove('hidden');
 document.getElementById('adminBox').classList.add('hidden');
 document.getElementById('title').textContent='Acesso do colaborador';
 document.getElementById('subtitle').textContent='Selecione seu nome para continuar. Não é necessário senha.';
 document.getElementById('tabFuncionario').classList.add('active');
 document.getElementById('tabAdmin').classList.remove('active');
}

function modoAdmin() {
 document.getElementById('funcionarioBox').classList.add('hidden');
 document.getElementById('funcForm').classList.add('hidden');
 document.getElementById('adminBox').classList.remove('hidden');
 document.getElementById('title').textContent='Acesso administrativo';
 document.getElementById('subtitle').textContent='Área restrita para gestão do sistema.';
 document.getElementById('tabAdmin').classList.add('active');
 document.getElementById('tabFuncionario').classList.remove('active');
}

function entrarFuncionario(login) {
 document.getElementById('loginFuncionario').value = login;
 document.getElementById('funcForm').submit();
}

function filtrar() {
 const termo = document.getElementById('busca').value.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');
 document.querySelectorAll('.employee-btn').forEach(btn => {
 const texto = btn.innerText.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');
 btn.style.display = texto.includes(termo) ? 'flex' : 'none';
 });
}
</script>
"""

# =========================================================
# ROTAS
# =========================================================
@app.before_request
def verificar_sessao():
 rotas_abertas = {"login", "login_funcionario", "static"}
 if "usuario" not in session and request.endpoint not in rotas_abertas:
  return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
 erro = None

 if request.method == "POST":
  usuario = request.form.get("usuario", "").strip().lower()
  senha = request.form.get("senha", "")

  if usuario == "kauan.adm" and senha == ADMIN_PASSWORD:
   session.clear()
   session["usuario"] = "kauan.adm"
   session["nome"] = "Kauan Marin"
   session["projeto"] = "ADMIN"
   session["perfil"] = "ADMIN"
   session.permanent = True
   return redirect(url_for("admin"))

  erro = "Usuário ou senha incorretos."

 colaboradores = [
  (login, dados)
  for login, dados in USUARIOS.items()
  if dados["perfil"] == "COLABORADOR"
 ]

 return render_template_string(
  LOGIN_HTML,
  colaboradores=colaboradores,
  erro=erro
 )

@app.route("/login_funcionario", methods=["POST"])
def login_funcionario():
 login_func = request.form.get("login_funcionario", "").strip().lower()

 dados = USUARIOS.get(login_func)

 if not dados or dados["perfil"] != "COLABORADOR":
  return redirect(url_for("login"))

 session.clear()
 session["usuario"] = login_func
 session["nome"] = dados["nome"]
 session["projeto"] = dados["projeto"]
 session["perfil"] = "COLABORADOR"
 session.permanent = True

 return redirect(url_for("upload_colaborador"))

@app.route("/")
def index():
 if session.get("perfil") == "ADMIN":
  return redirect(url_for("admin"))
 return redirect(url_for("upload_colaborador"))

# =========================================================
# ADMIN
# =========================================================
@app.route("/admin")
def admin():
 if not exigir_admin():
  return redirect(url_for("login"))

 dados = {p: status_projeto(p) for p in PROJETOS}

 total = sum(len(v) for v in dados.values())
 enviados = sum(
  1 for lista in dados.values()
  for item in lista if item["status"] == "ok"
 )
 pendentes = total - enviados
 projetos_prontos = sum(
  1 for p in PROJETOS
  if dados[p] and all(x["status"] == "ok" for x in dados[p])
 )

 return render_template_string(
  STYLE + """
 <div class="app-shell">
 <aside class="sidebar">
 <div class="side-brand">
 <div class="side-logo">A</div>
 <div>
 <strong>CONTROLE DE PONTO</strong>
 <span>Gestão RH</span>
 </div>
 </div>
 <div class="nav-title">Menu</div>
 <button class="nav-item active">⌂ &nbsp; Visão geral</button>
 <button class="nav-item" onclick="document.getElementById('projetos').scrollIntoView({behavior:'smooth'})">▦ &nbsp; Projetos</button>

<div class="side-bottom">
 <button class="nav-item nav-logout" onclick="location.href='/logout'">↪ &nbsp; Sair da Conta</button>
 </div>
 </aside>

 <main class="content">
 <div class="mobile-user-card">
  <span class="user-name">Kauan Marin</span>
  <span class="user-role">Administrador</span>
 </div>

 <div class="topbar">
 <div>
 <div class="eyebrow">PAINEL ADMINISTRATIVO</div>
 <h1>Olá, Kauan 👋</h1>
 </div>
 <a href="/logout" class="topbar-mobile-logout">↪ Sair</a>
 <div class="user-pill">
 <div class="avatar">KM</div>
 <div>
 <strong>Kauan Marin</strong>
 <small>Administrador</small>
 </div>
 </div>
 </div>

 <div class="stats">
 <div class="stat">
 <div class="stat-label">COLABORADORES</div>
 <div class="stat-value">{{ total }}</div>
 <div class="stat-foot">cadastrados nos projetos</div>
 </div>
 <div class="stat">
 <div class="stat-label">RECEBIDOS</div>
 <div class="stat-value">{{ enviados }}</div>
 <div class="stat-foot">folhas neste mês</div>
 </div>
 <div class="stat">
 <div class="stat-label">PENDENTES</div>
 <div class="stat-value">{{ pendentes }}</div>
 <div class="stat-foot">aguardando envio</div>
 </div>
 <div class="stat">
 <div class="stat-label">PROJETOS PRONTOS</div>
 <div class="stat-value">{{ projetos_prontos }}</div>
 <div class="stat-foot">100% concluídos</div>
 </div>
 </div>

 <div id="projetos" class="projects">
 {% for p in projetos %}
 {% set lista = dados[p] %}
 {% set total_p = lista|length %}
 {% set ok_p = lista|selectattr('status','equalto','ok')|list|length %}
 {% set pendentes_p = total_p - ok_p %}
 {% set pct = ((ok_p / total_p) * 100)|round|int if total_p else 0 %}
 <div class="project">
 <div class="project-head">
 <h3>{{ p }}</h3>
 {% if total_p == 0 %}
 <span class="badge empty">SEM CADASTRO</span>
 {% elif ok_p == total_p %}
 <span class="badge ok">PRONTO</span>
 {% else %}
 <span class="badge pending">PENDENTE</span>
 {% endif %}
 </div>

 <div class="project-count">
 <span>{{ ok_p }} de {{ total_p }} recebidas</span>
 <strong>{{ pct }}%</strong>
 </div>

 <div class="progress"><div style="width:{{ pct }}%"></div></div>

 {% for item in lista %}
 <div class="employee-mini">
 <span class="mini-dot {% if item.status == 'ok' %}ok{% endif %}"></span>
 <span class="mini-name">{{ item.nome }}</span>

 {% if item.status == 'ok' %}
 <div class="item-actions">
 <button class="icon-btn" title="Visualizar" onclick="window.open('{{ url_for('ver_arquivo', projeto=p, login_user=item.login) }}','_blank')">↗</button>
 <button class="icon-btn delete-btn" title="Excluir arquivo" onclick="confirmarExclusao('{{ p }}', '{{ item.login }}', '{{ item.nome }}')">🗑</button>
 </div>
 {% endif %}
 </div>
 {% endfor %}

 {# PERMITE O ENVIO DESDE QUE HAJA AO MENOS 1 ARCHIVO ENTREGUE #}
 {% if ok_p > 0 %}
 <div class="actions">
 <button class="action-btn action-main" onclick="abrirModalEmail('{{ p }}', {{ ok_p }}, {{ pendentes_p }})">✉ Enviar ao RH</button>
 </div>
 {% endif %}
 </div>
 {% endfor %}
 </div>
 </main>
 </div>

 <div id="modalConfirmacao" class="modal-overlay hidden">
 <div class="modal-card">
 <div class="modal-icon">⚠️</div>
 <h3>Excluir folha de ponto?</h3>
 <p id="modalTexto">Esta ação não poderá ser desfeita.</p>
 <div class="modal-actions">
 <button class="modal-btn btn-cancel" onclick="fecharModalExclusao()">Cancelar</button>
 <button class="modal-btn btn-danger" id="btnConfirmarExcluir">Excluir</button>
 </div>
 </div>
 </div>

 <div id="modalEmail" class="modal-overlay hidden">
 <div class="modal-card">
 <div class="modal-icon email-icon">✉</div>
 <h3>Enviar ao RH</h3>
 <p id="modalEmailTexto">Confirme o envio dos arquivos do projeto.</p>

<div class="field" style="text-align:left;">
 <label>E-MAILS EM CÓPIA (CC)</label>
 <input type="text" id="inputCC" class="search-input" placeholder="exemplo@andritz.com, gestor@andritz.com" value="{{ email_cc_padrao }}">
 <small style="color:var(--muted);font-size:10px;margin-top:4px;display:block;">Separe múltiplos e-mails por vírgula.</small>
 </div>

 <div class="modal-actions">
 <button class="modal-btn btn-cancel" onclick="fecharModalEmail()">Cancelar</button>
 <button class="modal-btn btn-primary-modal" id="btnConfirmarEnviarEmail">Enviar Agora</button>
 </div>
 </div>
 </div>

 <div id="toast" class="toast"></div>

 <script>
 let rotaExclusaoPendencia = null;
 let projetoEnvioPendencia = null;

 function toast(msg, erro=false) {
 const t=document.getElementById('toast');
 t.textContent=msg;
 t.style.background=erro ? '#ef4444' : '#0f172a';
 t.classList.add('show');
 setTimeout(()=>t.classList.remove('show'),4500);
 }

 function confirmarExclusao(projeto, loginUser, nome) {
 rotaExclusaoPendencia = '/remover/' + encodeURIComponent(projeto) + '/' + encodeURIComponent(loginUser);
 document.getElementById('modalTexto').textContent = 'Tem certeza de que deseja excluir a folha de ponto de ' + nome + '?';
 document.getElementById('modalConfirmacao').classList.remove('hidden');
 }

 function fecharModalExclusao() {
 document.getElementById('modalConfirmacao').classList.add('hidden');
 rotaExclusaoPendencia = null;
 }

 document.getElementById('btnConfirmarExcluir').addEventListener('click', function() {
 if (rotaExclusaoPendencia) {
 window.location.href = rotaExclusaoPendencia;
 }
 });

 function abrirModalEmail(projeto, recebidas, pendentes) {
 projetoEnvioPendencia = projeto;
 let txt = 'Confirme o envio das ' + recebidas + ' folha(s) do projeto ' + projeto + ' para o RH.';
 if (pendentes > 0) {
 txt += ' (Atenção: existem ' + pendentes + ' colaborador(es) com entrega pendente).';
 }
 document.getElementById('modalEmailTexto').textContent = txt;
 document.getElementById('modalEmail').classList.remove('hidden');
 }

 function fecharModalEmail() {
 document.getElementById('modalEmail').classList.add('hidden');
 projetoEnvioPendencia = null;
 }

 document.getElementById('btnConfirmarEnviarEmail').addEventListener('click', async function() {
 if (!projetoEnvioPendencia) return;

const btn = this;
 const original = btn.textContent;
 const ccInput = document.getElementById('inputCC').value;
 const emailsCc = ccInput.split(',').map(e => e.trim()).filter(e => e.length > 0);

 btn.disabled = true;
 btn.textContent = 'Enviando...';

 try {
 const r = await fetch('/enviar_email', {
 method: 'POST',
 headers: {'Content-Type': 'application/json'},
 body: JSON.stringify({
 projeto: projetoEnvioPendencia,
 emails_cc: emailsCc
 })
 });
 const data = await r.json();
 toast(data.msg, !data.ok);
 fecharModalEmail();
 if(data.ok) setTimeout(() => location.reload(), 1500);
 } catch(e) {
 toast('Não foi possível conectar ao servidor.', true);
 } finally {
 btn.disabled = false;
 btn.textContent = original;
 }
 });

 async function atualizar() {
 try {
 const r=await fetch('/status_projetos');
 if(!r.ok) return;
 const data=await r.json();
 } catch(e) {}
 }
 setInterval(atualizar, 15000);
 </script>
 """,
  projetos=PROJETOS,
  dados=dados,
  total=total,
  enviados=enviados,
  pendentes=pendentes,
  projetos_prontos=projetos_prontos,
  email_cc_padrao=", ".join(EMAIL_CONFIG["copia"])
 )

@app.route("/status_projetos")
def status_projetos():
 if not exigir_admin():
  return jsonify({}), 403
 return jsonify({p: status_projeto(p) for p in PROJETOS})

@app.route("/enviar_email", methods=["POST"])
def enviar_email():
 if not exigir_admin():
  return jsonify({"ok": False, "msg": "Acesso negado."}), 403
 data = request.get_json(silent=True) or {}
 projeto = data.get("projeto", "")
 emails_cc = data.get("emails_cc", [])

 if projeto not in PROJETOS:
  return jsonify({"ok": False, "msg": "Projeto inválido."}), 400
 ok, msg = enviar_email_projeto(projeto, emails_cc=emails_cc)
 return jsonify({"ok": ok, "msg": msg})

# =========================================================
# COLABORADOR (ACEITA JPEG E JPG)
# =========================================================
@app.route("/upload", methods=["GET", "POST"])
def upload_colaborador():
 if session.get("perfil") != "COLABORADOR":
  return redirect(url_for("login"))

 sucesso = False
 erro = None

 if request.method == "POST":
  file = request.files.get("arquivo")
  if not file or not file.filename:
   erro = "Selecione uma folha antes de continuar."
  else:
   pasta = os.path.join(
    BASE, session["projeto"], get_mes_atual()
   )
   os.makedirs(pasta, exist_ok=True)
   ext = os.path.splitext(file.filename)[1].lower()

   # PERMITE PDF, EXCEL, WORD, JPEG E JPG
   permitidos = {".pdf", ".xlsx", ".xls", ".docx", ".doc", ".jpg", ".jpeg"}
   if ext not in permitidos:
    erro = "Formato não permitido. Use PDF, Excel, Word, JPG ou JPEG."
   else:
    nome_arq = f"{session['usuario']}{ext}"
    file.save(os.path.join(pasta, nome_arq))
    sucesso = True

 arq_atual = arquivo_do_login(session["projeto"], session["usuario"])

 return render_template_string(
  STYLE + """
 <div class="app-shell">
 <aside class="sidebar">
 <div class="side-brand">
 <div class="side-logo">A</div>
 <div>
 <strong>CONTROLE DE PONTO</strong>
 <span>Área do colaborador</span>
 </div>
 </div>
 <div class="nav-title">Meu acesso</div>
 <button class="nav-item active">▣ &nbsp; Minha folha</button>

 <div class="side-bottom">
 <button class="nav-item nav-logout" onclick="location.href='/logout'">↪ &nbsp; Sair da Conta</button>
 </div>
 </aside>

 <main class="content">
 <div class="mobile-user-card">
  <span class="user-name">{{ nome }}</span>
  <span class="user-role">Colaborador</span>
 </div>

 <div class="topbar">
 <div>
 <div class="eyebrow">{{ projeto }} • {{ mes }}</div>
 <h1>Olá, {{ nome.split(' ')[0] }} 👋</h1>
 </div>
 <a href="/logout" class="topbar-mobile-logout">↪ Sair</a>
 <div class="user-pill">
 <div class="avatar">{{ nome[:2] }}</div>
 <div>
 <strong>{{ nome }}</strong>
 <small>Colaborador</small>
 </div>
 </div>
 </div>

 {% if erro %}
 <div class="error">{{ erro }}</div>
 {% endif %}

 <div class="upload-card">
 <div class="eyebrow">ENVIO MENSAL</div>
 <h2 style="margin:0 0 6px;font-size:20px;font-weight:800;letter-spacing:-.5px;">Sua folha de ponto</h2>
 <p style="color:var(--muted);font-size:12px;line-height:1.5;margin:0 0 20px;">
 Envie sua folha referente ao período atual. O arquivo será identificado automaticamente.
 </p>

 {% if arq_atual %}
 <div class="file-status-box">
 <div class="file-status-icon">✓</div>
 <div>
 <div style="font-size:10px;color:#047857;font-weight:800;letter-spacing:.3px;">FOLHA ENVIADA</div>
 <div style="font-size:12px;font-weight:700;color:#065f46;margin-top:1px;">{{ arq_atual }}</div>
 </div>
 </div>
 {% endif %}

 <form method="POST" enctype="multipart/form-data">
 <label class="dropzone" for="arquivo">
 <div class="big-icon">↑</div>
 <strong id="arquivoNome">
 {% if arq_atual %}Substituir arquivo enviado{% else %}Selecionar arquivo de folha{% endif %}
 </strong>
 <span>Formatos aceitos: PDF, Excel, Word, JPG ou JPEG</span>
 <input id="arquivo" class="hidden" type="file" name="arquivo" accept=".pdf,.xlsx,.xls,.docx,.doc,.jpg,.jpeg" required onchange="mostrarArquivo(this)">
 </label>

 {% if arq_atual %}
 <button class="primary-btn btn-enviado" style="margin-top:16px;" type="submit">
 ✓ Enviado com sucesso (Reenviar)
 </button>
 {% else %}
 <button class="primary-btn" style="margin-top:16px;" type="submit">
 Enviar folha de ponto
 </button>
 {% endif %}
 </form>
 </div>
 </main>
 </div>

 <script>
 function mostrarArquivo(input) {
 const nome=input.files[0]?.name || 'Selecionar arquivo de folha';
 document.getElementById('arquivoNome').textContent=nome;
 }
 </script>
 """,
  projeto=session["projeto"],
  mes=get_mes_atual(),
  nome=session["nome"],
  sucesso=sucesso,
  erro=erro,
  arq_atual=arq_atual
 )

# =========================================================
# ARQUIVO / REMOVER / LOGOUT
# =========================================================
@app.route("/ver_arquivo/<projeto>/<login_user>")
def ver_arquivo(projeto, login_user):
 if not exigir_admin():
  return "Acesso negado.", 403
 if projeto not in PROJETOS or login_user not in USUARIOS:
  return "Arquivo inválido.", 404
 arq = arquivo_do_login(projeto, login_user)
 if arq:
  pasta = os.path.join(BASE, projeto, get_mes_atual())
  return send_from_directory(os.path.abspath(pasta), arq)
 return "Arquivo não encontrado.", 404

@app.route("/remover/<projeto>/<login_user>")
def remover(projeto, login_user):
 if not exigir_admin():
  return "Acesso negado.", 403
 arq = arquivo_do_login(projeto, login_user)
 if arq:
  pasta = os.path.join(BASE, projeto, get_mes_atual())
  try:
   os.remove(os.path.join(pasta, arq))
  except Exception as e:
   print("Erro ao remover:", e)
 return redirect(url_for("admin"))

@app.route("/logout")
def logout():
 session.clear()
 return redirect(url_for("login"))

if __name__ == "__main__":
 app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
