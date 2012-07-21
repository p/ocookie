from . import CookieParser, CookieDict

def parse_cookies(httplib_headers):
    cookies = [
        CookieParser.parse_set_cookie_value(
            header[1]
        ) for header in httplib_headers if header[0].lower() == 'set-cookie'
    ]
    return cookies
