# In[]:
# Import required libraries
import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
from dash_daq import StopButton, Indicator, DarkThemeProvider, ToggleSwitch
import plotly.graph_objs as go

from dash_daq_drivers.kurtjlesker_instruments import MGC4000

# line colors
LINE_COLORS = ['#19d3f3', '#e763fa', '#00cc96', '#EF553B']

# font and background colors associated with each themes
BKG_COLOR = {'dark': '#2a3f5f', 'light': '#F3F6FA'}
GRID_COLOR = {'dark': 'white', 'light': '#C8D4E3'}
TEXT_COLOR = {'dark': 'white', 'light': '#506784'}

# create a pressure gauge
PRESSURE_GAUGE = MGC4000(mock=True)

# set the gauge inside the lab's instrument rack
INSTRUMENT_RACK = [PRESSURE_GAUGE]


def grey_out(style_dict, pwr_status):
    if style_dict is None:
        answer = {}
    else:
        answer = style_dict
    if pwr_status:
        answer['opacity'] = 1
    else:
        answer['opacity'] = 0.3
    return answer


def is_instrument_port(port_name):
    """test if a string can be a com of gpib port"""
    answer = False
    if isinstance(port_name, str):
        ports = ['COM', 'com', 'GPIB0::', 'gpib0::']
        for port in ports:
            if port in port_name:
                answer = not (port == port_name)
    return answer


# Create controls using a function
def generate_lab_layout(instr_list, theme='light'):
    """generate the layout of the app from a list of instruments"""

    # the rack contains the control components of the instrument(s) interface
    rack = []
    for instr in instr_list:
        rack.append(instr.setup_layout(theme))

    html_layout = [
        html.Div(
            [
                # Instruments are in the instrument rack
                html.Div(
                    [
                        html.Div(
                            id='instrument-rack',
                            children=rack,
                            style={'width': '100%'}
                        ),
                        # This div is used as a an output of a callback which wouldn't need output
                        html.Div(
                            id='event-output-div',
                            children='',
                            style={'display': 'none'}
                        ),
                        # Control panel for the data acquisition
                        html.Div(
                            id='measure-div',
                            children=[
                                StopButton(
                                    id='measureButton',
                                    buttonText='Start'
                                ),
                                Indicator(
                                    id='measuring',
                                    value=False,
                                    label='Is measuring :',
                                    labelPosition="top",
                                )
                            ],
                            style={
                                'width': '300px',
                                'display': 'flex',
                                'flexDirection': 'row',
                                'alignItems': 'center',
                                'justifyContent': 'space-between'
                            }
                        )
                    ],
                    style={
                        'width': '100%',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'alignItems': 'center',
                        'margin': '5px'
                    }
                ),
                html.Div(
                    [
                        # Display of the acquired data
                        dcc.Graph(
                            id='graph',
                            style={'width': '90 %'},
                            figure={
                                'data': [],
                                'layout': dict(
                                    paper_bgcolor=BKG_COLOR[theme],
                                    plot_bgcolor=BKG_COLOR[theme],
                                    font=dict(
                                        color=TEXT_COLOR[theme],
                                        size=15,
                                    )
                                )
                            }
                        )
                    ],
                    style={
                        'width': '100%',
                        'alignItems': 'center',
                    }
                ),
                html.Div(
                    [
                        dcc.Markdown('''
**What is this app about?**

This is an app to show the graphic elements of Dash DAQ used to create an
interface for the pressure gauges from Kurt J. Lesker multi gauges controller
MGC4000. This mock demo does not actually connect to a physical instrument
the values displayed are generated randomly for demonstration purposes.

**How to use the app**

Choose which gauge(s) you would like to measure values from in the
`Instrument parameters` combobox and click `Run`, the measured data will be
displayed on the graph below while the latest measured value will be
displayed on each gauge. You can purchase the Dash DAQ components at [
dashdaq.io](https://www.dashdaq.io/)''')
                    ],
                    style={
                        'max-width': '600px',
                        'margin': '15px auto 300 px auto',
                        'padding': '40px',
                        'box-shadow': '10px 10px 5px rgba(0, 0, 0, 0.2)',
                        'border': '1px solid #DFE8F3'
                    },
                    className="row"
                )
            ],
            style={
                'width': '100%',
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'justifyContent': 'center',
                'color': TEXT_COLOR[theme],
                'background': BKG_COLOR[theme]
            }
        )
    ]

    if theme == 'dark':
        return DarkThemeProvider(children=html_layout)
    elif theme == 'light':
        return html.Div(children=html_layout)


