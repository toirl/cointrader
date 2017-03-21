#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import datetime
from cointrader.strategy import Strategy, Signal, WAIT, SELL, BUY, signal_map

log = logging.getLogger(__name__)


class Followtrend(Strategy):
    """Simple trend follow strategie."""

    def __init__(self):
        Strategy.__init__(self)
        self._macd = WAIT

    def signal(self, market, resolution, start, end):
        # Get current chart
        chart = market.get_chart(resolution, start, end)
        closing = chart.values()

        self._value = closing[-1][1]
        self._date = datetime.datetime.utcfromtimestamp(closing[-1][0])

        # MACDH is an early indicator for trend changes. We are using the
        # MACDH as a precondition for trading signals here and required
        # the MACDH signal a change into a bullish/bearish market. This
        # signal stays true as long as the signal changes.
        macdh_signal = self.macdh(chart)
        if macdh_signal.value == BUY:
            self._macd = BUY
        if macdh_signal.value == SELL:
            self._macd = SELL

        # Finally we are using the double_cross signal as confirmation
        # of the former MACDH signal
        dc_signal = self.double_cross(chart)
        if self._macd == BUY and dc_signal.value == BUY:
            return dc_signal
        elif self._macd == SELL and dc_signal.value == SELL:
            return dc_signal
        else:
            return Signal(WAIT, dc_signal.date)


def takeprofit(data, sluggish=1.5):
    last = data[0][1]
    signal = WAIT

    for item in data:
        d = item[0]
        v = item[1]
        change = (v - last) / last * 100
        if change < 0 and change * -1 >= sluggish:
            signal = SELL
        elif change > 0 and change >= sluggish:
            signal = BUY
        else:
            signal = WAIT
        last = v

    log.debug("{} signal @ {}: Value: {}, Change: {}".format(signal_map[signal],
                                                             datetime.datetime.utcfromtimestamp(d),
                                                             v,
                                                             change))
    return Signal(signal, datetime.datetime.utcfromtimestamp(d))


def followtrend(data, sluggish=1.5):
    support = None
    resistance = None
    last = data[0][1]
    signal = WAIT

    def breaks_resistance(v, resistance, sluggish):
        resistance = resistance + (resistance / 100 * sluggish)
        return v > resistance

    def breaks_support(v, support, sluggish):
        support = support - (support / 100 * sluggish)
        return v < support

    for item in data:
        d = item[0]
        v = item[1]
        if resistance is None:
            # We are searching a new resistance and wait for a change in
            # the current trend.
            if v < last:
                resistance = last
        if support is None:
            # We are searching a new support and wait for a change in
            # the current trend.
            if v > last:
                support = last
        if resistance is not None and support is not None:
            # Trend is now in correction phase. It s changing with in
            # the range of the last resistance and last support.
            if not breaks_resistance(v, resistance, sluggish) and not breaks_support(v, support, sluggish):
                # Nothing special here no signal.
                signal = WAIT
            elif breaks_resistance(v, resistance, sluggish):
                # Trend breaks the last resistance. This is a BUY
                # signal. The resistiance is gone and the support will
                # be the last resistance.

                #  TODO: Better check the effect of using
                #  last/resistance as the new support. Currently I
                #  suspect that using the old resitiance as the new
                #  support is more relaxed and leaves a larger
                #  correction band and not triggering false SELL
                #  signales. Using last seems to be more greedy
                #  but results in small correction bands and potentially
                #  more wrong sell signal. (ti) <2017-02-24 21:37>
                support = resistance
                # support = last

                resistance = None
                signal = BUY
            elif breaks_support(v, support, sluggish):
                # Trend breaks the last support. This is a SELL
                # signal. The support is gone and the resistance will
                # be the last support.

                #  TODO: Better check the effect of using
                #  last/support as the new resistance. See above TODO
                #  for more comments. (ti) <2017-02-24 21:37>
                resistance = support
                # resistance = last

                support = None
                signal = SELL
        last = v
        log.debug("{} signal @ {}: Value: {}, Resistance: {}, Support: {}".format(signal_map[signal],
                                                                                  datetime.datetime.utcfromtimestamp(d),
                                                                                  v,
                                                                                  resistance,
                                                                                  support))
    return Signal(signal, datetime.datetime.utcfromtimestamp(d))
