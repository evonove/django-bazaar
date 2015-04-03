from __future__ import absolute_import
from __future__ import unicode_literals

from bazaar.settings import bazaar_settings
from bazaar.warehouse.models import Location


def get_location(slug):
    try:
        return Location.objects.get(slug=slug)
    except Location.DoesNotExist:
        return None


def get_storage():
    return Location.objects.get_or_create(name=bazaar_settings.STORAGE_NAME,
                                          slug=bazaar_settings.STORAGE,
                                          type=Location.LOCATION_STORAGE)[0]


def get_output():
    return Location.objects.get_or_create(name=bazaar_settings.OUTPUT_NAME,
                                          slug=bazaar_settings.OUTPUT,
                                          type=Location.LOCATION_OUTPUT)[0]


def get_lost_and_found():
    return Location.objects.get_or_create(name=bazaar_settings.LOST_AND_FOUND_NAME,
                                          slug=bazaar_settings.LOST_AND_FOUND,
                                          type=Location.LOCATION_LOST_AND_FOUND)[0]


def get_customer():
    return Location.objects.get_or_create(name=bazaar_settings.CUSTOMER_NAME,
                                          slug=bazaar_settings.CUSTOMER,
                                          type=Location.LOCATION_CUSTOMER)[0]


def get_supplier():
    return Location.objects.get_or_create(name=bazaar_settings.SUPPLIER_NAME,
                                          slug=bazaar_settings.SUPPLIER,
                                          type=Location.LOCATION_SUPPLIER)[0]
