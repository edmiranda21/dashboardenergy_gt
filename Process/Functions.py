import pandas as pd
import os
from pathlib import Path

# Name color to each type of plant
colors_plants = {'Hidroeléctrica': 'blue', 'Turbina de Vapor': 'red', 'Turbina de Gas': 'darkgrey', 'Eólico': 'green',
                 'Fotovoltaica': 'yellowgreen', 'Biogas': 'orange', 'Geotérmica': 'purple',
                 'Motor Reciprocante': 'brown',
                 'Biomasa': 'coral'}

# Extract the data
def load_data():
    # Get the main directory
    current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    working_dir = Path(current_dir) / 'csv_files'

    # Load and process the data
    ts = pd.read_csv(working_dir / 'energy_ENOS_2004-2024.csv', encoding='utf8', index_col=0)
    ts.index = pd.to_datetime(ts.index)
    return ts


# Transform data to feed the LLM model in Tab 1
def extract_data_chart_tab1(data_store):
    technology = data_store[0]['Tipo de generación']

    # Format data
    monthly_data = [
        f"{entry['Mes']} {entry['Año']}: {entry['Generación [GWh]']} GWh"
        for entry in data_store
    ]
    # Final format
    return (f"The technology is {technology}. "
            f"Data {monthly_data}"
    )

# Transform data to feed the LLM model in Tab 2
def extract_data_chart_tab2(data_store):
    technology = data_store[0]['Tipo de generación']

    # Format data
    monthly_data = [
        f"{entry['Mes']} {entry['Año']} : ({entry['Generación [GWh]']} GWh and {entry['Anom']})"
        for entry in data_store
    ]
    # Final format
    return (f"The technology is {technology}. "
            f"Data {monthly_data}"
    )