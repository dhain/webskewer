from httpd.time_util import now_log


__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'


def log_req(env, headers_sent, clen=None):
    status, headers = headers_sent
    if clen is None:
        for name, value in headers:
            if name.lower != 'content-length':
                continue
            clen = value
            break
        else:
            clen = '-'
    return '%s - %s [%s] "%s" %s %s' % (
        env['REMOTE_ADDR'],
        env.get('REMOTE_USER', '-'),
        now_log(),
        env['neti.http_request'].rstrip(),
        status.split(' ', 1)[0],
        clen
    )


def log_err(msg, remote_addr='-'):
    return '[%s] [error] [client %s] %s' % (
        now_log(),
        remote_addr,
        msg
    )


def log_exc(remote_addr='-'):
    from asyncore import compact_traceback
    tb = str(compact_traceback()[1:])
    return log_err(tb, remote_addr)
