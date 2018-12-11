#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys

from pykit import fsutil
from pykit import logutil
from zabbixdiscovery import ZabbixDiscovery
from zabbixsender import ZabbixSender

logger = logging.getLogger(__name__)

SYS_CLASS_NET = '/sys/class/net'


def get_discovery_list():

    return get_alive_device(SYS_CLASS_NET)


def get_alive_device(device_dir):

    devices = os.listdir(device_dir)
    devices = [device for device in devices
               if os.path.isdir(os.path.join(device_dir, device))]

    alive_devices = []

    try:

        for device in devices:

            path = os.path.join(device_dir, device, 'operstate')
            status = fsutil.read_file(path).strip().split('\n')[0]

            if "up" == status:
                alive_devices.append(device)

    except Exception as e:

        logger.error("while get_discovery_list: " + repr(e))
        return []

    return alive_devices


def get_device_stats(device_dir, devices, statistics, other):

    _dict = {}

    for device in devices:
        if not _dict.get(device):
            _dict[device] = {}

        for metric in statistics:
            path = os.path.join(device_dir, device, 'statistics', metric)

            try:
                _dict[device][metric] = fsutil.read_file(
                    path).strip().split('\n')[0]

            except Exception as e:
                logger.error("while get_device_stats: " + repr(e))
                return {}

        for x in other:
            path = os.path.join(device_dir, device, x)

            try:
                _dict[device][x] = fsutil.read_file(
                    path).strip().split('\n')[0]

            except Exception as e:
                logger.error("while get_device_stats: " + repr(e))
                return {}

    return _dict


def collect_data():

    alive_devices = get_alive_device(SYS_CLASS_NET)

    statistics = ['tx_errors', 'rx_errors',
                  'tx_dropped', 'rx_dropped',
                  'rx_missed_errors',
                  ]
    other = ['speed']

    _list = []
    _list.append(get_device_stats(SYS_CLASS_NET, alive_devices, statistics, other))

    return _list


if __name__ == '__main__':

    logutil.make_logger(base_dir='/var/log/zabbix', level='INFO')

    parser = argparse.ArgumentParser(description='zbx lld')

    parser.add_argument('cmd', type=str, nargs=1,
                        choices=['discovery', 'report'],
                        help='command to run')

    args = parser.parse_args()

    cmd = args.cmd[0]

    lld_key = 'ETHNAME'
    item_key = 'net.device.stats'

    if cmd == 'discovery':

        d = ZabbixDiscovery(lld_key=lld_key, lld_list=get_discovery_list())

        d.dump()

    elif cmd == 'report':

        s = ZabbixSender(item_key=item_key)

        data = collect_data()

        print s.send(data)
        """
            0   # data sent
            -1  # data sent error
        """
