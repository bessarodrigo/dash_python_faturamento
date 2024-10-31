import pandas as pd
from sqlalchemy import create_engine
# import streamlit as st
import matplotlib.pyplot as plt
from cycler import cycler
import locale

# Conectar ao banco 'telemedicina'
postgres_str = 'postgresql://postgres:123456789@localhost:5432/telemedicina'
engine = create_engine(postgres_str)

try:
    # Usar uma consulta SQL para selecionar os dados da tabela 'recebimentos'
    query = "SELECT * FROM telemedicina.recebimentos;"
    df = pd.read_sql(query, engine)

    print("Dados carregados com sucesso!")
    print(df.head())

except Exception as e:
    print(f"Erro ao consumir dados do banco de dados: {e}")
