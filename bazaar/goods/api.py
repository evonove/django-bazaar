from bazaar.listings.models import Listing


def listing_bulk_creation(products):
    """
    Create a 1x listing for every product that doesn't have it yet
    """
    # import ipdb
    # ipdb.set_trace()
    one_item_listings = Listing.objects.filter(product__compositeproduct__isnull=True)

    products = products.exclude(listings__in=one_item_listings)

    for product in products:
        if not hasattr(product, 'compositeproduct'):
            Listing.objects.create(title=product.name, description=product.description,
                                   picture_url=product.photo, product=product)


def get_oneper_listing_by_product(product):
    try:
        one_item_listing = Listing.objects.get(product=product)
    except Exception:
        one_item_listing = None
    return one_item_listing
