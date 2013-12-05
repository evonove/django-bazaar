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


admin.site.register(Store)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Publishing)
