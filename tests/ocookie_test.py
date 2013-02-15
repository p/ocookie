import unittest, time

import ocookie

class CookieTest(unittest.TestCase):
    def test_construction(self):
        cookie = ocookie.Cookie('foo', 'bar', httponly=True)
        self.assertEquals('foo', cookie.name)
        self.assertEquals('bar', cookie.value)
        self.assertTrue(cookie.httponly)
        self.assertFalse(cookie.secure)

class CookieDictTest(unittest.TestCase):
    def test_cookie_header_value_one(self):
        cookie_dict = ocookie.CookieDict()
        cookie_dict['a'] = ocookie.Cookie('a', 'b')
        header_value = cookie_dict.cookie_header_value()
        self.assertEqual('a=b', header_value)
    
    def test_cookie_header_value_two(self):
        cookie_dict = ocookie.CookieDict()
        cookie_dict['a'] = ocookie.Cookie('a', 'b')
        cookie_dict['c'] = ocookie.Cookie('c', 'd')
        header_value = cookie_dict.cookie_header_value()
        self.assertTrue(
            header_value == 'a=b; c=d' or
            header_value == 'c=d; a=b'
        )
    
    def test_cookie_header_value_empty(self):
        cookie_dict = ocookie.CookieDict()
        cookie_dict['a'] = ocookie.Cookie('a', 'aa')
        cookie_dict['b'] = ocookie.Cookie('b', '')
        cookie_dict['c'] = ocookie.Cookie('c', None)
        header_value = cookie_dict.cookie_header_value()
        self.assertEqual('a=aa', header_value)
    
    def test_cookie_header_value_colon(self):
        cookie_dict = ocookie.CookieDict()
        cookie_dict['a'] = ocookie.Cookie('a', 'b:c')
        header_value = cookie_dict.cookie_header_value()
        # matches urllib2 behavior
        self.assertEqual('a=b:c', header_value)
    
    def test_deletion(self):
        cookie_dict = ocookie.CookieDict()
        cookie_dict['a'] = ocookie.Cookie('a', 'b')
        self.assertTrue('a' in cookie_dict)
        self.assertTrue('c' not in cookie_dict)
        cookie_dict['c'] = ocookie.Cookie('c', 'd')
        self.assertTrue('c' in cookie_dict)
        
        del cookie_dict['c']
        self.assertTrue('c' not in cookie_dict)
    
    def test_access(self):
        cookie_dict = ocookie.CookieDict()
        cookie_dict['a'] = ocookie.Cookie('a', 'b')
        a = cookie_dict['a']
        self.assertEqual('b', a.value)
    
    def test_overwrite(self):
        cookie_dict = ocookie.CookieDict()
        cookie_dict['a'] = ocookie.Cookie('a', 'b')
        cookie_dict['a'] = ocookie.Cookie('a', 'c')
        a = cookie_dict['a']
        self.assertEqual('c', a.value)
    
    def test_copy(self):
        cookie_dict = ocookie.CookieDict()
        cookie_dict['a'] = ocookie.Cookie('a', 'c')
        a = cookie_dict['a']
        self.assertEqual('c', a.value)
        
        copy = ocookie.CookieDict(cookie_dict)
        assert 'a' in copy
        self.assertEqual('c', copy['a'].value)

class CookieJarTest(unittest.TestCase):
    def test_add(self):
        cookie_jar = ocookie.CookieJar()
        cookie = ocookie.Cookie('foo', 'bar')
        cookie_jar.add(cookie)
        
        self.assertTrue('foo' in cookie_jar)
        # Not currently supported
        #self.assertTrue(cookie in cookie_jar)
        
        # negative assertions
        self.assertFalse('bar' in cookie_jar)
        #bar_cookie = ocookie.Cookie('bar', 'bar')
        #self.assertFalse(bar_cookie in cookie_jar)
    
    def test_replacement(self):
        cookie_jar = ocookie.CookieJar()
        cookie = ocookie.Cookie('foo', 'bar')
        cookie_jar.add(cookie)
        
        replacement_cookie = ocookie.Cookie('foo', 'quux')
        cookie_jar.add(replacement_cookie)
        
        self.assertTrue('foo' in cookie_jar)
        self.assertEqual('quux', cookie_jar['foo'].value)
    
    def test_clear(self):
        cookie_jar = ocookie.CookieJar()
        cookie = ocookie.Cookie('foo', 'bar')
        cookie_jar.add(cookie)
        assert 'foo' in cookie_jar
        
        cookie_jar.clear()
        assert 'foo' not in cookie_jar
    
    def test_build_cookie_header_value(self):
        cookie_jar = ocookie.CookieJar()
        cookie = ocookie.Cookie('foo', 'bar')
        cookie_jar.add(cookie)
        assert 'foo' in cookie_jar
        
        expected = 'foo=bar'
        self.assertEqual(expected, cookie_jar.build_cookie_header_value())
    
    def test_build_cookie_header_value_two_cookies(self):
        cookie_jar = ocookie.CookieJar()
        cookie_jar.add(ocookie.Cookie('foo', 'foo-value'))
        cookie_jar.add(ocookie.Cookie('bar', 'bar-value'))
        
        actual = cookie_jar.build_cookie_header_value()
        self.assertTrue(
            actual == 'foo=foo-value; bar=bar-value' or
            actual == 'bar=bar-value; foo=foo-value'
        )
    
    def test_build_cookie_header_value_empty(self):
        cookie_jar = ocookie.CookieJar()
        cookie_jar.add(ocookie.Cookie('foo', 'foo-value'))
        cookie_jar.add(ocookie.Cookie('bar', ''))
        cookie_jar.add(ocookie.Cookie('quux', None))
        
        expected = 'foo=foo-value'
        self.assertEqual(expected, cookie_jar.build_cookie_header_value())
    
    def test_build_cookie_header_value_colon(self):
        cookie_jar = ocookie.CookieJar()
        cookie_jar.add(ocookie.Cookie('foo', 'a:b'))
        
        # matches urllib2 behavior
        expected = 'foo=a:b'
        self.assertEqual(expected, cookie_jar.build_cookie_header_value())
    
    def test_construct_copy(self):
        cookie_jar = ocookie.CookieJar()
        cookie_jar.add(ocookie.Cookie('foo', 'a:b'))
        assert 'foo' in cookie_jar
        
        copy = ocookie.CookieJar(cookie_jar)
        assert 'foo' in copy
        self.assertEqual(cookie_jar['foo'], copy['foo'])

