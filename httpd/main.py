import os
import signal
import socket
import errno
import re


import greennet
from greennet import greenlet
from greennet.trigger import Trigger


from httpd.serve import accept_connections, listen
from httpd.static_files import static_files
sf = static_files('.')
rx = re.compile(r'/(.*)')

def handle_request(req):
    return sf(req, rx.match(req['path']))


def stop(trigger):
    trigger.wait()
    hub = greennet.get_hub()
    hub.tasks.clear()
    for wait in hub.fdwaits:
        try:
            os.close(wait.fd)
        except Exception:
            pass
    hub.fdwaits.clear()


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
    greennet.schedule(greenlet(stop), trigger)
    greennet.switch()
    try:
        accept_connections(sock, handle_request)
    except socket.error, err:
        if err.args[0] != errno.EBADF:
            raise

