#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys
import psutil

from pykit import fsutil
from pykit import logutil
from zabbixdiscovery import ZabbixDiscovery
from zabbixsender import ZabbixSender

logger = logging.getLogger(__name__)


def get_discovery_list():

    try:

        _list = fsutil.get_all_mountpoint()
        logger.info("get_discovery_list: " + repr(_list))

        return _list

    except Exception as e:

        logger.error("while get_discovery_list: " + repr(e))

        return []


def collect_data():

    item_params = {}

    try:

        partitions = psutil.disk_partitions(all=False)

        for x in partitions:
            item_params[x.mountpoint] = x.device

    except Exception as e:

        logger.error("set item_params data error: " + repr(e))
        return []

    _dict = {}

    try:

        lines = fsutil.read_file('/tmp/zbx-iostat-data').split('\n')

        for line in lines:
            _line = line.split()
            if not line.startswith('Device') and len(_line) == 14:
                block_device = _line[0]
                _dict[block_device] = _line[1:]

    except Exception as e:

        logger.error("load /tmp/zbx-iostat-data data error: " + repr(e))
        return []

    for k, iostat_values in _dict.items():
        iostat_keys = [
            'rrqm/s',
            'wrqm/s',
            'r/s',
            'w/s',
            'rMB/s',
            'wMB/s',
            'avgrq-sz',
            'avgqu-sz',
            'await',
            'r_await',
            'w_await',
            'svctm',
            '%util',
        ]
        # map value to key
        iostat = dict(zip(iostat_keys, iostat_values))
        _dict[k] = iostat

    try:

        for mountpoint, device in item_params.items():

            if 'mapper' in device:

                _fetch_key = os.readlink(device).split('/')[-1]

            else:

                _fetch_key = device.split('/')[-1]
                # remove digit from string
                _fetch_key = ''.join(
                    [i for i in _fetch_key if not i.isdigit()])

            item_params[mountpoint] = _dict[_fetch_key]

    except Exception as e:

        logger.error("data map failed: " + repr(e))
        return []

    _list = []
    _list.append(item_params)

    logger.info("collect_data: " + repr(_list))

    return _list


if __name__ == "__main__":

    logutil.make_logger(base_dir='/var/log/zabbix', level='INFO')

    parser = argparse.ArgumentParser(description='zbx lld')

    parser.add_argument('cmd', type=str, nargs=1,
                        choices=['discovery', 'report'],
                        help='command to run')

    args = parser.parse_args()

    cmd = args.cmd[0]

    lld_key = 'MYMOUNTPOINT'
    item_key = 'my.vfs.iostat'

    if cmd == 'discovery':

        d = ZabbixDiscovery(lld_key=lld_key, lld_list=get_discovery_list())

        d.dump()

    elif cmd == 'report':

        s = ZabbixSender(item_key=item_key)

        data = collect_data()

        if len(data) == 0:
            print -1
            sys.exit(-1)

        print s.send(data)

        """
            0   # data sent
            -1  # data sent error
        """
