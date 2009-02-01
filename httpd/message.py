import urllib
from urlparse import urlsplit

from httpd import grammar
from httpd.exceptions import BadVersionError, BadRequestError


__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'


def parse_request(req):
    for r in (grammar.req1x, grammar.req09):
        m = r.match(req)
        if m is None:
            continue
        if r is grammar.req1x:
            method, uri, ver_maj, ver_min = m.groups()
            version = (int(ver_maj), int(ver_min))
        else:
            method = 'GET'
            uri = m.group(1)
            version = (0,9)
        break
    else:
        raise BadRequestError(req)
    if version < (0,9):
        raise BadVersionError(version)
    if version == (0,9) and method != 'GET':
        raise BadRequestError(req)
    splituri = urlsplit(uri)
    return {
        'REQUEST_METHOD': method,
        'PATH_INFO': urllib.unquote(splituri.path),
        'QUERY_STRING': splituri.query,
        'SERVER_PROTOCOL': 'HTTP/%d.%d' % version,
        'neti.http_request': req,
        'neti.http_uri': uri,
        'neti.http_version': version,
        'neti.split_uri': splituri,
    }
