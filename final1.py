import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import json
import requests  # Para obter o GeoJSON dos estados brasileiros

# Carrega o dataset
df = pd.read_csv('dataset_unificado_processado.csv')

# Obtendo o GeoJSON do Brasil
url_geojson = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
geojson_data = requests.get(url_geojson).json()

# Filtra para manter apenas os estados do Sudeste
sudeste_states = ["Espírito Santo", "Minas Gerais", "Rio de Janeiro", "São Paulo"]
sudeste_geojson = {
    "type": "FeatureCollection",
    "features": [f for f in geojson_data["features"] if f["properties"]["name"] in sudeste_states]
}

# Mapeia nomes completos para siglas
mapa_estados = {
    "Espírito Santo": "ES",
    "Minas Gerais": "MG",
    "Rio de Janeiro": "RJ",
    "São Paulo": "SP"
}

# Cria coluna de siglas no GeoJSON
for feature in sudeste_geojson["features"]:
    feature["id"] = mapa_estados[feature["properties"]["name"]]

# Dashboard Streamlit
st.title("Dashboard de Análise de Dados")

# Botões para seleção de anos
st.subheader("Selecione os Anos para Análise")

col1, col2 = st.columns(2)
with col1:
    ano_2017 = st.toggle("2017", value=True)
with col2:
    ano_2018 = st.toggle("2018", value=True)

# Filtragem dos anos selecionados
anos_selecionados = []
if ano_2017:
    anos_selecionados.append("2017")
if ano_2018:
    anos_selecionados.append("2018")
if not anos_selecionados:
    anos_selecionados = ["2017", "2018"]

# Botões para seleção de estados
st.subheader("Selecione os Estados para Análise")

col1, col2, col3, col4 = st.columns(4)
with col1:
    estado_es = st.toggle("ES", value=True)
with col2:
    estado_mg = st.toggle("MG", value=True)
with col3:
    estado_rj = st.toggle("RJ", value=True)
with col4:
    estado_sp = st.toggle("SP", value=True)

# Filtragem dos estados selecionados
estados_selecionados = []
if estado_es:
    estados_selecionados.append("ES")
if estado_mg:
    estados_selecionados.append("MG")
if estado_rj:
    estados_selecionados.append("RJ")
if estado_sp:
    estados_selecionados.append("SP")
if not estados_selecionados:
    estados_selecionados = ["ES", "MG", "RJ", "SP"]

# Filtrando os dados conforme a seleção
df_filtrado = df[df["ANO_IS"].astype(str).isin(anos_selecionados) & df["ESTADO"].isin(estados_selecionados)]

# Cálculo de totais
total_casos = df_filtrado["Casos_Total"].sum()
total_obitos = df_filtrado["Obitos_Total"].sum()

# Exibição dos totais
st.subheader("Resumo Geral")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Casos Totais", value=total_casos)
with col2:
    st.metric(label="Óbitos Totais", value=total_obitos)

# Gráfico de Casos Totais por Estado
st.subheader("Casos Totais por Estado")
df_estados = df_filtrado.groupby("ESTADO")["Casos_Total"].sum().reset_index()
fig = px.bar(df_estados, x="ESTADO", y="Casos_Total", title="Casos Totais por Estado")
st.plotly_chart(fig)

# **MAPA DO SUDESTE BRASILEIRO**
st.subheader("Distribuição dos Estados Selecionados")

# Criando um DataFrame para o mapa
df_mapa = pd.DataFrame({"ESTADO": ["ES", "MG", "RJ", "SP"]})
df_mapa["Selecionado"] = df_mapa["ESTADO"].apply(lambda x: 1 if x in estados_selecionados else 0)

# Criando o mapa
fig_mapa = px.choropleth(
    df_mapa,
    geojson=sudeste_geojson,
    locations="ESTADO",
    featureidkey="id",
    color="Selecionado",
    color_continuous_scale=["#636363", "#ffcc00"],  # Cinza para não selecionado, amarelo para selecionado
    title="Mapa Interativo dos Estados Selecionados",
)

fig_mapa.update_geos(fitbounds="locations", visible=False)
fig_mapa.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)'))  # Fundo transparente

st.plotly_chart(fig_mapa)
