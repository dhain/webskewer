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
    """A file-like object that is always empty."""
    
    __slots__ = ('_closed',)
    
    def __init__(self):
        self._closed = False
    
    def __iter__(self):
        return self
    
    def next(self):
        if self._closed:
            raise IOError('read from closed file')
        raise StopIteration()
    
    def read(self, size=None):
        if self._closed:
            raise IOError('read from closed file')
        return ''
    
    def readline(self):
        if self._closed:
            raise IOError('read from closed file')
        return ''
    
    def readlines(self, hint=None):
        if self._closed:
            raise IOError('read from closed file')
        return []
    
    def close(self):
        self._closed = True


class IterFile(object):
    """A file like-object wrapping an iterator that yields strings.
    
    Take an iterable, for example:
    
    >>> def hello_iter():
    ...     yield 'hello '
    ...     yield 'world!'
    ... 
    
    Wrap it in IterFile, and turn it into a file-like object:
    
    >>> file_like = IterFile(hello_iter())
    >>> file_like.read()
    'hello world!'
    """
    
    __slots__ = ('_iter', '_buf')
    
    def __init__(self, it):
        self._iter = iter(it)
        self._buf = ''
    
    def __iter__(self):
        return iter(self.readline, '')
    
    def read(self, size=None):
        if self._iter is None:
            raise IOError('read from closed file')
        while size is None or len(self._buf) < size:
            try:
                self._buf += self._iter.next()
            except StopIteration:
                break
        if size is None:
            data = self._buf
            self._buf = ''
        else:
            data = self._buf[:size]
            self._buf = self._buf[size:]
        return data
    
    def readline(self):
        if self._iter is None:
            raise IOError('read from closed file')
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
        if self._iter is None:
            raise IOError('read from closed file')
        return list(self)
    
    def close(self):
        self._iter = None
        self._buf = None


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


