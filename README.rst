Dev's Getting Started
=====================

Setting up the developer's environment is easy::

    $ pipenv install --dev --skip-lock

Note, do not use ``--skip-lock`` if your package targeted more than one Python version.

Then you may enter the shell and perform your job::

    $ pipenv shell
    $ pytest
    ...

After install - you need change the limit values in the source library Notion::

    notion/client.py
    notion/store.py
    searching all value: "limit": 1000 or more and change to 100, not more

