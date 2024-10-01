
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import threading
import time
import os


# Função para simular a corrida com e sem arrefecimento
def simulate_race_with_cooling(circuit):
    time_data = np.linspace(0, 90, 180)  # Tempo em minutos (1h30)
    
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
    base_temp = circuit_temp_map.get(circuit, 25)

    temperature_without_cooling = base_temp + 20 * np.sin(2 * np.pi * time_data / 20) + np.random.normal(0, 3, len(time_data))
    temperature_with_cooling = temperature_without_cooling - 10 * np.sin(2 * np.pi * time_data / 20) - np.random.normal(0, 2, len(time_data))

    return time_data, temperature_without_cooling, temperature_with_cooling

# Função para gerar o conteúdo do arquivo TXT
def generate_txt_content(circuit, rpm):
    return f"Circuito: {circuit}\nRPM: {rpm}\nLED 1: ON\nVentoinha 1: ON\nVentoinha 2: ON\nDuração: 3 minutos\n"

# Função para simular a ativação de LED e ventoinhas
def send_rpm_to_arduino(circuit, rpm):
    print(f"LED 1 ON, Ventoinha 1 e 2 ON por 3 minutos no circuito {circuit}")
    time.sleep(180)  # Simula 3 minutos de funcionamento
    print(f"LED 1 OFF, Ventoinha 1 e 2 OFF no circuito {circuit}")

# Função para gerar o link de download do arquivo TXT
def download_txt_link(circuit, rpm):
    content = generate_txt_content(circuit, rpm)
    return f"data:text/plain;charset=utf-8,{content}"

# Iniciar o app Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout do aplicativo
app.layout = dbc.Container([

    # Botões de seleção de circuitos
    dbc.Row(
        dbc.Col(html.Div(id='circuit-selection', children=[
            html.Div([
                html.Button('Campo Grande', id='btn-campo-grande', className='circuit-btn', n_clicks=0),
                html.Button('Goiânia', id='btn-goiania', className='circuit-btn', n_clicks=0),
                html.Button('Londrina', id='btn-londrina', className='circuit-btn', n_clicks=0),
                html.Button('Santa Cruz', id='btn-santa-cruz', className='circuit-btn', n_clicks=0),
                html.Button('Interlagos', id='btn-interlagos', className='circuit-btn', n_clicks=0),
                html.Button('Cascavel', id='btn-cascavel', className='circuit-btn', n_clicks=0),
                html.Button('Tarumã', id='btn-taruma', className='circuit-btn', n_clicks=0),
                html.Button('Curvelo', id='btn-curvelo', className='circuit-btn', n_clicks=0),
            ], className='button-grid'),
        ]), width=12)
    ),
    
    # Link para download do arquivo TXT
    html.A("Download Arquivo TXT", id='download-link', download="circuito_rpm.txt", href="", target="_blank"),
    
], fluid=True)

# Callback para gerar o arquivo TXT e fazer o download
@app.callback(
    Output('download-link', 'href'),
    Input('btn-campo-grande', 'n_clicks'),
    Input('btn-goiania', 'n_clicks'),
    Input('btn-londrina', 'n_clicks'),
    Input('btn-santa-cruz', 'n_clicks'),
    Input('btn-interlagos', 'n_clicks'),
    Input('btn-cascavel', 'n_clicks'),
    Input('btn-taruma', 'n_clicks'),
    Input('btn-curvelo', 'n_clicks'),
)
def generate_file(n_campo_grande, n_goiania, n_londrina, n_santa_cruz, n_interlagos, n_cascavel, n_taruma, n_curvelo):
    # Determina o circuito baseado no botão clicado
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    circuit = button_id.replace('btn-', '').replace('-', ' ').capitalize()

    # Mapa de RPM por circuito
    circuit_rpm_map = {
        'Campo Grande': 3500,
        'Goiânia': 3700,
        'Londrina': 3400,
        'Santa Cruz': 3600,
        'Interlagos': 3800,
        'Cascavel': 3300,
        'Tarumã': 3200,
        'Curvelo': 3400,
    }
    rpm = circuit_rpm_map.get(circuit, 3000)

    # Enviar os dados ao "Arduino" (simulado)
    send_rpm_to_arduino(circuit, rpm)

    # Gerar link para download do arquivo TXT
    return download_txt_link(circuit, rpm)

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
