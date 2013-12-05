from django.contrib import admin

from .models import Listing, Publishing, Store


class ListingAdmin(admin.ModelAdmin):
    model = Listing
    raw_id_fields = ('products',)


admin.site.register(Store)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Publishing)
