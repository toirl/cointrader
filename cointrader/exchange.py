#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cointrader.exchanges.poloniex import Poloniex as PoloniexApi
from cointrader.chart import Chart

CASH = {"0.01$": 0.01, "0.1$": 0.1, "1$": 1, "2$": 2, "5$": 5, "10$": 10, "25$": 25, "50$": 25}


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

    def __init__(self, exchange, name):
        """TODO: to be defined1.

        :name: TODO

        """
        self._exchange = exchange
        self._name = name

    @property
    def url(self):
        return "{}{}".format(self._exchange.url, self._name)

    def _get_chart_data(self, resolution, timeframe):
        return self._exchange._api.chart(self._name,
                                         self._exchange.resolution2seconds(resolution),
                                         self._exchange.timeframe2seconds(timeframe))

    def get_chart(self, resolution="30m", timeframe="1d"):
        data = self._get_chart_data(resolution, timeframe)
        return Chart(data)

    def buy(self, btc, price=None):
        # Calculate fee
        btc = add_fee(btc)
        return 0, 1

    def sell(self, amount, price=None):
        print("SELL")
        btc = add_fee(1)
        return btc, 1


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

    def get_chart(self, resolution="30m", timeframe="1d"):
        if self._chart_data is None:
            self._chart_data = self._get_chart_data(resolution, timeframe)
        return Chart(self._chart_data[0:self._backtest_tick])

    def buy(self, btc, price=None):
        price = float(self._chart_data[0:self._backtest_tick][-1]['close'])
        btc = add_fee(btc)
        amount = btc / price
        return amount, price

    def sell(self, amount, price=None):
        price = float(self._chart_data[0:self._backtest_tick][-1]['close'])
        btc = add_fee(amount * price)
        return btc, price


class Exchange(object):

    """Baseclass for all exchanges"""
    resolutions = {"5m": 5 * 60, "15m": 15 * 60,
                   "30m": 30 * 60, "2h": 60 * 60 * 2,
                   "24h": 60 * 60 * 24}
    timeframes = {"5m": 5 * 60, "15m": 15 * 60, "30m": 30 * 60,
                  "1h": 60 * 60, "2h": 60 * 60 * 2, "6h": 60 * 60 * 6,
                  "12h": 60 * 60 * 12, "1d": 60 * 60 * 24,
                  "2d": 60 * 60 * 24 * 2, "1w": 60 * 60 * 24 * 7,
                  "1M": 60 * 60 * 24 * 31, "3M": 60 * 60 * 24 * 31 * 3,
                  "1Y": 60 * 60 * 24 * 356}

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

    def get_market(self, market, backtest=False):
        raise NotImplementedError

    def resolution2seconds(self, resolution):
        return self.resolutions[resolution]

    def timeframe2seconds(self, timeframe):
        return self.timeframes[timeframe]


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

    def get_balance(self, currency):
        return self._api.balance()[currency]

    def get_market(self, name, backtest=False):
        if backtest:
            return BacktestMarket(self, name)
        else:
            return Market(self, name)
