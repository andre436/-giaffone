# Turbina
Documentação do Código de Simulação
 de Arrefecimento da Turbina
 2. Introdução
 2.1. Contexto do Problema
 Emummundoonde as corridas de caminhões são decididas por frações de segundo, cada
 componente do veículo deve funcionar de maneira otimizada. A turbina, responsável por
 aumentar a eficiência do motor, pode se tornar um ponto crítico quando exposta a temperaturas
 extremas. O superaquecimento pode não apenas reduzir a potência do motor, mas também
 causar danos irreparáveis à turbina.
 2.2. A Importância do Arrefecimento da Turbina
 Oresfriamento da parte fria da turbina é fundamental para manter a eficiência e a longevidade
 do motor. Um sistema de arrefecimento eficaz garante que a turbina funcione em temperaturas
 ideais, maximizando o desempenho e minimizando os riscos de falha.
 2.3. Objetivo da Aplicação
 Esta aplicação tem como objetivo simular o comportamento térmico da parte fria da turbina do
 caminhão sob diferentes condições de arrefecimento, permitindo a visualização das variações
 de temperatura ao longo do tempo.
 2.4. Público-Alvo
 Engenheiros automotivos, mecânicos e entusiastas de corridas que desejam otimizar sistemas
 de arrefecimento e entender melhor o impacto da temperatura no desempenho das turbinas.
 3. Configuração do Ambiente
 3.1. Requisitos de Sistema
 ● Sistema Operacional: Windows, Linux ou macOS
 17
● VersãodoPython: 3.6 ou superior
 ● MemóriaRAM:Mínimo de 4 GB
 ● EspaçoemDisco: Pelo menos 100 MB livres
 3.2. Instalação do Python e Dependências
 1. Instalação do Python: Baixe e instale a versão mais recente do Python a partir do site
 oficial python.org.
 Instalação das Bibliotecas: Abra um terminal e execute o seguinte comando:
 bash
 Copiar código
 pip install dash dash-bootstrap-components plotly numpy
 2.
 4. Estrutura do Código
 4.1. Descrição Geral
 Ocódigo é organizado em seções distintas, facilitando a manutenção e compreensão.
 4.2. Organizando o Código
 Ocódigo é dividido em:
 ● Importações: Carregamento das bibliotecas necessárias.
 ● Definição de Funções: Lógica de simulação e manipulação de dados.
 ● Inicialização do App: Configuração da aplicação Dash.
 ● LayoutdaInterface: Estrutura visual da aplicação.
 ● Gráficos e Callbacks: Criação de gráficos interativos e definições de interação do
 usuário.
 5. Explicação do Código
 5.1. Importações
 python
 Copiar código
 import os
 import dash
 from dash import dcc, html, Input, Output
 import dash_bootstrap_components as dbc
 18
import plotly.graph_objects as go
 import numpy as np
 import threading
 5.2. Funções
 5.2.1. Simulação do Arrefecimento da Turbina
 python
 Copiar código
 def simulate_cooling():
 time_data = np.linspace(0, 90, 180) # Tempo em minutos (1h30)
 # Temperatura sem arrefecimento
 temperature_without_cooling = 700 + 100 * np.sin(2 * np.pi *
 time_data / 20) + np.random.normal(0, 5, len(time_data))
 # Temperatura com arrefecimento
 temperature_with_cooling = temperature_without_cooling- 50 *
 np.sin(2 * np.pi * time_data / 20)- np.random.normal(0, 3,
 len(time_data))
 # Diferença de temperatura
 temperature_difference = temperature_without_cooling
temperature_with_cooling
 return time_data, temperature_without_cooling,
 temperature_with_cooling, temperature_difference
 5.2.2. Envio de Dados para o Arduino
 python
 Copiar código
 def send_temperature_to_arduino(circuit, temperature):
 filepath = r'C:\Users\User\Desktop\python\turbina_temperatura.txt'
 with open(filepath, 'w') as file:
 file.write(f'Circuito: {circuit}\n')
 file.write(f'Temperatura: {temperature}\n')
 def turbine_simulation():
 19
