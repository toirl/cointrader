#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import click
import logging
from .helpers import render_bot_statistic, render_bot_tradelog, render_bot_title, render_signal_details
from cointrader.strategies.helpers import is_max_value, is_min_value

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


class Strategy(object):

    """Docstring for Strategy. """

    def __str__(self):
        return "{}".format(self.__class__)

    def __init__(self):
        self.bot = None
        self._chart = None
        """Current chart"""
        self._details = {}
        """Dictionary with details on the signal(s)
        {"indicator": {"signal": 1, "details": Foo}}
        """

    def details(self, market, resolution):
        """Will return details on the reasong why the signal was emited."""
        return self._details

    def set_bot(self, bot):
        self.bot = bot

    def signal(self, market, resolution, start, end):
        """Will return either a BUY, SELL or WAIT signal for the given
        market"""
        raise NotImplementedError

    def sma(self, chart, window=12):
        """Generates a trade signal based on a moving averanges. A BUY
        signal is generated if the EMA higher than the closing price. A
        SELL signal is emited if the EMA is lower than the closing
        price."""

        sma = chart.sma(window)[-1]
        closing = chart.values()
        value = closing[-1][1]
        date = datetime.datetime.utcfromtimestamp(closing[-1][0])

        signal = WAIT
        if value > sma:
            signal = BUY
        elif value < sma:
            signal = SELL
        self._details["SMA"] = {"signal": signal, "details": "SMA{}: {})".format(window, sma)}
        return Signal(signal, date)

    def ema(self, chart, window=12):
        """Generates a trade signal based on a moving averanges. A BUY
        signal is generated if the EMA higher than the closing price. A
        SELL signal is emited if the EMA is lower than the closing
        price."""

        ema = chart.ema(window)[-1]
        closing = chart.values()
        value = closing[-1][1]
        date = datetime.datetime.utcfromtimestamp(closing[-1][0])

        signal = WAIT
        if value > ema:
            signal = BUY
        elif value < ema:
            signal = SELL
        self._details["EMA"] = {"signal": signal, "details": "EMA{}: {})".format(window, ema)}
        return Signal(signal, date)

    def double_cross(self, chart, fast=12, slow=26):
        """Generates a trade signal based on two moving averanges with
        different width. A BUY signal is generated if the faster EMA
        crosses the slower EMA in up direction and the faster EMA is higher
        than the closing price. A SELL signal is emited if the faster SMA
        crosses the lower from above and is lower than the closing
        price."""

        closing = chart.values()
        value = closing[-1][1]
        date = datetime.datetime.utcfromtimestamp(closing[-1][0])
        ema_1 = chart.ema(fast)[-1]
        ema_2 = chart.ema(slow)[-1]
        signal = WAIT

        if value > ema_1 and ema_1 > ema_2:
            signal = BUY
        elif value < ema_1 and ema_1 < ema_2:
            signal = SELL
        self._details["EMA"] = {"signal": signal, "details": "EMA{}: {}, EMA{}: {})".format(fast, ema_1, slow, ema_2)}
        return Signal(signal, date)

    def macdh(self, chart):
        """Generates a SELL signal as soon as the macdh value changes
        from positve value into negativ value. It generates a BUY signal
        if the value from negativ to positiv."""

        macdh = chart.macdh()[::-1][0:2]
        closing = chart.values()
        date = datetime.datetime.utcfromtimestamp(closing[-1][0])
        if macdh[0] < 0 and macdh[1] > 0:
            signal = SELL
        elif macdh[0] > 0 and macdh[1] < 0:
            signal = BUY
        else:
            signal = WAIT
        self._details["MACDH"] = {"signal": signal, "details": "MACDH: {}".format(macdh)}
        return Signal(signal, date)

    def macdh_momententum(self, chart):

        macdh = chart.macdh()
        closing = chart.values()
        date = datetime.datetime.utcfromtimestamp(closing[-1][0])

        pos_macdh_local_max = is_max_value(macdh) and macdh[-1] > 0
        # pos_macdh_local_min = is_min_value(macdh) and macdh[-1] > 0
        neg_macdh_local_min = is_min_value(macdh) and macdh[-1] < 0
        # neg_macdh_local_max = is_max_value(macdh) and macdh[-1] < 0

        signal = WAIT
        if pos_macdh_local_max:  # or neg_macdh_local_max:
            signal = SELL
        elif neg_macdh_local_min:  # or pos_macdh_local_min:
            signal = BUY

        self._details["MACDHMomentum"] = {"signal": signal, "details": "MACDH: {}".format(macdh)}
        return Signal(signal, date)


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


class Klondike(Strategy):

    def signal(self, market, resolution, start, end):
        chart = market.get_chart(resolution, start, end)

        signal = self.macdh(chart)
        if signal.buy:
            return signal
        elif signal.sell:
            return signal
        return Signal(WAIT, chart.date)


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
        log.debug("macdh signal: {}".format(self._macd))

        # Finally we are using the double_cross signal as confirmation
        # of the former MACDH signal
        dc_signal = self.double_cross(chart)
        if self._macd == BUY and dc_signal.value == BUY:
            signal = dc_signal
        elif self._macd == SELL and dc_signal.value == SELL:
            signal = dc_signal
        else:
            signal = Signal(WAIT, dc_signal.date)

        log.debug("Final signal @{}: {}".format(signal.date, signal.value))
        return signal


class InteractivStrategyWrapper(object):

    def __init__(self, strategie):
        self._strategie = strategie
        self.bot = None

    def set_bot(self, bot):
        self.bot = bot

    def __str__(self):
        return "Interavtiv: {}".format(self._strategie)

    def signal(self, market, resolution, start, end):
        """Will return either a BUY, SELL or WAIT signal for the given
        market"""

        # Get current chart
        click.echo(render_bot_title(self.bot, market, resolution))
        signal = self._strategie.signal(market, resolution, start, end)

        click.echo('Signal: {} {}'.format(signal.date, signal_map[signal.value]))
        click.echo(render_signal_details(self._strategie.details(market, resolution)))
        click.echo('')
        options = []
        if self.bot.btc:
            options.append("b) Buy")
        if self.bot.amount:
            options.append("s) Sell")
        options.append("l) Tradelog")
        options.append("p) Performance of bot")
        options.append("d) Show details on signal")
        options.append("q) Quit")
        options.append("")
        options.append("Press any key to continue")

        click.echo(u'\n'.join(options))
        c = click.getchar()
        if c == 'b' and self.bot.btc:
            # btc = click.prompt('BTC', default=self.bot.btc)
            if click.confirm('Buy for {} btc?'.format(self.bot.btc)):
                return Signal(BUY, datetime.datetime.utcnow())
        if c == 's' and self.bot.amount:
            # amount = click.prompt('Amount', default=self.bot.amount)
            if click.confirm('Sell {}?'.format(self.bot.amount)):
                return Signal(SELL, datetime.datetime.utcnow())
        if c == 'l':
            click.echo(render_bot_tradelog(self.bot.trades))
        if c == 'p':
            click.echo(render_bot_statistic(self.bot.stat()))
        if c == 'd':
            click.echo(render_signal_details(self._strategie.details(market, resolution)))
        if c == 'q':
            return Signal(QUIT, datetime.datetime.utcnow())
        else:
            return Signal(WAIT, datetime.datetime.utcnow())
