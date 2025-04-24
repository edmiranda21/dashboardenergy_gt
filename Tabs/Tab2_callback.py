from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
pd.options.mode.copy_on_write = True

# Import the necessary functions
from Process.Text import mardown_tab2, markdonw_disclamer
from Process.Functions import colors_plants, load_data
from Process.LLM_configure import update_information_tab2

# Get the data
ts = load_data()

# transform the data
ts_unique_years = [{'label': i, 'value': i} for i in ts['Año'].unique()]
ts_unique_technology = [{'label': i, 'value': i} for i in ts['Tipo de generación'].unique()]
ts_unique_technology2 = [item for item in ts_unique_technology if item['value'] != 'Biomasa']


# Layout for Tab 2
layout_tab2 = html.Div(children=[
            html.H2(children='Power Generation and Climate',
                    style={'textAlign': 'center'}),
            html.Div(children=[dcc.Markdown(mardown_tab2)]),

            html.H4('Select the year'),
            dcc.Dropdown(id='select_year_tab2',
                         options=ts_unique_years,
                         value=[2018, 2019, 2020, 2021, 2022, 2023, 2024],  # Needed if multi=True
                         multi=True),

            html.H4('Select the type of technology'),
            dcc.Dropdown(id='select_technology_tab2',
                         options=ts_unique_technology2,
                         value='Hidroeléctrica',
                         multi=False),

            dcc.Graph(id='energy-graph-climate-tab2', figure={}),

            # Add an analysis of a LLM chatbot
            html.Div(children=[
                html.H2(children='Analysis by Google: Gemini 2.0 Flash Experimental',
                        style={'textAlign': 'center'}),
                html.Div(children=[dcc.Markdown(markdonw_disclamer)],
                            style={'textAlign': 'center',"fontSize": "18px"}),
                dcc.Store(id="data-store"), # Store the data
                html.Button('Generate Analysis', id='button_analysis', n_clicks=0, disabled=False,
                            style={"fontSize": "17px", "height": 60, "width": 180}),
                html.Div(id='chatbot-responsetab2',
                         children= dcc.Loading(
                             id='loading-tab2',
                             type='circle',
                             children='Display the analysis here'))
        ])
        ])

# Register callbacks for Tab 1
def register_callbacks_tab2(app):
    @app.callback([Output(component_id='energy-graph-climate-tab2', component_property='figure'),
                   Output("data-store", "data")],  # Disable button
                  [Input(component_id='select_year_tab2', component_property='value'),
                   Input(component_id='select_technology_tab2', component_property='value'),
                   ])
    # Set the function to update the graphs
    def update_graph_tab2(value_year, technology):
        if len(value_year) == 1:
            select_year = value_year
        else:
            select_year = [value_year][0]

        if technology:
            set_technology = technology

        # Copy the original dataframe to avoid modifying the original
        ts_copy = ts.copy(deep=True)
        # Use a filter with query
        ts_copy = ts_copy[ts_copy['Año'].isin(select_year) & ts_copy['Tipo de generación'].isin([set_technology])]
        ts_copy.sort_index(inplace=True)

        # print(ts_copy['Tipo de generación'].value_counts())
        # print(set_technology)

        # Filter only the necessary data to store and later call to the chatbot
        def update_filter_data(dataframe):
            dataframe['Generación [GWh]'] = dataframe['Generación [GWh]'].round(3)
            filter_data = dataframe[['Mes', 'Año', 'Tipo de generación', 'Generación [GWh]', 'Anom']].to_dict('records')
            return filter_data

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(go.Scatter(x=ts_copy.index, y=ts_copy['Generación [GWh]'],
                                 name=str(set_technology), marker=dict(color=colors_plants[set_technology])),
                      secondary_y=False)

        fig.add_trace(go.Scatter(x=ts_copy.index, y=ts_copy['Anom'], name='Anomalie-El Niño',
                                 marker=dict(color='red', opacity=0.1), fill='tozeroy'), secondary_y=True)

        fig.update_yaxes(range=[0, ts_copy['Generación [GWh]'].max() * 1.15],
                         secondary_y=False)

        fig.update_layout(
            title=f"<b>Power generation for technology for the years "
                  f"{min(ts_copy.index.year)} - {max(ts_copy.index.year)}</b>",
            xaxis_title='Year',
            yaxis_title='Generation [GWh]')

        return fig, update_filter_data(ts_copy)

    update_information_tab2(app)