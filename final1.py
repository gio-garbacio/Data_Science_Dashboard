import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import json
import requests
from sklearn.preprocessing import MinMaxScaler

# Configura a página para usar largura total
st.set_page_config(layout="wide")  # Permite usar toda a largura da tela
st.markdown("<h1 style='text-align: center; color: white; background-color: darkred; padding: 10px;'>Bom Dia Giovanna!!!</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)


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

# ------------------------------------------------------------------------------
# TÍTULO DO DASHBOARD
st.title("Dashboard de Análise de Dados")

# ------------------------------------------------------------------------------
# PRIMEIRA LINHA: Seleção de Ano | Seleção de Estado | Mapa do Sudeste | Resumo Geral
with st.container():
    colA1, colA2, colA3 = st.columns([3, 6, 3])

    # --------------------------
    # COLUNA A1: Seleção de Anos e Seleção de Estados
    with colA1:
        st.subheader("Selecione os Anos para Análise")

        col1, col2 = st.columns(2)  # Criando duas colunas

        with col1:
            ano_2017 = st.toggle("2017", value=True)
        with col2:
            ano_2018 = st.toggle("2018", value=True)
        st.text("")
        st.text("")
        st.text("")
        st.text("")

        anos_selecionados = []
        if ano_2017:
            anos_selecionados.append("2017")
        if ano_2018:
            anos_selecionados.append("2018")

        if not anos_selecionados:
            anos_selecionados = ["2017", "2018"]

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

        # Filtragem dos dados
        df_filtrado = df[df["ANO_IS"].astype(str).isin(anos_selecionados) & df["ESTADO"].isin(estados_selecionados)]

        # Adiciona a coluna de população ao DataFrame filtrado
        df_filtrado["POPULACAO"] = df_filtrado.apply(
            lambda row: populacao_estados_ano[row["ESTADO"]][row["ANO_IS"]], axis=1
        )

    # --------------------------
    # --------------------------
# COLUNA A2: Gráfico de Mapa do Sudeste
with colA2:
    st.subheader("Mapa do Sudeste")
    
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
        color_discrete_map={"Selecionado": "#0068C9", "Não Selecionado": "#696969"},
    )

    fig_mapa.update_geos(fitbounds="locations", visible=False)

    # 🛠 Ajusta o layout para ocupar a largura da coluna e aproxima a legenda do mapa
    fig_mapa.update_layout(
        width=600,  # Define uma largura fixa (ajuste se necessário)
        height=350, # Define uma altura fixa
        dragmode=False,
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        coloraxis_showscale=False,
        margin={"r":0,"t":30,"l":0,"b":0},  # Remove margens desnecessárias
        legend=dict(
            x=0.02,  # Posição horizontal da legenda (mais próxima do mapa)
            y=0.02,  # Posição vertical da legenda (mais próxima do mapa)
            bgcolor="black",  # Fundo da legenda levemente transparente
            bordercolor="black",
            borderwidth=1,
        ),
        modebar_remove=["zoom", "pan", "zoomInGeo", "zoomOutGeo", "resetGeo"]
    )

    # 🔹 Use `use_container_width=True` para forçar o ajuste ao container
    st.plotly_chart(fig_mapa, use_container_width=True, key="mapa_1")


        # --------------------------
        # COLUNA A3: Resumo Geral
    with colA3:
        st.subheader("Resumo Geral")

        # Cálculos para o resumo
        total_casos = df_filtrado["Casos_Total"].sum()
        total_obitos = df_filtrado["Obitos_Total"].sum()
        taxa_mortalidade = (total_obitos / total_casos) * 100 if total_casos > 0 else 0

        # Exibindo os KPIs um abaixo do outro
        st.metric(label="Casos Totais", value=total_casos)
        st.metric(label="Óbitos Totais", value=total_obitos)
        st.metric(label="Taxa de Mortalidade", value=f"{taxa_mortalidade:.2f}%")




# ------------------------------------------------------------------------------
# SEGUNDA LINHA: Proporção de Casos por Estado | Número de Casos e Óbitos por Estado | Gráfico Dispersão Correlação
with st.container():
    colB1, colB2, colB3 = st.columns([3, 4, 4])
    with colB1:
        st.subheader("Proporção de Casos por Estado")
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        df_casos_estado = df_filtrado.groupby("ESTADO")["Casos_Total"].sum().reset_index()
        fig_pizza = px.pie(
            df_casos_estado,
            values="Casos_Total",
            names="ESTADO",
        )
        fig_pizza.update_traces(hovertemplate="%{value} casos em %{label}")
        st.plotly_chart(fig_pizza, use_container_width=True)
    with colB2:
        st.subheader("Febre Amarela: Número de Casos e Óbitos por Estado")
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
        st.plotly_chart(fig_bar, use_container_width=True)
    with colB3:
        st.subheader("Correlação entre Casos Totais e Fatores Climáticos")
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

        var_selecionada = st.selectbox(
            "Selecione um fator climático para análise:",
            list(opcoes_climaticas_disp.keys()),
            index=0
        )

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

        # Coluna formatada para Data
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
        st.plotly_chart(fig_dispersao, use_container_width=True)
        
