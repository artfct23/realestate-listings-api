from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point


class Agency(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    class Meta:
        verbose_name = 'Агентство'
        verbose_name_plural = 'Агентства'

    def __str__(self):
        return self.name


class Listing(models.Model):
    PROPERTY_TYPES = [
        ('apartment', 'Квартира'),
        ('house', 'Дом'),
        ('commercial', 'Коммерческая'),
        ('land', 'Земельный участок'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    address = models.CharField(max_length=500)
    rooms = models.PositiveIntegerField(null=True, blank=True)
    floor = models.PositiveIntegerField(null=True, blank=True)
    square_meters = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.PointField()
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='listings')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        indexes = [
            models.Index(fields=['price', 'property_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]

    def save(self, *args, **kwargs):
        self.location = Point(self.longitude, self.latitude)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'listing']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
