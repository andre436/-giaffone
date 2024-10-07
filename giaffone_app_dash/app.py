import os
import dash
from dash import dcc, html, Input, Output, State, callback_context
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

# Cálculos de Transferência de Calor
def calculate_heat_transfer():
    # Dados do sistema
    T_in = 550  # °C
    T_intercooler_out = 120  # °C
    T_new_system_out = 80  # °C
    intercooler_efficiency = 0.7
    new_system_efficiency = 0.9

    # Variação de temperatura
    delta_T_intercooler = T_in - T_intercooler_out  # °C
    delta_T_new_system = T_in - T_new_system_out  # °C

    # Emissões de CO₂
    emissions_current = 550  # g/km
    emissions_reduction = 0.05  # 5%
    emissions_new_system = emissions_current * (1 - emissions_reduction)  # g/km

    return delta_T_intercooler, delta_T_new_system, emissions_current, emissions_new_system

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
        return is_open, dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'close-modal':
        return False, dash.no_update

    # Get the circuit name
    circuit = triggered_id.replace('btn-', '').replace('-', ' ').title()
    if circuit == 'Goiania':
        circuit = 'Goiânia'
    elif circuit == 'Taruma':
        circuit = 'Tarumã'

    # Simular novos dados de temperatura com base no circuito selecionado
    time_data, temp_without, temp_with = simulate_race_with_cooling(circuit)

    # Gráficos de temperatura
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=time_data, y=temp_without, mode='lines+markers', name='Sem Arrefecimento', 
                                  line=dict(color='red', width=2), fill='tozeroy'))
    fig_temp.add_trace(go.Scatter(x=time_data, y=temp_with, mode='lines+markers', name='Com Arrefecimento', 
                                  line=dict(color='cyan', width=2), fill='tozeroy'))
    fig_temp.update_layout(
        title=f'Análise da Temperatura da Turbina - {circuit}',
        xaxis_title='Tempo (minutos)',
        yaxis_title='Temperatura (°C)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        font_size=16,
        showlegend=True
    )

    # Texto explicativo para o gráfico de temperatura
    temp_explanation = html.P("Esse gráfico mostra a variação de temperatura da turbina ao longo do tempo. Com o sistema de arrefecimento, observa-se uma redução significativa na temperatura média, "
                              "permitindo uma operação mais eficiente e menos sujeita a falhas térmicas. A diferença de temperatura é calculada usando os valores de base definidos para cada circuito, "
                              "com simulação de variações temporais baseadas em senos.")

    # Cálculos de Transferência de Calor
    delta_T_intercooler, delta_T_new_system, emissions_current, emissions_new_system = calculate_heat_transfer()

    # Gráficos de Transferência de Calor
    fig_heat_transfer = go.Figure()
    fig_heat_transfer.add_trace(go.Bar(
        x=['Intercooler Atual', 'Novo Sistema'],
        y=[delta_T_intercooler, delta_T_new_system],
        name='Variação de Temperatura',
        marker_color=['blue', 'green']
    ))
    fig_heat_transfer.update_layout(
        title='Transferência de Calor',
        xaxis_title='Sistema',
        yaxis_title='Variação de Temperatura (°C)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        font_size=16,
        showlegend=False
    )

    # Texto explicativo para o gráfico de Transferência de Calor
    heat_transfer_explanation = html.P("A transferência de calor é um fator crítico no desempenho da turbina. O gráfico compara a eficiência entre o sistema atual (Intercooler) e o novo sistema de arrefecimento proposto. "
                                       "A diferença de temperatura foi calculada usando a fórmula de variação de temperatura com base na eficiência de cada sistema. O novo sistema de arrefecimento apresenta uma eficiência superior, "
                                       "reduzindo a temperatura de saída e potencialmente aumentando a durabilidade da turbina.")

    # Gráficos de Emissões de CO2
    fig_emissions = go.Figure()
    fig_emissions.add_trace(go.Bar(
        x=['Sistema Atual', 'Novo Sistema'],
        y=[emissions_current, emissions_new_system],
        name='Emissões de CO2',
        marker_color=['darkred', 'darkgreen']
    ))
    fig_emissions.update_layout(
        title='Redução das Emissões de CO2',
        xaxis_title='Sistema',
        yaxis_title='Emissões de CO2 (g/km)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        font_size=16,
        showlegend=False
    )

    # Texto explicativo para o gráfico de Emissões
    emissions_explanation = html.P("O gráfico demonstra o impacto do novo sistema na redução das emissões de CO2. A redução é estimada em 5%, comparando as emissões atuais com as do novo sistema. "
                                   "Esses valores são calculados com base nas emissões por km do sistema atual e na eficiência de arrefecimento do novo sistema, que promove uma combustão mais limpa e menos poluente.")

    # Organização dos gráficos e explicações no layout
    return True, [
        dcc.Graph(figure=fig_temp),
        temp_explanation,
        dcc.Graph(figure=fig_heat_transfer),
        heat_transfer_explanation,
        dcc.Graph(figure=fig_emissions),
        emissions_explanation,
    ]


# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
