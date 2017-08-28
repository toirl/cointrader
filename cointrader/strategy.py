#!/usr/bin/env python
import datetime
import logging
from cointrader.indicators import (
    WAIT, BUY, SELL, Signal, macdh_momententum, macdh, double_cross
)

log = logging.getLogger(__name__)


class Strategy(object):

    """Docstring for Strategy. """

    def __str__(self):
        return "{}".format(self.__class__)

    def __init__(self):
        self.signals = {}
        """Dictionary with details on the signal(s)
        {"indicator": {"signal": 1, "details": Foo}}"""

    def signal(self, chart):
        """Will return either a BUY, SELL or WAIT signal for the given
        market"""
        raise NotImplementedError


class NullStrategy(Strategy):

    """The NullStrategy does nothing than WAIT. It will emit not BUY or
    SELL signal and is therefor the default strategy when starting
    cointrader to protect the user from loosing money by accident."""

    def signal(self, chart):
        """Will return either a BUY, SELL or WAIT signal for the given
        market"""
        signal = Signal(WAIT, datetime.datetime.utcnow())
        self.signals["WAIT"] = signal
        return signal


class Klondike(Strategy):

    def signal(self, chart):
        signal = macdh_momententum(chart)
        self.signals["MACDH_MOMEMENTUM"] = signal
        if signal.buy:
            return signal
        elif signal.sell:
            return signal
        return Signal(WAIT, datetime.datetime.utcfromtimestamp(chart.date))


class Followtrend(Strategy):
    """Simple trend follow strategie."""

    def __init__(self):
        Strategy.__init__(self)
        self._macd = WAIT

    def signal(self, chart):
        # Get current chart
        closing = chart.values()

        self._value = closing[-1][1]
        self._date = datetime.datetime.utcfromtimestamp(closing[-1][0])

        # MACDH is an early indicator for trend changes. We are using the
        # MACDH as a precondition for trading signals here and required
        # the MACDH signal a change into a bullish/bearish market. This
        # signal stays true as long as the signal changes.
        macdh_signal = macdh(chart)
        if macdh_signal.value == BUY:
            self._macd = BUY
        if macdh_signal.value == SELL:
            self._macd = SELL
        log.debug("macdh signal: {}".format(self._macd))

        # Finally we are using the double_cross signal as confirmation
        # of the former MACDH signal
        dc_signal = double_cross(chart)
        if self._macd == BUY and dc_signal.value == BUY:
            signal = dc_signal
        elif self._macd == SELL and dc_signal.value == SELL:
            signal = dc_signal
        else:
            signal = Signal(WAIT, dc_signal.date)

        log.debug("Final signal @{}: {}".format(signal.date, signal.value))
        self.signals["DC"] = signal
        return signal
