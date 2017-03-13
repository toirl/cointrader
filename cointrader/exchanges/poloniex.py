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

    def chart(self, currency, start, end, period=1800):
        raise NotImplementedError()

    def book(self, currency):
        raise NotImplementedError()

    def balance(self):
        raise NotImplementedError()

    def buy(self, market, amount, price, option=None):
        """Places a limit buy order in a given market. Required POST
        parameters are "currencyPair", "rate", and "amount". If
        successful, the method will return the order number. Sample
        output::

            {"orderNumber":31226040,"resultingTrades":[{"amount":"338.8732","date":"2014-10-18
            23:03:21","rate":"0.00000173","total":"0.00058625","tradeID":"16164","type":"buy"}]}

        'total' is the amount of btc after applying the fee of the order.
        This is the amount of BTC you actually used in the the order.

        You may optionally set "fillOrKill", "immediateOrCancel",
        "postOnly" to 1. A fill-or-kill order will either fill in its
        entirety or be completely aborted. An immediate-or-cancel order
        can be partially or completely filled, but any portion of the
        order that cannot be filled immediately will be canceled rather
        than left on the order book. A post-only order will only be
        placed if no portion of it fills immediately; this guarantees
        you will never pay the taker fee on any
        part of the order that fills.

        :market: Currency pair like BTC_DASH.
        :amount: How many coins do you want to buy
        :price: For which price do you want to buy?
        :option: See docsstring for more details
        :returns: Dict with details on order.
        """
        raise NotImplementedError()

    def sell(self, market, amount, price=None):
        """Places a limit sell order in a given market. Required POST
        parameters are "currencyPair", "rate", and "amount". If
        successful, the method will return the order number. Sample
        output::

            {"orderNumber":31226040,"resultingTrades":[{"amount":"338.8732","date":"2014-10-18
            23:03:21","rate":"0.00000173","total":"0.00058625","tradeID":"16164","type":"sell"}]}

        'total' is the amount of btc after applying the fee of the order.
        This is the amount of BTC you actually used in the the order.

        You may optionally set "fillOrKill", "immediateOrCancel",
        "postOnly" to 1. A fill-or-kill order will either fill in its
        entirety or be completely aborted. An immediate-or-cancel order
        can be partially or completely filled, but any portion of the
        order that cannot be filled immediately will be canceled rather
        than left on the order book. A post-only order will only be
        placed if no portion of it fills immediately; this guarantees
        you will never pay the taker fee on any
        part of the order that fills.

        :market: Currency pair like BTC_DASH.
        :amount: How many coins do you want to buy
        :price: For which price do you want to buy?
        :option: See docsstring for more details
        :returns: Dict with details on order.
        """
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

    def chart(self, currency, start, end, period=1800):
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

    def buy(self, market, amount, price, option):
        params = {"command": "buy",
                  "currencyPair": market,
                  "rate": price,
                  "amount": amount,
                  "nonce": int(time.time() * 1000)}

        if option == "fillOrKill":
            params["fillOrKill"] = 1
        elif option == "immediateOrCancel":
            params["immediateOrCancel"] = 1
        elif option == "postOnly":
            params["postOnly"] = 1

        sign = hmac.new(str(self.secret), urllib.urlencode(params), hashlib.sha512).hexdigest()
        headers = {"Key": self.key, "Sign": sign}
        r = requests.post("https://poloniex.com/tradingApi", data=params, headers=headers)
        result = json.loads(r.content)
        return result

    def sell(self, market, amount, price, option=None):
        params = {"command": "sell",
                  "currencyPair": market,
                  "rate": price,
                  "amount": amount,
                  "nonce": int(time.time() * 1000)}

        if option == "fillOrKill":
            params["fillOrKill"] = 1
        elif option == "immediateOrCancel":
            params["immediateOrCancel"] = 1
        elif option == "postOnly":
            params["postOnly"] = 1

        sign = hmac.new(str(self.secret), urllib.urlencode(params), hashlib.sha512).hexdigest()
        headers = {"Key": self.key, "Sign": sign}
        r = requests.post("https://poloniex.com/tradingApi", data=params, headers=headers)
        return json.loads(r.content)
