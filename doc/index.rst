ocookie - a comprehensive cookie library for Python
===================================================

**ocookie** aims to be an easy to use and comprehensive library for
working with cookies. While Python has several cookie-related libraries
in its standard library, they have incompatible interfaces and do not
expose all of the data and operations that one might need. **ocookie**
strives to provide a layered API suitable for all cookie-related tasks,
be they low level or high level, in a single library.

cookielib provides cookie management functionality, but the client and
server parts are separate and not easily convertible from one to the other.
cookielib is tightly coupled to httplib; parsing cookies with cookielib
requires one to construct fake httplib request and response objects.
Finally, cookielib's API itself can be improved.

ocookie should satisfy the needs of any application dealing with cookies.
Specifically it aims to address the following use cases:

Some of the use cases that ocookie has been designed for are:

- HTTP clients/crawlers/scrapers needing cookie jar functionality
- HTTP client libraries wishing to expose cookies on requests and responses
- HTTP server applications using cookies to keep state
- HTTP proxies forwarding cookies in both directions
- Test frameworks sending cookies in requests and asserting on cookies in
  responses

As such, ocookie provides the following cookie objects:

- RawCookie to examine cookies as they appear in an HTTP response
- Cookie is a canonicalized RawCookie with conflicting fields resolved
- LiveCookie is a cookie that understands its expiration time and validity

ocookie provides the following collections:

- CookieList is a simple list of cookies, handy for HTTP proxies
- CookieDict is a dictionary keyed by cookie name, handy when working with
  a single HTTP request or response
- CookieJar is a cookie container that understands cookie expiration,
  convenient for crawlers

ocookie provides CookieParser to parse cookies and serializers on all
cookie objects.

ocookie's main cookie parser is not intended to be a full cookie parser, as
this turns out to be a rather complex undertaking. Rather, ocookie provides a
light parser that will work for most web sites and applications, and for the
remaining cases ocookie will fall back on cookielib for cookie parsing.

ocookie values programmer time:

- Client and server interfaces are similar where it makes sense
- Straightforward conversions from client to server objects and vice versa
- Clear and intuitive naming conventions

Note: API is not yet stable.

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
