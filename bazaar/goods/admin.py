from django.contrib import admin
from .models import Product, PriceList, ProductElement, ProductPrice


class ProductElementInline(admin.TabularInline):
    model = ProductElement


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductElementInline,
    ]


class ProductInline(admin.TabularInline):
    model = ProductPrice


class PriceListAdmin(admin.ModelAdmin):
    inlines = [
        ProductInline,
    ]


admin.site.register(Product, ProductAdmin)
admin.site.register(PriceList, PriceListAdmin)
