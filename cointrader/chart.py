#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import pandas
import datetime
from stockstats import StockDataFrame


def chart2csv(chart):
    out = []
    header = "date,amount,close,high,low,open,volume"
    out.append(header)
    for cs in chart:
        out.append("{},{},{},{},{},{},{}".format(cs["date"],
                                                 "", cs["close"], cs["high"],
                                                 cs["low"], cs["open"], cs["volume"]))
    return u"\n".join(out)


def search_chartdata_by_date(data, dt, le=True):
    ts = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
    chart_item = data[0]
    for d in data:
        if d["date"] <= ts:
            chart_item = d
        else:
            break
    return chart_item


class Chart(object):
    """The chart provides a unified interface to the chart data. It also
    gives access so some common indicators like macd, sma and ema.

    The `data` is provided as list of dictionaries where each
    dictionary represents a single set of data per point in the
    chart::

        {
            u'date': 1500112800,
            u'open': 0.07132169,
            u'close': 0.07162004,
            u'high': 0.07172972,
            u'low': 0.07114623,
            u'volume': 7.49372245,
            u'quoteVolume': 104.69114835,
            u'weightedAverage': 0.07157933,
        }

    The `start` and `end` datetimes define the relevant timeframe of
    the chart for later profit calculations. This date range is
    needed as the chart itself cointains more more datapoints than
    within the given date range. This is because we need more data
    to ensure that indicators like ema and sma provide sensefull
    values right on from the begin of the timeframe. So there must
    be more data available before the start.
    """

    def __init__(self, data, start, end):
        """Will build a chart instance from the given raw data input.

        :data: List of datapoints as dictionary.
        :start: Datetime object.
        :end: Datetime object.

        """
        self._data = data
        self._start = start
        self._end = end
        self._stock = StockDataFrame.retype(pandas.read_csv(io.StringIO(chart2csv(data))))

    @property
    def data(self):
        return self._data

    @property
    def date(self):
        return self._data[-1]["date"]

    @property
    def close(self):
        return self._data[-1]["close"]

    def get_first_point(self):
        return search_chartdata_by_date(self.data, self._start)

    def get_last_point(self):
        return search_chartdata_by_date(self.data, self._end)

    def values(self, which="close"):
        return [(v["date"], v[which]) for v in self._data]

    ################
    #  Indicators  #
    ################

    def macdh(self):
        macdh = self._stock.get("macdh")
        return macdh.tolist()

    def sma(self, window=10):
        sma = self._stock.get("close_{}_sma".format(window))
        return sma.tolist()

    def ema(self, window=10):
        ema = self._stock.get("close_{}_ema".format(window))
        return ema.tolist()
