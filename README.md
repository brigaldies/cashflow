# Content

This is a set of personal finance management tools to monitor and plan your cash flow.

# Features

## Transactions

The tool reads your planned transactions from an Excel spreadsheet according to the following format:

## Excel Spreadsheet Format

Sheet name: transactions

Columns:

- **item**: Free text description of the transaction (e.g., utility water).
- **enable**: Flag to enable (1) or disable the transaction (0).
- **item_type**: Transaction type ("debit" or "credit").
- **schedule_label**: Free text description of the transaction schedule (e.g., every first of the month).
- **schedule_type**: Transaction schedule type (See explanations below).
- **schedule_start**: Start of the transaction schedule in the yyyy-mm-dd date format.
- **schedule_expr**: Schedule expression (See explanations below).
- **amount**: Transaction amount (float)

### Schedule types


### Schedule Expression

#### Schedule type: "croniter"

A cron expression as supported in the Python package [croniter](https://pypi.org/project/croniter/).

#### Schedule type: "days_in_the_month"

A comma-separated list of days (one or more) in the month, including "last" as a special keyword (e.g., "15,last" for 
the 15th of the month and the last day of the month).

#### Schedule type: "one_time"

Leave the **schedule_expr** column blank, and specify an yyyy-mm-dd date in the **schedule_start** column.

### Excel Spreadsheet Content Example

TODO: Add a table to show transactions examples of various schedule types.

## Jupyter Notebooks

### Notebook: cashflow

The notebook loads the transactions from a specified Excel file pathname, and plots them along a time line from the time
of processing ("now") and a specified number of days in the future.

TODO: Show a screen shot.

# Google Sheets Access

To access your cash flow transactions from a Google sheet instead, follow the instructions in the link below to establish
the access credentials:

See [setup tutorial](https://www.youtube.com/watch?v=7I2s81TsCnc)

# Visualization from Kibana

## Pre-Requisites

Install Docker.

## Docker Compose

From the project's repo root, run the following docker command to start up the Elasticsearch + Kibana runtime environment:

```docker-compose up```

From the command line, check the status of Elasticsearch with the following curl command:

```curl http://127.0.0.1:9200/_cat/health```

## Visualization

1. From your browser, connect to Kibana at [http://localhost:5601](http://localhost:5601).
2. Go to Management, and import the saved Kibana objects (Index patterns, filters, visualizations, and dashboards) from the file kibana_saved_objects_export.json in the project's root directory.

# TODO

- Add a project's root directory parameter in config.cfg so that all directory paths are relative to the project's root.
