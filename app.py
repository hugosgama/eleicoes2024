import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import elections as el

selected_year = st.sidebar.selectbox("Selecione o ano", options=[2024])
selected_candidate_type = st.sidebar.selectbox("Selecione o tipo de candidatura", options=['Prefeito', 'Vereador'])
selected_location = st.sidebar.selectbox("Selecione o tipo de candidatura", options=['AC','AM', 'AL', 'AP', 'BA',
                                                                                     'CE','ES','GO' ,'MA','MG','MS','MT',
                                                                                     'PA', 'PB', 'PE', 'PI', 'PR', 'RJ',
                                                                                     'RN', 'RO','RR', 'RS','SC','SE','SP', 'TO'])

# Título da aplicação
st.title(f'Eleições Municipais {selected_year}')

result_df = el.read_elections_data(selected_year, selected_candidate_type, selected_location)

# Mostrar os dados carregados
st.header(f"Dados Carregados - Eleições {selected_location} {selected_year}")
st.write(result_df.head())

#Explorar os dados
st.header("Explorando os Dados")

st.subheader("Estastíticas Descritivas")
st.write(result_df.describe())

column_options = result_df.columns.tolist()
selected_column = st.selectbox("Selecione a coluna para visualizar",index=10, options=column_options)

fig = px.histogram(result_df, x=selected_column)
st.plotly_chart(fig)

#Analisar os resultados por espectro
st.header("Análise dos resultados por espectro")
# Seção para upload de arquivo
parties_uploaded_filename = st.file_uploader("Faça upload do arquivo com espectro dos partidos  (formato CSV com sep = ;)", type=["csv"])

# Verificar se o arquivo foi carregado
if parties_uploaded_filename is not None:
    uploaded_df = pd.read_csv(parties_uploaded_filename, sep=';')

    st.subheader(f"Dados Carregados")
    st.write(uploaded_df.head())

    result_df = el.merge_elections_with_partidos(result_df, uploaded_df)

    st.subheader(f'Partido do Candidato Mais Votado por Município {selected_location} 2024 ({selected_candidate_type})')
    fig2 = px.histogram(result_df, x='SG_PARTIDO').update_xaxes(categoryorder='total descending')
    st.plotly_chart(fig2)

    st.subheader(f'Candidatos mais Votados por Espectro {selected_location} 2024 ({selected_candidate_type})')
    fig3 = px.histogram(result_df, x='Espectro').update_xaxes(categoryorder='total descending')
    st.plotly_chart(fig3)

    result_df = el.merge_elections_with_shapefile(result_df, selected_location)

    fig4, ax = plt.subplots(1,1,figsize=(28,10))
    st.subheader(f'Espectro do Candidato ({selected_candidate_type}) Mais Votado por Município {selected_location} - {selected_year}')
    result_df.plot(column='Espectro', legend=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig4)



