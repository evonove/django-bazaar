from django.contrib import admin
from .models import Product, PriceList, ProductElement


class ProductElementInline(admin.TabularInline):
    model = ProductElement


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductElementInline,
    ]


admin.site.register(Product, ProductAdmin)
admin.site.register(PriceList)
