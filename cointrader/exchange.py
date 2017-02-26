#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .exchanges.poloniex import Poloniex as PoloniexApi
from .chart import Chart

RESOLUTIONS = {"5m": 5 * 60, "15m": 15 * 60, "30m": 30 * 60, "2h": 60 * 60 * 2, "12h": 60 * 60 * 12}
TIMEFRAME = {"5m": 5 * 60, "15m": 15 * 60, "30m": 30 * 60, "1h": 60 * 60, "2h": 60 * 60 * 2,
             "6h": 60 * 60 * 6, "12h": 60 * 60 * 12, "1d": 60 * 60 * 24, "2d": 60 * 60 * 24 * 2, "1w": 60 * 60 * 24 * 7}
CASH = {"0.01$": 0.01, "0.1$": 0.1, "1$": 1, "2$": 2, "5$": 5, "10$": 10, "25$": 25, "50$": 25}


def get_market_name(market):
    return market[0]


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

    def __init__(self, exchange, name):
        """TODO: to be defined1.

        :name: TODO

        """
        self._exchange = exchange
        self._name = name

    @property
    def url(self):
        return "{}{}".format(self._exchange.url, self._name)

    def get_chart(self, resolution="30m", timeframe="1d"):
        data = self._exchange._api.chart(self._name,
                                         self._exchange.resolution2seconds(resolution),
                                         self._exchange.timeframe2seconds(timeframe))
        return Chart(data)

    def buy(self):
        print("BUY")

    def sell(self):
        print("SELL")


class Exchange(object):

    """Baseclass for all exchanges"""

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

    def get_market(self, market):
        raise NotImplementedError

    def resolution2seconds(self, resolution):
        return RESOLUTIONS[resolution]

    def timeframe2seconds(self, timeframe):
        return TIMEFRAME[timeframe]


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

    def get_balance(self, currency):
        return self._api.balance()[currency]

    def get_market(self, name):
        return Market(self, name)
