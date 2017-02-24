#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json


class Config(object):

    def __init__(self, config=None):

        self.verbose = False
        self.market = "poloniex"
        self.api_key = None
        self.api_secret = None

        if config:
            values = json.load(config)
            for key in values:
                if key == "api":
                    self.api_key = values[key]["key"]
                    self.api_secret = values[key]["secret"]

    @property
    def api(self):
        if not self.api_key or not self.api_secret:
            raise RuntimeError("API not configured")
        return self.api_key, self.api_secret
