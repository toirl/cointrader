#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import pandas
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


class Chart(object):

    """Docstring for Chart. """

    def __init__(self, data):
        """TODO: to be defined1.

        :data: TODO

        """
        self._data = data
        self._stock = StockDataFrame.retype(pandas.read_csv(io.StringIO(chart2csv(data))))

    @property
    def data(self):
        return self._data

    def values(self, which="close"):
        return [(v["date"], v[which]) for v in self._data]

    def macdh(self):
        macdh = self._stock.get("macdh")
        return macdh.tolist()
