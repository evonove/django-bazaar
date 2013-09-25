from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured

from .models import Product, PriceList


def get_default_price_list():
    """
    Return the default price list
    """
    try:
        return PriceList.objects.get(default=True)
    except PriceList.DoesNotExist:
        raise ImproperlyConfigured("A default price list must exists. Please create one")


def create_product_for_good(good, price, quantity=1):
    """
    Creates a product for the specified `good` with `quantity`. `price` is set to the default price list.
    Returns the new product instance
    """

    product = Product.objects.create(name=good.name, description=good.description)
    product.save()

    # Add good to product elements list
    product.elements.create(good=good, quantity=quantity)

    # Set product's base price on default price list
    default_price_list = get_default_price_list()
    product.prices.create(product=product, price_list=default_price_list, price=price)

    return product
