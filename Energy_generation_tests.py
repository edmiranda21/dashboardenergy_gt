import pandas as pd
# Import libraries
pd.options.mode.copy_on_write = True
import plotly.io as pio
from dash import Dash, dcc, html, Input, Output
# libraries to import the callbacks
from Process.Text import mardown_text_intro
from Tabs.Tab1_callback import layout_tab1,register_callbacks_tab1
from Tabs.Tab2_callback import layout_tab2, register_callbacks_tab2


pio.templates.default = 'plotly_white'  # set as template

# visit http://127.0.0.1:8050/ in your web browser.

# Create a Dash app
app = Dash(__name__, suppress_callback_exceptions=True)

# For deployment with gunicorn
server = app.server

app.layout = html.Div(children=[
    html.H1(children='Power Plants in Guatemala',
            style={'textAlign': 'center'}),
    dcc.Markdown(mardown_text_intro),
    dcc.Tabs(id='Tabs-single-choice', value='tabs',
             children=[
                 dcc.Tab(label='Power Generation', value='tab-1'),
                 dcc.Tab(label='Climate & Energy', value='tab-2'),
             ]),
    html.Div(id='tabs-content'),
])

# Connect the plotly graph with Dash Components
@app.callback(Output('tabs-content', 'children'),
              [Input('Tabs-single-choice', 'value')],
              prevent_initial_call=True)

def render_content(tab):
    if tab == 'tab-1':
        return layout_tab1

    elif tab == 'tab-2':
        return layout_tab2


# Call the function to register the callbacks tab1
register_callbacks_tab1(app)
register_callbacks_tab2(app)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=7860)