# Import libraries
import pandas as pd
from pathlib import Path
import os
# libraries to plot
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from dash import Dash, dcc, html, Input, Output, callback, dash_table

pio.templates.default = 'plotly_white'  # set as template

# visit http://127.0.0.1:8050/ in your web browser.


# Working directory
current_dir = os.getcwd()
working_dir = Path(current_dir) / 'csv_files'


# Load and process the data
ts = pd.read_csv(working_dir / 'energy_ENOS_2004-2023.csv', encoding='utf8', index_col=0)
ts.index = pd.to_datetime(ts.index)


# transform the data
ts_unique_years = [{'label': i, 'value': i} for i in ts['Año'].unique()]
ts_unique_technology = [{'label': i, 'value': i} for i in ts['Tipo de generación'].unique()]
ts_unique_technology2 = [item for item in ts_unique_technology if item['value'] != 'Biomasa']

# Name color to each type of plant
colors_plants = {'Hidroeléctrica': 'blue', 'Turbina de Vapor': 'red', 'Turbina de Gas': 'darkgrey', 'Eólico': 'green',
                 'Fotovoltaica': 'yellowgreen', 'Biogas': 'orange', 'Geotérmica': 'purple',
                 'Motor Reciprocante': 'brown',
                 'Biomasa': 'coral'}

mardown_text_intro = '''
    This dashboard showcases my skills in data management and information visualization using
    data obtained from a custom script I created: [Jupyter Notebook](Data_process/Energy_data_clean.ipynb).
    
    The dashboard provides an overview of Guatemala's electricity market from 2004 to 2023, allowing
    users to explore electricity generation by technology type across various visualizations.


    You will find two tabs with the following information:
    * **First Tab**: Visualize electricity generation by technology over the years with three types of visualization: Line plot, Boxplot, Heatmap and a Pie Chart.
    * **Second Tab**: Visualize electricity generation by technology over the years with the incorporation of the influence of the Niño–Southern Oscillation on power generation.
    
    &nbsp;

    **Note: the technology names will be keep in spanish, as the original data is in spanish.**
    > _All credits to the original information can be found on the website: [AMM, Administrator de Mercado Mayorista](https://reportesbi.amm.org.gt)._
    
    '''

mardown_tab1 = '''
To analyze the behavior of electric power generation plants in Guatemala during the years 2004 - 2023. Three aspects will be analyzed:
* Technology generation over time
* Technology generation per month, with the help of a Heatmap
                        '''

mardown_tab2 = '''
To analyze the behavior of the electric power generation plants in Guatemala during the years 2004 - 2023. The following aspects will be analyzed:
* Influence of the El Niño–Southern Oscillation on power generation
'''

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
        return html.Div(children=[
            html.H2(children='Power Generation by Technology',
                    style={'textAlign': 'center'}),
            html.Div(children=[dcc.Markdown(mardown_tab1)]),
            html.H4('Select the year'),
            dcc.Dropdown(id='select_year_tab1',
                         options=ts_unique_years,
                         value=[2018, 2019, 2020, 2021, 2022, 2023],  # Needed if multi=True
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
        ])

    elif tab == 'tab-2':
        return html.Div(children=[
            html.H2(children='Power Generation and Climate',
                    style={'textAlign': 'center'}),
            html.Div(children=[dcc.Markdown(mardown_tab2)]),

            html.H4('Select the year'),
            dcc.Dropdown(id='select_year_tab2',
                         options=ts_unique_years,
                         value=[2018, 2019, 2020, 2021, 2022, 2023],  # Needed if multi=True
                         multi=True),

            html.H4('Select the type of technology'),
            dcc.Dropdown(id='select_technology_tab2',
                         options=ts_unique_technology2,
                         value='Hidroeléctrica',
                         multi=False),

            dcc.Graph(id='energy-graph-climate-tab2', figure={})
        ])


# Connect the plotly graph with Dash Components
# In this case year button
@app.callback([Output(component_id='energy-graph', component_property='figure'),
               Output(component_id='blox-plot', component_property='figure'),
               Output(component_id='heat-map', component_property='figure'),
               Output(component_id='pie-graph', component_property='figure')],
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

    return fig_line, fig_box, fig_heat, fig_pie


@app.callback(Output(component_id='energy-graph-climate-tab2', component_property='figure'),
              [Input(component_id='select_year_tab2', component_property='value'),
               Input(component_id='select_technology_tab2', component_property='value')])
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

    return fig


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=7860)
