# Architecture

PortfolioTracker is a self-hosted web application composed of:

- Next.js/React frontend with server rendering and a backend-for-frontend API proxy.
- Django REST Framework API with owner-scoped multi-tenancy.
- PostgreSQL for application data.
- Redis for caching and Celery queues.
- Celery worker and beat processes for price refreshes, snapshots, and retention tasks.
- Nginx as the production reverse proxy.

The browser sends requests through Next.js route handlers. Access and refresh JWTs remain in HTTP-only cookies, and the proxy forwards authenticated requests to Django. Portfolio calculations support FIFO, LIFO, and weighted-average cost. Tax filing integrations use per-country adapters; India currently receives country-neutral analysis while its filing adapter remains intentionally unavailable.
