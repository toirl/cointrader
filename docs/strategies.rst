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
                --automatic \
                --start "2017-03-01 00:00:00" \
                --end "2017-03-16 08:00:00" \
                --btc 1.0 \
                --coins 1 \
                BTC_DASH

Despite of this single flag the bot will work as usual. It will trade on the
given market for the defined timeframe and resolution. After the backtest has
finished a small statistic on this trading run is shown::

        2017-03-16 12:03:32,075 INFO  [cointrader.bot][MainThread] Creating new bot BTC_DASH
        2017-03-16 12:03:32,640 INFO  [cointrader.bot][MainThread] 2017-03-01 00:00:00: INIT 1.0 BTC 1.0 COINS
        2017-03-16 12:03:32,658 INFO  [cointrader.bot][MainThread] Backtest finished

At the end the tradelog will be displayed to see the trading activity of the
bot::

        Tradelog:
        +---------------------+------+------------+-------+--------+-----+------+
        | DATE                | TYPE | RATE       | COINS | COINS' | BTC | BTC' |
        +---------------------+------+------------+-------+--------+-----+------+
        | 2017-03-01 00:00:00 | INIT | 0.02748946 | 1.0   | --     | 1.0 | --   |
        +---------------------+------+------------+-------+--------+-----+------+

And finally a statistic of the performance of the strategy is shown::

        Statistic:
        +------------+---------------------+---------------------+----------+
        |            | 2017-03-01 00:00:00 | 2017-03-16 08:00:00 | CHANGE % |
        +------------+---------------------+---------------------+----------+
        | COINTRADER | 1.02748946          | 1.0738834           | 4.3202   |
        | MARKET     | 1.02748946          | 1.0738834           | 4.3202   |
        +------------+---------------------+---------------------+----------+

The statistic compares the performance of the bot with the market evaluation.
This is done by comparing BTC values. The value is defined as::

        value = amount of coins * rate + btc

The rate refers to the current rate of the market at the begin and the end of
the timeframe.

This makes it easy to see if the bot makes more or less money for you.
