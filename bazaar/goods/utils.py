from __future__ import unicode_literals

from .models import Product, PriceList


def create_product_for_good(good, price, quantity=1, name=None):
    """
    Creates a product for the specified `good` with `quantity`. `price` is set to the default price list.
    Returns the new product instance
    """
    product_name = name or good.name

    product = Product.objects.create(name=product_name, description=good.description)
    product.save()

    # Add good to product elements list
    product.elements.create(good=good, quantity=quantity)

    # Set product's base price on default price list
    default_price_list = PriceList.objects.get_default()
    product.prices.create(product=product, price_list=default_price_list, price=price)

    return product
