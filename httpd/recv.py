import greennet

from httpd import grammar, headers, message
from httpd.exceptions import RequestTooLargeError, HeadersTooLargeError, \
                            ChunkTooLargeError, BadChunkSizeError, \
                            BadRequestError, UnimplementedError


__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'


def recv_requests(sock, maxlen=8192):
    while True:
        req = '\r\n'
        while req == '\r\n':
            req = ''.join(
                greennet.recv_until_maxlen(sock, '\r\n', maxlen,
                                           RequestTooLargeError))
        req = message.request(req)
        if req['version'] > (0,9):
            req['headers'], req['entity']['headers'] = recv_headers(sock)
            req['entity']['body'] = recv_entity(sock, req)
        yield req


def recv_headers(sock, maxlen=1048576):
    head = ''.join(
        greennet.recv_until_maxlen(sock, '\r\n\r\n', maxlen,
                                   HeadersTooLargeError))
    if head == '\r\n\r\n':
        return ({}, {})
    return headers.parse_separate(head[:-2])


def recv_entity(sock, req):
    if 'transfer-encoding' in req['headers']:
        if 'content-length' in req['entity']['headers']:
            raise BadRequestError()
        if req['headers']['transfer-encoding'].lower() != 'chunked':
            raise UnimplementedError()
        return recv_chunked(sock)
    else:
        try:
            clen = int(req['entity']['headers'].get('content-length', 0))
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
        m = grammar.chunk_size.match(chunk_size)
        if not m:
            raise BadChunkSizeError()
        chunk_size = int(chunk_size, 16)
        if chunk_size == 0:
            break
        for data in greennet.recv_bytes(sock, chunk_size):
            yield data
    raise StopIteration(recv_headers(sock)[1])

