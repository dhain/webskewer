from webskewer.wsgi.http import MovedPermanently


class with_slash(object):
    def __init__(self, application):
        self.application = application
    
    def __call__(self, environ, start_response):
        path = environ.get('SCRIPT_NAME', '') + environ.get('PATH_INFO', '')
        if path.endswith('/'):
            return self.application(environ, start_response)
        location = path + '/'
        if environ.get('QUERY_STRING'):
            location += '?' + environ['QUERY_STRING']
        return MovedPermanently(location)(environ, start_response)


class without_slash(object):
    def __init__(self, application):
        self.application = application
    
    def __call__(self, environ, start_response):
        path = environ.get('SCRIPT_NAME', '') + environ.get('PATH_INFO', '')
        if not path.endswith('/'):
            return self.application(environ, start_response)
        location = path.rstrip('/')
        if environ.get('QUERY_STRING'):
            location += '?' + environ['QUERY_STRING']
        return MovedPermanently(location)(environ, start_response)
