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
    El presente dashboard tiene como objectivo desmostrar mis habilidades en el manejo de datos y visualización de información, luego de
    haber obtenido la información del siguiente script elaborado por mi persona: [GitHub](https://github.com/).

    La información a visualizar es una imagen del mercado eléctrico de Guatemala a través de los años 2004 - 2023, donde
    es posible visualizar la generación electrica por tipo de tecnología en distintas visualizaciones.


    Su persona encontrará dos Tabs con la siguiente información:
    * **Primer Tab**: visualizar la generación eléctrica por tecnología a traves de los años con tres tipos de visualización: Line plot, Boxplot, Heatmap y un diagrama de pastel.
    * **Segunda Tab**: visualizar la generación eléctrica por tecnología a traves de los años con la incorporación de la influencia del fenómeno de El Niño en la generación de energía eléctrica.

   > _Todo los creditos a la información original se encuentran en el portal: [AMM, Administrator de Mercado Mayorista](https://reportesbi.amm.org.gt)._

    '''

mardown_tab1 = '''
Analizar el comportamiento de las plantas generadoras de energía eléctrica en Guatemala durante los años 2004-2023. Se analizarán tres aspectos:
* Generación de la tecnología a lo largo del tiempo
* Generación de la tecnología por mes, con la ayuda de un mapa de calor
                        '''

mardown_tab2 = '''
Analizar el comportamiento de las plantas generadoras de energía eléctrica en Guatemala durante los años 2004-2023. Se analizará el aspecto:
* Influencia del fenómeno de El Niño en la generación de energía eléctrica
'''

# Create a Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
# For deployment with gunicorn
server = app.server

app.layout = html.Div(children=[
    html.H1(children='Plantas de generación eléctrica en Guatemala',
            style={'textAlign': 'center'}),
    dcc.Markdown(mardown_text_intro),
    dcc.Tabs(id='Tabs-single-choice', value='tabs',
             children=[
                 dcc.Tab(label='Generación eléctrica', value='tab-1'),
                 dcc.Tab(label='Clima y energía', value='tab-2'),
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
            html.H2(children='Generación eléctrica por tipo de tecnología',
                    style={'textAlign': 'center'}),
            html.Div(children=[dcc.Markdown(mardown_tab1)]),
            html.H4('Seleccione el año'),
            dcc.Dropdown(id='select_year_tab1',
                         options=ts_unique_years,
                         value=[2018, 2019, 2020, 2021, 2022, 2023],  # Needed if multi=True
                         multi=True),

            html.H4('Seleccione el tipo de tecnología'),
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
            html.H2(children='Generación eléctrica y clima',
                    style={'textAlign': 'center'}),
            html.Div(children=[dcc.Markdown(mardown_tab2)]),

            html.H4('Seleccione el año'),
            dcc.Dropdown(id='select_year_tab2',
                         options=ts_unique_years,
                         value=[2018, 2019, 2020, 2021, 2022, 2023],  # Needed if multi=True
                         multi=True),

            html.H4('Seleccione el tipo de tecnología'),
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
    title_text_line = (f"<b>Generación eléctrica de {technology} para los años "
                       f"[{min(ts_copy.index.year)} - {max(ts_copy.index.year)}]</b>")
    title_text_boxplot = (f"<b>Generación eléctrica mensual de {technology} para los años "
                          f"[{min(ts_copy.index.year)} - {max(ts_copy.index.year)}]</b>")
    title_text_heatmap = (f"<b>Distribución de la Generación eléctrica de {technology} para los años "
                          f"[{min(ts_copy.index.year)} - {max(ts_copy.index.year)}]</b>")

    # Create a line plot with the selected data from the ts_copy dataframe
    fig_line = px.line(ts_copy, x=ts_copy.index, y='Generación [GWh]', color="Tipo de generación",
                       color_discrete_map=colors_plants)
    fig_line.update_layout(title=title_text_line,
                           xaxis_title='Año',
                           yaxis_title='Generación (GWh)',
                           legend_title='Planta')
    # set y range values manual
    fig_line.update_yaxes(range=[0, ts_copy['Generación [GWh]'].max() * 1.15])

    # Figure Boxplot
    fig_box = px.box(ts_copy, x='Mes', y='Generación [GWh]', color='Tipo de generación',
                     color_discrete_map=colors_plants)
    fig_box.update_yaxes(range=[0, ts_copy['Generación [GWh]'].max() * 1.15])
    fig_box.update_layout(title_text=title_text_boxplot, showlegend=False, title_font={"size": 15})
    fig_box.update_yaxes(title_text="Generación [GWh]", titlefont=dict(size=13))

    # Figure of Heatmap
    fig_heat = go.Figure()
    fig_heat.add_trace(go.Heatmap(
        x=ts_copy['Año'],
        y=ts_copy['Mes'],
        z=ts_copy['Generación [GWh]'],
        colorscale='spectral', colorbar=dict(title='Generación [GWh]', titleside='right')))
    fig_heat.update_yaxes(range=[0, 12], title_text="Mes", titlefont=dict(size=13))
    fig_heat.update_xaxes(range=[min(ts_copy.index.year), max(ts_copy.index.year)], title_text='Año',
                          titlefont=dict(size=13))
    fig_heat.update_layout(title=title_text_heatmap, showlegend=False, title_font={"size": 15})
    fig_heat.update_traces(hovertemplate="Mes: %{x}<br>Tipo de generación: %{y}<br>Generación [GWh]: %{z:.3f}")

    # Figure of Pie chart to show the percentage of the plant select for each month
    fig_pie = px.pie(ts_copy, values='Generación [GWh]', names='Año',
                     title=f"<b>% de Generación eléctrica por {technology} para los años "
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

    fig.add_trace(go.Scatter(x=ts_copy.index, y=ts_copy['Anom'], name='Anomalie- El Niño',
                             marker=dict(color='red', opacity=0.1), fill='tozeroy'), secondary_y=True)

    fig.update_layout(
        title=f"<b>Generación eléctrica por tipo de tecnología para los años {min(ts_copy.index.year)} - {max(ts_copy.index.year)}</b>")

    return fig


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=7860)
