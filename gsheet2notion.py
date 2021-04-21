# -*- coding: utf-8 -*-
#
# SPDX-FileCopyrightText: 2020 IgorKha <hahabahov@yandex.ru>
# SPDX-License-Identifier: GPL-3.0
#

"""Send updates from Mesto's Google Sheet to Notion."""

# Standard imports
import csv
from typing import Final, List

# Third party packages
import click
import gspread
import pandas as pd
from notion.client import NotionClient
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Project specific imports
from secret import (
    db_file,
    gsheet_page,
    gsheet_url,
    notion_key,
    notion_url,
    slack_channel,
    slack_key
)

# BEGIN Constants
_COLUMNS: Final[List[str]] = [
    'Date'
  , 'Name'
  , 'Email'
  , 'OpenLand'
  , 'Telegram'
  , 'Team_to_help'
  , 'Competence'
  , 'Task'
  , 'Profit'
  , 'Why_we'
  , 'work_hour'
  , 'timezone'
  , 'About_me'
  , 'otkuda_uznal'
  , 'CV'
  , 'first_status'
  , 'Interview'
  , 'Result'
  ]
# END Constants


# BEGIN Globals
# TODO Get rid of the globals!
# class slackmessage:
wclient = WebClient(token=slack_key)
# END Globals


# BEGIN Internal functions
def _read_google_sheet(sheet):
    """ Read google sheet. """
    gc = gspread.service_account(filename='credentials.json')
    sh = gc.open_by_url(gsheet_url)                         # Open the file by url
    worksheet = sh.worksheet(sheet)                         # Select the sheet inside the file
    return worksheet.get_all_records()


def _send_message_to_slack(chat, text):
    try:
        response = wclient.chat_postMessage(channel=chat, text=text)
        assert response['message']['text'] == text

    except SlackApiError as e:
        # You will get a SlackApiError if 'ok' is False
        assert e.response['ok'] is False
        assert e.response['error']  # str like 'invalid_auth', 'channel_not_found'
        print(f'Got an error: {e.response["error"]}')
        # TODO Handle the exception properly!
# END Internal functions


@click.command()
@click.help_option(
    '--help'
  , '-h'
  )
@click.version_option(message='%(version)s')
def gsheet2notion():
    """Send updates from Mesto's Google Sheet to Notion."""

    # We collect the pandas DataFrame and rename the columns to names
    # that correspond to the names of the property in notion
    df = pd.DataFrame(_read_google_sheet(gsheet_page))

    df.columns = _COLUMNS

    # Convert DataFrame to strings
    df = df.astype(str)

    # Convert into a list of dictionaries
    df = pd.DataFrame.to_dict(df, orient='records')

    # Notion, Access a database using the URL of the database page or the inline block
    client = NotionClient(token_v2=notion_key)
    cv = client.get_collection_view(notion_url)

    # Read the CSV file
    with open(db_file) as f:
        db = [
            {
                k: str(v) for k, v in row.items()
            }
            for row in csv.DictReader(f, skipinitialspace=True)
          ]

    time_check = []
    for i in db:
        time_check.append(i['Date'])

    # Compare the `DataFrame` with records from the file using the `Date`
    # key, write to the `result`, and add a new pair to the dictionary.
    result = []
    for i in df:
        if i['Date'] not in time_check:
            result.append(i)
            i.update({'Status': 'Новая'})

    # Write to Notion from the `result`
    for mapping in result:
        row = cv.collection.add_row()
        for key, value in mapping.items():
            setattr(row, key, value)

    # Append to the CSV file
    try:
        keys = result[0].keys()
        with open(db_file, 'a+', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            # TODO Write the header to make the result file a bit more
            # human-friendly but skip the first record on read.
            # dict_writer.writeheader()
            dict_writer.writerows(result)

        # Collecting names and send message to Slack
        # TODO Move out of `try`
        msg = ', '.join(map(lambda item: item.get('Name'), result))
        _send_message_to_slack(
            slack_channel
          , text=f'New volunteer CV: {msg}'
          )

    except Exception:
        AssertionError('Unexpected exception')
        # TODO Handle it properly!

    print('Done')
