# Banas API

A production-ready Django REST API for managing a milk delivery business: customers, daily entries, billing, payments, and route management. Includes JWT authentication, async task processing with Celery, Redis-backed caching/queues, S3-based media storage, and containerized deployment.

## Features

- Authentication with JWT (access + refresh)
- Customer management and account tracking
- Daily entry recording (including QR-based flows)
- Billing and payment workflows
- Route management
- Dashboard analytics
- Caching and async background jobs (Celery + Redis)
- Swagger UI and OpenAPI schema
- Docker and docker-compose for development and deployment

## Tech Stack

- Django: Web framework providing the project structure, ORM, templating, and admin.
- Django REST Framework (DRF): API layer for serializers, viewsets, and authentication integration.
- SimpleJWT: JWT-based authentication, with access/refresh tokens and configurable lifetimes.
- Celery: Distributed task queue for background processing (e.g., scheduled jobs, heavy tasks).
- Redis: Message broker and cache backend used by Celery and Django caching.
- PostgreSQL: Relational database for reliable data persistence.
- drf-yasg: Generates interactive Swagger UI and OpenAPI schemas for the API.
- WhiteNoise: Efficient static files serving in production-like environments.
- Django CORS Headers: Handles Cross-Origin Resource Sharing for frontend integrations.
- django-import-export: Simplifies data import/export via the admin.
- Django Storages + boto3 (S3): Stores media on Amazon S3, generating publicly accessible URLs.
- Gunicorn: WSGI HTTP server for running Django in containers.
- Docker + docker-compose: Containerization for local dev and deployment workflows.

## Getting Started

### Prerequisites

- Docker (recommended) or Python 3.11+
- Redis and PostgreSQL instances (docker-compose provides these)
- AWS S3 bucket and credentials (for media) or adjust settings for local media

### Environment Variables

Create a `.env` file at the project root with the following keys (examples shown as placeholders):

```
DJANGO_SETTINGS_MODULE=banas.settings
DEBUG=1
SECRET_KEY={{DJANGO_SECRET_KEY}}

DB_NAME=banas
DB_USER=postgres
DB_PASSWORD={{POSTGRES_PASSWORD}}
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_USERNAME={{EMAIL_USERNAME}}
EMAIL_APP_PASSWORD={{EMAIL_APP_PASSWORD}}

AWS_ACCESS_KEY_ID={{AWS_ACCESS_KEY_ID}}
AWS_SECRET_ACCESS_KEY={{AWS_SECRET_ACCESS_KEY}}
AWS_STORAGE_BUCKET_NAME={{AWS_STORAGE_BUCKET_NAME}}
AWS_S3_REGION_NAME={{AWS_S3_REGION_NAME}}
```

Note: Replace all {{PLACEHOLDER}} values with your actual secrets via environment management. Do not commit secrets to VCS.

### Local Development (Docker)

1. Build and start the stack:
   - `docker compose up --build`
2. Apply migrations and create a superuser (if not handled by entrypoint):
   - `docker compose exec api python manage.py migrate`
   - `docker compose exec api python manage.py createsuperuser`
3. Access services:
   - API: http://localhost:8000/
   - Django Admin: http://localhost:8000/banas/secure/admin/
   - Swagger UI: http://localhost:8000/swagger/

### Local Development (Python only)

1. Create and activate a virtual environment (example with venv):
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Configure `.env` as described above.
4. Run migrations and start the server:
   - `python manage.py migrate`
   - `python manage.py runserver 0.0.0.0:8000`

## OpenAPI / Swagger

- The OpenAPI schema is available at `swagger.yaml` in the project root.
- Interactive docs are available at `/swagger/` (powered by drf-yasg).

To validate the schema locally:
- `pip install openapi-spec-validator`
- `python -c "from openapi_spec_validator import validate_spec; import yaml; print(validate_spec(yaml.safe_load(open('swagger.yaml'))))"`

## Authentication

- Obtain tokens: `POST /api/login/` with `{"username": "...", "password": "..."}`
- Refresh token: `POST /api/user/token/refresh/` with `{"refresh": "..."}`
- Use the access token by setting: `Authorization: Bearer <access_token>`

Token lifetimes are configured in `banas/settings.py` under `SIMPLE_JWT`.

## Common Workflows

- Customers: CRUD via `/api/customer/` and `/api/customer/{id}/`
- Daily Entries: create/view via `/api/dailyentry/` and related routes
- Bills: list and generate via `/api/bill/bills/` and `/api/bill/generatebill/{customer_id}/`
- Payments: record and list via `/api/payment/` and `/api/payment/customer/{customer_id}/`
- Routes: manage via `/api/route/` and `/api/route/{id}/`

## Running Tests

- Django tests:
  - `python manage.py test`
- You can scope tests to an app:
  - `python manage.py test customer`

## Linting & Formatting (optional)

You can add tools like black, isort, flake8. Example commands if configured:
- `black .`
- `isort .`
- `flake8`

## Deployment Notes

- Gunicorn is configured in docker-compose to run the app.
- WhiteNoise serves static files; ensure `collectstatic` is run in your pipeline.
- Ensure appropriate `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` are configured for your deployment domain.

## License

MIT
