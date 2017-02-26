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

To get general help to the application please use the help flag::

        cointrader --help

Trading
-------
Cointrader can start its trading activity by using the following command::

        contrader start BTC_DASH

Cointrader expects a valid currency pair as argument to the start command.
Please not that the naming of the currency pair is depended on the configured
exchange.

Without any further arguments cointrader will start an interactive trading
session. Cointrader will emit trading signals (BUY, WAIT, SELL) and waits for
your decision what to do.

The trading signals are based on a technical
analysis with the default trading strategy on a candlestick chart of the last
24H in a 30 minutes resolution.

The time frame can be changed by using the `--timeframe` option. See `--help`
for more information.

The resolution can be changed by using the `--resolution` option. See `--help`
for more information.

If you want to start your trading session in a automatic session you can set
the `--automatic` flag. Cointrader will then automatically take action on the
emitted trading signals. In automatic mode the resolution will determine
between two trading actions.

Balance
-------
Cointrader can show your current balance at the configured exchange by
invoking the balance command::

        contrader balance

This will give you an output like this::

        CUR          total    btc_value
        -------------------------------
        DASH:  14.34446293   0.34583237
        BTC :   0.04910656   0.04910656
        -------------------------------
        TOTAL BTC:           0.39493893
        TOTAL USD:        465.392085719


Explore
-------
Cointrader can explore the different markets on the given exchange and will
result the most interesting markets to trade on for the last 24H::

        contrader explore

On default cointrader will look for the top three volume and profit markets and
only lists those markets which are in the top three in both categories. The command
will give you an output like this::

        BTC_DASH     4.47%     2190.7 https://poloniex.com/exchange#btc_dash
        BTC_ETH      3.21%     5138.0 https://poloniex.com/exchange#btc_eth

If the command gives no output means that there are no markets in the top three
which met bot critera. In this sitution you can either use the `--top`
attribute to increase the amount of markets which are consired as interesting.

Alternatively you can use the `--order-by-volume` and `--order-by-profit` flag
to only look on profit or volume markets.

