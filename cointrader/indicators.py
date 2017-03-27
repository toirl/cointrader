#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import datetime

log = logging.getLogger(__name__)

BUY = 1
SELL = -1
WAIT = 0
QUIT = -99
signal_map = {
    BUY: "BUY",
    WAIT: "WAIT",
    SELL: "SELL",
    QUIT: "QUIT"
}
# Signals for strategies.


class Signal(object):

    def __init__(self, signal, date):
        self.value = signal
        self.date = date

    @property
    def buy(self):
        return self.value == BUY

    @property
    def sell(self):
        return self.value == SELL


def is_max_value(values):
    """Will return True if the last recent values of the given list of
    values describe a local maximum value. A local maximum is defined as
    followed: A < B > C

    :series: List of values
    :returns: True or False

    """
    # Only take the last three values to check if we see a local
    # maximum.
    v = values[-3::]
    a = v[0]
    b = v[1]
    c = v[2]
    return a < b > c


def is_min_value(values):
    """Will return True if the last recent values of the given list of
    values describe a local minimum value. A local minimum is defined as
    followed: A > B < C

    :series: List of values
    :returns: True or False

    """
    # Only take the last three values to check if we see a local
    # maximum.
    v = values[-3::]
    a = v[0]
    b = v[1]
    c = v[2]
    return a > b < c


# def takeprofit(data, sluggish=1.5):
#     last = data[0][1]
#     signal = WAIT
#
#     for item in data:
#         d = item[0]
#         v = item[1]
#         change = (v - last) / last * 100
#         if change < 0 and change * -1 >= sluggish:
#             signal = SELL
#         elif change > 0 and change >= sluggish:
#             signal = BUY
#         else:
#             signal = WAIT
#         last = v
#
#     log.debug("{} signal @ {}: Value: {}, Change: {}".format(signal_map[signal],
#                                                              datetime.datetime.utcfromtimestamp(d),
#                                                              v,
#                                                              change))
#     return Signal(signal, datetime.datetime.utcfromtimestamp(d))
#
#
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