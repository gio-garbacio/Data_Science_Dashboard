import streamlit as st

import numpy as np
import pandas as pd
import plotly.express as px
import json
import requests
from sklearn.preprocessing import MinMaxScaler
import base64

# Função para usar imagem no cabeçalho
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

img_base64 = get_base64_image("logo mosquito.png")
    
    
# Carrega o dataset
df = pd.read_csv('dataset_unificado_processado.csv')

# Dados de população dos estados do Sudeste por ano (fonte: IBGE)
populacao_estados_ano = {
    "ES": {2017: 4016356, 2018: 3972388},
    "MG": {2017: 21119536, 2018: 21040662},
    "RJ": {2017: 16718956, 2018: 17159960},
    "SP": {2017: 45094866, 2018: 45538936}
}

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
for feature in sudeste_geojson["features"]:
    feature["id"] = mapa_estados[feature["properties"]["name"]]
    
# Configura a página para usar largura total
st.set_page_config(layout="wide") 


st.markdown(
    """
    <style>
        /* Define o fundo da página inteira */
        [data-testid="stAppViewContainer"] {
            background-color: #0E1117;
        }

        /* Altera a cor de fundo do container principal */
        [data-testid="stAppViewBlockContainer"] {
            background-color: #0E1117;
        }
    </style>
    """,
    unsafe_allow_html=True
)
# ------------------------------------------------------------------------------
# CABEÇALHO
st.markdown(f"""
    <div style='display: flex; align-items: center; background-color: #003366 ; padding: 10px; color: white; border-radius: 10px;'>
        <img src='data:image/png;base64,{img_base64}' width='150' style='margin-right: 15px;'>
        <div>
            <h1 style='font-size: 40px; font-weight: bold; margin-bottom: 0px;'>Ciclo Viral: Associando a Febre Amarela ao Clima no Sudeste</h1>
            <h3 style='font-size: 24px; font-weight: normal; margin-top: 0px; line-height: 1.2;'>Uma análise dos casos entre 2017 e 2018 e sua relação com fatores climáticos</h3>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PRIMEIRA LINHA: Seleção de Ano e de Estado | Mapa do Sudeste | Proporção de casos | Resumo Geral
with st.container():
    colA1, colA2, colA3, colA4 = st.columns([2, 4, 3, 2])

    # COLUNA A1: Seleção de dados para análise
    with colA1:
        # Título principal
        st.markdown("<h2 style='font-size: 26px; font-weight: bold; text-align: center; color: white;'>Seleção de Dados para Análise</h2>", unsafe_allow_html=True)
        st.markdown("""
    
        """, unsafe_allow_html=True)
        st.text("")

        # Seção de Anos
        st.markdown("<h4 style='color: white;'>Anos</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            ano_2017 = st.checkbox("2017", value=True)
        with col2:
            ano_2018 = st.checkbox("2018", value=True)

        # Espaçamento
        st.markdown("<br>", unsafe_allow_html=True)

        # Seção de Estados
        st.markdown("<h4 style='color: white;'>Estados</h4>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            estado_es = st.checkbox("ES", value=True)
        with col2:
            estado_mg = st.checkbox("MG", value=True)
        with col3:
            estado_rj = st.checkbox("RJ", value=True)
        with col4:
            estado_sp = st.checkbox("SP", value=True)

        # Processamento das seleções
        anos_selecionados = [ano for ano, ativo in [("2017", ano_2017), ("2018", ano_2018)] if ativo] or ["2017", "2018"]
        estados_selecionados = [
            estado for estado, ativo in [("ES", estado_es), ("MG", estado_mg), ("RJ", estado_rj), ("SP", estado_sp)] if ativo
        ] or ["ES", "MG", "RJ", "SP"]

        # Filtragem dos dados
        df_filtrado = df[df["ANO_IS"].astype(str).isin(anos_selecionados) & df["ESTADO"].isin(estados_selecionados)]

        df_filtrado["POPULACAO"] = df_filtrado.apply(
            lambda row: populacao_estados_ano[row["ESTADO"]][row["ANO_IS"]], axis=1
        )

    # COLUNA A2: Gráfico de Mapa do Sudeste
with colA2:
    st.markdown("<h2 style='font-size: 26px; font-weight: bold; text-align: center; color: white;'>Mapa do Sudeste</h2>", unsafe_allow_html=True)

    df_mapa = pd.DataFrame({"ESTADO": ["ES", "MG", "RJ", "SP"]})
    df_mapa["Selecionado"] = df_mapa["ESTADO"].apply(
        lambda x: "Selecionado" if x in estados_selecionados else "Não Selecionado"
    )

    fig_mapa = px.choropleth(
        df_mapa,
        geojson=sudeste_geojson,
        locations="ESTADO",
        featureidkey="id",
        color="Selecionado",
        color_discrete_map={"Selecionado": "#FCDB04", "Não Selecionado": "#696969"},
        hover_data={"ESTADO": True, "Selecionado": False} 
    )

    fig_mapa.update_geos(fitbounds="locations", visible=False)

    # Ajusta o layout para ocupar a largura da coluna e melhora a legenda
    fig_mapa.update_layout(
        width=600,  
        height=350, 
        dragmode=False,
        geo=dict(bgcolor='#0E1117'),  
        paper_bgcolor="#0E1117",  
        plot_bgcolor="#0E1117",  
        coloraxis_showscale=False,
        margin={"r":0,"t":30,"l":0,"b":0},  
        legend=dict(
            x=0.02,  
            y=0.02,  
            bgcolor="#0E1117",  
            bordercolor="#0E1117",
            borderwidth=1,
            font=dict(color="white")  # Deixa a legenda branca
        ),
        modebar_remove=["zoom", "pan", "zoomInGeo", "zoomOutGeo", "resetGeo"]
    )
    st.text("")
    st.text("")
    st.text("")
    st.plotly_chart(fig_mapa, use_container_width=True, key="mapa_1")

    # COLUNA A3: Proporção de casos 
    with colA3:
        st.markdown("<h2 style='font-size: 26px; font-weight: bold; text-align: center; color: white;'>Proporção de Casos por Estado</h2>", unsafe_allow_html=True)
        df_casos_estado = df_filtrado.groupby("ESTADO")["Casos_Total"].sum().reset_index()
        fig_pizza = px.pie(
        df_casos_estado,
            values="Casos_Total",
            names="ESTADO",
            color="ESTADO",
            color_discrete_map={
                "ES": "#003366",
                "MG": "#FCDB04",
                "RJ": "#0068c9",
                "SP": "#83c9ff"
    }
        )
        fig_pizza.update_traces(hovertemplate="%{value} casos em %{label}")
        fig_pizza.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="white"),  
            legend=dict(
                font=dict(color="white")  # Deixa os nomes dos estados na legenda brancos
            )
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
        
        
    # COLUNA A4: Resumo Geral
    with colA4:
        # st.markdown("<h2 style='font-size: 26px; font-weight: bold; text-align: center; color: white;'>Resumo Geral</h2>", unsafe_allow_html=True)
        total_casos = df_filtrado["Casos_Total"].sum()
        total_obitos = df_filtrado["Obitos_Total"].sum()
        taxa_mortalidade = (total_obitos / total_casos) * 100 if total_casos > 0 else 0

        kpi_style = """
                <style>
                    .kpi-container {
                        background-color:#003366;
                        color: white;
                        text-align: center;
                        padding: 10px;
                        border-radius: 10px;
                        font-size: 26px;
                        margin-bottom: 25px;
                    }
                </style>
            """
        st.markdown(kpi_style, unsafe_allow_html=True)
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        kpi_html = f"""
            <div class="kpi-container"><strong>Casos Totais</strong><br>{total_casos:,}</div>
            <div class="kpi-container"><strong>Óbitos Totais</strong><br>{total_obitos:,}</div>
            <div class="kpi-container"><strong>Taxa de Mortalidade</strong><br>{taxa_mortalidade:.2f}%</div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)
        

