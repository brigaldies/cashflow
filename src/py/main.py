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
    parser.add_argument('-t', '--transactions', help='Transactions Excel file', required=True)

    args = parser.parse_args()

    # Load the transactions from an Excel sheet
    # raw_transactions_df = excel_sheet.excel_load_transactions(args.transactions, debug=True)

    # Load the transactions from a Google sheet
    raw_transactions_df = google_sheet.gspread_load_transactions()

    transactions_df = expenses.transactions.load_transactions(raw_transactions_df, starting_balance=6119.30, days=90, debug=True)

    print('\nDate-sorted transactions:')
    print(transactions_df.info())
    print(transactions_df.shape)
    print(transactions_df)
