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
def format_col_name(col_name):
    replacements = {
        '(km)': '(km)',
        '(bpm)': '(bpm)',
        'Max': 'Máximo',
        'Media': 'Média',
        'Num': 'Número de',
        'Distancia': 'Distância',
        'Percorrida': 'Percorrida',
        'Estimado': 'Estimado',
        'Frequencia': 'Frequência',
        'Pontuacao': 'Pontuação',
        'Risco': 'Risco',
        'Lesao': 'Lesão',
        'Categoria': 'Categoria',
        'Sprints': 'Sprints',
        'Fadiga_Excessiva/Risco_Lesao': 'Fadiga Excessiva / Risco de Lesão',
        'Lesao_Muscular_Leve': 'Lesão Muscular Leve',
        'Entorse_Leve': 'Entorse Leve',
        'Contusao': 'Contusão',
        'Articular': 'Articular',
        'Nenhuma_Lesao': 'Nenhuma Lesão',
        'Tipo_Atividade': 'Tipo de Atividade',
        'Acute_Workload': 'Carga Aguda de Treino',
        'Chronic_Workload': 'Carga Crônica de Treino',
        'ACWR': 'Razão Carga Aguda/Crônica (ACWR)',
        'Dias_Desde_Ultima_Lesao': 'Dias Desde Última Lesão',
        'Num_Lesoes_Anteriores': 'Número de Lesões Anteriores',
        'Probabilidade_Lesao': 'Probabilidade de Lesão',
        'Tipo_Lesao': 'Tipo de Lesão',
        'Tempo_Ausencia': 'Tempo de Ausência',
        'Tipo_Lesao_Formatado': 'Tipo de Lesão'
    }
    if col_name in replacements:
        return replacements[col_name]
    formatted_name = col_name.replace('_', ' ')
    for old_part, new_part in replacements.items():
        if old_part not in ['Tipo_Lesao', 'Tempo_Ausencia', 'Tipo_Lesao_Formatado']:
            formatted_name = formatted_name.replace(old_part.replace('_', ' '), new_part)
    return formatted_name

def map_risk_category_to_text(risk_category_value):
    if pd.isna(risk_category_value):
        return 'N/A'
    return risk_category_value

# --- Configurações do Banco de Dados ---
DATA_FOLDER = 'data'
DB_FILE = os.path.join(DATA_FOLDER, 'performance_data.db')
TABLE_NAME = 'performance_atletas'
engine = create_engine(f'sqlite:///{DB_FILE}')

# --- Carregar os Dados Iniciais ---
def load_data_from_sql():
    try:
        df = pd.read_sql_table(TABLE_NAME, engine)
        df['Data'] = pd.to_datetime(df['Data'])
        df['Tipo_Lesao_Formatado'] = df['Tipo_Lesao'].apply(format_col_name) 
        df['Categoria_Risco_Lesao_Formatado'] = df['Categoria_Risco_Lesao'].apply(map_risk_category_to_text) 
        df['Tipo_Atividade_Formatado'] = df['Tipo_Atividade'].apply(format_col_name)
        print(f"Dados carregados do SQL com sucesso. Total de {len(df)} registros.")
        print(f"Colunas disponíveis em df_global: {df.columns.tolist()}")
        print(f"Nomes de jogadores únicos no DB: {sorted(df['Nome_Padronizado'].unique().tolist())}")
        return df
    except Exception as e:
        print(f"Erro ao carregar dados do banco de dados: {e}")
        return pd.DataFrame()

