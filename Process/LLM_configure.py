from dash import dcc, Input, Output, State
from dotenv import load_dotenv
# from huggingface_hub import InferenceClient
from openai import OpenAI
from Process.Text import context_tab1, context_tab2
from Process.Functions import extract_data_chart_tab1, build_llm_payload_tab1,build_llm_payload_tab2
import os

# Hugging Face API
load_dotenv()

token_openai = os.environ.get('OPENAI_API_KEY')
model = "openai/gpt-oss-20b:free"

client_openai = client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=token_openai,
)

# Text input for the LLM model
def set_message(context_tab,text_input_model):
    message = [
        {'role': "system", "content": context_tab},
        {"role": "user", "content": text_input_model}
    ]

    completion = client.chat.completions.create(extra_headers={"HTTP-Referer":"https://huggingface.co/spaces/edmiranda2301/Energy_gt_demo",
                                                               "X-Title": "Energy_Dashboard"},
                                                model=model,
                                                messages=message,
                                                max_tokens=3500,
                                                temperature=0)


    return completion.choices[0].message.content

# Send the analysis to the LLM model
def send_analysis(clicks, store_data, context_tab, extract_data_chart_tab, store_data_distribution=None):
    if clicks is None or clicks == 0:
        return 'No analysis generated', False

    if clicks == 3:
        message = '❌You have reached the limit of 2 analysis'
        return message, True

    if store_data_distribution is None:
        # message = f'{extract_data_chart_tab(store_data)}'
        message = f'{set_message(context_tab, extract_data_chart_tab(store_data))}'
        return dcc.Markdown(message, style={"fontSize": "18px"}), False
    else:
        # message = f'{extract_data_chart_tab(store_data, store_data_distribution)}'
        message = f'{set_message(context_tab, extract_data_chart_tab(store_data, store_data_distribution))}'
        return dcc.Markdown(message, style={"fontSize": "18px"}), False

# Obtain information from the current dashboard
def update_information_tab1(app):
    @app.callback(
        [Output('loading-tab1', 'children'),
         Output('button_analysis_tab1', 'disabled')],
        Input('button_analysis_tab1', 'n_clicks'),
        [State('data-store-tab1', 'data'),
         State('data-store-distribution-tab1', 'data')])

    def update_analysis(clicks, store_data, store_data_distribution):
        return send_analysis(clicks, store_data, context_tab1, build_llm_payload_tab1, store_data_distribution)


def update_information_tab2(app):
    @app.callback([Output('loading-tab2', 'children'),
                   # Output('chatbot-responsetab2', 'children'),
                   Output('button_analysis', 'disabled')],
                  Input('button_analysis', 'n_clicks'),
                  State('data-store', 'data'))
    def update_analysis(clicks, store_data):
        return send_analysis(clicks, store_data, context_tab2, build_llm_payload_tab2)