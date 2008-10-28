from urlparse import urlsplit

from httpd import grammar, status, headers
from httpd.exceptions import BadVersionError, BadRequestError


__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'


_urlattrs = ('scheme', 'netloc', 'path', 'query', 'fragment')


def entity(headers=None, body=None, clen=None, ctype=None):
    if headers is None:
        headers = {}
    e = {
        'headers': headers
    }
    if body is not None:
        e['body'] = body
    if clen is not None:
        headers['content-length'] = clen
    elif hasattr(body, '__len__'):
        headers['content-length'] = len(body)
    if ctype is not None:
        headers['content-type'] = ctype
    return e


def request(req, headers=None, ent=None):
    if isinstance(req, tuple):
        method, uri, version = req
        if version == (0,9):
            req = method + ' ' + uri + '\r\n'
        else:
            req = '%s %s HTTP/%d.%d\r\n' % ((method, uri) + version)
    else:
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
    
    u = urlsplit(uri)
    r = {
        'request': req,
        'version': version,
        'method': method,
        'uri': uri,
        'splituri': u,
        'headers': {} if headers is None else headers,
        'entity': entity() if ent is None else ent
    }
    for a in _urlattrs:
        r[a] = getattr(u, a)
    
    return r


def format_req(req):
    if req['version'] < (1,0):
        return req['request']
    else:
        return (req['request'] +
                headers.format_headers(req['headers']) +
                headers.format_headers(req['entity']['headers']) +
                '\r\n')


def response(version=(1,1), status=status.OK, headers=None, ent=None):
    r = {
        'version': version,
        'status': status,
        'headers': {} if headers is None else headers,
        'entity': entity() if ent is None else ent
    }
    return r


def Response(req, *a, **kw):
    r = response(*a, **kw)
    try:
        r['headers']['connection'] = req['headers']['connection']
    except KeyError:
        pass
    return r


EmptyEnt = entity(body='', clen=0)

Continue = ('HTTP/1.1 100 Continue\r\n\r\n', True)

ExpectFailed = response(status=status.EXPECTATION_FAILED, ent=EmptyEnt)

ee = ('<html><head><title>%(stc)d %(stm)s</title></head>'
      '<body><h1>%(stc)d %(stm)s</h1><p>%(msg)s</p></body></html>')


def ErrEnt(st, msg, headers=None):
    stc, stm = st
    return entity(headers, ee % locals(), ctype='text/html')


def ErrMsg(req, st, msg):
    return Response(req, status=st, ent=ErrEnt(st, msg))


def ServerError(req):
    st = status.SERVER_ERROR
    r = response(status=st,
                 ent=ErrEnt(st, 'There was an error while handling '
                                'your request. Try again later.'))
    r['headers']['connection'] = 'close'
    return r


def BadRequest(req):
    st = status.BAD_REQUEST
    r = response(status=st,
                 ent=ErrEnt(st, '"' + req.strip() +
                                '" is not a valid request.'))
    r['headers']['connection'] = 'close'
    return r


def NotFound(req):
    st = status.NOT_FOUND
    return Response(req, status=st,
                    ent=ErrEnt(st, req['uri'] + ' was not found.'))


def NotModified(req):
    return Response(req, status=status.NOT_MODIFIED, ent=EmptyEnt)


def NoContent(req):
    return Response(req, status=status.NO_CONTENT, ent=EmptyEnt)


def SeeOther(req, loc):
    st = status.SEE_OTHER
    return Response(req, status=st,
                    ent=ErrEnt(st, 'Please see ' + loc + '.',
                    {'location': loc}))


def MovedPermanently(req, loc):
    st = status.MOVED_PERMANENTLY
    return Response(req, status=st,
                    ent=ErrEnt(st, req['uri'] + ' has moved to ' +
                                   loc + ' permanently.',
                               {'location': loc}))


def Options(req, meths):
    st = status.OK
    m = ', '.join(meths)
    return Response(req, status=st,
                    ent=ErrEnt(st, req['uri'] + ' supports the '
                                   'following methods: ' + m,
                               {'allow': m}))


def MethodNotAllowed(req, meths):
    st = status.METHOD_NOT_ALLOWED
    return Response(req, status=st,
                    ent=ErrEnt(st, req['uri'] + ' does not support ' +
                                   req['method'],
                               {'allow': ', '.join(meths)}))


def RangeNotSatisfiable(req, size):
    st = status.RANGE_NOT_SATISFIABLE
    return Response(req, status=st,
                    ent=ErrEnt(st, 'Requested range not satisfiable',
                               {'content-range': '*/%d' % (size,)}))


def PartialContent(req, ranges, clen=None):
    st = status.PARTIAL_CONTENT
    ent = {}
    if clen is None:
        clen = '*'
    else:
        clen = str(clen)
    if len(ranges) == 1:
        start, end, ent['body'] = ranges[0]
        ent['headers'] = {
            'content-range': 'bytes %d-%d/%s' % (start, end, clen),
            'content-length': end - start,
        }
    else:
        boundary = multipart.make_boundary()
        ent['headers'] = {
            'content-type': 'multipart/byteranges; boundary=' + boundary,
        }
        ent['parts'] = [entity({
            'content-range': 'bytes %d-%d/%s' % (start, end, clen),
        }, body) for start, end, body in ranges]
        ent['body'] = multipart.format_multipart(ent['parts'], boundary)
    return Response(req, status=st, ent=ent)
