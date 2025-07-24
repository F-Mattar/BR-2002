import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

# --- Configurações ---
DATA_FOLDER = 'data'
PROCESSED_CSV_FILE = os.path.join(DATA_FOLDER, 'performance_reconciliada_e_analisada.csv')
FINAL_CSV_FILE = os.path.join(DATA_FOLDER, 'performance_final_para_db.csv')
MODEL_FILE = os.path.join(DATA_FOLDER, 'modelo_previsao_lesao.pkl')
TRAIN_MODEL = True # Alterne para False após treinar o modelo uma vez

def run_analysis_and_prediction():
    """
    Carrega os dados processados, treina um modelo de ML para prever lesões
    e adiciona as previsões ao DataFrame.
    """
    print("Iniciando a análise e a previsão de lesões...")

    try:
        df = pd.read_csv(PROCESSED_CSV_FILE)
        print(f"Dados processados carregados com sucesso. Total de {len(df)} registros.")
    except FileNotFoundError:
        print(f"Erro: Arquivo '{PROCESSED_CSV_FILE}' não encontrado.")
        print("Por favor, execute 'data_processor.py' primeiro.")
        return

    # --- Pré-processamento e Feature Engineering para o modelo de ML ---
    df['Data'] = pd.to_datetime(df['Data'])
    
    # Preenche NaNs na coluna 'Num_Lesoes_Anteriores'
    df['Num_Lesoes_Anteriores'] = df['Num_Lesoes_Anteriores'].fillna(0)

    # --- TRATAMENTO CRÍTICO PARA A VARIÁVEL-ALVO (VERSÃO MELHORADA) ---
    # Passo 1: Primeiro, preenche NaNs com a string 'Nao'.
    df['Lesao_Ocorreu'] = df['Lesao_Ocorreu'].fillna('Nao')
    
    # Passo 2: Mapeia as strings para inteiros.
    df['Lesao_Ocorreu'] = df['Lesao_Ocorreu'].map({'Sim': 1, 'Nao': 0})
    
    # Passo 3: Preenche quaisquer NaNs que tenham sido introduzidos pelo map (se houver valores não esperados na coluna)
    # com 0. Esta etapa é a correção final para o seu erro atual.
    df['Lesao_Ocorreu'] = df['Lesao_Ocorreu'].fillna(0)

    # --- Definição de Features e Target ---
    features = [
        'Acute_Workload', 'Chronic_Workload', 'ACWR',
        'Num_Sprints', 'Distancia_Percorrida_(km)',
        'Dias_Desde_Ultima_Lesao', 'Num_Lesoes_Anteriores',
        'VO2_Media_7d', 'Dist_Media_7d', 'Sprints_Media_7d'
    ]
    target = 'Lesao_Ocorreu'

    # --- TRATAMENTO DOS VALORES FALTANTES (NaNs) nas features ---
    print("\nVerificando e tratando valores faltantes (NaNs) nas features...")
    for col in features:
        if df[col].isnull().any():
            print(f"  > Preenchendo NaNs na coluna '{col}' com 0.")
            df[col] = df[col].fillna(0)
    
    # Verificação para garantir que o DataFrame não está vazio.
    if df.empty:
        print("\nERRO: Após tratar os valores faltantes, o DataFrame ainda está vazio.")
        print("Verifique os dados de entrada. A execução será interrompida.")
        return

    print(f"DataFrame pronto para o treino. Total de {len(df)} registros restantes.")

    # --- Treinamento e Previsão ---
    if TRAIN_MODEL:
        print("\nTreinando um novo modelo de Machine Learning...")
        X = df[features]
        y = df[target]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        print("\nRelatório de Classificação do Modelo:")
        print(classification_report(y_test, y_pred, zero_division=0))

        joblib.dump(model, MODEL_FILE)
        print(f"Modelo treinado salvo em: {MODEL_FILE}")
    else:
        print("\nCarregando modelo de ML previamente treinado...")
        try:
            model = joblib.load(MODEL_FILE)
            print("Modelo carregado com sucesso.")
        except FileNotFoundError:
            print(f"Erro: Arquivo do modelo '{MODEL_FILE}' não encontrado. Por favor, execute o script com TRAIN_MODEL = True para treiná-lo primeiro.")
            return

    df['Risco_Lesao_ML'] = model.predict(df[features])
    df['Risco_Lesao_ML'] = df['Risco_Lesao_ML'].astype(int)

    df.to_csv(FINAL_CSV_FILE, index=False)
    print(f"\nAnálise concluída. DataFrame final (com previsões de ML) salvo em: {FINAL_CSV_FILE}")

# --- Ponto de entrada do script ---
if __name__ == "__main__":
    run_analysis_and_prediction()