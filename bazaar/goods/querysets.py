from __future__ import unicode_literals

from django.db import models


from django.utils.datastructures import SortedDict

from django.utils import timezone

FORCED_LOWER = -999999


class ProductsQuerySet(models.QuerySet):

    def with_availability(self, location_storage_id):
        return self.extra(
            select=SortedDict([
                ("availability",
                 "SELECT COALESCE(SUM(quantity), %s) "
                 "FROM warehouse_stock "
                 "WHERE warehouse_stock.product_id = goods_product.id "
                 "AND warehouse_stock.location_id = %s"),
            ]),
            select_params=(
                FORCED_LOWER, location_storage_id,
            )
        )

    def with_total_avr_cost(self, location_storage_id, location_output_id):
        return self.extra(
            select=SortedDict([
                ("total_avr_cost",
                 "SELECT SUM(unit_price*quantity)/SUM(quantity) "
                 "FROM warehouse_stock "
                 "WHERE warehouse_stock.product_id = goods_product.id "
                 "AND(warehouse_stock.location_id = %s OR warehouse_stock.location_id = %s) "
                 "AND quantity != 0 AND "
                    "(SELECT SUM(quantity) "
                    "FROM warehouse_stock "
                    "WHERE warehouse_stock.product_id = goods_product.id "
                    "AND(warehouse_stock.location_id = %s OR warehouse_stock.location_id = %s)) != 0"),
            ]),
            select_params=(
                location_storage_id,
                location_output_id,
                location_storage_id,
                location_output_id
            )
        )

    def with_total_avr_cost_by_locations(self, location_ids):
        where_clause = ' 1 = 0 '
        for location_id in location_ids:
            where_clause += 'OR warehouse_stock.location_id = %s '
        return self.extra(
            select=SortedDict([
                ("total_avr_cost",
                 "SELECT SUM(unit_price*quantity)/SUM(quantity) "
                 "FROM warehouse_stock "
                 "WHERE warehouse_stock.product_id = goods_product.id "
                 "AND({})"
                 "AND quantity != 0 AND "
                    "(SELECT SUM(quantity) "
                    "FROM warehouse_stock "
                    "WHERE warehouse_stock.product_id = goods_product.id "
                    "AND({})) != 0".format(where_clause, where_clause)),
            ]),
            select_params=location_ids + location_ids
        )

    def with_stock_quantity(self, location_storage_id, location_output_id):
        return self.extra(
            select=SortedDict([
                ("stock_quantity",
                 "SELECT COALESCE(SUM(quantity), %s) "
                 "FROM warehouse_stock "
                 "WHERE warehouse_stock.product_id = goods_product.id "
                 "AND (warehouse_stock.location_id = %s OR warehouse_stock.location_id = %s)"),
            ]),
            select_params=(
                FORCED_LOWER, location_storage_id, location_output_id
            )
        )

    def with_sold(self, location_customer_id):
        return self.extra(
            select=SortedDict([(
                "sold",
                "SELECT COALESCE(SUM(quantity), %s) "
                "FROM warehouse_stock WHERE warehouse_stock.product_id = goods_product.id "
                "AND (warehouse_stock.location_id = %s)"),
            ]),
            select_params=(
                FORCED_LOWER, location_customer_id
            )
        )

    def with_last_sold(self, location_customer_id, time_ago, present=timezone.now()):
        return self.extra(
            select=SortedDict([
                ("last_sold",
                 "SELECT COALESCE(SUM(warehouse_movement.quantity), %s) "
                 "FROM warehouse_movement WHERE "
                 "warehouse_movement.product_id = goods_product.id "
                 "AND warehouse_movement.to_location_id = %s "
                 "AND warehouse_movement.date < %s AND warehouse_movement.date > %s"),
            ]),
            select_params=(
                FORCED_LOWER, location_customer_id, present, time_ago
            )
        )
