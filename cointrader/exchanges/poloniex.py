#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import urllib
import json
import time
import hmac
import hashlib
import requests
import datetime


def totimestamp(dt):
    td = dt - datetime.datetime(1970, 1, 1)
    # return td.total_seconds()
    return int((td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6)


class Api(object):

    """Docstring for Api. """

    def __init__(self, config):
        api = config.api
        self.key = api[0]
        self.secret = api[1]

    def ticker(self, currency=None):
        raise NotImplementedError()

    def volume(self, currency=None):
        raise NotImplementedError()

    def chart(self, currency, period=1800, timeframe=None):
        raise NotImplementedError()

    def book(self, currency):
        raise NotImplementedError()

    def balance(self):
        raise NotImplementedError()

    def buy(self, market, amount, price=None):
        raise NotImplementedError()

    def sell(self, market, amount, price=None):
        raise NotImplementedError()


class Poloniex(Api):

    MAKER_FEE = 0.15
    TAKER_FEE = 0.25
    # So-called maker-taker fees offer a transaction rebate to those who
    # provide liquidity (the market maker), while charging customers who
    # take that liquidity. The chief aim of maker-taker fees is to stimulate
    # trading activity within an exchange by extending to firms the
    # incentive to post orders, in theory facilitating trading.

    def ticker(self, currency=None):
        """
        Returns the ticker of the given currency pair. If no pair is given
        the volume of all markets are returned.

        Example output::

            {
                "BTC_LTC":{"last":"0.0251",
                           "lowestAsk":"0.02589999",
                           "highestBid":"0.0251",
                           "percentChange":"0.02390438",
                           "baseVolume":"6.16485315",
                           "quoteVolume":"245.82513926"},
                ...
            }
        """
        params = {"command": "returnTicker"}
        r = requests.get("https://poloniex.com/public", params=params)
        result = json.loads(r.content)
        if currency:
            return result[currency]
        return result

    def volume(self, currency=None):
        """
        Returns the volume of the given currency. If not currency is given
        the volume of all currency are returned.

        Example output::

            {"BTC_LTC":{"BTC":"2.23248854",
                        "LTC":"87.10381314"},
             "BTC_NXT":{"BTC":"0.981616","NXT":"14145"},
             ...}
        """
        params = {"command": "return24hVolume"}
        r = requests.get("https://poloniex.com/public", params=params)
        result = json.loads(r.content)
        if currency:
            pairs = []
            for c in currency:
                pairs.append("BTC_{}".format(c))
                pairs.append("USDT_{}".format(c))
            result = {c: result[c] for c in pairs if result.get(c)}
        return result

    def book(self, currency):
        """
        Returns the order book for a given market, as well as a sequence
        number for use with the Push API and an indicator specifying
        whether the market is frozen. You may set currencyPair to "all"
        to get the order books of all markets. Sample output::

            {"asks":[[0.00007600,1164],[0.00007620,1300], ... ],
             "bids":[[0.00006901,200],[0.00006900,408], ... ],
             "isFrozen": 0, "seq": 18849}
        """
        params = {"command": "returnOrderBook",
                  "currencyPair": currency,
                  "depth": 10}

        r = requests.get("https://poloniex.com/public", params=params)
        return json.loads(r.content)

    def chart(self, currency, period=1800, timeframe=None):
        """
        Returns candlestick chart data. Required GET parameters are
        "currencyPair", "period" (candlestick period in seconds; valid
        values are 300, 900, 1800, 7200, 14400, and 86400), "start", and
        "end". "Start" and "end" are given in UNIX timestamp format and
        used to specify the date range for the data returned.

        On the default the chart for the last day with a period of 30
        minutes is returned.

        Sample output::

            [{"date":1405699200,
              "high":0.0045388,
              "low":0.00403001,
              "open":0.00404545,
              "close":0.00427592,
              "volume":44.11655644,
              "quoteVolume":10259.29079097,
              "weightedAverage":0.00430015},
              ...]

        https://poloniex.com/public?command=returnChartData&currencyPair=BTC_XMR&start=1405699200&end=9999999999&period=14400
        """
        end = datetime.datetime.now()
        if timeframe is None:
            start = end - datetime.timedelta(seconds=3600 * 24)
        else:
            start = end - datetime.timedelta(seconds=timeframe)

        ts_end = totimestamp(end)
        ts_start = totimestamp(start)

        params = {"command": "returnChartData",
                  "currencyPair": currency,
                  "start": ts_start,
                  "end": ts_end,
                  "period": period}

        r = requests.get("https://poloniex.com/public", params=params)
        return json.loads(r.content)

    def balance(self):
        """
        Returns the balance of the given currency. If not currency is given
        the balance of all currency are returned.

        Example output::

        """
        result = {}
        params = {"command": "returnCompleteBalances", "nonce": int(time.time() * 1000)}
        sign = hmac.new(str(self.secret), urllib.urlencode(params), hashlib.sha512).hexdigest()
        headers = {"Key": self.key, "Sign": sign}
        r = requests.post("https://poloniex.com/tradingApi", data=params, headers=headers)
        tmp = json.loads(r.content)
        for currency in tmp:
            result[currency] = {}
            result[currency]["quantity"] = float(tmp[currency]["available"])
            result[currency]["btc_value"] = float(tmp[currency]["btcValue"])
        return result

    def buy(self, market, amount, price=None):
        return amount, price

    def sell(self, market, amount, price=None):
        return amount, price
