from collections import deque

from webskewer.serve.grammar import range_spec
from webskewer.serve.exceptions import BadRangeSpecError


def parse_range(s):
    start, end = (int(x) if x else None for x in s.split('-', 1))
    if (start, end) == (None, None):
        raise BadRangeSpecError((start, end))
    if None not in (start, end) and start > end:
        raise BadRangeSpecError((start, end))
    if start is None:
        start = -end
        end = None
    return (start, end)


def canon(ranges, size=None):
    if not ranges:
        return
    ranges = deque(sorted(ranges))
    suffix = None
    if ranges[0][0] < 0:
        suffix = ranges.popleft()
        while ranges:
            if ranges[0] >= 0:
                break
            ranges.popleft()
    if size is not None:
        suffix = (max(0, size + suffix[0]), size - 1)
        while ranges:
            if suffix[0] <= ranges[-1][0]:
                ranges.pop()
            else:
                break
    if not ranges:
        if suffix:
            yield suffix
        return
    last = ranges.popleft()
    for start, end in ranges:
        if size is not None and start >= size:
            break
        if start <= last[1] + 1:
            last = (last[0], max(end, last[1]))
        else:
            yield last
            last = (start, end)
    yield last
    if suffix:
        yield suffix


def parse_ranges(s):
    m = range_spec.match(s)
    if not m:
        raise BadRangeSpecError(s)
    for r in m.group(1).split(','):
        yield parse_range(r.strip())


def range_helper():
    if 'range' in req['headers']:
        try:
            ranges = canonicalize_suffix(st.st_size,
                                *parse_ranges(req['headers']['range']))
        except BadRangeSpecError:
            pass
        else:
            resp['status'] = PARTIAL_CONTENT
            if len(ranges) == 1:
                start, end = ranges[0]
                endx = st.st_size - 1 if end is None else end
                ent['headers']['content-range'] = 'bytes %d-%d/%d' % (
                                                start, endx, st.st_size)
                ent['headers']['content-length'] = endx - start
                if f:
                    ent['body'] = reader(f, self.read_buf, (s, e))
            else:
                boundary = make_boundary()
                multipart = message.entity()
                multipart['headers'] = ent['headers'].copy()
                multipart['headers']['content-type'] = (
                    'multipart/byteranges; boundary=' + boundary)
                del multipart['headers']['content-length']
                if f:
                    parts = []
                    for s, e in ranges:
                        part = ent.copy()
                        part['headers'] = {
                            'content-type': ent['headers']['content-type'],
                            'content-range': 'bytes %d-%d/%d' % (
                                s, st.st_size - 1 if e is None else e, st.st_size)
                        }
                        part['body'] = reader(f, self.read_buf, (s, e))
                        parts.append(part)
                    multipart['body'] = format_multipart(parts, boundary)
                resp['entity'] = multipart

