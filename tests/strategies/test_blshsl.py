#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_blshsl.py
----------------------------------
This will test the blshsl strategy. Which means basically buy low, sell
high, stop loss.
"""


def test_monoton_raising():
    """Monoton raising chart. State is still in in initial phase.
    Therefor no signal is emitted"""
    from cointrader.indicators import followtrend
    chart1 = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9)]
    signal = followtrend(chart1)
    assert signal.value == 0
