.. _backtest:

===========
Backtesting
===========

Backtesting is the act of testing a strategy on real chart data from the past.
This can be used to measure the performance of your trading strategy in
comparison to the market.

Doing backtests with cointrader is easy by setting the `backtest` flag::

        cointrader start --backtest --automatic --timeframe 1d --resolution 5m BTC_DASH 0.05                                                                            2.Mär.17 23.21

Despite of this single flag the bot will work as usual. It will trade on the
given market for the defined timeframe and resolution. After the backtest has
finished a small statistic on this trading run is shown::

        2017-03-02 23:21:19,239 INFO  [cointrader.cointrader][MainThread] 2017-03-02 00:35:00: Bought 1.34737233083 for 0.03709999
        2017-03-02 23:21:19,603 INFO  [cointrader.cointrader][MainThread] 2017-03-02 16:50:00: Sold 1.34737233083 for 0.0415 -> 0.0559019727414
        2017-03-02 23:21:19,795 INFO  [cointrader.cointrader][MainThread] Backtest finished

        Statistic:
        Traded from 2017-03-01 23:25:00 until 2017-03-02 22:20:00
        Trading started with a rate of 0.0352397 BTC and ended at 0.03198681 BTC
        Started with 0.05 BTC
        Ended with 0.0559019727414 BTC
        Cointrader makes: 11.8%
        Market makes: -13.78%

