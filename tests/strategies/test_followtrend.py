#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_followtrend
----------------------------------

Tests for `cointrader.strategies.trend` module.
"""


def test_monoton_raising():
    """Monoton raising chart. State is still in in initial phase.
    Therefor no signal is emitted"""
    from cointrader.strategies.trend import followtrend
    chart1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    signal = followtrend(chart1)
    assert signal == 0


def test_monoton_falling():
    """Monoton falling chart.  State is still in in initial phase.
    Therefor no signal is emitted"""
    from cointrader.strategies.trend import followtrend
    chart1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    chart1.reverse()
    signal = followtrend(chart1)
    assert signal == 0


def test_localmin_found():
    """Test initial phase. After reaching a local minimum no local
    maximum has been found yet. No signal is emitted. We are still
    waiting for entering the correction phase"""
    from cointrader.strategies.trend import followtrend
    chart1 = [9, 8, 5, 4, 3, 2, 1, 2, 4, 5]
    signal = followtrend(chart1)
    assert signal == 0


def test_localmax_found():
    """Test initial phase. After reaching a local maximum no local
    minimum has been found yet. No signal is emitted. We are still
    waiting for entering the correction phase"""
    from cointrader.strategies.trend import followtrend
    chart1 = [1, 2, 5, 7, 8, 7, 6, 5, 4]
    signal = followtrend(chart1)
    assert signal == 0


def test_raising_correction():
    """Test correction phase. After reaching a local maximum and local
    minimum we are in correction phase. No signal is emitted. We are still
    waiting for crossing the last maximum."""
    from cointrader.strategies.trend import followtrend
    chart1 = [1, 2, 5, 4, 3, 4, 3, 4, 3]
    signal = followtrend(chart1)
    assert signal == 0


def test_falling_correction():
    """Test correction phase. After reaching a local maximum and local
    minimum we are in correction phase. No signal is emitted. We are still
    waiting for crossing the last minimum."""
    from cointrader.strategies.trend import followtrend
    chart1 = [9, 7, 5, 1, 2, 3, 6, 2, 3, 2, 3]
    signal = followtrend(chart1)
    assert signal == 0


def test_raising_buy_signal():
    """Test correction phase. After reaching a local maximum and local
    minimum we are in correction phase and the last maximum is exeeded.
    BUY signal is emitted"""
    from cointrader.strategies.trend import followtrend
    chart1 = [1, 2, 5, 4, 3, 4, 3, 4, 3, 5, 6]
    signal = followtrend(chart1)
    assert signal == 1


def test_raising_sell_signal():
    """Test correction phase. After reaching a local maximum and local
    minimum we are in correction phase and the last minimum is exeeded.
    SELL signal is emitted"""
    from cointrader.strategies.trend import followtrend
    chart1 = [7, 3, 5, 4, 3, 4, 3, 4, 3, 3, 2]
    signal = followtrend(chart1)
    assert signal == -1


def test_falling_buy_signal():
    """Test correction phase. After reaching a local maximum and local
    minimum we are in correction phase and the last maximum is exeeded.
    BUY signal is emitted"""
    from cointrader.strategies.trend import followtrend
    chart1 = [9, 8, 5, 6, 7, 6, 5, 6, 10]
    signal = followtrend(chart1)
    assert signal == 1


def test_falling_sell_signal():
    """Test correction phase. After reaching a local maximum and local
    minimum we are in correction phase and the last maximum is exeeded.
    BUY signal is emitted"""
    from cointrader.strategies.trend import followtrend
    chart1 = [9, 8, 5, 6, 7, 6, 5, 5, 4]
    signal = followtrend(chart1)
    assert signal == -1
