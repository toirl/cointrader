# -*- coding: utf-8 -*-
import datetime
import time
import logging
import sqlalchemy as sa
from . import Base, engine, db
from .strategy import BUY, SELL, QUIT
from .exchange import BacktestMarket

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


def get_bot(market, strategy, resolution, timeframe, btc, amount):
    try:
        bot = db.query(Cointrader).filter(Cointrader.market == market._name).one()
        log.info("Loading bot {} {}".format(bot.market, bot.id))
        bot._market = market
        bot.strategy = str(strategy)
        bot._strategy = strategy
        bot._resolution = resolution
        bot._timeframe = timeframe
        db.commit()
        btc, amount = replay_tradelog(bot.trades)
        log.info("Loaded state from trade log: {} BTC {} COINS".format(btc, amount))
        bot.btc = btc
        bot.amount = amount
    except sa.orm.exc.NoResultFound:
        bot = Cointrader(market, strategy, resolution, timeframe)
        log.info("Creating new bot {}".format(bot.market))
        if btc is None:
            balances = market._exchange.get_balance()
            btc = balances["BTC"]["quantity"]
        if amount is None:
            balances = market._exchange.get_balance()
            amount = balances[market.currency]["quantity"]
        bot.btc = btc
        bot.amount = amount
        chart = market.get_chart(resolution, timeframe)
        rate = chart._data[-1]["close"]
        date = datetime.datetime.utcnow()

        # If we have a "backtest" market that set the start of trading
        # to the first date in chart.
        if isinstance(market, BacktestMarket):
            date = datetime.datetime.utcfromtimestamp(chart._data[0]["date"])

        trade = Trade(date, "INIT", 0, 0, market._name, amount, rate, btc)
        bot.trades.append(trade)
        db.add(bot)
    db.commit()
    strategy.set_bot(bot)
    return bot


class Trade(Base):
    """Trading log"""
    __tablename__ = "trades"
    id = sa.Column(sa.Integer, primary_key=True)
    bot_id = sa.Column(sa.Integer, sa.ForeignKey('bots.id'))
    date = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    order_type = sa.Column(sa.String, nullable=False)
    order_id = sa.Column(sa.Integer, nullable=False)
    trade_id = sa.Column(sa.Integer, nullable=False)
    market = sa.Column(sa.String, nullable=False)
    amount = sa.Column(sa.Float, nullable=False)
    rate = sa.Column(sa.Float, nullable=False)
    btc = sa.Column(sa.Float, nullable=False)
    value = sa.Column(sa.Float, nullable=False)

    def __init__(self, date, order_type, order_id, trade_id, market, amount, rate, btc):
        """TODO: to be defined1.

        :bot_id: ID of the bot which initiated the trade
        :date: Date of the order
        :order_id: ID of the order
        :trade_id: ID of a single trade within the order
        :market: Currency_pair linke BTC_DASH
        :amount: How many coins bought (including fee)/sold in order
        :rate: Rate for the order
        :order_type: Type of order. Can be either "BUY, SELL"
        :btc: How many BTC you placed in order/get (including fee) from order

        """
        if not isinstance(date, datetime.datetime):
            self.date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        else:
            self.date = date
        self.order_type = order_type
        self.order_id = order_id
        self.trade_id = trade_id
        self.market = market
        self.amount = amount
        self.rate = rate
        self.btc = btc
        self.value = 0
        if self.order_type == "BUY":
            self.value = float(amount) * float(rate)
            log.info("{}: BUY {} @ {} paid -> {} BTC".format(self.date, self.amount, self.rate, self.btc))
        elif self.order_type == "SELL":
            self.value = btc
            log.info("{}: SELL {} @ {} earned -> {} BTC".format(self.date, self.amount, self.rate, self.btc))
        else:
            self.value = float(btc) + (float(amount) * float(rate))
            log.info("{}: INIT {} BTC {} COINS".format(self.date, self.btc, self.amount))


class Cointrader(Base):
    """Cointrader"""
    __tablename__ = "bots"
    id = sa.Column(sa.Integer, primary_key=True)
    created = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)
    active = sa.Column(sa.Boolean, nullable=False, default=True)
    market = sa.Column(sa.String, nullable=False)
    strategy = sa.Column(sa.String, nullable=False)
    trades = sa.orm.relationship("Trade")

    def __init__(self, market, strategy, resolution="30m", timeframe="1d"):

        self.market = market._name
        self.strategy = str(strategy)

        self._market = market
        self._strategy = strategy
        self._resolution = resolution
        self._timeframe = timeframe

        self.amount = 0
        self.btc = 0
        # The bot has either btc to buy or amount of coins to sell.

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
            trade = Trade(date, order_type, order_id, trade_id, self._market._name, amount, rate, btc)
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
            trade = Trade(date, order_type, order_id, trade_id, self._market._name, amount, rate, btc)
            self.trades.append(trade)

        # Finally set the internal state of the bot. Amount will be 0 after
        # selling but we now have some BTC.
        self.state = 0
        self.amount = 0
        self.btc = total_btc
        db.commit()

    def stat(self, delete_trades=False):
        """Returns a dictionary with some statistic of the performance of the bot.
        Performance means how good cointrader performs in comparison to
        the market movement. Market movement is measured by looking at
        the start- and end rate of the chart.

        The performance of cointrader is measured by looking at the
        start and end value of the trade. These values are also
        multiplied with the start and end rate. So if cointrader does
        some good decisions and increases eater btc or amount of coins
        of the bot the performance should be better."""

        # Get chart data.
        data = self._market.get_chart().data
        market_end_rate = data[-1]["close"]
        market_start_rate = data[0]["close"]

        for trade in self.trades:
            value = trade.value * market_end_rate
            if trade.order_type == "INIT":
                start_rate = trade.rate
                start_date = trade.date
                start_value = trade.value * market_start_rate

        stat = {
            "start": start_date,
            "end": datetime.datetime.utcfromtimestamp(data[-1]["date"]),
            "start_rate": start_rate,
            "end_rate": data[-1]["close"],
            "profit_chart": ((market_end_rate - market_start_rate) / market_end_rate) * 100,
            "start_value": start_value,
            "end_value": value,
            "profit_cointrader": ((value - start_value) / (start_value or 1) * 100),
        }
        if delete_trades:
            for trade in self.trades:
                db.delete(trade)
            db.commit()
        return stat

    def start(self, interval=None, backtest=False):
        """Start the bot and begin trading with given amount of BTC.

        The bot will trigger a analysis of the chart every N seconds.
        The default number of seconds is set on initialisation using the
        `resolution` option. You can overwrite this setting
        by using the `interval` option.

        By setting the `backtest` option the trade will be simulated on
        real chart data. This is useful for testing to see how good
        your strategy performs.

        :btc: Amount of BTC to start trading with
        :interval: Number of seconds to wait until the bot again call
        for a trading signal. This defaults to the resolution of the bot
            which is provided on initialisation.
        :backtest: Simulate trading on historic chart data on the given market.
        :returns: None

        """
        self._start_btc = self.btc
        if interval is None:
            interval = self._market._exchange.resolution2seconds(self._resolution)
        while 1:
            signal = self._strategy.signal(self._market, self._resolution, self._timeframe)
            if signal == BUY and self.btc:
                self._buy()
            elif signal == SELL and self.amount:
                self._sell()
            elif signal == QUIT:
                log.info("Bot stopped")
                break
            if backtest:
                if not self._market.continue_backtest():
                    log.info("Backtest finished")
                    break
            time.sleep(interval)
