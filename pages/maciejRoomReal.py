import dash
from dash import Dash, dcc, html, Input, Output, callback

dash.register_page(__name__)

layout = html.Div([
    html.Div(
        children='Regulator PID dla pokoju Macieja symulator', 
        style={'fontSize': 24, 'fontWeight': 'bold', 'textAlign': 'center'}
    ),
    html.Div(
        'Symulacja pokoju macieja przy założeniach, że:  pokoj jest szescianem i tylko 1 sciana wychodzi na dwor jak faktycznie (reszta scian nie zaklada strat ciepla)'
    ),
    html.Div(id='maciej2_start_output'),
    dcc.Slider(0, 30, 1, value=15, id='slider_start'),
    html.Div(id='maciej2_set_output'),
    dcc.Slider(0, 30, 1, value=25, id='slider_set'),
    html.Div(id='maciej2_outside_output'),
    dcc.Slider(-20, 30, 0.5, value=0, id='slider_outside'),
    html.Div(id='maciej2_time_output'),
    dcc.Slider(0, 420, 10, value=300, id='slider_time'),
    

    html.Div(id='maciej2_output'),
])

@callback(
    Output('maciej2_outside_output', 'children'),
    Input('slider_outside', 'value')
)
def tempOutside(value):
    return f'Temperaura zewnetrzna: {value}'

@callback(
    Output('maciej2_start_output', 'children'),
    Input('slider_start', 'value')
)
def startValue(value):
    return f'Temperaura poczatkowa: {value}'

@callback(
    Output('maciej2_set_output', 'children'),
    Input('slider_set', 'value')
)
def setValue(value):
    return f'Temperaura zadana: {value}'

@callback(
    Output('maciej2_time_output', 'children'),
    Input('slider_time', 'value')
)
def simTime(value):
    return f'Czas symulacji: {value} min'

@callback(
    Output('maciej2_output', 'children'),
    Input('slider_start', 'value'),
    Input('slider_set', 'value'),
    Input('slider_time', 'value'),
    Input('slider_outside', 'value'),

)
def PID(start_value, set_value, sim_time, outside_temp):
    e = []
    U = 0.2  # wspolczynnik strat ciepla
    control_output = []
    temperature = []
    air_density = []
    current_value = start_value
    secondsSimTime = sim_time * 60
    timeStep = 1
    qMax = 1200
    integral = 0
    error = 0
    previous_error = 0
    room_volume = 34
    kp = 40
    ti = 600
    td = 1
    walls = pow(room_volume, 2/3) * 1
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

def airDensity(temperature):
    P = 101325  # pressure in Pa
    R = 287.058  # stala gazowa
    T = temperature + 273.15  # Kelviny
    return P / (R * T)