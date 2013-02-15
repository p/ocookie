import time

# python 2/3 compatibility
try:
    # 3.x and this must be first
    import urllib.parse as urllib_parse
except ImportError:
    # 2.x
    import urllib as urllib_parse

try:
    # 2.x
    base_exception_class = StandardError
except NameError:
    # 3.x
    base_exception_class = Exception

class CookieError(base_exception_class):
    pass

OPTIONAL_ATTRIBUTES = [
    'comment', 'domain', 'expires', 'httponly', 'max-age', 'path', 'secure',
    'version',
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
        if 'max-age' in converted_attributes:
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
    
    def __str__(self):
        attrs = ''
        for key in self.attributes:
            attrs += '; %s=%s' % (key, self.attributes[key])
        return '<%s(%s=%s%s)>' % (self.__class__.__name__, self.name, self.value, attrs)
    
    @property
    def expires_timestamp(self):
        return CookieExpirationTime.parse(self.expires).value

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

strftime_format = '%a %b %m %d %H:%M:%S %Z %Y'
strftime_format2 = '%a, %d %b %Y %H:%M:%S %Z'
strftime_format_netscape = '%a, %d-%b-%Y %H:%M:%S %Z'

def parse_http_time(time_str):
    if time_str:
        import calendar
        try:
            value = calendar.timegm(time.strptime(time_str, strftime_format2))
        except ValueError:
            value = calendar.timegm(time.strptime(time_str, strftime_format_netscape))
    else:
        value = None
    return value

class CookieExpirationTime(object):
    def __init__(self, value, str=None):
        if not isinstance(value, int) and not isinstance(value, float):
            raise ValueError('Value must be int or float: %s' % value)
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
            self.str = time.strftime(strftime_format, time.gmtime(self.value))
        return self.str

class LiveCookie(RawCookie):
    '''A cookie that tracks its expiration time.'''
    
    def __init__(self, name, value, **attributes):
        self.issue_time = time.time()
        RawCookie.__init__(self, name, value, **attributes)
    
    def valid(self):
        expires = self.expires_timestamp
        if expires is None:
            # valid until the end of session
            # assume as long as we're alive, we are in the session
            return True
        return expires > time.time()
    
    @property
    def expires_timestamp(self):
        max_age = self.attributes.get('max-age')
        if max_age is not None:
            expires = self.issue_time + max_age
        else:
            expires = self.attributes.get('expires')
            if expires is not None:
                expires = CookieExpirationTime.parse(expires).value
        return expires
    
    def __setattr__(self, key, value):
        if key == 'issue_time':
            object.__setattr__(self, key, value)
        else:
            RawCookie.__setattr__(self, key, value)

class CookieParser(object):
    @staticmethod
    def parse_cookie_value(text):
        cookie_dict = {}
        pairs = text.split(';')
        for pair in pairs:
            pair = pair.strip()
            name, value = pair.split('=')
            cookie = Cookie(name, value)
            cookie_dict[name] = cookie
        return cookie_dict
    
    @staticmethod
    def parse_set_cookie_value(text):
        attrs = text.split(';')
        name, value = attrs[0].split('=', 1)
        kwargs = {}
        for attr in attrs[1:]:
            fields = attr.split('=')
            if len(fields) > 1:
                attr_name, attr_value = [field.strip() for field in fields]
            else:
                attr_name = fields[0].strip()
                attr_value = True
            attr_name = attr_name.lower()
            if not attr_name in OPTIONAL_ATTRIBUTES_DICT:
                raise CookieError("Invalid cookie attribute: %s in cookie: %s" % (attr_name, text))
            kwargs[attr_name.replace('-', '_')] = attr_value
        return Cookie(name, value, **kwargs)
    
    @staticmethod
    def parse_set_cookie_header(text):
        name, value = text.split(':')
        name = name.lower()
        if name != 'set-cookie' and name != 'set-cookie2':
            raise CookieError("Not a Set-Cookie header: %s" % text)
        return self.parse_set_cookie_value(value.strip())

class CookieList(object):
    '''A list of cookies.
    
    Use when the order of cookies is significant, or when setting
    multiple cookies of the same name.
    '''

class CookieDict(dict):
    '''A dictionary of cookies.
    
    Use when retrieving cookies by name is desired.
    
    Setting a cookie overwrites any previously set cookies with the same name.
    '''
    
    def cookie_header_value(self):
        pairs = [name + '=' + self[name].value for name in self if self[name].value is not None and self[name].value.strip() != '']
        return '; '.join(pairs)

class CookieJar(object):
    '''A cookie jar, as is commonly implemented by user agents.
    
    Understands cookie expiration. Setting a cookie with an invalid or
    past expiration time deletes the cookie from the jar. Cookies that
    expire naturally are also automatically removed from the jar.
    '''
    
    def __init__(self, cookie_jar=None):
        if cookie_jar is None:
            self.cookie_dict = CookieDict()
        else:
            # copy
            self.cookie_dict = CookieDict(cookie_jar.cookie_dict)
    
    def __iter__(self):
        return self.cookie_dict.__iter__()
    
    def __delitem__(self, name):
        del self.cookie_dict[name]
    
    def __getitem__(self, name):
        return self.cookie_dict[name]
    
    def __setitem__(self, name, cookie):
        raise TypeError('Use add to put cookies into a CookieJar')
    
    def __contains__(self, name):
        return name in self.cookie_dict
    
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
        
        # valid means not expired
        if cookie.valid():
            self.cookie_dict[cookie.name] = cookie
        # if cookie was never set, and we are asked to set it with
        # an expiration date in the past, do nothing
        elif cookie.name in self.cookie_dict:
            del self.cookie_dict[cookie.name]
    
    def valid_cookies(self):
        # XXX hack relying on current internals of CookieDict
        return [cookie for cookie in self.cookie_dict.values() if cookie.valid()]
    
    def build_cookie_header_value(self):
        '''Creates value for a Cookie header, as would be sent by a user agent,
        from cookies currently in the jar.
        
        Cookies that are expired are not included.
        '''
        
        cookies = []
        for cookie in self.valid_cookies():
            # do not send empty cookies
            if cookie.value is not None and cookie.value.strip() != '':
                # XXX try not quoting cookie value
                # was: urllib_parse.quote(cookie.value)
                text = cookie.name + '=' + cookie.value
                cookies.append(text)
        return '; '.join(cookies)
    
    def clear(self):
        self.cookie_dict = CookieDict()
    
    def keys(self):
        return self.cookie_dict.keys()

def cookie_list_to_dict(cookie_list):
    cookie_dict = CookieDict()
    for cookie in cookie_list:
        cookie_dict[cookie.name] = cookie
    return cookie_dict
