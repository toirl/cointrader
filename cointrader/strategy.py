#!/usr/bin/env python
import datetime
import click
import logging
from .helpers import render_bot_statistic, render_bot_tradelog, render_bot_title, render_signal_details
from cointrader.indicators import (
    WAIT, BUY, SELL, QUIT, signal_map, Signal, macdh_momententum
)

log = logging.getLogger(__name__)


class Strategy(object):

    """Docstring for Strategy. """

    def __str__(self):
        return "{}".format(self.__class__)

    def __init__(self):
        self.bot = None
        self.signals = {}
        """Dictionary with details on the signal(s)
        {"indicator": {"signal": 1, "details": Foo}}"""
        self._chart = None
        """Current chart"""

    def set_bot(self, bot):
        self.bot = bot

    def signal(self, market, resolution, start, end):
        """Will return either a BUY, SELL or WAIT signal for the given
        market"""
        raise NotImplementedError


class NullStrategy(Strategy):

    """The NullStrategy does nothing than WAIT. It will emit not BUY or
    SELL signal and is therefor the default strategy when starting
    cointrader to protect the user from loosing money by accident."""

    def signal(self, market, resolution, start, end):
        """Will return either a BUY, SELL or WAIT signal for the given
        market"""
        signal = Signal(WAIT, datetime.datetime.utcnow())
        self.signals["WAIT"] = signal
        return signal


class Klondike(Strategy):

    def signal(self, market, resolution, start, end):
        chart = market.get_chart(resolution, start, end)
        signal = macdh_momententum(chart)
        self.signals["MACDH_MOMEMENTUM"] = signal
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
        self.signals["DC"] = signal
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
        click.echo(render_signal_details(self._strategie.signals))
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
            click.echo(render_signal_details(self._strategie.signals))
        if c == 'q':
            return Signal(QUIT, datetime.datetime.utcnow())
        else:
            return Signal(WAIT, datetime.datetime.utcnow())
