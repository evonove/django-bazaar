from django.contrib import admin
from .models import Good, Product, PriceList


class ProductGoodInline(admin.TabularInline):
    model = Product.goods.through


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductGoodInline,
    ]


admin.site.register(Good)
admin.site.register(Product, ProductAdmin)
admin.site.register(PriceList)
