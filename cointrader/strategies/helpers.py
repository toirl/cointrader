#!/usr/bin/env python
# -*- coding: utf-8 -*-


def is_max_value(values):
    """Will return True if the last recent values of the given list of
    values describe a local maximum value. A local maximum is defined as
    followed: A < B > C

    :series: List of values
    :returns: True or False

    """
    # Only take the last three values to check if we see a local
    # maximum.
    v = values[-3::]
    a = v[0]
    b = v[1]
    c = v[2]
    return a < b > c


def is_min_value(values):
    """Will return True if the last recent values of the given list of
    values describe a local minimum value. A local minimum is defined as
    followed: A > B < C

    :series: List of values
    :returns: True or False

    """
    # Only take the last three values to check if we see a local
    # maximum.
    v = values[-3::]
    a = v[0]
    b = v[1]
    c = v[2]
    return a > b < c
