# -*- coding: utf-8 -*-
#
# SPDX-FileCopyrightText: 2020 IgorKha <IgorKha@blah.blah.blah>
# SPDX-License-Identifier: GPL-3.0
#
# Send updates from Mesto's Google Sheet to Notion
#
#

# Third party packages
import click


@click.command()
@click.help_option(
    '--help'
  , '-h'
  )
@click.version_option(message='%(version)s')
def gsheet2notion():
    ''' Send updates from Mesto's Google Sheet to Notion

        TODO Move your code here from ``notion_cli3.py`
    '''
    print('Done')
