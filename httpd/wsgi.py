import sys

from httpd import status


__all__ = ['BadRequest', 'ServerError', 'HelloWorld']


ee = ('<html><head><title>%(stc)d %(stm)s</title></head>'
      '<body><h1>%(stc)d %(stm)s</h1><p>%(msg)s</p></body></html>\r\n')


def BadRequest(environ, start_response):
    msg = 'Bad request.'
    stc, stm = st = status.BAD_REQUEST
    message = ee % locals()
    start_response('%d %s' % st,
                   [('Content-type', 'text/html'),
                    ('Content-length', str(len(message)))])
    return [message]


def ServerError(environ, start_response):
    msg = 'An internal server error has occurred. Please try again later.'
    exc_info = sys.exc_info()
    if exc_info == (None, None, None):
        exc_info = ()
    else:
        exc_info = (exc_info,)
    stc, stm = st = status.SERVER_ERROR
    message = ee % locals()
    start_response('%d %s' % st,
                   [('Content-type', 'text/html'),
                    ('Content-length', str(len(message)))],
                   *exc_info)
    exc_info = None
    return [message]


def NotFound(environ, start_response):
    msg = 'Not found.'
    stc, stm = st = status.NOT_FOUND
    message = ee % locals()
    start_response('%d %s' % st,
                   [('Content-type', 'text/html'),
                    ('Content-length', str(len(message)))])
    return [message]


def NotModified(environ, start_response):
    msg = 'Not modified.'
    stc, stm = st = status.NOT_MODIFIED
    message = ee % locals()
    start_response('%d %s' % st,
                   [('Content-type', 'text/html'),
                    ('Content-length', str(len(message)))])
    return [message]


def MovedPermanently(location):
    def MovedPermanently(environ, start_response):
        msg = ('The requested resource has moved to '
               '<a href="%(location)s">%(location)s</a>.' % locals())
        stc, stm = st = status.MOVED_PERMANENTLY
        message = ee % locals()
        start_response('%d %s' % st,
                       [('Location', location),
                        ('Content-type', 'text/html'),
                        ('Content-length', str(len(message)))])
        return [message]
    return MovedPermanently


def RangeNotSatisfiable(size):
    def RangeNotSatisfiable(environ, start_response):
        msg = 'Requested range not satisfiable.'
        stc, stm = st = status.RANGE_NOT_SATISFIABLE
        message = ee % locals()
        start_response('%d %s' % st,
                       [('Content-range', '*/%d' % (size,)),
                        ('Content-type', 'text/html'),
                        ('Content-length', str(len(message)))])
        return [message]
    return RangeNotSatisfiable


def HelloWorld(environ, start_response):
    msg = 'Hello World!'
    stc, stm = st = status.OK
    message = ee % locals()
    start_response('%d %s' % st,
                   [('Content-type', 'text/html'),
                    ('Content-length', str(len(message)))])
    return [message]


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
