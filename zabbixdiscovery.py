#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

logger = logging.getLogger(__name__)


class ZabbixDiscovery(object):

    def __init__(self, **ctx):

        self.item_key = ctx.get('lld_key')  # 'S2MOUNTPOINT'
        self.lld_list = ctx.get('lld_list', [])

    def dump(self):

        print json.dumps(self.handle(), indent=2)

    def handle(self):

        return self.do_handle()

    def do_handle(self):

        discovery = {"data": []}

        key = '{#' + self.item_key + '}'

        discovery['data'] = [{key: el} for el in self.lld_list]

        return discovery
