from httpd.time_util import now_log


__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'


def log_req(req, resp, clen=None):
    if clen is None:
        clen = resp['entity']['headers'].get('content-length', '-')
    return '%s - %s [%s] "%s" %d %s' % (
        req.get('remote_addr', '-'),
        req.get('username', '-'),
        now_log(),
        req['request'].rstrip(),
        resp['status'][0],
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
