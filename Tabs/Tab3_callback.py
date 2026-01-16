from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
pd.options.mode.copy_on_write = True

# Import the necessary functions

# Get the data
# ts = load_data()

# A simple Markdown text for Tab 3
layout_tab3 = html.Div(children=[
    html.H2(children='Hourly Analysis',
            style={'textAlign': 'center'}),
    html.Div(children=[dcc.Markdown("This tab is under construction. Please check back later.")],
             style = {'textAlign': 'center', "fontSize": "18px"})])

# Register callbacks for Tab 3
def register_callbacks_tab3(app):
    pass