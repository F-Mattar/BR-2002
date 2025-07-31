import dashboard_app
import data_generator
import data_processor
import analysis_script
import load_to_sql
import os

if __name__ == '__main__':
    print("=====================================================")
    print("=             Iniciando Pipeline de Dados           =")
    print("=====================================================")

    # Garante que a pasta 'data' existe para evitar erros
    
    if not os.path.exists('data'):
        os.makedirs('data')

    # Etapa 1: Gerar os dados fictícios
    print("\n--- Etapa 1: Gerando dados fictícios ---")
    data_generator.gerar_e_salvar_dados()
    print("--- Etapa 1 Concluída ---")

    # Etapa 2: Processar, reconciliar e analisar os dados

    print("\n--- Etapa 2: Processando e reconciliando dados ---")
    data_processor.executar_processamento_dados()
    print("--- Etapa 2 Concluída ---")

    # Etapa 3: Analisar e treinar modelo de ML

    print("\n--- Etapa 3: Analisando e treinando modelo de ML ---")
    analysis_script.executar_analise_e_previsao()
    print("--- Etapa 3 Concluída ---")

    # Etapa 4: Carregar os dados processados e analisados para o SQL

    print("\n--- Etapa 4: Carregando dados para o banco de dados ---")
    load_to_sql.carregar_dados_processados_para_sql()
    print("--- Etapa 4 Concluída ---")

    print("\n=====================================================")
    print("=             Pipeline Concluída!                   =")
    print("=        Iniciando o Dashboard Interativo...        =")
    print("=====================================================")

    # Etapa 5: Iniciar o dashboard

    # Esta função irá bloquear a execução e manter o servidor rodando

    dashboard_app.executar_app_dashboard()