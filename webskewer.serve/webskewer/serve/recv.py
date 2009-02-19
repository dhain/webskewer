import greennet

from webskewer.serve import headers, message
from webskewer.common import http_grammar
from webskewer.common.util import IterFile, DummyFile
from webskewer.common.exceptions import (
    RequestTooLargeError, HeadersTooLargeError, ChunkTooLargeError,
    BadChunkSizeError, BadRequestError, UnimplementedError)


def recv_requests(sock, maxlen=8192):
    while True:
        req = '\r\n'
        while req == '\r\n':
            req = ''.join(
                greennet.recv_until_maxlen(sock, '\r\n', maxlen,
                                           RequestTooLargeError))
        env = message.parse_request(req)
        if env['webskewer.http_version'] > (0,9):
            env.update(recv_headers(sock))
            env['wsgi.input'] = IterFile(recv_entity(sock, env))
        else:
            env['wsgi.input'] = DummyFile()
        yield env


def recv_headers(sock, maxlen=1048576):
    head = ''.join(
        greennet.recv_until_maxlen(sock, '\r\n\r\n', maxlen,
                                   HeadersTooLargeError))
    if head == '\r\n\r\n':
        return {}
    return headers.wsgi_headers(head[:-2])


def recv_entity(sock, env):
    if 'HTTP_TRANSFER_ENCODING' in env:
        if 'CONTENT_LENGTH' in env:
            raise BadRequestError()
        if env['HTTP_TRANSFER_ENCODING'].lower() != 'chunked':
            raise UnimplementedError()
        return recv_chunked(sock)
    else:
        try:
            clen = int(env.get('CONTENT_LENGTH', 0))
        except ValueError:
            raise BadRequestError()
        return greennet.recv_bytes(sock, clen)


def recv_chunked(sock):
    while True:
        chunk_size = '\r\n'
        while chunk_size == '\r\n':
            chunk_size = ''.join(
                greennet.recv_until_maxlen(sock, '\r\n\r\n', 258,
                                           ChunkTooLargeError))
        m = http_grammar.chunk_size.match(chunk_size)
        if not m:
            raise BadChunkSizeError()
        chunk_size = int(chunk_size, 16)
        if chunk_size == 0:
            break
        for data in greennet.recv_bytes(sock, chunk_size):
            yield data
    raise StopIteration(recv_headers(sock))

