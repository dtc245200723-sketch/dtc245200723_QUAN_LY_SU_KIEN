# dtc245200723_QUAN_LY_SU_KIEN

Project implementing an event management system with Django, PostgreSQL, Nginx, monitoring, logging, and security hardening using Docker Compose.

## Overview

This project provides:

- Django web app for event listing, registration, ticket management, and admin.
- PostgreSQL as the database backend.
- pgAdmin for database administration.
- Nginx with self-signed TLS certificate as reverse proxy.
- Prometheus and Grafana for system monitoring.
- Loki and Promtail for centralized logging.
- Docker Compose deployment with isolated frontend/backend networks.

## Prerequisites

- Docker Desktop or Docker Engine with Compose V2
- OpenSSL for generating local certificates
- Access to the project folder on a local machine

## Setup

1. Create the environment file:
   - Copy `.env.example` to `.env`
   - Update the values for your local environment

2. Generate a self-signed certificate:

```bash
mkdir -p nginx/certs
openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout nginx/certs/server.key \
  -out nginx/certs/server.crt \
  -days 365 \
  -subj "/CN=localhost"
```

3. Start the stack:

```bash
docker compose up --build -d
```

4. Check service health:

```bash
docker compose ps
docker compose logs -f web db nginx
```

## Access URLs

- Web app (HTTPS): https://localhost
- Admin login: https://localhost/admin/
- pgAdmin: http://localhost:5050
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Default credentials

Use values defined in `.env`.

## Core functionality

- Event listing and details
- User signup/login/logout
- Event creation/editing/deletion by staff/admin
- Registration and ticket generation
- Ticket and registration history
- Admin panel via Django

## Monitoring verification

- Prometheus targets: http://localhost:9090/targets
- Grafana datasource: Prometheus and Loki should be auto-provisioned
- Dashboard: Event Monitoring Dashboard should appear in Grafana

## Logging verification

The following Loki queries should return logs when the services are active:

```logql
{compose_service="web"}
{compose_service="web"} |= "ERROR"
{compose_service="nginx"} |~ "\" 5[0-9][0-9] "
```

## Hardening notes

- Django runs as a non-root user inside the container.
- Sensitive values are managed via `.env` instead of being committed.
- Internal services use backend/frontend Docker networks.
- Nginx exposes only HTTP/HTTPS for external access.
- Security headers are configured in the Nginx reverse proxy.
- Use self-signed TLS certificates only for local testing.

## Troubleshooting

- If PostgreSQL is not ready, wait for `db` health to become healthy.
- If the app does not start, run `docker compose logs web`.
- If Grafana does not show data, wait a few minutes for Prometheus scrapes.
- If Nginx TLS fails, confirm the certificate files exist and are readable.

## GitHub repository

Repository name: `dtc245200723_QUAN_LY_SU_KIEN`