# ------------------------------------------------------------------------------
# TERCEIRA LINHA: Linha Evol. Casos | Linha Evol. Fator Climático
with st.container():
    colC1, colC2 = st.columns([5,5])

    with colC1:
        st.subheader("Evolução Temporal de Casos de Febre Amarela")
        st.text("")
        st.text("")
        st.text("")
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
        st.plotly_chart(fig_evolucao, use_container_width=True)

    # Coluna B2: Gráfico de Linha Evolução Fator Climático
    with colC2:
        st.subheader("Evolução Temporal de um Fator Climático")

        opcoes_climaticas = {
            "Temperatura": "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)",
            "Precipitação": "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)",
            "Radiação": "RADIACAO GLOBAL (Kj/m²)",
            "Pressão": "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)"
        }
        unidades_climaticas = {
            "Temperatura": "Temperatura média (°C)",
            "Precipitação": "Precipitação total (mm)",
            "Radiação": "Radiação global (Kj/m²)",
            "Pressão": "Pressão atmosférica (mB)"
        }
        variavel_selecionada = st.selectbox(
            "Selecione um fator climático para visualizar:",
            list(opcoes_climaticas.keys()),
            index=0
        )

        df_climatico = df_filtrado.groupby(["ANO_IS", "MES_IS"]).agg({
            opcoes_climaticas[variavel_selecionada]: "mean"
        }).reset_index()

        df_climatico = df_climatico.rename(
            columns={opcoes_climaticas[variavel_selecionada]: variavel_selecionada}
        )

        fig_climatico = px.line(
            df_climatico,
            x="MES_IS",
            y=variavel_selecionada,
            color="ANO_IS",
            labels={
                "MES_IS": "Mês",
                variavel_selecionada: unidades_climaticas[variavel_selecionada],
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
        st.plotly_chart(fig_climatico, use_container_width=True)

# ------------------------------------------------------------------------------
# QUARTA LINHA: Linha Evol. Temporal de Casos, Óbitos e Fatires Climáticos Normalizada
with st.container():
        st.subheader("Evolução Temporal de Casos, Óbitos e Fatires Climáticos")
    # *Normalização dos dados*
        scaler = MinMaxScaler()
        colunas_normalizar = [
            "Casos_Total", "Obitos_Total",
            "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)",
            "RADIACAO GLOBAL (Kj/m²)",
            "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)",
            "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)"
        ]

        df_normal = df_filtrado.copy()
        df_normal[colunas_normalizar] = scaler.fit_transform(df_filtrado[colunas_normalizar])

        # Mapeamento para os nomes simplificados no seletor
        opcoes_seletor = {
            "Temperatura": "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)",
            "Radiação Global": "RADIACAO GLOBAL (Kj/m²)",
            "Precipitação": "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)",
            "Pressão Atmosférica": "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)"
        }

        variavel_climatica = st.selectbox(
            "Selecione a variável climática:",
            options=list(opcoes_seletor.keys()),
            index=0  # Padrão: Temperatura
        )

        # Obtém o nome técnico correspondente à opção selecionada
        variavel_tecnica = opcoes_seletor[variavel_climatica]

        # *Ajuste na Ordenação dos Meses*
        df_normal["MES_GLOBAL"] = df_normal["MES_IS"]
        if len(anos_selecionados) == 2:  # Se 2017 e 2018 foram selecionados
            df_normal.loc[df_normal["ANO_IS"] == 2018, "MES_GLOBAL"] += 12

        # Agrupando dados por mês e ano
        df_evolucao = df_normal.groupby(["ANO_IS", "MES_GLOBAL"]).agg({
            "Casos_Total": "sum",
            "Obitos_Total": "sum",
            "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)": "mean",
            "RADIACAO GLOBAL (Kj/m²)": "mean",
            "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)": "mean",
            "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)": "mean"
        }).reset_index()


        df_plot = df_evolucao.copy()

        # Criando um dataframe longo para o Plotly
        df_long = df_plot.melt(
            id_vars=["ANO_IS", "MES_GLOBAL"], 
            value_vars=["Casos_Total", "Obitos_Total", variavel_tecnica],
            var_name="Variável", 
            value_name="Valor"
        )

        # Mapeando nomes para melhor legibilidade no gráfico
        nome_variaveis = {
            "Casos_Total": "Casos",
            "Obitos_Total": "Óbitos",
            "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)": "Temperatura",
            "RADIACAO GLOBAL (Kj/m²)": "Radiação",
            "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)": "Precipitação",
            "PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)": "Pressão Atmosférica"
        }
        df_long["Variável"] = df_long["Variável"].map(nome_variaveis)

        # Criando o gráfico de linhas
        fig_evolucao = px.line(
            df_long,
            x="MES_GLOBAL",
            y="Valor",
            color="Variável",
            markers=True,
            labels={"MES_GLOBAL": "Mês", "Valor": "Valor Normalizado"},
        )

        # Definindo os meses de verão (Dez, Jan, Fev)
        meses_verao = [12, 1, 2]  # Considerando o ano calendário (Dez do ano anterior até Fev)

        # Adicionando retângulos para destacar os meses de verão
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

        # Exibir o gráfico
        st.plotly_chart(fig_evolucao, use_container_width=True)

    
