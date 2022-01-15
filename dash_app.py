import dash
from dash import dcc
from dash import html
from dash.dcc.Interval import Interval
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_daq as daq
import numpy as np
import sqlite3
import time

from storage import convert_data_to_df, see_data



app = dash.Dash()

def legs_plot(id=1, secs = 10):
    
    pd = get_user_data_by_secs(id, secs)
    datetime = np.array(pd["datetimes"])
    values = np.array(pd["values"])
    anomalies = np.array(pd["anomalies"])
    sensor_list = ["L0", "L1", "L2", "R0", "R1", "R2"]

    fig = go.Figure()
    for idx, sensor in enumerate(sensor_list):
        fig.add_trace(go.Scatter(x=datetime, y=values[:,idx], name=sensor, legendgrouptitle_text="Sensors", legendgroup="sensors"))
        fig.add_trace(go.Scatter(x=datetime, y=values[:,idx][anomalies[:,idx] == "True"], name=sensor, line=dict(color="#FF0000"), legendgrouptitle_text="Anomalies", legendgroup="anomalies"))

    return fig

def create_layout():
    app.layout = html.Div(id = 'parent', children = [
        html.H1(id = 'H1', children = 'Tesla visualizer', style = {'textAlign': 'center',\
            'marginTop': 40, 'marginBottom': 40}), \
        dcc.Dropdown(
            id='person-dropdown',
            options=[
                {'label': 'Janek Grzegorczyk', 'value': 1},
                {'label': 'Elbieta Kochalska', 'value': 2},
                {'label': 'Albert Lisowski', 'value': 3},
                {'label': 'Ewelina Nosowska', 'value': 4},
                {'label': 'Piotr Fokalski', 'value': 5},
                {'label': 'Bartosz Moskalski', 'value': 6}
            ],
            value=1),\
        html.Div(children = 'Select number of seconds to show'), \
        daq.NumericInput(
            id='secs-num',
            min=0,
            max=600,
            value=10,
            size=120
        ), \
        dcc.Graph(id = 'the_plot', figure = legs_plot(1, 10)), \
        dcc.Interval(id = 'interval', interval = 1000, n_intervals = 0)
    ])

@app.callback(
    Output(component_id='the_plot', component_property='figure'),
    Input(component_id='interval', component_property='n_intervals'),
    Input('person-dropdown', 'value'),
    Input('secs-num', 'value'))
def graph_update(n_intervals, person_value, secs):
    print(n_intervals)
    return legs_plot(person_value, secs)


def get_user_data_by_secs(patient_id, secs):
    _conn = sqlite3.connect('patients.db')
    c = _conn.cursor()
    ts = time.time()
    c.execute("SELECT * FROM USERS WHERE patient_id=? AND end_time>?", (patient_id,ts-secs,))
    print(f"\n\nGot user with id: {patient_id} from last {secs} seconds: \n\n")
    users = c.fetchall()
    see_data(users)
    return convert_data_to_df(users)
