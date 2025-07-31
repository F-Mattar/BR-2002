import pandas as pd
from sqlalchemy import create_engine
import os

# --- Configurações ---
PASTA_DADOS = 'data'
ARQUIVO_CSV_PROCESSADO = os.path.join(PASTA_DADOS, 'performance_reconciliada_e_analisada.csv')
ARQUIVO_DB = os.path.join(PASTA_DADOS, 'dados_performance.db')
NOME_TABELA = 'performance_atletas'

def carregar_dados_processados_para_sql():
    """
    Carrega dados de performance processados de um arquivo CSV para um banco de dados SQLite.
    """
    os.makedirs(PASTA_DADOS, exist_ok=True)

    try:
        if not os.path.exists(ARQUIVO_CSV_PROCESSADO):
            print(f"Erro: Arquivo '{ARQUIVO_CSV_PROCESSADO}' não encontrado.")
            print("Por favor, execute 'processador_dados.py' primeiro para gerar os dados processados.")
            return

        df = pd.read_csv(ARQUIVO_CSV_PROCESSADO)
        print(f"Dados carregados do CSV processado com sucesso. Total de {len(df)} registros.")

        # Observação: A conversão para datetime pode ser redundante se o script anterior

        df['Data'] = pd.to_datetime(df['Data'])

        engine = create_engine(f'sqlite:///{ARQUIVO_DB}')
        
        # Salva o DataFrame no banco de dados SQLite
        
        df.to_sql(NOME_TABELA, engine, if_exists='replace', index=False)

        print(f"Dados salvos com sucesso no banco de dados SQLite: {ARQUIVO_DB}, tabela: {NOME_TABELA}")

    except Exception as e:
        print(f"Erro ao carregar dados para o banco de dados: {e}")

if __name__ == '__main__':
    carregar_dados_processados_para_sql()