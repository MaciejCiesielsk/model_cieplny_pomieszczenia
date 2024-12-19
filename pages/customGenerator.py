import dash
from dash import Dash, dcc, html, Input, Output, callback

dash.register_page(__name__)

layout = html.Div([
    html.Div(children='Regulator PID dla modelu ogrzewania pomieszczenia', style={'fontSize': 24, 'fontWeight': 'bold', 'textAlign': 'center'}),
    html.Div('Tutaj zakładamy, że pomieszczenie jest wiszącym sześcianem z dostępem do dworu z każdej strony. Mocą grzejnika można sterować.'),

    html.Div(children='Objetosc pomieszczenia (m³)'),
    dcc.Input(id='room_volume', type='number', value=32, step=1),

    html.Div(children='Maksymalna moc grzałki (W)'),
    dcc.Input(id='heater_power', type='number', value=1200, step=10),

    html.Div(id='slider_start_output'),
    dcc.Slider(0, 30, 1, value=15, id='slider_start'),

    html.Div(id='slider_set_output'),
    dcc.Slider(0, 30, 1, value=25, id='slider_set'),

    html.Div(id='slider_outside_output'),
    dcc.Slider(-20, 30, 0.5, value=0, id='slider_outside'),

    html.Div(id='slider_time_output'),
    dcc.Slider(0, 420, 10, value=300, id='slider_time'),

    html.Div("Blokada na blad"),
    html.Div(id='error_output'),
    dcc.Input(id='error_input', type='number', value=2, step=0.1),

    html.Div("Kp"),
    html.Div(id='kp_output'),
    dcc.Input(id='kp_input', type='number', value=8.2, step=0.1),

    html.Div("Ti"),
    html.Div(id='ti_output'),
    dcc.Input(id='ti_input', type='number', value=200, step=0.1),

    html.Div("Td"),
    html.Div(id='td_output'),
    dcc.Input(id='td_input', type='number', value=1, step=0.1),

    html.Div(id='e_output'),
])

@callback(
    Output('slider_outside_output', 'children'),
    Input('slider_outside', 'value')
)
def tempOutside(value):
    return f'Temperaura zewnetrzna: {value}'

@callback(
    Output('slider_start_output', 'children'),
    Input('slider_start', 'value')
)
def startValue(value):
    return f'Temperaura poczatkowa: {value}'

@callback(
    Output('slider_set_output', 'children'),
    Input('slider_set', 'value')
)
def setValue(value):
    return f'Temperaura zadana: {value}'

@callback(
    Output('slider_time_output', 'children'),
    Input('slider_time', 'value')
)
def simTime(value):
    return f'Czas symulacji: {value} min'

@callback(
    Output('e_output', 'children'),
    Input('slider_start', 'value'),
    Input('slider_set', 'value'),
    Input('slider_time', 'value'),
    Input('kp_input', 'value'),
    Input('ti_input', 'value'),
    Input('td_input', 'value'),
    Input('room_volume', 'value'),
    Input('heater_power', 'value'),
    Input('slider_outside', 'value'),
    Input('error_input', 'value'),
)
def PID(start_value, set_value, sim_time, kp, ti, td, room_volume, heater_power, outside_temp, offset):
    if None in [start_value, set_value, sim_time, kp, ti, td, room_volume, heater_power, outside_temp]:
        return html.Div("Error: All input values must be provided and not None.")
    e = []
    U = 0.2 # wspolczynnik strat ciepla
    control_output = []
    temperature = []
    air_density = []
    current_value = start_value
    secondsSimTime = sim_time * 60
    timeStep = 1
    qMax = heater_power
    integral = 0
    error = 0
    previous_error = 0
    walls = pow(room_volume, 2/3) * 6
    cp = 1005 # srednia pojemnosc cieplna powietrza
    for _ in range(secondsSimTime):
        m = airDencity(current_value) * room_volume
        air_density.append(m)
        temperature.append(current_value)
        qLoss = U * walls * (current_value - outside_temp)
        error = set_value - current_value
        error = max(min(error, offset), -offset)  # maksymalny blad 2 stopnie, zeby nie lecialo do 30 stopni
        e.append(error)

        proportional = error
        integral += error * timeStep
        derivative = (error - previous_error) / timeStep

        pidValue = kp * (proportional + (1/ti) * integral + td * derivative)
        pidValue = max(min(pidValue, qMax), 0)

        control_output.append(pidValue)
        current_value += (pidValue - qLoss) / (m * cp)
        previous_error = error

    return html.Div([
        dcc.Graph(
            figure={
                'data': [
                    {'x': [i / 60 for i in range(len(temperature))], 'y': temperature, 'type': 'line', 'name': 'Temperatura'},
                    {'x': [i / 60 for i in range(len(temperature))], 'y': [set_value] * len(temperature), 'type': 'line', 'name': 'Temperatura zadana', 'line': {'dash': 'dash'}},
                ],
                'layout': {
                    'title': 'Wykres temperatury w czasie',
                    'xaxis': {'title': 'Czas (min)'},
                    'yaxis': {'title': 'Temperatura (°C)'},
                }
            }
        ),
        dcc.Graph(
            figure={
                'data': [
                    {'x': [i / 60 for i in range(len(control_output))], 'y': control_output, 'type': 'line', 'name': 'Moc grzałki'},
                ],
                'layout': {
                    'title': 'Wykres mocy grzałki w czasie',
                    'xaxis': {'title': 'Czas (min)'},
                    'yaxis': {'title': 'Moc (W)'},
                }
            }
        ),
        dcc.Graph(
            figure={
                'data': [
                    {'x': [i / 60 for i in range(len(e))], 'y': e, 'type': 'line', 'name': 'Błąd'},
                ],
                'layout': {
                    'title': 'Wykres błędu w czasie',
                    'xaxis': {'title': 'Czas (min)'},
                    'yaxis': {'title': 'Błąd (°C)'},
                }
            }
        ),
    ])

def airDencity(temperature):
    P = 101325 # pressure in Pa
    R = 287.058 # stala gazowa
    T = temperature + 273.15 # Kelviny
    return P / (R * T)
