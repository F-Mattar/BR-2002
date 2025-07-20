import pandas as pd
import numpy as np
from fuzzywuzzy import process, fuzz
from datetime import datetime, timedelta

# Usar lista como fonte de nomes reais dos jogadores

jogadores = [
    {"Nome": "Marcos", "Posicao": "Goleiro", "Numero": 1},
    {"Nome": "Cafu", "Posicao": "Lateral-direito", "Numero": 2},
    {"Nome": "Lúcio", "Posicao": "Zagueiro", "Numero": 3},
    {"Nome": "Roque Júnior", "Posicao": "Zagueiro", "Numero": 4},
    {"Nome": "Edmilson", "Posicao": "Zagueiro", "Numero": 5},
    {"Nome": "Roberto Carlos", "Posicao": "Lateral-esquerdo", "Numero": 6},
    {"Nome": "Ricardinho", "Posicao": "Meio-campista", "Numero": 7},
    {"Nome": "Gilberto Silva", "Posicao": "Volante", "Numero": 8},
    {"Nome": "Ronaldo", "Posicao": "Atacante", "Numero": 9},
    {"Nome": "Rivaldo", "Posicao": "Meio-campista", "Numero": 10},
    {"Nome": "Ronaldinho Gaúcho", "Posicao": "Meio-campista", "Numero": 11},
    {"Nome": "Dida", "Posicao": "Goleiro", "Numero": 12},
    {"Nome": "Belletti", "Posicao": "Lateral-direito", "Numero": 13},
    {"Nome": "Anderson Polga", "Posicao": "Zagueiro", "Numero": 14},
    {"Nome": "Kléberson", "Posicao": "Volante", "Numero": 15},
    {"Nome": "Júnior", "Posicao": "Lateral-esquerdo", "Numero": 16},
    {"Nome": "Denílson", "Posicao": "Meio-campista", "Numero": 17},
    {"Nome": "Vampeta", "Posicao": "Volante", "Numero": 18},
    {"Nome": "Juninho Paulista", "Posicao": "Meio-campista", "Numero": 19},
    {"Nome": "Edílson", "Posicao": "Atacante", "Numero": 20},
    {"Nome": "Luizão", "Posicao": "Atacante", "Numero": 21},
    {"Nome": "Rogério Ceni", "Posicao": "Goleiro", "Numero": 22},
    {"Nome": "Kaká", "Posicao": "Meio-campista", "Numero": 23}
]

df_jogadores_oficiais = pd.DataFrame(jogadores)
nomes_oficiais = df_jogadores_oficiais['Nome'].unique().tolist()

try:
    df_jogos = pd.read_csv('data/dados_de_jogos.csv')
    df_medico = pd.read_csv('data/departamento_medico.csv')
    df_preparador = pd.read_csv('data/preparador_fisico.csv')
    
    print('CSVs carregados com sucesso!')

except FileNotFoundError as e:
    print(f"Erro ao carregar arquivo: {e}. Certifique-se de que os CSVs estão na pasta 'data'.")
    exit()

# Unificar os dados

df_raw = pd.concat([df_jogos, df_medico, df_preparador], ignore_index=True)
print(f"\nTotal de registros brutos após unificação: {len(df_raw)}")
print("Primeiras 5 linhas dos dados brutos unificados:")
print(df_raw.head())

# Converter 'Data' para datetime

print('\nConvertendo \'Data\' para tipo datetime...')
df_raw['Data'] = pd.to_datetime(df_raw['Data'])

# Ordenar por jogador e 'Data' para cálculos de janelas móveis

df_raw = df_raw.sort_values(by=['Nome_Jogador', 'Data']).reset_index(drop=True)

# Tratar inconsistências de nomes (reconciliação)

def standardize_name(name, choices, threshold=85):
    if pd.isna(name): # Casa haja ausência de nome
        return None
    if name in choices:
        return name
    
    # scorer para similaridade de string

    match, score = process.extractOne(name, choices, scorer=fuzz.ratio)
    
    if score >= threshold: # Similaridade alta o suficiente
        return match
    return name

print('\nPadronizando nomes dos jogadores...')

df_raw['Nome_Padronizado'] = df_raw['Nome_Jogador'].apply(lambda x: standardize_name(x,nomes_oficiais))

print('Padronização concluída com sucesso!')

nomes_com_variacoes = df_raw.groupby('Nome_Jogador')['Nome_Padronizado'].nunique()
nomes_expostos = nomes_com_variacoes[nomes_com_variacoes > 1].index.tolist()

if not nomes_expostos: # Caso não haja variações no nome após a padronização
    print(df_raw[['Nome_Jogador','Nome_Padronizado']].drop_duplicates().head(10))
else:
    print(df_raw[df_raw['Nome_Jogador'].isin(nomes_expostos)][['Nome_Jogador','Nome_Padronizado']].drop_duplicates())

# Tratar dados ausentes

print('\nTratando dados faltantes...')
numeric_cols = ['Distancia_Percorrida_(km)', 'Num_Sprints', 'VO2_Max_Estimado', 'FC_Media_(bpm)', 'Minutos_Jogados']
for col in numeric_cols:
    df_raw[col] = df_raw.groupby('Posicao')[col].transform(lambda x: x.fillna(x.mean()))
    df_raw[col] = df_raw[col].fillna(df_raw[col].mean())

df_raw['Lesao_Ocorreu'] = df_raw['Lesao_Ocorreu'].fillna(False).astype(bool)
df_raw['Tipo_Lesao'] = df_raw['Tipo_Lesao'].fillna('Nenhuma_Lesao')
df_raw['Tempo_Ausencia'] = df_raw['Tempo_Ausencia'].fillna(0).astype(int)

