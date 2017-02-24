#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import logging
import datetime

log = logging.getLogger(__name__)

BUY = 1
SELL = -1
WAIT = 0
signal_map = {
    BUY: "BUY",
    WAIT: "WAIT",
    SELL: "SELL"
}
# Signals for strategies.


class Strategy(object):

    """Docstring for Strategy. """

    def __init__(self):
        self._signal_history = []
        """Store last emitted signals"""

    def details(self, market, resolution, timeframe):
        """Will return details on the reasong why the signal was emited."""
        raise NotImplementedError

    def signal(self, market, resolution, timeframe):
        """Will return either a BUY, SELL or WAIT signal for the given
        market"""
        raise NotImplementedError


class InteractivStrategyWrapper(object):

    def __init__(self, strategie):
        self._strategie = strategie

    def signal(self, market, resolution, timeframe):
        """Will return either a BUY, SELL or WAIT signal for the given
        market"""

        # Get current chart
        signal = self._strategie.signal(market, resolution, timeframe)

        click.echo('Date: {}'.format(datetime.datetime.now()))
        click.echo('Url: {}'.format(market.url))
        click.echo('Signal: {}'.format(signal_map[signal]))
        click.echo('What should I do? Press any key to continue')
        click.echo('[b (buy), s (sell)], d (details), space (wait)]')
        c = click.getchar()
        if c == 'b':
            return BUY
        if c == 's':
            return SELL
        if c == 'd':
            click.echo(self._strategie.details(market, resolution, timeframe))
            return self.signal(market, resolution, timeframe)
        else:
            return WAIT
