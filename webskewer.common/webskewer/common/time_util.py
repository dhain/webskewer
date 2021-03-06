import datetime
from pytz import timezone


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


def check_if_modified_since(environ, mt):
    if 'HTTP_IF_MODIFIED_SINCE' in environ:
        return dt_from_1123(environ['HTTP_IF_MODIFIED_SINCE']) < mt
    return True


def set_localtime(tzname):
    global localtime
    localtime = timezone(tzname)

