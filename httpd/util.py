import re
from sys import modules
from os.path import getmtime
from urllib import unquote_plus
from urlparse import urlunsplit

from httpd import message


"""http helper utilites."""

__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'


__all__ = []


def normurl(req, slash):
    """Check a request's path for trailing slashes.
    
    If the slash argument is True, and the request's path does not have a
    trailing slash, return a MovedPermanently response to the same path, with
    a trailing slash. If slash is True and the request's path does have a
    trailing slash, return None. Vice-versa if the slash argument is False.
    """
    p = req['path']
    if slash:
        if not p.endswith('/'):
            p += '/'
    else:
        p = p.rstrip('/')
    if req['path'] != p:
        parts = list(req['splituri'])
        parts[2] = p
        return message.MovedPermanently(req, urlunsplit(parts))

__all__.append('normurl')


def decodeurl(url):
    """Unquote and decode (utf-8) a url."""
    return unquote_plus(url).decode('utf-8')

__all__.append('decodeurl')


def reloading(f):
    """Decorator that reloads containing module of decorated function."""
    m = modules[f.__module__]
    fn = m.__file__
    if fn.endswith('.pyc'):
        fn = fn[:-1]
    m.__mtime__ = getmtime(fn)
    f = [f, f.__name__]
    
    def wrapped(*args, **kw):
        mt = getmtime(fn)
        if mt > m.__mtime__:
            reload(m)
            m.__mtime__ = mt
            f[0] = getattr(m, f[1])
            wrapped.__doc__ = f[0].__doc__
        return f[0](*args, **kw)
    
    wrapped.__name__ = f[1]
    wrapped.__doc__ = f.__doc__
    return wrapped

__all__.append('reloading')


