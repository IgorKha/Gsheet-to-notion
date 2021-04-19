# -*- coding: utf-8 -*-
#
# SPDX-FileCopyrightText: 2020 IgorKha <hahabahov@yandex.ru>
# SPDX-License-Identifier: GPL-3.0
#
# Send updates from Mesto's Google Sheet to Notion
#
#

# Standard imports
import csv

# Third party packages
import click
import pandas as pd
from notion.client import NotionClient

# Project specific imports
from gsh import googlesheet
from secret import db_file, gsheet_page, notion_key, notion_url, slack_channel
from slack_msg import message


@click.command()
@click.help_option(
    '--help'
    , '-h'
)
@click.version_option(message='%(version)s')
def gsheet2notion():
    client = NotionClient(token_v2=notion_key)

    # We collect the pandas DataFrame and rename the columns to names
    # that correspond to the names of the property in notion
    df = pd.DataFrame(
        googlesheet(gsheet_page))

    df.columns = ['Date', 'Name', 'Email', 'OpenLand', 'Telegram', 'Team_to_help', 'Competence', 'Task', 'Profit',
                  'Why_we', 'work_hour', 'timezone', 'About_me', 'otkuda_uznal', 'CV', 'first_status',
                  'Interview', 'Result']

    # Convert DataFrame to strings
    df = df.astype(str)

    # Convert to a list of dictionaries
    df = pd.DataFrame.to_dict(df, orient='records')

    # Notion, Access a database using the URL of the database page or the inline block
    cv = client.get_collection_view(notion_url)

    # Read csv
    with open(db_file) as f:
        db = [{k: str(v) for k, v in row.items()}
             for row in csv.DictReader(f, skipinitialspace=True)]

    time_check = []
    for i in db:
        time_check.append(i['Date'])

    # We compare the DataFrame with the file using the 'Date' key and write in 'result'
    # and add new pair in dictionary
    result = []
    for i in df:
        if i['Date'] not in time_check:
            result.append(i)
            i.update({'Status': 'Новая'})

    # Write in Notion from result
    for mapping in result:
        row = cv.collection.add_row()
        for key, value in mapping.items():
            setattr(row, key, value)

    # Append in csv file
    try:
        keys = result[0].keys()
        with open(db_file, 'a+', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            # dict_writer.writeheader()
            dict_writer.writerows(result)

        # Collecting names for message in Slack
        namelist = []
        for el in result:
            name = el.get('Name')
            namelist.append(name)

        # Send message in Slack
        msg = ', '.join(namelist)
        message(slack_channel, text=f"New volunteer CV: {msg}")
    except:
        pass

    print('Done')