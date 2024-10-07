import os
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import threading
import time

# Função para simular a corrida com e sem arrefecimento
def simulate_race_with_cooling(circuit, intercooler_efficiency, additional_cooling_efficiency):
    time_data = np.linspace(0, 90, 180)  # Tempo em minutos (1h30)
    
    # Definindo temperaturas baseadas em cada circuito
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

    base_temp = circuit_temp_map.get(circuit, 25)  # Temperatura padrão do ambiente

    # Condições iniciais da turbina
    initial_temp_no_cooling = 550  # Temperatura de admissão sem resfriamento (°C)
    intercooler_temp = 120  # Temperatura com intercooler (°C)

    # Cálculos de eficiência térmica
    intercooler_temp_drop = initial_temp_no_cooling - intercooler_temp  # Redução com intercooler
    intercooler_effective_temp = intercooler_temp - intercooler_temp_drop * (1 - intercooler_efficiency)

    # Temperatura com arrefecimento adicional
    final_temp_with_cooling = intercooler_temp - intercooler_temp_drop * additional_cooling_efficiency

    # Simulando as curvas de temperatura ao longo do tempo
    temperature_without_cooling = initial_temp_no_cooling + base_temp * np.sin(2 * np.pi * time_data / 20) + np.random.normal(0, 3, len(time_data))
    temperature_with_cooling = temperature_without_cooling - (initial_temp_no_cooling - final_temp_with_cooling) * (np.sin(2 * np.pi * time_data / 20) + np.random.normal(0, 2, len(time_data)))

    return time_data, temperature_without_cooling, temperature_with_cooling

# Função para calcular emissões de CO₂
def calculate_co2_emissions(initial_emissions, cooling_efficiency):
    # Redução estimada nas emissões com base na eficiência do sistema de resfriamento
    emission_reduction = initial_emissions * (1 - 0.05 * cooling_efficiency)
    return emission_reduction

# Função para gerar o conteúdo do arquivo TXT
def generate_txt_content(circuit, rpm, final_temp_with_cooling, co2_emissions):
    content = f"Circuito: {circuit}\n"
    content += f"RPM: {rpm}\n"
    content += f"Temperatura com sistema de resfriamento: {final_temp_with_cooling:.2f} °C\n"
    content += f"Emissões de CO₂: {co2_emissions:.2f} g/km\n"
    content += "Ações:\n"
    content += "- Acender LED 1\n"
    content += "- Após, acender LED 2 e apagar LED 1\n"
    content += "- Ligar Ventoinha 1 e Ventoinha 2\n"
    content += "Duração das ações: 3 minutos\n"
    return content

# Iniciar o app Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout do aplicativo
app.layout = dbc.Container([
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
    ], id='modal', size='lg'),

    # Componente para download do arquivo TXT
    dcc.Download(id='download-txt'),

], fluid=True, style={'height': '100vh', 'width': '100vw', 'padding': '0', 'margin': '0', 'backgroundColor': 'black'})

# Função para atualizar o gráfico e gerar o arquivo TXT com base no circuito selecionado
@app.callback(
    Output('modal', 'is_open'),
    Output('modal-content', 'children'),
    Output('download-txt', 'data'),
    [Input('btn-campo-grande', 'n_clicks'),
     Input('btn-goiania', 'n_clicks'),
     Input('btn-londrina', 'n_clicks'),
     Input('btn-santa-cruz', 'n_clicks'),
     Input('btn-interlagos', 'n_clicks'),
     Input('btn-cascavel', 'n_clicks'),
     Input('btn-taruma', 'n_clicks'),
     Input('btn-curvelo', 'n_clicks'),
     Input('close-modal', 'n_clicks')],
    [State('modal', 'is_open')]
)
def display_dashboard(n_campo_grande, n_goiania, n_londrina, n_santa_cruz, n_interlagos, n_cascavel, n_taruma, n_curvelo, close_n_clicks, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return is_open, dash.no_update, dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'close-modal':
        return False, dash.no_update, dash.no_update

    # Map the circuit name
    circuit = triggered_id.replace('btn-', '').replace('-', ' ').title()
    if circuit == 'Goiania':
        circuit = 'Goiânia'
    elif circuit == 'Taruma':
        circuit = 'Tarumã'

    # Map RPM based on circuit
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

    intercooler_efficiency = 0.70
    additional_cooling_efficiency = 0.90

    # Simular novos dados de temperatura com base no circuito selecionado
    time_data, temp_without, temp_with = simulate_race_with_cooling(circuit, intercooler_efficiency, additional_cooling_efficiency)

    # Calculando as emissões de CO2
    initial_emissions = 550  # Emissões iniciais em g/km
    co2_emissions = calculate_co2_emissions(initial_emissions, additional_cooling_efficiency)

    # Gerar conteúdo do arquivo TXT
    txt_content = generate_txt_content(circuit, rpm, temp_with[-1], co2_emissions)

    # Gráficos
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=time_data, y=temp_without, mode='lines+markers', name='Sem Arrefecimento', 
                                  line=dict(color='red', width=2), fill='tozeroy'))
    fig_temp.add_trace(go.Scatter(x=time_data, y=temp_with, mode='lines+markers', name='Com Arrefecimento', 
                                  line=dict(color='cyan', width=2), fill='tozeroy'))
    fig_temp.update_layout(
        title=f'Análise de Temperatura no Circuito de {circuit}',
        xaxis_title='Tempo (min)',
        yaxis_title='Temperatura (°C)',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )

    return True, dcc.Graph(figure=fig_temp), {'content': txt_content, 'filename': f'{circuit}_dados_corrida.txt'}

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
