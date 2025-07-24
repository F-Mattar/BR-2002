import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_and_save_data():
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

    start_date = datetime(2002, 1, 1)
    end_date = datetime(2002, 6, 29)

    performance_data = []
    GAME_DAY_PROB = 0.25
    current_date = start_date

    player_daily_workload = {jogador['Nome']: [] for _, jogador in df_jogadores.iterrows()}
    player_last_injury_date = {jogador['Nome']: None for _, jogador in df_jogadores.iterrows()}
    player_total_injuries = {jogador['Nome']: 0 for _, jogador in df_jogadores.iterrows()}

    def calculate_workload(history, days):
        relevant_history = [h for h in history if h['Data'] >= current_date - timedelta(days=days)]
        return sum(h['Distancia_Percorrida_(km)'] for h in relevant_history if not np.isnan(h['Distancia_Percorrida_(km)']))

    while current_date <= end_date:
        is_game_day = np.random.rand() < GAME_DAY_PROB

        if is_game_day:
            players_in_game = df_jogadores.sample(n=np.random.randint(11, 15)).index.tolist()
            
            for index, jogador in df_jogadores.iterrows():
                nome_original = jogador['Nome']
                nome_display = nome_original

                minutos_jogados = 0
                dist_mean, sprints_mean, vo2_mean, fc_mean = 0, 0, 0, 0
                source_choice = 'Preparador_Fisico'

                if index in players_in_game:
                    minutos_jogados = np.random.choice([45, 90], p=[0.3, 0.7])
                    source_choice = 'Dados_de_Jogos'

                    if jogador['Posicao'] == 'Goleiro':
                        dist_mean = np.random.uniform(3, 6)
                        sprints_mean = np.random.randint(2, 7)
                        vo2_mean = np.random.uniform(48, 52)
                        fc_mean = np.random.uniform(135, 150)
                    elif jogador['Posicao'] == 'Zagueiro':
                        dist_mean = np.random.uniform(8, 11)
                        sprints_mean = np.random.randint(15, 30)
                        vo2_mean = np.random.uniform(53, 58)
                        fc_mean = np.random.uniform(150, 165)
                    elif jogador['Posicao'] in ['Lateral-direito', 'Lateral-esquerdo', 'Volante', 'Meio-campista']:
                        dist_mean = np.random.uniform(10, 14)
                        sprints_mean = np.random.randint(25, 45)
                        vo2_mean = np.random.uniform(55, 62)
                        fc_mean = np.random.uniform(160, 180)
                    else: # Atacante
                        dist_mean = np.random.uniform(9, 13)
                        sprints_mean = np.random.randint(30, 50)
                        vo2_mean = np.random.uniform(54, 60)
                        fc_mean = np.random.uniform(155, 175)
                else:
                    if np.random.rand() < 0.6:
                        dist_mean = np.random.uniform(1, 3)
                        sprints_mean = np.random.randint(0, 2)
                        vo2_mean = np.random.uniform(40, 45)
                        fc_mean = np.random.uniform(100, 120)
                        source_choice = np.random.choice(['Preparador_Fisico', 'Departamento_Medico'], p=[0.8, 0.2])
                    else:
                        dist_percorrida = 0
                        num_sprints = 0
                        vo2_max_estimado = np.random.uniform(35, 45)
                        fc_media = np.random.uniform(90, 110)
                        minutos_jogados = 0
                        source_choice = 'Nenhum_Registro'
                
                if source_choice == 'Nenhum_Registro':
                    continue

                dist_percorrida = np.random.normal(dist_mean, 1.5)
                num_sprints = np.random.normal(sprints_mean, 5)
                vo2_max_estimado = np.random.normal(vo2_mean, 3)
                fc_media = np.random.normal(fc_mean, 8)

                if np.random.rand() < 0.05: dist_percorrida = np.nan
                if np.random.rand() < 0.03: vo2_max_estimado = np.nan
                if np.random.rand() < 0.02: minutos_jogados = np.nan
                
                if nome_original == 'Ronaldo' and np.random.rand() < 0.1: nome_display = 'Ronaldo Fenômeno'
                elif nome_original == 'Ronaldinho Gaúcho' and np.random.rand() < 0.1: nome_display = 'Ronaldinho'

                lesao_data = {
                    'Lesao_Ocorreu': False,
                    'Tipo_Lesao': 'Nenhuma_Lesao',
                    'Tempo_Ausencia': 0
                }

                if minutos_jogados > 0:
                    if (vo2_max_estimado < (vo2_mean - 5) and np.random.rand() < 0.3):
                        if np.random.rand() < 0.6:
                            lesao_data['Lesao_Ocorreu'] = True
                            lesao_data['Tipo_Lesao'] = 'Fadiga_Excessiva/Risco_Lesao'
                            lesao_data['Tempo_Ausencia'] = int(np.random.normal(5, 2))
                        else:
                            lesao_data['Lesao_Ocorreu'] = True
                            lesao_data['Tipo_Lesao'] = 'Lesao_Muscular_Leve'
                            lesao_data['Tempo_Ausencia'] = int(np.random.normal(10, 3))
                    elif (dist_percorrida > (dist_mean + 5) and np.random.rand() < 0.2):
                        if np.random.rand() < 0.7:
                            lesao_data['Lesao_Ocorreu'] = True
                            lesao_data['Tipo_Lesao'] = 'Lesao_Muscular_Leve'
                            lesao_data['Tempo_Ausencia'] = int(np.random.normal(10, 3))
                        else:
                            lesao_data['Lesao_Ocorreu'] = True
                            lesao_data['Tipo_Lesao'] = 'Lesao_Articular'
                            lesao_data['Tempo_Ausencia'] = int(np.random.normal(30, 7))
                
                if not lesao_data['Lesao_Ocorreu'] and np.random.rand() < 0.005:
                    lesao_data['Lesao_Ocorreu'] = True
                    lesao_data['Tipo_Lesao'] = np.random.choice(['Contusao', 'Entorse_Leve', 'Lesao_Muscular_Leve'])
                    lesao_data['Tempo_Ausencia'] = int(np.random.normal(2, 1))

                if lesao_data['Lesao_Ocorreu']:
                    player_last_injury_date[nome_original] = current_date
                    player_total_injuries[nome_original] += 1
                
                acute_workload = calculate_workload(player_daily_workload[nome_original], 7)
                chronic_workload = calculate_workload(player_daily_workload[nome_original], 28)
                acwr = acute_workload / chronic_workload if chronic_workload > 0 else 0
                
                days_since_last_injury = (current_date - player_last_injury_date[nome_original]).days if player_last_injury_date[nome_original] else np.nan

                record = {
                    'Nome_Jogador': nome_display,
                    'Posicao': jogador['Posicao'],
                    'Data': current_date.strftime('%Y-%m-%d'),
                    'Minutos_Jogados': minutos_jogados,
                    'Distancia_Percorrida_(km)': max(0, round(dist_percorrida, 2)) if not np.isnan(dist_percorrida) else np.nan,
                    'Num_Sprints': max(0, int(num_sprints)) if not np.isnan(num_sprints) else np.nan,
                    'VO2_Max_Estimado': max(30, round(vo2_max_estimado, 2)) if not np.isnan(vo2_max_estimado) else np.nan,
                    'FC_Media_(bpm)': max(80, int(fc_media)) if not np.isnan(fc_media) else np.nan,
                    'Lesao_Ocorreu': lesao_data['Lesao_Ocorreu'],
                    'Tipo_Lesao': lesao_data['Tipo_Lesao'],
                    'Tempo_Ausencia': lesao_data['Tempo_Ausencia'],
                    'Fonte': source_choice,
                    'Tipo_Atividade': 'Jogo' if is_game_day else 'Treino',
                    'Acute_Workload': round(acute_workload, 2),
                    'Chronic_Workload': round(chronic_workload, 2),
                    'ACWR': round(acwr, 2),
                    'Dias_Desde_Ultima_Lesao': days_since_last_injury,
                    'Num_Lesoes_Anteriores': player_total_injuries[nome_original]
                }
                performance_data.append(record)
                
                player_daily_workload[nome_original].append({
                    'Data': current_date,
                    'Distancia_Percorrida_(km)': record['Distancia_Percorrida_(km)']
                })

        else: # Dia de Treino
            for index, jogador in df_jogadores.iterrows():
                if np.random.rand() < 0.8:
                    nome_original = jogador['Nome']
                    nome_display = nome_original

                    if jogador['Posicao'] == 'Goleiro':
                        dist_mean = np.random.uniform(2, 5)
                        sprints_mean = np.random.randint(0, 5)
                        vo2_mean = np.random.uniform(40, 48)
                        fc_mean = np.random.uniform(120, 140)
                    elif jogador['Posicao'] == 'Zagueiro':
                        dist_mean = np.random.uniform(6, 9)
                        sprints_mean = np.random.randint(8, 20)
                        vo2_mean = np.random.uniform(48, 53)
                        fc_mean = np.random.uniform(140, 155)
                    elif jogador['Posicao'] in ['Lateral-direito', 'Lateral-esquerdo', 'Volante', 'Meio-campista']:
                        dist_mean = np.random.uniform(8, 11)
                        sprints_mean = np.random.randint(20, 35)
                        vo2_mean = np.random.uniform(50, 58)
                        fc_mean = np.random.uniform(150, 170)
                    else: # Atacante
                        dist_mean = np.random.uniform(7, 10)
                        sprints_mean = np.random.randint(25, 40)
                        vo2_mean = np.random.uniform(48, 55)
                        fc_mean = np.random.uniform(145, 165)
                    
                    dist_percorrida = np.random.normal(dist_mean, 1.0)
                    num_sprints = np.random.normal(sprints_mean, 3)
                    vo2_max_estimado = np.random.normal(vo2_mean, 2)
                    fc_media = np.random.normal(fc_mean, 5)

                    minutos_jogados = np.random.choice([0, 60, 90, 120], p=[0.1, 0.3, 0.4, 0.2])
                    if minutos_jogados == 0:
                        dist_percorrida = 0
                        num_sprints = 0
                        vo2_max_estimado = np.random.uniform(35, 45)
                        fc_media = np.random.uniform(90, 110)

                    if np.random.rand() < 0.05: dist_percorrida = np.nan
                    if np.random.rand() < 0.03: vo2_max_estimado = np.nan
                    if np.random.rand() < 0.02: minutos_jogados = np.nan
                    
                    if nome_original == 'Ronaldo' and np.random.rand() < 0.1: nome_display = 'Ronaldo Fenômeno'
                    elif nome_original == 'Ronaldinho Gaúcho' and np.random.rand() < 0.1: nome_display = 'Ronaldinho'

                    lesao_data = {
                        'Lesao_Ocorreu': False,
                        'Tipo_Lesao': 'Nenhuma_Lesao',
                        'Tempo_Ausencia': 0
                    }

                    if minutos_jogados > 0:
                        if (vo2_max_estimado < (vo2_mean - 4) and np.random.rand() < 0.25):
                            if np.random.rand() < 0.7:
                                lesao_data['Lesao_Ocorreu'] = True
                                lesao_data['Tipo_Lesao'] = 'Fadiga_Excessiva/Risco_Lesao'
                                lesao_data['Tempo_Ausencia'] = int(np.random.normal(4, 1))
                            else:
                                lesao_data['Lesao_Ocorreu'] = True
                                lesao_data['Tipo_Lesao'] = 'Lesao_Muscular_Leve'
                                lesao_data['Tempo_Ausencia'] = int(np.random.normal(8, 2))
                        elif (dist_percorrida > (dist_mean + 4) and np.random.rand() < 0.15):
                            if np.random.rand() < 0.8:
                                lesao_data['Lesao_Ocorreu'] = True
                                lesao_data['Tipo_Lesao'] = 'Lesao_Muscular_Leve'
                                lesao_data['Tempo_Ausencia'] = int(np.random.normal(8, 2))
                            else:
                                lesao_data['Lesao_Ocorreu'] = True
                                lesao_data['Tipo_Lesao'] = 'Lesao_Articular'
                                lesao_data['Tempo_Ausencia'] = int(np.random.normal(20, 5))
                    
                    if not lesao_data['Lesao_Ocorreu'] and np.random.rand() < 0.005:
                        lesao_data['Lesao_Ocorreu'] = True
                        lesao_data['Tipo_Lesao'] = np.random.choice(['Contusao', 'Entorse_Leve', 'Lesao_Muscular_Leve'])
                        lesao_data['Tempo_Ausencia'] = int(np.random.normal(2, 1))

                    if lesao_data['Lesao_Ocorreu']:
                        player_last_injury_date[nome_original] = current_date
                        player_total_injuries[nome_original] += 1
                    
                    acute_workload = calculate_workload(player_daily_workload[nome_original], 7)
                    chronic_workload = calculate_workload(player_daily_workload[nome_original], 28)
                    acwr = acute_workload / chronic_workload if chronic_workload > 0 else 0
                    
                    days_since_last_injury = (current_date - player_last_injury_date[nome_original]).days if player_last_injury_date[nome_original] else np.nan

                    record = {
                        'Nome_Jogador': nome_display,
                        'Posicao': jogador['Posicao'],
                        'Data': current_date.strftime('%Y-%m-%d'),
                        'Minutos_Jogados': minutos_jogados,
                        'Distancia_Percorrida_(km)': max(0, round(dist_percorrida, 2)) if not np.isnan(dist_percorrida) else np.nan,
                        'Num_Sprints': max(0, int(num_sprints)) if not np.isnan(num_sprints) else np.nan,
                        'VO2_Max_Estimado': max(30, round(vo2_max_estimado, 2)) if not np.isnan(vo2_max_estimado) else np.nan,
                        'FC_Media_(bpm)': max(80, int(fc_media)) if not np.isnan(fc_media) else np.nan,
                        'Lesao_Ocorreu': lesao_data['Lesao_Ocorreu'],
                        'Tipo_Lesao': lesao_data['Tipo_Lesao'],
                        'Tempo_Ausencia': lesao_data['Tempo_Ausencia'],
                        'Fonte': np.random.choice(['Preparador_Fisico', 'Departamento_Medico'], p=[0.9, 0.1]),
                        'Tipo_Atividade': 'Treino',
                        'Acute_Workload': round(acute_workload, 2),
                        'Chronic_Workload': round(chronic_workload, 2),
                        'ACWR': round(acwr, 2),
                        'Dias_Desde_Ultima_Lesao': days_since_last_injury,
                        'Num_Lesoes_Anteriores': player_total_injuries[nome_original]
                    }
                    performance_data.append(record)

                    player_daily_workload[nome_original].append({
                        'Data': current_date,
                        'Distancia_Percorrida_(km)': record['Distancia_Percorrida_(km)']
                    })
        
        current_date += timedelta(days=1)

    df_performance = pd.DataFrame(performance_data)
    os.makedirs('data', exist_ok=True)
    df_performance.to_csv('data/performance_completa_gerada.csv', index=False)

    print("Novos dados fictícios com ACWR, Histórico de Lesões e outras métricas gerados e salvos em 'data/performance_completa_gerada.csv'")

if __name__ == '__main__':
    generate_and_save_data()