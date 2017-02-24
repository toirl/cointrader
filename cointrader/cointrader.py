# -*- coding: utf-8 -*-
import datetime
import time
import logging
from . import Base, sa
from .strategy import BUY, SELL, WAIT

log = logging.getLogger(__name__)

def get_trader(exchange, market):
    """TODO: Docstring for get_trader.

    :arg1: TODO
    :returns: TODO

    """
    pass


class Cointrader(Base):
    """Docstring for Cointrader. """
    __tablename__ = "bots"
    id = sa.Column(sa.Integer, primary_key=True)
    created = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __init__(self, market, strategy, resolution="30m", timeframe="1d"):
        self._market = market
        self._strategy = strategy
        self._resolution = resolution
        self._timeframe = timeframe

    def start(self, interval=None):
        if interval is None:
            interval = self._market._exchange.resolution2seconds(self._resolution)
        while 1:
            signal = self._strategy.signal(self._market, self._resolution, self._timeframe)
            log.debug('Date: {}'.format(datetime.datetime.now()))
            if signal == BUY:
                log.debug("Signal: BUY")
                self._market.buy()
            elif signal == SELL:
                log.debug("Signal: SELL")
                self._market.sell()
            elif signal == WAIT:
                log.debug("Signal: WAIT")
            else:
                raise RuntimeWarning("Unknow signal returned from strategy!")
            log.debug("ZZZ for {} seconds".format(interval))
            time.sleep(interval)
