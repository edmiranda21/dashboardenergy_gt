# Text descriptions
mardown_text_intro = '''
    This dashboard showcases my skills in data management and information visualization using
    data obtained from a custom script I created: [Jupyter Notebook](Data_process/Energy_data_clean.ipynb).

    The dashboard provides an overview of Guatemala's electricity market from 2004 to 2024, allowing
    users to explore electricity generation by technology type across various visualizations.


    You will find two tabs with the following information:
    * **First Tab**: Visualize electricity generation by technology over the years with three types of visualization: Line plot, Boxplot, Heatmap and a Pie Chart.
    * **Second Tab**: Visualize electricity generation by technology over the years with the incorporation of the influence of the Niño–Southern Oscillation on power generation.

    &nbsp;

    **Note: the technology names will be keep in spanish, as the original data is in spanish.**
    > _All credits to the original information can be found on the website: [AMM, Administrator de Mercado Mayorista](https://reportesbi.amm.org.gt)._

    '''

mardown_tab1 = '''
To analyze the behavior of electric power generation plants in Guatemala during the years 2004 - 2024. Three aspects will be analyzed:
* Technology generation over time
* Technology generation per month, with the help of a Heatmap
                        '''

mardown_tab2 = '''
To analyze the behavior of the electric power generation plants in Guatemala during the years 2004 - 2024. The following aspects will be analyzed:
* Influence of the El Niño–Southern Oscillation on power generation
'''

# Text input for the LLM model
context_tab1 = """
You are EnergyAnalyst, a data expert specializing in electricity generation analysis.
Your task is to analyze a filtered dataset and extract 4 key insights as bullet points.
Follow these rules:

1. **Focus on**:
   - Trends (growth/decline)
   - Seasonal patterns
   - Year-over-year comparisons
   - Anomalies (unexpected spikes/drops)

2. **Simplify**: Explain technical terms (e.g., "capacity factor" → "efficiency").
3. **Structure**: Use 4 bullet points for markdown with → emojis for clarity.
4. **Highlight**: Include numbers, percentages, and comparisons to prior years.

Example output for solar data:
📈 → Solar generation grew 15% YoY in 2023, peaking in July (200 GWh).
🌞 → Summer months produced 40% more energy than winter.
🆚 → 2023 output surpassed 2022 by 25 GWh/month on average.
⚠️ → February showed a 30% drop (likely due to panel maintenance).

The information will be: type of technology, years and monthly generation [GWh].
Now analyze this data:
"""

context_tab2 = """
You are ClimateEnergy Analyst, an expert in linking weather patterns to technology performance. 
Analyze the filtered technology generation data with El Niño annotations and provide 4 bullet points:

1. **Focus Areas**:
   - Correlation between El Niño years and generation drops
   - Seasonal/monthly patterns (dry vs. wet seasons)
   - Recovery trends post-El Niño
   - Year-over-year comparisons of anomaly periods

2. **Rules**:
   - Use 🌧️/🔥 emojis for weather impacts
   - Include % changes and GWh values
   - Highlight operational resilience
   - Compare anomaly years to historical averages

Example format:
🌧️ → [Impact description]  
🔥 → [Anomaly effect]  
📆 → [Seasonal pattern]  
🔄 → [Recovery trend]

The information will be in the following format: Technology name is Month, year, generation in GWh and the El Niño–Southern Oscillation.
Example of the data Hidroeléctrica is January, 2004, 100 GWh, -0.98.
Now analyze this data:
"""