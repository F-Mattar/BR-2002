import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def gerar_e_salvar_dados():
    """
    Gera dados fictícios de performance e risco de lesão para a Seleção do Brasil de 2002
    e salva o resultado em um arquivo CSV.
    """
    # Lista de jogadores da Seleção do Brasil de 2002
    jogadores = [
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

    df_jogadores = pd.DataFrame(jogadores)

    data_inicio = datetime(2002, 1, 1)
    data_fim = datetime(2002, 6, 29)

    dados_performance = []
    PROB_DIA_DE_JOGO = 0.25
    data_atual = data_inicio

    carga_trabalho_diaria_jogador = {jogador['Nome']: [] for _, jogador in df_jogadores.iterrows()}
    ultima_data_lesao_jogador = {jogador['Nome']: None for _, jogador in df_jogadores.iterrows()}
    total_lesoes_jogador = {jogador['Nome']: 0 for _, jogador in df_jogadores.iterrows()}

    def calcular_carga_trabalho(historico, dias):
        historico_relevante = [h for h in historico if h['Data'] >= data_atual - timedelta(days=dias)]
        return sum(h['Distancia_Percorrida_(km)'] for h in historico_relevante if not np.isnan(h['Distancia_Percorrida_(km)']))

    while data_atual <= data_fim:
        dia_de_jogo = np.random.rand() < PROB_DIA_DE_JOGO

        if dia_de_jogo:
            jogadores_no_jogo = df_jogadores.sample(n=np.random.randint(11, 15)).index.tolist()
            
            for index, jogador in df_jogadores.iterrows():
                nome_original = jogador['Nome']
                nome_exibicao = nome_original

                minutos_jogados = 0
                media_dist, media_sprints, media_vo2, media_fc = 0, 0, 0, 0
                escolha_fonte = 'Preparador_Fisico'

                if index in jogadores_no_jogo:
                    minutos_jogados = np.random.choice([45, 90], p=[0.3, 0.7])
                    escolha_fonte = 'Dados_de_Jogos'

                    if jogador['Posicao'] == 'Goleiro':
                        media_dist = np.random.uniform(3, 6)
                        media_sprints = np.random.randint(2, 7)
                        media_vo2 = np.random.uniform(48, 52)
                        media_fc = np.random.uniform(135, 150)
                    elif jogador['Posicao'] == 'Zagueiro':
                        media_dist = np.random.uniform(8, 11)
                        media_sprints = np.random.randint(15, 30)
                        media_vo2 = np.random.uniform(53, 58)
                        media_fc = np.random.uniform(150, 165)
                    elif jogador['Posicao'] in ['Lateral-direito', 'Lateral-esquerdo', 'Volante', 'Meio-campista']:
                        media_dist = np.random.uniform(10, 14)
                        media_sprints = np.random.randint(25, 45)
                        media_vo2 = np.random.uniform(55, 62)
                        media_fc = np.random.uniform(160, 180)
                    else: # Atacante
                        media_dist = np.random.uniform(9, 13)
                        media_sprints = np.random.randint(30, 50)
                        media_vo2 = np.random.uniform(54, 60)
                        media_fc = np.random.uniform(155, 175)
                else:
                    if np.random.rand() < 0.6:
                        media_dist = np.random.uniform(1, 3)
                        media_sprints = np.random.randint(0, 2)
                        media_vo2 = np.random.uniform(40, 45)
                        media_fc = np.random.uniform(100, 120)
                        escolha_fonte = np.random.choice(['Preparador_Fisico', 'Departamento_Medico'], p=[0.8, 0.2])
                    else:
                        distancia_percorrida = 0
                        num_sprints = 0
                        vo2_max_estimado = np.random.uniform(35, 45)
                        fc_media = np.random.uniform(90, 110)
                        minutos_jogados = 0
                        escolha_fonte = 'Nenhum_Registro'
                
                if escolha_fonte == 'Nenhum_Registro':
                    continue

                distancia_percorrida = np.random.normal(media_dist, 1.5)
                num_sprints = np.random.normal(media_sprints, 5)
                vo2_max_estimado = np.random.normal(media_vo2, 3)
                fc_media = np.random.normal(media_fc, 8)

                if np.random.rand() < 0.05: distancia_percorrida = np.nan
                if np.random.rand() < 0.03: vo2_max_estimado = np.nan
                if np.random.rand() < 0.02: minutos_jogados = np.nan
                
                if nome_original == 'Ronaldo' and np.random.rand() < 0.1: nome_exibicao = 'Ronaldo Fenômeno'
                elif nome_original == 'Ronaldinho Gaúcho' and np.random.rand() < 0.1: nome_exibicao = 'Ronaldinho'

                dados_lesao = {
                    'Lesao_Ocorreu': False,
                    'Tipo_Lesao': 'Nenhuma_Lesao',
                    'Tempo_Ausencia': 0
                }

                if minutos_jogados > 0:
                    if (vo2_max_estimado < (media_vo2 - 5) and np.random.rand() < 0.3):
                        if np.random.rand() < 0.6:
                            dados_lesao['Lesao_Ocorreu'] = True
                            dados_lesao['Tipo_Lesao'] = 'Fadiga_Excessiva/Risco_Lesao'
                            dados_lesao['Tempo_Ausencia'] = int(np.random.normal(5, 2))
                        else:
                            dados_lesao['Lesao_Ocorreu'] = True
                            dados_lesao['Tipo_Lesao'] = 'Lesao_Muscular_Leve'
                            dados_lesao['Tempo_Ausencia'] = int(np.random.normal(10, 3))
                    elif (distancia_percorrida > (media_dist + 5) and np.random.rand() < 0.2):
                        if np.random.rand() < 0.7:
                            dados_lesao['Lesao_Ocorreu'] = True
                            dados_lesao['Tipo_Lesao'] = 'Lesao_Muscular_Leve'
                            dados_lesao['Tempo_Ausencia'] = int(np.random.normal(10, 3))
                        else:
                            dados_lesao['Lesao_Ocorreu'] = True
                            dados_lesao['Tipo_Lesao'] = 'Lesao_Articular'
                            dados_lesao['Tempo_Ausencia'] = int(np.random.normal(30, 7))
                
                if not dados_lesao['Lesao_Ocorreu'] and np.random.rand() < 0.005:
                    dados_lesao['Lesao_Ocorreu'] = True
                    dados_lesao['Tipo_Lesao'] = np.random.choice(['Contusao', 'Entorse_Leve', 'Lesao_Muscular_Leve'])
                    dados_lesao['Tempo_Ausencia'] = int(np.random.normal(2, 1))

                if dados_lesao['Lesao_Ocorreu']:
                    ultima_data_lesao_jogador[nome_original] = data_atual
                    total_lesoes_jogador[nome_original] += 1
                
                carga_aguda = calcular_carga_trabalho(carga_trabalho_diaria_jogador[nome_original], 7)
                carga_cronica = calcular_carga_trabalho(carga_trabalho_diaria_jogador[nome_original], 28)
                relacao_carga_aguda_cronica = carga_aguda / carga_cronica if carga_cronica > 0 else 0
                
                dias_desde_ultima_lesao = (data_atual - ultima_data_lesao_jogador[nome_original]).days if ultima_data_lesao_jogador[nome_original] else np.nan

                registro = {
                    'Nome_Jogador': nome_exibicao,
                    'Posicao': jogador['Posicao'],
                    'Data': data_atual.strftime('%Y-%m-%d'),
                    'Minutos_Jogados': minutos_jogados,
                    'Distancia_Percorrida_(km)': max(0, round(distancia_percorrida, 2)) if not np.isnan(distancia_percorrida) else np.nan,
                    'Num_Sprints': max(0, int(num_sprints)) if not np.isnan(num_sprints) else np.nan,
                    'VO2_Max_Estimado': max(30, round(vo2_max_estimado, 2)) if not np.isnan(vo2_max_estimado) else np.nan,
                    'FC_Media_(bpm)': max(80, int(fc_media)) if not np.isnan(fc_media) else np.nan,
                    'Lesao_Ocorreu': dados_lesao['Lesao_Ocorreu'],
                    'Tipo_Lesao': dados_lesao['Tipo_Lesao'],
                    'Tempo_Ausencia': dados_lesao['Tempo_Ausencia'],
                    'Fonte': escolha_fonte,
                    'Tipo_Atividade': 'Jogo' if dia_de_jogo else 'Treino',
                    'Carga_Aguda': round(carga_aguda, 2),
                    'Carga_Cronica': round(carga_cronica, 2),
                    'Relacao_Carga_Aguda_Cronica': round(relacao_carga_aguda_cronica, 2),
                    'Dias_Desde_Ultima_Lesao': dias_desde_ultima_lesao,
                    'Num_Lesoes_Anteriores': total_lesoes_jogador[nome_original]
                }
                dados_performance.append(registro)
                
                carga_trabalho_diaria_jogador[nome_original].append({
                    'Data': data_atual,
                    'Distancia_Percorrida_(km)': registro['Distancia_Percorrida_(km)']
                })

        else: # Dia de Treino
            for index, jogador in df_jogadores.iterrows():
                if np.random.rand() < 0.8: # Nem todos os jogadores treinam todos os dias
                    nome_original = jogador['Nome']
                    nome_exibicao = nome_original

                    if jogador['Posicao'] == 'Goleiro':
                        media_dist = np.random.uniform(2, 5)
                        media_sprints = np.random.randint(0, 5)
                        media_vo2 = np.random.uniform(40, 48)
                        media_fc = np.random.uniform(120, 140)
                    elif jogador['Posicao'] == 'Zagueiro':
                        media_dist = np.random.uniform(6, 9)
                        media_sprints = np.random.randint(8, 20)
                        media_vo2 = np.random.uniform(48, 53)
                        media_fc = np.random.uniform(140, 155)
                    elif jogador['Posicao'] in ['Lateral-direito', 'Lateral-esquerdo', 'Volante', 'Meio-campista']:
                        media_dist = np.random.uniform(8, 11)
                        media_sprints = np.random.randint(20, 35)
                        media_vo2 = np.random.uniform(50, 58)
                        media_fc = np.random.uniform(150, 170)
                    else: # Atacante
                        media_dist = np.random.uniform(7, 10)
                        media_sprints = np.random.randint(25, 40)
                        media_vo2 = np.random.uniform(48, 55)
                        media_fc = np.random.uniform(145, 165)
                    
                    distancia_percorrida = np.random.normal(media_dist, 1.0)
                    num_sprints = np.random.normal(media_sprints, 3)
                    vo2_max_estimado = np.random.normal(media_vo2, 2)
                    fc_media = np.random.normal(media_fc, 5)

                    minutos_jogados = np.random.choice([0, 60, 90, 120], p=[0.1, 0.3, 0.4, 0.2])
                    if minutos_jogados == 0:
                        distancia_percorrida = 0
                        num_sprints = 0
                        vo2_max_estimado = np.random.uniform(35, 45)
                        fc_media = np.random.uniform(90, 110)

                    if np.random.rand() < 0.05: distancia_percorrida = np.nan
                    if np.random.rand() < 0.03: vo2_max_estimado = np.nan
                    if np.random.rand() < 0.02: minutos_jogados = np.nan
                    
                    if nome_original == 'Ronaldo' and np.random.rand() < 0.1: nome_exibicao = 'Ronaldo Fenômeno'
                    elif nome_original == 'Ronaldinho Gaúcho' and np.random.rand() < 0.1: nome_exibicao = 'Ronaldinho'

                    dados_lesao = {
                        'Lesao_Ocorreu': False,
                        'Tipo_Lesao': 'Nenhuma_Lesao',
                        'Tempo_Ausencia': 0
                    }

                    if minutos_jogados > 0:
                        if (vo2_max_estimado < (media_vo2 - 4) and np.random.rand() < 0.25):
                            if np.random.rand() < 0.7:
                                dados_lesao['Lesao_Ocorreu'] = True
                                dados_lesao['Tipo_Lesao'] = 'Fadiga_Excessiva/Risco_Lesao'
                                dados_lesao['Tempo_Ausencia'] = int(np.random.normal(4, 1))
                            else:
                                dados_lesao['Lesao_Ocorreu'] = True
                                dados_lesao['Tipo_Lesao'] = 'Lesao_Muscular_Leve'
                                dados_lesao['Tempo_Ausencia'] = int(np.random.normal(8, 2))
                        elif (distancia_percorrida > (media_dist + 4) and np.random.rand() < 0.15):
                            if np.random.rand() < 0.8:
                                dados_lesao['Lesao_Ocorreu'] = True
                                dados_lesao['Tipo_Lesao'] = 'Lesao_Muscular_Leve'
                                dados_lesao['Tempo_Ausencia'] = int(np.random.normal(8, 2))
                            else:
                                dados_lesao['Lesao_Ocorreu'] = True
                                dados_lesao['Tipo_Lesao'] = 'Lesao_Articular'
                                dados_lesao['Tempo_Ausencia'] = int(np.random.normal(20, 5))
                    
                    if not dados_lesao['Lesao_Ocorreu'] and np.random.rand() < 0.005:
                        dados_lesao['Lesao_Ocorreu'] = True
                        dados_lesao['Tipo_Lesao'] = np.random.choice(['Contusao', 'Entorse_Leve', 'Lesao_Muscular_Leve'])
                        dados_lesao['Tempo_Ausencia'] = int(np.random.normal(2, 1))

                    if dados_lesao['Lesao_Ocorreu']:
                        ultima_data_lesao_jogador[nome_original] = data_atual
                        total_lesoes_jogador[nome_original] += 1
                    
                    carga_aguda = calcular_carga_trabalho(carga_trabalho_diaria_jogador[nome_original], 7)
                    carga_cronica = calcular_carga_trabalho(carga_trabalho_diaria_jogador[nome_original], 28)
                    relacao_carga_aguda_cronica = carga_aguda / carga_cronica if carga_cronica > 0 else 0
                    
                    dias_desde_ultima_lesao = (data_atual - ultima_data_lesao_jogador[nome_original]).days if ultima_data_lesao_jogador[nome_original] else np.nan

                    registro = {
                        'Nome_Jogador': nome_exibicao,
                        'Posicao': jogador['Posicao'],
                        'Data': data_atual.strftime('%Y-%m-%d'),
                        'Minutos_Jogados': minutos_jogados,
                        'Distancia_Percorrida_(km)': max(0, round(distancia_percorrida, 2)) if not np.isnan(distancia_percorrida) else np.nan,
                        'Num_Sprints': max(0, int(num_sprints)) if not np.isnan(num_sprints) else np.nan,
                        'VO2_Max_Estimado': max(30, round(vo2_max_estimado, 2)) if not np.isnan(vo2_max_estimado) else np.nan,
                        'FC_Media_(bpm)': max(80, int(fc_media)) if not np.isnan(fc_media) else np.nan,
                        'Lesao_Ocorreu': dados_lesao['Lesao_Ocorreu'],
                        'Tipo_Lesao': dados_lesao['Tipo_Lesao'],
                        'Tempo_Ausencia': dados_lesao['Tempo_Ausencia'],
                        'Fonte': np.random.choice(['Preparador_Fisico', 'Departamento_Medico'], p=[0.9, 0.1]),
                        'Tipo_Atividade': 'Treino',
                        'Carga_Aguda': round(carga_aguda, 2),
                        'Carga_Cronica': round(carga_cronica, 2),
                        'Relacao_Carga_Aguda_Cronica': round(relacao_carga_aguda_cronica, 2),
                        'Dias_Desde_Ultima_Lesao': dias_desde_ultima_lesao,
                        'Num_Lesoes_Anteriores': total_lesoes_jogador[nome_original]
                    }
                    dados_performance.append(registro)

                    carga_trabalho_diaria_jogador[nome_original].append({
                        'Data': data_atual,
                        'Distancia_Percorrida_(km)': registro['Distancia_Percorrida_(km)']
                    })
        
        data_atual += timedelta(days=1)

    df_performance = pd.DataFrame(dados_performance)
    os.makedirs('data', exist_ok=True)
    df_performance.to_csv('data/performance_completa_gerada.csv', index=False)

    print("Novos dados fictícios com Carga Aguda Crônica (CACR), Histórico de Lesões e outras métricas gerados e salvos em 'data/performance_completa_gerada.csv'")

if __name__ == '__main__':
    gerar_e_salvar_dados()