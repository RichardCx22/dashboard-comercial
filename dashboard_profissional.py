import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ================= CONFIG =================
st.set_page_config(page_title="Dashboard Executivo v2", layout="wide")

# ================= CSS (PADRÃO CEO DARK) =================
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
.progress-fill { height: 100%; border-radius: 10px; transition: width 0.5s ease-in-out; }

div.stButton > button { width: 100%; border-radius: 8px; background-color: #334155; color: white; border: none; height: 35px; font-size: 12px; }
div.stButton > button:hover { background-color: #475569; border: 1px solid #6366F1; }
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
            st.rerun()
        else: st.error("Incorreto")
    st.stop()

# ================= DADOS (CORREÇÃO DE DATAS SEQUENCIAIS) =================
np.random.seed(42)
datas_range = pd.date_range("2026-03-01", "2026-03-22")
df = pd.DataFrame({
    "Data": datas_range,
    "Meta": np.random.randint(8000, 15000, len(datas_range)),
    "Realizado": np.random.randint(7000, 16000, len(datas_range)),
    "Crescimento": np.random.uniform(-2, 5, len(datas_range)),
    "Caminhao": np.random.randint(5, 15, len(datas_range))
})

# ================= FILTROS SIDEBAR =================
st.sidebar.header("📅 Período")
data_inicio = st.sidebar.date_input("Início", df["Data"].min())
data_fim = st.sidebar.date_input("Fim", df["Data"].max())
df_filtrado = df[(df["Data"] >= pd.to_datetime(data_inicio)) & (df["Data"] <= pd.to_datetime(data_fim))]

# ================= FUNÇÃO KPI =================
def kpi_card(col, label, value, progress=None, color="#FFFFFF", key=None):
    fill_color = "#10B981" if (progress is None or progress >= 1) else "#F87171"
    prog_html = ""
    if progress is not None:
        pct = min(max(progress, 0), 1) * 100
        prog_html = f'<div class="progress-container"><div class="progress-fill" style="width:{pct}%; background-color:{fill_color};"></div></div>'
    
    col.markdown(f'<div class="kpi-box"><div class="kpi-label">{label}</div><div class="kpi-number" style="color:{color};">{value}</div>{prog_html}</div>', unsafe_allow_html=True)
    return col.button(f"🔍 Detalhar {label}", key=f"btn_{key}") if key else False

# ================= CÁLCULOS =================
meta_total = df_filtrado["Meta"].sum()
realizado_total = df_filtrado["Realizado"].sum()
atingimento = realizado_total / meta_total if meta_total > 0 else 0
crescimento_medio = df_filtrado["Crescimento"].mean()

# ================= LAYOUT SUPERIOR (KPIs) =================
c1, c2, c3 = st.columns(3)
c4, c5, c6 = st.columns(3)

kpi_card(c1, "💰 Meta Total", f"R$ {meta_total:,.0f}")
f_real = kpi_card(c2, "📈 Realizado", f"R$ {realizado_total:,.0f}", key="real")
cor_at = "#10B981" if atingimento >= 1 else "#F87171"
kpi_card(c3, "🎯 Atingimento", f"{atingimento:.2%}", progress=atingimento, color=cor_at)

kpi_card(c4, "📊 Crescimento", f"{crescimento_medio:.2f}%", progress=(crescimento_medio/10+0.5))
kpi_card(c5, "🚚 Caminhões", f"{df_filtrado['Caminhao'].sum()}", color="#38BDF8")
status_txt = "META BATIDA" if atingimento >= 1 else "ABAIXO DA META"
kpi_card(c6, "Status", status_txt, color="#FACC15" if atingimento >= 1 else "#F87171")

st.markdown("---")

# ================= NOVOS GRÁFICOS (LINHA PRINCIPAL) =================
col_graf_1, col_graf_2 = st.columns([2, 1])

with col_graf_1:
    # Gráfico de Barras com todas as datas (Correção do erro 2)
    fig_barra = px.bar(df_filtrado, x="Data", y=["Meta", "Realizado"], 
                      barmode="group", template="plotly_dark",
                      color_discrete_sequence=["#6366F1", "#10B981"])
    fig_barra.update_layout(title="Performance Diária", xaxis=dict(type='category'))
    st.plotly_chart(fig_barra, use_container_width=True)

with col_graf_2:
    # Gráfico de Rosca (Donut) - Composição da Meta
    fig_donut = px.pie(values=[realizado_total, max(0, meta_total-realizado_total)], 
                       names=['Realizado', 'Pendente'], hole=.6,
                       color_discrete_sequence=["#10B981", "#334155"],
                       template="plotly_dark")
    fig_donut.update_layout(title="Composição da Meta", showlegend=False)
    st.plotly_chart(fig_donut, use_container_width=True)

# ================= LINHA DE TENDÊNCIA E MELHOR DIA =================
col_graf_3, col_graf_4 = st.columns([1, 2])

with col_graf_3:
    # Indicador de Tendência (Gauge ou Delta)
    ultimo_realizado = df_filtrado["Realizado"].iloc[-1]
    dia_anterior = df_filtrado["Realizado"].iloc[-2] if len(df_filtrado) > 1 else ultimo_realizado
    delta = ((ultimo_realizado / dia_anterior) - 1) * 100

    fig_delta = go.Figure(go.Indicator(
        mode = "delta+number",
        value = ultimo_realizado,
        number = {'prefix': "R$ ", 'font': {'size': 40}},
        delta = {'reference': dia_anterior, 'relative': True, 'valueformat': '.2%'},
        title = {"text": "Tendência (Último Dia vs Anterior)", "font": {"size": 16, "color": "#94A3B8"}},
        domain = {'x': [0, 1], 'y': [0, 1]}
    ))
    fig_delta.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250)
    st.plotly_chart(fig_delta, use_container_width=True)

with col_graf_4:
    # Gráfico de Linha - Evolução do Crescimento
    fig_linha = px.line(df_filtrado, x="Data", y="Crescimento", 
                        title="Evolução do Crescimento (%)", template="plotly_dark")
    fig_linha.update_traces(line_color='#6366F1', fill='tozeroy')
    fig_linha.update_layout(xaxis=dict(type='category'), height=300)
    st.plotly_chart(fig_linha, use_container_width=True)

# Rodapé com o destaque do melhor dia
melhor_dia = df_filtrado.loc[df_filtrado["Realizado"].idxmax()]
st.success(f"🏆 **Destaque:** O melhor resultado foi em **{melhor_dia['Data'].strftime('%d/%m')}** com faturamento de **R$ {melhor_dia['Realizado']:,.0f}**.")
