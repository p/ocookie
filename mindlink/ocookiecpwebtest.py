from . import ocookie

def parse_cookies(cpwt_cookies):
    '''Parses self.cookies after a getPage call.
    '''
    
    cookies = [ocookie.CookieParser.parse_set_cookie_value(cookie[1]) for cookie in cpwt_cookies]
    return cookies

class CpwtCookieJar(ocookie.CookieJar):
    def update(self, cpwt_cookies):
        cookies = parse_cookies(cpwt_cookies)
        for cookie in cookies:
            self.add(cookie)
