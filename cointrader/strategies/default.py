#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from cointrader.strategy import Strategy

log = logging.getLogger(__name__)


class Klondike(Strategy):

    def signal(self, market, resolution, start, end):
        self._chart = market.get_chart(resolution, start, end)
        signal = self.double_cross(self._chart)
        return signal
