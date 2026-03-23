import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(page_title="Dashboard CEO - Havan 2026", layout="wide")

# ================= CSS (ESTILO DARK CORPORATIVO) =================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0F172A; color: white; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }

.kpi-box {
    background-color: #1E293B;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    border: 1px solid #334155;
    margin-bottom: 10px;
}
.kpi-label { font-size: 14px; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.kpi-number { font-size: 32px; font-weight: 800; margin-bottom: 10px; }
.progress-container { background-color: #334151; border-radius: 10px; height: 8px; width: 100%; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 10px; }

/* Botões de Detalhar nos Cards */
div.stButton > button {
    width: 100%; border-radius: 8px; background-color: #334155;
    color: #94A3B8; border: 1px solid #475569; font-size: 11px; height: 30px;
}
div.stButton > button:hover { background-color: #6366F1; color: white; }

/* Botão de Fechar Detalhamento */
.stButton > button[kind="secondary"] {
    background-color: #EF4444 !important;
    color: white !important;
    border: none !important;
    width: auto !important;
    padding: 0 20px !important;
}
</style>
""", unsafe_allow_html=True)

# ================= SISTEMA DE LOGIN =================
USERS = {"gerente": "havan2026", "funcionario": "havan"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "show_detalhes" not in st.session_state: st.session_state.show_detalhes = False

if not st.session_state.logged_in:
    st.title("🔐 Login Dashboard Havan")
    user = st.text_input("Usuário")
    pw = st.text_input("Senha", type="password")
    if st.button("Acessar Dashboard"):
        if user in USERS and USERS[user] == pw:
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Usuário ou senha incorretos")
    st.stop()

# ================= FUNÇÕES DE APOIO =================
def formata_br(valor):
    return f"{valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def kpi_card(col, label, value, progress=None, color="#FFFFFF", key=None):
    fill_color = "#10B981" if (progress is None or progress >= 1) else "#F87171"
    prog_html = f'<div class="progress-container"><div class="progress-fill" style="width:{min(max(progress,0),1)*100}%; background-color:{fill_color};"></div></div>' if progress is not None else ""
    col.markdown(f'<div class="kpi-box"><div class="kpi-label">{label}</div><div class="kpi-number" style="color:{color};">{value}</div>{prog_html}</div>', unsafe_allow_html=True)
    if key:
        if col.button(f"DETALHAR {label.upper()}", key=f"btn_{key}"):
            st.session_state.show_detalhes = True

# ================= DADOS =================
np.random.seed(42)
datas_range = pd.date_range("2026-03-01", "2026-03-22")
df = pd.DataFrame({
    "Data": datas_range,
    "Meta": np.random.randint(9000, 15000, len(datas_range)),
    "Realizado": np.random.randint(8000, 16000, len(datas_range)),
    "Crescimento": np.random.uniform(-1, 4, len(datas_range)),
    "Caminhao": np.random.randint(8, 18, len(datas_range))
})

# ================= SIDEBAR =================
st.sidebar.title("📅 Período")
data_ini = st.sidebar.date_input("Início", df["Data"].min())
data_fim = st.sidebar.date_input("Fim", df["Data"].max())
df_filtrado = df[(df["Data"] >= pd.to_datetime(data_ini)) & (df["Data"] <= pd.to_datetime(data_fim))].copy()
df_filtrado["Data_Str"] = df_filtrado["Data"].dt.strftime('%d/%m')

# ================= CÁLCULOS =================
meta_tot, real_tot = df_filtrado["Meta"].sum(), df_filtrado["Realizado"].sum()
ating_tot = real_tot / meta_tot if meta_tot > 0 else 0

# ================= GRID DE KPIs =================
c1, c2, c3 = st.columns(3)
kpi_card(c1, "💰 Meta Total", f"R$ {formata_br(meta_tot)}")
kpi_card(c2, "📈 Realizado", f"R$ {formata_br(real_tot)}", key="realizado")
kpi_card(c3, "🎯 Atingimento", f"{ating_tot:.2%}", progress=ating_tot, color="#10B981" if ating_tot >= 1 else "#F87171")

c4, c5, c6 = st.columns(3)
kpi_card(c4, "📊 Crescimento", f"{df_filtrado['Crescimento'].mean():.2f}%", progress=(df_filtrado['Crescimento'].mean()/5 + 0.5))
kpi_card(c5, "🚚 Caminhões", formata_br(df_filtrado["Caminhao"].sum()), color="#38BDF8")
kpi_card(c6, "Status", "META BATIDA" if ating_tot >= 1 else "ABAIXO DA META", color="#FACC15" if ating_tot >= 1 else "#F87171")

# ================= SEÇÃO DE DETALHAMENTO DINÂMICO =================
if st.session_state.show_detalhes:
    st.markdown("---")
    head_col1, head_col2 = st.columns([0.85, 0.15])
    with head_col1:
        st.markdown("### 🔍 Detalhamento Diário do Realizado")
    with head_col2:
        if st.button("✖ FECHAR", type="secondary"):
            st.session_state.show_detalhes = False
            st.rerun()
    
    st.dataframe(df_filtrado[["Data", "Realizado", "Meta"]].sort_values("Data"), use_container_width=True, hide_index=True)

st.markdown("---")

# ================= GRÁFICOS =================
col_esq, col_dir = st.columns(2)
with col_esq:
    fig_barra = px.bar(df_filtrado, x="Data_Str", y=["Meta", "Realizado"], barmode="group", template="plotly_dark", color_discrete_sequence=["#6366F1", "#10B981"])
    fig_barra.update_layout(title="Performance Diária", xaxis_title=None, yaxis_title="Valor", legend=dict(orientation="h", y=1.1, x=1))
    st.plotly_chart(fig_barra, use_container_width=True)

with col_dir:
    fig_rosca = px.pie(values=[real_tot, max(0, meta_tot - real_tot)], names=['Realizado', 'Pendente'], hole=.6, color_discrete_sequence=["#10B981", "#334155"], template="plotly_dark")
    fig_rosca.update_layout(title="Atingimento Global")
    st.plotly_chart(fig_rosca, use_container_width=True)

if st.sidebar.button("Sair"):
    st.session_state.logged_in = False
    st.rerun()
