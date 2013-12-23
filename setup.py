# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys

import bazaar

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = bazaar.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='Django Bazaar',
    version=version,
    description="It's a bazaar",
    long_description=readme + '\n\n' + history,
    author='Federico Frenguelli',
    author_email='synasius@gmail.com',
    url='https://github.com/evonove/django-bazaar',
    packages=[
        'bazaar',
    ],
    include_package_data=True,
    install_requires=[
        'Pillow',
        'django-braces',
        'django-crispy-forms>=1.4.0',
        'django-stored-messages>=0.2.1',
        'djangorestframework==2.3.10',
        'django-money>=0.4.1',
        'django-money-rates',
        'django-filter',
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-bazaar',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)