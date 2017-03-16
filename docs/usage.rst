=====
Usage
=====
The cointrader application is CLI application and provides some basic commands
which are hopefully useful for your daily trading activity.

To get general help to the application please use the help flag::

        cointrader --help

Trading
-------
You can start trading by using the following command. Cointrader expects a
valid currency pair as argument and the start amount of BTC to the start
command. Please not that the naming of the currency pair is depended on the
configured exchange.::

        cointrader start BTC_DASH

Cointrader will try to load a previously created bot for the given market from
the database and build the current state of the bot from the trade log. If no
bot can be loaded a new bot will be created. 

You can restrict the amount of coins and BTC the bot will use on trading by
setting the `--btc` or `--coins` parameter. This will set the the initial
amount of BTC and coins the bot will use for trading.  **Tip:** You can use
the :ref:`exchange_command` to calculate the amount of BTC from given dollar.

.. warning::

        On default cointrader will use use the complete available amount of BTC and
        coins for trading for the new bot! Make sure you restrict the amount
        of coins and BTC the bot will use for trading!


With no further options cointrader will work on a chart with a resolution of
30min. The resolution can be changed by using the `--resolution` option. 

You can set a timeframe to define the trading time of cointrader.
A start and end of the timeframe can be set by using the `--start` and `--end`
option which takes a datetime argument in the format "YYYY-MM-DD HH:MM:SS".
On default cointrader will start to trade immediately and will trade until you
stop cointrader.

.. index::
   single: Strategy

Cointrader use different trading strategies. You can choose which strategy to
use by setting the `--strategy` option. On default cointrader will use a very
defensive "Wait-Strategy" which will only emit "Wait" signals. So no buys or
sells a replaced.

.. note::

        Cointrader currently has no working trading strategy. It is the
        current objectiv of the defvelopment to come up with a working
        profitable strategy.


.. index::
   single: Backtest

Trading can be done in backtest mode. To start trading in backtest
mode set the `--backtest` flag. See :ref:`backtest` for more details.

.. index::
   single: Papertrading 

Paper Trade
^^^^^^^^^^^
A paper trade is a simulated trade. Cointrader can simlate buying and selling
coins without actual involiving real money. This is great to test you trading
strategy without any risk.
To start cointrader in paper trade mode you must set the `--papertrade` flag.

.. index::
   single: interactive trading

Interactive trading
^^^^^^^^^^^^^^^^^^^
Without any further arguments cointrader will start an *interactive trading
session*. Cointrader will emit trading signals (BUY, WAIT, SELL) and waits for
your decision what to do.

Automatic trading
^^^^^^^^^^^^^^^^^
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
which met bot criteria. In this situation you can either use the `--top`
attribute to increase the amount of markets which are considered as interesting.

Alternatively you can use the `--order-by-volume` and `--order-by-profit` flag
to only look on profit or volume markets.

.. _exchange_command:

Exchange
--------
Exchange is a simple helper command to calculate how many BTC you get for a
certain amount of USD::

        cointrader change 50                                                                                                     2.Mär.17 23.09
        -> 50.0$ ~ 0.03999086BTC # 2017-03-02
