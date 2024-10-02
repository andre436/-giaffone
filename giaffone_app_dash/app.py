import os
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import threading
import time
import requests  # Adicione esta importação

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

# Função para gerar o conteúdo do arquivo TXT
def generate_txt_content(circuit, rpm):
    content = f"Circuito: {circuit}\n"
    content += f"RPM: {rpm}\n"
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

    # Mapeamento dos circuitos
    circuit_map = {
        'btn-campo-grande': 'Campo Grande',
        'btn-goiania': 'Goiânia',
        'btn-londrina': 'Londrina',
        'btn-santa-cruz': 'Santa Cruz',
        'btn-interlagos': 'Interlagos',
        'btn-cascavel': 'Cascavel',
        'btn-taruma': 'Tarumã',
        'btn-curvelo': 'Curvelo',
    }

    # Obtendo o nome do circuito
    circuit = circuit_map.get(triggered_id, 'Desconhecido')

    # Mapeamento de RPM baseado no circuito
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

    # Gerar conteúdo TXT
    txt_content = generate_txt_content(circuit, rpm)

    # Simular ações em uma thread separada
    def simulate_actions():
        print(f"Acendendo LED 1")
        time.sleep(1)
        print(f"Acendendo LED 2 e apagando LED 1")
        time.sleep(1)
        print(f"Ligando Ventoinha 1 e Ventoinha 2")
        time.sleep(180)  # 3 minutos
        print(f"Desligando Ventoinha 1 e Ventoinha 2")

    # Enviar dados para o ESP
    try:
        requests.post("http://192.168.1.9:80", data={'circuit': circuit, 'rpm': rpm})
        print(f'Dados enviados para o ESP: Circuito={circuit}, RPM={rpm}')
    except Exception as e:
        print(f'Erro ao enviar dados para o ESP: {e}')

    # Iniciar simulação em uma thread separada
    threading.Thread(target=simulate_actions).start()

    # Gerar os gráficos
    time_data, temp_without_cooling, temp_with_cooling = simulate_race_with_cooling(circuit)
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=time_data, y=temp_without_cooling, mode='lines', name='Sem Arrefecimento', line=dict(color='red')))
    figure.add_trace(go.Scatter(x=time_data, y=temp_with_cooling, mode='lines', name='Com Arrefecimento', line=dict(color='blue')))
    figure.update_layout(title=f'Temperaturas em {circuit}', xaxis_title='Tempo (min)', yaxis_title='Temperatura (°C)')

    # Preparar conteúdo do modal
    modal_content = [
        dcc.Graph(figure=figure),
        dcc.Markdown(txt_content),
    ]

    return True, modal_content, dcc.send_data_frame(txt_content, 'circuito.txt')

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
