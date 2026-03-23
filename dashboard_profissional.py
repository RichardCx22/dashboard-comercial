import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Painel de Performance Comercial", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
body { background-color: #0F172A; color: white; font-family: 'Arial', sans-serif; }
h1, h2, h3 { color: white; }
.metric-text { text-align:center; }
html, body, [class*="css"] { font-size: 16px; }
@media (max-width: 768px) {
    html, body, [class*="css"] { font-size: 20px; }
}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
usuarios = {
    "gerente": "havan2026",
    "funcionario": "havan2026"
}

def login():
    st.markdown("<h2 style='text-align:center;'>🔐 Login do Sistema</h2>", unsafe_allow_html=True)
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in usuarios and usuarios[usuario] == senha:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.success("Login realizado com sucesso!")
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

# ================= FILTROS =================
st.sidebar.header("📅 Filtros")
data_inicio = st.sidebar.date_input("Data inicial", df["Data"].min())
data_fim = st.sidebar.date_input("Data final", df["Data"].max())
df_filtrado = df[(df["Data"] >= pd.to_datetime(data_inicio)) & (df["Data"] <= pd.to_datetime(data_fim))]

# ================= KPIs =================
meta_total = df_filtrado["Meta"].sum()
realizado_total = df_filtrado["Realizado"].sum()
atingimento = realizado_total / meta_total if meta_total > 0 else 0
crescimento_medio = df_filtrado["Crescimento"].mean()
caminhao_total = df_filtrado["Caminhao"].sum()
melhor_dia = df_filtrado.loc[df_filtrado["Realizado"].idxmax()]
status = "🟢 Meta Batida" if atingimento >= 1 else "🔴 Abaixo da Meta"

# ================= CABEÇALHO =================
st.markdown("""
<h1 style='text-align: center;'>🚀 Painel de Performance Comercial</h1>
<p style='text-align: center; color: gray;'>Acompanhamento estratégico de metas e resultados em tempo real</p>
""", unsafe_allow_html=True)

# ================= KPIs VISUAIS =================
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
col5, col6 = st.columns(2)

col1.metric("💰 Meta", f"R$ {meta_total:,.0f}")
col2.metric("📈 Realizado", f"R$ {realizado_total:,.0f}")

cor_atingimento = "green" if atingimento >= 1 else "red"
col3.markdown(f"<h3 style='text-align:center;'>🎯 Atingimento</h3><h2 style='text-align:center; color:{cor_atingimento};'>{atingimento:.2%}</h2>", unsafe_allow_html=True)

col4.metric("📊 Crescimento", f"{crescimento_medio:.2f}%")
col5.metric("🚚 Caminhão", caminhao_total)
col6.metric("Status", status)

# ================= BARRA DE PROGRESSO =================
st.subheader("🎯 Progresso da Meta")
st.progress(min(atingimento, 1.0))

# ================= MELHOR DIA =================
st.subheader("🏆 Melhor Dia de Vendas")
st.info(f"📅 Data: {melhor_dia['Data'].date()}  \n💰 Venda: R$ {melhor_dia['Realizado']:,.2f}")

# ================= GRÁFICOS =================
st.subheader("📊 Análises")
colA = st.container()
colB = st.container()

with colA:
    st.subheader("📈 Meta vs Realizado")
    fig1 = px.area(df_filtrado, x="Data", y=["Meta", "Realizado"], markers=True)
    fig1.update_layout(template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

with colB:
    st.subheader("📉 Crescimento (%)")
    fig2 = px.line(df_filtrado, x="Data", y="Crescimento", markers=True)
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

# ================= PRODUTOS =================
st.subheader("📦 Performance de Produtos / Serviços")
produtos = df_filtrado[["Protecao","Cartao","VendaLista","Garantia","Multi"]].sum().reset_index()
produtos.columns = ["Produto", "Valor"]
fig3 = px.bar(produtos, x="Produto", y="Valor", text_auto=True)
fig3.update_layout(template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

# ================= RANKING =================
st.subheader("🏆 Ranking de Performance")
df_filtrado["Atingimento"] = df_filtrado["Realizado"] / df_filtrado["Meta"]
ranking = df_filtrado.sort_values("Realizado", ascending=False)
st.dataframe(ranking[["Data","Meta","Realizado","Atingimento"]])
