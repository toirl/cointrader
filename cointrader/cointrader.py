# -*- coding: utf-8 -*-
import datetime
import time
import logging
import sqlalchemy as sa
from . import Base, engine, db
from .strategy import BUY, SELL, WAIT

log = logging.getLogger(__name__)


class Trade(Base):
    """Trading log"""
    __tablename__ = "trades"
    id = sa.Column(sa.Integer, primary_key=True)
    bot_id = sa.Column(sa.Integer, sa.ForeignKey('bots.id'))
    date = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    order_type = sa.Column(sa.String, nullable=False)
    order_id = sa.Column(sa.Integer, nullable=False)
    trade_id = sa.Column(sa.Integer, nullable=False)
    market = sa.Column(sa.String, nullable=False)
    amount = sa.Column(sa.Float, nullable=False)
    rate = sa.Column(sa.Float, nullable=False)
    btc = sa.Column(sa.Float, nullable=False)
    btc_taxed = sa.Column(sa.Float, nullable=False)

    def __init__(self, bot_id, date, order_type, order_id, trade_id, market, amount, rate, btc, btc_taxed):
        """TODO: to be defined1.

        :bot_id: ID of the bot which initiated the trade
        :date: Date of the order
        :order_id: ID of the order
        :trade_id: ID of a single trade within the order
        :market: Currency_pair linke BTC_DASH
        :amount: How many coins bought/sold in order
        :rate: Rate for the order
        :order_type: Type of order. Can be either "BUY, SELL"
        :btc: How many BTC you placed in order
        :btc_taxed: How many BTC are actually used in order after applying the tax

        """
        self.bot_id = bot_id
        self.date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        self.order_type = order_type
        self.order_id = order_id
        self.trade_id = trade_id
        self.market = market
        self.amount = amount
        self.rate = rate
        self.btc = btc
        self.btc_taxed = btc_taxed
        log.info("{}: Bought {} for {}".format(self.date, self.amount, self.rate))


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
