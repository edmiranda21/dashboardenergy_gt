# Guatemala's energy generation dashboard

Here you will find the code to deploy the dashboard page with the help of docker. To see a live 
version please visit this [Hugging Face space.](https://huggingface.co/spaces/edmiranda2301/Energy_gt_demo)

The dashboard is a demo of my skills in data visualization and processing. The dashboard is created with 
the use of Plotly and Dash libraries. These libraries were chosen because of their interactive capabilities.
Update added a new feature where the information display will be analyzed by a LLM model, 
in this case the [Google: Gemini 2.0 Flash Experimental ](https://openrouter.ai/google/gemini-2.0-flash-exp:free).

You will find two tabs in this dashboard
* **The first tab** will show the energy generation by 
  source in Guatemala (A single choice dropdown). At the bottom you find an option to receive a analysis by a LLM model.
* **The second tab** will show the energy generation and 
  the ENOS index in Guatemala (A single choice dropdown). At the bottom you find an option to receive a analysis by a LLM model.


<br>

###  **All the cleaning and processing are in jupyter notebook:**
* The [first jupyter notebook](Data_process/Energy_demand_gt_2024.ipynb) is used to extract, load and transform the data from various *csv files, each file represent a year of montly generation of energy by different technologies.
* The [second jupyter notebook](Data_process/Climate.ipynb) is used to extract, load and transform the Information obtained climate for Monthly Niño-3.4 index.
* *Each notebook has a description of the code and the steps to follow to run the code.*

**The data used in this project are from the following sources:**
* [AMM 'Administrator de Mercado Mayorista'](https://reportesbi.amm.org.gt), open data source from Guatemala.
*  Climate for Monthly Niño-3.4 index from [NOAA]( https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/detrend.nino34.ascii.txt)
* Inspired by this book and repository [Modern Time Series Forecasting with Python by Manu Joseph](https://github.com/PacktPublishing/Modern-Time-Series-Forecasting-with-Python)
* Models LLM:  [Google: Gemini 2.0 Flash Experimental ](https://openrouter.ai/google/gemini-2.0-flash-exp:free),
[MoonshotAI: Kimi K2 0711: Free](https://openrouter.ai/moonshotai/kimi-k2:free) or 
[OpenAI: gpt-oss-20b Free](https://openrouter.ai/openai/gpt-oss-20b:free). I choose a three LLM alternatives, is OpenRouter’s solution name Model routing, used when the providers are down or not available.

### Project Structure

```
dashboardenergy_gt/
├── Energy_generation_tabs.py         # Main file to run the dashboard
├── Data_process                      # Jupyter notebooks for data processing
├── csv_files                         # CSV files directory
├── Process                           # Functions, LLM model configuration and prompts
├── Tabs                              # Files for each tab in the dashboard
├── Dockerfile                        # Dockerfile to build the image
├── Profile                           # gunicorn profile directory
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```


## Related Project

### Data Source & Methodology

To avoid manual data collection from the main source, I create this project to scrape the information from the website: [AMM 'Administrator de Mercado Mayorista'](https://reportesbi.amm.org.gt/).
The scrape is capable of extracting energy demand data and generation data categorized by technology type for year in hourly intervals. 

- **Repository**: [Guatemala's energy generation dashboard](https://github.com/edmiranda21/Energy_tool_scrape)

**Key Features:**
- Extracts hourly energy demand data using Playwright
- Extracts generation data categorized by technology type and total generation 
- Available technologies include: Hydroelectric, Wind, Photovoltaic, Geothermal, Reciprocating Engine, Gas Turbine, Steam Turbine, and Import/Export

**Note**: Data extraction requires occasional human intervention due to website instability. This project is designed for educational purposes and should be used in compliance with the AMM website's terms of service.

Check my [**LinkedIn**](http://www.linkedin.com/in/edgar-enrique-miranda-sandoval-a0731294) for more information about me.