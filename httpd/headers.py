from httpd import grammar
from httpd.exceptions import BadHeaderError


"""HTTP header helper functions."""

__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'


def format_headers(hs):
    """Format a header dict as a string."""
    return ''.join(h + ': ' + format_value(v) + '\r\n'
                   for h, v in hs.iteritems())


def append_header(headers, name, value):
    """Append a header and value to a header dict.
    
    args:
    headers: the header dictionary to append the header to.
    name: the name of the header to append (eg. 'content-type').
    value: the value of the header to append.
    
    If there is already a header in headers with the same name as the one you
    are trying to append, the resulting value of the header will be a list
    containing all the values so far appended for that name. Examples:
    
    hs = {}
    append_header(hs, 'allow', 'GET')
    # hs == {'allow': 'GET'}
    append_header(hs, 'allow', 'HEAD')
    # hs == {'allow': ['GET', 'HEAD']}
    append_header(hs, 'allow', ['PUT', 'DELETE'])
    # hs == {'allow': ['GET', 'HEAD', 'PUT', 'DELETE']}
    """
    if name in headers:
        v = headers[name]
        if isinstance(v, list):
            if isinstance(value, list):
                v.extend(value)
            else:
                v.append(value)
        else:
            if isinstance(value, list):
                headers[name] = [v] + value
            else:
                headers[name] = [v, value]
    else:
        headers[name] = value


def merge(h1, h2):
    """Merge the items from header dict h2 into h1."""
    for h, v in h2.iteritems():
        append_header(h1, h, v)


_slash_match = lambda m: '\\' + m.group(0)
def qs(s):
    """Turn s into an HTTP quoted-string."""
    s = s.replace('\\', '\\\\')
    return '"' + grammar.nqtext.sub(_slash_match, s) + '"'

def qscx(s):
    """Turn s into an HTTP quoted-string if it is not an HTTP token."""
    return s if grammar.token.match(s) else qs(s)

def qsc(s):
    """Turn s into an HTTP quoted-string if it is not a valid header value."""
    return s if grammar.text.match(s) else qs(s)


_unslash_match = lambda m: m.group(0)[1]
def uqs(s):
    """Turn an HTTP quoted-string into an unquoted string."""
    return grammar.qpair.sub(_unslash_match, s[1:-1])

def uqsc(s):
    """Turn a string into an unquoted string only if it's an HTTP quoted-string."""
    m = grammar.qstring.match(s)
    return uqs(s) if m and m.end() == len(s) else s


def parse_value(v):
    """Parse a header value."""
    v = uqsc(v.strip())
    return int(v) if v.isdigit() else v


def parse_list(v):
    """Parse a comma-separated header value into a list."""
    return [parse_value(m.group(1)) for m in grammar.value_list.finditer(v)]


def format_value(v):
    """Format v as a header value string.
    
    v will be turned into an HTTP quoted-string as necessary.
    """
    if not isinstance(v, basestring):
        try:
            v = ', '.join(qscx(str(vv)) for vv in v)
        except TypeError:
            v = qsc(str(v))
    else:
        v = qsc(v)
    return v


gen_hdrs = set(('cache-control', 'connection', 'date', 'pragma', 'trailer',
    'transfer-encoding', 'upgrade', 'via', 'warning'))

req_hdrs = set((
    'accept', 'accept-charset', 'accept-encoding', 'accept-language',
    'authorization', 'expect', 'from', 'host', 'if-match',
    'if-modified-since', 'if-none-match', 'if-range', 'if-unmodified-since',
    'max-forwards', 'proxy-authorization', 'range', 'referer', 'te',
    'user-agent'
))

resp_hdrs = set((
    'accept-ranges', 'age', 'etag', 'location', 'proxy-authenticate',
    'retry-after', 'server', 'vary', 'www-authenticate'
))

msg_hdrs = gen_hdrs | req_hdrs | resp_hdrs


def parse_headers(s):
    """Parse a string of headers."""
    start = 0
    slen = len(s)
    while start < slen:
        m = grammar.header.match(s, start)
        if m is None:
            raise BadHeaderError(start)
        yield m.groups()
        start = m.end()


def separate(hs):
    """Separate header dict into message and entity header dicts."""
    r = {}
    e = {}
    for h, v in hs.iteritems():
        if h in msg_hdrs:
            r[h] = v
        else:
            e[h] = v
    return r, e


def parse_separate(s):
    """Parse a string of headers into message and entity header dicts."""
    r = {}
    e = {}
    for h, v in parse_headers(s):
        h = h.lower()
        v = parse_value(v)
        if h in msg_hdrs:
            append_header(r, h, v)
        else:
            append_header(e, h, v)
    return r, e
