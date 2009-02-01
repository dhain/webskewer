import re


def regex_strings():
    octet   = r"(?:.|\n)"
    char    = ("[" + ''.join([chr(d) for d in xrange(128)])
                ).replace("\\","\\\\"
                ).replace("]","\\]") + "]"
    upalpha = r"[A-Z]"
    loalpha = r"[a-z]"
    alpha   = r"[a-zA-Z]"
    digit   = r"[0-9]"
    ctl     = r"[%s]" % (''.join([chr(d) for d in xrange(32)])+chr(127),)
    cr      = chr(13)
    lf      = chr(10)
    sp      = chr(32)
    ht      = chr(9)
    quote   = chr(34)
    crlf    = cr + lf
    lws     = r"(?:(?:%s)?[%s%s]+)" % (crlf, sp, ht)
    text    = r"(?:"+lws+"|[^"+ctl[1:-1]+"])"
    hexdig  = r"[a-fA-F0-9]"
    
    seps    = r"[()<>@,;:\\\"/\[\]?={}%s%s]" % (sp, ht)
    token   = r"(?:[^%s%s%s]+)" % (ctl[1:-1], seps[1:-1],
        ''.join([chr(d) for d in xrange(129,255)]))
    
    ctext   = text[:-2]+"()])"
    qtext   = text[:-2]+'"])'
    nqtext  = ctl[:-2]+'"]'
    qpair   = r"(?:\\%s)" % (char,)
    comment = r"(?:\((?:%s|%s)*(?<!\\)\))" % (ctext, qpair)
    qstring = r'(?:"(?:%s|%s)+(?<!\\)")' % (qtext, qpair)
    
    month     = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    weekday   = r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
    wkday     = r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)"
    time      = r"(\d{2}):(\d{2}):(\d{2})"
    date3     = r"%s (\d{2}| \d)" % (month,)
    date2     = r"(\d{2})-%s-(\d{2})" % (month,)
    date1     = r"(\d{2}) %s (\d{4})" % (month,)
    asctd     = r"%s %s %s (\d{4})" % (wkday, date3, time)
    rfc850    = r"%s, %s %s GMT" % (weekday, date2, time)
    rfc1123   = r"%s, %s %s GMT" % (wkday, date1, time)
    date      = r"%s|%s|%s" % (asctd, rfc850, rfc1123)
    
    parameter = r"%s=(?:%s|%s)" % (token, token, qstring)
    transfer_coding = r"%s(?:;%s)*" % (token, parameter)
    media_type = r"%s/%s(?:;%s)*" % (token, token, parameter)
    product = r"%s(?:/%s)?" % (token, token)
    qvalue = r"(?:0(?:\.\d{0,3})?)|(?:1(?:\.0{0,3})?)"
    language_tag = r"%s{1,8}(?:-%s{1,8})*" % (alpha, alpha)
    
    cookie_path = r"(?:;%s*\$path=(%s|%s))" % (lws, token, qstring)
    cookie_domain = r"(?:;%s*\$domain=(%s|%s))" % (lws, token, qstring)
    cookie_value = r"(?i)(%s)=(%s|%s)%s?%s?" % \
        (token, token, qstring, cookie_path, cookie_domain)
    
    host_value = r"([^:]+)(?::(\d+))?$"
    
    header = r"(%s):(%s*)%s" % (token, text, crlf)
    value_list = r"(?:^|,)%s*(%s|%s)" % (lws, token, qstring)
    
    range_spec = r"bytes=((?:(?:\d+-\d*)|(?:-\d+))" + \
        r"(?:,%s*(?:(?:\d+-\d*)|(?:-\d+)))*)$" % (lws,)
    
    chunk_ext  = r"(?:;%s(?:=(?:%s|%s))?)" % (token, token, qstring)
    chunk_size = r"(%s+)\s*%s*\s*%s" % (hexdig, chunk_ext, crlf)
    
    http_version = r"HTTP/(\d+)\.(\d+)"
    abs_uri      = r"(?:[a-zA-Z][a-zA-Z0-9+-.]*://[^/?#\s]+/[^#\s]*)"
    abs_path     = r"(?:/[^#\s]*)"
    req09 = r"GET (%s)%s$" % (abs_path, crlf)
    req1x = r"(%s) (\*|%s|%s) %s%s$" % \
        (token, abs_path, abs_uri, http_version, crlf)
    
    resp1x = r"%s (\d{3}) (%s+)%s$" % (http_version, text, crlf)
    
    token += '$'
    
    del d
    return dict((k, re.compile(v)) for k,v in locals().iteritems())

locals().update(regex_strings())
