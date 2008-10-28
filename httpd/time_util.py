import datetime
from pytz import timezone


__author__ = 'David Hain'
__copyright__ = '2007-2008 ' + __author__
__license__ = 'MIT'


UTC = timezone('UTC')
localtime = timezone('US/Pacific')

log_datetime = "%d/%b/%Y:%H:%M:%S %z"
now_log = lambda tz=localtime: datetime.datetime.now().replace(tzinfo=tz).strftime(log_datetime)

rfc1123 = "%a, %d %b %Y %H:%M:%S GMT"
now_1123 = lambda: datetime.datetime.utcnow().strftime(rfc1123)
now_utc = lambda: datetime.datetime.utcnow().replace(tzinfo=UTC)
dt_from_1123 = lambda s: datetime.datetime.strptime(s, rfc1123).replace(tzinfo=UTC)
dt_to_1123 = lambda d: d.astimezone(UTC).strftime(rfc1123)
timestamp_to_dt = lambda t,tz=UTC: datetime.datetime.utcfromtimestamp(t).replace(tzinfo=tz)
timestamp_to_1123 = lambda t,tz=UTC: dt_to_1123(timestamp_to_dt(t,tz))


def check_if_modified_since(req, mt):
    if 'if-modified-since' in req['headers']:
        return dt_from_1123(req['headers']['if-modified-since']) < mt
    return True


def set_localtime(tzname):
    global localtime
    localtime = timezone(tzname)

