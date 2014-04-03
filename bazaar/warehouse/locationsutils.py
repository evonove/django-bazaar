from django.db.models import Sum, Avg
from bazaar.warehouse.models import Stock
from locations import get_storage, get_output


def get_stored_quantity(product):
    l = Stock.objects.filter(product=product, location=get_storage()).aggregate(total_quantity=Sum('quantity'))\
        .values('total_quantity')
    return l[0] if l else None


def get_stored_price(product):
    l = Stock.objects.filter(product=product, location=get_storage()).aggregate(total_unit_price=Avg('unit_price'))\
        .values('total_unit_price')
    return l[0] if l else None


def get_output_quantity(product):
    l = Stock.objects.filter(product=product, location=get_output()).aggregate(total_quantity=Sum('quantity'))\
        .values('total_quantity')
    return l[0] if l else None


def get_output_price(product):
    l = Stock.objects.filter(product=product, location=get_output()).aggregate(total_unit_price=Avg('unit_price'))\
        .values('total_unit_price')
    return l[0] if l else None


def get_total_quantity(product):
    l = Stock.objects.filter(product=product, location__in=[get_output(), get_storage()])\
        .aggregate(total_quantity=Sum('quantity')).values('total_quantity')
    return l[0] if l else None


def get_total_price(product):
    l = Stock.objects.filter(product=product, location__in=[get_output(), get_storage()])\
        .aggregate(total_unit_price=Avg('unit_price')).values('total_unit_price')
    return l[0] if l else None