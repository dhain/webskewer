import sys

from webskewer.common import http_status


__all__ = ['BadRequest', 'ServerError', 'HelloWorld']


ee = ('<html><head><title>%(status)s</title></head>'
      '<body><h1>%(status)s</h1><p>%(msg)s</p></body></html>\r\n')


def Simple(message, status=http_status.OK,
           headers=(), ctype='text/html', exc_info=()):
    def app(environ, start_response):
        msg = message
        body = ee % locals()
        start_response(status,
                       [('Content-type', ctype),
                        ('Content-length', str(len(body)))] + list(headers),
                       exc_info)
        return [body]
    return app


def BadRequest():
    return Simple('Bad request.', http_status.BAD_REQUEST)


def ServerError():
    return Simple('An internal server error has occurred. '
                  'Please try again later.',
                  http_status.SERVER_ERROR, exc_info=sys.exc_info())


def NotFound():
    return Simple('Not found.', http_status.NOT_FOUND)


def NotModified():
    return Simple('Not modified.', http_status.NOT_MODIFIED)


def MovedPermanently(location):
    return Simple('The requested resource has moved to '
                  '<a href="%(location)s">%(location)s</a>.' % locals(),
                  http_status.MOVED_PERMANENTLY,
                  [('Location', location)])


def SeeOther(location):
    return Simple('The requested resource was found at '
                  '<a href="%(location)s">%(location)s</a>.' % locals(),
                  http_status.SEE_OTHER,
                  [('Location', location)])


def RangeNotSatisfiable(size):
   return Simple('Requested range not satisfiable.',
                 http_status.RANGE_NOT_SATISFIABLE,
                 [('Content-range', '*/%d' % (size,))])


def HelloWorld():
    return Simple('Hello World!', ctype='text/plain')


def Options(methods):
    methods = ', '.join(methods)
    return Simple('The requested resource supports the following methods: ' +
                  methods, headers=[('Allow', methods)])


def MethodNotAllowed(methods):
    return Simple('Method not allowed.',
                  http_status.METHOD_NOT_ALLOWED,
                  [('Allow', ', '.join(methods))])


def PartialContent(req, ranges, clen=None):
    st = http_status.PARTIAL_CONTENT
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
