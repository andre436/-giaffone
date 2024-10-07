import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

# Inicializando o app Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Layout do app
app.layout = html.Div([
    dbc.Container([
        html.H1('Simulação de Resfriamento da Turbina - Fórmula Truck', style={'textAlign': 'center'}),
        
        # Seleção do circuito
        html.Label('Selecione o Circuito:'),
        dcc.Dropdown(
            id='circuit-dropdown',
            options=[
                {'label': 'Campo Grande/MS - 17/03', 'value': 'Campo Grande/MS - 17/03'},
                {'label': 'Goiânia/GO - 14/04', 'value': 'Goiânia/GO - 14/04'},
                {'label': 'Londrina/PR - 12/05', 'value': 'Londrina/PR - 12/05'},
                {'label': 'Santa Cruz (Potenza/MG) - 16/06', 'value': 'Santa Cruz (Potenza/MG) - 16/06'},
                {'label': 'Interlagos/SP - 04/08', 'value': 'Interlagos/SP - 04/08'},
                {'label': 'Cascavel/PR - 01/09', 'value': 'Cascavel/PR - 01/09'},
                {'label': 'Tarumã/RS - 13/10', 'value': 'Tarumã/RS - 13/10'},
                {'label': 'Curvelo/MG - 17/11', 'value': 'Curvelo/MG - 17/11'},
                {'label': 'Goiânia/GO - 08/12', 'value': 'Goiânia/GO - 08/12'}
            ],
            value='Campo Grande/MS - 17/03',
            style={'margin-bottom': '20px'}
        ),
        
        # Botão para gerar gráficos
        dbc.Button('Gerar Gráficos', id='generate-graphs-btn', color='primary', block=True),
        
        # Modal para exibir os gráficos
        dbc.Modal(
            [
                dbc.ModalHeader('Análise dos Dados'),
                dbc.ModalBody(id='graphs-modal-content')
            ],
            id='graphs-modal',
            size='lg'
        )
    ])
])

# Função para gerar os gráficos com base no circuito selecionado
@app.callback(
    [dash.dependencies.Output('graphs-modal', 'is_open'),
     dash.dependencies.Output('graphs-modal-content', 'children')],
    [dash.dependencies.Input('generate-graphs-btn', 'n_clicks')],
    [dash.dependencies.State('circuit-dropdown', 'value')]
)
def generate_graphs(n_clicks, circuit):
    if n_clicks is None:
        return False, None

    # Dados simulados de temperatura e eficiência
    time_data = list(range(0, 181, 15))  # 0 a 180 minutos (3 horas)
    temp_without = [180, 175, 170, 165, 160, 155, 150, 145, 140, 135, 130, 125, 120]  # Sem arrefecimento
    temp_with = [180, 170, 160, 150, 140, 130, 120, 110, 105, 100, 95, 90, 85]  # Com arrefecimento
    efficiency_without = [80, 78, 75, 73, 70, 68, 65, 63, 60, 58, 55, 52, 50]  # Sem arrefecimento
    efficiency_with = [80, 82, 85, 87, 90, 92, 95, 97, 100, 102, 105, 108, 110]  # Com arrefecimento
    rpm = 3500  # RPM fixo para simplificar

    # Gráfico de Temperatura
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=time_data, y=temp_without, mode='lines+markers', name='Sem Arrefecimento',
                                  line=dict(color='red', width=2)))
    fig_temp.add_trace(go.Scatter(x=time_data, y=temp_with, mode='lines+markers', name='Com Arrefecimento',
                                  line=dict(color='blue', width=2), fill='tozeroy'))
    fig_temp.update_layout(title=f'Temperatura ao Longo do Tempo - {circuit}',
                           xaxis_title='Tempo (minutos)', yaxis_title='Temperatura (°C)',
                           template='plotly_dark')

    # Gráfico de Eficiência
    fig_efficiency = go.Figure()
    fig_efficiency.add_trace(go.Scatter(x=time_data, y=efficiency_without, mode='lines+markers',
                                        name='Eficiência Sem Arrefecimento', line=dict(color='orange', width=2)))
    fig_efficiency.add_trace(go.Scatter(x=time_data, y=efficiency_with, mode='lines+markers',
                                        name='Eficiência Com Arrefecimento', line=dict(color='green', width=2)))
    fig_efficiency.update_layout(title=f'Eficiência ao Longo do Tempo - {circuit}',
                                 xaxis_title='Tempo (minutos)', yaxis_title='Eficiência (%)',
                                 template='plotly_dark')

    # Gráfico de Comparação de RPM
    fig_rpm = go.Figure()
    fig_rpm.add_trace(go.Bar(x=[circuit], y=[rpm], name='RPM', marker_color='purple'))
    fig_rpm.update_layout(title='Comparação de RPM por Circuito',
                          xaxis_title='Circuito', yaxis_title='RPM',
                          template='plotly_dark')

    # Conteúdo do modal com todos os gráficos
    modal_content = dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_temp), width=12),
        dbc.Col(dcc.Graph(figure=fig_efficiency), width=12),
        dbc.Col(dcc.Graph(figure=fig_rpm), width=12),
    ])

    return True, modal_content

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
