from __future__ import absolute_import
from __future__ import unicode_literals
from django.utils import timezone

from django.utils.text import slugify
from factory import fuzzy
from bazaar.listings.models import Publishing

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

    @factory.post_generation
    def product(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            quantity = kwargs.get("quantity", 1)
            ListingSetFactory(product=extracted, listing=self, quantity=quantity)

    @factory.post_generation
    def products(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            quantity = kwargs.get("quantity", 1)
            for product in extracted:
                ListingSetFactory(product=product, listing=self, quantity=quantity)


class ListingSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'listings.ListingSet'

    product = factory.SubFactory(ProductFactory)
    listing = factory.SubFactory(ListingFactory)

    quantity = 1


class StoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'listings.store'


class PublishingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'listings.Publishing'

    external_id = fuzzy.FuzzyText(length=10)
    status = Publishing.ACTIVE_PUBLISHING
    store = factory.SubFactory(StoreFactory)
