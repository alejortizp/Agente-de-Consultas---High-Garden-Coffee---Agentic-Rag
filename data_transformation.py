"""
Transformacion de Datos (EDA) - Dataset de Consumo Doméstico de Café
Proyecto: High Garden Coffee - Agente de Consultas
"""

import numpy as np
import pandas as pd


# =============================================================================
# 1. CARGA Y TRANSFORMACIÓN (reproducción de analisis.py)
# =============================================================================
df_coffe = pd.read_parquet('coffee_db.parquet', engine='pyarrow')

var_anios = [c for c in df_coffe.columns if '/' in c and c != 'Coffee type']

df_coffe.set_index('Country', inplace=True)
df_t_coffe = df_coffe[var_anios].T
df_t_coffe['Fecha'] = pd.to_datetime(df_t_coffe.index, format='%Y/%y')

cols = df_t_coffe.columns
df_melted = df_t_coffe.melt(
    id_vars=['Fecha'], value_vars=cols.drop('Fecha'),
    var_name='Country', value_name='Ventas'
)

df_coffe.reset_index(inplace=True)
df_final = pd.merge(
    df_melted,
    df_coffe[['Country', 'Coffee type']].drop_duplicates(),
    on='Country', how='left'
)

# Normalizar tipos de café: unificar mezclas en una sola categoría
df_final['Coffee type'] = df_final['Coffee type'].replace({
    'Robusta/Arabica': 'Mezcla (Arabica/Robusta)',
    'Arabica/Robusta': 'Mezcla (Arabica/Robusta)',
})

df_final.to_csv('coffee_final.csv', index=False)
