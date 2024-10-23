import os
import pandas as pd
from zipfile import ZipFile
import geopandas as gpd

FOLDER = '/Users/kterra/projects/streamlit-eleicoes/data-sources/'

def read_elections_data(year, candidate_type, location):
    file_path = os.path.join(FOLDER, f'votacao_candidato_munzona_{year}.zip')
    file_name = f'votacao_candidato_munzona_{year}_BRASIL.csv'
    with ZipFile(file_path) as z:
        with z.open(file_name) as f:
            selected_df = pd.read_csv(f,sep=';',encoding='ISO-8859-1', decimal=',')   
            selected_df = selected_df[selected_df['DS_CARGO']== candidate_type].reset_index(drop=True)      
            if (location != 'BR'):
                selected_df = selected_df[selected_df['SG_UF']==location].reset_index(drop=True)      


    return selected_df

def merge_elections_with_partidos(selected_df, df_partidos):

    espec_type = pd.CategoricalDtype(categories=['direita', 'centro', 'esquerda'], ordered=True)
    df_partidos['Espectro'] = df_partidos['Espectro'].astype(espec_type)
    
    selected_df = selected_df.merge(df_partidos[['NR_PARTIDO','Espectro']], left_on='NR_PARTIDO', right_on='NR_PARTIDO')

    selected_df = selected_df.groupby(['NR_CANDIDATO','NM_UE'])\
        .agg({'Espectro' :'first','NM_URNA_CANDIDATO' :'first', 
              'NM_MUNICIPIO' :'first', 'CD_MUNICIPIO' :'first', 'SG_UF' :'first',
      'DS_SIT_TOT_TURNO' :'first', 'NR_PARTIDO' :'first',
      'SG_PARTIDO' :'first','QT_VOTOS_NOMINAIS' : 'sum' })\
      .sort_values(by='QT_VOTOS_NOMINAIS',ascending=False)\
      .drop_duplicates(subset=['CD_MUNICIPIO'],keep='first')

    return selected_df

def merge_elections_with_shapefile(selected_df, location):

    SHAPEFILE_PATH= os.path.join(FOLDER, f'shapefiles/{location}_Municipios_2022/{location}_Municipios_2022.shp')
                
    geo_df = gpd.read_file(SHAPEFILE_PATH)
    geo_df['NM_MUN'] = geo_df['NM_MUN'].str.upper()
 
    selected_df = geo_df.merge(selected_df, left_on='NM_MUN', right_on='NM_MUNICIPIO')

    return selected_df