# ------------------------------------------------------------------------------
# SEGUNDA LINHA: Número de Casos e Óbitos por Estado | Evolução Temporal de Casos de Febre Amarela
with st.container():
    colB1, colB2 = st.columns([ 5, 5])
    # COLUNA B1: Número de Casos e Óbitos por Estado
    with colB1:
        st.markdown("<h2 style='font-size: 26px; font-weight: bold; text-align: center; color: white;'>Número de Casos e Óbitos por Estado</h2>", unsafe_allow_html=True)
        st.text("")
        st.text("")
        df_estados = df_filtrado.groupby("ESTADO").agg({
            "Casos_Total": "sum",
            "Obitos_Total": "sum"
        }).reset_index()
        fig_bar = px.bar(
            df_estados,
            x="ESTADO",
            y=["Casos_Total", "Obitos_Total"],
            barmode='group',
            labels={"value": "Número de Casos e de Mortes", "variable": "Tipo"}
        )
        fig_bar.update_traces(
            hovertemplate="%{y} %{data.name}<extra></extra>"
        ).for_each_trace(lambda t: t.update(
            name=t.name.replace("Casos_Total", "Casos").replace("Obitos_Total", "Óbitos")
        ))
        fig_bar.update_traces(hovertemplate="%{y} %{data.name} em %{x}")
        fig_bar.update_layout(
                    paper_bgcolor="#0E1117",
                    plot_bgcolor="#0E1117",
                    font=dict(color="white"),
                    legend=dict(
                        font=dict(color="white")  # Deixa os rótulos da legenda em branco
                    )
                )
        st.plotly_chart(fig_bar, use_container_width=True)

    # COLUNA B2: Evolução Temporal de Casos de Febre Amarela
    with colB2:
        st.markdown("<h2 style='font-size: 26px; font-weight: bold; text-align: center; color: white;'>Evolução Temporal de Casos de Febre Amarela</h2>", unsafe_allow_html=True)
        st.text("")
        st.text("")
        df_evolucao = df_filtrado.groupby(["ANO_IS", "MES_IS"]).agg({"Casos_Total": "sum"}).reset_index()

        fig_evolucao = px.line(
        df_evolucao,
        x="MES_IS",
        y="Casos_Total",
        color="ANO_IS",
        labels={"MES_IS": "Mês", "Casos_Total": "Número de casos por mês"},
        )
        fig_evolucao.update_xaxes(
            tickvals=list(range(1, 13)),
            ticktext=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                        "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        )
        fig_evolucao.update_traces(
            hovertemplate="%{y} casos em %{x}/%{data.name}<extra></extra>"
        )
        fig_evolucao.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="white"),
            legend=dict(
                font=dict(color="white")  # Deixa os rótulos da legenda em branco
            )
        )
        st.text("")
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        
# ------------------------------------------------------------------------------
# TERCEIRA LINHA: Seletor de Fator Climático | Correlação entre Casos Totais e Fatores Climáticos | Evolução Temporal de um Fator Climático
with st.container():
    colC1, colC2, colC3 = st.columns([3, 5, 5])

    # COLUNA C1: Seletor de fator climático geral
    with colC1:
        st.markdown("<h2 style='font-size: 26px; font-weight: bold; text-align: center; color: white;'>Seletor de fator climático</h2>", unsafe_allow_html=True)

        opcoes_climaticas_disp = {
            "Temperatura": "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)",
            "Precipitação": "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)",
            "Radiação": "RADIACAO GLOBAL (Kj/m²)",
            "Pressão": "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)"
        }
        unidades_climaticas_disp = {
            "Temperatura": "Temperatura média (°C)",
            "Precipitação": "Precipitação total (mm)",
            "Radiação": "Radiação global (Kj/m²)",
            "Pressão": "Pressão atmosférica (mB)"
        }
        st.markdown("<p style='color: white; font-size: 16px;'>Selecione um fator climático para análise:</p>", unsafe_allow_html=True)
        var_selecionada = st.selectbox(
            "",
            list(opcoes_climaticas_disp.keys()),
            index=0
        )

    # COLUNA C2: Correlação entre Casos Totais e Fatores Climáticos
    with colC2:
        st.markdown("<h2 style='font-size: 26px; font-weight: bold; text-align: center; color: white;'>Correlação entre Casos Totais e Fatores Climáticos</h2>", unsafe_allow_html=True)

        fig_dispersao = px.scatter(
            df_filtrado,
            x=opcoes_climaticas_disp[var_selecionada],
            y="Casos_Total",
            color="Mortalidade",
            labels={
                opcoes_climaticas_disp[var_selecionada]: unidades_climaticas_disp[var_selecionada],
                "Casos_Total": "Casos Totais"
            },
        )

        df_filtrado["Data_Formatada"] = df_filtrado["MES_IS"].map({
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
        }) + "/" + df_filtrado["ANO_IS"].astype(str)

        fig_dispersao.update_traces(
            hovertemplate=(
                "Estado = %{customdata[0]}<br>"
                "Data = %{customdata[1]}<br>"
                "%{xaxis.title.text} = %{x:.2f}<br>"
                "Casos Totais = %{y:.2f}<br>"
                "Mortalidade = %{marker.color:.2f}<extra></extra>"
            ),
            customdata=df_filtrado[["ESTADO", "Data_Formatada"]]
        )
        fig_dispersao.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="white"),
            legend=dict(
                font=dict(color="white")
            )
        )
        st.plotly_chart(fig_dispersao, use_container_width=True)

    # COLUNA C3: Evolução Temporal de um Fator Climático
    with colC3:
        st.markdown("<h2 style='font-size: 26px; font-weight: bold; text-align: center; color: white;'>Evolução Temporal de um Fator Climático</h2>", unsafe_allow_html=True)

        df_climatico = df_filtrado.groupby(["ANO_IS", "MES_IS"]).agg({
            opcoes_climaticas_disp[var_selecionada]: "mean"
        }).reset_index()

        df_climatico = df_climatico.rename(
            columns={opcoes_climaticas_disp[var_selecionada]: var_selecionada}
        )

        fig_climatico = px.line(
            df_climatico,
            x="MES_IS",
            y=var_selecionada,
            color="ANO_IS",
            labels={
                "MES_IS": "Mês",
                var_selecionada: unidades_climaticas_disp[var_selecionada],
                "ANO_IS": "Ano"
            },
        )
        fig_climatico.update_xaxes(
            tickvals=list(range(1, 13)),
            ticktext=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                      "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        )
        fig_climatico.update_traces(
            hovertemplate="%{y:.2f} em %{x}/%{data.name}<extra></extra>"
        )
        fig_climatico.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="white"),
            legend=dict(
                font=dict(color="white")
            )
        )
        st.text("")
        st.plotly_chart(fig_climatico, use_container_width=True)

