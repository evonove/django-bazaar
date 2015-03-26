from __future__ import unicode_literals

from django.db import models

FORCED_LOWER = -999999


class ListingManager(models.Manager):
    def high_availability(self):
        """
        Returns a list of ids of the listings for which the quantity of a product in stock
        is less then the amount needed to satisfy it
        """
        from django.db.models import F
        from .models import Publishing
        from ..warehouse.models import Location
        listings = self.filter(publishings__status=Publishing.ACTIVE_PUBLISHING,
                               product__stocks__location__type=Location.LOCATION_STORAGE,
                               product__stocks__quantity__lt=F('publishings__available_units'))
        return listings.values_list('id')

    def low_availability(self):
        """
        Returns a list of ids of the listings for which the quantity of a product in stock
        is more then the amount needed to satisfy it
        """
        from django.db.models import F
        from .models import Publishing
        from ..warehouse.models import Location
        listings = self.filter(publishings__status=Publishing.ACTIVE_PUBLISHING,
                               product__stocks__location__type=Location.LOCATION_STORAGE,
                               product__stocks__quantity__gt=F('publishings__available_units') + 2)
        return listings.values_list('id')

    def low_price(self):
        """
        Returns a list of ids of the listings for which the quantity of a product in stock
        is less then the amount needed to satisfy it
        """
        from django.db.models import F
        from .models import Publishing
        from ..warehouse.models import Location
        # FIXME: How this can work?
        listings = self.filter(publishings__status=Publishing.ACTIVE_PUBLISHING,
                               product__stocks__location__type=Location.LOCATION_STORAGE,
                               product__stocks__unit_price__gt=F('publishings'))
        return listings.values_list('id')


class PublishingsManager(models.Manager):

    def active(self, listing=None):
        qs = self.get_queryset().filter(status=self.model.ACTIVE_PUBLISHING)
        if listing is not None:
            qs = qs.filter(listing=listing)
        return qs

    def main_publishings(self, listing=None):
        where = """
        "listings_publishing"."pub_date" IN
            (
                SELECT MAX("A0"."pub_date") AS "max_date"
                  FROM "listings_publishing" AS "A0"
                 WHERE NOT ("A0"."status" = %s )
                   AND "listings_publishing"."listing_id" = "A0"."listing_id"
                   AND "listings_publishing"."store_id" = "A0"."store_id"
              GROUP BY "A0"."listing_id", "A0"."store_id"
            )
        AND NOT EXISTS (
             SELECT *
               FROM "listings_publishing" AS "B0"
              WHERE "B0"."status" = %s
                AND "listings_publishing"."listing_id" = "B0"."listing_id"
                AND "listings_publishing"."store_id" = "B0"."store_id"
            )
        """

        qs = self.get_queryset().extra(
            where=[where], params=[self.model.ACTIVE_PUBLISHING, self.model.ACTIVE_PUBLISHING]
        )

        if listing is not None:
            qs = qs.filter(listing=listing)

        return qs | self.active(listing)