root_layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        dcc.Interval(id='interval', interval=5000),
        html.Div(
            id='header',
            children=[
                html.H2('Dash DAQ: pressure gauge monitoring'),
                ToggleSwitch(
                    id='toggleTheme',
                    label='Dark/Light layout',
                    size=30,
                ),
                html.Img(
                    src='https://s3-us-west-1.amazonaws.com/plotly'
                        '-tutorials/excel/dash-daq/dash-daq-logo'
                        '-by-plotly-stripe.png',
                    style={
                        'height': '100',
                        'float': 'right',
                    }
                )
            ],
            className='banner',
            style={
                'width': '100%',
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'background': '#A2B1C6',
                'color': '#506784'
            }
        ),
        html.Div(
            id='page-content',
            children=generate_lab_layout(INSTRUMENT_RACK),
            style={'width': '100%'}
        ),
    ]
)

# Create dash app
app = dash.Dash('')
server = app.server
app.css.append_css(
    {'external_url': 'https://codepen.io/bachibouzouk/pen/dKJyoK.css'}
)

app.config.suppress_callback_exceptions = False
app.scripts.config.serve_locally = True

# In[]:
# Create app layout
app.layout = root_layout

# In[]:
# Create callbacks
# generate the callbacks between the instrument and the app
for instr in INSTRUMENT_RACK:
    instr.generate_callbacks(
        app,
        inputs=[Input('interval', 'n_intervals')]
    )


@app.callback(Output('page-content', 'children'),

              [Input('toggleTheme', 'value')])
def page_layout(value):
    if value:
        return generate_lab_layout(INSTRUMENT_RACK, 'dark')
    else:
        return generate_lab_layout(INSTRUMENT_RACK, 'light')


@app.callback(
    Output('measuring', 'value'),
    [Input('measureButton', 'n_clicks')],
    [State('measuring', 'value')]
)
def trigger_measure(n_clicks, is_measuring):
    if n_clicks is None:
        return is_measuring
    else:
        return not is_measuring


@app.callback(
    Output('measureButton', 'buttonText'),
    [Input('measureButton', 'n_clicks')],
    [State('measuring', 'value')]
)
def change_measure_btn_label(n_clicks, is_measuring):
    answer = 'Start'

    if n_clicks is not None:
        if not is_measuring:
            answer = 'Stop'
    return answer


@app.callback(
    Output('%s_controls_div' % PRESSURE_GAUGE.unique_id(), 'style'),
    [Input('%s_power_button' % PRESSURE_GAUGE.unique_id(), 'on')],
    [State('%s_controls_div' % PRESSURE_GAUGE.unique_id(), 'style')],
)
def grey_out_controls_div(pwr_status, style_dict):
    return grey_out(style_dict, pwr_status)


@app.callback(
    Output('%s_gauges_div' % PRESSURE_GAUGE.unique_id(), 'style'),
    [Input('%s_power_button' % PRESSURE_GAUGE.unique_id(), 'on')],
    [State('%s_gauges_div' % PRESSURE_GAUGE.unique_id(), 'style')],
)
def grey_out_gauges_div(pwr_status, style_dict):
    return grey_out(style_dict, pwr_status)


@app.callback(
    Output('measure-div', 'style'),
    [Input('%s_power_button' % PRESSURE_GAUGE.unique_id(), 'on')],
    [State('measure-div', 'style')],
)
def grey_out_measuring_div(pwr_status, style_dict):
    return grey_out(style_dict, pwr_status)


@app.callback(
    Output('measureButton', 'disabled'),
    [Input('%s_power_button' % PRESSURE_GAUGE.unique_id(), 'on')]
)
def enable_measure_btn(pwr_status):
    return not pwr_status


