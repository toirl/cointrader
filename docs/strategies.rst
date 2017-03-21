.. _backtest:

===========
Backtesting
===========

Backtesting is the act of testing a strategy on real chart data from the past.
This can be used to measure the performance of your trading strategy in
comparison to the market.

Doing backtests with cointrader is easy by setting the `--backtest` flag::

        cointrader start \
                --backtest \
                --strategy Trend \
                --resolution 2h \
                --automatic \
                --coins 10 \
                --start "2017-03-18 00:00:00" \
                --end "2017-03-21 19:00:00" \
                BTC_DASH

Despite of this single flag the bot will work as usual. It will trade on the
given market for the defined timeframe and resolution. After the backtest has
finished a small statistic on this trading run is shown::

        2017-03-21 22:18:39,411 INFO  [cointrader.bot][MainThread] Creating new bot BTC_DASH
        2017-03-21 22:18:40,405 INFO  [cointrader.bot][MainThread] 2017-03-18 00:00:00: INIT 0.0 BTC 10.0 COINS
        2017-03-21 22:18:40,604 INFO  [cointrader.bot][MainThread] 2017-03-21 00:00:00: SELL 10.0 @ 0.09662999 earned -> 0.966058325025 BTC
        2017-03-21 22:18:40,662 INFO  [cointrader.bot][MainThread] Backtest finished

At the end the tradelog will be displayed to see the trading activity of the
bot::

        Tradelog:
        +---------------------+------+------------+-------+--------+-----+----------------+
        | DATE                | TYPE | RATE       | COINS | COINS' | BTC | BTC'           |
        +---------------------+------+------------+-------+--------+-----+----------------+
        | 2017-03-18 00:00:00 | INIT | 0.0881     | 10.0  | --     | 0.0 | --             |
        | 2017-03-21 00:00:00 | SELL | 0.09662999 | 10.0  | --     | --  | 0.966058325025 |
        +---------------------+------+------------+-------+--------+-----+----------------+

And finally a statistic of the performance of the strategy is shown::

        Statistic:
        +------------+---------------------+---------------------+----------+
        |            | 2017-03-18 00:00:00 | 2017-03-21 18:00:00 | CHANGE % |
        +------------+---------------------+---------------------+----------+
        | COINTRADER | 0.881               | 0.966058325025      | 8.8047   |
        | MARKET     | 0.881               | 0.8361              | -5.3702  |
        +------------+---------------------+---------------------+----------+

The statistic compares the performance of the bot with the market evaluation.
This is done by comparing BTC values. The value is defined as::

        value = amount of coins * rate + btc

The rate refers to the current rate of the market at the begin and the end of
the timeframe.

This makes it easy to see if the bot makes more or less money for you.
