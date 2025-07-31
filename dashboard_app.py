import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from sqlalchemy import create_engine
import os
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# --- Funções de Formatação ---

def formatar_nome_coluna(nome_coluna):
    """
    Formata nomes de colunas para exibição amigável no dashboard.
    """
    substituicoes = {
        'Max': 'Máximo',
        'Media': 'Média',
        'Num': 'Número de',
        'Distancia': 'Distância',
        'Frequencia': 'Frequência',
        'Pontuacao': 'Pontuação',
        'Lesao': 'Lesão',
        'Fadiga_Excessiva/Risco_Lesao': 'Fadiga Excessiva / Risco de Lesão',
        'Lesao_Muscular_Leve': 'Lesão Muscular Leve',
        'Entorse_Leve': 'Entorse Leve',
        'Contusao': 'Contusão',
        'Nenhuma_Lesao': 'Nenhuma Lesão',
        'Tipo_Atividade': 'Tipo de Atividade',
        'Carga_Aguda': 'Carga Aguda de Treino',
        'Carga_Cronica': 'Carga Crônica de Treino',
        'Relacao_Carga_Aguda_Cronica': 'Razão Carga Aguda/Crônica (RACR)',
        'Dias_Desde_Ultima_Lesao': 'Dias Desde Última Lesão',
        'Num_Lesoes_Anteriores': 'Número de Lesões Anteriores',
        'Probabilidade_Lesao': 'Probabilidade de Lesão',
        'Tipo_Lesao': 'Tipo de Lesão',
        'Tempo_Ausencia': 'Tempo de Ausência',
        'Tipo_Lesao_Formatado': 'Tipo de Lesão',
        'Risco_Lesao_ML': 'Risco de Lesão (ML)'
    }
    
    if nome_coluna in substituicoes:
        return substituicoes[nome_coluna]
    
    nome_formatado = nome_coluna.replace('_', ' ')
    
    for parte_antiga, parte_nova in substituicoes.items():
        if parte_antiga not in ['Tipo_Lesao', 'Tempo_Ausencia', 'Tipo_Lesao_Formatado', 'Carga_Aguda', 'Carga_Cronica', 'Relacao_Carga_Aguda_Cronica', 'Risco_Lesao_ML']:
            nome_formatado = nome_formatado.replace(parte_antiga.replace('_', ' '), parte_nova)
            
    return nome_formatado

def mapear_categoria_risco_para_texto(valor_categoria_risco):
    """
    Mapeia o valor da categoria de risco para um texto.
    """
    if pd.isna(valor_categoria_risco):
        return 'N/A'
    return valor_categoria_risco

# --- Configurações do Banco de Dados ---

PASTA_DADOS = 'data'
ARQUIVO_DB = os.path.join(PASTA_DADOS, 'dados_performance.db')
NOME_TABELA = 'performance_atletas'
engine = create_engine(f'sqlite:///{ARQUIVO_DB}')

# --- Carregar os Dados Iniciais ---

def carregar_dados_do_sql():
    """
    Carrega os dados de performance do banco de dados SQLite.
    """
    try:
        df = pd.read_sql_table(NOME_TABELA, engine)
        df['Data'] = pd.to_datetime(df['Data'])
        
        # Garante que 'Lesao_Ocorreu' é booleano (para filtros e lógica)

        df['Lesao_Ocorreu'] = df['Lesao_Ocorreu'].astype(bool)

        # Formatação das colunas para exibição

        df['Tipo_Lesao_Formatado'] = df['Tipo_Lesao'].apply(formatar_nome_coluna) 
        df['Categoria_Risco_Lesao_Formatado'] = df['Categoria_Risco_Lesao'].apply(mapear_categoria_risco_para_texto) 
        df['Tipo_Atividade_Formatado'] = df['Tipo_Atividade'].apply(formatar_nome_coluna)

        print(f"Dados carregados do SQL com sucesso. Total de {len(df)} registros.")
        print(f"Colunas disponíveis em df_global: {df.columns.tolist()}")
        print(f"Nomes de jogadores únicos no DB: {sorted(df['Nome_Padronizado'].unique().tolist())}")
        return df
    except Exception as e:
        print(f"Erro ao carregar dados do banco de dados: {e}")
        return pd.DataFrame()

