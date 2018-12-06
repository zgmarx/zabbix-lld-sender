#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import pwd

from pykit import dictutil
from pykit import fsutil
from pykit import proc

logger = logging.getLogger(__name__)


class ZabbixSender(object):

    def __init__(self, **ctx):

        self.item_key = ctx.get('item_key')
        user = ctx.get('user', 'zabbix')
        group = ctx.get('group', 'zabbix')

        self.data_file_dir = ctx.get('dir', '/dev/shm/zabbix')
        self.data_file = '/'.join([self.data_file_dir, self.item_key])

        self.uid = pwd.getpwnam(user).pw_uid
        self.gid = pwd.getpwnam(group).pw_gid

        self.sender = '/bin/zabbix_sender'
        self.agent_configfile = '/etc/zabbix/zabbix_agentd.conf'

    def construct(self, data, depth=16):
        """
        data is a list of dicts or dict.
        if depth is larger than 16, set it as your need.
        """

        rst = []

        def gen_keys(data):

            _rst = []

            for keys, value in dictutil.depth_iter(data, maxdepth=depth):

                if len(keys) == 1:
                    item_params = keys[0]
                else:
                    item_params = ','.join(keys)

                item_value = value

                m = "{0} {1}[{2}] {3}".format(
                    '-', self.item_key, item_params, item_value)
                _rst.append(m)

            return _rst

        if isinstance(data, dict) and len(data) != 0:

            rst = gen_keys(data)

        elif isinstance(data, list):
            for _data in data:
                rst = rst + gen_keys(_data)
        else:

            logger.err('unspport construct:' + repr(type(data)))

        return rst

    def save_to_file(self, data):

        try:

            if not os.path.exists(self.data_file_dir):
                fsutil.makedirs(self.data_file_dir)

        except Exception as e:

            logger.error("mkdir: " + self.data_file_dir + " " + repr(e))
            return -1  # data sent error

        try:
            content = "\n".join(data)
            fsutil.write_file(self.data_file, content, self.uid, self.gid)

        except Exception as e:

            logger.error("write data to " + self.data_file + " " + repr(e))

            return -1  # data sent error

    def send(self, data):

        data = self.construct(data)

        self.save_to_file(data)

        returncode, out, err = proc.command(self.sender,
                                            '-c', self.agent_configfile,
                                            '-i', self.data_file)
        logger.info(out)

        if returncode == 0:

            return 0  # data sent

        else:

            logger.error("while send data to remote zabbix: " + repr(err))
            return -1  # data sent error
