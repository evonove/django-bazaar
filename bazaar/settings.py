from __future__ import unicode_literals
"""
This module is largely inspired by django-rest-framework settings.

Settings for Django Bazaar are all namespaced in the DJANGO_BAZAAR setting.
For example your project's `settings.py` file might look like this:

DJANGO_BAZAAR = {
    'DEFAULT_CURRENCY': 'EUR',
}

This module provides the `bazaar_settings` object, that is used to access
Bazaar settings, checking for user settings first, then falling
back to the defaults.
"""

from django.conf import settings
from django.utils import importlib, six

import moneyed

USER_SETTINGS = getattr(settings, 'DJANGO_BAZAAR', None)

DEFAULTS = {
    'CURRENCIES': (),
    'DEFAULT_CURRENCY': moneyed.EUR.code,
    'DEFAULT_AVAILABILITY_BACKEND': 'bazaar.warehouse.availability.AvailabilityBackend',
    'AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION': False,
    'LOGIN_REDIRECT_URL': "bazaar:home",
    'STORES': {},
    'LISTING_FILTER': 'bazaar.listings.filters.ListingFilter',
}

# List of settings that cannot be empty
MANDATORY = (
    'DEFAULT_CURRENCY',
    'DEFAULT_AVAILABILITY_BACKEND',
)

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    'DEFAULT_AVAILABILITY_BACKEND',
    'LISTING_FILTER',
)


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if isinstance(val, six.string_types):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        msg = "Could not import '%s' for setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class BazaarSettings(object):
    """
    A settings object, that allows Bazaar settings to be accessed as properties.

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(self, user_settings=None, defaults=None, import_strings=None, mandatory=None):
        self.user_settings = user_settings or {}
        self.defaults = defaults or {}
        self.import_strings = import_strings or ()
        self.mandatory = mandatory or ()

    def __getattr__(self, attr):
        # return None when searching for undefined validation methods
        if attr.startswith("validate_"):
            return None

        if attr not in self.defaults.keys():
            raise AttributeError("Invalid Bazaar setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        self.validate_setting(attr, val)

        # CURRENCIES is converted from a tuple to a list of tuples
        if attr == "CURRENCIES":
            if val:
                val = [(code, moneyed.CURRENCIES[code].name) for code in val]
            else:
                val = [(currency.code, currency.name) for currency in six.itervalues(moneyed.CURRENCIES)]

        # Cache the result
        setattr(self, attr, val)
        return val

    def validate_setting(self, attr, val):
        if not val and attr in self.mandatory:
            raise AttributeError("Bazaar setting: '%s' is mandatory" % attr)

        validator_func = getattr(self, "validate_%s" % attr.lower())
        if validator_func:
            validator_func(val)

    def validate_currencies(self, value):
        for code in value:
            if code not in moneyed.CURRENCIES:
                raise AttributeError(
                    "Bazaar setting CURRENCIES: '%s' is not a valid currency code." % value)

    def validate_default_currency(self, value):
        if value not in (code for code, value in self.CURRENCIES):
            raise AttributeError(
                "Bazaar setting DEFAULT_CURRENCY: '%s' is not a valid currency code." % value)


bazaar_settings = BazaarSettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS, MANDATORY)
