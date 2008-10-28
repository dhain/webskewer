import random

from httpd import headers


__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__version__ = '2.0a'


make_boundary = lambda: 'neti' + (
    ''.join(random.choice('abcdef1234567890') for _ in xrange(24)))


def format_multipart(parts, boundary):
    yield '--' + boundary
    for part in parts:
        yield '\r\n' + headers.format_headers(part.get('headers', {})) + '\r\n'
        for data in part['body']:
            yield data
        yield '\r\n--' + boundary
    yield '--\r\n\r\n'

