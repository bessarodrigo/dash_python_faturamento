import pandas as pd
from sqlalchemy import create_engine
# import streamlit as st
import matplotlib.pyplot as plt
from cycler import cycler
import locale

# Defina a função de conexão e obtenção de dados
@st.cache_data
def get_data():
    # Configura a string de conexão ao banco 'telemedicina'
    postgres_str = 'postgresql://postgres:123456789@localhost:5432/telemedicina'
    engine = create_engine(postgres_str)

    # Consultar a tabela "recebimentos"
    query = "SELECT * FROM telemedicina.recebimentos" 
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
    
    return df

# Carregar os dados
data = get_data()

# Exibir os dados no Streamlit
# st.write("Tabela de Recebimentos")
# st.dataframe(data)
