#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from cointrader.strategy import Strategy, Signal, WAIT


class NullStrategy(Strategy):

    """The NullStrategy does nothing than WAIT. It will emit not BUY or
    SELL signal and is therefor the default strategy when starting
    cointrader to protect the user from loosing money by accident."""

    def details(self, market, resolution):
        """Will return details on the reasong why the signal was emited."""
        return {}

    def signal(self, market, resolution, start, end):
        """Will return either a BUY, SELL or WAIT signal for the given
        market"""
        signal = Signal(WAIT, datetime.datetime.utcnow())
        self._details["WAIT"] = {"signal": signal, "details": "I am just waiting"}
        return signal
