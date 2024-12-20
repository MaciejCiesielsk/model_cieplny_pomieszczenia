import dash
from dash import dcc, html, Input, Output, callback, State

dash.register_page(__name__)

layout = html.Div([
    html.Div(
        children='Regulator PID dla pokoju Macieja symulator', 
        style={'fontSize': 24, 'fontWeight': 'bold', 'textAlign': 'center'}
    ),
    html.Div(
        'Symulacja pokoju macieja przy założeniach, że:  pokój jest sześcianem wiszącym w powietrzu z dostępem do dworu z każdej strony, a grzejnik ma moc 100W na m2'
    ),
    html.Div('Czas próbkowania: 1s'),
    html.Div(id='maciej_start_output'),
    dcc.Slider(0, 30, 1, value=15, id='slider_start'),
    html.Div(id='maciej_set_output'),
    dcc.Slider(0, 30, 1, value=25, id='slider_set'),
    html.Div(id='maciej_outside_output'),
    dcc.Slider(-20, 30, 1, value=0, id='slider_outside'),

    html.Button('Start Symulacji', id='start_button', n_clicks=0),
    html.Button('Reset', id='reset_button', n_clicks=0),

    html.Div(id='maciej_output'),

    dcc.Graph(id='temperature_graph1', figure={'data': [], 'layout': {'title': 'Wykres temperatury w czasie', 'xaxis': {'title': 'Czas (min)'}, 'yaxis': {'title': 'Temperatura (°C)'}}}),
    dcc.Graph(id='heater_power_graph1', figure={'data': [], 'layout': {'title': 'Wykres mocy grzałki w czasie', 'xaxis': {'title': 'Czas (min)'}, 'yaxis': {'title': 'Moc (W)'}}}),
    dcc.Graph(id='error_graph1', figure={'data': [], 'layout': {'title': 'Wykres błędu w czasie', 'xaxis': {'title': 'Czas (min)'}, 'yaxis': {'title': 'Błąd (°C)'}}}),
    dcc.Store(id='previous_results1', data={'temperature': [], 'control_output': [], 'error': []})
])

@callback(
    Output('maciej_outside_output', 'children'),
    Input('slider_outside', 'value')
)
def tempOutside(value):
    return f'Temperaura zewnetrzna: {value}'

@callback(
    Output('maciej_start_output', 'children'),
    Input('slider_start', 'value')
)
def startValue(value):
    return f'Temperaura poczatkowa: {value}'

@callback(
    Output('maciej_set_output', 'children'),
    Input('slider_set', 'value')
)
def setValue(value):
    return f'Temperaura zadana: {value}'

@callback(
    Output('maciej_output', 'children'),
    Output('temperature_graph1', 'figure'),
    Output('heater_power_graph1', 'figure'),
    Output('error_graph1', 'figure'),
    Output('previous_results1', 'data'),
    Input('start_button', 'n_clicks'),
    Input('reset_button', 'n_clicks'),
    State('slider_start', 'value'),
    State('slider_set', 'value'),
    State('slider_outside', 'value'),
    State('previous_results1', 'data')
)
def PID(start_clicks, reset_clicks, start_value, set_value, outside_temp, previous_results):
    if dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'reset_button':
        return html.Div(), {
            'data': [], 
            'layout': {'title': 'Wykres temperatury w czasie', 'xaxis': {'title': 'Czas (min)'}, 'yaxis': {'title': 'Temperatura (°C)'}}}, {'data': [], 'layout': {'title': 'Wykres mocy grzałki w czasie', 'xaxis': {'title': 'Czas (min)'}, 'yaxis': {'title': 'Moc (W)'}}}, {'data': [], 'layout': {'title': 'Wykres błędu w czasie', 'xaxis': {'title': 'Czas (min)'}, 'yaxis': {'title': 'Błąd (°C)'}}}, {'temperature': [], 'control_output': [], 'error': []}

    if not dash.callback_context.triggered or dash.callback_context.triggered[0]['prop_id'].split('.')[0] != 'start_button':
        return dash.no_update

    e = []
    U = 0.2  # wspolczynnik strat ciepla
    control_output = []
    temperature = []
    air_density = []
    current_value = start_value
    secondsSimTime = 300 * 60
    timeStep = 1
    qMax = 1200
    integral = 0
    error = 0
    previous_error = 0
    room_volume = 34
    kp = 80
    ti = 450
    td = 100
    walls = pow(room_volume, 2/3) * 6
    cp = 1005  # srednia pojemnosc cieplna powietrza
    for _ in range(secondsSimTime):
        m = airDensity(current_value) * room_volume
        air_density.append(m)
        temperature.append(current_value)
        qLoss = U * walls * (current_value - outside_temp)
        error = set_value - current_value
        error = max(min(error, 2), -2)  # maksymalny blad 2 stopnie, zeby nie lecialo do 30 stopni
        e.append(error)

        proportional = error
        integral += error * timeStep
        derivative = (error - previous_error) / timeStep

        pidValue = kp * proportional + (kp/ti) * integral + kp * td * derivative
        pidValue = max(min(pidValue, qMax), 0)
        
        control_output.append(pidValue)
        current_value += (pidValue - qLoss) / (m * cp)
        previous_error = error
        
    temperature_fig = {
        'data': [
            {'x': [i / 60 for i in range(len(temperature))], 'y': temperature, 'type': 'line', 'name': 'Temperatura'},
            {'x': [i / 60 for i in range(len(temperature))], 'y': [set_value] * len(temperature), 'type': 'line', 'name': 'Temperatura zadana', 'line': {'dash': 'dash'}},
            {'x': [i / 60 for i in range(len(previous_results['temperature']))], 'y': previous_results['temperature'], 'type': 'line', 'name': 'Poprzednia Temperatura', 'line': {'dash': 'dash', 'color': 'gray'}}
        ],
        'layout': {
            'title': 'Wykres temperatury w czasie',
            'xaxis': {'title': 'Czas (min)'},
            'yaxis': {'title': 'Temperatura (°C)'},
        }
    }

    heater_power_fig = {
        'data': [
            {'x': [i / 60 for i in range(len(control_output))], 'y': control_output, 'type': 'line', 'name': 'Moc grzałki'},
            {'x': [i / 60 for i in range(len(previous_results['control_output']))], 'y': previous_results['control_output'], 'type': 'line', 'name': 'Poprzednia Moc grzałki', 'line': {'dash': 'dash', 'color': 'gray'}}
        ],
        'layout': {
            'title': 'Wykres mocy grzałki w czasie',
            'xaxis': {'title': 'Czas (min)'},
            'yaxis': {'title': 'Moc (W)'},
        }
    }

    error_fig = {
        'data': [
            {'x': [i / 60 for i in range(len(e))], 'y': e, 'type': 'line', 'name': 'Błąd'},
            {'x': [i / 60 for i in range(len(previous_results['error']))], 'y': previous_results['error'], 'type': 'line', 'name': 'Poprzedni Błąd', 'line': {'dash': 'dash', 'color': 'gray'}}
        ],
        'layout': {
            'title': 'Wykres błędu w czasie',
            'xaxis': {'title': 'Czas (min)'},
            'yaxis': {'title': 'Błąd (°C)'},
        }
    }

    new_results = {
        'temperature': temperature,
        'control_output': control_output,
        'error': e
    }

    return html.Div(), temperature_fig, heater_power_fig, error_fig, new_results


def airDensity(temperature):
    P = 101325  # pressure in Pa
    R = 287.058  # stala gazowa
    T = temperature + 273.15  # Kelviny
    return P / (R * T)
