import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
from matplotlib.colors import to_rgb
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from scipy.stats import gaussian_kde
pd.options.mode.copy_on_write = True
from Process.Functions import colors_plants, load_data

# Get the data
ts = load_data()

# transform the data
ts_unique_years = [{'label': i, 'value': i} for i in ts['Año'].unique()]
ts_unique_technology = [{'label': i, 'value': i} for i in ts['Tipo de generación'].unique()]

app = Dash(__name__, suppress_callback_exceptions=True)

# For deployment with gunicorn
server = app.server

# Layout
app.layout = html.Div(children=[
    html.H1(children='Power Plants in Guatemala',
            style={'textAlign': 'center'}),
    dcc.Markdown("Test"),
    dcc.Tabs(id='Tabs-single-choice', value='tabs',
             children=[
                 dcc.Tab(label='Power Generation', value='tab-1'),
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
            html.Div(children=[dcc.Markdown("Test")]),
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

            html.Div(children=[
                html.Div(dcc.Graph(id='pie-graph', figure={}), style={'display': 'inline-block'}),
                html.Div(dcc.Graph(id='Ridgeline-plot', figure={}), style={'display': 'inline-block'})]),

            html.Div(dcc.Graph(id='Seasonal-plot', figure={})),
        ])

# Register callbacks for Tab 1
@app.callback([Output(component_id='energy-graph', component_property='figure'),
               Output(component_id='blox-plot', component_property='figure'),
               Output(component_id='heat-map', component_property='figure'),
               Output(component_id='pie-graph', component_property='figure'),
               Output(component_id='Ridgeline-plot', component_property='figure'),
               Output(component_id='Seasonal-plot', component_property='figure')],
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
    title_text_boxplot = (f"<b>Montly power geneartion of {technology} for the years <br>"
                          f"[{min(ts_copy.index.year)} - {max(ts_copy.index.year)}]</b>")
    title_text_heatmap = (f"<b>Monthly Electricity Generation Distribution (%) <br>"
                          f"for {technology} [{min(ts_copy.index.year)} - {max(ts_copy.index.year)}]</b>")

    title_text_pie = (f"<b>Percent of power plant by {technology} for the years <br>"
                           f"[{min(ts_copy.index.year)} - {max(ts_copy.index.year)}]</b>")

    title_text_ridgeline = (f"<b>Ridgeline Plot of Monthly Generation Distribution <br>"
                          f"for {technology} [{min(ts_copy.index.year)} - {max(ts_copy.index.year)}]</b>")

    title_text_seasonal = (f"<b>Seasonal Plot of Monthly Generation <br>"
                          f"for {technology} [{min(ts_copy.index.year)} - {max(ts_copy.index.year)}]</b>")

    # Create a line plot with the selected data from the ts_copy dataframe
    fig_line = px.line(ts_copy, x=ts_copy.index, y='Generación [GWh]', color="Tipo de generación",
                       color_discrete_map=colors_plants)
    fig_line.update_layout(title=title_text_line,
                           xaxis_title='Year',
                           yaxis_title='Generation [GWh]',
                           legend_title='Power Plant',
                           title_font={"size": 15})
    # set y range values manual
    fig_line.update_yaxes(range=[0, ts_copy['Generación [GWh]'].max() * 1.15])

    # Figure Boxplot
    fig_box = px.box(ts_copy, x='Mes', y='Generación [GWh]', color='Tipo de generación',
                     color_discrete_map=colors_plants)
    fig_box.update_yaxes(range=[0, ts_copy['Generación [GWh]'].max() * 1.15])
    fig_box.update_layout(title_text=title_text_boxplot, showlegend=False, title_font={"size": 15},
                          xaxis_title='Month')
    fig_box.update_yaxes(title_text="Generation [GWh]", titlefont=dict(size=13))

    # Transformation to heatmap normalization
    # Calculate the total generation for each year
    ts_copy['Yearly_Total'] = ts_copy.groupby('Año')['Generación [GWh]'].transform('sum')
    # Calculate the percentage contribution of each month for its year
    # Handle cases where Yearly_Total might be 0 to avoid division by zero
    ts_copy['Generation [%]'] = np.where(
        ts_copy['Yearly_Total'] > 0,
        (ts_copy['Generación [GWh]'] / ts_copy['Yearly_Total']) * 100,
        0  # Assign 0% if the yearly total is 0
    )

    # Define the correct order for months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                   'November', 'December']

    # Ensure 'Month' is a categorical type with the correct order
    ts_copy['Month'] = pd.Categorical(ts_copy['Mes'], categories=month_order, ordered=True)

    # Pivot the table to get Months as rows, Years as columns, and Percentage as values
    heatmap_data_pct =ts_copy.pivot_table(
        index='Month',
        columns='Year',
        values='Generation [%]',
        observed=False
    ).fillna(0)

    # Extract years and months for axes labels (ensure month order is correct)
    years_axis = heatmap_data_pct.columns
    months_axis = heatmap_data_pct.index  # Already ordered correctly due to Categorical

    # Figure of Heatmap
    fig_heat = go.Figure()
    fig_heat.add_trace(go.Heatmap(
        x=years_axis,
        y=months_axis,
        z=heatmap_data_pct.values,
        colorscale='Spectral_r', colorbar=dict(title='Generation [%]', titleside='right'),
    reversescale=False))
    fig_heat.update_layout(
    title=title_text_heatmap,
    xaxis_title='Year',
    yaxis_title='Month', # Treat years as categories if needed
    title_font={"size": 15}
    )

    # fig_heat.update_yaxes(range=[0, 12], title_text="Month", titlefont=dict(size=13))
    fig_heat.update_layout(showlegend=False, title_font={"size": 15})
    # update traces
    fig_heat.update_traces(hovertemplate="Month: %{y}<br>Year: %{x|%Y}<br>Generation [%]: %{z:.3f}")

    # Figure of Pie chart to show the percentage of the plant select for each month
    fig_pie = px.pie(ts_copy, values='Generación [GWh]', names='Año',
                     color_discrete_map=px.colors.qualitative.Set3)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label',
                          insidetextorientation='radial',
                          marker=dict(line=dict(color='black', width=2)))
    fig_pie.update_layout(title=title_text_pie,
    title_font={"size": 15})

    # # --- Sample Data Generation (Replace with your actual data loading) ---
    # # Using the same sample data generator as before for consistency
    years = range(min(ts_copy.index.year), max(ts_copy.index.year))
    # print(years)

    df = ts_copy[['Año', 'Mes', 'Generación [GWh]']]

    # We want to show the distribution of monthly generation values for each year.

    # Define the range for the x-axis (Generation GWh)
    # Make it slightly wider than the actual min/max for better plotting
    min_gen = df['Generación [GWh]'].min()
    max_gen = df['Generación [GWh]'].max()
    x_range =np.linspace(min_gen * 0.8, max_gen * 1.1, 200)  # 200 points for smoothness

    #
    # Store calculated KDEs and other info
    distributions = []
    sorted_years = sorted(df['Año'].unique())

    for i, year in enumerate(sorted_years):
        # Get the monthly generation values for this specific year
        year_data = df[df['Año'] == year]['Generación [GWh]'].values

        # Need at least 2 data points to calculate KDE
        if len(year_data) > 1:
            try:
                # Calculate Kernel Density Estimate
                kde = gaussian_kde(year_data)
                # Evaluate the KDE over our x_range
                density = kde.evaluate(x_range)

                # Normalize density for better visual stacking (optional but recommended)
                # This makes the peak height visually similar for easier comparison of shape
                if density.max() > 0:
                    normalized_density = density / density.max()
                else:
                    normalized_density = density  # Avoid division by zero if density is flat zero

                distributions.append({
                    'year': year,
                    'x_range': np.around(x_range,3),
                    'density': np.around(normalized_density,4),  # Use normalized density
                    # 'original_density': density,  # Keep original if needed for hover
                    'vertical_offset': i  # Simple offset based on year index
                })
            except Exception as e:
                print(f"Could not calculate KDE for year {year}: {e}")
                # Optionally append placeholder data or skip
                distributions.append({
                    'year': year,
                    'x_range': x_range,
                    'density': np.zeros_like(x_range),
                    'original_density': np.zeros_like(x_range),
                    'vertical_offset': i
                })
    # Save the distributions to a text file
    with open('distributions.txt', 'w') as f:
        for dist in distributions:
            f.write(f"Year: {dist['year']}, Density: {dist['density'].tolist()}, Vertical Offset: {dist['vertical_offset']}\n")

    # Create color scale
    colors = px.colors.sequential.Viridis

    # --- Create the Ridgeline Plot Figure ---
    fig_ridgeline = go.Figure()

    # Define vertical spacing factor (adjust this to control overlap)
    spacing_factor = 0.85

    for idx,dist_data in enumerate(reversed(distributions)):  # Plot from top to bottom (latest year at top)
        color_scale = colors[int(idx/len(distributions)*len(colors))]

        year = dist_data['year']
        x = dist_data['x_range']
        y = dist_data['density'] * spacing_factor + dist_data['vertical_offset']  # Add offset
        # original_density_vals = dist_data['original_density']  # For hover

        fig_ridgeline.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name=str(year),
            fill='toself',  # Fill area under the curve towards y=vertical_offset effectively
            fillcolor=f'rgba{(*to_rgb(color_scale), 0.2)}',  # Example semi-transparent fill
            line=dict(color=color_scale, width=1.8),  # Example line color
            # hoverinfo='x+name',  # Show Generation (x) and Year (name)
        ))

    # --- Customize Layout ---
    # Create lists for y-axis ticks and labels
    tickvals = [d['vertical_offset'] for d in distributions]
    ticktext = [str(d['year']) for d in distributions]

    fig_ridgeline.update_layout(
        title=title_text_ridgeline,
        title_font={"size": 15},
        xaxis_title='Monthly Generation [GWh]',
        yaxis_title='Year',
        yaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext,
            showgrid=False,  # Often looks cleaner without horizontal gridlines
            zeroline=False
        ),
        xaxis=dict(
            range=[min_gen * 0.75, max_gen * 1.15],
            showgrid=True,
            zeroline=False
        ),
        showlegend=False,  # Legend isn't very useful here; years are on y-axis
        plot_bgcolor='rgba(240,240,240,0.8)',  # Light gray background
        margin=dict(l=50, r=20, t=80, b=50),
        # height=600,  # Adjust height as needed based on number of years
        # width=800
    )

    # A Seasonal Plot
    fig_seasonal = go.Figure()

    for month_name in ts_copy['Month'].unique():
        month_data = ts_copy[ts_copy['Month'] == month_name]

        fig_seasonal.add_trace(go.Scatter(
            x=month_data['Año'],
            y=month_data['Generación [GWh]'],
            mode='lines+markers',
            name=str(month_name),
            marker=dict(size=10, opacity=0.6)
        ))

    fig_seasonal.update_layout(
      title=title_text_seasonal,
      xaxis_title='Year',
        yaxis_title='Generation [GWh]',
      legend_title= 'Month',
      plot_bgcolor='rgba(240,240,240,0.8)',
      margin=dict(l=50, r=20, t=80, b=50)
    )


    return fig_line, fig_box, fig_heat, fig_pie, fig_ridgeline, fig_seasonal

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7860)