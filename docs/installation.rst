.. highlight:: shell

============
Installation
============


Stable release
--------------

To install Cointrader, run this command in your terminal:

.. code-block:: console

    $ pip install cointrader

This is the preferred method to install Cointrader, as it will always install the most recent stable release. 

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for Cointrader can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/toirl/cointrader

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/toirl/cointrader/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/toirl/cointrader
.. _tarball: https://github.com/toirl/cointrader/tarball/master

Configuration
-------------
Contraider uses a configuration file to set some important settings like the
key and the secret for the API on the configured exchange. A configuration
looks like this and must be located in your `$HOME` directory with the filename
`.cointrader.ini`. Please make sure you have created a configuration file.::

        [DEFAULT]
        # Set default exchange which will be used for trading.
        # Currently onyl Poloniex is supported!
        exchange = poloniex

        [poloniex]
        # See https://poloniex.com/apiKeys for more details.
        api_key = YOUR-API-KEY-HERE
        api_secret = YOUR-API-SECRET-HERE

        #
        ## Default logging configuration of the application.
        #
        [loggers]
        keys = root, cointrader

        [handlers]
        keys = console

        [formatters]
        keys = generic

        [logger_root]
        level = ERROR
        handlers = console

        [logger_cointrader]
        level = INFO
        handlers =
        qualname = cointrader

        [handler_console]
        class = StreamHandler
        args = (sys.stderr,)
        level = NOTSET
        formatter = generic

        [formatter_generic]
        format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s


