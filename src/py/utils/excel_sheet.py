import pandas as pd


def excel_load_transactions(local_computer_pathname, debug=False):
    print('Loading transactions from pathname {}...'.format(local_computer_pathname))

    # Load the Excel file
    xlsx = pd.ExcelFile(local_computer_pathname)

    # Load the designated Excel sheet into a Pandas data frame
    df = pd.read_excel(xlsx, sheet_name='transactions', header=1)

    if debug:
        print('{} records read.'.format(df.shape[0]))
        print(df.info())

    return df
