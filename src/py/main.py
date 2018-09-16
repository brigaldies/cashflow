import argparse

import expenses.transactions

if __name__ == "__main__":
    """
    Program's main entry point.
    See the arguments in the parser.add_argument() calls below.
    """
    parser = argparse.ArgumentParser(description='Personal Cash Flow Analysis and Reporting.')
    parser.add_argument('-t', '--transactions', help='Transactions Excel file', required=True)

    args = parser.parse_args()

    transactions_df = expenses.transactions.load_transactions(args.transactions, starting_balance=6119.30, days=90)

    print('\nDate-sorted transactions:')
    print(transactions_df.info())
    print(transactions_df.shape)
    print(transactions_df)
