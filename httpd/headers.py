from httpd import grammar
from httpd.exceptions import BadHeaderError


"""HTTP header helper functions."""

__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'


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


def wsgi_headers(headers):
    env = {}
    for h, v in parse_headers(headers):
        k = 'HTTP_' + h.upper().replace('-', '_')
        v = v.strip()
        if k in env:
            env[k] += ', ' + v
        else:
            env[k] = v
        if k in ('HTTP_CONTENT_TYPE', 'HTTP_CONTENT_LENGTH'):
            env[k[5:]] = v
    return env


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


gen_hdrs = set((
    'HTTP_CACHE_CONTROL', 'HTTP_CONNECTION', 'HTTP_DATE', 'HTTP_PRAGMA',
    'HTTP_TRAILER', 'HTTP_TRANSFER_ENCODING', 'HTTP_UPGRADE', 'HTTP_VIA',
    'HTTP_WARNING'
))

req_hdrs = set((
    'HTTP_ACCEPT', 'HTTP_ACCEPT_CHARSET', 'HTTP_ACCEPT_ENCODING',
    'HTTP_ACCEPT_LANGUAGE', 'HTTP_AUTHORIZATION', 'HTTP_EXPECT', 'HTTP_FROM',
    'HTTP_HOST', 'HTTP_IF_MATCH', 'HTTP_IF_MODIFIED_SINCE',
    'HTTP_IF_NONE_MATCH', 'HTTP_IF_RANGE', 'HTTP_IF_UNMODIFIED_SINCE',
    'HTTP_MAX_FORWARDS', 'HTTP_PROXY_AUTHORIZATION', 'HTTP_RANGE',
    'HTTP_REFERER', 'HTTP_TE', 'HTTP_USER_AGENT'
))

resp_hdrs = set((
    'HTTP_ACCEPT_RANGES', 'HTTP_AGE', 'HTTP_ETAG', 'HTTP_LOCATION',
    'HTTP_PROXY_AUTHENTICATE', 'HTTP_RETRY_AFTER', 'HTTP_SERVER', 'HTTP_VARY',
    'HTTP_WWW_AUTHENTICATE'
))

msg_hdrs = gen_hdrs | req_hdrs | resp_hdrs
