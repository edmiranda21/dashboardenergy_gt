from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
pd.options.mode.copy_on_write = True

# Import the necessary functions
from Process.Text import mardown_tab1, markdonw_disclamer
from Process.Functions import colors_plants, load_data
from Process.LLM_configure import update_information_tab1


# Get the data
ts = load_data()

# transform the data
ts_unique_years = [{'label': i, 'value': i} for i in ts['Año'].unique()]
ts_unique_technology = [{'label': i, 'value': i} for i in ts['Tipo de generación'].unique()]


# Layout for Tab 1
layout_tab1 = html.Div(children=[
            html.H2(children='Power Generation by Technology',
                    style={'textAlign': 'center'}),
            html.Div(children=[dcc.Markdown(mardown_tab1)]),
            html.H4('Select the year'),
            dcc.Dropdown(id='select_year_tab1',
                         options=ts_unique_years,
                         value=[2018, 2019, 2020, 2021, 2022, 2023, 2024],  # Needed if multi=True
                         multi=True),

            html.H4('Select the type of technology'),
            dcc.Dropdown(id='select_technology_tab1',
                         options=ts_unique_technology,
                         value='Hidroeléctrica',
                         multi=False),

            dcc.Graph(id='energy-graph', figure={}),

            html.Div(children=[
                html.Div(dcc.Graph(id='blox-plot', figure={}), style={'display': 'inline-block'}),
                html.Div(dcc.Graph(id='heat-map', figure={}), style={'display': 'inline-block'})]),

            dcc.Graph(id='pie-graph', figure={}),

            # Add an analysis of a LLM chatbot
            html.Div(children= [
                html.H2(children='Analysis by Mistral Small 3.1 24B',
                        style={'textAlign': 'center'}),
                html.Div(children=[dcc.Markdown(markdonw_disclamer)],
                         style={'textAlign': 'center', "fontSize": "18px"}),
                dcc.Store(id="data-store-tab1"), # Store the data
                html.Button('Generate Analysis', id='button_analysis_tab1', n_clicks=0, disabled=False,
                            style={"fontSize": "17px", "height": 60, "width": 180}),
                html.Div(id='chatbot-response-tab1',
                         children= dcc.Loading(
                             id='loading-tab1',
                             type='circle',
                             children='Display the analysis here'))
            ])
        ])

# Register callbacks for Tab 1
def register_callbacks_tab1(app):
    @app.callback([Output(component_id='energy-graph', component_property='figure'),
                   Output(component_id='blox-plot', component_property='figure'),
                   Output(component_id='heat-map', component_property='figure'),
                   Output(component_id='pie-graph', component_property='figure'),
                   Output("data-store-tab1", "data")],
                  [Input(component_id='select_year_tab1', component_property='value'),
                   Input(component_id='select_technology_tab1', component_property='value')])
    # Set the function to update the graphs
    def update_graph_tab1(value_year, technology):
        if len(value_year) == 1:
            select_year = value_year
        else:
            select_year = [value_year][0]

        if technology:
            set_technology = [technology]
        # Copy the original dataframe to avoid modifying the original
        ts_copy = ts.copy(deep=True)
        # Use a filter with query
        ts_copy = ts_copy[ts_copy['Año'].isin(select_year) & ts_copy['Tipo de generación'].isin(set_technology)]
        # set global variables
        title_text_line = (f"<b>Power generation of {technology} for the years "
                           f"[{min(ts_copy.index.year)} - {max(ts_copy.index.year)}]</b>")
        title_text_boxplot = (f"<b>Montly power geneartion of {technology} for the years "
                              f"[{min(ts_copy.index.year)} - {max(ts_copy.index.year)}]</b>")
        title_text_heatmap = (f"<b>Electricity Generation Distribution for {technology} for the years "
                              f"[{min(ts_copy.index.year)} - {max(ts_copy.index.year)}]</b>")

        # Create a line plot with the selected data from the ts_copy dataframe
        fig_line = px.line(ts_copy, x=ts_copy.index, y='Generación [GWh]', color="Tipo de generación",
                           color_discrete_map=colors_plants)
        fig_line.update_layout(title=title_text_line,
                               xaxis_title='Year',
                               yaxis_title='Generation [GWh]',
                               legend_title='Power Plant')
        # set y range values manual
        fig_line.update_yaxes(range=[0, ts_copy['Generación [GWh]'].max() * 1.15])

        # Figure Boxplot
        fig_box = px.box(ts_copy, x='Mes', y='Generación [GWh]', color='Tipo de generación',
                         color_discrete_map=colors_plants)
        fig_box.update_yaxes(range=[0, ts_copy['Generación [GWh]'].max() * 1.15])
        fig_box.update_layout(title_text=title_text_boxplot, showlegend=False, title_font={"size": 15},
                              xaxis_title='Month')
        fig_box.update_yaxes(title_text="Generation [GWh]", titlefont=dict(size=13))

        # Figure of Heatmap
        fig_heat = go.Figure()
        fig_heat.add_trace(go.Heatmap(
            x=ts_copy['Año'],
            y=ts_copy['Mes'],
            z=ts_copy['Generación [GWh]'],
            colorscale='spectral', colorbar=dict(title='Generation [GWh]', titleside='right')))
        fig_heat.update_yaxes(range=[0, 12], title_text="Month", titlefont=dict(size=13))
        fig_heat.update_xaxes(range=[min(ts_copy.index.year), max(ts_copy.index.year)], title_text='Year',
                              titlefont=dict(size=13))
        fig_heat.update_layout(title=title_text_heatmap, showlegend=False, title_font={"size": 15})
        fig_heat.update_traces(hovertemplate="Month: %{x}<br>Type of power plant: %{y}<br>Generation [GWh]: %{z:.3f}")

        # Figure of Pie chart to show the percentage of the plant select for each month
        fig_pie = px.pie(ts_copy, values='Generación [GWh]', names='Año',
                         title=f"<b>Percent of power plant by {technology} for the years "
                               f"[{min(ts_copy.index.year)} - {max(ts_copy.index.year)}]</b>",
                         color_discrete_map=px.colors.qualitative.Set3)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label',
                              insidetextorientation='radial',
                              marker=dict(line=dict(color='black', width=2)))

        # Filter only the necessary data to store and later call to the chatbot
        def update_filter_data_tab1(dataframe):
            dataframe['Generación [GWh]'] = dataframe['Generación [GWh]'].round(3)
            filter_data = dataframe[['Mes', 'Año', 'Tipo de generación', 'Generación [GWh]']].to_dict('records')
            return filter_data

        return fig_line, fig_box, fig_heat, fig_pie, update_filter_data_tab1(ts_copy)

    update_information_tab1(app)