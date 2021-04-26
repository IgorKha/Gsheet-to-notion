# -*- coding: utf-8 -*-
#
# SPDX-FileCopyrightText: 2020 IgorKha <hahabahov@yandex.ru>
# SPDX-License-Identifier: GPL-3.0
#

"""Send updates from Mesto's Google Sheet to Notion."""

# Standard imports
import csv

# Third party packages
import click
import gspread
from notion.client import NotionClient # TODO change to notion-py lib
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
_NAMES_XLAT = {
    'Timestamp': 'Date'
  , 'Представься, пожалуйста (имя и фамилия) ': 'Name'
  , 'Email address': 'Email'
  , 'Как тебя найти в Месте (@... в Openland)': 'OpenLand'
  , 'Оставь контакт в Telegram (или другом мессенджере)': 'Telegram'
  , 'Какой команде ты сможешь помочь?': 'Team_to_help'
  , 'Какие твои профессиональные компетенции?': 'Competence'
  , 'Какие задачи тебе интересны в команде Mesto?': 'Task'
  , 'Что ты хотел бы получить от волонтерского опыта в команде Места?': 'Profit'
  , 'Расскажи нам более подробно о том, почему ты хочешь быть в наших рядах': 'Why_we'
  , 'Каким временем ты располагаешь и готов уделять Месту (часы в неделю)? ': 'work_hour'
  , 'В каком часовом поясе ты живешь?': 'timezone'
  , 'Ну и самое главное: расскажи пару слов о себе)!': 'About_me'
  , 'Откуда ты узнал о возможности попасть в команду Места?': 'otkuda_uznal'
  , 'Прикрепи ссылку на свое резюме ': 'CV'
  , 'Первичный статус ': 'first_status'
  , 'Интервью: кратко ': 'Interview'
  , 'Результат': 'Result'
}
# END Constants


# BEGIN Globals
# TODO Get rid of this!
__wclient = WebClient(token=slack_key)
# END Globals


# BEGIN Internal functions
def _read_google_sheet(sheet):
    """ Read google sheet. """
    g_secret = gspread.service_account(filename='credentials.json')
    g_sheet = g_secret.open_by_url(gsheet_url)              # Open the file by url
    worksheet = g_sheet.worksheet(sheet)                    # Select the sheet inside the file
    return worksheet.get_all_records()


def _send_message_to_slack(chat, text):
    try:
        response = __wclient.chat_postMessage(channel=chat, text=text)
        assert response['message']['text'] == text

    except SlackApiError as e:
        # You will get a SlackApiError if 'ok' is False
        assert e.response['ok'] is False
        assert e.response['error']  # str like 'invalid_auth', 'channel_not_found'
        print(f'Got an error: {e.response["error"]}')
        # TODO Handle the exception properly!
        # TODO Use `logger`
# END Internal functions


@click.command()
@click.help_option(
    '--help'
  , '-h'
  )
@click.version_option(message='%(version)s')
def gsheet2notion():
    """Send updates from Mesto's Google Sheet to Notion."""

    worksheet = _read_google_sheet(gsheet_page)

    source_data = []
    for mapping in worksheet:
        record = {}
        for old_key, new_key in _NAMES_XLAT.items():
            record[new_key] = mapping[old_key]
        source_data.append(record)

    # Notion, Access a database using the URL of the database page or the inline block
    client = NotionClient(token_v2=notion_key)
    notion_cli = client.get_collection_view(notion_url)

    # Read the CSV file
    with open(db_file) as f:
        transformed = [
            {
                k: str(v) for k, v in row.items()
            }
            for row in csv.DictReader(f, skipinitialspace=True)
          ]

    time_check = []
    for i in transformed:
        time_check.append(i['Date'])

    # Compare the `source_data` with records from the file using the `Date`
    # key, write to the `result`, and add a new pair to the dictionary.
    result = []
    for i in source_data:
        if i['Date'] not in time_check:
            result.append(i)
            i.update({'Status': 'Новая'})

    # Write to Notion from the `result`
    for mapping in result:
        row = notion_cli.collection.add_row()
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
          , text=f'New volunteer CV: *{msg}*'
          )

    except Exception:
        AssertionError('Unexpected exception')
        # TODO Handle it properly!

    print('Done')
