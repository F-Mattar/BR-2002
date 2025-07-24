import pandas as pd
import numpy as np
from fuzzywuzzy import process, fuzz
from datetime import datetime, timedelta
import os
from sqlalchemy import create_engine

# --- Encapsulando a lógica principal em uma função ---
def run_data_processor():
    """
    Processa, reconcilia e analisa os dados de performance de jogadores,
    calculando métricas adicionais e salvando em CSV e SQLite.
    """
    print("--- Etapa 2: Processando e Reconciliando Dados ---")

    # Lista de jogadores OFICIAIS com algumas variações comuns/esperadas para reconciliação.
    # A chave "Nome" é o nome OFICIAL, e a lista pode incluir variações de escrita.
    # O fuzzywuzzy usará a lista de "nomes_oficiais_para_fuzzy" para buscar correspondências.
    jogadores_oficiais_e_aliases = [
        {"Nome": "Marcos", "Posicao": "Goleiro", "Numero": 1},
        {"Nome": "Cafu", "Posicao": "Lateral-direito", "Numero": 2},
        {"Nome": "Lúcio", "Posicao": "Zagueiro", "Numero": 3},
        {"Nome": "Roque Júnior", "Posicao": "Zagueiro", "Numero": 4},
        {"Nome": "Edmilson", "Posicao": "Volante", "Numero": 5},
        {"Nome": "Roberto Carlos", "Posicao": "Lateral-esquerdo", "Numero": 6},
        {"Nome": "Ricardinho", "Posicao": "Meio-campista", "Numero": 7},
        {"Nome": "Gilberto Silva", "Posicao": "Volante", "Numero": 8},
        {"Nome": "Ronaldo", "Posicao": "Atacante", "Numero": 9},
        {"Nome": "Rivaldo", "Posicao": "Atacante", "Numero": 10},
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

    # A lista de nomes OFICIAIS para o fuzzywuzzy procurar correspondências.
    nomes_oficiais_para_fuzzy = [j["Nome"] for j in jogadores_oficiais_e_aliases]
    nomes_oficiais_para_fuzzy = list(set(nomes_oficiais_para_fuzzy)) # Remove duplicatas se houver

    # Criar um DataFrame com a informação oficial (Nome, Posicao, Numero) para eventual merge
    df_jogadores_oficiais_info = pd.DataFrame(jogadores_oficiais_e_aliases)
    df_jogadores_oficiais_info = df_jogadores_oficiais_info.drop_duplicates(subset=['Nome']) # Garantir nomes únicos para join

    # Criar a pasta 'data' se não existir (garantia)
    DATA_FOLDER = 'data'
    os.makedirs(DATA_FOLDER, exist_ok=True)

    # Configurações do Banco de Dados
    DB_FILE = os.path.join(DATA_FOLDER, 'performance_data.db')
    TABLE_NAME = 'performance_atletas'
    engine = create_engine(f'sqlite:///{DB_FILE}')

    # Carregar o arquivo unificado gerado pelo data_generator.py
    PROCESSED_DATA_INPUT_FILE = os.path.join(DATA_FOLDER, 'performance_completa_gerada.csv')

    try:
        df_raw = pd.read_csv(PROCESSED_DATA_INPUT_FILE)
        print(f"Dados carregados com sucesso de: {PROCESSED_DATA_INPUT_FILE}")
        print(f"\nTotal de registros brutos após carregamento: {len(df_raw)}")
        print("Primeiras 5 linhas dos dados brutos (antes da reconciliação):")
        print(df_raw.head())
        print(f"\nNomes únicos em Nome_Jogador antes da reconciliação: {df_raw['Nome_Jogador'].nunique()}")
        print(f"Lista de nomes únicos: {sorted(df_raw['Nome_Jogador'].unique().tolist())}")


    except FileNotFoundError as e:
        print(f"Erro ao carregar arquivo: {e}. Certifique-se de que '{PROCESSED_DATA_INPUT_FILE}' está na pasta 'data'.")
        print("Você precisa rodar o 'data_generator.py' atualizado antes de rodar este script.")
        return # Use return para sair da função em caso de erro

    # Converter 'Data' para datetime
    print('\nConvertendo \'Data\' para tipo datetime...')
    df_raw['Data'] = pd.to_datetime(df_raw['Data'])

    # Tratar inconsistências de nomes (reconciliação)
    def standardize_name(name, choices, threshold=85):
        if pd.isna(name):
            return None
        
        known_aliases = {
            'Ronaldo Fenômeno': 'Ronaldo',
            'Ronaldo Nazário': 'Ronaldo',
            'Ronaldinho': 'Ronaldinho Gaúcho',
            'Luizao': 'Luizão',
            'Denilson': 'Denílson'
        }

        if name in known_aliases:
            return known_aliases[name]
        
        if name in choices:
            return name

        match, score = process.extractOne(name, choices, scorer=fuzz.ratio)
        if score >= threshold:
            return match
        return name

    print('\nPadronizando nomes dos jogadores com fuzzywuzzy...')
    df_raw['Nome_Padronizado'] = df_raw['Nome_Jogador'].apply(lambda x: standardize_name(x, nomes_oficiais_para_fuzzy))
    print('Padronização concluída com sucesso!')

    print("\nVerificação de nomes após padronização:")
    nomes_unicos_apos_padronizacao = df_raw['Nome_Padronizado'].unique().tolist()
    print(f"Número de nomes únicos após padronização: {len(nomes_unicos_apos_padronizacao)}")
    print(f"Lista de nomes únicos: {sorted(nomes_unicos_apos_padronizacao)}")

    # Verificar nomes que podem ter mais de uma variação original mapeada para eles ou vice-versa
    nomes_originais_por_padronizado = df_raw.groupby('Nome_Padronizado')['Nome_Jogador'].nunique()
    nomes_padronizados_com_multiplas_origens = nomes_originais_por_padronizado[nomes_originais_por_padronizado > 1]

    if not nomes_padronizados_com_multiplas_origens.empty:
        print("\nNomes padronizados que resultaram de múltiplas variações originais:")
        for nome_padr, count in nomes_padronizados_com_multiplas_origens.items():
            original_names = df_raw[df_raw['Nome_Padronizado'] == nome_padr]['Nome_Jogador'].unique().tolist()
            print(f"  '{nome_padr}' foi mapeado de: {original_names}")
    else:
        print("\nTodos os nomes originais foram mapeados para um único nome padronizado sem conflito aparente.")

    # Ordenar por jogador padronizado e 'Data' para cálculos de janelas móveis
    df_raw = df_raw.sort_values(by=['Nome_Padronizado', 'Data']).reset_index(drop=True)

    # Tratar dados ausentes
    print('\nTratando dados faltantes (se houver algum após a geração)...')
    numeric_cols_to_fill = [
        'Minutos_Jogados', 'Distancia_Percorrida_(km)', 'Num_Sprints',
        'VO2_Max_Estimado', 'FC_Media_(bpm)',
        'Acute_Workload', 'Chronic_Workload', 'ACWR',
        'Dias_Desde_Ultima_Lesao', 'Num_Lesoes_Anteriores'
    ]

    for col in numeric_cols_to_fill:
        if col in df_raw.columns:
            df_raw[col] = df_raw.groupby('Posicao')[col].transform(lambda x: x.fillna(x.mean()))
            df_raw[col] = df_raw[col].fillna(df_raw[col].mean())
        else:
            print(f"Aviso: Coluna '{col}' não encontrada no DataFrame, ignorando preenchimento de NaN.")

    if 'Dias_Desde_Ultima_Lesao' in df_raw.columns:
        df_raw['Dias_Desde_Ultima_Lesao'] = df_raw['Dias_Desde_Ultima_Lesao'].fillna(df_raw['Dias_Desde_Ultima_Lesao'].mean())

    # Garantir tipos de dados para colunas numéricas
    for col in ['Minutos_Jogados', 'Num_Sprints', 'FC_Media_(bpm)']:
        if col in df_raw.columns:
            df_raw[col] = df_raw[col].astype(int)
    for col in ['Distancia_Percorrida_(km)', 'VO2_Max_Estimado', 'Acute_Workload', 'Chronic_Workload', 'ACWR']:
        if col in df_raw.columns:
            df_raw[col] = df_raw[col].astype(float)
    if 'Num_Lesoes_Anteriores' in df_raw.columns:
        df_raw['Num_Lesoes_Anteriores'] = df_raw['Num_Lesoes_Anteriores'].astype(int)

    df_raw['Lesao_Ocorreu'] = df_raw['Lesao_Ocorreu'].fillna(False).astype(bool)
    df_raw['Tipo_Lesao'] = df_raw['Tipo_Lesao'].fillna('Nenhuma_Lesao').astype(str)
    df_raw['Tempo_Ausencia'] = df_raw['Tempo_Ausencia'].fillna(0).astype(int)


    print("\nNúmero de valores nulos após tratamento (deve ser 0 ou muito próximo para colunas principais):")
    print(df_raw.isnull().sum())


    # Implementação de Modelos Estatísticos / Detecção de Anomalias / Previsão de Risco de Lesão
    print('\nIniciando análise de performance e risco de lesão (cálculo de rolling metrics e score de risco)...')

    # Calcular métricas de janela móvel (rolling metrics) para cada jogador
    df_raw['VO2_Media_7d'] = df_raw.groupby('Nome_Padronizado')['VO2_Max_Estimado'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
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
    ).fillna(0)
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

    # Implementar a pontuação de risco de lesão
    df_raw['Pontuacao_Risco_Lesao'] = 0

    # Adicionar pontos com base nas anomalias detectadas
    df_raw.loc[df_raw['Alerta_VO2_Anomalo'], 'Pontuacao_Risco_Lesao'] += 3
    df_raw.loc[df_raw['Alerta_Dist_Anomala'], 'Pontuacao_Risco_Lesao'] += 2
    df_raw.loc[df_raw['Alerta_Sprints_Anomalos'], 'Pontuacao_Risco_Lesao'] += 2

    # Usar 'Num_Lesoes_Anteriores' do data_generator
    df_raw.loc[df_raw['Num_Lesoes_Anteriores'] > 0, 'Pontuacao_Risco_Lesao'] += 1

    # --- ALTERAÇÃO PRINCIPAL AQUI PARA O data_processor.py ---
    # Mapear pontuação para categorias de risco (AJUSTADO PARA INCLUIR 1 EM 'BAIXO')
    def map_risk_score(score):
        if score >= 6: # Para pontuações 6 ou mais
            return 'Muito Alto'
        elif score >= 4: # Para pontuações 4 ou 5
            return 'Alto'
        elif score >= 2: # Para pontuações 2 ou 3
            return 'Moderado'
        elif score >=0 and score <= 1: # Para pontuações 0 ou 1
            return 'Baixo'
        else: # Caso haja algum score negativo ou inválido
            return 'Desconhecido'

    df_raw['Categoria_Risco_Lesao'] = df_raw['Pontuacao_Risco_Lesao'].apply(map_risk_score)

    print("\nAnálise de risco de lesão concluída.")
    print("Linhas com as novas métricas de risco (últimas 10):")
    print(df_raw[['Data', 'Nome_Padronizado', 'Pontuacao_Risco_Lesao', 'Categoria_Risco_Lesao']].tail(10))

    # --- DEBUG: Dados Finais Antes de Salvar (DATA PROCESSOR) ---
    print("\n--- DEBUG: Dados Finais Antes de Salvar (DATA PROCESSOR) ---")
    print("Amostra de 'Pontuacao_Risco_Lesao' e 'Categoria_Risco_Lesao':")
    # Mostrar todas as linhas onde Pontuacao_Risco_Lesao é 0 ou 1
    debug_risk_data = df_raw[df_raw['Pontuacao_Risco_Lesao'].isin([0, 1])]
    if not debug_risk_data.empty:
        print(debug_risk_data[['Data', 'Nome_Padronizado', 'Pontuacao_Risco_Lesao', 'Categoria_Risco_Lesao']].head(20))
    else:
        print("Nenhum registro com Pontuacao_Risco_Lesao 0 ou 1 encontrado nesta amostra.")

    print("\nTipos de dados das colunas de risco:")
    print(df_raw[['Pontuacao_Risco_Lesao', 'Categoria_Risco_Lesao']].dtypes)

    print("\nContagem de valores na 'Pontuacao_Risco_Lesao':")
    print(df_raw['Pontuacao_Risco_Lesao'].value_counts(dropna=False))

    print("\nContagem de valores na 'Categoria_Risco_Lesao':")
    print(df_raw['Categoria_Risco_Lesao'].value_counts(dropna=False))
    print("\n--- Fim DEBUG: DATA PROCESSOR ---")

    # Definir o caminho para o arquivo de saída
    PROCESSED_DATA_OUTPUT_FILE = os.path.join(DATA_FOLDER, 'performance_reconciliada_e_analisada.csv')

    # Reordenar colunas e salvar o DataFrame reconciliado e analisado no CSV
    final_columns = [
        'Nome_Jogador', 'Nome_Padronizado', 'Posicao', 'Data', 'Tipo_Atividade',
        'Minutos_Jogados', 'Distancia_Percorrida_(km)', 'Num_Sprints',
        'VO2_Max_Estimado', 'FC_Media_(bpm)',
        'Lesao_Ocorreu', 'Tipo_Lesao', 'Tempo_Ausencia',
        'VO2_Media_7d', 'Dist_Media_7d', 'Sprints_Media_7d',
        'VO2_DP_7d', 'Dist_DP_7d', 'Sprints_DP_7d',
        'Alerta_VO2_Anomalo', 'Alerta_Dist_Anomala', 'Alerta_Sprints_Anomalos',
        'Pontuacao_Risco_Lesao', 'Categoria_Risco_Lesao',
        'Num_Lesoes_Anteriores', 
        'Acute_Workload', 'Chronic_Workload', 'ACWR', 'Dias_Desde_Ultima_Lesao',
        'Fonte'
    ]

    existing_columns_to_save = [col for col in final_columns if col in df_raw.columns]
    df_raw[existing_columns_to_save].to_csv(PROCESSED_DATA_OUTPUT_FILE, index=False)
    print(f"\nDataFrame processado salvo em CSV: {PROCESSED_DATA_OUTPUT_FILE}")

    # Salvar no banco de dados SQLite
    # Usar if_exists='replace' para sobrescrever a tabela existente com os dados processados
    print(f"\nSalvando DataFrame no banco de dados SQLite: {DB_FILE} na tabela '{TABLE_NAME}'...")
    df_raw[existing_columns_to_save].to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
    print("Dados salvos no banco de dados com sucesso.")

    print("\nDistribuição de Tipos de Atividade no DataFrame final:")
    print(df_raw['Tipo_Atividade'].value_counts())
    print("\n--- Etapa 2 Concluída ---")
    
# --- Bloco de execução para permitir que o script rode sozinho ---
if __name__ == "__main__":
    run_data_processor()