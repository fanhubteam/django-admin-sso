.. _changelog:

Change log
==========

`Next version`_
~~~~~~~~~~~~~~~


`4.0`_ (2021-12-13)
~~~~~~~~~~~~~~~~~~~

- Dropped support for old versions of Django.


`3.1`_ (2020-12-13)
~~~~~~~~~~~~~~~~~~~

- Made the ``request`` argument to
  ``DjangoSSOAuthBackend.authenticate`` mandatory and actually pass the
  request from inside the authentication view.
- Added Django 3.1 to the CI matrix.


`3.0`_ (2020-01-21)
~~~~~~~~~~~~~~~~~~~

- Added compatibility with Django 2, 3.0.


.. _3.0: https://github.com/matthiask/django-admin-sso/commit/3.0
.. _3.1: https://github.com/matthiask/django-admin-sso/compare/3.0...3.1
.. _4.0: https://github.com/matthiask/django-admin-sso/compare/3.1...4.0
.. _Next version: https://github.com/matthiask/django-admin-sso/compare/4.0...main
