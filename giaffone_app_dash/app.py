import os
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import threading
import time
import requests  # Para enviar os dados ao ESP

# Código C++ do ESP32
esp32_code = '''
// Definir as portas do ESP32
const int motorPin = 5;  // Pino do motor
const int redSignalPin = 12;  // Pino do sinal vermelho
const int greenSignalPin = 14;  // Pino do sinal verde
const int fan1Pin = 16;  // Pino da ventoinha 1
const int fan2Pin = 17;  // Pino da ventoinha 2
const int pumpPin = 18;  // Pino da bomba

// Função para configurar os pinos
void setup() {
  // Configurar os pinos como saídas
  pinMode(motorPin, OUTPUT);
  pinMode(redSignalPin, OUTPUT);
  pinMode(greenSignalPin, OUTPUT);
  pinMode(fan1Pin, OUTPUT);
  pinMode(fan2Pin, OUTPUT);
  pinMode(pumpPin, OUTPUT);

  // Inicialmente, tudo desligado
  digitalWrite(motorPin, LOW);
  digitalWrite(redSignalPin, LOW);
  digitalWrite(greenSignalPin, LOW);
  digitalWrite(fan1Pin, LOW);
  digitalWrite(fan2Pin, LOW);
  digitalWrite(pumpPin, LOW);
}

void loop() {
  // 1. Ativar motor entre 4 e 4,8 RPM
  analogWrite(motorPin, 64);  // Ajustar PWM para 4/4.8 RPM

  // 2. Acender o sinal vermelho
  digitalWrite(redSignalPin, HIGH);
  delay(2000);  // Aguardar 2 segundos
  
  // 3. Apagar sinal vermelho e acender sinal verde
  digitalWrite(redSignalPin, LOW);
  digitalWrite(greenSignalPin, HIGH);
  delay(2000);  // Aguardar 2 segundos

  // 4. Ligar o motor do micro-ondas, ventoinhas e bomba por 3 minutos (180000 ms)
  digitalWrite(fan1Pin, HIGH);
  digitalWrite(fan2Pin, HIGH);
  digitalWrite(pumpPin, HIGH);
  
  delay(180000);  // Executa por 3 minutos

  // 5. Desligar motor, ventoinhas e bomba
  digitalWrite(motorPin, LOW);
  digitalWrite(fan1Pin, LOW);
  digitalWrite(fan2Pin, LOW);
  digitalWrite(pumpPin, LOW);

  // 6. Apagar o sinal verde
  digitalWrite(greenSignalPin, LOW);

  // Aguardar para o próximo ciclo
  delay(10000);  // Espera 10 segundos antes de reiniciar o ciclo
}
'''

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
def update_simulation(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, close_click, is_open):
    # Identificar qual botão foi clicado
    clicked_button = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    if clicked_button == 'close-modal':
        return False, None, None

    # Mapear o botão clicado para o circuito correspondente
    circuit_map = {
        'btn-campo-grande': 'Campo Grande',
        'btn-goiania': 'Goiânia',
        'btn-londrina': 'Londrina',
        'btn-santa-cruz': 'Santa Cruz',
        'btn-interlagos': 'Interlagos',
        'btn-cascavel': 'Cascavel',
        'btn-taruma': 'Tarumã',
        'btn-curvelo': 'Curvelo'
    }

    circuit = circuit_map.get(clicked_button, 'N/A')
    
    # Simular a corrida
    time_data, temp_no_cooling, temp_with_cooling = simulate_race_with_cooling(circuit)

    # Enviar o código para o ESP32
    try:
        url = 'http://192.168.1.9/send_code'  # Endereço IP do ESP
        payload = {'code': esp32_code}
        requests.post(url, data=payload)
    except:
        print(f"Falha ao enviar código para o ESP32 no circuito {circuit}")

    # Gerar conteúdo do arquivo TXT
    txt_content = generate_txt_content(circuit, 4.5)

    # Plotar o gráfico
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_data, y=temp_no_cooling, mode='lines', name='Sem Arrefecimento', line=dict(color='firebrick')))
    fig.add_trace(go.Scatter(x=time_data, y=temp_with_cooling, mode='lines', name='Com Arrefecimento', line=dict(color='royalblue')))
    fig.update_layout(title=f"Simulação de Temperatura - {circuit}", xaxis_title='Tempo (min)', yaxis_title='Temperatura (°C)', template='plotly_dark')

    return True, dcc.Graph(figure=fig), dict(content=txt_content, filename=f'{circuit}.txt')
# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
