from django.contrib import admin
from .models import Warehouse, Movement


class MovementInline(admin.TabularInline):
    model = Movement


class WarehouseAdmin(admin.ModelAdmin):
    inlines = [
        MovementInline,
    ]


admin.site.register(Warehouse, WarehouseAdmin)
