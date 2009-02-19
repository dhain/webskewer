from webskewer.serve.time_util import now_log


def log_req(env, status, headers, clen=None):
    if clen is None:
        for name, value in headers:
            if name.lower() != 'content-length':
                continue
            clen = value
            break
        else:
            clen = '-'
    return '%s - %s [%s] "%s" %s %s' % (
        env['REMOTE_ADDR'],
        env.get('REMOTE_USER', '-'),
        now_log(),
        env['webskewer.http_request'].rstrip(),
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
