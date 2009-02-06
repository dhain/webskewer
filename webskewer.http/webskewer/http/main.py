import os
import signal
import socket
import select
import errno
import re


import greennet
from greennet import greenlet
from greennet.trigger import Trigger


from webskewer.http.serve import accept_connections, listen
from webskewer.http.static_files import static_files


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
        accept_connections(sock, static_files(u'.'))
    except (socket.error, select.error), err:
        if err.args[0] != errno.EBADF:
            raise
