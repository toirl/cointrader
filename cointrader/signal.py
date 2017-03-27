#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


