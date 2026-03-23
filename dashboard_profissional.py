import streamlit as st
import pandas as pd
import plotly.express as px
import random

st.set_page_config(page_title="Dashboard Comercial PRO", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
h2, h4 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
usuarios = {
    "gerente": "havan2026",
    "funcionario": "havan2026"
}

def login():
    st.title("🔐 Login do Sistema")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in usuarios and usuarios[usuario] == senha:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    login()
    st.stop()

st.sidebar.success(f"Logado como: {st.session_state['usuario']}")

# ================= DADOS =================
dados = [
('2026-03-19',140000.00,133181.38,0.0,40.69,0,1,129.99,3339.52,509.96,6),
('2026-02-13',185000.37,141174.73,-23.69,181.32,1,2,239.98,2939.53,430.72,8),
('2026-02-12',185000.37,139364.34,-24.67,134.46,4,4,0.0,2813.53,0.0,5),
('2026-02-16',175000.35,226895.00,29.65,208.47,7,9,0.0,4231.03,0.0,11),
('2026-02-15',255000.51,240553.23,-5.67,260.92,8,9,0.0,5828.67,0.0,20),
('2026-02-19',175000.35,133218.57,-23.88,191.23,6,6,0.0,1264.11,0.0,11),
('2026-02-20',185000.37,126238.98,-31.76,198.87,2,2,0.0,1468.51,340.99,22),
('2026-02-23',160000.32,138573.50,0.0,132.71,5,5,0.0,2425.00,155.97,13),
('2026-02-24',160000.32,131858.74,0.0,90.18,3,4,0.0,1710.83,169.98,13),
('2026-02-25',130000.26,133151.33,2.38,154.66,2,4,249.89,2691.43,169.98,20),
]

colunas = ["Data","Meta","Realizado","Crescimento","Troco","Protecao","Cartao","VendaLista","Garantia","Multi","Caminhao"]

df = pd.DataFrame(dados, columns=colunas)
df["Data"] = pd.to_datetime(df["Data"])
df = df.sort_values("Data")

# ================= SIMULAÇÕES =================
vendedores = ["João", "Maria", "Carlos", "Ana"]
lojas = ["Loja Centro", "Loja Norte", "Loja Sul"]

df["Vendedor"] = [random.choice(vendedores) for _ in range(len(df))]
df["Loja"] = [random.choice(lojas) for _ in range(len(df))]

# ================= FILTROS =================
st.sidebar.header("📅 Filtros")

data_inicio = st.sidebar.date_input("Data inicial", df["Data"].min())
data_fim = st.sidebar.date_input("Data final", df["Data"].max())

df_filtrado = df[(df["Data"] >= pd.to_datetime(data_inicio)) & 
                 (df["Data"] <= pd.to_datetime(data_fim))]

# ================= KPIs =================
meta_total = df_filtrado["Meta"].sum()
realizado_total = df_filtrado["Realizado"].sum()
atingimento = realizado_total / meta_total if meta_total > 0 else 0
crescimento_medio = df_filtrado["Crescimento"].mean()
caminhao_total = df_filtrado["Caminhao"].sum()

melhor_dia = df_filtrado.loc[df_filtrado["Realizado"].idxmax()]

# ================= HEADER =================
st.markdown("""
<h1 style='text-align: center;'>🚀 Painel de Performance Comercial</h1>
<p style='text-align: center; color: gray;'>Acompanhamento estratégico em tempo real</p>
""", unsafe_allow_html=True)

# ================= KPIs =================
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

# LINHA 1
col1.markdown(f"""
<h4>💰 Meta</h4>
<h2>R$ {meta_total:,.0f}</h2>
""", unsafe_allow_html=True)

col2.markdown(f"""
<h4>📈 Realizado</h4>
<h2>R$ {realizado_total:,.0f}</h2>
""", unsafe_allow_html=True)

cor = "red" if atingimento < 1 else "green"
col3.markdown(f"""
<h4>🎯 Atingimento</h4>
<h2 style='color:{cor};'>{atingimento:.2%}</h2>
""", unsafe_allow_html=True)

# LINHA 2
col4.markdown(f"""
<h4>📊 Crescimento</h4>
<h2>{crescimento_medio:.2f}%</h2>
""", unsafe_allow_html=True)

col5.markdown(f"""
<h4>🚚 Caminhão</h4>
<h2 style='color:#38BDF8;'>{caminhao_total}</h2>
""", unsafe_allow_html=True)

status_text = "🟢 Meta Batida" if atingimento >= 1 else "🔴 Abaixo da Meta"

col6.markdown(f"""
<h4>Status</h4>
<h2>{status_text}</h2>
""", unsafe_allow_html=True)

# ================= ALERTA =================
if atingimento < 0.9:
    st.error("⚠️ Desempenho abaixo do esperado!")
elif atingimento < 1:
    st.warning("⚠️ Próximo da meta!")
else:
    st.success("✅ Meta atingida!")

# ================= PROGRESSO =================
st.progress(min(atingimento, 1.0))

# ================= MELHOR DIA =================
st.markdown(f"""
<div style='background-color:#1E293B; padding:20px; border-radius:10px;'>
<h3>🏆 Melhor Dia</h3>
<p>{melhor_dia['Data'].date()}</p>
<p>R$ {melhor_dia['Realizado']:,.2f}</p>
</div>
""", unsafe_allow_html=True)

# ================= PREVISÃO =================
dias = len(df_filtrado)
meta_diaria = meta_total / dias if dias > 0 else 0
media_realizado = df_filtrado["Realizado"].mean()
previsao = media_realizado * 30
projecao = previsao / meta_total if meta_total > 0 else 0

st.subheader("🔮 Inteligência Comercial")

c1, c2, c3 = st.columns(3)
c1.metric("Meta Diária", f"R$ {meta_diaria:,.0f}")
c2.metric("Previsão Mês", f"R$ {previsao:,.0f}")
c3.metric("Projeção Meta", f"{projecao:.2%}")

# ================= GRÁFICOS =================
fig1 = px.area(df_filtrado, x="Data", y=["Meta", "Realizado"], template="plotly_dark")
st.plotly_chart(fig1, use_container_width=True)

df_filtrado["MediaMovel"] = df_filtrado["Realizado"].rolling(3).mean()
fig2 = px.line(df_filtrado, x="Data", y=["Realizado", "MediaMovel"], template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

# ================= RODAPÉ =================
st.markdown("""
<hr>
<p style='text-align:center; font-size:12px; color:gray;'>
Desenvolvido por Richard • Dashboard Comercial PRO
</p>
""", unsafe_allow_html=True)
