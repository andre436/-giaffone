import os 
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np

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
        dbc.ModalHeader("Gráficos da Corrida", style={'backgroundColor': 'black', 'color': 'white'}),
        dbc.ModalBody(
            dbc.Container(id='modal-content', fluid=True),
            style={'backgroundColor': 'black', 'color': 'white'}  # Fundo e texto do corpo do modal
        ),
        dbc.ModalFooter(
            dbc.Button("Fechar", id='close-modal', className='ml-auto', style={'backgroundColor': 'black', 'color': 'white'})
        ),
    ], id='modal', size='lg', style={'backgroundColor': 'black'}),  # Fundo preto no modal inteiro

], fluid=True, style={'height': '100vh', 'width': '100vw', 'padding': '0', 'margin': '0', 'backgroundColor': 'black'})

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
        plot_bgcolor='black',  # Fundo preto do gráfico
        paper_bgcolor='black',  # Fundo preto do paper
        font_color='white',
        font_size=16,
        showlegend=True
    )

    # Cálculos de Transferência de Calor
    delta_T_intercooler, delta_T_new_system, emissions_current, emissions_new_system = calculate_heat_transfer()

    # Gráficos de Transferência de Calor
    fig_heat_transfer = go.Figure()
    fig_heat_transfer.add_trace(go.Bar(x=['Intercooler Atual', 'Novo Sistema de Resfriamento'],
                                       y=[delta_T_intercooler, delta_T_new_system],
                                       marker_color=['red', 'cyan'], name='Redução de Temperatura (°C)'))
    fig_heat_transfer.update_layout(
        title='Redução de Temperatura com Sistemas de Resfriamento',
        xaxis_title='Sistema',
        yaxis_title='Redução de Temperatura (°C)',
        plot_bgcolor='black',  # Fundo preto do gráfico
        paper_bgcolor='black',  # Fundo preto do paper
        font_color='white',
        font_size=16,
        showlegend=True
    )

    # Gráficos de Emissões de CO₂
    fig_emissions = go.Figure()
    fig_emissions.add_trace(go.Bar(x=['Sistema Atual', 'Sistema Adicional'],
                                   y=[emissions_current, emissions_new_system],
                                   marker_color=['red', 'cyan'], name='Emissões (g/km)'))
    fig_emissions.update_layout(
        title='Emissões de CO₂ com e sem Sistema de Resfriamento',
        xaxis_title='Sistema',
        yaxis_title='Emissões (g/km)',
        plot_bgcolor='black',  # Fundo preto do gráfico
        paper_bgcolor='black',  # Fundo preto do paper
        font_color='white',
        font_size=16,
        showlegend=True
    )

    # Texto explicativo
    explanatory_text = html.Div([
        html.P(
            """
            A melhoria no sistema de arrefecimento contribui significativamente para reduzir a temperatura da turbina.
            Com o novo sistema, a eficiência aumentada reduz a temperatura de saída para 80°C, em comparação com os 120°C 
            do sistema intercooler atual. Isso é alcançado devido à maior eficiência do novo sistema (90% contra 70% do intercooler),
            resultando em uma variação de temperatura maior. Além disso, a redução de emissões de CO₂ é estimada em 5% 
            para o novo sistema, reduzindo de 550 g/km para aproximadamente 522,5 g/km.
            """
        ),
        html.P(
            """
            O cálculo da variação de temperatura é baseado na fórmula:
            ΔT = T_in - T_out, onde:
            T_in = 550°C, T_out_intercooler = 120°C, e T_out_novo_sistema = 80°C.
            """
        )
    ], style={'color': 'white', 'font-size': '16px'})

    # Conteúdo do modal com gráficos e texto explicativo
    modal_content = html.Div([
        dcc.Graph(figure=fig_temp),
        dcc.Graph(figure=fig_heat_transfer),
        dcc.Graph(figure=fig_emissions),
        explanatory_text  # Adicionando o texto explicativo
    ])

    return True, modal_content

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
