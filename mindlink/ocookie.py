import time, urllib

class CookieError(StandardError):
    pass

OPTIONAL_ATTRIBUTES = [
    'expires', 'path', 'comment', 'domain', 'max-age', 'secure',
    'version', 'httponly',
]
ALL_ATTRIBUTES = [
    'name', 'value'
] + OPTIONAL_ATTRIBUTES

OPTIONAL_ATTRIBUTES_DICT = {}
for key in OPTIONAL_ATTRIBUTES:
    OPTIONAL_ATTRIBUTES_DICT[key] = True
ALL_ATTRIBUTES_DICT = {}
for key in ALL_ATTRIBUTES:
    ALL_ATTRIBUTES_DICT[key] = True
del key

class RawCookie(object):
    '''An unaltered cookie from a Set-Cookie header.
    
    Only those attributes that were set in the header are present.
    For example, if max-age was set and expires was not set then
    the value of expires would be None.
    '''
    
    def __init__(self, name, value, **attributes):
        # Apparently cherrypy changes max-age to Max-Age at some point.
        # And this is how it is spelled in RFC too.
        converted_attributes = {}
        for key in attributes:
            key_lower = key.lower().replace('_', '-')
            if not key_lower in OPTIONAL_ATTRIBUTES_DICT:
                if key_lower in ALL_ATTRIBUTES_DICT:
                    raise ValueErrror("Tried passing a required attribute as an optional attribute: " + str(key))
                else:
                    raise ValueError("Unrecognized cookie attribute: " + str(key))
            converted_attributes[key_lower] = attributes[key]
        self.name = name
        self.value = value
        # maybe we should only do type conversion in parsers
        if converted_attributes.has_key('max-age'):
            # XXX check if RFC allows floating point max-age
            converted_attributes['max-age'] = float(converted_attributes['max-age'])
        self.attributes = converted_attributes
    
    def __getattr__(self, key):
        key = key.lower()
        if not key in OPTIONAL_ATTRIBUTES_DICT:
            raise AttributeError("Unrecognized cookie attribute: " + str(key))
        return self.attributes.get(key, None)
    
    def __setattr__(self, key, value):
        if key in ('attributes', 'name', 'value'):
            object.__setattr__(self, key, value)
        else:
            key_lower = key.lower()
            if not key_lower in OPTIONAL_ATTRIBUTES_DICT:
                raise AttributeError("Unrecognized cookie attribute: " + str(key))
            self.attributes[key_lower] = value

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

class CookieExpirationTime:
    def __init__(self, value, str=None):
        self.value = value
        self.str = str
    
    @staticmethod
    def parse(time_str):
        time = parse_http_time(time_str)
        return CookieExpirationTime(time, str=time_str)
    
    def __str__(self):
        return self.as_http_date()
    
    def as_http_date(self):
        if self.str is None:
            self.str = time.strftime('%a %b %m %d %H:%M:%S %Z %Y', self.value)
        return self.str

class LiveCookie(RawCookie):
    '''A cookie that tracks its expiration time.'''
    
    def __init__(self, name, value, **attributes):
        self.issue_time = time.time()
        RawCookie.__init__(self, name, value, **attributes)
    
    def valid(self):
        expires = self.expires
        if expires is None:
            # valid until the end of session
            # assume as long as we're alive, we are in the session
            return True
        return expires < time.time()
    
    @property
    def expires(self):
        max_age = self.attributes.get('max-age')
        if max_age is not None:
            expires = self.issue_time + max_age
        else:
            expires = self.attributes.get('expires')
        return CookieExpirationTime(expires)
    
    def __setattr__(self, key, value):
        if key == 'issue_time':
            object.__setattr__(self, key, value)
        else:
            RawCookie.__setattr__(self, key, value)

class CookieParser:
    @staticmethod
    def parse_set_cookie_value(text):
        attrs = text.split(';')
        name, value = attrs[0].split('=')
        kwargs = {}
        for attr in attrs[1:]:
            attr_name, attr_value = [field.strip() for field in attr.split('=')]
            attr_name = attr_name.lower()
            if not attr_name in OPTIONAL_ATTRIBUTES_DICT:
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
        
        if not isinstance(cookie, LiveCookie):
            cookie = LiveCookie(cookie.name, cookie.value, **cookie.attributes)
        
        if cookie.valid():
            self.cookies[cookie.name] = cookie
        else:
            del self.cookies[cookie.name]
    
    def valid_cookies(self):
        # XXX hack relying on current internals of CookieDict
        return [cookie for cookie in self.cookies.cookies.values() if cookie.valid()]
    
    def build_cookie_header(self):
        '''Creates value for a Cookie header, as would be sent by a user agent,
        from cookies currently in the jar.
        
        Cookies that are expired are not included.
        '''
        
        cookies = []
        for cookie in self.valid_cookies():
            text = cookie.name + '=' + urllib.quote(cookie.value)
            cookies.append(text)
        return ', '.join(cookies)
    
    def clear(self):
        self.cookies = CookieDict()