for i in range(180): # 3 minutos = 180 segundos
 time.sleep(1) # Simula 1 segundo
 thread = threading.Thread(target=turbine_simulation)
 thread.start()
 5.3. Inicialização do App Dash
 python
 Copiar código
 app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
 5.4. Layout do App
 python
 Copiar código
 app.layout = dbc.Container([
 dbc.Row([
 dbc.Col(html.H1("Simulação de Arrefecimento da Turbina"),
 className="text-center")
 ]),
 dbc.Row([
 dbc.Col(dcc.Dropdown(
 id='circuit-dropdown',
 options=[
 {'label': 'Circuito A', 'value': 'circuit_a'},
 {'label': 'Circuito B', 'value': 'circuit_b'},
 {'label': 'Circuito C', 'value': 'circuit_c'}
 ],
 value='circuit_a',
 clearable=False
 ), width=6)
 ]),
 dbc.Row([
 dbc.Col(dcc.Graph(id='temperature-graph'), width=12)
 ])
 ])
 20
5.5. Gráficos
 python
 Copiar código
 def create_temperature_graph(time_data, temp_without, temp_with,
 temp_diff):
 fig_temp = go.Figure()
 fig_temp.add_trace(go.Scatter(x=time_data, y=temp_without,
 mode='lines', name='Sem Arrefecimento', line=dict(color='red')))
 fig_temp.add_trace(go.Scatter(x=time_data, y=temp_with,
 mode='lines', name='Com Arrefecimento', line=dict(color='blue')))
 fig_temp.update_layout(title='Temperatura da Turbina ao Longo do
 Tempo', xaxis_title='Tempo (minutos)', yaxis_title='Temperatura (°C)')
 return fig_temp
 5.6. Callbacks
 python
 Copiar código
 @app.callback(Output('temperature-graph', 'figure'),
 Input('circuit-dropdown', 'value'))
 def update_graph(selected_circuit):
 time_data, temp_without, temp_with, temp_diff = simulate_cooling()
 fig_temp = create_temperature_graph(time_data, temp_without,
 temp_with, temp_diff)
 return fig_temp
 6. Executando o Código
 6.1. Como Rodar o Aplicativo
 Salve o código em um arquivo Python (por exemplo, app.py) e execute o seguinte comando:
 bash
 Copiar código
 python app.py
 A aplicação estará disponível em http://127.0.0.1:8050/.
 21
6.2. Interação do Usuário
 Os usuários podem selecionar diferentes circuitos usando um menu dropdown, e os gráficos de
 temperatura serão atualizados automaticamente.
 7. Resultados e Análise
 7.1. Tabela Comparativa
 A tabela a seguir apresenta uma comparação entre diferentes sistemas de refrigeração para a
 parte fria da turbina, considerando suas capacidades e eficiência:
 Sistema de
 Refrigeração
 Água
 Ar a Pressão
 Refrigerante a
 Gás
 Combinação
 de Sistemas
 Temperatura de
 Funcionamento
 (°C)
 20- 80
 0- 50-20 a 50
 0- 80
 Eficiência
 Energética
 7.2. Discussão sobre os Gráficos
 Vantagens
 Alta
 Média
 Muito Alta
 Alta
 Fácil de
 implementar,
 baixo custo
 Resfriamento
 rápido
 Excelente
 controle de
 temperatura
 Maior eficiência
 ao unir diferentes
 métodos
 Desvantagens
 Limitação na
 faixa de
 temperatura
 Requer
 compressores e
 manutenção
 Alto custo e
 complexidade no
 sistema
 Complexidade no
 design e
 instalação
 Os gráficos gerados pela aplicação mostram a comparação entre a temperatura da turbina com
 e sem arrefecimento, permitindo uma análise visual do impacto do sistema de resfriamento.
 7.3. Interpretação dos Dados
 Os dados obtidos da simulação mostram que o sistema de arrefecimento pode reduzir
 significativamente a temperatura da turbina, melhorando assim o desempenho geral do
 caminhão.
 22
8. Conclusão
 A simulação do arrefecimento da parte fria da turbina é uma ferramenta valiosa para entender
 como diferentes métodos de resfriamento afetam o desempenho do motor em situações de
 corrida. Os resultados sugerem que um sistema de resfriamento bem projetado pode não
 apenas aumentar a eficiência, mas também prolongar a vida útil dos componentes do motor.
 9. Referências
 ● Python.org
 ● Artigos sobre arrefecimento de turbinas e eficiência de motore
