from celery import shared_task
from elasticsearch import Elasticsearch
from django.conf import settings


def get_es_client():
    return Elasticsearch(settings.ELASTICSEARCH_HOST)


@shared_task(bind=True, max_retries=3)
def index_listing(self, listing_id):
    from .models import Listing
    try:
        listing = Listing.objects.select_related('agency').get(id=listing_id)
        es = get_es_client()

        doc = {
            'listing_id': listing.id,
            'title': listing.title,
            'description': listing.description,
            'price': float(listing.price),
            'property_type': listing.property_type,
            'address': listing.address,
            'rooms': listing.rooms,
            'latitude': listing.latitude,
            'longitude': listing.longitude,
            'agency_name': listing.agency.name,
            'is_active': listing.is_active,
        }

        es.index(index='listings', id=listing.id, document=doc)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def delete_listing_from_index(self, listing_id):
    try:
        es = get_es_client()
        es.delete(index='listings', id=listing_id, ignore=[404])
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task
def reindex_all_listings():
    from .models import Listing
    listing_ids = Listing.objects.filter(is_active=True).values_list('id', flat=True)
    for listing_id in listing_ids:
        index_listing.delay(listing_id)
