from __future__ import with_statement
from contextlib import closing
import socket
import sys

import greennet
from greennet import greenlet
from greennet.queue import Queue

from httpd import message
from httpd.log import log_req, log_exc
from httpd.headers import format_headers
from httpd.recv import recv_requests
from httpd.time_util import now_1123


__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'


def send_responses(sock, response_queue):
    while True:
        req, resp = response_queue.popleft()
        if resp is None:
            break
        try:
            if req['version'] > (0,9):
                preamble = ('HTTP/%d.%d ' % resp['version'] +
                            '%d %s\r\n' % resp['status'] +
                            format_headers(resp['headers']) +
                            format_headers(resp['entity']['headers']) +
                            '\r\n')
                greennet.sendall(sock, preamble)
            if req['method'] != 'HEAD' and 'body' in resp['entity']:
                if isinstance(resp['entity']['body'], basestring):
                    greennet.sendall(sock, resp['entity']['body'])
                else:
                    for data in resp['entity']['body']:
                        greennet.sendall(sock, data)
        except Exception:
            response_queue.clear()
            break


def handle_connection(sock, handler):
    response_queue = Queue()
    greennet.schedule(greenlet(send_responses), sock, response_queue)
    remote_addr, remote_port = sock.getpeername()[:2]
    with closing(sock):
        try:
            for req in recv_requests(sock):
                req['remote_addr'] = remote_addr
                req['remote_port'] = remote_port
                try:
                    resp = handler(req)
                except Exception:
                    print >> sys.stderr, log_exc(remote_addr)
                    resp = message.ServerError(req)
                else:
                    print log_req(req, resp)
                response_queue.append((req, resp))
                if 'body' in req['entity']:
                    for _ in req['entity']['body']:
                        pass
                if req['version'] < (1,1):
                    break
                connection = req['headers'].get('connection', '').lower()
                if connection == 'close':
                    break
        except greennet.ConnectionLost:
            pass
        except Exception:
            pass
        response_queue.append((None, None))
        response_queue.wait_until_empty()


def accept_connections(sock, handler):
    with closing(sock):
        while True:
            client, addr = greennet.accept(sock)
            greennet.schedule(greenlet(handle_connection), client, handler)


def listen(addr):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(addr)
    sock.listen(socket.SOMAXCONN)
    return sock