# --- Encapsulando a Lógica do Dashboard em uma Função ---
def run_dashboard_app():
    global df_global
    df_global = load_data_from_sql()
    player_names = sorted(df_global['Nome_Padronizado'].unique()) if not df_global.empty else []
    
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
                    id='player-dropdown',
                    options=[{'label': name, 'value': name} for name in player_names],
                    placeholder="Selecione um jogador para análise individual...",
                    multi=False,
                    clearable=True
                ))
            ], className="mb-4 shadow border-0"),
            width=12, lg=6
        ), justify="center"),
        dbc.Row(dbc.Col(html.Div(id='player-output-container'), width=12)),
        dbc.Row(dbc.Col(html.Hr(style={'borderColor': 'white', 'borderWidth': '3px'}), className="my-5")),
        dbc.Row(dbc.Col(html.H2("Comparação de Jogadores", className="text-light text-center mb-4"))),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(html.H4("Selecione Jogador 1", className="card-title text-center text-primary")),
                    dbc.CardBody(dcc.Dropdown(
                        id='player-dropdown-1',
                        options=[{'label': name, 'value': name} for name in player_names],
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
                        id='player-dropdown-2',
                        options=[{'label': name, 'value': name} for name in player_names],
                        placeholder="Selecione o segundo jogador...",
                        multi=False,
                        clearable=True
                    ))
                ], className="mb-4 shadow border-0"),
                width=12, lg=6
            )
        ], justify="center"),
        dbc.Row(dbc.Col(html.Div(id='comparison-output-container'), width=12))
    ], fluid=True, style={'backgroundColor': '#0066CC', 'padding': '3rem'})

    @app.callback(
        Output('player-output-container', 'children'),
        Input('player-dropdown', 'value')
    )
    def update_player_info(selected_player):
        if selected_player is None:
            return dbc.Alert("Selecione um jogador no menu acima para visualizar os detalhes de performance e risco de lesão.", color="info", className="text-center my-5")
        player_df = df_global[df_global['Nome_Padronizado'] == selected_player].copy()
        if player_df.empty:
            return dbc.Alert(f"Dados não encontrados para o jogador: {selected_player}", color="warning", className="text-center my-5")
        latest_data = player_df.sort_values(by='Data', ascending=False).iloc[0]
        risk_color_map = {'Baixo': 'success', 'Moderado': 'warning', 'Alto': 'danger', 'Muito Alto': 'dark'}
        risk_category_text = latest_data.get('Categoria_Risco_Lesao_Formatado', 'N/A') 
        risk_badge_color = risk_color_map.get(risk_category_text, 'secondary')
        dias_desde_lesao = latest_data.get('Dias_Desde_Ultima_Lesao')
        data_registro_atual = latest_data.get('Data') 
        last_injury_date_for_player = player_df[player_df['Lesao_Ocorreu'] == True]['Data'].max()
        dias_texto = "N/A"
        if pd.notna(dias_desde_lesao) and dias_desde_lesao is not None:
            if pd.notna(last_injury_date_for_player) and pd.notna(data_registro_atual):
                dias_texto = (
                    f"Última lesão em {last_injury_date_for_player.strftime('%Y-%m-%d')}, "
                    f"{int(dias_desde_lesao)} dias sem lesionar "
                    f"(Data de referência: {data_registro_atual.strftime('%Y-%m-%d')})"
                )
            else:
                dias_texto = f"{int(dias_desde_lesao)} dias sem lesionar (Data de referência: {data_registro_atual.strftime('%Y-%m-%d') if pd.notna(data_registro_atual) else 'N/A'})"
        elif player_df['Lesao_Ocorreu'].sum() == 0:
            dias_texto = "Nenhuma lesão registrada"
        else:
            dias_texto = "Informação de dias sem lesão indisponível"
        summary_card = dbc.Card([
            dbc.CardHeader(html.H2(f"Perfil Detalhado: {selected_player}", className="card-title text-center text-primary")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(html.P(f"Posição: {latest_data.get('Posicao', 'N/A')}", className="lead mb-0 text-dark")),
                    dbc.Col(html.P([f"Pontuação de Risco de Lesão: {latest_data.get('Pontuacao_Risco_Lesao', 'N/A')} (", dbc.Badge(risk_category_text, color=risk_badge_color, className="me-1 fs-6"), ")"], className="lead mb-0 text-dark")),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col(html.P(dias_texto, className="lead mb-0 text-dark")),
                    dbc.Col(html.P(f"Número de Lesoes Anteriores: {latest_data.get('Num_Lesoes_Anteriores', 'N/A')}", className="lead mb-0 text-dark"))
                ])
            ])
        ], className="mb-4 shadow p-2 border-0 bg-light")
        risk_trend_df = player_df.dropna(subset=['Pontuacao_Risco_Lesao']).sort_values(by='Data')
        if not risk_trend_df.empty:
            fig_risk = px.line(risk_trend_df, x='Data', y='Pontuacao_Risco_Lesao', title=f'Pontuação de Risco de Lesão', labels={'Pontuacao_Risco_Lesao': 'Pontuação de Risco'}, template='plotly_white', color_discrete_sequence=['red'])
            fig_risk.update_traces(mode='lines+markers')
            fig_risk.update_layout(hovermode="x unified")
        else:
            fig_risk = go.Figure().update_layout(title="Dados de Pontuação de Risco Insuficientes")
        if 'Probabilidade_Lesao' not in player_df.columns:
            player_df['Probabilidade_Lesao'] = player_df['Pontuacao_Risco_Lesao'].apply(lambda x: min(0.95, max(0.05, 0.05 + x * 0.1)) if pd.notna(x) else np.nan)
        prob_lesao_trend_df = player_df.dropna(subset=['Probabilidade_Lesao']).sort_values(by='Data')
        if not prob_lesao_trend_df.empty:
            fig_prob_lesao = px.line(prob_lesao_trend_df, x='Data', y='Probabilidade_Lesao', title=f'Probabilidade de Lesão', labels={'Probabilidade_Lesao': 'Probabilidade de Lesão (%)'}, line_shape='spline', template='plotly_white', color_discrete_sequence=['orange'])
            fig_prob_lesao.update_traces(mode='lines+markers', hovertemplate='Data: %{x}<br>Probabilidade: %{y:.2%}')
            fig_prob_lesao.update_layout(hovermode="x unified", yaxis_tickformat=".0%")
            fig_prob_lesao.add_hline(y=0.5, line_dash="dot", line_color="red", annotation_text="Limiar de Alerta (50%)", annotation_position="bottom right")
        else:
            fig_prob_lesao = go.Figure().update_layout(title="Dados de Probabilidade de Lesão Insuficientes")
        performance_metrics = ['Distancia_Percorrida_(km)', 'Num_Sprints', 'VO2_Max_Estimado', 'FC_Media_(bpm)']
        brazil_colors = ['#009739', '#FEDD00', '#002776', '#a8a8a8'] 
        performance_graphs_components = []
        for i, metric in enumerate(performance_metrics):
            if metric in player_df.columns and not player_df[metric].dropna().empty:
                formatted_metric_name = format_col_name(metric)
                fig_perf = px.line(player_df.sort_values(by='Data'), x='Data', y=metric, title=f'{formatted_metric_name}', labels={'Data': 'Data', metric: formatted_metric_name}, template='plotly_white', color_discrete_sequence=[brazil_colors[i % len(brazil_colors)]])
                fig_perf.update_traces(mode='lines+markers')
                fig_perf.update_layout(hovermode="x unified")
                performance_graphs_components.append(dbc.Col(dbc.Card(dcc.Graph(figure=fig_perf), className="h-100"), md=6, className="mb-4 shadow"))
            else:
                performance_graphs_components.append(dbc.Col(dbc.Card(dbc.CardBody(html.P(f"Dados insuficientes para {format_col_name(metric)}.", className="text-center text-muted m-auto"))), md=6, className="mb-4 shadow d-flex align-items-center justify-content-center"))
        injury_history_df = player_df[player_df['Lesao_Ocorreu'] == True].sort_values(by='Data', ascending=False).copy()
        if 'Data' in injury_history_df.columns:
            injury_history_df['Data'] = injury_history_df['Data'].dt.strftime('%Y-%m-%d')
        if not injury_history_df.empty:
            cols_config = []
            for col_id in ['Data', 'Tipo_Lesao_Formatado', 'Tempo_Ausencia']:
                if col_id in injury_history_df.columns:
                    col_def = {"id": col_id, "name": format_col_name(col_id)}
                    cols_config.append(col_def)
            injury_table_component = dbc.Card([
                dbc.CardHeader(html.H3("Histórico de Lesões", className="card-title text-center", style={'color': 'black'})), 
                dbc.CardBody(dash_table.DataTable(id='player-injury-table', columns=cols_config, data=injury_history_df[['Data', 'Tipo_Lesao_Formatado', 'Tempo_Ausencia']].to_dict('records'), style_table={'overflowX': 'auto'}, style_cell={'textAlign': 'left', 'padding': '10px'}, style_header={'backgroundColor': '#0066CC', 'fontWeight': 'bold', 'color': 'white'}, style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}]))
            ], className="mb-4 shadow border-0 bg-light")
        else:
            injury_table_component = dbc.Card([
                dbc.CardHeader(html.H3("Histórico de Lesões", className="card-title text-center", style={'color': 'black'})),
                dbc.CardBody(html.P("Nenhuma lesão registrada para este jogador.", className="text-center text-muted m-auto text-dark"))
            ], className="mb-4 shadow border-0 bg-light d-flex align-items-center justify-content-center")
        return html.Div([
            summary_card,
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_risk), className="h-100"), md=6, className="mb-4 shadow"),
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_prob_lesao), className="h-100"), md=6, className="mb-4 shadow"),
            ], className="g-4"),
            html.H3("Métricas de Performance", className="text-center my-4 text-light"),
            dbc.Row(performance_graphs_components, className="g-4"),
            injury_table_component
        ], className="mt-4")

    @app.callback(
        Output('comparison-output-container', 'children'),
        [Input('player-dropdown-1', 'value'),
         Input('player-dropdown-2', 'value')]
    )
    def update_comparison_info(selected_player_1, selected_player_2):
        if not selected_player_1 and not selected_player_2:
            return dbc.Alert("Selecione dois jogadores para comparar suas performances e riscos de lesão.", color="info", className="text-center my-5")
        if not selected_player_1 or not selected_player_2:
            return dbc.Alert("Selecione ambos os jogadores para iniciar a comparação.", color="warning", className="text-center my-5")
        if selected_player_1 == selected_player_2:
            return dbc.Alert("Por favor, selecione dois jogadores diferentes para comparação.", color="danger", className="text-center my-5")
        player_df_1 = df_global[df_global['Nome_Padronizado'] == selected_player_1].copy()
        player_df_2 = df_global[df_global['Nome_Padronizado'] == selected_player_2].copy()
        if player_df_1.empty or player_df_2.empty:
            return dbc.Alert(f"Dados insuficientes para um ou ambos os jogadores: {selected_player_1}, {selected_player_2}", color="warning", className="text-center my-5")
        risk_color_map = {'Baixo': 'success', 'Moderado': 'warning', 'Alto': 'danger', 'Muito Alto': 'dark'}
        def create_risk_badge(data_row):
            risk_category_text = data_row.get('Categoria_Risco_Lesao_Formatado', 'N/A')
            risk_badge_color = risk_color_map.get(risk_category_text, 'secondary')
            return dbc.Badge(risk_category_text, color=risk_badge_color, className="me-1 fs-6")
        def format_dias_texto_comparison(df, current_data_row):
            dias_desde_lesao = current_data_row.get('Dias_Desde_Ultima_Lesao')
            data_registro_atual = current_data_row.get('Data')
            last_injury_date = df[df['Lesao_Ocorreu'] == True]['Data'].max()
            if pd.notna(dias_desde_lesao) and dias_desde_lesao is not None:
                if pd.notna(last_injury_date) and pd.notna(data_registro_atual):
                    return (
                        f"Última lesão em {last_injury_date.strftime('%Y-%m-%d')}, "
                        f"{int(dias_desde_lesao)} dias sem lesionar "
                        f"(Data de referência: {data_registro_atual.strftime('%Y-%m-%d')})"
                    )
                else:
                    return f"{int(dias_desde_lesao)} dias sem lesionar (Data de referência: {data_registro_atual.strftime('%Y-%m-%d') if pd.notna(data_registro_atual) else 'N/A'})"
            elif df['Lesao_Ocorreu'].sum() == 0:
                return "Nenhuma lesão registrada"
            else:
                return "Informação de dias sem lesão indisponível"
        latest_data_1 = player_df_1.sort_values(by='Data', ascending=False).iloc[0]
        latest_data_2 = player_df_2.sort_values(by='Data', ascending=False).iloc[0]
        dias_texto_1 = format_dias_texto_comparison(player_df_1, latest_data_1)
        dias_texto_2 = format_dias_texto_comparison(player_df_2, latest_data_2)
        comparison_summary_cards = dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H3(selected_player_1, className="card-title text-center text-primary")),
                dbc.CardBody([
                    html.P(f"Posição: {latest_data_1.get('Posicao', 'N/A')}", className="mb-0"),
                    html.P(['Risco: ', create_risk_badge(latest_data_1), f" ({latest_data_1.get('Pontuacao_Risco_Lesao', 'N/A')})"], className="mb-0"),
                    html.P(dias_texto_1, className="mb-0"),
                    html.P(f"Lesões Anteriores: {latest_data_1.get('Num_Lesoes_Anteriores', 'N/A')}", className="mb-0")
                ])
            ], className="h-100 shadow border-0 bg-light"), md=6),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H3(selected_player_2, className="card-title text-center text-primary")),
                dbc.CardBody([
                    html.P(f"Posição: {latest_data_2.get('Posicao', 'N/A')}", className="mb-0"),
                    html.P(['Risco: ', create_risk_badge(latest_data_2), f" ({latest_data_2.get('Pontuacao_Risco_Lesao', 'N/A')})"], className="mb-0"),
                    html.P(dias_texto_2, className="mb-0"),
                    html.P(f"Lesões Anteriores: {latest_data_2.get('Num_Lesoes_Anteriores', 'N/A')}", className="mb-0")
                ])
            ], className="h-100 shadow border-0 bg-light"), md=6)
        ], className="g-4 mb-4")
        fig_risk_comparison = go.Figure()
        if 'Probabilidade_Lesao' not in player_df_1.columns:
            player_df_1['Probabilidade_Lesao'] = player_df_1['Pontuacao_Risco_Lesao'].apply(lambda x: min(0.95, max(0.05, 0.05 + x * 0.1)) if pd.notna(x) else np.nan)
        if 'Probabilidade_Lesao' not in player_df_2.columns:
            player_df_2['Probabilidade_Lesao'] = player_df_2['Pontuacao_Risco_Lesao'].apply(lambda x: min(0.95, max(0.05, 0.05 + x * 0.1)) if pd.notna(x) else np.nan)
        fig_risk_comparison.add_trace(go.Scatter(x=player_df_1['Data'], y=player_df_1['Pontuacao_Risco_Lesao'], mode='lines+markers', name=selected_player_1 + ' (Risco)', line=dict(color='red')))
        fig_risk_comparison.add_trace(go.Scatter(x=player_df_2['Data'], y=player_df_2['Pontuacao_Risco_Lesao'], mode='lines+markers', name=selected_player_2 + ' (Risco)', line=dict(color='blue')))
        fig_risk_comparison.add_trace(go.Scatter(x=player_df_1['Data'], y=player_df_1['Probabilidade_Lesao'], mode='lines+markers', name=selected_player_1 + ' (Probabilidade)', line=dict(color='salmon', dash='dot')))
        fig_risk_comparison.add_trace(go.Scatter(x=player_df_2['Data'], y=player_df_2['Probabilidade_Lesao'], mode='lines+markers', name=selected_player_2 + ' (Probabilidade)', line=dict(color='lightblue', dash='dot')))
        fig_risk_comparison.update_layout(title='Comparação de Risco e Probabilidade de Lesão', xaxis_title='Data', yaxis_title='Valor', template='plotly_white', hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_dist_comparison = go.Figure()
        fig_dist_comparison.add_trace(go.Scatter(x=player_df_1['Data'], y=player_df_1['Distancia_Percorrida_(km)'], mode='lines+markers', name=selected_player_1, line=dict(color='#009739')))
        fig_dist_comparison.add_trace(go.Scatter(x=player_df_2['Data'], y=player_df_2['Distancia_Percorrida_(km)'], mode='lines+markers', name=selected_player_2, line=dict(color='#FEDD00')))
        fig_dist_comparison.update_layout(title='Comparação de Distância Percorrida (km)', xaxis_title='Data', yaxis_title='Distância Percorrida (km)', template='plotly_white', hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        injury_history_df_1 = player_df_1[player_df_1['Lesao_Ocorreu'] == True].sort_values(by='Data', ascending=False).copy()
        if 'Data' in injury_history_df_1.columns:
            injury_history_df_1['Data'] = injury_history_df_1['Data'].dt.strftime('%Y-%m-%d')
        cols_config_1 = [{"id": col_id, "name": format_col_name(col_id)} for col_id in ['Data', 'Tipo_Lesao_Formatado', 'Tempo_Ausencia'] if col_id in injury_history_df_1.columns]
        injury_table_1 = dbc.Card([
            dbc.CardHeader(html.H4(f"Histórico de Lesões: {selected_player_1}", className="card-title text-center", style={'color': 'black'})),
            dbc.CardBody(dash_table.DataTable(id='player-1-injury-table', columns=cols_config_1, data=injury_history_df_1[['Data', 'Tipo_Lesao_Formatado', 'Tempo_Ausencia']].to_dict('records'), style_table={'overflowX': 'auto'}, style_cell={'textAlign': 'left', 'padding': '10px'}, style_header={'backgroundColor': '#0066CC', 'fontWeight': 'bold', 'color': 'white'}, style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}]) if not injury_history_df_1.empty else html.P("Nenhuma lesão registrada.", className="text-center text-muted m-auto text-dark"))
        ], className="h-100 shadow border-0 bg-light")
        injury_history_df_2 = player_df_2[player_df_2['Lesao_Ocorreu'] == True].sort_values(by='Data', ascending=False).copy()
        if 'Data' in injury_history_df_2.columns:
            injury_history_df_2['Data'] = injury_history_df_2['Data'].dt.strftime('%Y-%m-%d')
        cols_config_2 = [{"id": col_id, "name": format_col_name(col_id)} for col_id in ['Data', 'Tipo_Lesao_Formatado', 'Tempo_Ausencia'] if col_id in injury_history_df_2.columns]
        injury_table_2 = dbc.Card([
            dbc.CardHeader(html.H4(f"Histórico de Lesões: {selected_player_2}", className="card-title text-center", style={'color': 'black'})),
            dbc.CardBody(dash_table.DataTable(id='player-2-injury-table', columns=cols_config_2, data=injury_history_df_2[['Data', 'Tipo_Lesao_Formatado', 'Tempo_Ausencia']].to_dict('records'), style_table={'overflowX': 'auto'}, style_cell={'textAlign': 'left', 'padding': '10px'}, style_header={'backgroundColor': '#0066CC', 'fontWeight': 'bold', 'color': 'white'}, style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}]) if not injury_history_df_2.empty else html.P("Nenhuma lesão registrada.", className="text-center text-muted m-auto text-dark"))
        ], className="h-100 shadow border-0 bg-light")
        return html.Div([
            comparison_summary_cards,
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_risk_comparison), className="h-100"), md=12, className="mb-4 shadow"),
            ]),
            dbc.Row([
                dbc.Col(dbc.Card(dcc.Graph(figure=fig_dist_comparison), className="h-100"), md=12, className="mb-4 shadow"),
            ]),
            html.H3("Histórico de Lesões Comparativo", className="text-center my-4 text-light"),
            dbc.Row([
                dbc.Col(injury_table_1, md=6, className="mb-4"),
                dbc.Col(injury_table_2, md=6, className="mb-4"),
            ], className="g-4")
        ])
    
    app.run(debug=True)

# --- Bloco de execução para permitir que o script rode sozinho ---
if __name__ == '__main__':
    run_dashboard_app()