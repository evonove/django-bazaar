from django.contrib import admin
from .models import Product, PriceList, ProductPrice


class ProductInline(admin.TabularInline):
    model = ProductPrice
    raw_id_fields = ('product',)


class PriceListAdmin(admin.ModelAdmin):
    inlines = [
        ProductInline,
    ]


admin.site.register(Product)
admin.site.register(PriceList, PriceListAdmin)
