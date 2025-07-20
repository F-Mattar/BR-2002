import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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

# Converter o dicionário para DataFrame Pandas

df_jogadores = pd.DataFrame(jogadores)

# Considerar que os dados foram colhidos num determinado intervalo de tempo

start_date = datetime(2002,3,1) # Início de preparação para a Copa de 2002
end_date = datetime(2002,6,29) # Véspera da final da Copa de 2002

performance_data = []

for index, jogador in df_jogadores.iterrows():
    current_date = start_date
    while current_date <= end_date:
        if np.random.rand() < 0.8: # 80% de chance de haver registro dos dados no dia

            # Os dados serão valores médios característicos para cada posição durante treino ou jogo

            if jogador['Posicao'] in ['Goleiro','Zagueiro']:
                dist_mean = 8 # distância percorrida em km
                sprints_mean = 15 # número de sprints
                vo2_mean = 50 # VO2 máximo estimado em mL/kg/min
                fc_mean = 150 # frequência cardíaca estimada em bpm
            elif jogador['Posicao'] in ['Lateral-Direito','Lateral-Esquerdo','Volante','Meio-Camppista']:
                dist_mean = 10
                sprints_mean = 25
                vo2_mean = 55
                fc_mean = 160
            else: #Atacante
                dist_mean = 9
                sprints_mean = 30
                vo2_mean = 52
                fc_mean = 155
            
            # Vamos adicionar ruído aos dados para simular variabiliade usando a função numpy.random.normal(loc,scale,size), que gera números a partir de uma distribuição normal

            dist_percorrida = np.random.normal(dist_mean,1.5)
            num_sprints = np.random.normal(sprints_mean,5)
            vo2_max_estimado = np.random.normal(vo2_mean,3)
            fc_media = np.random.normal(fc_mean,8)
            minutos_jogados = np.random.choice([0,45,90],p=[0.3,0.2,0.5])

            # Simular alguns dados faltantes aleatoriamente (para reconciliação)

            if np.random.rand() < 0.05: # 5% de chance de um dado faltar
                dist_percorrida = np.nan
            if np.random.rand() < 0.03:
                vo2_max_estimado = np.nan
            if np.random.rand() < 0.02:
                minutos_jogados = np.nan
            
            # Simular algumas inconsistências em nomes (para reconciliação)
            
            nome = jogador['Nome']
            if jogador['Nome'] == 'Ronaldo' and np.random.rand() < 0.1:
                nome = 'Ronaldo Fenômeno'
            elif jogador['Nome'] == 'Ronaldinho Gaúcho' and np.random.rand() < 0.1:
                nome = 'Ronaldinho'

            # Queda de VO2 máximo (maior fadiga) ou sobrecarga (aumento significativo na distância percorrida) pode gerar lesões

            lesao_data = {
                'Lesao_Ocorreu': False,
                'Tipo_Lesao': None,
                'Tempo_Ausencia': 0 # Tempo de ausência (em dias) para descanso/monitoramento
            }

            # Queda significativa no VO2 Máximo (indicador de fadiga/risco)

            if (vo2_max_estimado < (vo2_mean - 5) and np.random.rand() < 0.3):
                if np.random.rand() < 0.6: # 60% de chance de ser uma Fadiga Excessiva/Risco
                    lesao_data['Lesao_Ocorreu'] = True
                    lesao_data['Tipo_Lesao'] = 'Fadiga_Excessiva/Risco_Lesao' # Não é uma lesão grave, mas é um alerta
                    lesao_data['Tempo_Ausencia'] = int(np.random.normal(5, 2)) # 3-7 dias de 'descanso/monitoramento'
                else: # 40% de chance de ser uma Lesão Muscular Leve
                    lesao_data['Lesao_Ocorreu'] = True
                    lesao_data['Tipo_Lesao'] = 'Lesao_Muscular_Leve'
                    lesao_data['Tempo_Ausencia'] = int(np.random.normal(10, 3)) # 7-13 dias de 'descanso/monitoramento'

            # Distância percorrida excessiva (indicador de sobrecarga)

            elif (dist_percorrida > (dist_mean + 5) and np.random.rand() < 0.2):
                if np.random.rand() < 0.7: # 70% de chance de ser uma Lesão Muscular Leve por sobrecarga
                    lesao_data['Lesao_Ocorreu'] = True
                    lesao_data['Tipo_Lesao'] = 'Lesao_Muscular_Leve'
                    lesao_data['Tempo_Ausencia'] = int(np.random.normal(10, 3)) # 7-13 dias
                else: # 30% de chance de ser uma Lesão Articular por sobrecarga
                    lesao_data['Lesao_Ocorreu'] = True
                    lesao_data['Tipo_Lesao'] = 'Lesao_Articular'
                    lesao_data['Tempo_Ausencia'] = int(np.random.normal(30, 7)) # 23-37 dias 

            # Adicionar uma chance pequena de lesão aleatória diária, independente das métricas

            elif not lesao_data['Lesao_Ocorreu'] and np.random.rand() < 0.005: # Apenas se não houver lesão anterior
                lesao_data['Lesao_Ocorreu'] = True
                lesao_data['Tipo_Lesao'] = np.random.choice(['Contusao', 'Entorse_Leve', 'Lesao_Muscular_Leve'])
                lesao_data['Tempo_Ausencia'] = int(np.random.normal(2, 1)) # 1-3 dias de ausência

            performance_data.append({
                'Nome_Jogador': nome,
                'Posicao': jogador['Posicao'],
                'Data': current_date.strftime('%Y-%m-%d'), # Padrão ISO 8601
                'Minutos_Jogados': minutos_jogados,
                'Distancia_Percorrida_(km)': max(0, round(dist_percorrida, 2)),
                'Num_Sprints': max(0, int(num_sprints)),
                'VO2_Max_Estimado': max(30, round(vo2_max_estimado, 2)),
                'FC_Media_(bpm)': max(80, int(fc_media)),
                'Lesao_Ocorreu': lesao_data['Lesao_Ocorreu'],
                'Tipo_Lesao': lesao_data['Tipo_Lesao'],
                'Tempo_Ausencia': lesao_data['Tempo_Ausencia'], 
                'Fonte': np.random.choice(['Preparador_Fisico', 'Departamento_Medico', 'Dados_de_Jogos'])
                })
        current_date += timedelta(days=np.random.randint(2,8)) # Registros são feitos entre 2 e 7 dias, que corresponde a um intervalo aproximado entre jogos ou treinos

df_performance = pd.DataFrame(performance_data)

# Simular fontes distintas dos dados colhidos

df_performance_prep = df_performance[df_performance['Fonte'] == 'Preparador_Fisico']
df_performance_med = df_performance[df_performance['Fonte'] == 'Departamento_Medico']
df_performance_jogo = df_performance[df_performance['Fonte'] == 'Dados_de_Jogos']

df_performance_prep.to_csv('data/preparador_fisico.csv', index=False) # Não é necessário evidenciar o índice
df_performance_med.to_csv('data/departamento_medico.csv', index=False)
df_performance_jogo.to_csv('data/dados_de_jogos.csv', index=False)

print("Dados fictícios gerados e salvos em 'data/'")