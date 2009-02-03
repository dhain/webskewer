from __future__ import with_statement
from contextlib import closing
import socket
import sys

import greennet
from greennet import greenlet

from httpd import message, exceptions, wsgi
from httpd.log import log_req, log_exc, log_err
from httpd.recv import recv_requests
from httpd.time_util import now_1123
from httpd.util import DummyFile


__version__ = (0,1)


class RequestHandler(object):
    __slots__ = ('sock', 'application', 'environ', 'status',
                 'headers', 'headers_sent', 'chunked', 'bytes_sent')
    
    def __init__(self, sock, application, environ):
        self.sock = sock
        self.application = application
        self.environ = environ
        self.status = None
        self.headers = None
        self.headers_sent = False
        self.chunked = False
        self.bytes_sent = 0
    
    def handle(self):
        resp = None
        try:
            resp = self.application(self.environ, self.start_response)
            for data in resp:
                if data:
                    self.write(data)
            if not self.headers_sent:
                self._write_headers()
        except Exception:
            print >> sys.stderr, log_exc(self.environ['REMOTE_ADDR'])
            if self.headers_sent:
                return True # signal caller to close connection
            self.application = wsgi.ServerError
            return self.handle()
        finally:
            if hasattr(resp, 'close'):
                resp.close()
        if self.chunked:
            greennet.sendall(self.sock, '0\r\n\r\n')
        print log_req(self.environ, self.status, self.headers, self.bytes_sent)
        for _ in self.environ['wsgi.input']:
            pass
    
    def _write_headers(self):
        self.headers_sent = True
        if self.environ['neti.http_version'] > (0,9):
            missing = set(['server', 'date', 'content-length'])
            headers = []
            for header in self.headers:
                lower = header[0].lower()
                if lower in missing:
                    missing.remove(lower)
                headers.append('%s: %s\r\n' % header)
            add_headers = []
            if 'content-length' in missing:
                if self.environ['neti.http_version'] > (1,0):
                    add_headers.append('Transfer-Encoding: chunked\r\n')
                    self.chunked = True
                else:
                    self.environ['HTTP_CONNECTION'] = 'close'
            if 'date' in missing:
                add_headers.append('Date: %s\r\n' % (now_1123(),))
            if 'server' in missing:
                add_headers.append('Server: neti/%d.%d\r\n' % __version__)
            out = ''.join(['HTTP/1.1 %s\r\n' % (self.status,)] +
                          add_headers + headers + ['\r\n'])
            greennet.sendall(self.sock, out)
    
    def write(self, data):
        if self.headers is None:
            raise AssertionError('write() before start_response()')
        elif not self.headers_sent:
            self._write_headers()
        self.bytes_sent += len(data)
        if self.chunked:
            data = '%x\r\n' % (len(data),) + data + '\r\n'
        greennet.sendall(self.sock, data)
    
    def start_response(self, status, headers, exc_info=None):
        if exc_info:
            try:
                if self.headers_sent:
                    # Re-raise original exception if headers sent
                    raise exc_info[0], exc_info[1], exc_info[2]
            finally:
                exc_info = None     # avoid dangling circular ref
        elif self.headers is not None:
            raise AssertionError("start_response() already called")
        self.status = status
        self.headers = headers
        return self.write


def handle_connection(sock, application):
    remote_addr, remote_port = sock.getpeername()[:2]
    local_addr, local_port = sock.getsockname()[:2]
    server_env = {
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
    }
    with closing(sock):
        try:
            for environ in recv_requests(sock):
                environ.update(server_env)
                handler = RequestHandler(sock, application, environ)
                if handler.handle():
                    break
                connection = environ.get('HTTP_CONNECTION', '').lower()
                if environ['neti.http_version'] < (1,1):
                    break
                if connection == 'close':
                    break
        except exceptions.Error, err:
            environ = {
                'wsgi.input': DummyFile(),
                'neti.http_version': (1,1)
            }
            environ.update(server_env)
            handler = RequestHandler(sock, wsgi.BadRequest, environ)
            handler.handle()
            print >> sys.stderr, log_err(repr(err), remote_addr)
        except greennet.ConnectionLost:
            pass
        except Exception:
            print >> sys.stderr, log_exc(remote_addr)


def accept_connections(sock, application):
    with closing(sock):
        while True:
            client, addr = greennet.accept(sock)
            greennet.schedule(greenlet(handle_connection), client, application)


def listen(addr):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(addr)
    sock.listen(socket.SOMAXCONN)
    return sock