class CookieHeaderValueParsingTest(unittest.TestCase):
    def test_one(self):
        value = 'foo=bar'
        cookie_dict = ocookie.CookieParser.parse_cookie_value(value)
        self.assertEqual(1, len(cookie_dict))
        self.assert_('foo' in cookie_dict)
        self.assertEqual('bar', cookie_dict['foo'].value)
        
        # negative checks for sanity
        self.assert_('bar' not in cookie_dict)
    
    def test_two(self):
        value = 'a=b; c=d'
        cookie_dict = ocookie.CookieParser.parse_cookie_value(value)
        self.assertEqual(2, len(cookie_dict))
        self.assert_('a' in cookie_dict)
        self.assertEqual('b', cookie_dict['a'].value)
        self.assert_('c' in cookie_dict)
        self.assertEqual('d', cookie_dict['c'].value)
        
        # negative checks for sanity
        self.assert_('bar' not in cookie_dict)

class CookieParserTest(unittest.TestCase):
    def test_parsing(self):
        text = 'foo=bar'
        cookie = ocookie.CookieParser.parse_set_cookie_value(text)
        self.assertEquals('foo', cookie.name)
        self.assertEquals('bar', cookie.value)
    
    def test_parsing_with_attributes(self):
        text = 'foo=bar; domain=.cc.edu; path=/; expires=Mon Jul 11 10:41:15 EDT 2011'
        cookie = ocookie.CookieParser.parse_set_cookie_value(text)
        self.assertEquals('foo', cookie.name)
        self.assertEquals('bar', cookie.value)
        self.assertEquals('.cc.edu', cookie.domain)
        self.assertEquals('/', cookie.path)
        self.assertEquals('Mon Jul 11 10:41:15 EDT 2011', cookie.expires)
    
    def test_parsing_with_valueless_attributes(self):
        text = 'foo=bar; httponly'
        cookie = ocookie.CookieParser.parse_set_cookie_value(text)
        self.assertEquals('foo', cookie.name)
        self.assertEquals('bar', cookie.value)
        self.assertEquals(True, cookie.httponly)
    
    def test_parsing_with_equal_sign(self):
        text = 'PREF=ID=38a82ea:FF=0:TM=59433:LM=209211:S=ad_B-z5; expires=Wed, 11-Feb-2015 22:59:51 GMT; path=/; domain=.bar.com'
        cookie = ocookie.CookieParser.parse_set_cookie_value(text)
        self.assertEquals('PREF', cookie.name)
        self.assertEquals('ID=38a82ea:FF=0:TM=59433:LM=209211:S=ad_B-z5', cookie.value)

class TimeParsingTest(unittest.TestCase):
    def test_time_parsing(self):
        text = 'Sun, 01 Jan 2012 00:00:00 GMT'
        time = ocookie.parse_http_time(text)
        self.assertEquals(1325376000, time)
    
    def test_time_parsing_netscape_yyyy(self):
        # RFC 2109 specifies:
        # Wdy, DD-Mon-YY HH:MM:SS GMT
        # Nowadays YY is replaced by YYYY for sanity.
        text = 'Sun, 01-Jan-2012 00:00:00 GMT'
        time = ocookie.parse_http_time(text)
        self.assertEquals(1325376000, time)

if __name__ == '__main__':
    unittest.main()
