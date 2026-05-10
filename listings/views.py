from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.core.cache import cache
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from elasticsearch import Elasticsearch
from django.conf import settings

from .models import Listing, Agency, Favorite
from .serializers import (
    ListingSerializer, ListingListSerializer,
    AgencySerializer, FavoriteSerializer, NearbyQuerySerializer,
)
from .filters import ListingFilter
from .tasks import index_listing, delete_listing_from_index


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.filter(is_active=True).select_related('agency', 'created_by')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = ListingFilter
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ListingListSerializer
        return ListingSerializer

    def list(self, request, *args, **kwargs):
        cache_key = f'listings:{request.query_params.urlencode()}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=3600)
        return response

    def perform_create(self, serializer):
        listing = serializer.save(created_by=self.request.user)
        index_listing.delay(listing.id)

    def perform_update(self, serializer):
        listing = serializer.save()
        index_listing.delay(listing.id)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        delete_listing_from_index.delay(instance.id)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'Параметр q обязателен'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        es = Elasticsearch(settings.ELASTICSEARCH_HOST)

        result = es.search(
            index='listings',
            body={
                'query': {
                    'multi_match': {
                        'query': query,
                        'fields': ['title^2', 'description', 'address'],
                    }
                },
                'size': 20,
            }
        )

        listing_ids = [hit['_id'] for hit in result['hits']['hits']]
        listings = Listing.objects.filter(id__in=listing_ids, is_active=True).select_related('agency')
        serializer = ListingListSerializer(listings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        serializer = NearbyQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        lat = serializer.validated_data['latitude']
        lon = serializer.validated_data['longitude']
        radius = serializer.validated_data['radius']

        point = Point(lon, lat, srid=4326)

        listings = (
            Listing.objects
            .filter(is_active=True, location__distance_lte=(point, D(m=radius)))
            .annotate(distance=Distance('location', point))
            .order_by('distance')
            .select_related('agency')[:50]
        )

        serializer = ListingListSerializer(listings, many=True)
        return Response(serializer.data)


class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Favorite.objects
            .filter(user=self.request.user)
            .select_related('listing', 'listing__agency')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
