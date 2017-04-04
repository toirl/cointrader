# -*- coding: utf-8 -*-
import select

import sys
import datetime
import time
import logging
import sqlalchemy as sa
import click
from cointrader import Base, engine, db
from cointrader.indicators import (
    WAIT, BUY, SELL, Signal
)
from cointrader.helpers import (
    render_bot_statistic, render_bot_tradelog,
    render_bot_title, render_signal_detail,
    render_user_options
)

TIMEOUT = 0
# Number of seconds the bot will wait for user input in automatic mode
# to reattach the bot

log = logging.getLogger(__name__)


def replay_tradelog(trades):
    btc = 0
    amount = 0
    for t in trades:
        if t.order_type == "INIT":
            btc = t.btc
            amount = t.amount
        elif t.order_type == "BUY":
            btc -= t.btc
            amount += t.amount
        else:
            btc += t.btc
            amount -= t.amount
    return btc, amount


def init_db():
    Base.metadata.create_all(engine)


def get_bot(market, strategy, resolution, start, end, btc, amount):

    try:
        bot = db.query(Cointrader).filter(Cointrader.market == market._name).one()
        log.info("Loading bot {} {}".format(bot.market, bot.id))
        bot._market = market
        bot.strategy = str(strategy)
        bot._strategy = strategy
        bot._resolution = resolution
        bot._start = start
        bot._end = end
        db.commit()
        btc, amount = replay_tradelog(bot.trades)
        log.info("Loaded state from trade log: {} BTC {} COINS".format(btc, amount))
        bot.btc = btc
        bot.amount = amount
    except sa.orm.exc.NoResultFound:
        bot = Cointrader(market, strategy, resolution, start, end)
        log.info("Creating new bot {}".format(bot.market))
        if btc is None:
            balances = market._exchange.get_balance()
            btc = balances["BTC"]["quantity"]
        if amount is None:
            balances = market._exchange.get_balance()
            amount = balances[market.currency]["quantity"]
        bot.btc = btc
        bot.amount = amount
        chart = market.get_chart(resolution, start, end)
        rate = chart.get_first_point()["close"]
        date = datetime.datetime.utcfromtimestamp(chart.get_first_point()["date"])

        trade = Trade(date, "INIT", 0, 0, market._name, rate, amount, 0, btc, 0)
        bot.trades.append(trade)
        db.add(bot)
    db.commit()
    strategy.set_bot(bot)
    return bot


class Trade(Base):
    """All trades of cointrader are saved in the database. A trade can either be a BUY or SELL."""
    __tablename__ = "trades"
    id = sa.Column(sa.Integer, primary_key=True)
    bot_id = sa.Column(sa.Integer, sa.ForeignKey('bots.id'))
    date = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    order_type = sa.Column(sa.String, nullable=False)
    order_id = sa.Column(sa.Integer, nullable=False)
    trade_id = sa.Column(sa.Integer, nullable=False)
    market = sa.Column(sa.String, nullable=False)
    rate = sa.Column(sa.Float, nullable=False)

    amount = sa.Column(sa.Float, nullable=False)
    amount_taxed = sa.Column(sa.Float, nullable=False)
    btc = sa.Column(sa.Float, nullable=False)
    btc_taxed = sa.Column(sa.Float, nullable=False)

    def __init__(self, date, order_type, order_id, trade_id, market, rate, amount, amount_taxed, btc, btc_taxed):
        """Initialize a new trade log entry.

        :bot_id: ID of the bot which initiated the trade
        :date: Date of the order
        :order_id: ID of the order
        :order_type: Type of order. Can be either "BUY, SELL"
        :trade_id: ID of a single trade within the order
        :market: Currency_pair linke BTC_DASH
        :rate: Rate for the order
        :amount: How many coins sold
        :amount_taxed: How many coins bought (including fee) order
        :btc: How many payed on buy
        :btc_taxed: How many BTC get (including fee) from sell

        """
        if not isinstance(date, datetime.datetime):
            self.date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        else:
            self.date = date
        self.order_type = order_type
        self.order_id = order_id
        self.trade_id = trade_id
        self.market = market
        self.rate = rate
        self.amount = amount
        self.amount_taxed = amount_taxed
        self.btc = btc
        self.btc_taxed = btc_taxed
        if self.order_type == "BUY":
            log.info("{}: BUY {} @ {} paid -> {} BTC".format(self.date, self.amount_taxed, self.rate, self.btc))
        elif self.order_type == "SELL":
            log.info("{}: SELL {} @ {} earned -> {} BTC".format(self.date, self.amount, self.rate, self.btc_taxed))
        else:
            log.info("{}: INIT {} BTC {} COINS".format(self.date, self.btc, self.amount))


