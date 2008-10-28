import os
import signal
import socket
import select
import errno
import re


import greennet
from greennet import greenlet
from greennet.trigger import Trigger


__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'


from httpd.serve import accept_connections, listen
from httpd.static_files import static_files
sf = static_files('.')
rx = re.compile(r'/(.*)')

def handle_request(req):
    return sf(req, rx.match(req['path']))


def stop(trigger, sock):
    trigger.wait()
    sock.close()


def signal_handler(trigger):
    def handle(sig, frm):
        trigger.pull()
    return handle


def main():
    sock = listen(('', 8000))
    trigger = Trigger()
    import signal
    handler = signal_handler(trigger)
    signal.signal(signal.SIGINT, handler)
    greennet.schedule(greenlet(stop), trigger, sock)
    greennet.switch()
    try:
        accept_connections(sock, handle_request)
    except (socket.error, select.error), err:
        if err.args[0] != errno.EBADF:
            raise

