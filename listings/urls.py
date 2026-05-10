from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, AgencyViewSet, FavoriteViewSet

router = DefaultRouter()
router.register('listings', ListingViewSet, basename='listing')
router.register('agencies', AgencyViewSet, basename='agency')
router.register('favorites', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
]
