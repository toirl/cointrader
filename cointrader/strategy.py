#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import click
import logging
from .helpers import render_bot_statistic, render_bot_tradelog, render_bot_title, render_signal_details

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

    def sma(self, chart, sma1=5, sma2=20):
        """Generates a trade signal based on two moving averanges with
        different width. A BUY signal is generated if the shorter SMA1
        crosses the longer SMA2 in up direction and the SMA1 is higher
        than the closing price. A SELL signal is emited if the SMA1
        crosses the SMA2 from above and is lower than the closing
        price."""

        sma_1 = chart.sma(sma1)[-1]
        sma_2 = chart.sma(sma2)[-1]
        signal = WAIT

        if self._value > sma_1 and sma_1 > sma_2:
            signal = BUY
        elif self._value < sma_1 and sma_1 < sma_2:
            signal = SELL
        self._details["SMA"] = {"signal": signal, "details": "SMA{}: {}, SMA{}: {})".format(sma1, sma_1, sma2, sma_2)}
        return Signal(signal, self._date)

    def ema(self, chart, ema1=5, ema2=20):
        """Generates a trade signal based on two moving averanges with
        different width. A BUY signal is generated if the shorter SMA1
        crosses the longer SMA2 in up direction and the SMA1 is higher
        than the closing price. A SELL signal is emited if the SMA1
        crosses the SMA2 from above and is lower than the closing
        price."""

        ema_1 = chart.ema(ema1)[-1]
        ema_2 = chart.ema(ema2)[-1]
        signal = WAIT

        if self._value > ema_1 and ema_1 > ema_2:
            signal = BUY
        elif self._value < ema_1 and ema_1 < ema_2:
            signal = SELL
        self._details["EMA"] = {"signal": signal, "details": "EMA{}: {}, EMA{}: {})".format(ema1, ema_1, ema2, ema_2)}
        return Signal(signal, self._date)

    def macdh(self, chart):
        """Generates a SELL signal as soon as the macdh value changes
        from positve value into negativ value. It generates a BUY signal
        if the value from negativ to positiv."""

        macdh = chart.macdh()[::-1][0:2]
        if macdh[0] < 0 and macdh[1] > 0:
            signal = SELL
        elif macdh[0] > 0 and macdh[1] < 0:
            signal = BUY
        else:
            signal = WAIT
        self._details["MACDH"] = {"signal": signal, "details": "MACDH: {}".format(macdh)}
        return Signal(signal, self._date)


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
        click.echo(render_signal_details(self._strategie.details(market, resolution)))
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
            click.echo(render_signal_details(self._strategie.details(market, resolution)))
        if c == 'q':
            return Signal(QUIT, datetime.datetime.utcnow())
        else:
            return Signal(WAIT, datetime.datetime.utcnow())
