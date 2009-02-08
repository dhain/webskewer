import re
import sys
import unittest

from webskewer.wsgi.slash import with_slash, without_slash


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


class TestSlash(unittest.TestCase):
    def test_with_slash_pass(self):
        called = []
        
        @with_slash
        def app(environ, start_response):
            called.append(True)
        
        def start_response(status, headers, exc_info=None):
            assert False, 'start_response was called'
        
        app(environ(uri='/hello/'), start_response)
        assert called
    
    def test_add_slash(self):
        uri = '/hello'
        expected_location = '/hello/'
        
        @with_slash
        def app(environ, start_response):
            assert False, 'application was called'
        
        called = []
        
        def start_response(status, headers, exc_info=None):
            called.append(True)
            assert exc_info is None
            assert status.startswith('301 ')
            for name, value in headers:
                if name.lower() == 'location':
                    assert value == expected_location
                    break
            else:
                assert False, 'location header not present'
        
        app(environ(uri=uri), start_response)
        assert called
    
    def test_add_slash_with_query(self):
        uri = '/hello'
        query = 'world=true'
        expected_location = '/hello/?world=true'
        
        @with_slash
        def app(environ, start_response):
            assert False, 'application was called'
        
        called = []
        
        def start_response(status, headers, exc_info=None):
            called.append(True)
            assert exc_info is None
            assert status.startswith('301 ')
            for name, value in headers:
                if name.lower() == 'location':
                    assert value == expected_location
                    break
            else:
                assert False, 'location header not present'
        
        app(environ(uri=uri, query=query), start_response)
        assert called
    
    def test_without_slash_pass(self):
        called = []
        
        @without_slash
        def app(environ, start_response):
            called.append(True)
        
        def start_response(status, headers, exc_info=None):
            assert False, 'start_response was called'
        
        app(environ(uri='/hello'), start_response)
        assert called
    
    def test_remove_slash(self):
        uri = '/hello/'
        expected_location = '/hello'
        
        @without_slash
        def app(environ, start_response):
            assert False, 'application was called'
        
        called = []
        
        def start_response(status, headers, exc_info=None):
            called.append(True)
            assert exc_info is None
            assert status.startswith('301 ')
            for name, value in headers:
                if name.lower() == 'location':
                    assert value == expected_location
                    break
            else:
                assert False, 'location header not present'
        
        app(environ(uri=uri), start_response)
        assert called
    
    def test_remove_slash_with_query(self):
        uri = '/hello/'
        query = 'world=true'
        expected_location = '/hello?world=true'
        
        @without_slash
        def app(environ, start_response):
            assert False, 'application was called'
        
        called = []
        
        def start_response(status, headers, exc_info=None):
            called.append(True)
            assert exc_info is None
            assert status.startswith('301 ')
            for name, value in headers:
                if name.lower() == 'location':
                    assert value == expected_location
                    break
            else:
                assert False, 'location header not present'
        
        app(environ(uri=uri, query=query), start_response)
        assert called
    
    def test_without_slash_root(self):
        called = []
        
        @without_slash
        def app(environ, start_response):
            called.append(True)
        
        def start_response(status, headers, exc_info=None):
            assert False, 'start_response was called'
        
        app(environ(), start_response)
        assert called
    
    def test_without_slash_root_query(self):
        called = []
        
        @without_slash
        def app(environ, start_response):
            called.append(True)
        
        def start_response(status, headers, exc_info=None):
            assert False, 'start_response was called'
        
        app(environ(query='world=true'), start_response)
        assert called



if __name__ == '__main__':
    unittest.main()
