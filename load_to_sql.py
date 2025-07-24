import pandas as pd
from sqlalchemy import create_engine
import os

# --- Configurações ---
DATA_FOLDER = 'data'
PROCESSED_CSV_FILE = os.path.join(DATA_FOLDER, 'performance_reconciliada_e_analisada.csv')
DB_FILE = os.path.join(DATA_FOLDER, 'performance_data.db')
TABLE_NAME = 'performance_atletas'

def load_processed_data_to_sql():
    # Cria a pasta 'data' se não existir
    os.makedirs(DATA_FOLDER, exist_ok=True)

    try:
        # Verifica se o arquivo CSV processado existe
        if not os.path.exists(PROCESSED_CSV_FILE):
            print(f"Erro: Arquivo '{PROCESSED_CSV_FILE}' não encontrado.")
            print("Por favor, execute 'data_processor.py' primeiro para gerar os dados processados.")
            return

        # Carrega o CSV processado
        df = pd.read_csv(PROCESSED_CSV_FILE)
        print(f"Dados carregados do CSV processado com sucesso. Total de {len(df)} registros.")

        # Converte a coluna 'Data' para datetime para garantir o tipo correto no DB
        # O processador já faz isso, mas é bom garantir aqui também
        df['Data'] = pd.to_datetime(df['Data'])
        # A coluna 'Data_Ultima_Lesao' não foi incluída no seu gerador/processador.
        # Se ela for adicionada futuramente, trate-a aqui. Por enquanto, pode causar erro se não existir.
        # Com base no seu data_generator, não há uma coluna 'Data_Ultima_Lesao' explícita no DataFrame gerado.
        # A informação de Dias_Desde_Ultima_Lesao é um número de dias, não uma data em si.
        # Portanto, esta linha abaixo pode ser removida ou comentada se essa coluna não existir.
        # df['Data_Ultima_Lesao'] = pd.to_datetime(df['Data_Ultima_Lesao'], errors='coerce')


        # Cria a engine de conexão com o SQLite
        engine = create_engine(f'sqlite:///{DB_FILE}')

        # Salva o DataFrame no banco de dados SQLite
        # if_exists='replace' irá substituir a tabela existente (útil para desenvolvimento)
        df.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)

        print(f"Dados salvos com sucesso no banco de dados SQLite: {DB_FILE}, tabela: {TABLE_NAME}")
        # Opcional: imprimir nomes únicos após carregamento no DB para depuração
        df_from_db = pd.read_sql_table(TABLE_NAME, engine)
        print(f"Verificação: {len(df_from_db['Nome_Padronizado'].unique())} nomes únicos no DB.")

    except Exception as e:
        print(f"Erro ao carregar dados para o banco de dados: {e}")

if __name__ == '__main__':
    load_processed_data_to_sql()