# 📊  Data_Science_Dashboard_Final

Este repositório contém um **dashboard interativo** desenvolvido com **Streamlit** e **Plotly**, que permite visualizar e analisar dados relacionados a casos e óbitos por estado, além de sua correlação com fatores climáticos.  

## 📝 Descrição  

O dashboard apresenta:  

- **Seleção dinâmica de anos e estados** para análise  
- **Resumo geral** com total de casos e óbitos  
- **Mapa** dos estados do Sudeste  
- **Gráficos de barras e linhas** para análise temporal e distribuição de casos  
- **Gráfico de dispersão** para correlação entre fatores climáticos e casos  

## 📂 Estrutura do Repositório  

```
📦 Data_Science_Dashboard
 ┣ 📜 dataset_unificado_processado.csv  # Dataset utilizado na análise
 ┣ 📜 final1.py                         # Código principal do dashboard
 ┗ 📜 README.md                         # Este arquivo
 ┗ 📜 logo mosquito.png                 # Imagem da logo do dashboard
```

## 🚀 Como Executar  

### 1️⃣ Pré-requisitos  
Você precisa ter **Python 3.8+** instalado, além das seguintes bibliotecas:  

```bash
pip install streamlit pandas numpy plotly requests scikit-learn
```

### 2️⃣ Executar o Dashboard  
Clone este repositório e execute o seguinte comando no terminal:  

```bash
streamlit run final1.py
```

O Streamlit abrirá automaticamente o dashboard no seu navegador.  

## 📊 Exemplo de Visualização  

 
![image](https://github.com/user-attachments/assets/4f18259d-d1d6-48d9-ad45-15ca88d1f61c)


## 📌 Funcionalidades  

✔️ Filtragem por **ano** e **estado**  
✔️ **Resumo geral** de casos e óbitos  
✔️ **Mapa** do Sudeste brasileiro  
✔️ **Gráficos dinâmicos** para análise de evolução e correlação  


