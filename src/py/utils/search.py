import configparser
import json
import os

import elasticsearch
import elasticsearch.helpers
from requests.auth import HTTPBasicAuth


def connect(url=None, timeout=1000):
    """
    Connect to Elasticsearch
    :param url: ES URL.
    :param timeout: Connection timeout.
    :param http_auth: Credentials
    :return: Elasticsearch connection handle
    """
    # Read the configuration
    config = configparser.ConfigParser()

    cwd = os.getcwd()
    config_file_pathname = 'settings.cfg'
    print('Current directory: {}'.format(cwd))
    if cwd.endswith('/notebooks'):
        config_file_pathname = '../../../settings.cfg'
    elif cwd.endswith('/py'):
        config_file_pathname = '../../settings.cfg'

    if not os.path.isfile(config_file_pathname):
        raise RuntimeError('Config file "{}" does not exist.'.format(config_file_pathname))
    print('Reading config from {}...'.format(config_file_pathname))
    config.read(config_file_pathname)

    ES_URL = config['DEFAULT']['ES_URL']
    print('ES_URL={}'.format(ES_URL))

    if 'ES_USER' in config['DEFAULT']:
        auth = (config['DEFAULT']['ES_USER'], config['DEFAULT']['ES_PASSWORD'])
        ES_AUTH = HTTPBasicAuth(*auth)
    else:
        auth = None
        ES_AUTH = None
    print('ES_AUTH={}'.format(ES_AUTH))

    if url is None:
        url = ES_URL
    es = elasticsearch.Elasticsearch(url, timeout=timeout, http_auth=ES_AUTH)
    print(json.dumps(es.info(), indent=4))
    return es


def create_index(es, index_name, analysisSettings={}, mappingSettings={}):
    """
    Delete and create an index.
    :param es:
    :param index_name:
    :param analysisSettings:
    :param mappingSettings:
    :return:
    """
    settings = {
        "settings": {
            "number_of_shards": 1,
            "index": {
                "analysis": analysisSettings,
            }
        }
    }

    if mappingSettings:
        settings['mappings'] = mappingSettings

    print('Deleting the index ...')
    es.indices.delete(index_name, ignore=[400, 404])

    print('Creating the index ...')
    es.indices.create(index_name, body=settings)

    pass


def index_transactions(es, index_name, transactions_df):
    """
    Index the transactions.
    :param es: Elasticsearch connection handle.
    :param index_name: Elasticsearch index name.
    :param transactions_df: Transactions dataframe.
    :return: None.
    """

    def bulkTransactions(transactions_df):
        """
        Loop over a transactions dataframe.
        :param transactions_df:
        :return:
        """
        es_doc_id = 0
        for index, row in transactions_df.iterrows():
            transaction_json = {
                'date': index,
                'item': row['item'],
                'item_type': row['item_type'],
                'amount': row['amount'],
                'balance': row['balance']

            }
            addCmd = {"_index": index_name,
                      "_type": "transaction",
                      "_id": es_doc_id,
                      "_source": transaction_json}
            es_doc_id += 1
            print('Indexing: {}'.format(addCmd))
            yield addCmd

    elasticsearch.helpers.bulk(es, bulkTransactions(transactions_df))


if __name__ == "__main__":
    es = connect()
    create_index(es, "cashflow")
