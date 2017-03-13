#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import time
from cointrader.exchanges.poloniex import Poloniex as PoloniexApi
from cointrader.chart import Chart


def get_market_name(market):
    return market[0]


def add_fee(btc, fee=0.025):
    return btc - (btc / 100 * fee)


class Coin(object):

    """Docstring for Coin."""

    def __init__(self, name, quantity, btc_value=None):
        self.name = name
        self.quantity = quantity
        self.btc_value = btc_value

    @property
    def value(self):
        return self.btc_value


class Market(object):

    """Docstring for Market. """

    def __init__(self, exchange, name, dry_run=False):
        """TODO: to be defined1.

        :name: TODO

        """
        self._exchange = exchange
        self._name = name
        self._dry_run = dry_run

    @property
    def currency(self):
        pair = self._name.split("_")
        return pair[1]

    @property
    def url(self):
        return "{}{}".format(self._exchange.url, self._name)

    def _get_chart_data(self, resolution, start, end):
        period = self._exchange.resolution2seconds(resolution)
        internal_start = start
        # Calculate internal start date of the chart. The internal start
        # date is used to ensure that the chart contains enough data to
        # compute indicators like SMA or EMA. On default we excpect at
        # least 120 data points in the chart to be present.
        MIN_POINTS = 120

        # 1. First check if the timeframe is already large enough to
        # calculate the indicators.
        td = end - internal_start
        ticks = td.total_seconds() / period
        offset = 0
        if ticks < MIN_POINTS:
            # Not enough data points. We need to set the start date back
            # in the past.
            offset = MIN_POINTS - ticks
            internal_start = internal_start - datetime.timedelta(seconds=period * offset)

        return self._exchange._api.chart(self._name, internal_start, end, period), int(offset)

    def get_chart(self, resolution="30m", start=None, end=None):
        """Will return a chart of the market. On default the chart will
        have a resolution of 30m. It will include the last recent data
        of the market on default. You can optionally define a different
        timeframe by providing a start and end point. On default the
        start and end of the chart will be the time of requesting the
        chart data.

        The start and end date are used to get the start and end rate of
        the market for later profit calculations.

        :resolution: Resolution of the chart (Default 30m)
        :start: Start of the chart data (Default Now)
        :end: End of the chart data (Default Now)
        :returns: Chart instance.
        """
        if end is None:
            end = datetime.datetime.utcnow()
        if start is None:
            start = datetime.datetime.utcnow()

        data, offset = self._get_chart_data(resolution, start, end)
        return Chart(data, start, end)

    def buy(self, btc, price=None, option=None):
        """Will buy coins on the market for the given amount of BTC. On
        default we will make a market order which means we will try to
        buy for the best price available. If price is given the order
        will be placed for at the given price. You can optionally
        provide some options. See
        :class:`cointrader.exchanges.poloniex.api` for more details.

        :btc: Amount of BTC
        :price: Optionally price for which you want to buy
        :option: Optionally some buy options
        :returns: Dict witch details on the order.
        """
        if price is None:
            # Get best price on market.
            orderbook = self._exchange._api.book(self._name)
            asks = orderbook["asks"]   # Asks in the meaning of "I wand X for Y"
            best_offer = asks[-1]
            price = float(best_offer[0])
        amount = btc / price
        if self._dry_run:
            amount = add_fee(amount)
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {u'orderNumber': u'{}'.format(int(time.time() * 1000)),
                    u'resultingTrades': [
                        {u'tradeID': u'{}'.format(int(time.time() * 1000)),
                         u'rate': u'{}'.format(price),
                         u'amount': u'{}'.format(amount),
                         u'date': u'{}'.format(date),
                         u'total': u'{}'.format(btc),
                         u'type': u'buy'}]}
        else:
            return self._exchange._api.buy(self._name, amount, price, option)

    def sell(self, amount, price=None, option=None):
        if price is None:
            # Get best price on market.
            orderbook = self._exchange._api.book(self._name)
            bids = orderbook["bids"]  # Bids in the meaning of "I give you X for Y"
            best_offer = bids[-1]
            price = float(best_offer[0])
        btc = amount * price
        if self._dry_run:
            btc = add_fee(btc)
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {u'orderNumber': u'{}'.format(int(time.time() * 1000)),
                    u'resultingTrades': [
                        {u'tradeID': u'{}'.format(int(time.time() * 1000)),
                         u'rate': u'{}'.format(price),
                         u'amount': u'{}'.format(amount),
                         u'date': u'{}'.format(date),
                         u'total': u'{}'.format(btc),
                         u'type': u'sell'}]}
        else:
            return self._exchange._api.sell(self._name, amount, price, option)


