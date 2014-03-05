from __future__ import unicode_literals

from django.db import models

from itertools import chain
from django.db.models import Max, Min


class ListingManager(models.Manager):
    def unavailable_ids(self):
        """
        Returns a list of ids of the listings for which the quantity of a product in stock
        is less than the amount needed to satisfy it
        """
        from django.db import connection
        from models import Order
        cursor = connection.cursor()

        cursor.execute("""
            SELECT DISTINCT A.listing_id FROM
                (SELECT
                    "listings_publishing"."listing_id",
                    "listings_listingset"."product_id",
                    "listings_publishing"."available_units" * "listings_listingset"."quantity"
                      AS "needed"
                FROM "listings_publishing"
                    JOIN "listings_listingset"
                    ON "listings_publishing"."listing_id" = "listings_listingset"."listing_id") AS A
            JOIN
                (SELECT
                    "listings_listingset"."product_id",
                    COALESCE("warehouse_stock"."quantity", 0) -
                    SUM("listings_listingset"."quantity" *
                    COALESCE("listings_order"."quantity", 0)) as "available"
                FROM "listings_listingset"
                    JOIN "listings_publishing"
                    ON "listings_publishing"."listing_id" = "listings_listingset"."listing_id"
                    LEFT JOIN "listings_order"
                    ON (
                      "listings_order"."publishing_id" = "listings_publishing"."id" AND
                      "listings_order"."status" = %s
                      )
                    LEFT JOIN "warehouse_stock"
                    ON "warehouse_stock"."product_id" = "listings_listingset"."product_id"
                GROUP BY "listings_listingset"."product_id", "warehouse_stock"."quantity") AS B
            ON A.product_id = B.product_id
            WHERE A.needed > B.available
            """, [Order.ORDER_PENDING])

        res = cursor.fetchall()
        return [r[0] for r in res]

    def low_cost_ids(self):
        """
        Returns a list of ids of the listings that have a publishing with a price lower
        than their cost
        """
        from django.db import connection
        cursor = connection.cursor()

        cursor.execute("""SELECT DISTINCT l.id
            FROM listings_listing AS l JOIN listings_publishing AS pu
            ON l.id = pu.listing_id
            WHERE pu.price < (SELECT SUM(s.price * ls.quantity)
                FROM listings_listing AS l1 JOIN listings_listingset AS ls
                ON l1.id = ls.listing_id JOIN goods_product AS p
                ON p.id = ls.product_id LEFT JOIN warehouse_stock AS s
                ON p.id = s.product_id
                WHERE l1.id = l.id)""")

        res = cursor.fetchall()
        return [r[0] for r in res]


class PublishingManager(models.Manager):

    def active_or_last_completed_publishing(self, listing):
        """
        Retrieves all the active publishings for every store,
        if no active publishing found, retrieves last completed publishing.
        """
        active_pubs = listing.publishings.filter(status__contains='Active')
        completed_pubs = listing.publishings.exclude(store_id=active_pubs.values_list('store', flat=True).distinct())
        store_lasts_completed = completed_pubs.values('store').distinct().annotate(last_date=Max('pub_date'))
        for it in store_lasts_completed:

            active_pubs = list(chain(active_pubs, completed_pubs.filter(pub_date=it["last_date"], store_id=it["store"])))
        return active_pubs
