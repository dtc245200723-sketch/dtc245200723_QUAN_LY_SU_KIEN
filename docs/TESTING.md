# EventHub - Testing Guide

## Validate Docker Compose
Run: docker compose config -q

## Start services
Run: docker compose up --build -d
Check: docker compose ps

## Database migrations
Run: docker compose exec web python manage.py migrate

## Run Django tests
Run: docker compose exec web python manage.py test events
