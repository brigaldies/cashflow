# For Google API credentials: See tutorial https://www.youtube.com/watch?v=7I2s81TsCnc
# For gspread API: See README at https://github.com/burnash/gspread

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# DO NOT CHECK-IN!
google_api_file = 'cashflow-e30812754233.json'


def gspread_load_transactions(debug=False):
    print('Retrieve Google API credentials...')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(google_api_file, scope)

    print('Authorizing with Google API credentials...')
    gc = gspread.authorize(credentials)

    gspreadsheet_name = 'transactions'
    print('Reading all records from Google spreadsheet {}...'.format(gspreadsheet_name))
    wks = gc.open(gspreadsheet_name).sheet1
    records = wks.get_all_records()

    print('Loading records into a data frame...')
    df = pd.DataFrame(
        columns=[
            'item',
            'enabled',
            'item_type',
            'schedule_label',
            'schedule_type',
            'schedule_start',
            'schedule_expr',
            'amount'
        ]
    )
    df_idx = 0
    for record in records:
        df.loc[df_idx] = [
            record['item'],
            record['enabled'],
            record['item_type'],
            record['schedule_label'],
            record['schedule_type'],
            record['schedule_start'],
            str(record['schedule_expr']),
            record['amount']
        ]
        df_idx += 1

    if debug:
        print('{} records read.'.format(df.shape[0]))
        print(df.info())

    return df


if __name__ == "__main__":
    df = gspread_load_transactions()
    print(df.info())
    print(df)
