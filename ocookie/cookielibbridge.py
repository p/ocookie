import cookielib
import rfc822
import cStringIO as StringIO

class PatchedCookielibCookieJar(cookielib.CookieJar):
    def _cookie_from_cookie_tuple(self, tup, request):
        # set to beginning of time to avoid any of the cookies expiring
        self._now = 0
        return cookielib.CookieJar._cookie_from_cookie_tuple(self, tup, request)

class FakeUrllibRequest(object):
    def get_full_url(self):
        return 'http://example.com/'

class FakeUrllibResponse(object):
    def __init__(self, info):
        self._info = info
    
    def info(self):
        return self._info

def parse_set_cookie_value(text):
    buf = StringIO.StringIO()
    buf.write('Set-Cookie: ')
    buf.write(text)
    buf.write("\n\n")
    buf.seek(0)
    
    message = rfc822.Message(buf)
    request = FakeUrllibRequest()
    response = FakeUrllibResponse(message)
    
    cl_cookie_jar = PatchedCookielibCookieJar()
    cl_cookies = cl_cookie_jar.make_cookies(response, request)
    print cl_cookies
    return cl_cookies
