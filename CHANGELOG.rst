.. _changelog:

Change log
==========

`Next version`_
~~~~~~~~~~~~~~~

- Made the ``request`` argument to
  ``DjangoSSOAuthBackend.authenticate`` mandatory and actually pass the
  request from inside the authentication view.
- Added Django 3.1 to the CI matrix.


`3.0`_ (2020-10-04)
~~~~~~~~~~~~~~~~~~~

- Added compatibility with Django 2, 3.0.


.. _3.0: https://github.com/matthiask/django-admin-sso/commit/3.0
.. _3.1: https://github.com/matthiask/django-admin-sso/compare/3.0...3.1
.. _Next version: https://github.com/matthiask/django-admin-sso/compare/0.13...master