print("\nNúmero de valores nulos após tratamento (deve ser 0 para colunas principais):")
print(df_raw.isnull().sum())

# Garantir que todas as colunas numéricas tenham o tipo correto após preenchimento dos valores nulos

df_raw['Distancia_Percorrida_(km)'] = df_raw['Distancia_Percorrida_(km)'].astype(float)
df_raw['Num_Sprints'] = df_raw['Num_Sprints'].astype(int)
df_raw['VO2_Max_Estimado'] = df_raw['VO2_Max_Estimado'].astype(float)
df_raw['FC_Media_(bpm)'] = df_raw['FC_Media_(bpm)'].astype(int)
df_raw['Minutos_Jogados'] = df_raw['Minutos_Jogados'].astype(int)

# Implementação de Modelos Estatísticos / Detecção de Anomalias / Previsão de Risco de Lesão

print('\nIniciando análise de performance e risco de lesão...')

# Calcular métricas de janela móvel (rolling metrics) para cada jogador

df_raw['VO2_Media_7d'] = df_raw.groupby('Nome_Padronizado')['VO2_Max_Estimado'].transform(
    lambda x: x.rolling(window=7,min_periods=1).mean()
)
df_raw['Dist_Media_7d'] = df_raw.groupby('Nome_Padronizado')['Distancia_Percorrida_(km)'].transform(
    lambda x: x.rolling(window=7, min_periods=1).mean()
)
df_raw['Sprints_Media_7d'] = df_raw.groupby('Nome_Padronizado')['Num_Sprints'].transform(
    lambda x: x.rolling(window=7, min_periods=1).mean()
)

# Calcular desvio padrão móvel (para detecção de anomalia)

df_raw['VO2_DP_7d'] = df_raw.groupby('Nome_Padronizado')['VO2_Max_Estimado'].transform(
    lambda x: x.rolling(window=7, min_periods=1).std()
).fillna(0) # Preencher NaN (se window for menor que min_periods) com 0 para evitar erros em cálculos futuros)

df_raw['Dist_DP_7d'] = df_raw.groupby('Nome_Padronizado')['Distancia_Percorrida_(km)'].transform(
    lambda x: x.rolling(window=7, min_periods=1).std()
).fillna(0)

df_raw['Sprints_DP_7d'] = df_raw.groupby('Nome_Padronizado')['Num_Sprints'].transform(
    lambda x: x.rolling(window=7, min_periods=1).std()
).fillna(0)

# Detecção de Anomalias (usando 2 desvios padrão - regra de 95% de confiança)

df_raw['Alerta_VO2_Anomalo'] = (df_raw['VO2_Max_Estimado'] < (df_raw['VO2_Media_7d'] - 2 * df_raw['VO2_DP_7d'])) | \
                               (df_raw['VO2_Max_Estimado'] > (df_raw['VO2_Media_7d'] + 2 * df_raw['VO2_DP_7d']))

df_raw['Alerta_Dist_Anomala'] = (df_raw['Distancia_Percorrida_(km)'] > (df_raw['Dist_Media_7d'] + 2 * df_raw['Dist_DP_7d']))
df_raw['Alerta_Sprints_Anomalos'] = (df_raw['Num_Sprints'] > (df_raw['Sprints_Media_7d'] + 2 * df_raw['Sprints_DP_7d']))

df_raw['Alerta_Dist_Anomala'] = (df_raw['Distancia_Percorrida_(km)'] > (df_raw['Dist_Media_7d'] + 2 * df_raw['Dist_DP_7d']))
df_raw['Alerta_Sprints_Anomalos'] = (df_raw['Num_Sprints'] > (df_raw['Sprints_Media_7d'] + 2 * df_raw['Sprints_DP_7d']))

# Implementar a pontuação de risco de lesão

df_raw['Pontuacao_Risco_Lesao'] = 0

# Adicionar pontos com bas nas anomalias detectadas

df_raw.loc[df_raw['Alerta_VO2_Anomalo'], 'Pontuacao_Risco_Lesao'] += 3 # Queda/Aumento anômalo de VO2 é um risco alto
df_raw.loc[df_raw['Alerta_Dist_Anomala'], 'Pontuacao_Risco_Lesao'] += 2 # Pico de distância é risco moderado
df_raw.loc[df_raw['Alerta_Sprints_Anomalos'], 'Pontuacao_Risco_Lesao'] += 2 # Pico de sprints é risco moderado

# Contar número de lesões anteriores

df_raw['Lesoes_Anteriores_Acumuladas'] = df_raw.groupby('Nome_Padronizado')['Lesao_Ocorreu'].cumsum() - df_raw['Lesao_Ocorreu']
df_raw.loc[df_raw['Lesoes_Anteriores_Acumuladas'] > 0, 'Pontuacao_Risco_Lesao'] += 1 # Aumenta risco se já teve lesão

# Mapear pontuação para categorias de risco

def map_risk_score(score):
    if score >= 5:
        return 'Muito Alto'
    elif score >= 3:
        return 'Alto'
    elif score >= 1:
        return 'Moderado'
    else:
        return 'Baixo'

df_raw['Categoria_Risco_Lesao'] = df_raw['Pontuacao_Risco_Lesao'].apply(map_risk_score)

print("\nAnálise de risco de lesão concluída.")
print("Linhas com as novas métricas de risco:")
print(df_raw[['Data', 'Nome_Padronizado', 'VO2_Max_Estimado', 'Alerta_VO2_Anomalo', 'Distancia_Percorrida_(km)', 'Alerta_Dist_Anomala', 'Pontuacao_Risco_Lesao', 'Categoria_Risco_Lesao', 'Lesao_Ocorreu', 'Tipo_Lesao', 'Tempo_Ausencia']].head(10))