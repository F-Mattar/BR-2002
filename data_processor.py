import pandas as pd
import numpy as np
from fuzzywuzzy import process, fuzz
from datetime import datetime, timedelta
import os
from sqlalchemy import create_engine

# --- Encapsulando a lógica principal em uma função ---

def executar_processamento_dados():
    """
    Processa, reconcilia e analisa os dados de performance de jogadores,
    calculando métricas adicionais e salvando em CSV e SQLite.
    """
    print("--- Etapa 2: Processando e Reconciliando Dados ---")

    # Lista de jogadores oficiais com algumas variações comuns/esperadas para reconciliação.

    # O fuzzywuzzy usará a lista de "nomes_oficiais_para_fuzzy" para buscar correspondências.

    jogadores_oficiais_e_apelidos = [
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

    # A lista de nomes oficiais para o fuzzywuzzy procurar correspondências.

    nomes_oficiais_para_fuzzy = [j["Nome"] for j in jogadores_oficiais_e_apelidos]
    nomes_oficiais_para_fuzzy = list(set(nomes_oficiais_para_fuzzy)) # Remove duplicatas se houver

    # Criar um DataFrame com a informação oficial (Nome, Posicao, Numero)

    df_info_jogadores_oficiais = pd.DataFrame(jogadores_oficiais_e_apelidos)
    df_info_jogadores_oficiais = df_info_jogadores_oficiais.drop_duplicates(subset=['Nome']) # Garantir nomes únicos

    # Criar a pasta 'data' se não existir (garantia)

    PASTA_DADOS = 'data'
    os.makedirs(PASTA_DADOS, exist_ok=True)

    # Configurações do Banco de Dados

    ARQUIVO_DB = os.path.join(PASTA_DADOS, 'dados_performance.db')
    NOME_TABELA = 'performance_atletas'
    engine = create_engine(f'sqlite:///{ARQUIVO_DB}')

    # Carregar o arquivo unificado gerado pelo gerador_dados.py

    ARQUIVO_ENTRADA_PROCESSAMENTO = os.path.join(PASTA_DADOS, 'performance_completa_gerada.csv')

    try:
        df_bruto = pd.read_csv(ARQUIVO_ENTRADA_PROCESSAMENTO)
        print(f"Dados carregados com sucesso de: {ARQUIVO_ENTRADA_PROCESSAMENTO}")
        print(f"\nTotal de registros brutos após carregamento: {len(df_bruto)}")
        print("Primeiras 5 linhas dos dados brutos (antes da reconciliação):")
        print(df_bruto.head())
        print(f"\nNomes únicos em Nome_Jogador antes da reconciliação: {df_bruto['Nome_Jogador'].nunique()}")
        print(f"Lista de nomes únicos: {sorted(df_bruto['Nome_Jogador'].unique().tolist())}")

    except FileNotFoundError as e:
        print(f"Erro ao carregar arquivo: {e}. Certifique-se de que '{ARQUIVO_ENTRADA_PROCESSAMENTO}' está na pasta 'data'.")
        print("Você precisa rodar o 'gerador_dados.py' atualizado antes de rodar este script.")
        return # return para sair da função em caso de erro

    # Converter 'Data' para datetime

    print('\nConvertendo \'Data\' para tipo datetime...')
    df_bruto['Data'] = pd.to_datetime(df_bruto['Data'])

    # Tratar inconsistências de nomes (reconciliação)

    def padronizar_nome(nome, opcoes, limiar=85):
        if pd.isna(nome):
            return None
        
        apelidos_conhecidos = {
            'Ronaldo Fenômeno': 'Ronaldo',
            'Ronaldo Nazário': 'Ronaldo',
            'Ronaldinho': 'Ronaldinho Gaúcho',
            'Luizao': 'Luizão',
            'Denilson': 'Denílson'
        }

        if nome in apelidos_conhecidos:
            return apelidos_conhecidos[nome]
        
        if nome in opcoes:
            return nome

        correspondencia, pontuacao = process.extractOne(nome, opcoes, scorer=fuzz.ratio)
        if pontuacao >= limiar:
            return correspondencia
        return nome

    print('\nPadronizando nomes dos jogadores com fuzzywuzzy...')
    df_bruto['Nome_Padronizado'] = df_bruto['Nome_Jogador'].apply(lambda x: padronizar_nome(x, nomes_oficiais_para_fuzzy))
    print('Padronização concluída com sucesso!')

    print("\nVerificação de nomes após padronização:")
    nomes_unicos_apos_padronizacao = df_bruto['Nome_Padronizado'].unique().tolist()
    print(f"Número de nomes únicos após padronização: {len(nomes_unicos_apos_padronizacao)}")
    print(f"Lista de nomes únicos: {sorted(nomes_unicos_apos_padronizacao)}")

    # Verificar nomes que podem ter mais de uma variação original mapeada para eles ou vice-versa

    nomes_originais_por_padronizado = df_bruto.groupby('Nome_Padronizado')['Nome_Jogador'].nunique()
    nomes_padronizados_com_multiplas_origens = nomes_originais_por_padronizado[nomes_originais_por_padronizado > 1]

    if not nomes_padronizados_com_multiplas_origens.empty:
        print("\nNomes padronizados que resultaram de múltiplas variações originais:")
        for nome_padr, count in nomes_padronizados_com_multiplas_origens.items():
            nomes_originais = df_bruto[df_bruto['Nome_Padronizado'] == nome_padr]['Nome_Jogador'].unique().tolist()
            print(f"  '{nome_padr}' foi mapeado de: {nomes_originais}")
    else:
        print("\nTodos os nomes originais foram mapeados para um único nome padronizado sem conflito aparente.")

    # Ordenar por jogador padronizado e 'Data' para cálculos de janelas móveis

    df_bruto = df_bruto.sort_values(by=['Nome_Padronizado', 'Data']).reset_index(drop=True)

    # Tratar dados ausentes

    print('\nTratando dados faltantes (se houver algum após a geração)...')
    colunas_numericas_para_preencher = [
        'Minutos_Jogados', 'Distancia_Percorrida_(km)', 'Num_Sprints',
        'VO2_Max_Estimado', 'FC_Media_(bpm)',
        'Carga_Aguda', 'Carga_Cronica', 'Relacao_Carga_Aguda_Cronica', # Nomes das colunas ACWR atualizados
        'Dias_Desde_Ultima_Lesao', 'Num_Lesoes_Anteriores'
    ]

    for col in colunas_numericas_para_preencher:
        if col in df_bruto.columns:
            df_bruto[col] = df_bruto.groupby('Posicao')[col].transform(lambda x: x.fillna(x.mean()))
            df_bruto[col] = df_bruto[col].fillna(df_bruto[col].mean())
        else:
            print(f"Aviso: Coluna '{col}' não encontrada no DataFrame, ignorando preenchimento de NaN.")

    if 'Dias_Desde_Ultima_Lesao' in df_bruto.columns:
        df_bruto['Dias_Desde_Ultima_Lesao'] = df_bruto['Dias_Desde_Ultima_Lesao'].fillna(df_bruto['Dias_Desde_Ultima_Lesao'].mean())

    # Garantir tipos de dados para colunas numéricas

    for col in ['Minutos_Jogados', 'Num_Sprints', 'FC_Media_(bpm)']:
        if col in df_bruto.columns:
            df_bruto[col] = df_bruto[col].astype(int)
    for col in ['Distancia_Percorrida_(km)', 'VO2_Max_Estimado', 'Carga_Aguda', 'Carga_Cronica', 'Relacao_Carga_Aguda_Cronica']: # Nomes das colunas ACWR atualizados
        if col in df_bruto.columns:
            df_bruto[col] = df_bruto[col].astype(float)
    if 'Num_Lesoes_Anteriores' in df_bruto.columns:
        df_bruto['Num_Lesoes_Anteriores'] = df_bruto['Num_Lesoes_Anteriores'].astype(int)

    df_bruto['Lesao_Ocorreu'] = df_bruto['Lesao_Ocorreu'].fillna(False).astype(bool)
    df_bruto['Tipo_Lesao'] = df_bruto['Tipo_Lesao'].fillna('Nenhuma_Lesao').astype(str)
    df_bruto['Tempo_Ausencia'] = df_bruto['Tempo_Ausencia'].fillna(0).astype(int)

    print("\nNúmero de valores nulos após tratamento (deve ser 0 ou muito próximo para colunas principais):")
    print(df_bruto.isnull().sum())

    # Implementação de Modelos Estatísticos / Detecção de Anomalias / Previsão de Risco de Lesão

    print('\nIniciando análise de performance e risco de lesão (cálculo de métricas móveis e score de risco)...')

    # Calcular métricas de janela móvel (rolling metrics) para cada jogador

    df_bruto['VO2_Media_7d'] = df_bruto.groupby('Nome_Padronizado')['VO2_Max_Estimado'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )
    df_bruto['Dist_Media_7d'] = df_bruto.groupby('Nome_Padronizado')['Distancia_Percorrida_(km)'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )
    df_bruto['Sprints_Media_7d'] = df_bruto.groupby('Nome_Padronizado')['Num_Sprints'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )

    # Calcular desvio padrão móvel (para detecção de anomalia)

    df_bruto['VO2_DP_7d'] = df_bruto.groupby('Nome_Padronizado')['VO2_Max_Estimado'].transform(
        lambda x: x.rolling(window=7, min_periods=1).std()
    ).fillna(0)
    df_bruto['Dist_DP_7d'] = df_bruto.groupby('Nome_Padronizado')['Distancia_Percorrida_(km)'].transform(
        lambda x: x.rolling(window=7, min_periods=1).std()
    ).fillna(0)
    df_bruto['Sprints_DP_7d'] = df_bruto.groupby('Nome_Padronizado')['Num_Sprints'].transform(
        lambda x: x.rolling(window=7, min_periods=1).std()
    ).fillna(0)

    # Detecção de Anomalias (usando 2 desvios padrão - regra de 95% de confiança)

    df_bruto['Alerta_VO2_Anomalo'] = (df_bruto['VO2_Max_Estimado'] < (df_bruto['VO2_Media_7d'] - 2 * df_bruto['VO2_DP_7d'])) | \
                                   (df_bruto['VO2_Max_Estimado'] > (df_bruto['VO2_Media_7d'] + 2 * df_bruto['VO2_DP_7d']))

    df_bruto['Alerta_Dist_Anomala'] = (df_bruto['Distancia_Percorrida_(km)'] > (df_bruto['Dist_Media_7d'] + 2 * df_bruto['Dist_DP_7d']))
    df_bruto['Alerta_Sprints_Anomalos'] = (df_bruto['Num_Sprints'] > (df_bruto['Sprints_Media_7d'] + 2 * df_bruto['Sprints_DP_7d']))

    # Implementar a pontuação de risco de lesão

    df_bruto['Pontuacao_Risco_Lesao'] = 0

    # Adicionar pontos com base nas anomalias detectadas

    df_bruto.loc[df_bruto['Alerta_VO2_Anomalo'], 'Pontuacao_Risco_Lesao'] += 3
    df_bruto.loc[df_bruto['Alerta_Dist_Anomala'], 'Pontuacao_Risco_Lesao'] += 2
    df_bruto.loc[df_bruto['Alerta_Sprints_Anomalos'], 'Pontuacao_Risco_Lesao'] += 2

    # Usar 'Num_Lesoes_Anteriores' do gerador_dados

    df_bruto.loc[df_bruto['Num_Lesoes_Anteriores'] > 0, 'Pontuacao_Risco_Lesao'] += 1

    # --- ALTERAÇÃO PRINCIPAL AQUI PARA O processador_dados.py ---

    # Mapear pontuação para categorias de risco (AJUSTADO PARA INCLUIR 1 EM 'BAIXO')

    def mapear_pontuacao_risco(pontuacao):
        if pontuacao >= 6: # Para pontuações 6 ou mais
            return 'Muito Alto'
        elif pontuacao >= 4: # Para pontuações 4 ou 5
            return 'Alto'
        elif pontuacao >= 2: # Para pontuações 2 ou 3
            return 'Moderado'
        elif pontuacao >=0 and pontuacao <= 1: # Para pontuações 0 ou 1
            return 'Baixo'
        else: # Caso haja algum score negativo ou inválido
            return 'Dado Inválido'

    df_bruto['Categoria_Risco_Lesao'] = df_bruto['Pontuacao_Risco_Lesao'].apply(mapear_pontuacao_risco)

    print("\nAnálise de risco de lesão concluída.")
    print("Linhas com as novas métricas de risco (últimas 10):")
    print(df_bruto[['Data', 'Nome_Padronizado', 'Pontuacao_Risco_Lesao', 'Categoria_Risco_Lesao']].tail(10))

    # --- DEBUG: Dados Finais Antes de Salvar (PROCESSADOR DE DADOS) ---

    print("\n--- DEBUG: Dados Finais Antes de Salvar (PROCESSADOR DE DADOS) ---")
    print("Amostra de 'Pontuacao_Risco_Lesao' e 'Categoria_Risco_Lesao':")

    # Mostrar todas as linhas onde Pontuacao_Risco_Lesao é 0 ou 1

    dados_risco_debug = df_bruto[df_bruto['Pontuacao_Risco_Lesao'].isin([0, 1])]
    if not dados_risco_debug.empty:
        print(dados_risco_debug[['Data', 'Nome_Padronizado', 'Pontuacao_Risco_Lesao', 'Categoria_Risco_Lesao']].head(20))
    else:
        print("Nenhum registro com Pontuacao_Risco_Lesao 0 ou 1 encontrado nesta amostra.")

    print("\nTipos de dados das colunas de risco:")
    print(df_bruto[['Pontuacao_Risco_Lesao', 'Categoria_Risco_Lesao']].dtypes)

    print("\nContagem de valores na 'Pontuacao_Risco_Lesao':")
    print(df_bruto['Pontuacao_Risco_Lesao'].value_counts(dropna=False))

    print("\nContagem de valores na 'Categoria_Risco_Lesao':")
    print(df_bruto['Categoria_Risco_Lesao'].value_counts(dropna=False))
    print("\n--- Fim DEBUG: PROCESSADOR DE DADOS ---")

    # Definir o caminho para o arquivo de saída

    ARQUIVO_SAIDA_PROCESSAMENTO = os.path.join(PASTA_DADOS, 'performance_reconciliada_e_analisada.csv')

    # Reordenar colunas e salvar o DataFrame reconciliado e analisado no CSV

    colunas_finais = [
        'Nome_Jogador', 'Nome_Padronizado', 'Posicao', 'Data', 'Tipo_Atividade',
        'Minutos_Jogados', 'Distancia_Percorrida_(km)', 'Num_Sprints',
        'VO2_Max_Estimado', 'FC_Media_(bpm)',
        'Lesao_Ocorreu', 'Tipo_Lesao', 'Tempo_Ausencia',
        'VO2_Media_7d', 'Dist_Media_7d', 'Sprints_Media_7d',
        'VO2_DP_7d', 'Dist_DP_7d', 'Sprints_DP_7d',
        'Alerta_VO2_Anomalo', 'Alerta_Dist_Anomala', 'Alerta_Sprints_Anomalos',
        'Pontuacao_Risco_Lesao', 'Categoria_Risco_Lesao',
        'Num_Lesoes_Anteriores', 
        'Carga_Aguda', 'Carga_Cronica', 'Relacao_Carga_Aguda_Cronica', 'Dias_Desde_Ultima_Lesao', # Nomes das colunas ACWR atualizados
        'Fonte'
    ]

    colunas_existentes_para_salvar = [col for col in colunas_finais if col in df_bruto.columns]
    df_bruto[colunas_existentes_para_salvar].to_csv(ARQUIVO_SAIDA_PROCESSAMENTO, index=False)
    print(f"\nDataFrame processado salvo em CSV: {ARQUIVO_SAIDA_PROCESSAMENTO}")

    # Salvar no banco de dados SQLite

    # Usar if_exists='replace' para sobrescrever a tabela existente com os dados processados
    
    print(f"\nSalvando DataFrame no banco de dados SQLite: {ARQUIVO_DB} na tabela '{NOME_TABELA}'...")
    df_bruto[colunas_existentes_para_salvar].to_sql(NOME_TABELA, engine, if_exists='replace', index=False)
    print("Dados salvos no banco de dados com sucesso.")

    print("\nDistribuição de Tipos de Atividade no DataFrame final:")
    print(df_bruto['Tipo_Atividade'].value_counts())
    print("\n--- Etapa 2 Concluída ---")
    
# --- Bloco de execução para permitir que o script rode sozinho ---

if __name__ == "__main__":
    executar_processamento_dados()