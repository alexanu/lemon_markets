import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd
import json


def lemon_manual_trade(request):

    with open('lemon-trading-google-sheets-creds.json') as f:
        gs_creds = json.load(f)

    # Connect to Google Sheets
    scope = ['https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(gs_creds, scope)
    client = gspread.authorize(credentials)
    sheet = client.open("lemon-trading").worksheet("risk_mgmt")
    df = pd.DataFrame(sheet.get_all_records())
    invest = df[(df.strategy=="manual_trade") & (df.parameter=="max_capital")].value[0]

    return {
        "code": "trade done",
        "invested": invest
    }
