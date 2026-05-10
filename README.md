# RealEstate Listings API

REST API для поиска и управления объявлениями о недвижимости.

## Стек

- **Django** + **Django REST Framework**
- **PostgreSQL** + **PostGIS** (геолокация)
- **Elasticsearch** (полнотекстовый поиск)
- **Redis** (кэширование)
- **Celery** (асинхронная индексация)
- **Docker** + **Docker Compose**

## Запуск

```bash
git clone https://github.com/artfct23/realestate-listings-api.git
cd realestate-listings-api

cp .env.example .env

docker-compose up --build
```

API доступен на **http://localhost:8000**

Swagger UI: **http://localhost:8000/api/schema/swagger/**

## API

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/listings/` | Список объявлений с фильтрацией |
| POST | `/api/listings/` | Создать объявление |
| GET | `/api/listings/{id}/` | Детали объявления |
| PATCH | `/api/listings/{id}/` | Обновить объявление |
| DELETE | `/api/listings/{id}/` | Удалить объявление |
| GET | `/api/listings/search/?q=текст` | Поиск через Elasticsearch |
| GET | `/api/listings/nearby/?latitude=55.75&longitude=37.60&radius=1000` | Объявления рядом |
| GET | `/api/agencies/` | Список агентств |
| GET | `/api/favorites/` | Избранные объявления |

## Фильтры

```
GET /api/listings/?property_type=apartment
GET /api/listings/?price_min=1000000&price_max=5000000
GET /api/listings/?rooms_min=2&rooms_max=3
```

## Примеры запросов

```bash
# Создать объявление
curl -X POST http://localhost:8000/api/listings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Квартира в центре Москвы",
    "description": "Уютная квартира рядом с метро",
    "price": 5000000,
    "property_type": "apartment",
    "address": "Москва, ул. Арбат, д. 10",
    "latitude": 55.7505,
    "longitude": 37.5964,
    "rooms": 2,
    "square_meters": 54.5,
    "agency_id": 1
  }'

# Поиск по тексту
curl "http://localhost:8000/api/listings/search/?q=квартира+арбат"

# Найти объявления рядом (в радиусе 1км)
curl "http://localhost:8000/api/listings/nearby/?latitude=55.75&longitude=37.60&radius=1000"
```
