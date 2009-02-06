import re
import sys
import unittest

from webskewer.wsgi.route import router


def environ(method='GET', uri='/', headers=None, query=''):
    environ = {
        'REQUEST_METHOD': method,
        'SCRIPT_NAME': '',
        'PATH_INFO': uri,
        'QUERY_STRING': query,
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1,0),
        'wsgi.url_scheme': 'http',
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    if headers:
        environ.update(headers)
    return environ


class TestRouter(unittest.TestCase):
    def test_empty(self):
        def start_response(status, headers, exc_info=None):
            assert exc_info is None
            assert status.startswith('404 '), repr(status)
        
        router()(environ(), start_response)
    
    def test_options(self):
        def test_options_with_methods(methods):
            def start_response(status, headers, exc_info=None):
                assert exc_info is None
                assert status.startswith('200 '), repr(status)
                for name, value in headers:
                    if name.lower() == 'allow':
                        if methods:
                            assert set(m.strip() for m in value.split(',')) == set(methods), repr(value)
                        else:
                            assert value == '', repr(value)
                        break
                else:
                    assert False, 'allow header not present'
            
            def app(environ, start_response):
                assert False, 'application was called'
            
            router([
                (re.compile(r'/'), methods, app)
            ])(environ('OPTIONS'), start_response)
        
        for methods in [
                [],
                ['GET'],
                ['GET', 'HEAD'],
                ['GET', 'HEAD', 'POST'],
                ['DELETE']]:
            try:
                test_options_with_methods(methods)
            except AssertionError, err:
                err.args = (methods,) + err.args
                raise
    
    def test_options_with_options(self):
        called = []
        
        def app(environ, start_response):
            called.append(True)
        
        def start_response(status, headers, exc_info=None):
            assert False, 'start_response was called'
        
        router([
            (re.compile(r'/'), ['OPTIONS'], app)
        ])(environ('OPTIONS'), start_response)
        
        assert called
    
    def test_options_star(self):
        def app(environ, start_response):
            assert False, 'application was called'
        
        def start_response(status, headers, exc_info=None):
            assert exc_info is None
            assert status.startswith('200 '), repr(status)
        
        router([
            (re.compile(r'/'), ['GET'], app)
        ])(environ('OPTIONS', '*'), start_response)
    
    def test_get(self):
        called = []
        
        def app(environ, start_response):
            called.append(True)
        
        def start_response(status, headers, exc_info=None):
            assert False, 'start_response was called'
        
        router([
            (re.compile(r'/'), ['GET'], app)
        ])(environ(), start_response)
        
        assert called
    
    def test_script_name(self):
        called = []
        
        def app(environ, start_response):
            called.append(True)
            assert environ['SCRIPT_NAME'] == '/something', repr(environ['SCRIPT_NAME'])
            assert environ['PATH_INFO'] == '/else', repr(environ['PATH_INFO'])
        
        def start_response(status, headers, exc_info=None):
            assert False, 'start_response was called'
        
        router([
            (re.compile(r'/something'), ['GET'], app)
        ])(environ(uri='/something/else'), start_response)
        
        assert called
    
    def test_multiple(self):
        called = []
        
        def app(environ, start_response):
            called.append(True)
        
        def start_response(status, headers, exc_info=None):
            assert False, 'start_response was called'
        
        router([
            (re.compile(r'/'), ['GET'], app),
            (re.compile(r'/something'), ['GET'], app)
        ])(environ(uri='/something'), start_response)
        
        assert called
    
    def test_method_not_allowed(self):
        methods = ['GET', 'HEAD']
        
        def start_response(status, headers, exc_info=None):
            assert exc_info is None
            assert status.startswith('405 '), repr(status)
            for name, value in headers:
                if name.lower() == 'allow':
                    if methods:
                        assert set(m.strip() for m in value.split(',')) == set(methods), repr(value)
                    else:
                        assert value == '', repr(value)
                    break
            else:
                assert False, 'allow header not present'
        
        def app(environ, start_response):
            assert False, 'application was called'
        
        router([
            (re.compile(r'/'), methods, app)
        ])(environ('POST'), start_response)
    
    def test_404(self):
        def start_response(status, headers, exc_info=None):
            assert exc_info is None
            assert status.startswith('404 '), repr(status)
        
        def app(environ, start_response):
            assert False, 'application was called'
        
        router([
            (re.compile(r'/something'), ['GET', 'HEAD'], app)
        ])(environ(), start_response)


if __name__ == '__main__':
    unittest.main()
