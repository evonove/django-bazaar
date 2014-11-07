from __future__ import unicode_literals

from django.db import models
from model_utils.managers import PassThroughManager, InheritanceManagerMixin

FORCED_LOWER = -999999


class ListingManager(models.Manager):
    def high_availability(self):
        """
        Returns a list of ids of the listings for which the quantity of a product in stock
        is less than the amount needed to satisfy it
        """
        from django.db import connection
        from models import Order, Publishing
        cursor = connection.cursor()

        # FIXME: following query do not work for listings composed by multiple product
        cursor.execute("""
            SELECT DISTINCT A.listing_id FROM
                (SELECT
                    "listings_publishing"."listing_id",
                    "listings_listingset"."product_id",
                    "listings_listingset"."quantity",
                    "listings_publishing"."available_units"
                      AS "needed"
                FROM "listings_publishing"
                    JOIN "listings_listingset"
                    ON ("listings_publishing"."listing_id" = "listings_listingset"."listing_id")
                -- following where selects main publishings
                WHERE "listings_publishing"."pub_date" IN (
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
                ) AS A
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
            WHERE A.needed < DIV(B.available, A.quantity)
            """, [Publishing.ACTIVE_PUBLISHING, Publishing.ACTIVE_PUBLISHING, Order.ORDER_PENDING])

        res = cursor.fetchall()
        return [r[0] for r in res]

    def unavailable_ids(self):
        """
        Returns a list of ids of the listings for which the quantity of a product in stock
        is less than the amount needed to satisfy it
        """
        from django.db import connection
        from models import Order, Publishing
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
                    ON "listings_publishing"."listing_id" = "listings_listingset"."listing_id"
                -- following where selects main publishings
                WHERE "listings_publishing"."pub_date" IN (
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
                ) AS A
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
            """, [Publishing.ACTIVE_PUBLISHING, Publishing.ACTIVE_PUBLISHING, Order.ORDER_PENDING])

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


class PublishingsManager(InheritanceManagerMixin, PassThroughManager):

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
