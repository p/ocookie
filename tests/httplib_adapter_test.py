import sys
import unittest
import ocookie.httplib_adapter
from tests import app

py3 = sys.version_info[0] == 3
if py3:
    import http.client as httplib
    def to_bytes(text):
        return text.encode('utf8')
else:
    import httplib
    def to_bytes(text):
        return text

port = 5040

def setup_module():
    app.run(port)

class HttplibAdapterTest(unittest.TestCase):
    def _request(self, url):
        conn = httplib.HTTPConnection('localhost', port)
        conn.request('GET', url)
        response = conn.getresponse()
        return response
    
    def test_no_cookies(self):
        response = self._request('/')
        self.assertEqual(to_bytes('none'), response.read())
        
        cookies = ocookie.httplib_adapter.parse_response_cookies(response)
        self.assertEqual(0, len(cookies))
    
    def test_cookies(self):
        response = self._request('/set')
        self.assertEqual(to_bytes('success'), response.read())
        
        cookies = ocookie.httplib_adapter.parse_response_cookies(response)
        self.assertEqual(1, len(cookies))
        
        cookie = cookies[0]
        self.assertEqual('visited', cookie.name)
        self.assertEqual('yes', cookie.value)

if __name__ == '__main__':
    unittest.main()
