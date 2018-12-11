#!/usr/bin/env python2.7
# coding: utf-8

import logging
import socket
import ssl
import sys
import urllib

from pykit import http
from pykit import logutil


logger = logging.getLogger(__name__)


def split_url(url):

    proto, rest = urllib.splittype(url)
    host, uri = urllib.splithost(rest)
    domain, port = urllib.splitport(host)

    if port is None:
        if proto == 'http':
            port = 80
        elif proto == 'https':
            port = 443
        else:
            logger.warn("Support 'http' or 'https' currently.")
            raise

    if uri == '':
        uri = '/'

    return proto, domain, int(port), uri


def visit_url(url, method):

    proto, domain, port, uri = split_url(url)

    # prepare for a request
    if proto == 'http':
        cli = http.Client(domain, port, timeout=20)

    if proto == 'https':
        context = ssl._create_unverified_context()
        cli = http.Client(domain, port, https_context=context, timeout=20)

    # send a request
    cli.request(uri, method=method, headers={})

    # deal with response
    try:
        response_code = cli.status
        cli.request('/')
        reponse_msg = cli.headers
    except (socket.timeout, ssl.SSLError) as e:
        logger.warn(
            'Socket timeout, ' + 'While access the {url}'.format(url=url))
        return -1
    except Exception as e:
        logger.exception(repr(e) + ' While access the {url}'.format(url=url))
        return -1

    return response_code, reponse_msg


if __name__ == '__main__':

    logutil.make_logger(base_dir='/var/log/zabbix', level='INFO')

    url = sys.argv[1]
    method = sys.argv[2]
    expect_response_code = sys.argv[3]

    response = visit_url(url, method)

    if isinstance(response, tuple):
        response_code, msg = response
        if response_code == int(expect_response_code):
            print 0
        else:
            print -1
    else:
        print -1

        '''
         0  # url response ok
        -1  # url response with error
        '''
