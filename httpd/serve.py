from __future__ import with_statement
from contextlib import closing
import socket
import sys

import greennet
from greennet import greenlet

from httpd import message, exceptions
from httpd.log import log_req, log_exc, log_err
from httpd.headers import format_headers
from httpd.recv import recv_requests
from httpd.time_util import now_1123
from httpd.wsgi import ServerError


__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'
__version__ = (0,1)


def handle_connection(sock, app):
    remote_addr, remote_port = sock.getpeername()[:2]
    local_addr, local_port = sock.getsockname()[:2]
    with closing(sock):
        try:
            for env in recv_requests(sock):
                env.update({
                    'REMOTE_ADDR': remote_addr,
                    'REMOTE_PORT': remote_port,
                    'SERVER_ADDR': local_addr,
                    'SERVER_PORT': local_port,
                    'SERVER_NAME': 'localhost',
                    'SCRIPT_NAME': '',
                    'wsgi.version': (1,0),
                    'wsgi.url_scheme': 'http',
                    'wsgi.errors': sys.stderr,
                    'wsgi.multithread': False,
                    'wsgi.multiprocess': False,
                    'wsgi.run_once': False,
                })
                
                headers_set = []
                headers_sent = []
                missing = set(['server', 'date', 'content-length'])
                
                def write(data):
                    if not headers_set:
                        raise AssertionError('write() before start_response()')
                    elif not headers_sent:
                        status, response_headers = headers_sent[:] = headers_set
                        if env['neti.http_version'] > (0,9):
                            out = ['HTTP/1.1 %s\r\n' % (status,)]
                            for header in response_headers:
                                lower = header[0].lower()
                                if lower in missing:
                                    missing.remove(lower)
                                out.append('%s: %s\r\n' % header)
                            out.append('\r\n')
                            if 'content-length' in missing:
                                out[1:1] = ['Transfer-Encoding: chunked\r\n']
                            if 'date' in missing:
                                out[1:1] = ['Date: %s\r\n' % (now_1123(),)]
                            if 'server' in missing:
                                out[1:1] = ['Server: neti/%d.%d\r\n' % __version__]
                            greennet.sendall(sock, ''.join(out))
                    if env['neti.http_version'] > (0,9) and 'content-length' in missing:
                        greennet.sendall(sock, '%x\r\n' % (len(data),))
                    greennet.sendall(sock, data)
                    if env['neti.http_version'] > (0,9) and 'content-length' in missing:
                        greennet.sendall(sock, '\r\n')
                
                def start_response(status, response_headers, exc_info=None):
                    if exc_info:
                        try:
                            if headers_sent:
                                # Re-raise original exception if headers sent
                                raise exc_info[0], exc_info[1], exc_info[2]
                        finally:
                            exc_info = None     # avoid dangling circular ref
                    elif headers_set:
                        raise AssertionError("Headers already set!")
                    headers_set[:] = [status, response_headers]
                    return write
                
                resp = None
                try:
                    resp = app(env, start_response)
                    for data in resp:
                        if data:
                            write(data)
                    if not headers_sent:
                        write('')
                except Exception:
                    print >> sys.stderr, log_exc(remote_addr)
                    if headers_sent:
                        break
                    for data in ServerError(env, start_response):
                        write(data)
                finally:
                    if hasattr(resp, 'close'):
                        resp.close()
                
                if env['neti.http_version'] > (0,9) and 'content-length' in missing:
                    greennet.sendall(sock, '0\r\n\r\n')
                
                print log_req(env, headers_sent)
                
                for _ in env['wsgi.input']:
                    pass
                
                if env['neti.http_version'] < (1,1):
                    break
                connection = env.get('HTTP_CONNECTION', '').lower()
                if connection == 'close':
                    break
        except exceptions.Error, err:
            greennet.sendall(sock, 'HTTP/1.1 400 Bad Request\r\n'
                                   'Server: neti/%d.%d\r\n'
                                   'Date: %s\r\n'
                                   'Content-type: text/html\r\n'
                                   'Content-length: 13\r\n\r\n'
                                   'Bad request\r\n'
                                   % (__version__[0],
                                      __version__[1],
                                      now_1123()))
            print >> sys.stderr, log_err(repr(err), remote_addr)
        except greennet.ConnectionLost:
            pass
        except Exception:
            print >> sys.stderr, log_exc(remote_addr)


def accept_connections(sock, app):
    with closing(sock):
        while True:
            client, addr = greennet.accept(sock)
            greennet.schedule(greenlet(handle_connection), client, app)


def listen(addr):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(addr)
    sock.listen(socket.SOMAXCONN)
    return sock

