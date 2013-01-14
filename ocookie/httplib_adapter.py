import sys
from . import CookieParser

py3 = sys.version_info[0] == 3

# possibly needed in python 2 only
def parse_cookies(httplib_set_cookie_headers):
    '''Parses a list of Set-Cookie and Set-Cookie2 headers.
    
    httplib_set_cookie_headers is a sequence of strings, each string being
    a full header string (e.g. "Set-Cookie: foo=bar; path=/").
    
    Returns a list of Cookie instances.
    '''
    
    cookies = []
    for header in httplib_set_cookie_headers:
        header = header.strip()
        name, value = header.split(' ', 1)
        value = value.strip()
        cookie = CookieParser.parse_set_cookie_value(value)
        cookies.append(cookie)
    return cookies

# RFC 2616 specifies that multiple headers can be combined into
# a single header by joining their values with commas
# (http://stackoverflow.com/questions/2454494/urllib2-multiple-set-cookie-headers-in-response).
# However, Set-Cookie headers simply cannot be combined in that way
# as they have commas in dates and also there is no standard
# way of quoting cookie values, which may also have commas.
# Therefore the correct way of accessing Set-Cookie headers
# is via httplib_response.msg.getallmatchingheaders() call.
# http://mail.python.org/pipermail/python-bugs-list/2007-March/037618.html
# Also:
# http://stackoverflow.com/questions/1649401/how-to-handle-multiple-set-cookie-header-in-http-response

# getallmatchingheaders had been broken in python 3:
# http://bugs.python.org/issue5053
# http://bugs.python.org/issue13425
# There is a get_all method which is python 3 only that does what
# getallmatchingheaders did (correctly).
# Additionally, get_all returns None by default if there are no
# matching headers.
if py3:
    def parse_response_cookies(httplib_response):
        values = httplib_response.msg.get_all('set-cookie', [])
        values.extend(httplib_response.msg.get_all('set-cookie2', []))
        cookies = [CookieParser.parse_set_cookie_value(value) for value in values]
        return cookies
else:
    def parse_response_cookies(httplib_response):
        headers = httplib_response.msg.getallmatchingheaders('set-cookie')
        headers.extend(httplib_response.msg.getallmatchingheaders('set-cookie2'))
        return parse_cookies(headers)

parse_response_cookies.__doc__ = '''
Parses cookies in an httplib Response.

Returns a list of Cookie instances.
'''
