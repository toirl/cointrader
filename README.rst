===============================
Cointrader
===============================


.. image:: https://img.shields.io/pypi/v/cointrader.svg
        :target: https://pypi.python.org/pypi/cointrader

.. image:: https://img.shields.io/travis/toirl/cointrader.svg
        :target: https://travis-ci.org/toirl/cointrader

.. image:: https://api.codacy.com/project/badge/Grade/ef487c2c01d4491e91dec5b8490214ee
        :target: https://www.codacy.com/app/torsten/cointrader?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=toirl/cointrader&amp;utm_campaign=Badge_Grade

.. image:: https://readthedocs.org/projects/cointrader/badge/?version=latest
        :target: https://cointrader.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/toirl/cointrader/shield.svg
     :target: https://pyup.io/repos/github/toirl/cointrader/
     :alt: Updates


Cointrader is Python based CLI trading application for crypto currencies on
the Poloniex_ exchange.  Cointrader can be used for semiautomatic guided
trading.

.. danger::

        You could loose money. Use cointrader at your own risk! I do not
        accept any responsibility for any losses.

        Cointrader is Alpha quality! It is not meant to be used for serious
        trading yet. It is still in a early development phase and has a bunch
        full of known defects. Expect all all aspects of the application to
        change in the future. Cointrader is not roundly tested.

        If you want to help cointrader the best Free Software trading bot your
        contribution is highly appreciated! Find details on how to participate
        in the `documentation <http://cointrader.readthedocs.io/en/latest/contributing.html>`_.


* Status: **Alpha**
* Free software: MIT license
* Source: https://github.com/toirl/cointrader
* Documentation: https://cointrader.readthedocs.io.

If you like the program, I am looking forward to a donation :)

* DASH: XypsuUMRTioV7bHSVzSDkNgihtr1gfiqAr
* BTC : 1L5xtVirGVpDL7958SPaHb6p9dHZoaQ2Cz

Features
--------

* Automatic trading. Cointrader will buy and sell following emitted
  trading signals.
* Semiautomatic trading. Cointrader just emits trading signals. You finally
  decide if you want to follow the signals.
* Paper trading. Just simlate trading. Do not actually place real orders.
* Trade logbook
* Profit/Loss analysis (Bot vs. Market)
* Backtesting. Check how good your strategy performs on historic charts.
* Explore exchanges and find interesting markets to trade on
* Show your balances

Planned
-------

* Risk- and Money management

 * Stop loss limits
 * Take profit limits

* Pluggable external trading strategies
* Support more exchanges

Motivation
----------
This program exists because I want to learn more about automatic trading
based on a technical analysis of charts.
I am no expert on trading or crypto currencies! I am a professional
Python programmer who stuck his nose into the crypto coin and trading world in
2017 and who was directly fascinated on this topic. After reading some books
on technical analysis I decided to write this program to learn more about
how automatic trading works.

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Poloniex: https://poloniex.com
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

