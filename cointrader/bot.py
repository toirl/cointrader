# -*- coding: utf-8 -*-
import datetime
import time
import logging
from cointrader import Base, sa
from cointrader.strategy import BUY, SELL, WAIT

log = logging.getLogger(__name__)


class Cointrader(Base):
    """Cointrader"""
    __tablename__ = "bots"
    id = sa.Column(sa.Integer, primary_key=True)
    created = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __init__(self, market, strategy, resolution="30m", timeframe="1d"):
        self._market = market
        self._strategy = strategy
        self._resolution = resolution
        self._timeframe = timeframe

        self._amount = 0
        self._value = 0
        self._start_btc = 0
        self._btc = 0
        self._start_rate = 0

    def _buy(self):
        log.debug("Signal: BUY")
        self._amount, price = self._market.buy(self._btc)
        if self._start_rate == 0:
            self._start_rate = price
        self._btc = 0
        self._value = self._amount * price
        data = self._market.get_chart().data[-1]
        date = datetime.datetime.utcfromtimestamp(data["date"])
        log.info("{}: Bought {} for {}".format(date, self._amount, price))

    def _sell(self):
        log.debug("Signal: SELL")
        proceeds, price = self._market.sell(self._amount)
        self._value = 0
        self._btc = proceeds
        data = self._market.get_chart().data[-1]
        date = datetime.datetime.utcfromtimestamp(data["date"])
        log.info("{}: Sold {} for {} -> {}".format(date, self._amount, price, self._btc))
        self._amount = 0

    def stat(self):
        """Returns a dictionary with some statistic of the performance of the bot."""

        data = self._market.get_chart().data
        end_rate = data[-1]["close"]

        # Calculate the value in BTC at the end of the trade.
        if self._amount:
            end_btc = self._amount * end_rate
        else:
            end_btc = self._btc

        stat = {
            "start": datetime.datetime.utcfromtimestamp(data[0]["date"]),
            "end": datetime.datetime.utcfromtimestamp(data[-1]["date"]),
            "start_price": data[0]["close"],
            "end_price": data[-1]["close"],
            "start_btc": self._start_btc,
            "end_btc": end_btc,
            "profit_cointrader": ((end_btc - self._start_btc) / self._start_btc) * 100,
            "profit_chart": ((end_rate - self._start_rate) / self._start_rate) * 100
        }
        return stat

    def start(self, btc, interval=None, backtest=False):
        """Start the bot and begin trading with given amount of BTC.

        The bot will trigger a analysis of the chart every N seconds.
        The default number of seconds is set on initialisation using the
        `resolution` option. You can overwrite this setting
        by using the `interval` option.

        By setting the `backtest` option the trade will be simulated on
        real chart data. This is useful for testing to see how good
        your strategy performs.

        :btc: Amount of BTC to start trading with
        :interval: Number of seconds to wait until the bot again call
        for a trading signal. This defaults to the resolution of the bot
            which is provided on initialisation.
        :backtest: Simulate trading on historic chart data on the given market.
        :returns: None

        """
        self._start_btc = btc
        self._btc = btc
        if interval is None:
            interval = self._market._exchange.resolution2seconds(self._resolution)
        while 1:
            signal = self._strategy.signal(self._market, self._resolution, self._timeframe)
            if signal == BUY and self._btc > 0:
                self._buy()
            elif signal == SELL and self._amount:
                self._sell()
            elif signal == WAIT:
                log.debug("Signal: WAIT")
            if backtest:
                if not self._market.continue_backtest():
                    log.info("Backtest finished")
                    return self.stat()
            log.debug("ZZZ for {} seconds".format(interval))
            time.sleep(interval)
