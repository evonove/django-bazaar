from __future__ import unicode_literals

from django.contrib import admin

from .models import Location, Movement


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')

    prepopulated_fields = {
        'slug': ('name',)
    }


class MovementAdmin(admin.ModelAdmin):
    list_display = ('from_location', 'to_location', 'product', 'quantity', 'unit_price', 'date')
    list_filter = ('from_location', 'to_location', 'product', 'date')

    raw_id_fields = ('product',)
    search_fields = ['product__name']


admin.site.register(Location, LocationAdmin)
admin.site.register(Movement, MovementAdmin)
