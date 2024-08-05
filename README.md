# Guatemala's energy generation dashboard

Here you will find the code to deploy the dashboard page with the help of docker. To see a live 
version please visit this [Hugging Face space.](https://huggingface.co/spaces/edmiranda2301/Energy_gt_demo)

The dashboard is a demo of my skills in data visualization and processing. The dashboard is created with 
the use of Plotly and Dash libraries. This libraries were chosen because of their interactive capabilities.

You will find two tabs in this dashboard
* **The first tab** will show the energy generation by 
  source in Guatemala (A single choice dropdown)
* **The second tab** will show the energy generation and 
  the ENOS index in Guatemala (A single choice dropdown)


<br>

###  **All the cleaning and processing are in jupyter notebook:**
* The [first jupyter notebook](Data_process/Energy_data_clean.ipynb) is used to extract, load and transform the data from various *csv files, each file represent a year of montly generation of energy by different technologies.
* The [second jupyter notebook](Data_process/Climate.ipynb) is used to extract, load and transform the Information obtained climate for Monthly Niño-3.4 index.
* *Each notebook has a description of the code and the steps to follow to run the code.*

**The data used in this project are from the following sources:**
* [AMM 'Administrator de Mercado Mayorista'](https://reportesbi.amm.org.gt), open data source from Guatemala.
*  Climate for Monthly Niño-3.4 index from [NOAA]( https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/detrend.nino34.ascii.txt)
* Inspired by this book and repository [Modern Time Series Forecasting with Python by Manu Joseph](https://github.com/PacktPublishing/Modern-Time-Series-Forecasting-with-Python)

Check my [**LinkedIn**](http://www.linkedin.com/in/edgar-enrique-miranda-sandoval-a0731294) for more information about me.