=======
History
=======

0.4.0 (2017-03-16)
------------------
First version with real trading functionality. However **cointrader has no
working trading strategy yet**. So the default strategy will do nothing than
waiting :). However you can use the interactive mode to buy and sell coins if
you want to.

* Added automatic trading. Cointrader will follow the emitted signals from the
  strategy.
* Added Papertrading. Do trading without any risk. Cointrader will simulate
  trading.
* Added Tradelog.

0.3.1 (2017-03-11)
------------------
Bugfix release.

* Fixed issue #4 (https://github.com/toirl/cointrader/issues/4)
  - Use absolute imports.
  - Renamed contrader modul into bot to prevent namespace issues.
  - Added missing requirement of the 'requests' package.

0.3.0 (2017-03-02)
------------------
* Added backtest functionality. Cointrader can simulate trading in
  backtest mode. In this mode the trade is done on historic chart data. This
  is useful to check the performance of your trading strategy. Please note
  that the backtest is not 100% accurate as buy and sell prices are based on the
  closing price of the currency. This is idealistic and will not reflect the
  whole market situation.
* Added new "exchange" command. Can be used to calculate how many BTC you get
  for a certain amount of USD.

0.2.0 (2017-02-26)
------------------

* Improved "Usage" documentation
* Changed format of configuration file from JSON to standard python
  configuration file (.ini)
* Added "balance" command
* Added "explore" command

0.1.0 (2017-02-21)
------------------

* First release on PyPI
