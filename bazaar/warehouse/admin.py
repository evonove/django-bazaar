from __future__ import unicode_literals

from django.contrib import admin
from .models import Stock, Movement


class MovementInline(admin.TabularInline):
    model = Movement


class StockAdmin(admin.ModelAdmin):
    inlines = [
        MovementInline,
    ]
    list_display = ('price', 'product', 'quantity')
    raw_id_fields = ('product',)
    search_fields = ['product__name']


admin.site.register(Stock, StockAdmin)
