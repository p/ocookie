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
app.run(port)

class HttplibAdapterTest(unittest.TestCase):
    def test_cookies(self):
        conn = httplib.HTTPConnection('localhost', port)
        conn.request('GET', '/set')
        response = conn.getresponse()
        self.assertEqual(to_bytes('success'), response.read())
        
        cookies = ocookie.httplib_adapter.parse_response_cookies(response)
        self.assertEqual(1, len(cookies))
        
        cookie = cookies[0]
        self.assertEqual('visited', cookie.name)
        self.assertEqual('yes', cookie.value)

if __name__ == '__main__':
    unittest.main()
