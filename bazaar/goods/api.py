from django.db.models import Count
from bazaar.listings.models import Listing, ListingSet


def listing_bulk_creation(product_queryset):
    """
    Create a 1x listing for every product that doesn't have it yet
    """

    products_id = product_queryset.values_list('id', flat=True)
    id_of_products_with_no_listing = set(products_id)

    one_item_listings = Listing.objects.annotate(Count('listing_sets')).filter(
        listing_sets__product__in=products_id,
        listing_sets__count=1,
        listing_sets__quantity=1
    ).all()

    for one_item_listing in one_item_listings:
        product = one_item_listing.listing_sets.all()[0].product
        id_of_products_with_no_listing.remove(product.id)

    products_with_no_listing = product_queryset.filter(id__in=id_of_products_with_no_listing).all()

    for product in products_with_no_listing:
        listing = Listing()
        listing.title = product.name
        listing.description = product.description
        listing.save()

        listingSet = ListingSet.objects.create(listing=listing, product=product, quantity=1)
        listingSet.save()
