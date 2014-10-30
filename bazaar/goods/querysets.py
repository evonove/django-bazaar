from __future__ import unicode_literals

import sys
from django.db import models


from django.utils.datastructures import SortedDict

from django.utils import timezone


FORCED_LOWER = -(sys.maxint - 1)


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

    def with_stock_price(self, location_storage_id, location_output_id):
        return self.extra(
            select=SortedDict([
                ("stock_price",
                 "SELECT AVG(unit_price) "
                 "FROM warehouse_stock "
                 "WHERE warehouse_stock.product_id = goods_product.id "
                 "AND(warehouse_stock.location_id = %s OR warehouse_stock.location_id = %s)"),
            ]),
            select_params=(
                location_storage_id,
                location_output_id
            )
        )

    def with_cost(self, location_storage_id):

        return self.extra(
            select=SortedDict([
                ("computed_cost",
                 "SELECT AVG(unit_price) "
                 "FROM warehouse_stock "
                 "WHERE warehouse_stock.product_id = goods_product.id "
                 "AND warehouse_stock.location_id = %s"),
            ]),
            select_params=(
                location_storage_id,
            )
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
                ("sold_last_month",
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
