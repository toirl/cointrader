#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_helpers
----------------------------------

Tests for `cointrader.strategies.helpers` module.
"""


def test_is_max_value_1():
    from cointrader.strategies.helpers import is_max_value
    values = [1, 2, 3, 4, 5]
    result = is_max_value(values)
    assert result is False


def test_is_max_value_2():
    from cointrader.strategies.helpers import is_max_value
    values = [1, 2, 3, 5, 4]
    result = is_max_value(values)
    assert result is True


def test_is_max_value_3():
    from cointrader.strategies.helpers import is_max_value
    values = [-4, -3, -2, -3]
    result = is_max_value(values)
    assert result is False


def test_is_min_value_1():
    from cointrader.strategies.helpers import is_min_value
    values = [1, 2, 3, 4, 5]
    result = is_min_value(values)
    assert result is False


def test_is_min_value_2():
    from cointrader.strategies.helpers import is_min_value
    values = [5, 2, 3, 5, 4]
    result = is_min_value(values)
    assert result is True


def test_is_min_value_3():
    from cointrader.strategies.helpers import is_min_value
    values = [-4, -3, -2, -3]
    result = is_min_value(values)
    assert result is True
