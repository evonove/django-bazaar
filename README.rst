=============================
Django Bazaar
=============================

.. image:: https://badge.fury.io/py/django-bazaar.png
    :target: http://badge.fury.io/py/django-bazaar
    
.. image:: https://travis-ci.org/evonove/django-bazaar.png?branch=master
        :target: https://travis-ci.org/evonove/django-bazaar

.. image:: https://pypip.in/d/django-bazaar/badge.png
        :target: https://crate.io/packages/django-bazaar?version=latest


It's a bazaar

Documentation
-------------

The full documentation is at http://django-bazaar.rtfd.org.

Quickstart
----------

Install Django Bazaar::

    pip install django-bazaar

To use it in a project add to `INSTALLED_APPS` the following:

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        'crispy_forms',
        'bazaar',
        'bazaar.goods',
        'bazaar.listings',
        'bazaar.warehouse',
        'bazaar.orders',
    )

Also add `django.core.context_processors.request` to `TEMPLATE_CONTEXT_PROCESSORS`

.. code-block:: python

    from django.conf import global_settings
    TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'django.core.context_processors.request',
    )

More documentation coming soon!

Features
--------

* TODO