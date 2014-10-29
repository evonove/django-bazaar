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
        listing = Listing()
        listing.title = product.name
        listing.description = product.description
        listing.save()

        listingSet = ListingSet.objects.create(listing=listing, product=product, quantity=1)
        listingSet.save()
