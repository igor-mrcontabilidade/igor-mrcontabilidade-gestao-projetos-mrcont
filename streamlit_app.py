import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import bcrypt
from datetime import date, datetime
from supabase import create_client, Client

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gestão de Projetos — MR Cont",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Supabase ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

sb = get_supabase()

# ── Paleta MR Cont ────────────────────────────────────────────────────────────
C_BG     = "#F0F2F5"
C_WHITE  = "#FFFFFF"
C_TITLE  = "#111111"
C_BODY   = "#4A4A4A"
C_ACCENT = "#1A6B7C"
C_NAVY   = "#1B2D4F"
C_TERRA  = "#C1440E"
C_NÉVOA  = "#E0F0F3"
C_BORDER = "#D5D9E0"

STATUS_MICRO_OPTS = ["A INICIAR", "EM ANDAMENTO", "CONCLUÍDO", "PAUSADO", "CANCELADO"]
STATUS_MACRO_OPTS = ["A INICIAR", "EM ANDAMENTO", "CONCLUÍDO", "PAUSADO", "CANCELADO"]
RESPONSAVEIS      = ["MARCOS", "IGOR", "MARIANA", "EQUIPE", "MARCOS/IGOR"]

STATUS_COLOR = {
    "A INICIAR":    "#6B87A8",
    "EM ANDAMENTO": "#1A6B7C",
    "CONCLUÍDO":    "#2C6E49",
    "PAUSADO":      "#5A5A5A",
    "CANCELADO":    "#C1440E",
}

CLIENTES_CADASTRADOS = sorted([
    "BGSN Participações LTDA",
    "Bruno Gabriel Santos Naziazeno",
    "Bruno Hiroyuki Oiko",
    "Carlos Evandro Alves dos Santos",
    "Concretize Construtora Ltda",
    "Costa & Bertoli Engenharia Ambiental Ltda",
    "Doméstica – Carlos Evandro Alves dos Santos",
    "Doméstica – Pedro Romero",
    "Duloren Transportes, Serviços e Manutenção",
    "E.M.V Empreendimentos de Assis Ltda",
    "Edivaldo Roberto da Silva",
    "Eletro RMG",
    "Embreagens Forte Ltda",
    "ENS Serviços Médicos",
    "Flaus Importação e Comércio Ltda",
    "Geovana Aparecida Susigam Maia",
    "Grupo Expresso Adamantina",
    "Grupo Oliver",
    "Gustavo Gomes Advogados Associados",
    "HLE Silos e Representações Agrícolas Ltda",
    "Infotech",
    "Isadora Pedrone dos Santos",
    "Juria Software Ltda",
    "Luiz Felipe Ferreira",
    "M. A. da Silva Junior",
    "M. P. dos Santos Manutenção Agrícola",
    "M. R. Contabilidade e Consultoria",
    "Megatec Instalações Comerciais e Refrigeração LTDA",
    "MRB Consultoria Empresarial",
    "Patricia Sartori",
    "R N Dos S. Flauzino",
    "Saúde e Estética Masculina Assis",
    "SCP Recanto das Flores e Patrimônio de Afetação",
    "Sideout Assessoria",
    "Talachia Gestão e Consultoria Ltda",
    "Truck Center Mecânica Vitória",
    "Valdir Messias da Silva",
    "Vinicius Fermino de O. Pimentel",
    "Wagner Christani",
    "WSM Consultoria",
])

