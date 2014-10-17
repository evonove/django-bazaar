from __future__ import absolute_import
from __future__ import unicode_literals

from django.utils.text import slugify

from bazaar.warehouse.models import Location

import factory

from moneyed import Money


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username',)

    username = 'john'


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'goods.Product'

    name = 'a product'
    price = Money(1, "EUR")


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'warehouse.Location'

    type = Location.LOCATION_STORAGE

    @factory.lazy_attribute
    def name(self):
        return "%s" % dict(Location.LOCATION_TYPE_CHOICES)[self.type]

    @factory.lazy_attribute_sequence
    def slug(self, n):
        return "%s%d" % (slugify(self.name), n)


class StorageFactory(LocationFactory):
    pass


class SupplierFactory(LocationFactory):
    type = Location.LOCATION_SUPPLIER


class CustomerFactory(LocationFactory):
    type = Location.LOCATION_CUSTOMER


class OutputFactory(LocationFactory):
    type = Location.LOCATION_OUTPUT


class LostFoundFactory(LocationFactory):
    type = Location.LOCATION_LOST_AND_FOUND


class StockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'warehouse.Stock'

    location = factory.SubFactory(StorageFactory)
    product = factory.SubFactory(ProductFactory)


class MovementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'warehouse.Movement'

    from_location = factory.SubFactory(SupplierFactory)
    to_location = factory.SubFactory(StorageFactory)

    product = factory.SubFactory(ProductFactory)

    quantity = 1
    unit_price = 1


class ListingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'listings.Listing'

    title = 'Listing test'


class ListingSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'listings.ListingSet'

    product = factory.SubFactory(ProductFactory)
    listing = factory.SubFactory(ListingFactory)

    quantity = 1
