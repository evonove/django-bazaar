from rest_framework import serializers
from bazaar.listings.models import Listing


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ('id', 'title', 'description')
