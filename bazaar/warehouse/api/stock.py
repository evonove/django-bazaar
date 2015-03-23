from __future__ import unicode_literals
from __future__ import division

import collections

from django.db.models import Sum

from ...utils import money_to_default


__all__ = [
    "get_stock_quantity", "get_stock_price", "get_storage_quantity", "get_storage_price",
    "get_customer_price", "get_customer_quantity", "get_output_price", "get_output_quantity",
    "get_lostandfound_price", "get_lostandfound_quantity", "get_supplier_price",
    "get_supplier_quantity",
]


def get_single_product_stock_quantity(product, location_type=None, **kwargs):
    from ..models import Stock

    qs = Stock.objects.filter(product=product, **kwargs)

    if location_type:
        if isinstance(location_type, collections.Sequence):
            qs = qs.filter(location__type__in=location_type)
        else:
            qs = qs.filter(location__type=location_type)

    result = qs.aggregate(Sum("quantity"))

    return result["quantity__sum"] or 0


def get_stock_quantity(product, location_type=None, **kwargs):
    is_composite = hasattr(product, 'compositeproduct')
    if is_composite:
        quantities = []
        for product_set in product.compositeproduct.product_sets.all():
            quantity = get_single_product_stock_quantity(product_set.product, location_type=location_type, **kwargs)
            quantity = quantity // product_set.quantity
            quantities.append(quantity)
        return min(quantities)
    else:
        return get_single_product_stock_quantity(product, location_type=location_type, **kwargs)


def get_stock_price_for_single_product(product, location_type=None, **kwargs):
    from ..models import Stock

    qs = Stock.objects.filter(product=product, **kwargs)

    if location_type:
        if isinstance(location_type, collections.Sequence):
            qs = qs.filter(location__type__in=location_type)
        else:
            qs = qs.filter(location__type=location_type)

    stocks = qs.values("unit_price", "quantity")

    if len(stocks) > 0:
        # compute a weighted arithmetic mean or standard mean if weights sum is 0
        weights = sum(map(lambda s: s["quantity"], stocks))
        if weights != 0:
            value = sum(map(lambda s: s["unit_price"] * s["quantity"], stocks)) / weights
        else:
            value = sum(map(lambda s: s["unit_price"], stocks)) / len(stocks)
    else:
        value = 0

    return money_to_default(value)


def get_stock_price(product, location_type=None, **kwargs):
    is_composite = hasattr(product, 'compositeproduct')
    cost = 0
    sets = 0
    if is_composite:
        for product_set in product.compositeproduct.product_sets.all():
            cost += get_stock_price_for_single_product(product_set.product, location_type=location_type, **kwargs)
            sets += 1
        cost = cost / sets
    else:
        cost = get_stock_price_for_single_product(product, location_type=location_type, **kwargs)
    return cost


def get_supplier_quantity(product, **kwargs):
    from ..models import Location
    return get_stock_quantity(product, Location.LOCATION_SUPPLIER, **kwargs)


def get_supplier_price(product, **kwargs):
    from ..models import Location
    return get_stock_price(product, Location.LOCATION_SUPPLIER, **kwargs)


def get_storage_quantity(product, **kwargs):
    from ..models import Location
    return get_stock_quantity(product, Location.LOCATION_STORAGE, **kwargs)


def get_storage_price(product, **kwargs):
    from ..models import Location
    return get_stock_price(product, Location.LOCATION_STORAGE, **kwargs)


def get_output_quantity(product, **kwargs):
    from ..models import Location
    return get_stock_quantity(product, Location.LOCATION_OUTPUT, **kwargs)


def get_output_price(product, **kwargs):
    from ..models import Location
    return get_stock_price(product, Location.LOCATION_OUTPUT, **kwargs)


def get_customer_quantity(product, **kwargs):
    from ..models import Location
    return get_stock_quantity(product, Location.LOCATION_CUSTOMER, **kwargs)


def get_customer_price(product, **kwargs):
    from ..models import Location
    return get_stock_price(product, Location.LOCATION_CUSTOMER, **kwargs)


def get_lostandfound_quantity(product, **kwargs):
    from ..models import Location
    return get_stock_quantity(product, Location.LOCATION_LOST_AND_FOUND, **kwargs)


def get_lostandfound_price(product, **kwargs):
    from ..models import Location
    return get_stock_price(product, Location.LOCATION_LOST_AND_FOUND, **kwargs)
