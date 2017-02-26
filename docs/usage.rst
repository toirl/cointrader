=============
Configuration
=============
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


=====
Usage
=====
The cointrader application is CLI application and provides some basic commands
which are hopefully usefull for your daily trading activity.

Getting help
------------
To get general help to the application please use the help flag::

        cointrader --help

Show current balance
--------------------
Cointrader can show yoyur current balance at the configured exchange by
invoking the balance command::

        contrader balance

Explore markets
---------------
Cointrader can explore the different markets on the given exchange and will
result the most interesting markets to trade on for the last 24H.

A market is considered interesting if it has a high trading volume and it has
a large positive change in its rate. Only markets which are in the TOP 5 in
both categories are listed on default.::

        contrader explore

General help to the application can be always shown be invoking contrainder
cointrader command.
G

Trading
-------
Contraider can start its trading activity by using the following command::

        contrader start BTC_DASH

This will start the cointrader bot in interactive mode.
