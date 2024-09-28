import os
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import threading
import time

# Função para simular a corrida com e sem arrefecimento
def simulate_race_with_cooling(circuit):
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

    base_temp = circuit_temp_map.get(circuit, 25)  # Temperatura padrão

    # Temperatura sem arrefecimento
    temperature_without_cooling = base_temp + 20 * np.sin(2 * np.pi * time_data / 20) + np.random.normal(0, 3, len(time_data))

    # Temperatura com arrefecimento
    temperature_with_cooling = temperature_without_cooling - 10 * np.sin(2 * np.pi * time_data / 20) - np.random.normal(0, 2, len(time_data))

    return time_data, temperature_without_cooling, temperature_with_cooling

# Simulação inicial dos dados
initial_circuit = 'Interlagos'  # Circuito inicial
time_data, temp_without, temp_with = simulate_race_with_cooling(initial_circuit)

# Função para enviar dados de RPM para o Arduino via arquivo TXT
def send_rpm_to_arduino(circuit, rpm):
    filepath = r'circuito_rpm.txt'  # Mude o caminho para o arquivo TXT
    with open(filepath, 'w') as file:
        file.write(f'Circuito: {circuit}\n')
        file.write(f'RPM: {rpm}\n')

    # Simula motor funcionando por 3 minutos em uma thread separada
    def motor_simulation():
        for i in range(180):  # 3 minutos = 180 segundos
            time.sleep(1)  # Simula 1 segundo

    thread = threading.Thread(target=motor_simulation)
    thread.start()

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
], fluid=True, style={'height': '100vh', 'width': '100vw', 'padding': '0', 'margin': '0', 'backgroundColor': 'black'})

# Estilos adicionais via CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body { 
                margin: 0; 
                background-image: url('C:/Users/User/Desktop/python-getting-started/IMG/IMAGEM DE FUNDO.jpg'); 
                background-size: cover; 
                background-position: center; 
            }
            .button-grid {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .circuit-btn {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 3rem;
                font-weight: bold;
                text-transform: uppercase;
                margin: 10px;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .circuit-btn:hover {
                letter-spacing: 2px;
                color: cyan;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Função para atualizar o gráfico com base no circuito selecionado
@app.callback(
    Output('modal', 'is_open'),
    Output('modal-content', 'children'),
    Input('btn-campo-grande', 'n_clicks'),
    Input('btn-goiania', 'n_clicks'),
    Input('btn-londrina', 'n_clicks'),
    Input('btn-santa-cruz', 'n_clicks'),
    Input('btn-interlagos', 'n_clicks'),
    Input('btn-cascavel', 'n_clicks'),
    Input('btn-taruma', 'n_clicks'),
    Input('btn-curvelo', 'n_clicks'),
    Input('close-modal', 'n_clicks'),
    State('modal', 'is_open')
)
def display_dashboard(n_campo_grande, n_goiania, n_londrina, n_santa_cruz, n_interlagos, n_cascavel, n_taruma, n_curvelo, close_n_clicks, is_open):
    # Define o circuito selecionado com base no botão clicado
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open, dash.no_update
    
    # Se o botão de fechar foi clicado, fecha a modal
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'close-modal':
        return False, dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    circuit = button_id.replace('btn-', '').replace('-', ' ').capitalize()

    # Envia o RPM para o Arduino
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
    send_rpm_to_arduino(circuit, rpm)

    # Simular novos dados de temperatura com base no circuito selecionado
    time_data, temp_without, temp_with = simulate_race_with_cooling(circuit)

    # Gráficos
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=time_data, y=temp_without, mode='lines+markers', name='Sem Arrefecimento', 
                                  line=dict(color='red', width=2), fill='tozeroy'))
    fig_temp.add_trace(go.Scatter(x=time_data, y=temp_with, mode='lines+markers', name='Com Arrefecimento', 
                                  line=dict(color='cyan', width=2), fill='tozeroy'))
    fig_temp.update_layout(
        title=f'Análise da Temperatura da Turbina - {circuit}',
        xaxis_title='Tempo (minutos)',
        yaxis_title='Temperatura (°C)',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        yaxis=dict(range=[0, 100]),
        xaxis=dict(showgrid=True, gridcolor='gray'),
    )

    performance_without_cooling = 100 - (temp_without - 70) * 0.5
    performance_with_cooling = 100 - (temp_with - 70) * 0.5
    fig_perf = go.Figure()
    fig_perf.add_trace(go.Scatter(x=time_data, y=performance_without_cooling, mode='lines+markers', name='Desempenho Sem Arrefecimento',
                                   line=dict(color='red', width=2), fill='tozeroy'))
    fig_perf.add_trace(go.Scatter(x=time_data, y=performance_with_cooling, mode='lines+markers', name='Desempenho Com Arrefecimento',
                                   line=dict(color='cyan', width=2), fill='tozeroy'))
    fig_perf.update_layout(
        title=f'Análise de Desempenho - {circuit}',
        xaxis_title='Tempo (minutos)',
        yaxis_title='Desempenho (%)',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        yaxis=dict(range=[0, 100]),
        xaxis=dict(showgrid=True, gridcolor='gray'),
    )

    # Montar conteúdo do modal
    modal_content = [
        dcc.Graph(figure=fig_temp),
        dcc.Graph(figure=fig_perf),
        html.Div([
            html.H4("Análise de Resultados"),
            html.P("A análise dos dados mostra que:"),
            html.P(f"- O sistema de arrefecimento teve um desempenho significativo na redução da temperatura média da turbina. "
                   f"No circuito de {circuit}, a temperatura sem arrefecimento alcançou até {max(temp_without):.1f} °C, "
                   f"enquanto com o sistema de arrefecimento a temperatura foi reduzida para {max(temp_with):.1f} °C."),
            html.P("- Essa redução de temperatura é crucial para evitar falhas no motor e melhorar a eficiência."),
            html.P("- A performance do veículo também se beneficiou, apresentando uma melhora de até {:.1f}% em relação ao desempenho sem o sistema de arrefecimento.".format(
                max(performance_without_cooling) - max(performance_with_cooling))),
            html.P(f"- A temperatura média foi mais estável com o sistema de arrefecimento, o que resulta em um melhor controle e segurança durante a corrida."),
        ])
    ]
    return True, modal_content

# Iniciar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