# ── CSS global ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  :root, html, html[data-theme="dark"], html[data-theme="light"] {{
    --background-color:           {C_BG}     !important;
    --secondary-background-color: {C_WHITE}  !important;
    --text-color:                 {C_TITLE}  !important;
    --primary-color:              {C_ACCENT} !important;
    color-scheme: light !important;
  }}
  html, body, .stApp {{
    background-color: {C_BG}   !important;
    color:            {C_TITLE}!important;
  }}
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewContainer"] > .main,
  section.main > div.block-container {{
    background-color: {C_BG}   !important;
    color:            {C_TITLE}!important;
  }}
  [data-testid="stSidebar"],
  [data-testid="stSidebar"] > div:first-child {{
    background-color: {C_WHITE}  !important;
    border-right: 1px solid {C_BORDER} !important;
  }}
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] div {{ color: {C_TITLE} !important; }}
  [data-baseweb="select"] > div,
  [data-baseweb="input"] input,
  [data-testid="stTextArea"] textarea,
  [data-testid="stDateInput"] input {{
    background-color: {C_WHITE}  !important;
    color:            {C_TITLE}  !important;
    border-color:     {C_BORDER} !important;
  }}
  [data-baseweb="select"] span,
  [data-baseweb="select"] [class*="singleValue"],
  [data-baseweb="select"] [class*="placeholder"] {{ color: {C_TITLE} !important; }}
  [role="option"] {{ background-color: {C_WHITE} !important; color: {C_TITLE} !important; }}
  [role="option"]:hover {{ background-color: {C_NÉVOA} !important; }}
  label {{ color: {C_BODY} !important; font-family: Arial, sans-serif !important;
           font-size: 13px !important; font-weight: 600 !important; }}
  [data-testid="stTabs"] button[role="tab"] {{
    color: {C_BODY} !important; font-family: Arial, sans-serif !important;
    font-size: 13px !important; font-weight: 600 !important; background: transparent !important;
  }}
  [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
    color: {C_ACCENT} !important; border-bottom: 2px solid {C_ACCENT} !important;
  }}
  button[kind="primary"] {{
    background-color: {C_ACCENT} !important; color: {C_WHITE} !important;
    border: none !important; font-family: Arial, sans-serif !important; font-weight: 700 !important;
  }}
  [data-testid="stDataEditor"] * {{
    font-family: Arial, sans-serif !important; font-size: 13px !important;
  }}
  hr {{ border-color: {C_BORDER} !important; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# AUTENTICAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
def hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_pw(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

def get_user(username: str):
    r = sb.table("usuarios").select("*").eq("username", username).execute()
    return r.data[0] if r.data else None

def login_page():
    st.markdown(
        f'<div style="background:{C_NAVY};padding:28px 32px;border-radius:12px;'
        f'margin-bottom:32px;border-left:4px solid {C_ACCENT};max-width:420px;margin:60px auto 32px">'
        f'<p style="font-family:Georgia,serif;font-size:24px;font-weight:400;color:#FFF;margin:0 0 4px 0">Gestão de Projetos</p>'
        f'<p style="font-family:Arial,sans-serif;font-size:11px;color:#94A3B8;letter-spacing:2.5px;text-transform:uppercase;margin:0">MR Cont · Martins Romero</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col = st.columns([1, 2, 1])[1]
    with col:
        st.markdown(
            f'<div style="background:{C_WHITE};border:1px solid {C_BORDER};border-radius:12px;padding:28px 28px 24px">',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p style="font-family:Georgia,serif;font-size:16px;color:{C_TITLE};margin:0 0 20px 0">Acesso ao Sistema</p>',
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username = st.text_input("Usuário", placeholder="seu.usuario")
            password = st.text_input("Senha",   placeholder="••••••••", type="password")
            submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)

        if submitted:
            user = get_user(username)
            if user and check_pw(password, user["password_hash"]):
                st.session_state.usuario     = user["username"]
                st.session_state.usuario_nome = user["nome"]
                st.session_state.role        = user["role"]
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
        st.markdown("</div>", unsafe_allow_html=True)


# Verificar sessão
if "usuario" not in st.session_state:
    st.session_state.usuario = None
    st.session_state.role    = None

if st.session_state.usuario is None:
    login_page()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE DADOS — Supabase
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def load_data() -> pd.DataFrame:
    r = sb.table("projetos").select("*").order("id").execute()
    if not r.data:
        return pd.DataFrame(columns=[
            "id","cliente","projeto_macro","micro_etapa",
            "prazo_micro","responsavel","status_micro","prazo_entrega","status_macro"
        ])
    df = pd.DataFrame(r.data)
    df["prazo_micro"]   = pd.to_datetime(df["prazo_micro"],   errors="coerce")
    df["prazo_entrega"] = pd.to_datetime(df["prazo_entrega"], errors="coerce")
    return df

def save_row(row: dict):
    if "id" in row and row["id"]:
        rid = row.pop("id")
        sb.table("projetos").update(row).eq("id", rid).execute()
    else:
        row.pop("id", None)
        sb.table("projetos").insert(row).execute()
    st.cache_data.clear()

def delete_row(row_id: int):
    sb.table("projetos").delete().eq("id", row_id).execute()
    st.cache_data.clear()

def upsert_dataframe(df_edited: pd.DataFrame):
    rows = []
    for _, r in df_edited.iterrows():
        row = {
            "cliente":       r["cliente"],
            "projeto_macro": r["projeto_macro"],
            "micro_etapa":   r["micro_etapa"],
            "prazo_micro":   r["prazo_micro"].strftime("%Y-%m-%d") if pd.notna(r["prazo_micro"]) else None,
            "responsavel":   r["responsavel"],
            "status_micro":  r["status_micro"],
            "prazo_entrega": r["prazo_entrega"].strftime("%Y-%m-%d") if pd.notna(r["prazo_entrega"]) else None,
            "status_macro":  r["status_macro"],
        }
        if "id" in r and pd.notna(r["id"]):
            row["id"] = int(r["id"])
        rows.append(row)
    sb.table("projetos").upsert(rows).execute()
    st.cache_data.clear()


# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE USUÁRIOS — apenas master
# ══════════════════════════════════════════════════════════════════════════════
def list_users():
    r = sb.table("usuarios").select("id,username,nome,role,created_at").order("created_at").execute()
    return r.data or []

def create_user(username: str, nome: str, password: str, role: str):
    sb.table("usuarios").insert({
        "username":      username,
        "nome":          nome,
        "password_hash": hash_pw(password),
        "role":          role,
    }).execute()

def delete_user(uid: int):
    sb.table("usuarios").delete().eq("id", uid).execute()

def change_password(username: str, new_pw: str):
    sb.table("usuarios").update({"password_hash": hash_pw(new_pw)}).eq("username", username).execute()


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS VISUAIS
# ══════════════════════════════════════════════════════════════════════════════
def badge(status: str) -> str:
    bg = STATUS_COLOR.get(status, "#6B87A8")
    return (
        f'<span style="display:inline-block;padding:3px 12px;border-radius:20px;'
        f'background:{bg};color:#FFF;font-family:Arial,sans-serif;'
        f'font-size:11px;font-weight:700;letter-spacing:0.5px;white-space:nowrap">'
        f'{status}</span>'
    )

def prazo_style(dt, today: date) -> str:
    if pd.isna(dt):
        return f"color:{C_BODY};font-family:Arial,sans-serif"
    d    = dt.date() if hasattr(dt, "date") else dt
    diff = (d - today).days
    if diff < 0:   return f"color:{C_TERRA};font-weight:700;font-family:Arial,sans-serif"
    if diff <= 7:  return f"color:#9A6200;font-weight:700;font-family:Arial,sans-serif"
    return             f"color:{C_BODY};font-family:Arial,sans-serif"

def card(content: str, accent: bool = False) -> str:
    b = f"border-left:4px solid {C_ACCENT};" if accent else ""
    return (
        f'<div style="background:{C_WHITE};{b}border:1px solid {C_BORDER};'
        f'border-radius:10px;padding:20px 24px;margin-bottom:16px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.07)">{content}</div>'
    )

def section_block(content: str) -> str:
    return (
        f'<div style="background:{C_BG};border:1px solid {C_BORDER};'
        f'border-radius:8px;padding:14px 18px;margin:10px 0">{content}</div>'
    )

def metric_html(value, label: str, color: str = C_TITLE) -> str:
    return (
        f'<div style="background:{C_WHITE};border:1px solid {C_BORDER};border-radius:10px;'
        f'padding:18px 20px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.06)">'
        f'<div style="font-family:Georgia,serif;font-size:32px;font-weight:400;'
        f'color:{color};line-height:1;margin-bottom:6px">{value}</div>'
        f'<div style="font-family:Arial,sans-serif;font-size:10px;color:#6B87A8;'
        f'letter-spacing:2px;text-transform:uppercase">{label}</div>'
        f'</div>'
    )

def pct_concluido(df_proj: pd.DataFrame) -> int:
    n = len(df_proj)
    return int((df_proj["status_micro"] == "CONCLUÍDO").sum() / n * 100) if n else 0


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
today = date.today()
df    = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="background:{C_NAVY};padding:18px 28px;border-radius:10px;'
    f'margin-bottom:24px;border-left:4px solid {C_ACCENT};'
    f'display:flex;justify-content:space-between;align-items:center">'
    f'<div>'
    f'<p style="font-family:Georgia,serif;font-size:22px;font-weight:400;color:#FFF;margin:0 0 3px 0">Gestão de Projetos</p>'
    f'<p style="font-family:Arial,sans-serif;font-size:11px;color:#94A3B8;letter-spacing:2px;text-transform:uppercase;margin:0">'
    f'MR Cont · Martins Romero Contabilidade e Consultoria</p>'
    f'</div>'
    f'<div style="text-align:right">'
    f'<p style="font-family:Arial,sans-serif;font-size:12px;color:#94A3B8;margin:0">'
    f'👤 {st.session_state.usuario_nome}</p>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<p style="font-family:Georgia,serif;font-size:15px;color:{C_TITLE};margin-bottom:16px">Filtros</p>',
        unsafe_allow_html=True,
    )
    clientes_ativos  = sorted(df["cliente"].unique().tolist()) if not df.empty else []
    clientes_sidebar = sorted(set(CLIENTES_CADASTRADOS + clientes_ativos))
    f_cliente = st.selectbox("Cliente",      ["Todos"] + clientes_sidebar)
    f_resp    = st.selectbox("Responsável",  ["Todos"] + sorted(df["responsavel"].unique().tolist()) if not df.empty else ["Todos"])
    f_status  = st.selectbox("Status Micro", ["Todos"] + STATUS_MICRO_OPTS + ["⚠️ ATRASADAS"])
    st.divider()
    st.markdown(
        f'<p style="font-size:11px;color:{C_BODY};letter-spacing:1.5px;text-transform:uppercase;font-family:Arial,sans-serif">'
        f'Hoje: {today.strftime("%d/%m/%Y")}</p>',
        unsafe_allow_html=True,
    )
    st.divider()
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.usuario      = None
        st.session_state.usuario_nome = None
        st.session_state.role         = None
        st.rerun()

# ── Filtrar ───────────────────────────────────────────────────────────────────
dfv = df.copy()
if not dfv.empty:
    if f_cliente != "Todos":
        dfv = dfv[dfv["cliente"] == f_cliente]
    if f_resp != "Todos":
        dfv = dfv[dfv["responsavel"] == f_resp]
    if f_status == "⚠️ ATRASADAS":
        dfv = dfv[
            (dfv["status_micro"] != "CONCLUÍDO") &
            dfv["prazo_micro"].apply(lambda x: not pd.isna(x) and x.date() < today)
        ]
    elif f_status != "Todos":
        dfv = dfv[dfv["status_micro"] == f_status]

# ── Métricas ──────────────────────────────────────────────────────────────────
total      = len(dfv)
concluidos = int((dfv["status_micro"] == "CONCLUÍDO").sum()) if not dfv.empty else 0
andamento  = int((dfv["status_micro"] == "EM ANDAMENTO").sum()) if not dfv.empty else 0
atrasados  = int(dfv[dfv["status_micro"] != "CONCLUÍDO"]["prazo_micro"]
                 .apply(lambda x: not pd.isna(x) and x.date() < today).sum()) if not dfv.empty else 0

cols = st.columns(5)
for col, val, lbl, cor in [
    (cols[0], dfv["projeto_macro"].nunique() if not dfv.empty else 0, "PROJETOS ATIVOS", C_TITLE),
    (cols[1], total,      "MICRO ETAPAS",  C_TITLE),
    (cols[2], andamento,  "EM ANDAMENTO",  C_ACCENT),
    (cols[3], concluidos, "CONCLUÍDAS",    "#2C6E49"),
    (cols[4], atrasados,  "ATRASADAS",     C_TERRA if atrasados else C_TITLE),
]:
    col.markdown(metric_html(val, lbl, cor), unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── Abas ──────────────────────────────────────────────────────────────────────
abas = ["  📋  Projetos  ", "  📊  Gráficos  ", "  ✏️  Editar  ", "  ➕  Novo Registro  "]
if st.session_state.role == "master":
    abas.append("  👥  Usuários  ")

tabs = st.tabs(abas)
tab_proj, tab_graf, tab_edit, tab_novo = tabs[0], tabs[1], tabs[2], tabs[3]
tab_users = tabs[4] if st.session_state.role == "master" else None


# ══════════════════════════════════════════════════════════════════════════════
# ABA 1 — PROJETOS
# ══════════════════════════════════════════════════════════════════════════════
with tab_proj:
    if dfv.empty:
        st.info("Nenhuma etapa encontrada para os filtros selecionados.")
    else:
        for cliente in dfv["cliente"].unique():
            df_cli = dfv[dfv["cliente"] == cliente]
            html_cli = (
                f'<p style="font-family:Arial,sans-serif;font-size:10px;color:#6B87A8;'
                f'letter-spacing:2px;text-transform:uppercase;margin:0 0 4px 0">CLIENTE</p>'
                f'<p style="font-family:Georgia,serif;font-size:17px;color:{C_TITLE};margin:0 0 12px 0">{cliente}</p>'
                f'<hr style="border:none;border-top:1px solid {C_BORDER};margin:0 0 14px 0">'
            )
            for projeto in df_cli["projeto_macro"].unique():
                df_proj   = df_cli[df_cli["projeto_macro"] == projeto]
                prazo_e   = df_proj["prazo_entrega"].iloc[0]
                sm        = df_proj["status_macro"].iloc[0]
                pct       = pct_concluido(df_proj)
                prazo_str = prazo_e.strftime("%d/%m/%Y") if not pd.isna(prazo_e) else "—"
                p_sty     = prazo_style(prazo_e, today)
                bar_c     = C_ACCENT if pct < 100 else "#2C6E49"

                proj_hdr = (
                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:6px">'
                    f'<p style="font-family:Georgia,serif;font-size:14px;color:{C_TITLE};margin:0">{projeto}</p>'
                    f'<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">'
                    f'<span style="{p_sty}">📅 {prazo_str}</span>'
                    f'{badge(sm)}'
                    f'<span style="font-family:Arial,sans-serif;font-size:12px;color:{C_ACCENT};font-weight:600">{pct}% concluído</span>'
                    f'</div></div>'
                    f'<div style="background:#E4E8EF;border-radius:4px;height:5px;margin-bottom:12px">'
                    f'<div style="background:{bar_c};width:{pct}%;height:5px;border-radius:4px"></div>'
                    f'</div>'
                )
                th_s  = (f"background:{C_BG};color:{C_BODY};font-family:Arial,sans-serif;"
                         f"font-size:10px;font-weight:700;letter-spacing:1.5px;"
                         f"text-transform:uppercase;padding:9px 12px;border-bottom:1px solid {C_BORDER}")
                td_b  = (f"padding:9px 12px;border-bottom:1px solid #EEF0F4;"
                         f"background:{C_WHITE};font-family:Arial,sans-serif;font-size:13px")
                rows  = ""
                for _, row in df_proj.iterrows():
                    pm    = row["prazo_micro"]
                    pm_s  = pm.strftime("%d/%m/%Y") if not pd.isna(pm) else "—"
                    rows += (
                        f'<tr>'
                        f'<td style="{td_b};color:{C_TITLE};width:48%">{row["micro_etapa"]}</td>'
                        f'<td style="{td_b};{prazo_style(pm,today)};text-align:center;width:15%">{pm_s}</td>'
                        f'<td style="{td_b};color:{C_NAVY};font-weight:600;text-align:center;width:15%">{row["responsavel"]}</td>'
                        f'<td style="{td_b};text-align:center;width:22%">{badge(row["status_micro"])}</td>'
                        f'</tr>'
                    )
                tabela = (
                    f'<table style="width:100%;border-collapse:collapse;margin-top:4px">'
                    f'<thead><tr>'
                    f'<th style="{th_s};text-align:left">MICRO ETAPA</th>'
                    f'<th style="{th_s};text-align:center">PRAZO</th>'
                    f'<th style="{th_s};text-align:center">RESPONSÁVEL</th>'
                    f'<th style="{th_s};text-align:center">STATUS</th>'
                    f'</tr></thead><tbody>{rows}</tbody></table>'
                )
                html_cli += section_block(proj_hdr + tabela)
            st.markdown(card(html_cli, accent=True), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ABA 2 — GRÁFICOS
# ══════════════════════════════════════════════════════════════════════════════
with tab_graf:
    FONT = dict(family="Arial, sans-serif", color=C_BODY, size=12)

    def fig_base(fig, title=""):
        fig.update_layout(
            title=dict(text=title, font=dict(family="Georgia, serif", size=15, color=C_TITLE), x=0, xref="paper"),
            paper_bgcolor=C_WHITE, plot_bgcolor=C_WHITE,
            font=FONT, margin=dict(t=52, b=30, l=10, r=10),
            showlegend=True,
            legend=dict(font=FONT, bgcolor=C_WHITE, bordercolor=C_BORDER, borderwidth=1),
        )
        fig.update_xaxes(color=C_BODY, linecolor=C_BORDER, gridcolor="#EAECF0")
        fig.update_yaxes(color=C_BODY, linecolor=C_BORDER, gridcolor="#EAECF0")
        return fig

    def wrap(fig, key):
        st.markdown(
            f'<div style="background:{C_WHITE};border:1px solid {C_BORDER};border-radius:10px;'
            f'padding:16px 18px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.06)">',
            unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=key)
        st.markdown("</div>", unsafe_allow_html=True)

    if dfv.empty:
        st.info("Nenhum dado para exibir.")
    else:
        g1, g2 = st.columns(2)
        with g1:
            cnt = dfv["status_micro"].value_counts().reset_index()
            cnt.columns = ["Status", "Qtd"]
            fig_d = go.Figure(go.Pie(
                labels=cnt["Status"], values=cnt["Qtd"], hole=0.55,
                marker=dict(colors=[STATUS_COLOR.get(s, "#6B87A8") for s in cnt["Status"]],
                            line=dict(color=C_WHITE, width=2)),
                textinfo="value+percent",
                textfont=dict(family="Arial, sans-serif", size=12, color="#FFF"),
            ))
            fig_d.add_annotation(text=f"<b>{total}</b><br>etapas", x=0.5, y=0.5, showarrow=False,
                                  font=dict(family="Georgia, serif", size=14, color=C_TITLE))
            fig_base(fig_d, "Distribuição por Status")
            fig_d.update_layout(height=300)
            wrap(fig_d, "donut")

        with g2:
            cnt_r = dfv.groupby(["responsavel", "status_micro"]).size().reset_index(name="Qtd")
            fig_r = px.bar(cnt_r, x="responsavel", y="Qtd", color="status_micro",
                           color_discrete_map=STATUS_COLOR, barmode="stack")
            fig_r.update_traces(marker_line_width=0)
            fig_base(fig_r, "Carga por Responsável")
            fig_r.update_layout(height=300, bargap=0.3, xaxis_title="", yaxis_title="")
            wrap(fig_r, "bar_resp")

        proj_stats = []
        for proj in dfv["projeto_macro"].unique():
            dp     = dfv[dfv["projeto_macro"] == proj]
            tp     = len(dp)
            conc   = int((dp["status_micro"] == "CONCLUÍDO").sum())
            and_p  = int((dp["status_micro"] == "EM ANDAMENTO").sum())
            atr_p  = int(dp[dp["status_micro"] != "CONCLUÍDO"]["prazo_micro"]
                         .apply(lambda x: not pd.isna(x) and x.date() < today).sum())
            pe     = dp["prazo_entrega"].iloc[0]
            proj_stats.append({
                "Projeto": proj, "Cliente": dp["cliente"].iloc[0],
                "Total": tp, "Concluído": conc, "Em Andamento": and_p,
                "A Iniciar": tp-conc-and_p, "Atrasadas": atr_p,
                "% Concluído": round(conc/tp*100) if tp else 0,
                "Prazo": pe.strftime("%d/%m/%Y") if not pd.isna(pe) else "—",
            })
        df_st = pd.DataFrame(proj_stats)

        fig_p = go.Figure()
        for lbl, cor in [("Concluído","#2C6E49"),("Em Andamento",C_ACCENT),("A Iniciar","#D0D6E0")]:
            fig_p.add_trace(go.Bar(name=lbl, y=df_st["Projeto"], x=df_st[lbl],
                                   orientation="h", marker=dict(color=cor, line=dict(width=0))))
        fig_base(fig_p, "Progresso por Projeto")
        fig_p.update_layout(height=max(260,len(proj_stats)*60), barmode="stack", bargap=0.35,
                            xaxis_title="", yaxis_title="", yaxis=dict(autorange="reversed"))
        wrap(fig_p, "bar_proj")

        gantt = []
        for proj in dfv["projeto_macro"].unique():
            dp = dfv[dfv["projeto_macro"] == proj].dropna(subset=["prazo_micro"])
            if dp.empty: continue
            gantt.append(dict(Task=proj, Start=dp["prazo_micro"].min(),
                              Finish=dp["prazo_entrega"].max() if not dp["prazo_entrega"].isna().all() else dp["prazo_micro"].max(),
                              Status=dp["status_macro"].iloc[0], Cliente=dp["cliente"].iloc[0]))
        if gantt:
            df_g = pd.DataFrame(gantt)
            fig_g = px.timeline(df_g, x_start="Start", x_end="Finish", y="Task",
                                color="Status", color_discrete_map=STATUS_COLOR, hover_data=["Cliente"])
            fig_g.update_traces(marker_line_width=0, opacity=0.85)
            fig_g.add_vline(x=datetime.combine(today, datetime.min.time()),
                            line_dash="dot", line_color=C_TERRA, line_width=1.5,
                            annotation_text="Hoje", annotation_font=dict(color=C_TERRA, size=11))
            fig_base(fig_g, "Linha do Tempo dos Projetos")
            fig_g.update_layout(height=max(260,len(gantt)*55), xaxis_title="", yaxis_title="",
                                yaxis=dict(autorange="reversed"))
            wrap(fig_g, "gantt")

        st.markdown(
            f'<div style="background:{C_WHITE};border:1px solid {C_BORDER};border-radius:10px;padding:18px 22px;margin-bottom:16px">'
            f'<p style="font-family:Georgia,serif;font-size:15px;color:{C_TITLE};margin:0 0 14px 0">Resumo por Projeto</p>',
            unsafe_allow_html=True)
        st.dataframe(df_st[["Cliente","Projeto","Total","Concluído","Em Andamento","A Iniciar","Atrasadas","% Concluído","Prazo"]],
                     use_container_width=True, hide_index=True,
                     column_config={
                         "% Concluído": st.column_config.ProgressColumn("% Concluído", min_value=0, max_value=100, format="%d%%"),
                         "Atrasadas":   st.column_config.NumberColumn("⚠️ Atrasadas"),
                     })
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ABA 3 — EDITAR
# ══════════════════════════════════════════════════════════════════════════════
with tab_edit:
    st.markdown(
        f'<div style="background:{C_NÉVOA};border-left:3px solid {C_ACCENT};border-radius:6px;'
        f'padding:10px 14px;margin-bottom:16px">'
        f'<p style="font-family:Arial,sans-serif;font-size:13px;color:{C_TITLE};margin:0">'
        f'Clique duas vezes em qualquer célula para editar. Clique em Salvar para confirmar.</p></div>',
        unsafe_allow_html=True)

    df_edit = dfv.copy()
    # Renomear colunas para exibição
    col_map = {
        "cliente": "Cliente", "projeto_macro": "Projeto Macro", "micro_etapa": "Micro Etapa",
        "prazo_micro": "Prazo Micro", "responsavel": "Responsável", "status_micro": "Status Micro",
        "prazo_entrega": "Prazo Entrega", "status_macro": "Status Macro",
    }
    df_show = df_edit.rename(columns=col_map)
    cols_show = ["id"] + list(col_map.values())
    df_show = df_show[[c for c in cols_show if c in df_show.columns]]

    edited = st.data_editor(
        df_show.reset_index(drop=True),
        use_container_width=True, num_rows="dynamic",
        column_config={
            "id":            st.column_config.NumberColumn("ID",            disabled=True, width="small"),
            "Cliente":       st.column_config.TextColumn("Cliente",         width="medium"),
            "Projeto Macro": st.column_config.TextColumn("Projeto Macro",   width="large"),
            "Micro Etapa":   st.column_config.TextColumn("Micro Etapa",     width="large"),
            "Prazo Micro":   st.column_config.DateColumn("Prazo Micro",     format="DD/MM/YYYY", width="small"),
            "Responsável":   st.column_config.SelectboxColumn("Responsável",options=RESPONSAVEIS+["MARIANA"], width="medium"),
            "Status Micro":  st.column_config.SelectboxColumn("Status Micro",options=STATUS_MICRO_OPTS, width="medium"),
            "Prazo Entrega": st.column_config.DateColumn("Prazo Entrega",   format="DD/MM/YYYY", width="small"),
            "Status Macro":  st.column_config.SelectboxColumn("Status Macro",options=STATUS_MACRO_OPTS, width="medium"),
        },
        hide_index=True, key="editor_main")

    if st.button("💾  Salvar alterações", type="primary"):
        col_back = {v: k for k, v in col_map.items()}
        df_save  = edited.rename(columns=col_back)
        upsert_dataframe(df_save)
        st.success("Salvo com sucesso.")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ABA 4 — NOVO REGISTRO
# ══════════════════════════════════════════════════════════════════════════════
with tab_novo:
    with st.form("form_novo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            clientes_form = sorted(set(CLIENTES_CADASTRADOS + (df["cliente"].unique().tolist() if not df.empty else [])))
            cli_sel = st.selectbox("Cliente", ["— Outro (digitar) —"] + clientes_form)
            cli_val = st.text_input("Nome do cliente") if cli_sel == "— Outro (digitar) —" else cli_sel
            prj_sel = st.selectbox("Projeto Macro", ["— Novo projeto —"] + (sorted(df["projeto_macro"].unique().tolist()) if not df.empty else []))
            prj_val = st.text_input("Nome do novo projeto") if prj_sel == "— Novo projeto —" else prj_sel
        with c2:
            micro = st.text_area("Descrição da Micro Etapa", height=90)
            resp  = st.selectbox("Responsável", RESPONSAVEIS + ["MARIANA"])
        c3, c4, c5, c6 = st.columns(4)
        with c3: pm_  = st.date_input("Prazo da Micro Etapa", value=today)
        with c4: sm_  = st.selectbox("Status Micro", STATUS_MICRO_OPTS)
        with c5: pe_  = st.date_input("Prazo de Entrega",     value=today)
        with c6: sma_ = st.selectbox("Status Macro",  STATUS_MACRO_OPTS)
        sub = st.form_submit_button("➕  Adicionar etapa", type="primary")

    if sub:
        if not cli_val or not prj_val or not micro:
            st.error("Preencha pelo menos Cliente, Projeto e a Micro Etapa.")
        else:
            save_row({
                "cliente": cli_val, "projeto_macro": prj_val, "micro_etapa": micro,
                "prazo_micro":   pm_.strftime("%Y-%m-%d"),
                "responsavel":   resp, "status_micro": sm_,
                "prazo_entrega": pe_.strftime("%Y-%m-%d"),
                "status_macro":  sma_,
            })
            st.success(f"Etapa adicionada ao projeto **{prj_val}**.")
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ABA 5 — USUÁRIOS (somente master)
# ══════════════════════════════════════════════════════════════════════════════
if tab_users is not None:
    with tab_users:
        st.markdown(
            f'<p style="font-family:Georgia,serif;font-size:16px;color:{C_TITLE};margin-bottom:20px">Gerenciamento de Usuários</p>',
            unsafe_allow_html=True)

        usuarios = list_users()
        if usuarios:
            df_u = pd.DataFrame(usuarios)
            df_u["created_at"] = pd.to_datetime(df_u["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
            st.dataframe(df_u[["username","nome","role","created_at"]].rename(columns={
                "username":"Usuário","nome":"Nome","role":"Perfil","created_at":"Criado em"
            }), use_container_width=True, hide_index=True)

        st.divider()
        st.markdown(
            f'<p style="font-family:Georgia,serif;font-size:14px;color:{C_TITLE};margin-bottom:12px">Criar novo usuário</p>',
            unsafe_allow_html=True)

        with st.form("form_usuario", clear_on_submit=True):
            uc1, uc2 = st.columns(2)
            with uc1:
                novo_username = st.text_input("Login (usuário)")
                novo_nome     = st.text_input("Nome completo")
            with uc2:
                novo_pw   = st.text_input("Senha", type="password")
                novo_role = st.selectbox("Perfil", ["user", "master"])
            criar = st.form_submit_button("➕  Criar usuário", type="primary")

        if criar:
            if not novo_username or not novo_nome or not novo_pw:
                st.error("Preencha todos os campos.")
            elif get_user(novo_username):
                st.error(f"Usuário '{novo_username}' já existe.")
            else:
                create_user(novo_username, novo_nome, novo_pw, novo_role)
                st.success(f"Usuário **{novo_username}** criado com sucesso.")
                st.rerun()

        st.divider()
        st.markdown(
            f'<p style="font-family:Georgia,serif;font-size:14px;color:{C_TITLE};margin-bottom:12px">Remover usuário</p>',
            unsafe_allow_html=True)
        if usuarios:
            usernames = [u["username"] for u in usuarios if u["username"] != st.session_state.usuario]
            if usernames:
                del_user = st.selectbox("Selecione o usuário para remover", usernames)
                if st.button("🗑️  Remover", type="primary"):
                    uid = next(u["id"] for u in usuarios if u["username"] == del_user)
                    delete_user(uid)
                    st.success(f"Usuário '{del_user}' removido.")
                    st.rerun()
