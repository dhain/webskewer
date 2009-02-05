import urllib
from urlparse import urlsplit

from webskewer.http import grammar
from webskewer.http.exceptions import BadVersionError, BadRequestError


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
        'webskewer.http_request': req,
        'webskewer.http_uri': uri,
        'webskewer.http_version': version,
        'webskewer.split_uri': splituri,
    }
