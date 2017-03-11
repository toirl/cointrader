# -*- coding: utf-8 -*-
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

__author__ = """Torsten Irländer"""
__email__ = 'torsten.irlaender@googlemail.com'
__version__ = '0.3.1'

Base = declarative_base()

engine = sa.create_engine('sqlite:///cointrader.db')
Session = sa.orm.sessionmaker(bind=engine)
db = Session()

Base.metadata.create_all(engine)