class Cointrader(Base):
    """Cointrader"""
    __tablename__ = "bots"
    id = sa.Column(sa.Integer, primary_key=True)
    created = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    active = sa.Column(sa.Boolean, nullable=False, default=True)
    market = sa.Column(sa.String, nullable=False)
    strategy = sa.Column(sa.String, nullable=False)
    automatic = sa.Column(sa.Boolean, nullable=False)
    trades = sa.orm.relationship("Trade")

    def __init__(self, market, strategy, resolution="30m", start=None, end=None, automatic=False):

        self.market = market._name
        self.strategy = str(strategy)
        self.automatic = automatic

        self._market = market
        self._strategy = strategy
        self._resolution = resolution
        self._start = start
        self._end = end

        self.amount = 0
        self.btc = 0
        # The bot has either btc to buy or amount of coins to sell.

    def get_last_sell(self):
        for t in self.trades[::-1]:
            if t.order_type == "SELL":
                return t

    def get_last_buy(self):
        for t in self.trades[::-1]:
            if t.order_type == "BUY":
                return t

    def _buy(self):
        result = self._market.buy(self.btc)
        order_id = result["orderNumber"]
        order_type = "BUY"
        total_amount = 0
        for t in result["resultingTrades"]:
            trade_id = t["tradeID"]
            date = t["date"]
            amount = t["amount"]
            total_amount += float(amount)
            rate = t["rate"]
            btc = t["total"]
            trade = Trade(date, order_type, order_id, trade_id, self._market._name, rate, 0, amount, self.btc, btc)
            self.trades.append(trade)

        # Finally set the internal state of the bot. BTC will be 0 after
        # buying but we now have some amount of coins.
        self.amount = total_amount
        self.btc = 0
        self.state = 1
        db.commit()

    def _sell(self):
        result = self._market.sell(self.amount)
        order_id = result["orderNumber"]
        order_type = "SELL"
        total_btc = 0
        for t in result["resultingTrades"]:
            trade_id = t["tradeID"]
            date = t["date"]
            amount = t["amount"]
            rate = t["rate"]
            btc = t["total"]
            total_btc += float(btc)
            trade = Trade(date, order_type, order_id, trade_id, self._market._name, rate, self.amount, amount, 0, btc)
            self.trades.append(trade)

        # Finally set the internal state of the bot. Amount will be 0 after
        # selling but we now have some BTC.
        self.state = 0
        self.amount = 0
        self.btc = total_btc
        db.commit()

    def stat(self, delete_trades=False):
        """Returns a dictionary with some statistic of the performance
        of the bot.  Performance means how good cointrader performs in
        comparison to the market movement. Market movement is measured
        by looking at the start- and end rate of the chart.

        The performance of cointrader is measured by looking at the
        start and end value of the trade. These values are also
        multiplied with the start and end rate. So if cointrader does
        some good decisions and increases eater btc or amount of coins
        of the bot the performance should be better."""

        chart = self._market.get_chart(self._resolution, self._start, self._end)

        first = chart.get_first_point()
        market_start_rate = first["close"]
        start_date = datetime.datetime.utcfromtimestamp(first["date"])

        last = chart.get_last_point()
        market_end_rate = last["close"]
        end_date = datetime.datetime.utcfromtimestamp(last["date"])

        # Set start value
        for trade in self.trades:
            if trade.order_type == "INIT":
                trader_start_btc = trade.btc
                trader_start_amount = trade.amount
                market_start_btc = trade.btc
                market_start_amount = trade.amount

        trader_end_btc = trader_start_btc
        trader_end_amount = trader_start_amount
        for trade in self.trades:
            if trade.order_type == "BUY":
                trader_end_amount += trade.amount_taxed
                trader_end_btc -= trade.btc
            elif trade.order_type == "SELL":
                trader_end_btc += trade.btc_taxed
                trader_end_amount -= trade.amount

        trader_start_value = trader_start_btc + trader_start_amount * market_start_rate
        market_start_value = trader_start_value
        trader_end_value = trader_end_btc + trader_end_amount * market_end_rate
        market_end_value = market_start_btc + market_start_amount * market_end_rate
        trader_profit = trader_end_value - trader_start_value
        market_profit = market_end_value - market_start_value

        stat = {
            "start": start_date,
            "end": end_date,
            "market_start_value": market_start_value,
            "market_end_value": market_end_value,
            "profit_chart": market_profit / market_end_value * 100,
            "trader_start_value": trader_start_value,
            "trader_end_value": trader_end_value,
            "profit_cointrader": trader_profit / trader_end_value * 100,
        }
        if delete_trades:
            for trade in self.trades:
                db.delete(trade)
            db.commit()
        return stat

    def _in_time(self, date):
        return (self._start is None or self._start <= date) and (self._end is None or date <= self._end)

    def _get_interval(self, automatic, backtest):
        # Set number of seconds to wait until the bot again call for a
        # trading signal. This defaults to the resolution of the bot
        # which is provided on initialisation.
        if automatic and not backtest:
            interval = self._market._exchange.resolution2seconds(self._resolution)
        else:
            interval = 0
        return interval

    def _handle_signal(self, signal):
        if signal.value == BUY and self.btc and self._in_time(signal.date):
            self._buy()
        elif signal.value == SELL and self.amount and self._in_time(signal.date):
            self._sell()

    def start(self, backtest=False, automatic=False):
        """Start the bot and begin trading with given amount of BTC.

        The bot will trigger a analysis of the chart every N seconds.
        The default number of seconds is set on initialisation using the
        `resolution` option. You can overwrite this setting
        by using the `interval` option.

        By setting the `backtest` option the trade will be simulated on
        real chart data. This is useful for testing to see how good
        your strategy performs.

        :btc: Amount of BTC to start trading with
        :backtest: Simulate trading on historic chart data on the given market.
        :returns: None
        """

        while 1:
            chart = self._market.get_chart(self._resolution, self._start, self._end)
            signal = self._strategy.signal(chart)
            log.debug("{} {}".format(signal.date, signal.value))
            interval = self._get_interval(self.automatic, backtest)

            if not automatic:
                click.echo(render_bot_title(self, self._market, chart))
                click.echo(render_signal_detail(signal))

                options = []
                if self.btc:
                    options.append(('b', 'Buy'))
                if self.amount:
                    options.append(('s', 'Sell'))
                options.append(('l', 'Tradelog'))
                options.append(('p', 'Performance of bot'))
                if not automatic:
                    options.append(('d', 'Detach'))
                options.append(('q', 'Quit'))

                click.echo(render_user_options(options))
                c = click.getchar()
                if c == 'b' and self.btc:
                    # btc = click.prompt('BTC', default=self.self.btc)
                    if click.confirm('Buy for {} btc?'.format(self.btc)):
                        signal = Signal(BUY, datetime.datetime.utcnow())
                if c == 's' and self.amount:
                    # amount = click.prompt('Amount', default=self.self.amount)
                    if click.confirm('Sell {}?'.format(self.amount)):
                        signal = Signal(SELL, datetime.datetime.utcnow())
                if c == 'l':
                    click.echo(render_bot_tradelog(self.trades))
                if c == 'p':
                    click.echo(render_bot_statistic(self.stat()))
                if c == 'd':
                    automatic = True
                    log.info("Bot detached")
                if c == 'q':
                    log.info("Bot stopped")
                    sys.exit(0)
                else:
                    signal = Signal(WAIT, datetime.datetime.utcnow())

            if automatic:
                click.echo("Press 'A' with in the next {} secods to reattach the bot.".format(TIMEOUT))
                i, o, e = select.select([sys.stdin], [], [], TIMEOUT)
                if (i):
                    value = sys.stdin.readline().strip()
                    print(value)
                    if value == "A":
                        automatic = False

            if signal:
                self._handle_signal(signal)

            if backtest:
                if not self._market.continue_backtest():
                    log.info("Backtest finished")
                    break

            time.sleep(interval)
