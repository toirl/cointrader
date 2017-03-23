# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from cointrader.strategies.null import NullStrategy
from cointrader.strategies.trend import Followtrend
from cointrader.strategies.default import Klondike

__author__ = """Torsten Irländer"""
__email__ = 'torsten.irlaender@googlemail.com'
__version__ = '0.4.0'

Base = declarative_base()

engine = sa.create_engine('sqlite:///cointrader.db')
Session = sa.orm.sessionmaker(bind=engine)
db = Session()

STRATEGIES = {
    "null": NullStrategy,
    "trend": Followtrend,
    "klondike": Klondike
}