# ------------------------------------------------------------------------------
# QUARTA LINHA: Linha Evol. Temporal de Casos, Óbitos e Fatores Climáticos Normalizada
with st.container():
    st.markdown("<h2 style='font-size: 26px; font-weight: bold; text-align: center; color: white;'>Evolução Temporal Normalizada</h2>", unsafe_allow_html=True)
    
    # *Normalização dos dados*
    scaler = MinMaxScaler()
    colunas_normalizar = [
        "Casos_Total", "Obitos_Total",
        opcoes_climaticas_disp[var_selecionada]
    ]

    df_normal = df_filtrado.copy()
    df_normal[colunas_normalizar] = scaler.fit_transform(df_filtrado[colunas_normalizar])

    # *Ajuste na Ordenação dos Meses*
    df_normal["MES_GLOBAL"] = df_normal["MES_IS"]
    if len(anos_selecionados) == 2:  # Se 2017 e 2018 foram selecionados
        df_normal.loc[df_normal["ANO_IS"] == 2018, "MES_GLOBAL"] += 12

    # Agrupando dados por mês e ano
    df_evolucao = df_normal.groupby(["ANO_IS", "MES_GLOBAL"]).agg({
        "Casos_Total": "sum",
        "Obitos_Total": "sum",
        opcoes_climaticas_disp[var_selecionada]: "mean"
    }).reset_index()

    df_plot = df_evolucao.copy()

    # Criando um dataframe longo para o Plotly
    df_long = df_plot.melt(
        id_vars=["ANO_IS", "MES_GLOBAL"], 
        value_vars=["Casos_Total", "Obitos_Total", opcoes_climaticas_disp[var_selecionada]],
        var_name="Variável", 
        value_name="Valor"
    )

    # Mapeando nomes para melhor legibilidade no gráfico
    nome_variaveis = {
        "Casos_Total": "Casos",
        "Obitos_Total": "Óbitos",
        opcoes_climaticas_disp["Temperatura"]: "Temperatura",
        opcoes_climaticas_disp["Radiação"]: "Radiação",
        opcoes_climaticas_disp["Precipitação"]: "Precipitação",
        opcoes_climaticas_disp["Pressão"]: "Pressão"
    }
    df_long["Variável"] = df_long["Variável"].map(nome_variaveis)

    cor_personalizada = {
        "Casos": "#0068c9",
        "Óbitos": "#83c9ff",
        "Temperatura": "#FCDB04",
        "Radiação": "#FCDB04",
        "Precipitação": "#FCDB04",
        "Pressão": "#FCDB04"
    }

    # Criando o gráfico de linhas
    fig_evolucao = px.line(
        df_long,
        x="MES_GLOBAL",
        y="Valor",
        color="Variável",
        markers=True,
        labels={"MES_GLOBAL": "Mês", "Valor": "Valor Normalizado"},
        color_discrete_map=cor_personalizada
    )

    # Definindo os meses de verão (Dez, Jan, Fev)
    if len(anos_selecionados) == 2:
        # Para dois anos (24 meses)
        fig_evolucao.add_vrect(
            x0=0.5, x1=2.5,  # Jan/2017 a Fev/2017
            fillcolor="yellow", opacity=0.1, layer="below", line_width=0
        )
        fig_evolucao.add_vrect(
            x0=12.5, x1=14.5,  # Jan/2018 a Fev/2018
            fillcolor="yellow", opacity=0.1, layer="below", line_width=0
        )
        # Dezembro de cada ano
        fig_evolucao.add_vrect(
            x0=11.5, x1=12.5,  # Dez/2017
            fillcolor="yellow", opacity=0.1, layer="below", line_width=0
        )
        fig_evolucao.add_vrect(
            x0=23.5, x1=24.5,  # Dez/2018
            fillcolor="yellow", opacity=0.1, layer="below", line_width=0
        )
    
        fig_evolucao.update_xaxes(
            tickvals=list(range(1, 25)),
            ticktext=["Jan 2017", "Fev 2017", "Mar 2017", "Abr 2017", "Mai 2017", "Jun 2017", "Jul 2017", "Ago 2017", "Set 2017", "Out 2017", "Nov 2017", "Dez 2017",
                      "Jan 2018", "Fev 2018", "Mar 2018", "Abr 2018", "Mai 2018", "Jun 2018", "Jul 2018", "Ago 2018", "Set 2018", "Out 2018", "Nov 2018", "Dez 2018"]
        )
    else:
        # Para um ano (12 meses)
        fig_evolucao.add_vrect(
            x0=0.5, x1=2.5,  # Jan a Fev
            fillcolor="yellow", opacity=0.1, layer="below", line_width=0
        )
        fig_evolucao.add_vrect(
            x0=11.5, x1=12.5,  # Dez
            fillcolor="yellow", opacity=0.1, layer="below", line_width=0
        )
    
        fig_evolucao.update_xaxes(
            tickvals=list(range(1, 13)),
            ticktext=["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        )

    # Adicionando legenda para as áreas destacadas
    fig_evolucao.add_annotation(
        xref="paper", yref="paper",
        x=0.02, y=1.15,
        text="Áreas amarelas: meses de verão (Dez, Jan, Fev)",
        showarrow=False,
        font=dict(size=16)
    )
    fig_evolucao.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="white"),
        legend=dict(
            font=dict(color="white")
        )
    )

    # Exibir o gráfico
    st.plotly_chart(fig_evolucao, use_container_width=True)
