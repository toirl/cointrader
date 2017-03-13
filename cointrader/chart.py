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
    """Docstring for Chart. """

    def __init__(self, data, start, end):
        """TODO: to be defined1.

        :data: TODO

        """
        self._data = data
        self._start = start
        self._end = end
        self._stock = StockDataFrame.retype(pandas.read_csv(io.StringIO(chart2csv(data))))

    @property
    def data(self):
        return self._data

    def get_first_point(self):
        return search_chartdata_by_date(self.data, self._start)

    def get_last_point(self):
        return search_chartdata_by_date(self.data, self._end)

    def values(self, which="close"):
        return [(v["date"], v[which]) for v in self._data]

    def macdh(self):
        macdh = self._stock.get("macdh")
        return macdh.tolist()

    def sma(self, window=10):
        sma = self._stock.get("close_{}_sma".format(window))
        return sma.tolist()
