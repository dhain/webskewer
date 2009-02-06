from webskewer.wsgi.http import NotFound, Options, MethodNotAllowed, Simple


class router(object):
    def __init__(self, routes=()):
        self.routes = routes
    
    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'OPTIONS' and environ['PATH_INFO'] == '*':
            return Simple('Hello, world')(environ, start_response)
        for rx, methods, application in self.routes:
            m = rx.match(environ['PATH_INFO'])
            if m is None:
                continue
            if environ['REQUEST_METHOD'] not in methods:
                if environ['REQUEST_METHOD'] == 'OPTIONS':
                    return Options(methods)(environ, start_response)
                return MethodNotAllowed(methods)(environ, start_response)
            environ['SCRIPT_NAME'] += m.group(0)
            environ['PATH_INFO'] = environ['PATH_INFO'][m.end():]
            environ['webskewer.route.args'] = m.groups()
            environ['webskewer.route.kwargs'] = m.groupdict()
            return application(environ, start_response)
        else:
            return NotFound()(environ, start_response)
