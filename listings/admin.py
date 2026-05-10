from django.contrib import admin
from .models import Listing, Agency, Favorite, ListingImage


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email']
    search_fields = ['name']


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'property_type', 'agency', 'is_active', 'created_at']
    list_filter = ['property_type', 'is_active']
    search_fields = ['title', 'address']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'created_at']


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ['listing', 'image_url', 'order']
