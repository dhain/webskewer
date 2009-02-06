
ee = ('<html><head><title>%(status)s</title></head>'
      '<body><h1>%(status)s</h1><p>%(msg)s</p></body></html>\r\n')


def Simple(message, status='200 OK', headers=(), ctype='text/html', exc_info=()):
    def app(environ, start_response):
        msg = message
        body = ee % locals()
        start_response(status,
                       [('Content-type', ctype),
                        ('Content-length', str(len(body)))] + list(headers),
                       *exc_info)
        return [body]
    return app


def BadRequest():
    return Simple('Bad request.', '400 Bad Request')


def ServerError():
    return Simple('An internal server error has occurred. '
                  'Please try again later.',
                  '500 Internal Server Error', exc_info=sys.exc_info())


def NotFound():
    return Simple('Not found.', '404 Not Found')


def NotModified():
    return Simple('Not modified.', '304 Not Modified')


def MovedPermanently(location):
    return Simple('The requested resource has moved to '
                  '<a href="%(location)s">%(location)s</a>.' % locals(),
                  '301 Moved Permanently',
                  [('Location', location)])


def RangeNotSatisfiable(size):
   return Simple('Requested range not satisfiable.',
                 '416 Requested Range Not Satisfiable',
                 [('Content-range', '*/%d' % (size,))])


def HelloWorld():
    return Simple('Hello World!', ctype='text/plain')


def Options(methods):
    methods = ', '.join(methods)
    return Simple('The requested resource supports the following methods: ' +
                  methods, headers=[('Allow', methods)])


def MethodNotAllowed(methods):
    return Simple('Method not allowed.',
                  '405 Method Not Allowed',
                  [('Allow', ', '.join(methods))])
