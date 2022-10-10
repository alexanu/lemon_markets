# this file is used for testing functions via functions-framework before deploying it to GCF
# Functions Framework https://cloud.google.com/functions/docs/functions-framework
    # Video from PTL: https://www.youtube.com/watch?v=j1_lqxsdJ8E
    # FF for Python: https://github.com/GoogleCloudPlatform/functions-framework-python
        # pip install functions-framework
        # create function "def submit_custom_order(request):" in main.py
        # functions-framework --target=submit_custom_order
            # functions-framework --target submit_custom_order --debug
            # the result will appear on localhost:8080
        # Install Insomnia for testing API requests => Create Request Collection => Create New Request (POST, JSON)
        # Put "localhost:8080" in URL field near "Send Button"
        # Enter JSON which will be send to localhost and envoke function submit_custom_order => output will appear on the right
        # after success, deploy to GCF. You will get an url of the function. Put this url into insomnia for testing

# GCF URL: https://europe-west3-lemon-trading.cloudfunctions.net/lemon-manual-trade

# {
# 	"symbol":"IE00B3YCGJ38",
# 	"investment":1000,
# 	"side":"buy",
# 	"passphrase": "XXXXXXX"
# }

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd
import json


def google_sheet_call(request):

    with open('lemon-trading-google-sheets-creds.json') as f:
        gs_creds = json.load(f)

    gs_creds['private_key'] = gs_creds['private_key'].replace('\\n', '\n')

    # Connect to Google Sheets
    scope = ['https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive']
    
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(gs_creds, scope)
    client = gspread.authorize(credentials)
    sheet = client.open("lemon-trading").worksheet("risk_mgmt")
    df = pd.DataFrame(sheet.get_all_records())
    invest = df[(df.strategy=="manual_trade") & (df.parameter=="max_capital")].value[0]

    return {
        "code": "trade done",
        "invested": invest
    }