class BacktestMarket(Market):

    """Market to enable backtesting a strategy on the market."""

    def __init__(self, exchange, name):
        """TODO: to be defined1.

        :exchange: TODO
        :name: TODO

        """
        Market.__init__(self, exchange, name)
        self._chart_data = None
        self._backtest_tick = 1

    def continue_backtest(self):
        self._backtest_tick += 1
        if self._chart_data and len(self._chart_data) >= self._backtest_tick:
            return True
        return False

    def get_chart(self, resolution="30m", start=None, end=None):
        if self._chart_data is None:
            self._chart_data, offset = self._get_chart_data(resolution, start, end)
            self._backtest_tick += offset
        return Chart(self._chart_data[0:self._backtest_tick], start, end)

    def buy(self, btc, price=None):
        price = float(self._chart_data[0:self._backtest_tick][-1]['close'])
        date = datetime.datetime.utcfromtimestamp(self._chart_data[0:self._backtest_tick][-1]['date'])
        btc = add_fee(btc)
        amount = btc / price
        return {u'orderNumber': u'{}'.format(int(time.time() * 1000)),
                u'resultingTrades': [
                    {u'tradeID': u'{}'.format(int(time.time() * 1000)),
                     u'rate': u'{}'.format(price),
                     u'amount': u'{}'.format(amount),
                     u'date': u'{}'.format(date),
                     u'total': u'{}'.format(btc),
                     u'type': u'buy'}]}

    def sell(self, amount, price=None):
        price = float(self._chart_data[0:self._backtest_tick][-1]['close'])
        date = datetime.datetime.utcfromtimestamp(self._chart_data[0:self._backtest_tick][-1]['date'])
        btc = add_fee(amount * price)
        return {u'orderNumber': u'{}'.format(int(time.time() * 1000)),
                u'resultingTrades': [
                    {u'tradeID': u'{}'.format(int(time.time() * 1000)),
                     u'rate': u'{}'.format(price),
                     u'amount': u'{}'.format(amount),
                     u'date': u'{}'.format(date),
                     u'total': u'{}'.format(btc),
                     u'type': u'sell'}]}


class Exchange(object):

    """Baseclass for all exchanges"""
    resolutions = {"5m": 5 * 60, "15m": 15 * 60,
                   "30m": 30 * 60, "1h": 60 * 60 * 1,
                   "2h": 60 * 60 * 2, "4h": 60 * 60 * 4, "24h": 60 * 60 * 24}

    def __init__(self, config, api=None):
        """TODO: to be defined1. """
        self._api = api
        self.coins = {}

        # Setup coins
        balance = self._api.balance()
        for currency in balance:
            if balance[currency]["quantity"] > 0:
                self.coins[currency] = Coin(currency,
                                            balance[currency]["quantity"],
                                            balance[currency]["btc_value"])

    @property
    def url(self):
        raise NotImplementedError

    @property
    def total_btc_value(self):
        return sum([self.coins[c].value for c in self.coins])

    @property
    def total_euro_value(self, limit=10):
        ticker = self._api.ticker()
        return float(ticker["USDT_BTC"]["last"]) * self.total_btc_value

    @property
    def markets(self):
        ticker = self._api.ticker()
        tmp = {}
        for currency in ticker:
            if currency.startswith("BTC_"):
                change = round(float(ticker[currency]["percentChange"]) * 100, 2)
                volume = round(float(ticker[currency]["baseVolume"]), 1)
                if change <= 0:
                    continue
                tmp[currency] = {"volume": volume, "change": change}
        return tmp

    def get_top_markets(self, markets, limit=10):
        if not markets:
            markets = self.markets
        top_profit = self.get_top_profit_markets(markets, limit)
        top_volume = self.get_top_volume_markets(markets, limit)
        top_profit_markets = set(map(get_market_name, top_profit))
        top_volume_markets = set(map(get_market_name, top_volume))

        top_markets = {}
        for market in top_profit_markets.intersection(top_volume_markets):
            top_markets[market] = markets[market]
        return sorted(top_markets.items(), key=lambda x: x[1]["change"], reverse=True)[0:limit]

    def get_top_profit_markets(self, markets=None, limit=10):
        if not markets:
            markets = self.markets
        return sorted(markets.items(),
                      key=lambda x: (float(x[1]["change"]), float(x[1]["volume"])), reverse=True)[0:limit]

    def get_top_volume_markets(self, markets=None, limit=10):
        if not markets:
            markets = self.markets
        return sorted(markets.items(),
                      key=lambda x: (float(x[1]["volume"]), float(x[1]["change"])), reverse=True)[0:limit]

    def get_market(self, market, backtest=False, dry_run=False):
        raise NotImplementedError

    def resolution2seconds(self, resolution):
        return self.resolutions[resolution]


class Poloniex(Exchange):

    def __init__(self, config):
        api = PoloniexApi(config)
        Exchange.__init__(self, config, api)

    @property
    def url(self):
        return "https://poloniex.com/exchange#"

    def btc2dollar(self, amount):
        ticker = self._api.ticker("USDT_BTC")
        rate = float(ticker["last"])
        return round(amount * rate, 2)

    def dollar2btc(self, amount):
        ticker = self._api.ticker("USDT_BTC")
        rate = float(ticker["last"])
        return round(amount / rate, 8)

    def get_balance(self, currency=None):
        if currency is None:
            return self._api.balance()
        else:
            return self._api.balance()[currency]

    def get_market(self, name, backtest=False, dry_run=False):
        if backtest:
            return BacktestMarket(self, name)
        else:
            return Market(self, name, dry_run)
