import os
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import threading
import time

# Configurações do aplicativo Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Função para simular a corrida com e sem arrefecimento
def simulate_race_with_cooling(circuit):
    time_data = np.linspace(0, 90, 180)  # Tempo em minutos (1h30)
    
    # Temperaturas baseadas em cada circuito
    circuit_temp_map = {
        'Campo Grande': 28,
        'Goiânia': 30,
        'Londrina': 20,
        'Santa Cruz': 24,
        'Interlagos': 18,
        'Cascavel': 22,
        'Tarumã': 16,
        'Curvelo': 26,
    }

    base_temp = circuit_temp_map.get(circuit, 25)  # Temperatura padrão

    # Temperatura sem arrefecimento
    temperature_without_cooling = base_temp + 20 * np.sin(2 * np.pi * time_data / 20) + np.random.normal(0, 3, len(time_data))

    # Temperatura com arrefecimento
    temperature_with_cooling = temperature_without_cooling - 10 * np.sin(2 * np.pi * time_data / 20) - np.random.normal(0, 2, len(time_data))

    # Salvar dados em um arquivo TXT
    save_data_to_file(circuit, time_data, temperature_without_cooling, temperature_with_cooling)

    return time_data, temperature_without_cooling, temperature_with_cooling

# Função para salvar dados em um arquivo TXT
def save_data_to_file(circuit, time_data, temp_without, temp_with):
    filename = f"{circuit.replace(' ', '_').lower()}_data.txt"
    with open(filename, 'w') as f:
        f.write("Tempo (min), Temperatura Sem Arrefecimento (°C), Temperatura Com Arrefecimento (°C)\n")
        for t, tw, tc in zip(time_data, temp_without, temp_with):
            f.write(f"{t:.2f}, {tw:.2f}, {tc:.2f}\n")

# Layout da página de login
login_layout = dbc.Container([
    dbc.Row(dbc.Col(html.H2("Login - SCAT", className="text-center"), width=12)),
    dbc.Row(dbc.Col(dbc.Input(id="username", placeholder="Usuário", type="text"), width=12)),
    dbc.Row(dbc.Col(dbc.Input(id="password", placeholder="Senha", type="password"), width=12)),
    dbc.Row(dbc.Col(dbc.Button("Acessar", id="login-button", color="primary", className="mt-3"), width=12)),
    dbc.Row(dbc.Col(html.Div(id="login-output", className="mt-2 text-danger"), width=12))
], className="mt-5")

# Layout principal do aplicativo
main_layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.Div(id='circuit-selection', children=[
            html.Div([
                html.Button('Campo Grande', id='btn-campo-grande', n_clicks=0),
                html.Button('Goiânia', id='btn-goiania', n_clicks=0),
                html.Button('Londrina', id='btn-londrina', n_clicks=0),
                html.Button('Santa Cruz', id='btn-santa-cruz', n_clicks=0),
                html.Button('Interlagos', id='btn-interlagos', n_clicks=0),
                html.Button('Cascavel', id='btn-cascavel', n_clicks=0),
                html.Button('Tarumã', id='btn-taruma', n_clicks=0),
                html.Button('Curvelo', id='btn-curvelo', n_clicks=0),
            ], className='button-grid'),
        ]), width=12)
    ),
    dbc.Row([html.Div(id='dashboard-container', style={'display': 'none'})]),  # Oculto até que um circuito seja selecionado

    # Modal para exibir os gráficos
    dbc.Modal([
        dbc.ModalHeader("Gráficos da Corrida"),
        dbc.ModalBody(
            dbc.Container(id='modal-content', fluid=True)
        ),
        dbc.ModalFooter(
            dbc.Button("Fechar", id='close-modal', className='ml-auto')
        ),
    ], id='modal', size='lg', is_open=False, style={"transition": "transform 0.3s ease-in-out"})
], fluid=True)

# Função de callback para lidar com o login
@app.callback(
    Output('login-output', 'children', allow_duplicate=True),
    Output('dashboard-container', 'style', allow_duplicate=True),
    Input('login-button', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value'),
    prevent_initial_call='initial_duplicate'  # Permitir duplicatas nas chamadas iniciais
)
def login(n_clicks, username, password):
    if n_clicks:
        if username == "scat" and password == "1234":  # Simples validação de login
            return f"Bem-vindo, {username}!", {'display': 'block'}
        else:
            return "Usuário ou senha inválidos", {'display': 'none'}
    return "", {'display': 'none'}

# Função para atualizar o gráfico com base no circuito selecionado
@app.callback(
    Output('modal', 'is_open', allow_duplicate=True),
    Output('modal-content', 'children', allow_duplicate=True),
    Output('dashboard-container', 'style', allow_duplicate=True),
    Input('btn-campo-grande', 'n_clicks'),
    Input('btn-goiania', 'n_clicks'),
    Input('btn-londrina', 'n_clicks'),
    Input('btn-santa-cruz', 'n_clicks'),
    Input('btn-interlagos', 'n_clicks'),
    Input('btn-cascavel', 'n_clicks'),
    Input('btn-taruma', 'n_clicks'),
    Input('btn-curvelo', 'n_clicks'),
    Input('close-modal', 'n_clicks'),
    State('modal', 'is_open'),
    State('dashboard-container', 'style'),
    prevent_initial_call='initial_duplicate'  # Permitir duplicatas nas chamadas iniciais
)
def display_dashboard(n_campo_grande, n_goiania, n_londrina, n_santa_cruz, n_interlagos, n_cascavel, n_taruma, n_curvelo, close_n_clicks, is_open, dashboard_style):
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, dash.no_update, dashboard_style
    
    # Se o botão de fechar foi clicado, fecha a modal
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'close-modal':
        return False, dash.no_update, dashboard_style

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    circuit = button_id.replace('btn-', '').replace('-', ' ').capitalize()

    # Simula a corrida com o circuito selecionado
    time_data, temp_without, temp_with = simulate_race_with_cooling(circuit)

    # Cria os gráficos
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_data, y=temp_without, mode='lines', name='Sem Arrefecimento'))
    fig.add_trace(go.Scatter(x=time_data, y=temp_with, mode='lines', name='Com Arrefecimento'))
    fig.update_layout(title=f'Temperaturas durante a corrida em {circuit}', xaxis_title='Tempo (min)', yaxis_title='Temperatura (°C)')

    return True, dcc.Graph(figure=fig), {'display': 'block'}

# Definir o layout inicial como a página de login
app.layout = login_layout

# Executar o servidor
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=True, host='0.0.0.0', port=port)
