from django.db.models import Count
from bazaar.listings.models import Listing, ListingSet


def listing_bulk_creation(products):
    """
    Create a 1x listing for every product that doesn't have it yet
    """
    one_item_listings = Listing.objects.annotate(Count('listing_sets')).filter(
        listing_sets__count=1,
        listing_sets__quantity=1
    )

    products = products.exclude(listings__in=one_item_listings)

    for product in products:
        one_item_listing = Listing.objects.create(title=product.name, description=product.description)
        ListingSet.objects.create(listing=one_item_listing, product=product, quantity=1)


def get_listing_by_id(id):
    try:
        listing = Listing.objects.get(pk=id)
    except Exception:
        listing = None

    return listing


def get_oneper_listing_by_product(product):
    try:
        one_item_listing = product.listings.annotate(Count('listing_sets')).filter(
            listing_sets__count=1,
            listing_sets__quantity=1
        ).get()
    except Exception:
        one_item_listing = None
    return one_item_listing
