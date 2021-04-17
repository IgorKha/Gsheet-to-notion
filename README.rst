Dev's Getting Started
=====================

Setting up the developer's environment is easy::

    $ pipenv install --dev --skip-lock

Note, do not use ``--skip-lock`` if your package targeted more than one Python version.

Then you may enter the shell and perform your job::

    $ pipenv shell
    $ pytest
    ...

