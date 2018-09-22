import calendar
import datetime

import croniter
import numpy as np
import pandas as pd


def load_transactions(transactions_df, starting_balance, days=30, debug=False):
    """
    Load the raw transactions into a Pandas data frame sorted and indexed by transaction date asc.
    :param transactions_df: Data frame that contains the raw transactions.
    :param days: Number of days in the future to build the transactions for.
    :param debug: Debug flag.
    :return: A Pandas dataframe that contains the transactions for the next <days> days.
    """
    tx_df = pd.DataFrame(
        columns=[
            'date',
            'date_ts',
            'item',
            'item_type',
            'amount',
            'balance'
        ]
    )

    print('Transactions count: {}'.format(transactions_df.shape[0]))
    print('Starting balance  : {}'.format(np.round(starting_balance, 2)))
    print('Days in the future: {}'.format(days))
    now = datetime.datetime.now()
    end_date = now + datetime.timedelta(days=days)
    print('Date interval     : From {} to {}'.format(now, end_date))

    # Process each row
    for index, row in transactions_df.iterrows():
        if debug: print('\n{}: {}'.format(index, row))

        if not int(row['enabled']):
            print('Row {} disabled.'.format(row))
            continue

        schedule_type = str(row['schedule_type']).lower()

        # Schedule type: Interval
        if schedule_type == 'interval':
            add_transactions_interval(row, days, end_date, tx_df, debug)

        # Schedule type: Twice a month
        elif schedule_type == 'days_in_month':
            add_transactions_twice_a_month(row, days, end_date, tx_df, debug)

        # Schedule: croniter
        elif schedule_type == 'croniter':
            add_transactions_cronite(row, days, end_date, tx_df, debug)

        # Schedule: croniter
        elif schedule_type == 'one_time':
            add_transactions_one_time(row, days, end_date, tx_df, debug)

        # Unsupported!
        else:
            raise RuntimeError('Schedule type "{}" not supported.'.format(schedule_type))

    # Sort the transactions by date ascending:
    tx_df.sort_values(by=['date', 'item'], inplace=True)
    tx_df.reset_index(drop=True, inplace=True)

    for i in np.arange(0, tx_df.shape[0]):
        multiplier = 1
        item_type = str(tx_df.loc[i, 'item_type']).lower()
        if not item_type in ('debit', 'credit'):
            raise RuntimeError('Unsupported transaction type "{}"'.format(tx_df.loc[i, 'item_type']))
        if item_type == 'debit':
            multiplier = -1

        if i == 0:
            tx_df.loc[i, 'balance'] = starting_balance + tx_df.loc[i, 'amount'] * multiplier
        else:
            tx_df.loc[i, 'balance'] = tx_df.loc[i - 1, 'balance'] + tx_df.loc[i, 'amount'] * multiplier

    # Set the date column as the index to create a time series
    tx_df.set_index('date', inplace=True)

    # Display some stats
    print('Starting balance: {}'.format(np.round(starting_balance, 2)))
    print('Min balance     : {}'.format(np.round(np.min(tx_df['balance']), 2)))
    print('Max balance     : {}'.format(np.round(np.max(tx_df['balance']), 2)))
    print('Max average     : {}'.format(np.round(np.average(tx_df['balance']), 2)))

    # Return the transactions data frame
    return tx_df


def add_transactions_interval(row, days, end_date, tx_df, debug=False):
    """
    Add transactions of type 'interval'.
    :param row: Transaction row.
    :param days: Number of days into the future.
    :param end_date: Last date in the future.
    :param tx_df: Data frame to add the transactions to.
    :param debug: Debug flag.
    :return: None.
    """
    now = datetime.datetime.now()
    start_date = datetime.datetime.strptime(row['schedule_start'], "%Y-%m-%d")
    if debug: print('Schedule start: {}'.format(start_date))
    tx_df_idx = tx_df.shape[0]
    for i in np.arange(1, days):
        interval = datetime.timedelta(days=int(i) * int(row['schedule_expr']))
        next_date = start_date + interval
        if next_date < now:
            continue
        if next_date <= end_date:
            if debug: print('\t[{}] Next event: {}'.format(i, next_date))
            tx_df.loc[tx_df_idx] = [
                next_date,
                next_date.timestamp(),
                row['item'],
                row['item_type'],
                row['amount'],
                0
            ]
            tx_df_idx += 1
        else:
            break


