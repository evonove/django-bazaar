from __future__ import unicode_literals
from django.contrib import admin

from .models import Listing, Publishing, Store


class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', )
    search_fields = ('sku', )
    model = Listing


class PublishingAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'listing', 'price', 'available_units',
                    'pub_date', 'last_modified', 'status', 'store', )
    list_filter = ('status', 'pub_date', 'last_modified', )
    search_fields = ('external_id', 'listing__title')


admin.site.register(Store)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Publishing, PublishingAdmin)
