#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import logging
import logging.config
if (sys.version_info > (3, 0)):
    # Python 3 code in this block
    import configparser
else:
    # Python 2 code in this block
    import ConfigParser as configparser

DEFAULT_CONFIG = ".cointrader.ini"


def get_path_to_config():
    env = os.getenv("HOME")
    return os.path.join(env, DEFAULT_CONFIG)


class Config(object):

    def __init__(self, configfile=None):

        self.verbose = False
        self.market = "poloniex"
        self.api_key = None
        self.api_secret = None

        if configfile:
            logging.config.fileConfig(configfile.name)
            config = configparser.ConfigParser()
            config.readfp(configfile)
            exchange = config.get("DEFAULT", "exchange")
            self.api_key = config.get(exchange, "api_key")
            self.api_secret = config.get(exchange, "api_secret")

    @property
    def api(self):
        if not self.api_key or not self.api_secret:
            raise RuntimeError("API not configured")
        return self.api_key, self.api_secret
