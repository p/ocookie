class CookieError(StandardError):
    pass

ATTRIBUTES = [
    'expires', 'path', 'comment', 'domain', 'max-age', 'secure',
    'version', 'httponly',
]

ATTRIBUTES_DICT = {}

for key in ATTRIBUTES:
    ATTRIBUTES_DICT[key] = True
del key

class RawCookie:
    '''An unaltered cookie from a Set-Cookie header.
    
    Only those attributes that were set in the header are present.
    For example, if max-age was set and expires was not set then
    the value of expires would be None.
    '''
    
    def __init__(self, name, value, **attributes):
        for key in attributes:
            if not key in ATTRIBUTES_DICT:
                raise ValueError("Unrecognized cookie attribute: " + str(key))
        self.name = name
        self.value = value
        self.attributes = attributes
    
    def __getattr__(self, key):
        if not key in ATTRIBUTES_DICT:
            raise AttributeError("Unrecognized cookie attribute: " + str(key))
        return self.attributes.get(key, None)
    
    def __setattr__(self, key, value):
        if not key in ATTRIBUTES_DICT:
            raise AttributeError("Unrecognized cookie attribute: " + str(key))
        self.attributes[key] = value

class Cookie(RawCookie):
    '''A canonicalized cookie.
    
    Currently the only case of multiple attributes affecting the same data is
    expires/max-age. Cookie implements RFC-compliant behavior of max-age.
    A Cookie object's expiration time may be retrieved via either expires
    or max-age. If a cookie was set with expires and its max-age is requested,
    expires will be converted to max-age using either response time,
    if set, or the time of Cookie object creation otherwise.
    
    Note: MSIE does not support max-age, therefore expires should always
    be used when serving cookies to browsers.
    (http://mrcoles.com/blog/cookies-max-age-vs-expires/)
    '''

class LiveCookie(Cookie):
    '''A cookie that tracks its expiration time.'''

class Cookie:
    def __init__(self, name, value,
        expires=None, path=None, comment=None, domain=None, max_age=None,
        secure=None, version=None, httponly=None
    ):
        self.name = name
        self.value = value
        self.expires = expires
        self.path = path
        self.comment = comment
        self.domain = domain
        self.max_age = max_age
        self.secure = secure
        self.version = version
        self.httponly = httponly

class CookieParser:
    @staticmethod
    def parse_set_cookie_value(text):
        attrs = text.split(';')
        name, value = attrs[0].split('=')
        kwargs = {}
        for attr in attrs[1:]:
            attr_name, attr_value = [field.strip() for field in attr.split('=')]
            if not attr_name in ATTRIBUTES_DICT:
                raise CookieError, "Invalid cookie attribute: %s in cookie: %s" % (attr_name, text)
            kwargs[attr_name.replace('-', '_')] = attr_value
        return Cookie(name, value, **kwargs)
    
    @staticmethod
    def parse_set_cookie_header(text):
        name, value = text.split(':')
        name = name.lower()
        if name != 'set-cookie' and name != 'set-cookie2':
            raise CookieError, "Not a Set-Cookie header: %s" % text
        return self.parse_set_cookie_value(value.strip())

class CookieList:
    '''A list of cookies.
    
    Use when the order of cookies is significant, or when setting
    multiple cookies of the same name.
    '''

class CookieDict:
    '''A dictionary of cookies.
    
    Use when retrieving cookies by name is desired.
    
    Setting a cookie overwrites any previously set cookies with the same name.
    '''
    
    def __init__(self):
        self.cookies = {}
    
    def __iter__(self):
        return self.cookies.__iter__()
    
    def __delitem__(self, name):
        # catch KeyError here?
        del self.cookies[name]
    
    def __getitem__(self, name):
        return self.cookies[name]
    
    def __setitem__(self, name, cookie):
        self.cookies[name] = cookie

class CookieJar:
    '''A cookie jar, as is commonly implemented by user agents.
    
    Understands cookie expiration. Setting a cookie with an invalid or
    past expiration time deletes the cookie from the jar. Cookies that
    expire naturally are also automatically removed from the jar.
    '''
    
    def __init__(self):
        self.cookies = CookieDict()
    
    def add(self, cookie):
        '''Adds a cookie to the cookie jar.
        
        If a cookie already exists with the same name, the old cookie is
        overwritten with the provided cookie.
        
        If the expiration time of the new cookie is in the past then
        no cookie is set (and if there was an existing cookie with the
        same name, the old cookie is deleted).
        '''
        
        if cookie.valid():
            self.cookies[cookie.name] = cookie
        else:
            del self.cookies[cookie.name]
    
    def build_cookie_header(self):
        '''Creates value for a Cookie header, as would be sent by a user agent,
        from cookies currently in the jar.
        
        Cookies that are expired are not included.
        '''
        
        cookies = []
        for cookie in self.cookies:
            if cookie.valid():
                cookies.append(cookie.name + '=' + cookies.value)
        return ', '.join(cookies)
