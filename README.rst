ocookie - a comprehensive cookie library for Python
===================================================

The goal of ocookie is to be a *comprehensive* cookie library.
It should satisfy the needs of any application dealing with cookies.
Specifically it aims to address the following use cases:

- HTTP clients/crawlers/scrapers dealing with cookies
- HTTP servers dealing with cookies
- HTTP proxies forwarding cookies
- Test frameworks keeping track of cookies and asserting over cookies
- Examining cookies returned from a single request
- Keeping track of session cookies via a cookie jar
- Maintaining pristine lists of cookie headers
- Accessing cookies as dictionaries

At the same time ocookie is intended to be easy to use:

- Client and server interfaces are similar where it makes sense
- Straightforward conversions from client to server objects and vice versa
- Clear and intuitive naming conventions
- Complete documentation

Note: API is not yet stable.

Tests
-----

Execute the test suite by running ``nosetests``.

The test suite uses some nose features and will not work with unittest alone.

.. image:: https://api.travis-ci.org/p/ocookie.png
  :target: https://travis-ci.org/p/ocookie

License
-------

Released under the 2 clause BSD license.