def add_transactions_twice_a_month(row, days, end_date, tx_df, debug=False):
    """
    Add transactions of type 'twice_a_month'.
    :param row: Transaction row.
    :param days: Number of days into the future.
    :param end_date: Last date in the future.
    :param tx_df: Data frame to add the transactions to.
    :param debug: Debug flag.
    :return: None.
    """
    now = datetime.datetime.now()
    sched_expr = str(row['schedule_expr'])
    tokens = sched_expr.split(',')
    tx_df_idx = tx_df.shape[0]
    for day_str in tokens:
        day_str = day_str.strip()
        if day_str.isdigit():
            day = int(day_str)
            # TODO: Check that the digit <= 28
            cron_expr = '0 0 {} * *'.format(day)
            cron = croniter.croniter(cron_expr, now)
            for i in np.arange(1, days):
                next_date = cron.get_next(datetime.datetime)
                if next_date < now:
                    continue
                if next_date <= end_date:
                    if debug: print('\t[{}] Next event: {}'.format(i, next_date))
                    tx_df.loc[tx_df_idx] = [
                        next_date,
                        next_date.timestamp(),
                        row['item'],
                        row['item_type'],
                        row['amount'],
                        0
                    ]
                    tx_df_idx += 1
                else:
                    break

        elif day_str.strip() == 'last':
            month = now.month
            year = now.year
            for i in np.arange(1, days):
                month_range = calendar.monthrange(year, month)
                next_date = datetime.datetime(year, month, month_range[1])
                if next_date < now:
                    continue
                if next_date <= end_date:
                    if debug: print('\t[{}] Next event: {}'.format(i, next_date))
                    tx_df.loc[tx_df_idx] = [
                        next_date,
                        next_date.timestamp(),
                        row['item'],
                        row['item_type'],
                        row['amount'],
                        0
                    ]
                    tx_df_idx += 1
                    month = (month + 1) % 13
                    if month == 0:
                        month += 1
                        year += 1
                else:
                    break
        else:
            raise RuntimeError('Unsupported "days_in_month" schedule expression syntax "{}".'.format(sched_expr))


def add_transactions_cronite(row, days, end_date, tx_df, debug=False):
    """
    Add transactions of type 'cronite'.
    :param row: Transaction row.
    :param days: Number of days into the future.
    :param end_date: Last date in the future.
    :param tx_df: Data frame to add the transactions to.
    :param debug: Debug flag.
    :return: None.
    """
    now = datetime.datetime.now()
    cron = croniter.croniter(str(row['schedule_expr']), now)
    tx_df_idx = tx_df.shape[0]
    for i in np.arange(1, days):
        next_date = cron.get_next(datetime.datetime)
        if next_date < now:
            continue
        if next_date <= end_date:
            if debug: print('\t[{}] Next event: {}'.format(i, next_date))
            tx_df.loc[tx_df_idx] = [
                next_date,
                next_date.timestamp(),
                row['item'],
                row['item_type'],
                row['amount'],
                0
            ]
            tx_df_idx += 1
        else:
            break


def add_transactions_one_time(row, days, end_date, tx_df, debug=False):
    """
    Add transactions of type 'one_time'.
    :param row: Transaction row.
    :param days: Number of days into the future.
    :param end_date: Last date in the future.
    :param tx_df: Data frame to add the transactions to.
    :param debug: Debug flag.
    :return: None.
    """
    now = datetime.datetime.now()
    tx_df_idx = tx_df.shape[0]
    next_date = datetime.datetime.strptime(row['schedule_start'], "%Y-%m-%d")
    if next_date >= now and next_date <= end_date:
        tx_df.loc[tx_df_idx] = [
            next_date,
            next_date.timestamp(),
            row['item'],
            row['item_type'],
            row['amount'],
            0
        ]
