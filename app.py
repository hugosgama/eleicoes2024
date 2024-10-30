import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import elections as el

# Função para carregar e exibir os dados
def load_election_data(year, candidate_type, location):
    st.title(f'Eleições Municipais {year}')
    
    # Carregar os dados das eleições
    result_df = el.read_elections_data(year, candidate_type, location)

    # Mostrar os dados carregados
    st.header(f"Dados Carregados - Eleições {location} {year}")
    st.write(result_df.head())
    
    return result_df

# Função para explorar os dados
def explore_data(result_df):
    st.header("Explorando os Dados")

    # Estatísticas descritivas
    st.subheader("Estatísticas Descritivas")
    st.write(result_df.describe())

    # Seleção de coluna para visualização
    column_options = result_df.columns.tolist()
    selected_column = st.selectbox("Selecione a coluna para visualizar", options=column_options, index=0)

    # Exibir histograma da coluna selecionada
    fig = px.histogram(result_df, x=selected_column)
    st.plotly_chart(fig)

# Função para análise de espectro dos resultados
def analyze_results_by_spectrum(result_df, location, year, candidate_type):
    st.header("Análise dos resultados por espectro")
    
    # Upload de arquivo com espectro dos partidos
    parties_uploaded_filename = st.file_uploader("Faça upload do arquivo com espectro dos partidos (formato CSV com sep=';')", type=["csv"])
    
    if parties_uploaded_filename is not None:
        # Carregar o arquivo CSV
        uploaded_df = pd.read_csv(parties_uploaded_filename, sep=';')
        st.subheader(f"Dados Carregados")
        st.write(uploaded_df.head())

        # Mesclar os dados eleitorais com os partidos
        result_df = el.merge_elections_with_partidos(result_df, uploaded_df)

        # Exibir gráfico dos partidos mais votados
        st.subheader(f'Partido do Candidato Mais Votado por Município {location} 2024 ({candidate_type})')
        fig2 = px.histogram(result_df, x='SG_PARTIDO').update_xaxes(categoryorder='total descending')
        st.plotly_chart(fig2)

        # Exibir gráfico por espectro
        st.subheader(f'Candidatos mais Votados por Espectro {location} 2024 ({candidate_type})')
        fig3 = px.histogram(result_df, x='Espectro').update_xaxes(categoryorder='total descending')
        st.plotly_chart(fig3)

        # Mesclar dados com shapefile para visualização geográfica
        result_df = el.merge_elections_with_shapefile(result_df, location)

        # Exibir mapa do espectro político
        fig4, ax = plt.subplots(1, 1, figsize=(28, 10))
        st.subheader(f'Espectro do Candidato ({candidate_type}) Mais Votado por Município {location} - {year}')
        result_df.plot(column='Espectro', legend=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig4)

# Interface principal do Streamlit
def main():
    # Seção de seleção na barra lateral
    selected_year = st.sidebar.selectbox("Selecione o ano", options=[2024,2020,2016,2012,2008])
    selected_candidate_type = st.sidebar.selectbox("Selecione o tipo de candidatura", options=['Prefeito','Vereador','Deputado Estadual','Deputado Federal',
                                                                                               'Governador','Senador'])
    selected_location = st.sidebar.selectbox("Selecione a localidade", 
                                             options=['AC','AM','AL','AP','BA','BR','CE','ES','GO','MA','MG', 
                                                      'MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO', 
                                                      'RR','RS','SC','SE','SP','TO'])
    
    # Carregar os dados de eleição
    result_df = load_election_data(selected_year, selected_candidate_type, selected_location)
    
    # Explorar os dados
    explore_data(result_df)
    
    # Analisar os resultados por espectro
    analyze_results_by_spectrum(result_df, selected_location, selected_year, selected_candidate_type)

# Executar a aplicação
if __name__ == "__main__":
    main()
