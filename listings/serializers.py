from rest_framework import serializers
from .models import Listing, Agency, Favorite, ListingImage


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ['id', 'name', 'phone', 'email']


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image_url', 'order']


class ListingSerializer(serializers.ModelSerializer):
    agency = AgencySerializer(read_only=True)
    agency_id = serializers.PrimaryKeyRelatedField(
        queryset=Agency.objects.all(), source='agency', write_only=True
    )
    images = ListingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'price', 'property_type',
            'address', 'rooms', 'floor', 'square_meters',
            'latitude', 'longitude', 'agency', 'agency_id',
            'images', 'is_active', 'created_at', 'updated_at',
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Цена должна быть больше 0')
        return value


class ListingListSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(source='agency.name', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'price', 'property_type',
            'address', 'rooms', 'square_meters',
            'latitude', 'longitude', 'agency_name', 'created_at',
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    listing = ListingListSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), source='listing', write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'listing', 'listing_id', 'created_at']


class NearbyQuerySerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    radius = serializers.IntegerField(default=1000, min_value=100, max_value=50000)
