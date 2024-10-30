import os
import pandas as pd
from zipfile import ZipFile
import geopandas as gpd

FOLDER = './data-sources/'

def read_elections_data(year, candidate_type, location):
    """
    Lê os dados de eleição a partir de um arquivo ZIP, filtra por tipo de candidatura e localidade.
    """
    file_path = os.path.join(FOLDER, f'votacao_candidato_munzona_{year}.zip')
    file_name = f'votacao_candidato_munzona_{year}_BRASIL.csv'

    # Verifica se o arquivo existe antes de tentar abri-lo
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")

    try:
        with ZipFile(file_path) as zip_file:
            with zip_file.open(file_name) as file:
                # Lê o CSV do arquivo ZIP
                df = pd.read_csv(file, sep=';', encoding='ISO-8859-1', decimal=',')

                # Filtra pelo tipo de candidatura (Prefeito ou Vereador)
                filtered_df = df[df['DS_CARGO'] == candidate_type].reset_index(drop=True)
                
                # Filtra pela localidade, se necessário
                if location != 'BR':
                    filtered_df = filtered_df[filtered_df['SG_UF'] == location].reset_index(drop=True)

                return filtered_df

    except Exception as e:
        raise Exception(f"Erro ao ler os dados: {e}")

def merge_elections_with_partidos(elections_df, parties_df):
    """
    Mescla os dados de eleições com os dados de espectro político dos partidos.
    """
    # Define a categorização de espectro político
    espectro_type = pd.CategoricalDtype(categories=['direita', 'centro', 'esquerda'], ordered=True)
    parties_df['Espectro'] = parties_df['Espectro'].astype(espectro_type)
    
    # Mescla os dados de eleição com o espectro dos partidos
    merged_df = elections_df.merge(parties_df[['NR_PARTIDO', 'Espectro']], on='NR_PARTIDO', how='left')

    # Agrupa por candidato e município, somando os votos e pegando a primeira ocorrência de outras colunas
    grouped_df = merged_df.groupby(['NR_CANDIDATO', 'NM_UE']).agg({
        'Espectro': 'first',
        'NM_URNA_CANDIDATO': 'first',
        'NM_MUNICIPIO': 'first',
        'CD_MUNICIPIO': 'first',
        'SG_UF': 'first',
        'DS_SIT_TOT_TURNO': 'first',
        'NR_PARTIDO': 'first',
        'SG_PARTIDO': 'first',
        'QT_VOTOS_NOMINAIS': 'sum'
    }).reset_index()

    # Ordena pelos votos nominais em ordem decrescente e remove duplicatas de municípios
    grouped_df = grouped_df.sort_values(by='QT_VOTOS_NOMINAIS', ascending=False)
    unique_df = grouped_df.drop_duplicates(subset=['CD_MUNICIPIO'], keep='first')

    return unique_df

def merge_elections_with_shapefile(elections_df, location):
    """
    Mescla os dados de eleições com o shapefile correspondente para visualização geográfica.
    """
    shapefile_path = os.path.join(FOLDER, f'shapefiles/{location}_Municipios_2022/{location}_Municipios_2022.shp')

    # Verifica se o shapefile existe antes de tentar abri-lo
    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"O shapefile {shapefile_path} não foi encontrado.")

    try:
        # Lê o shapefile usando geopandas
        geo_df = gpd.read_file(shapefile_path)
        
        # Normaliza os nomes dos municípios para facilitar o merge
        geo_df['NM_MUN'] = geo_df['NM_MUN'].str.upper()
        
        # Mescla os dados eleitorais com o shapefile
        merged_geo_df = geo_df.merge(elections_df, left_on='NM_MUN', right_on='NM_MUNICIPIO', how='left')

        return merged_geo_df

    except Exception as e:
        raise Exception(f"Erro ao mesclar com shapefile: {e}")
