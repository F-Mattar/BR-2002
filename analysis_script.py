import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

# --- Configurações ---

PASTA_DADOS = 'data'
ARQUIVO_CSV_PROCESSADO = os.path.join(PASTA_DADOS, 'performance_reconciliada_e_analisada.csv')
ARQUIVO_CSV_FINAL = os.path.join(PASTA_DADOS, 'performance_final_para_db.csv')
ARQUIVO_MODELO = os.path.join(PASTA_DADOS, 'modelo_previsao_lesao.pkl')
TREINAR_MODELO = True

def executar_analise_e_previsao():
    """
    Carrega os dados processados, treina um modelo de ML para prever lesões
    e adiciona as previsões ao DataFrame.
    """
    print("Iniciando a análise e a previsão de lesões...")

    try:
        df = pd.read_csv(ARQUIVO_CSV_PROCESSADO)
        print(f"Dados processados carregados com sucesso. Total de {len(df)} registros.")
    except FileNotFoundError:
        print(f"Erro: Arquivo '{ARQUIVO_CSV_PROCESSADO}' não encontrado.")
        print("Por favor, execute 'processador_dados.py' primeiro.")
        return

    # --- Pré-processamento e Engenharia de Features para o modelo de ML ---

    df['Data'] = pd.to_datetime(df['Data'])
    
    # Preenche NaNs na coluna 'Num_Lesoes_Anteriores'

    df['Num_Lesoes_Anteriores'] = df['Num_Lesoes_Anteriores'].fillna(0)

    # --- TRATAMENTO CRÍTICO PARA A VARIÁVEL-ALVO ---

    df['Lesao_Ocorreu'] = df['Lesao_Ocorreu'].astype(int)
    
    # --- Definição de Features e Variável-Alvo ---

    features = [
        'Carga_Aguda', 'Carga_Cronica', 'Relacao_Carga_Aguda_Cronica',
        'Num_Sprints', 'Distancia_Percorrida_(km)',
        'Dias_Desde_Ultima_Lesao', 'Num_Lesoes_Anteriores',
        'VO2_Media_7d', 'Dist_Media_7d', 'Sprints_Media_7d'
    ]
    variavel_alvo = 'Lesao_Ocorreu'

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

    if TREINAR_MODELO:
        print("\nTreinando um novo modelo de Machine Learning...")
        X = df[features]
        y = df[variavel_alvo]
        
        X_treino, X_teste, y_treino, y_teste = train_test_split(X, y, test_size=0.2, random_state=42)

        modelo = RandomForestClassifier(n_estimators=100, random_state=42)
        modelo.fit(X_treino, y_treino)

        y_previsao = modelo.predict(X_teste)
        print("\nRelatório de Classificação do Modelo:")
        print(classification_report(y_teste, y_previsao, zero_division=0))

        joblib.dump(modelo, ARQUIVO_MODELO)
        print(f"Modelo treinado salvo em: {ARQUIVO_MODELO}")
    else:
        print("\nCarregando modelo de ML previamente treinado...")
        try:
            modelo = joblib.load(ARQUIVO_MODELO)
            print("Modelo carregado com sucesso.")
        except FileNotFoundError:
            print(f"Erro: Arquivo do modelo '{ARQUIVO_MODELO}' não encontrado. Por favor, execute o script com TREINAR_MODELO = True para treiná-lo primeiro.")
            return

    # Realiza a previsão com o modelo treinado (ou carregado) no DataFrame completo

    df['Risco_Lesao_ML'] = modelo.predict(df[features])
    df['Risco_Lesao_ML'] = df['Risco_Lesao_ML'].astype(int)

    df.to_csv(ARQUIVO_CSV_FINAL, index=False)
    print(f"\nAnálise concluída. DataFrame final (com previsões de ML) salvo em: {ARQUIVO_CSV_FINAL}")

# --- Ponto de entrada do script ---

if __name__ == "__main__":
    executar_analise_e_previsao()