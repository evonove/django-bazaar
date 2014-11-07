from __future__ import unicode_literals

from django.db import models
import collections

from django.utils.datastructures import SortedDict

from django.utils import timezone
from model_utils.managers import InheritanceQuerySetMixin

FORCED_LOWER = -999999


class ProductsQuerySet(InheritanceQuerySetMixin, models.QuerySet):

    def with_availability(self, location_id):
        return self.extra(
            select=SortedDict([
                ("availability",
                 "SELECT COALESCE(SUM(quantity), %s) "
                 "FROM warehouse_stock "
                 "WHERE warehouse_stock.product_id = goods_product.id "
                 "AND warehouse_stock.location_id = %s"),
            ]),
            select_params=(
                FORCED_LOWER, location_id,
            )
        )

    def with_total_avr_cost(self, location_ids):
        if not isinstance(location_ids, collections.Sequence):
            location_ids = [location_ids]
        dynamic_quantity = ', '.join(['%s'] * len(location_ids))

        return self.extra(
            select=SortedDict([
                ("total_avr_cost",
                 "SELECT SUM(unit_price*quantity)/SUM(quantity) "
                 "FROM warehouse_stock "
                 "WHERE warehouse_stock.product_id = goods_product.id "
                 "AND warehouse_stock.location_id IN ({}) "
                 "AND quantity > 0".format(dynamic_quantity)),
            ]),
            select_params=location_ids
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
