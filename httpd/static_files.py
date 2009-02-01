import os
import datetime
import mimetypes

from httpd import message
from httpd import time_util
from httpd import range_util
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
    dir_listing = ('<html><head><title>Directory listing for'
                   '%(url_path)s</title></head><body><h1>Directory '
                   'listing for %(url_path)s</h1><ul>%(items)s</ul>'
                   '</body></html>')
    
    def __init__(self, root, index_files=None,
                 default_charset=None, listing=True):
        self.root = os.path.abspath(root)
        if index_files is None:
            index_files = ['index.html']
        self.index_files = index_files
        self.default_charset = default_charset
        self.listing = listing
    
    def send_file(self, req, fn):
        gzfn = fn + '.gz'
        if not fn.endswith('.gz') and os.path.isfile(gzfn):
            fn = gzfn
        st = os.stat(fn)
        mt = time_util.timestamp_to_dt(st.st_mtime, time_util.localtime)
        if not time_util.check_if_modified_since(req, mt):
            return message.NotModified(req)
        
        clen = st.st_size
        ctype, cenc = mimetypes.guess_type(fn)
        if ctype:
            if self.default_charset is not None and ctype.startswith('text/'):
                ctype += '; charset=' + self.default_charset
        
        ranges = req['headers'].get('range', None)
        if req['method'] == 'GET' and ranges:
            try:
                ranges = list(range_util.canon(
                              range_util.parse_ranges(ranges), clen))
            except BadRangeSpecError:
                ranges = None
            else:
                if not ranges:
                    return message.RangeNotSatisfiable(req, clen)
        
        ent_headers = {
            'last-modified': time_util.dt_to_1123(mt),
            'accept-ranges': 'bytes',
        }
        
        if req['method'] == 'GET':
            f = open(fn, 'rb')
        else:
            f = None
        
        if req['method'] == 'GET' and ranges:
            resp = message.PartialContent(req, (
                            (start, end, read_range(f, (start, end)))
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
            ent = message.entity(ent_headers,
                                 (f and read_range(f, (0, None))),
                                 clen, ctype)
            if cenc:
                ent['headers']['content-encoding'] = cenc
            resp = message.Response(req, ent=ent)
        
        return resp
    
    def list_dir(self, req, path):
        url_path = req['path']
        files = ['../']
        for fn in sorted(os.listdir(path)):
            if os.path.isdir(os.path.join(path, fn)):
                files.append(fn + '/')
            else:
                files.append(fn)
        items = ''.join('<li><a href="%s">%s</a></li>' % (fn, fn)
                        for fn in files)
        body = self.dir_listing % locals()
        return message.Response(req,
            ent=message.entity(body=body, ctype='text/html; charset=utf-8'))
    
    def __call__(self, req, m):
        rel_path = decodeurl(m.group(1))
        fn = os.path.normpath(os.path.join(self.root, rel_path))
        if fn.startswith(self.root):
            if os.path.isdir(fn):
                for f in self.index_files:
                    nfn = os.path.join(fn, f)
                    if os.path.isfile(nfn):
                        return normurl(req, True) or self.send_file(req, nfn)
                if self.listing:
                    return normurl(req, True) or self.list_dir(req, fn)
            elif os.path.isfile(fn):
                return normurl(req, False) or self.send_file(req, fn)
        return message.NotFound(req)
