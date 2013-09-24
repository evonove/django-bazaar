from django.contrib import admin
from .models import Warehouse, Stock, Movement


class StockInline(admin.TabularInline):
    model = Stock


class WarehouseAdmin(admin.ModelAdmin):
    inlines = [
        StockInline,
    ]


admin.site.register(Warehouse, WarehouseAdmin)
admin.site.register(Movement)
