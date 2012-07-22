import unittest, time

import ocookie

class CookieTest(unittest.TestCase):
    def test_construction(self):
        cookie = ocookie.Cookie('foo', 'bar', httponly=True)
        self.assertEquals('foo', cookie.name)
        self.assertEquals('bar', cookie.value)
        self.assertTrue(cookie.httponly)
        self.assertFalse(cookie.secure)

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

class CookieHeaderValueParsingtest(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
