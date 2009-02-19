import re
from sys import modules
from os.path import getmtime
from urllib import unquote_plus
from urlparse import urlunsplit


__all__ = ['fprop', 'decodeurl', 'DummyFile', 'IterFile', 'reloading']


def fprop(func):
    return property(**func())


def decodeurl(url):
    """Unquote and decode (utf-8) a url."""
    return unquote_plus(url).decode('utf-8')


class DummyFile(object):
    __slots__ = ()
    
    def __iter__(self):
        return self
    
    def next(self):
        raise StopIteration()
    
    def read(self, size=None):
        return ''
    
    def readline(self):
        return ''
    
    def readlines(self, hint=None):
        return []


class IterFile(object):
    __slots__ = ('_iter', '_buf')
    
    def __init__(self, it):
        self._iter = iter(it)
        self._buf = ''
    
    def __iter__(self):
        return iter(self.readline, '')
    
    def read(self, size=None):
        while size is None or len(self._buf) < size:
            try:
                self._buf += self._iter.next()
            except StopIteration:
                break
        data = self._buf[:size]
        self._buf = self._buf[size:]
        return data
    
    def readline(self):
        i = -1
        start = 0
        while i < 0:
            i = self._buf.find('\n', start)
            start = len(self._buf)
            try:
                self._buf += self._iter.next()
            except StopIteration:
                break
        if i < 0:
            data = self._buf
            self._buf = ''
            return data
        i += 1
        data = self._buf[:i]
        self._buf = self._buf[i:]
        return data
    
    def readlines(self, hint=None):
        return list(self)


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

