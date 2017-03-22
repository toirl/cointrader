#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import datetime
from cointrader.strategy import Strategy, Signal, WAIT, SELL, BUY, signal_map
from cointrader.strategies.helpers import is_max_value, is_min_value

log = logging.getLogger(__name__)


class MACDHMomentum(Strategy):

    """This stratgey will generate trading signal based on the market
    momentum based on MCDH indicator.

    A BUY signal is emitted if the momentum of the market
    reaches its maximum in a bearish market.

    A SELL signal is emitted if the momentum of the market
    reaches its maximum in a bullish market.
    """

    def __init__(self):
        Strategy.__init__(self)
        self._macd = WAIT

    def signal(self, market, resolution, start, end):
        # Get current chart
        signal = WAIT
        chart = market.get_chart(resolution, start, end)
        closing = chart.values()

        self._value = closing[-1][1]
        self._date = datetime.datetime.utcfromtimestamp(closing[-1][0])

        macdh = chart.macdh()

        # TODO: Check we the inverse of this strategy (BUY on MAX) is
        # better (ti) <2017-03-22 23:16>
        # Check if the market as reached its max momentum in a bullish
        # market.
        macdh_local_max = is_max_value(macdh) and macdh[-1] > 0
        if macdh_local_max:
            signal = SELL

        # Check if the market as reached its max momentum in a bearish
        # market.
        macdh_local_min = is_min_value(macdh) and macdh[-1] < 0
        if macdh_local_min:
            signal = BUY

        log.debug("Final signal @{}: {}".format(self._date, signal_map[signal]))
        return Signal(signal, self._date)
