from django.contrib import admin
from .models import Stock, Movement


class MovementInline(admin.TabularInline):
    model = Movement


class StockAdmin(admin.ModelAdmin):
    inlines = [
        MovementInline,
    ]


admin.site.register(Stock, StockAdmin)
