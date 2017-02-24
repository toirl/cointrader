#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .exchanges.poloniex import Poloniex as PoloniexApi
from .chart import Chart

RESOLUTIONS = {"5m": 5*60, "15m": 15*60, "30m": 30*60, "2h": 60*60*2, "12h": 60*60*12}
TIMEFRAME = {"5m": 5*60, "15m": 15*60, "30m": 30*60, "1h": 60*60, "2h": 60*60*2,
             "6h": 60*60*6, "12h": 60*60*12, "1d": 60*60*24, "2d": 60*60*24*2, "1w": 60*60*24*7}
CASH = {"0.01$": 0.01, "0.1$": 0.1, "1$": 1, "2$": 2, "5$": 5, "10$": 10, "25$": 25, "50$": 25}


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

    def __init__(self, config):
        """TODO: to be defined1. """
        self._api = None

    @property
    def url(self):
        raise NotImplementedError

    def get_market(self, market):
        raise NotImplementedError

    def resolution2seconds(self, resolution):
        return RESOLUTIONS[resolution]

    def timeframe2seconds(self, timeframe):
        return TIMEFRAME[timeframe]


class Poloniex(Exchange):

    def __init__(self, config):
        """TODO: to be defined1. """
        self._api = PoloniexApi(config)

    @property
    def url(self):
        return "https://poloniex.com/exchange#"

    def btc2dollar(self, amount):
        ticker = self._api.ticker("USDT_BTC")
        rate = float(ticker["last"])
        return round(amount*rate, 2)

    def get_balance(self, currency):
        return self._api.balance()[currency]

    def get_market(self, name):
        return Market(self, name)
