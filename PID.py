from dash import Dash, dcc, html, Input, Output, callback

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    html.Div(children='Regulator PID dla modelu ogrzewania pomieszczenia', style={'fontSize': 24, 'fontWeight': 'bold', 'textAlign': 'center'}),
    

    html.Div(children='Powierzchnia ścian pomieszczenia (m2)'),
    dcc.Input(id='room_volume', type='number', value=0, step=1),

    html.Div(children='Maksymalna moc grzałki (W)'),
    dcc.Input(id='heater_power', type='number', value=0, step=10),

    html.Div(id='slider_start_output'),
    dcc.Slider(0,30,1, value=15, id='slider_start'),

    html.Div(id='slider_set_output'),
    dcc.Slider(0,30,1, value=15, id='slider_set'),

    html.Div(id='slider_outside_output'),
    dcc.Slider(-20,30,0.5, value=0, id='slider_outside'),
    
    html.Div(id='slider_time_output'),
    dcc.Slider(0,30,1, value=1, id='slider_time'),
    
    html.Div("Kp"),
    html.Div(id='kp_output'),
    dcc.Input(id='kp_input', type='number', value=1, step=0.1),

    html.Div("Ti"),
    html.Div(id='ti_output'),
    dcc.Input(id='ti_input', type='number', value=1, step=0.1),

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
    return (f'Temperaura zewnetrzna: {value}')


@callback(
    Output('slider_start_output', 'children'),
    Input('slider_start', 'value')
)
def startValue(value):
    return (f'Temperaura poczatkowa: {value}')

@callback(
    Output('slider_set_output', 'children'),
    Input('slider_set', 'value')
)
def setValue(value):
    return (f'Temperaura zadana: {value}')

@callback(
    Output('slider_time_output', 'children'),
    Input('slider_time', 'value')
)
def simTime(value):
    return (f'Czas symulacji: {value} min')


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
    Input('slider_outside', 'value')
)
def PID(start_value, set_value, sim_time, kp, ti, td, room_volume, heater_power, outside_temp):
    e = []
    U = 0.3 # wspolczynnik strat ciepla
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
    cp = 1005 # srednia pojemnosc cieplna powietrza
    for _ in range(secondsSimTime):
        m = airDencity(current_value)
        air_density.append(m)
        temperature.append(current_value)
        qLoss = U * room_volume * (current_value - outside_temp)
        error = set_value - current_value
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
                    {'x': list(range(len(temperature))), 'y': temperature, 'type': 'line', 'name': 'Temperatura'},
                    {'x': list(range(len(temperature))), 'y': [set_value] * len(temperature), 'type': 'line', 'name': 'Temperatura zadana', 'line': {'dash': 'dash'}},
                ],
                'layout': {
                    'title': 'Wykres temperatury w czasie',
                    'xaxis': {'title': 'Czas (s)'},
                    'yaxis': {'title': 'Temperatura (°C)'},
                }
            }
        ),
        dcc.Graph(
            figure={
                'data': [
                    {'x': list(range(len(air_density))), 'y': air_density, 'type': 'line', 'name': 'Gęstość powietrza'},
                ],
                'layout': {
                    'title': 'Wykres gęstości powietrza w czasie',
                    'xaxis': {'title': 'Czas (s)'},
                    'yaxis': {'title': 'Gęstość powietrza (kg/m³)'},
                }
            }
        )
    ])

def airDencity(temperature):
    P = 101325
    R = 287.058
    T = temperature + 273.15
    return P/(R*T)

if __name__ == '__main__':
    app.run(debug=True)
