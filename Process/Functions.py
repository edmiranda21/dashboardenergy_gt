import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import os
import json
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

# Summarize ridgeline data for LLM to use in the Tab1_callback.py
def summarize_ridgeline(distributions):
    summary = []
    for dist in distributions:
        year = dist['year']
        density = np.array(dist['density'])
        x = np.array(dist['x_range'])

        # Detect peak values
        peaks, _ = find_peaks(density, prominence=0.05, height=0.2)
        n_peaks = len(peaks)

        dist_type = {0: "flat", 1: "unimodal", 2: "bimodal"}.get(n_peaks, "multimodal")

        # Approximate width: percentiles between 10% and 90%
        cumsum = np.cumsum(density)
        cumsum /= cumsum[-1]
        try:
            p10 = x[np.where(cumsum >= 0.10)[0][0]]
            p90 = x[np.where(cumsum >= 0.90)[0][0]]
            width = round(p90 - p10, 1)
        except:
            width = None

        summary.append({
            "year": int(year),
            "distribution": dist_type,
            "peaks": int(n_peaks),
            "width_GWh": width,
            "mean_GWh": round(np.average(x, weights=density), 1) if width else None
        })
    return summary

# Transform data to feed the LLM model in Tab 1
def build_llm_payload_tab1(data_store: list, data_store_distribution:list) -> str:
    """
    Input: list of dicts from dcc.Store (output of update_filter_data)
    Output: JSON string for LLM (compact, structured, dynamic)
    """
    if not data_store:
        return json.dumps({"error": "No data"})

    # --------------------------------------------------------------
    # 1. Convert to DataFrame for easy stats
    # --------------------------------------------------------------
    df = pd.DataFrame(data_store)

    # Create a proper datetime index: "Mes Año" → e.g., "January 2018"
    df['date'] = pd.to_datetime(df['Mes'] + ' ' + df['Año'].astype(str), format='%B %Y')

    # Sort by date (just in case)
    df = df.sort_values('date').reset_index(drop=True)

    # --------------------------------------------------------------
    # 2. Period info
    # --------------------------------------------------------------
    min_date = df['date'].iloc[0]
    max_date = df['date'].iloc[-1]
    period = f"{min_date:%Y-%B} to {max_date:%Y-%B}"

    # --------------------------------------------------------------
    # 3. Summary stats
    # --------------------------------------------------------------
    total_gwh = round(df['Generación [GWh]'].sum(), 1)
    mean_gwh  = round(df['Generación [GWh]'].mean(), 1)

    peak_idx = df['Generación [GWh]'].idxmax()
    low_idx  = df['Generación [GWh]'].idxmin()

    peak_month = df.loc[peak_idx, 'date'].strftime("%B %Y")
    low_month  = df.loc[low_idx,  'date'].strftime("%B %Y")

    # --------------------------------------------------------------
    # 4. Compact monthly data
    # --------------------------------------------------------------
    monthly = [
        {
            "Mes": f"{row['Mes']} {row['Año']}",
            "Generación [GWh]": round(row['Generación [GWh]'], 2)
        }
        for _, row in df.iterrows()
    ]

    # --------------------------------------------------------------
    # 5. Final payload
    # --------------------------------------------------------------
    technology = df['Tipo de generación'].iloc[0]

    payload = {
        "technology": technology,
        "period": period,
        "summary": {
            "total_GWh": total_gwh,
            "mean_monthly_GWh": mean_gwh,
            "peak_month": peak_month,
            "peak_GWh": round(df.loc[peak_idx, 'Generación [GWh]'], 1),
            "lowest_month": low_month,
            "lowest_GWh": round(df.loc[low_idx, 'Generación [GWh]'], 1),
            "coefficient_of_variation": round(df['Generación [GWh]'].std() / mean_gwh, 3),
        },
        "monthly_data": monthly,
        "ridgeline_insights": data_store_distribution
    }

    return json.dumps(payload, indent=2, ensure_ascii=False)


# Transform data to feed the LLM model in Tab 2
def build_llm_payload_tab2(data_store: list) -> str:
    """
    Input: list of dicts from dcc.Store (output of update_filter_data)
    Output: JSON string for LLM (compact, structured, dynamic)
    """
    if not data_store:
        return json.dumps({"error": "No data"})

    # --------------------------------------------------------------
    # 1. Convert to DataFrame for easy stats
    # --------------------------------------------------------------
    df = pd.DataFrame(data_store)

    # Create a proper datetime index: "Mes Año" → e.g., "January 2018"
    df['date'] = pd.to_datetime(df['Mes'] + ' ' + df['Año'].astype(str), format='%B %Y')

    # Sort by date (just in case)
    df = df.sort_values('date').reset_index(drop=True)

    # --------------------------------------------------------------
    # 2. Period info
    # --------------------------------------------------------------
    min_date = df['date'].iloc[0]
    max_date = df['date'].iloc[-1]
    period = f"{min_date:%Y-%B} to {max_date:%Y-%B}"

    # --------------------------------------------------------------
    # 3. Summary stats
    # --------------------------------------------------------------
    total_gwh = round(df['Generación [GWh]'].sum(), 1)
    mean_gwh  = round(df['Generación [GWh]'].mean(), 1)

    peak_idx = df['Generación [GWh]'].idxmax()
    low_idx  = df['Generación [GWh]'].idxmin()

    peak_month = df.loc[peak_idx, 'date'].strftime("%B %Y")
    low_month  = df.loc[low_idx,  'date'].strftime("%B %Y")

    # --------------------------------------------------------------
    # 4. ENSO correlation
    # --------------------------------------------------------------
    corr = df['Generación [GWh]'].corr(df['Anom'])
    corr = round(corr, 3) if not pd.isna(corr) else 0.0

    # --------------------------------------------------------------
    # 5. El Niño / La Niña months
    # --------------------------------------------------------------
    el_nino = df[df['Anom'] >= 0.5]['date'].dt.strftime('%Y-%m').tolist()
    la_nina = df[df['Anom'] <= -0.5]['date'].dt.strftime('%Y-%m').tolist()
    strong_el_nino = df[df['Anom'] >= 1.5]['date'].dt.strftime('%Y-%m').tolist()

    # --------------------------------------------------------------
    # 6. Compact monthly data
    # --------------------------------------------------------------
    monthly = [
        {
            "Mes": f"{row['Mes']} {row['Año']}",
            "Generación [GWh]": round(row['Generación [GWh]'], 2),
            "Anom": round(row['Anom'], 2)
        }
        for _, row in df.iterrows()
    ]

    # --------------------------------------------------------------
    # 7. Final payload
    # --------------------------------------------------------------
    technology = df['Tipo de generación'].iloc[0]

    payload = {
        "technology": technology,
        "period": period,
        "summary": {
            "total_GWh": total_gwh,
            "mean_monthly_GWh": mean_gwh,
            "peak_month": peak_month,
            "peak_GWh": round(df.loc[peak_idx, 'Generación [GWh]'], 1),
            "lowest_month": low_month,
            "lowest_GWh": round(df.loc[low_idx, 'Generación [GWh]'], 1),
            "coefficient_of_variation": round(df['Generación [GWh]'].std() / mean_gwh, 3),
            "enso_correlation_r": corr
        },
        "enso": {
            "el_nino_months": el_nino,
            "la_nina_months": la_nina,
            "strong_el_nino_months": strong_el_nino
        },
        "monthly_data": monthly
    }

    return json.dumps(payload, indent=2, ensure_ascii=False)