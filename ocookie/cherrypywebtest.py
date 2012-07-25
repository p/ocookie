from . import CookieParser, CookieJar

def parse_cookies(cpwt_cookies):
    '''Parses self.cookies after a getPage call.
    '''
    
    cookies = [CookieParser.parse_set_cookie_value(cookie_header[1]) for cookie_header in cpwt_cookies]
    return cookies

class CpwtCookieJar(CookieJar):
    def update(self, cpwt_cookies):
        cookies = parse_cookies(cpwt_cookies)
        for cookie in cookies:
            self.add(cookie)
