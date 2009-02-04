import os
import datetime
import mimetypes

from httpd import time_util, range_util, status, wsgi
from httpd.exceptions import RangePastEOFError, BadRangeSpecError
from httpd.util import normurl, decodeurl


def read_range(file, (start, end), bufsize=8192):
    file.seek(start)
    remain = True if end is None else end - start
    while remain:
        data = file.read(bufsize if end is None else min(remain, bufsize))
        if not data:
            if end is None:
                return
            else:
                raise RangePastEOFError()
        yield data
        if end is not None:
            remain -= len(data)


class static_files(object):
    read_buf = 8192
    dir_listing = (u'<html><head><title>Directory listing for'
                   u'%(url_path)s</title></head><body><h1>Directory '
                   u'listing for %(url_path)s</h1><ul>%(items)s</ul>'
                   u'</body></html>')
    
    def __init__(self, root, index_files=None,
                 default_charset=None, listing=True):
        self.root = os.path.abspath(root)
        if index_files is None:
            index_files = ['index.html']
        self.index_files = index_files
        self.default_charset = default_charset
        self.listing = listing
    
    def send_file(self, fn_):
        def send_file(environ, start_response):
            fn = fn_
            gzfn = fn + '.gz'
            if not fn.endswith('.gz') and os.path.isfile(gzfn):
                fn = gzfn
            st = os.stat(fn)
            mt = time_util.timestamp_to_dt(st.st_mtime, time_util.localtime)
            if not time_util.check_if_modified_since(environ, mt):
                return wsgi.NotModified()(environ, start_response)
            
            clen = st.st_size
            ctype, cenc = mimetypes.guess_type(fn)
            if ctype:
                if self.default_charset is not None and ctype.startswith('text/'):
                    ctype += '; charset=' + self.default_charset
            
            ranges = environ.get('HTTP_RANGE', None)
            if environ['REQUEST_METHOD'] == 'GET' and ranges:
                try:
                    ranges = list(range_util.canon(
                                  range_util.parse_ranges(ranges), clen))
                except BadRangeSpecError:
                    ranges = None
                else:
                    if not ranges:
                        return wsgi.RangeNotSatisfiable(clen)(environ, start_response)
            
            headers = [
                ('Last-modified', time_util.dt_to_1123(mt)),
                ('Accept-ranges', 'bytes'),
            ]
            
            if environ['REQUEST_METHOD'] == 'GET':
                f = open(fn, 'rb')
            else:
                f = None
            
            if False and environ['REQUEST_METHOD'] == 'GET' and ranges:
                # TODO: wsgify this
                def partial_start_response(status, headers, exc_info=None):
                    pass
                resp = wsgi.PartialContent(
                    ((start, end, read_range(f, (start, end)))
                     for start, end in ranges))
                content_headers = {}
                if ctype:
                    content_headers['content-type'] = ctype
                if cenc:
                    content_headers['content-encoding'] = cenc
                if content_headers:
                    for part in resp['entity']['parts']:
                        part['headers'].update(content_headers)
                resp['entity']['headers'].update(ent_headers)
            else:
                if ctype:
                    headers.append(('Content-type', ctype))
                if cenc:
                    headers.append(('Content-encoding', cenc))
                headers.append(('Content-length', clen))
                start_response(status.OK, headers)
                return read_range(f, (0, None))
        return send_file
    
    def list_dir(self, path):
        def list_dir(environ, start_response):
            url_path = environ['PATH_INFO']
            files = [u'../']
            for fn in sorted(os.listdir(path)):
                if os.path.isdir(os.path.join(path, fn)):
                    files.append(fn + u'/')
                else:
                    files.append(fn)
            items = u''.join(u'<li><a href="%s">%s</a></li>' % (fn, fn)
                             for fn in files).encode('utf-8')
            body = self.dir_listing % locals()
            start_response(status.OK,
                           [('Content-type', 'text/html; charset=utf-8'),
                            ('Content-length', str(len(body)))])
            return [body]
        return list_dir
    
    def __call__(self, environ, start_response):
        rel_path = environ['PATH_INFO'].lstrip('/').decode('utf-8')
        fn = os.path.normpath(os.path.join(self.root, rel_path))
        if fn.startswith(self.root):
            if os.path.isdir(fn):
                for f in self.index_files:
                    nfn = os.path.join(fn, f)
                    if os.path.isfile(nfn):
                        return (normurl(environ, True) or
                                self.send_file(nfn))(environ, start_response)
                if self.listing:
                    return (normurl(environ, True) or
                            self.list_dir(fn))(environ, start_response)
            elif os.path.isfile(fn):
                return (normurl(environ, False) or
                        self.send_file(fn))(environ, start_response)
        return wsgi.NotFound()(environ, start_response)