# --- Encapsulando a Lógica do Dashboard em uma Função ---

def executar_app_dashboard():
    global df_global
    df_global = carregar_dados_do_sql()
    nomes_jogadores = sorted(df_global['Nome_Padronizado'].unique()) if not df_global.empty else []
    
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.Img(src=app.get_asset_url('cbf_2002_logo.png'),
                             style={'height': '80px', 'marginRight': '15px', 'verticalAlign': 'middle'}),
                    html.Span("Dashboard de Performance e Risco de Lesão", 
                              className="h1 text-light text-center d-inline-block align-middle"),
                    html.Span(" Seleção Brasileira 2002", 
                              className="text-white text-center d-inline-block align-middle ms-3 fs-4")
                ], className="d-flex align-items-center justify-content-center flex-wrap"),
                width=12, className="text-center my-4" 
            )
        ], className="g-0 align-items-center justify-content-center"),

        dbc.Row(dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("Visualizar Dados do Jogador", className="card-title text-center text-primary")),
                dbc.CardBody(dcc.Dropdown(
                    id='dropdown-jogador',
                    options=[{'label': nome, 'value': nome} for nome in nomes_jogadores],
                    placeholder="Selecione um jogador para análise individual...",
                    multi=False,
                    clearable=True
                ))
            ], className="mb-4 shadow border-0"),
            width=12, lg=6
        ), justify="center"),

        dbc.Row(dbc.Col(html.Div(id='container-saida-jogador'), width=12)),

        dbc.Row(dbc.Col(html.Hr(style={'borderColor': 'white', 'borderWidth': '3px'}), className="my-5")),

        dbc.Row(dbc.Col(html.H2("Comparação de Jogadores", className="text-light text-center mb-4"))),

        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(html.H4("Selecione Jogador 1", className="card-title text-center text-primary")),
                    dbc.CardBody(dcc.Dropdown(
                        id='dropdown-jogador-1',
                        options=[{'label': nome, 'value': nome} for nome in nomes_jogadores],
                        placeholder="Selecione o primeiro jogador...",
                        multi=False,
                        clearable=True
                    ))
                ], className="mb-4 shadow border-0"),
                width=12, lg=6
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(html.H4("Selecione Jogador 2", className="card-title text-center text-primary")),
                    dbc.CardBody(dcc.Dropdown(
                        id='dropdown-jogador-2',
                        options=[{'label': nome, 'value': nome} for nome in nomes_jogadores],
                        placeholder="Selecione o segundo jogador...",
                        multi=False,
                        clearable=True
                    ))
                ], className="mb-4 shadow border-0"),
                width=12, lg=6
            )
        ], justify="center"),

        dbc.Row(dbc.Col(html.Div(id='container-saida-comparacao'), width=12))

    ], fluid=True, style={'backgroundColor': '#0066CC', 'padding': '3rem'})

    # --- Callbacks ---

    @app.callback(
        Output('container-saida-jogador', 'children'),
        Input('dropdown-jogador', 'value')
    )
    def atualizar_info_jogador(jogador_selecionado):
        if jogador_selecionado is None:
            return dbc.Alert("Selecione um jogador no menu acima para visualizar os detalhes de performance e risco de lesão.", color="info", className="text-center my-5")

        jogador_df = df_global[df_global['Nome_Padronizado'] == jogador_selecionado].copy()

        if jogador_df.empty:
            return dbc.Alert(f"Dados não encontrados para o jogador: {jogador_selecionado}", color="warning", className="text-center my-5")

        dados_mais_recentes = jogador_df.sort_values(by='Data', ascending=False).iloc[0]

        # Mapeamento de cores de risco

        mapa_cores_risco = {'Baixo': 'success', 'Moderado': 'warning', 'Alto': 'danger', 'Muito Alto': 'dark', 'N/A': 'secondary'} 

        texto_categoria_risco = dados_mais_recentes.get('Categoria_Risco_Lesao_Formatado', 'N/A') 
        cor_badge_risco = mapa_cores_risco.get(texto_categoria_risco, 'secondary')

        dias_desde_lesao = dados_mais_recentes.get('Dias_Desde_Ultima_Lesao')
        data_registro_atual = dados_mais_recentes.get('Data') 

        ultima_data_lesao_jogador = jogador_df[jogador_df['Lesao_Ocorreu'] == True]['Data'].max()

        texto_dias = "N/A"
        if pd.notna(dias_desde_lesao) and dias_desde_lesao is not None:
            if pd.notna(ultima_data_lesao_jogador) and pd.notna(data_registro_atual):
                texto_dias = (
                    f"Última lesão em {ultima_data_lesao_jogador.strftime('%Y-%m-%d')}, "
                    f"{int(dias_desde_lesao)} dias sem lesionar "
                    f"(Data de referência: {data_registro_atual.strftime('%Y-%m-%d')})"
                )
            else:
                texto_dias = f"{int(dias_desde_lesao)} dias sem lesionar (Data de referência: {data_registro_atual.strftime('%Y-%m-%d') if pd.notna(data_registro_atual) else 'N/A'})"
        elif jogador_df['Lesao_Ocorreu'].sum() == 0:
            texto_dias = "Nenhuma lesão registrada"
        else:
            texto_dias = "Informação de dias sem lesão indisponível"

        cartao_resumo = dbc.Card([
            dbc.CardHeader(html.H2(f"Perfil Detalhado: {jogador_selecionado}", className="card-title text-center text-primary")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(html.P(f"Posição: {dados_mais_recentes.get('Posicao', 'N/A')}", className="lead mb-0 text-dark")),
                    dbc.Col(html.P([f"Pontuação de Risco de Lesão: {dados_mais_recentes.get('Pontuacao_Risco_Lesao', 'N/A')} (", dbc.Badge(texto_categoria_risco, color=cor_badge_risco, className="me-1 fs-6"), ")"], className="lead mb-0 text-dark")),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col(html.P(texto_dias, className="lead mb-0 text-dark")),
                    dbc.Col(html.P(f"Número de Lesões Anteriores: {dados_mais_recentes.get('Num_Lesoes_Anteriores', 'N/A')}", className="lead mb-0 text-dark"))
                ])
            ])
        ], className="mb-4 shadow p-2 border-0 bg-light")

        # Gráfico de Tendência de Risco de Lesão

        df_tendencia_risco = jogador_df.dropna(subset=['Pontuacao_Risco_Lesao']).sort_values(by='Data')
        if not df_tendencia_risco.empty:
            fig_risco = px.line(df_tendencia_risco, x='Data', y='Pontuacao_Risco_Lesao', title=f'Pontuação de Risco de Lesão', labels={'Pontuacao_Risco_Lesao': 'Pontuação de Risco'}, template='plotly_white', color_discrete_sequence=['red'])
            fig_risco.update_traces(mode='lines+markers')
            fig_risco.update_layout(hovermode="x unified")
        else:
            fig_risco = go.Figure().update_layout(title="Dados de Pontuação de Risco Insuficientes")

        # Calcula a Probabilidade de Lesão se não existir (baseado na pontuação de risco)

        if 'Probabilidade_Lesao' not in jogador_df.columns:
            jogador_df['Probabilidade_Lesao'] = jogador_df['Pontuacao_Risco_Lesao'].apply(lambda x: min(0.95, max(0.05, 0.05 + x * 0.1)) if pd.notna(x) else np.nan)
        
        df_tendencia_prob_lesao = jogador_df.dropna(subset=['Probabilidade_Lesao']).sort_values(by='Data')
        if not df_tendencia_prob_lesao.empty:
            fig_prob_lesao = px.line(df_tendencia_prob_lesao, x='Data', y='Probabilidade_Lesao', title=f'Probabilidade de Lesão', labels={'Probabilidade_Lesao': 'Probabilidade de Lesão (%)'}, line_shape='spline', template='plotly_white', color_discrete_sequence=['orange'])
            fig_prob_lesao.update_traces(mode='lines+markers', hovertemplate='Data: %{x}<br>Probabilidade: %{y:.2%}')
            fig_prob_lesao.update_layout(hovermode="x unified", yaxis_tickformat=".0%")
            fig_prob_lesao.add_hline(y=0.5, line_dash="dot", line_color="red", annotation_text="Limiar de Alerta (50%)", annotation_position="bottom right")
        else:
            fig_prob_lesao = go.Figure().update_layout(title="Dados de Probabilidade de Lesão Insuficientes")

        # Gráficos de Métricas de Performance

        metricas_performance = ['Distancia_Percorrida_(km)', 'Num_Sprints', 'VO2_Max_Estimado', 'FC_Media_(bpm)']
        cores_brasil = ['#009739', '#FEDD00', '#002776', '#a8a8a8'] 
        componentes_graficos_performance = []

        for i, metric in enumerate(metricas_performance):
            if metric in jogador_df.columns and not jogador_df[metric].dropna().empty:
                nome_metrica_formatado = formatar_nome_coluna(metric)
                fig_perf = px.line(jogador_df.sort_values(by='Data'), x='Data', y=metric, title=f'{nome_metrica_formatado}', labels={'Data': 'Data', metric: nome_metrica_formatado}, template='plotly_white', color_discrete_sequence=[cores_brasil[i % len(cores_brasil)]])
                fig_perf.update_traces(mode='lines+markers')
                fig_perf.update_layout(hovermode="x unified")
                componentes_graficos_performance.append(dbc.Col(dbc.Card(dcc.Graph(figure=fig_perf), className="h-100"), md=6, className="mb-4 shadow"))
            else:
                componentes_graficos_performance.append(dbc.Col(dbc.Card(dbc.CardBody(html.P(f"Dados insuficientes para {formatar_nome_coluna(metric)}.", className="text-center text-muted m-auto"))), md=6, className="mb-4 shadow d-flex align-items-center justify-content-center"))

        # Histórico de Lesões (Tabela)

        df_historico_lesoes = jogador_df[jogador_df['Lesao_Ocorreu'] == True].sort_values(by='Data', ascending=False).copy()
        if 'Data' in df_historico_lesoes.columns:
            df_historico_lesoes['Data'] = df_historico_lesoes['Data'].dt.strftime('%Y-%m-%d')

        if not df_historico_lesoes.empty:
            config_colunas = []
            for col_id in ['Data', 'Tipo_Lesao_Formatado', 'Tempo_Ausencia']:
                if col_id in df_historico_lesoes.columns:
                    def_col = {"id": col_id, "name": formatar_nome_coluna(col_id)}
                    config_colunas.append(def_col)

            componente_tabela_lesao = dbc.Card([
                dbc.CardHeader(html.H3("Histórico de Lesões", className="card-title text-center", style={'color': 'black'})), 
                dbc.CardBody(dash_table.DataTable(
                    id='tabela-lesao-jogador',
                    columns=config_colunas,
                    data=df_historico_lesoes[['Data', 'Tipo_Lesao_Formatado', 'Tempo_Ausencia']].to_dict('records'),
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={'backgroundColor': '#0066CC', 'fontWeight': 'bold', 'color': 'white'},
                    style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}]
                ))
            ], className="mb-4 shadow border-0 bg-light")
        else:
            componente_tabela_lesao = dbc.Card([
                dbc.CardHeader(html.H3("Histórico de Lesões", className="card-title text-center", style={'color': 'black'})),
                dbc.CardBody(html.P("Nenhuma lesão registrada para este jogador.", className="text-center text-muted m-auto text-dark"))
            ], className="mb-4 shadow border-0 bg-light d-flex align-items-center justify-content-center")

        return html.Div([
            cartao_resumo,
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_risco), className="h-100"), md=6, className="mb-4 shadow"),
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_prob_lesao), className="h-100"), md=6, className="mb-4 shadow"),
            ], className="g-4"),
            html.H3("Métricas de Performance", className="text-center my-4 text-light"),
            dbc.Row(componentes_graficos_performance, className="g-4"),
            componente_tabela_lesao
        ], className="mt-4")

    @app.callback(
        Output('container-saida-comparacao', 'children'),
        [Input('dropdown-jogador-1', 'value'),
         Input('dropdown-jogador-2', 'value')]
    )
    def atualizar_info_comparacao(jogador_selecionado_1, jogador_selecionado_2):
        if not jogador_selecionado_1 and not jogador_selecionado_2:
            return dbc.Alert("Selecione dois jogadores para comparar suas performances e riscos de lesão.", color="info", className="text-center my-5")
        if not jogador_selecionado_1 or not jogador_selecionado_2:
            return dbc.Alert("Selecione ambos os jogadores para iniciar a comparação.", color="warning", className="text-center my-5")
        if jogador_selecionado_1 == jogador_selecionado_2:
            return dbc.Alert("Por favor, selecione dois jogadores diferentes para comparação.", color="danger", className="text-center my-5")

        jogador_df_1 = df_global[df_global['Nome_Padronizado'] == jogador_selecionado_1].copy()
        jogador_df_2 = df_global[df_global['Nome_Padronizado'] == jogador_selecionado_2].copy()

        if jogador_df_1.empty or jogador_df_2.empty:
            return dbc.Alert(f"Dados insuficientes para um ou ambos os jogadores: {jogador_selecionado_1}, {jogador_selecionado_2}", color="warning", className="text-center my-5")

        mapa_cores_risco = {'Baixo': 'success', 'Moderado': 'warning', 'Alto': 'danger', 'Muito Alto': 'dark', 'N/A': 'secondary'}

        def criar_badge_risco(linha_dados):
            texto_categoria_risco = linha_dados.get('Categoria_Risco_Lesao_Formatado', 'N/A')
            cor_badge_risco = mapa_cores_risco.get(texto_categoria_risco, 'secondary')
            return dbc.Badge(texto_categoria_risco, color=cor_badge_risco, className="me-1 fs-6")

        def formatar_dias_texto_comparacao(df_jogador, linha_dados_atual):
            dias_desde_lesao = linha_dados_atual.get('Dias_Desde_Ultima_Lesao')
            data_registro_atual = linha_dados_atual.get('Data')
            ultima_data_lesao = df_jogador[df_jogador['Lesao_Ocorreu'] == True]['Data'].max()

            if pd.notna(dias_desde_lesao) and dias_desde_lesao is not None:
                if pd.notna(ultima_data_lesao) and pd.notna(data_registro_atual):
                    return (
                        f"Última lesão em {ultima_data_lesao.strftime('%Y-%m-%d')}, "
                        f"{int(dias_desde_lesao)} dias sem lesionar "
                        f"(Data de referência: {data_registro_atual.strftime('%Y-%m-%d')})"
                    )
                else:
                    return f"{int(dias_desde_lesao)} dias sem lesionar (Data de referência: {data_registro_atual.strftime('%Y-%m-%d') if pd.notna(data_registro_atual) else 'N/A'})"
            elif df_jogador['Lesao_Ocorreu'].sum() == 0:
                return "Nenhuma lesão registrada"
            else:
                return "Informação de dias sem lesão indisponível"

        dados_mais_recentes_1 = jogador_df_1.sort_values(by='Data', ascending=False).iloc[0]
        dados_mais_recentes_2 = jogador_df_2.sort_values(by='Data', ascending=False).iloc[0]

        texto_dias_1 = formatar_dias_texto_comparacao(jogador_df_1, dados_mais_recentes_1)
        texto_dias_2 = formatar_dias_texto_comparacao(jogador_df_2, dados_mais_recentes_2)

        cartoes_resumo_comparacao = dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H3(jogador_selecionado_1, className="card-title text-center text-primary")),
                dbc.CardBody([
                    html.P(f"Posição: {dados_mais_recentes_1.get('Posicao', 'N/A')}", className="mb-0"),
                    html.P(['Risco: ', criar_badge_risco(dados_mais_recentes_1), f" ({dados_mais_recentes_1.get('Pontuacao_Risco_Lesao', 'N/A')})"], className="mb-0"),
                    html.P(texto_dias_1, className="mb-0"),
                    html.P(f"Lesões Anteriores: {dados_mais_recentes_1.get('Num_Lesoes_Anteriores', 'N/A')}", className="mb-0")
                ])
            ], className="h-100 shadow border-0 bg-light"), md=6),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H3(jogador_selecionado_2, className="card-title text-center text-primary")),
                dbc.CardBody([
                    html.P(f"Posição: {dados_mais_recentes_2.get('Posicao', 'N/A')}", className="mb-0"),
                    html.P(['Risco: ', criar_badge_risco(dados_mais_recentes_2), f" ({dados_mais_recentes_2.get('Pontuacao_Risco_Lesao', 'N/A')})"], className="mb-0"),
                    html.P(texto_dias_2, className="mb-0"),
                    html.P(f"Lesões Anteriores: {dados_mais_recentes_2.get('Num_Lesoes_Anteriores', 'N/A')}", className="mb-0")
                ])
            ], className="h-100 shadow border-0 bg-light"), md=6)
        ], className="g-4 mb-4")

        # Gráfico de comparação de risco e probabilidade

        fig_comparacao_risco = go.Figure()

        # Calcula a Probabilidade de Lesão se não existir (baseado na pontuação de risco)

        if 'Probabilidade_Lesao' not in jogador_df_1.columns:
            jogador_df_1['Probabilidade_Lesao'] = jogador_df_1['Pontuacao_Risco_Lesao'].apply(lambda x: min(0.95, max(0.05, 0.05 + x * 0.1)) if pd.notna(x) else np.nan)
        if 'Probabilidade_Lesao' not in jogador_df_2.columns:
            jogador_df_2['Probabilidade_Lesao'] = jogador_df_2['Pontuacao_Risco_Lesao'].apply(lambda x: min(0.95, max(0.05, 0.05 + x * 0.1)) if pd.notna(x) else np.nan)

        fig_comparacao_risco.add_trace(go.Scatter(x=jogador_df_1['Data'], y=jogador_df_1['Pontuacao_Risco_Lesao'], mode='lines+markers', name=jogador_selecionado_1 + ' (Risco)', line=dict(color='red')))
        fig_comparacao_risco.add_trace(go.Scatter(x=jogador_df_2['Data'], y=jogador_df_2['Pontuacao_Risco_Lesao'], mode='lines+markers', name=jogador_selecionado_2 + ' (Risco)', line=dict(color='blue')))
        fig_comparacao_risco.add_trace(go.Scatter(x=jogador_df_1['Data'], y=jogador_df_1['Probabilidade_Lesao'], mode='lines+markers', name=jogador_selecionado_1 + ' (Probabilidade)', line=dict(color='salmon', dash='dot')))
        fig_comparacao_risco.add_trace(go.Scatter(x=jogador_df_2['Data'], y=jogador_df_2['Probabilidade_Lesao'], mode='lines+markers', name=jogador_selecionado_2 + ' (Probabilidade)', line=dict(color='lightblue', dash='dot')))
        
        fig_comparacao_risco.update_layout(title='Comparação de Risco e Probabilidade de Lesão', xaxis_title='Data', yaxis_title='Valor', template='plotly_white', hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

        # Gráfico de comparação de distância percorrida

        fig_comparacao_distancia = go.Figure()
        fig_comparacao_distancia.add_trace(go.Scatter(x=jogador_df_1['Data'], y=jogador_df_1['Distancia_Percorrida_(km)'], mode='lines+markers', name=jogador_selecionado_1, line=dict(color='#009739')))
        fig_comparacao_distancia.add_trace(go.Scatter(x=jogador_df_2['Data'], y=jogador_df_2['Distancia_Percorrida_(km)'], mode='lines+markers', name=jogador_selecionado_2, line=dict(color='#FEDD00')))
        fig_comparacao_distancia.update_layout(title='Comparação de Distância Percorrida (km)', xaxis_title='Data', yaxis_title='Distância Percorrida (km)', template='plotly_white', hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

        # Tabelas de histórico de lesões comparativas

        df_historico_lesoes_1 = jogador_df_1[jogador_df_1['Lesao_Ocorreu'] == True].sort_values(by='Data', ascending=False).copy()
        if 'Data' in df_historico_lesoes_1.columns:
            df_historico_lesoes_1['Data'] = df_historico_lesoes_1['Data'].dt.strftime('%Y-%m-%d')
        config_colunas_1 = [{"id": col_id, "name": formatar_nome_coluna(col_id)} for col_id in ['Data', 'Tipo_Lesao_Formatado', 'Tempo_Ausencia'] if col_id in df_historico_lesoes_1.columns]
        
        tabela_lesao_1 = dbc.Card([
            dbc.CardHeader(html.H4(f"Histórico de Lesões: {jogador_selecionado_1}", className="card-title text-center", style={'color': 'black'})),
            dbc.CardBody(
                dash_table.DataTable(
                    id='tabela-lesao-jogador-1',
                    columns=config_colunas_1,
                    data=df_historico_lesoes_1[['Data', 'Tipo_Lesao_Formatado', 'Tempo_Ausencia']].to_dict('records'),
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={'backgroundColor': '#0066CC', 'fontWeight': 'bold', 'color': 'white'},
                    style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}]
                ) if not df_historico_lesoes_1.empty else html.P("Nenhuma lesão registrada.", className="text-center text-muted m-auto text-dark")
            )
        ], className="h-100 shadow border-0 bg-light")

        df_historico_lesoes_2 = jogador_df_2[jogador_df_2['Lesao_Ocorreu'] == True].sort_values(by='Data', ascending=False).copy()
        if 'Data' in df_historico_lesoes_2.columns:
            df_historico_lesoes_2['Data'] = df_historico_lesoes_2['Data'].dt.strftime('%Y-%m-%d')
        config_colunas_2 = [{"id": col_id, "name": formatar_nome_coluna(col_id)} for col_id in ['Data', 'Tipo_Lesao_Formatado', 'Tempo_Ausencia'] if col_id in df_historico_lesoes_2.columns]
        
        tabela_lesao_2 = dbc.Card([
            dbc.CardHeader(html.H4(f"Histórico de Lesões: {jogador_selecionado_2}", className="card-title text-center", style={'color': 'black'})),
            dbc.CardBody(
                dash_table.DataTable(
                    id='tabela-lesao-jogador-2',
                    columns=config_colunas_2,
                    data=df_historico_lesoes_2[['Data', 'Tipo_Lesao_Formatado', 'Tempo_Ausencia']].to_dict('records'),
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={'backgroundColor': '#0066CC', 'fontWeight': 'bold', 'color': 'white'},
                    style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}]
                ) if not df_historico_lesoes_2.empty else html.P("Nenhuma lesão registrada.", className="text-center text-muted m-auto text-dark")
            )
        ], className="h-100 shadow border-0 bg-light")

        return html.Div([
            cartoes_resumo_comparacao,
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_comparacao_risco), className="h-100"), md=12, className="mb-4 shadow"),
            ]),
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_comparacao_distancia), className="h-100"), md=12, className="mb-4 shadow"),
            ]),
            html.H3("Histórico de Lesões Comparativo", className="text-center my-4 text-light"),
            dbc.Row([
                dbc.Col(tabela_lesao_1, md=6, className="mb-4"),
                dbc.Col(tabela_lesao_2, md=6, className="mb-4"),
            ], className="g-4")
        ])
    
    app.run(debug=True)

# --- Bloco de execução para permitir que o script rode sozinho ---

if __name__ == '__main__':
    executar_app_dashboard()