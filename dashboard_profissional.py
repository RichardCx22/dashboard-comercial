import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ================= CONFIG =================
st.set_page_config(page_title="Dashboard Full Responsivo", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
body { background-color: #0F172A; color: white; font-family: 'Arial'; }

/* KPI Box */
.kpi-box {
    background-color: #1E293B;
    border-radius: 16px;
    padding: 16px;
    margin: 4px 0;
    box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    transition: transform 0.2s;
    cursor: pointer;
}
.kpi-box:hover { transform: translateY(-5px); }

.kpi-label { font-size: 16px; color: #CBD5E1; text-align: center; }
.kpi-number { font-size: 28px; font-weight: bold; text-align: center; }

/* Progress bar */
.progress-bar { background-color: #374151; border-radius: 12px; height: 12px; width: 100%; margin-top: 6px; }
.progress-fill { height: 12px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
USERS = {"gerente":"havan2026", "funcionario":"havan"}
st.session_state.setdefault("logged_in", False)

if not st.session_state.logged_in:
    st.title("🔐 Login Dashboard")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.success("Login realizado!")
        else:
            st.error("Usuário ou senha incorretos")
    st.stop()

# ================= DADOS =================
np.random.seed(42)
datas = pd.date_range("2026-03-01", "2026-03-22")
df = pd.DataFrame({
    "Data": np.random.choice(datas, 50),
    "Meta": np.random.randint(5000, 20000, 50),
    "Realizado": np.random.randint(4000, 22000, 50),
    "Crescimento": np.random.uniform(-5, 10, 50),
    "Caminhao": np.random.randint(0, 10, 50)
})

# ================= SIDEBAR =================
st.sidebar.header("📅 Filtros")
data_inicio = st.sidebar.date_input("Data inicial", df["Data"].min())
data_fim = st.sidebar.date_input("Data final", df["Data"].max())
df_filtrado = df[(df["Data"] >= pd.to_datetime(data_inicio)) & 
                 (df["Data"] <= pd.to_datetime(data_fim))]

# ================= FUNÇÃO KPI =================
def kpi_box(col, label, value, progress=None, color="#FFFFFF", key=None):
    fill_color = "#10B981" if (progress is None or progress>=1) else "#F87171"
    progress_html = ""
    if progress is not None:
        pct = min(progress,1)*100
        progress_html = f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width:{pct}%; background-color:{fill_color};"></div>
        </div>
        """
    clicked = False
    if key:
        clicked = col.button("", key=key, help=label)
    col.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-label">{label}</div>
        <div class="kpi-number" style="color:{color};">{value}</div>
        {progress_html}
    </div>
    """, unsafe_allow_html=True)
    return clicked

# ================= CÁLCULOS =================
meta_total = df_filtrado["Meta"].sum()
realizado_total = df_filtrado["Realizado"].sum()
atingimento = realizado_total / meta_total if meta_total != 0 else 0
crescimento_medio = df_filtrado["Crescimento"].mean()
caminhao_total = df_filtrado["Caminhao"].sum()
status_text = "🟢 Meta Batida" if atingimento >= 1 else "🔴 Abaixo da Meta"

# ================= LAYOUT RESPONSIVO =================
# Para celular, empilhar colunas se espaço for pequeno
def responsive_columns(n):
    try:
        width = st.runtime.scriptrunner._main_script.session_state["browser_width"]
    except:
        width = 1200
    if width < 600:
        return [st.container() for _ in range(n)]
    return st.columns(n)

col1, col2, col3 = responsive_columns(3)
col4, col5, col6 = responsive_columns(3)

# ================= KPIs CLIQUE =================
filter_meta = kpi_box(col1, "💰 Meta", f"R$ {meta_total:,.0f}")
filter_realizado = kpi_box(col2, "📈 Realizado", f"R$ {realizado_total:,.0f}", key="realizado")
cor = "#10B981" if atingimento >= 1 else "#F87171"
filter_atingimento = kpi_box(col3, "🎯 Atingimento", f"{atingimento:.2%}", progress=atingimento, color=cor, key="atingimento")
filter_crescimento = kpi_box(col4, "📊 Crescimento", f"{crescimento_medio:.2f}%", progress=(crescimento_medio/10+0.5))
filter_caminhao = kpi_box(col5, "🚚 Caminhão", f"{caminhao_total}", color="#38BDF8")
filter_status = kpi_box(col6, "Status", status_text, color="#FACC15" if atingimento >= 1 else "#F87171")

# ================= FILTRO AUTOMÁTICO =================
df_plot = df_filtrado.copy()
if filter_realizado: df_plot = df_plot[df_plot["Realizado"] > df_plot["Realizado"].mean()]
if filter_atingimento: df_plot = df_plot[df_plot["Realizado"]/df_plot["Meta"] >= 1]
if filter_crescimento: df_plot = df_plot[df_plot["Crescimento"] > 0]
if filter_caminhao: df_plot = df_plot[df_plot["Caminhao"] > 0]
if filter_status: df_plot = df_plot[df_plot["Realizado"]/df_plot["Meta"] >= 1]

# ================= GRÁFICOS RESPONSIVOS =================
st.markdown("---")
meta_realizado = df_plot.groupby("Data")[["Meta","Realizado"]].sum().reset_index()
fig1 = px.bar(meta_realizado, x="Data", y=["Meta","Realizado"], barmode="group",
              text_auto=True, template="plotly_dark", color_discrete_sequence=["#6366F1","#10B981"])
fig1.update_layout(title_text="Meta vs Realizado", title_x=0.5)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(meta_realizado, x="Data", y="Realizado", title="Tendência de Realizado",
               template="plotly_dark", markers=True)
fig2.update_traces(line=dict(color="#10B981", width=4))
st.plotly_chart(fig2, use_container_width=True)

if not df_plot.empty:
    melhor_dia = meta_realizado.loc[meta_realizado["Realizado"].idxmax()]
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-label">🏆 Melhor Dia</div>
        <div class="kpi-number"> {melhor_dia['Data'].date()} - R$ {melhor_dia['Realizado']:,.0f} </div>
    </div>
    """, unsafe_allow_html=True)

