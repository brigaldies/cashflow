import argparse

import expenses.transactions
import utils.excel_sheet as excel_sheet
import utils.google_sheet as google_sheet

if __name__ == "__main__":
    """
    Program's main entry point.
    See the arguments in the parser.add_argument() calls below.
    """
    parser = argparse.ArgumentParser(description='Personal Cash Flow Analysis and Reporting.')
    parser.add_argument('-t', '--transactions', help='Transactions Excel file', required=False)
    parser.add_argument('-g', '--googleapikey', help='Google API key file pathname', required=False)

    args = parser.parse_args()

    if not args.transactions and not args.googleapikey:
        raise RuntimeError('Missing command-line arguments.')

    # Load the transactions from an Excel sheet
    raw_transactions_df = None
    if args.transactions and not args.googleapikey:
        raw_transactions_df = excel_sheet.excel_load_transactions(args.transactions, debug=False)
    else:
        # Load the transactions from a Google sheet
        raw_transactions_df = google_sheet.gspread_load_transactions(
            google_api_file_pathname=args.googleapikey)

    transactions_df = expenses.transactions.load_transactions(raw_transactions_df, starting_balance=6119.30, days=90, debug=False)

    print('\nDate-sorted transactions:')
    print(transactions_df.info())
    print(transactions_df.shape)
    print(transactions_df)
