from __future__ import unicode_literals
from django.contrib import admin

from .models import Listing, ListingSet, Publishing, Store


class ListingSetInline(admin.TabularInline):
    model = ListingSet
    extra = 1
    raw_id_fields = ('product',)


class ListingAdmin(admin.ModelAdmin):
    inlines = [ListingSetInline]
    model = Listing


class PublishingAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'listing', 'price', 'available_units', 'pub_date', 'last_modified', 'status', 'store', )
    list_filter = ('status', 'pub_date', 'last_modified', )
    search_fields = ('external_id', 'listing__title')


admin.site.register(Store)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Publishing, PublishingAdmin)