@app.callback(
    Output('%s_instr_port' % PRESSURE_GAUGE.unique_id(), 'value'),
    [
        Input('%s_power_button' % PRESSURE_GAUGE.unique_id(), 'on'),
        Input('interval', 'n_intervals')
    ],
    [
        State('%s_instr_port' % (PRESSURE_GAUGE.unique_id()), 'value'),
        State('%s_instr_port' % (PRESSURE_GAUGE.unique_id()), 'placeholder')
    ]
)
def instrument_port_prevent_reset(pwr_status, _, text, placeholder):
    """prevents the input box's value to be reset by dcc.Interval"""
    if pwr_status:
        return text
    else:
        return placeholder


@app.callback(
    Output('%s_instr_port' % PRESSURE_GAUGE.unique_id(), 'disabled'),
    [Input('%s_power_button' % PRESSURE_GAUGE.unique_id(), 'on')],
)
def enable_instrument_port_input(pwr_status):
    return not pwr_status


@app.callback(
    Output('%s_instr_port_btn' % PRESSURE_GAUGE.unique_id(), 'disabled'),
    [
        Input('%s_power_button' % PRESSURE_GAUGE.unique_id(), 'on'),
        Input('%s_instr_port' % (PRESSURE_GAUGE.unique_id()), 'value')
    ],
    [State('%s_instr_port' % (PRESSURE_GAUGE.unique_id()), 'placeholder')]
)
def instrument_port_btn_update(pwr_status, text, placeholder):
    """enable or disable the connect button depending on the port name"""
    answer = True

    if text != placeholder:
        if is_instrument_port(text):
            answer = not pwr_status
    return answer


@app.callback(
    Output('event-output-div', 'children'),
    [Input('%s_instr_port_btn' % PRESSURE_GAUGE.unique_id(), 'n_clicks')],
    [State('%s_instr_port' % (PRESSURE_GAUGE.unique_id()), 'value')]
)
def instrument_port_btn_click(_, text):
    """reconnect the instrument to the new com port, this was handeled by an Event"""
    PRESSURE_GAUGE.connect(text)
    return text


@app.callback(
    Output('graph', 'figure'),
    [
        Input('interval', 'n_intervals'),
        Input('measuring', 'value'),
        Input('%s_channel' % (PRESSURE_GAUGE.unique_id()), 'value'),
        Input('toggleTheme', 'value')
    ],
    [
        State('%s_power_button' % PRESSURE_GAUGE.unique_id(), 'on')
    ]
)
def update_graph(
        _,
        is_measuring,
        selected_params,
        is_dark_theme,
        pwr_status
):

    if is_dark_theme:
        theme = 'dark'
    else:
        theme = 'light'
    # here one should write the script of what the instrument do
    data_for_graph = []

    if pwr_status and is_measuring:
        for instr in INSTRUMENT_RACK:

            # triggers the measure on the selected channels
            if is_measuring:
                for instr_channel in selected_params:
                    instr.measure(instr_param='%s' % instr_channel)

            # collects the data measured by all channels to update the graph
            for instr_chan in selected_params:

                if instr.measured_data[instr_chan]:
                    xdata = 1000 * instr.measured_data['%s_time' % instr_chan]
                    ydata = instr.measured_data[instr_chan]
                    data_for_graph.append(
                        go.Scatter(
                            x=xdata,
                            y=ydata,
                            mode='lines+markers',
                            name='%s:%s' % (instr, instr_chan),
                            line={
                                'width': 2
                            }
                        )
                    )

    return {
        'data': data_for_graph,
        'layout': dict(
            xaxis={
                'type': 'date',
                'title': 'Time',
                'color': TEXT_COLOR[theme],
                'gridcolor': GRID_COLOR[theme]
            },
            yaxis={
                'title': 'Pressure (mbar)',
                'gridcolor': GRID_COLOR[theme]
            },
            font=dict(
                color=TEXT_COLOR[theme],
                size=15,
            ),
            margin={'l': 100, 'b': 100, 't': 50, 'r': 20, 'pad': 0},
            plot_bgcolor=BKG_COLOR[theme],
            paper_bgcolor=BKG_COLOR[theme]
        )
    }


# In[]:
# Main
if __name__ == '__main__':
    app.run_server(debug=True)
