#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import click
import logging
from .helpers import render_bot_statistic, render_bot_tradelog, render_bot_title

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


class Strategy(object):

    """Docstring for Strategy. """

    def __str__(self):
        return "{}".format(self.__class__)

    def __init__(self):
        self._signal_history = []
        """Store last emitted signals"""
        self._bot = None

    def set_bot(self, bot):
        self._bot = bot

    def details(self, market, resolution):
        """Will return details on the reasong why the signal was emited."""
        raise NotImplementedError

    def signal(self, market, resolution, start, end):
        """Will return either a BUY, SELL or WAIT signal for the given
        market"""
        raise NotImplementedError


class NullStrategy(Strategy):

    def details(self, market, resolution):
        """Will return details on the reasong why the signal was emited."""
        return "I am doing nothing but waiting..."

    def signal(self, market, resolution, start, end):
        """Will return either a BUY, SELL or WAIT signal for the given
        market"""
        return Signal(WAIT, datetime.datetime.utcnow())


class InteractivStrategyWrapper(object):

    def __init__(self, strategie):
        self._strategie = strategie
        self._bot = None

    def set_bot(self, bot):
        self._bot = bot

    def __str__(self):
        return "Interavtiv: {}".format(self._strategie)

    def signal(self, market, resolution, start, end):
        """Will return either a BUY, SELL or WAIT signal for the given
        market"""

        # Get current chart
        click.echo(render_bot_title(self._bot, market, resolution))
        signal = self._strategie.signal(market, resolution, start, end)

        click.echo('Signal: {} {}'.format(signal.date, signal_map[signal.value]))
        click.echo('')
        options = []
        if self._bot.btc:
            options.append("b) Buy")
        if self._bot.amount:
            options.append("s) Sell")
        options.append("l) Tradelog")
        options.append("p) Performance of bot")
        options.append("d) Show details on signal")
        options.append("q) Quit")
        options.append("")
        options.append("Press any key to continue")

        click.echo(u'\n'.join(options))
        c = click.getchar()
        if c == 'b' and self._bot.btc:
            # btc = click.prompt('BTC', default=self._bot.btc)
            if click.confirm('Buy for {} btc?'.format(self._bot.btc)):
                return Signal(BUY, datetime.datetime.utcnow())
        if c == 's' and self._bot.amount:
            # amount = click.prompt('Amount', default=self._bot.amount)
            if click.confirm('Sell {}?'.format(self._bot.amount)):
                return Signal(SELL, datetime.datetime.utcnow())
        if c == 'l':
            click.echo(render_bot_tradelog(self._bot.trades))
        if c == 'p':
            click.echo(render_bot_statistic(self._bot.stat()))
        if c == 'd':
            click.echo(self._strategie.details(market, resolution))
        if c == 'q':
            return Signal(QUIT, datetime.datetime.utcnow())
        else:
            return Signal(WAIT, datetime.datetime.utcnow())
