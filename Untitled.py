import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import matplotlib.pyplot as plt
from cycler import cycler
import locale

# Defina a função de conexão e obtenção de dados
@st.cache_data
def get_data():
    postgres_str = 'postgresql+pg8000://postgres:123456789@localhost:5432/telemedicina'
    engine = create_engine(postgres_str)

    query = "SELECT * FROM telemedicina.recebimentos"
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    return df

# Carregar os dados
df = get_data()
df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')

# Configurando título da página e elementos básicos do layout
st.set_page_config(
    page_title="Dashboard de Variação Percentual de Recebimento",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Definir nomes dos meses em português
meses_pt = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# Sidebar simplificada com ano e mês
st.sidebar.subheader("Filtros")
ano = st.sidebar.selectbox("Ano:", options=df['DATA'].dt.year.unique(), index=(list(df['DATA'].dt.year.unique()).index(2024) if 2024 in df['DATA'].dt.year.unique() else 0))
mes_atual = st.sidebar.selectbox("Mês atual:", options=range(1, 13), format_func=lambda x: meses_pt[x - 1])

mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
ano_anterior = ano - 1 if mes_anterior == 12 else ano

# Cabeçalho
with st.container():
    st.title("Dashboard de Variação Percentual")
    st.caption("Análise mensal de recebimento por categoria e produto")
    st.markdown("<hr style='border-color: lightgray;'>", unsafe_allow_html=True)

# Calculando valores e variação percentual
valor_anterior = df[(df['DATA'].dt.year == ano_anterior) & (df['DATA'].dt.month == mes_anterior)]['TOTAL_RECEBIDO'].sum()
valor_atual = df[(df['DATA'].dt.year == ano) & (df['DATA'].dt.month == mes_atual)]['TOTAL_RECEBIDO'].sum()
variacao_percentual = ((valor_atual - valor_anterior) / valor_anterior * 100) if valor_anterior else 0

formatted_value_anterior = f"R$ {valor_anterior:,.2f}".replace(",", ".").replace(".", ",", 1)
formatted_value_atual = f"R$ {valor_atual:,.2f}".replace(",", ".").replace(".", ",", 1)

# Exibindo métricas no layout
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label=f"Recebimento em {meses_pt[mes_anterior - 1]}/{ano_anterior}", value=formatted_value_anterior)
    
with col2:
    st.metric(label=f"Recebimento em {meses_pt[mes_atual - 1]}/{ano}", value=formatted_value_atual)

with col3:
    st.metric(label="Variação Percentual", value=f"{variacao_percentual:.2f}%")

# Configurando cores para os gráficos
cores = plt.get_cmap('Pastel1').colors
ciclo_cores = cycler('color', cores)
plt.rc('axes', prop_cycle=ciclo_cores)

# Gráfico de Variação Percentual por Categoria
st.write('---')
st.markdown("<h2 style='color: gray; font-size: 20px;'>Variação Percentual por Categoria</h2>", unsafe_allow_html=True)

df_anterior_categoria = df[(df['DATA'].dt.year == ano_anterior) & (df['DATA'].dt.month == mes_anterior)]
df_atual_categoria = df[(df['DATA'].dt.year == ano) & (df['DATA'].dt.month == mes_atual)]

resultado_categoria_anterior = df_anterior_categoria.groupby('CATEGORIA')['TOTAL_RECEBIDO'].sum()
resultado_categoria_atual = df_atual_categoria.groupby('CATEGORIA')['TOTAL_RECEBIDO'].sum()

porcentagem_categoria = (resultado_categoria_atual - resultado_categoria_anterior) / resultado_categoria_anterior * 100
df_porcentagem_categoria = porcentagem_categoria.reset_index()
df_porcentagem_categoria.columns = ['CATEGORIA', 'VARIACAO_PERCENTUAL']
df_porcentagem_categoria['VARIACAO_PERCENTUAL'] = pd.to_numeric(df_porcentagem_categoria['VARIACAO_PERCENTUAL'], errors='coerce')

fig_categoria, ax_categoria = plt.subplots(figsize=(12, 7))
barras_categoria = ax_categoria.bar(df_porcentagem_categoria['CATEGORIA'], df_porcentagem_categoria['VARIACAO_PERCENTUAL'])

ax_categoria.bar_label(barras_categoria, labels=[f"{var:.2f}%" for var in df_porcentagem_categoria['VARIACAO_PERCENTUAL']], padding=3)
for i, var in enumerate(df_porcentagem_categoria['VARIACAO_PERCENTUAL']):
    barras_categoria[i].set_color(cores[0] if var < 0 else cores[2])

plt.box(False)
ax_categoria.tick_params(axis='x', rotation=45, labelsize=10, pad=20, length=0)
ax_categoria.set_yticks([])

st.pyplot(fig_categoria)

# Gráfico de Variação Percentual por Produto
st.write('---')
st.markdown("<h2 style='color: gray; font-size: 20px;'>Variação Percentual por Produto</h2>", unsafe_allow_html=True)

df_anterior_produto = df[(df['DATA'].dt.year == ano_anterior) & (df['DATA'].dt.month == mes_anterior)]
df_atual_produto = df[(df['DATA'].dt.year == ano) & (df['DATA'].dt.month == mes_atual)]

resultado_produto_anterior = df_anterior_produto.groupby('ITEM_PCG')['TOTAL_RECEBIDO'].sum()
resultado_produto_atual = df_atual_produto.groupby('ITEM_PCG')['TOTAL_RECEBIDO'].sum()

porcentagem_produto = (resultado_produto_atual - resultado_produto_anterior) / resultado_produto_anterior * 100
df_porcentagem_produto = porcentagem_produto.reset_index()
df_porcentagem_produto.columns = ['ITEM_PCG', 'VARIACAO_PERCENTUAL']
df_porcentagem_produto['VARIACAO_PERCENTUAL'] = pd.to_numeric(df_porcentagem_produto['VARIACAO_PERCENTUAL'], errors='coerce')

fig_produto, ax_produto = plt.subplots(figsize=(12, 7))
barras_produto = ax_produto.barh(df_porcentagem_produto['ITEM_PCG'], df_porcentagem_produto['VARIACAO_PERCENTUAL'])

ax_produto.bar_label(barras_produto, labels=[f"{var:.2f}%" for var in df_porcentagem_produto['VARIACAO_PERCENTUAL']], padding=3)
for i, var in enumerate(df_porcentagem_produto['VARIACAO_PERCENTUAL']):
    barras_produto[i].set_color(cores[0] if var < 0 else cores[2])

plt.box(False)
ax_produto.tick_params(axis='y', labelsize=10, pad=20, length=0)
ax_produto.set_xticks([])

st.pyplot(fig_produto)
