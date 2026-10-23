# dtc245200723_QUAN_LY_SU_KIEN

Project implementing an event management system with Django, PostgreSQL, Nginx, monitoring, logging, and security hardening using Docker Compose.

## Overview

This project provides:

- Django web app for event listing, registration, ticket management, and admin.
- PostgreSQL as the database backend.
- pgAdmin for database administration.
- Nginx with self-signed TLS certificate as reverse proxy.
- Prometheus and Grafana for system monitoring.
- Django and PostgreSQL metrics exported to Prometheus.
- Loki and Promtail for centralized logging.
- Docker Compose deployment with isolated frontend/backend networks.

## Prerequisites

- Docker Desktop or Docker Engine with Compose V2
- OpenSSL for generating local certificates
- Access to the project folder on a local machine

## Setup

1. Create the environment file:
   - In PowerShell, run `Copy-Item .env.example .env` (skip if `.env` already exists).
   - Replace all sample passwords and the Django secret with strong, unique values.
   - Keep `.env` private; it is excluded from Git.

2. Generate a self-signed certificate:

Run this from PowerShell in the repository directory:

```powershell
New-Item -ItemType Directory -Force nginx\certs
openssl req -x509 -nodes -newkey rsa:2048 -keyout nginx\certs\server.key -out nginx\certs\server.crt -days 365 -subj "/CN=localhost"
```

3. Start the stack:

```bash
docker compose config -q
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
- Loki API (local diagnostics): http://localhost:3100

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
- Confirm `prometheus`, `node-exporter`, `cadvisor`, `postgres-exporter`, `nginx-exporter`, and `django-web` targets are `UP`.
- Grafana provisions Prometheus and Loki with stable datasource IDs.
- Dashboard: **Event Monitoring Dashboard** includes CPU, memory, Nginx traffic, PostgreSQL connections, Django request rate, and scrape status.
- Django `/metrics` is collected internally by Prometheus; it is not exposed through the public Nginx proxy.
- Nginx `stub_status` listens on the internal-only container port `8081` for the exporter.

## Logging verification

In Grafana **Explore**, select the Loki datasource and run these LogQL queries:

```logql
{compose_service="web"}
{compose_service="web"} |= "ERROR"
{compose_service="nginx"} |~ "\" 5[0-9][0-9] "
sum by (compose_service) (count_over_time({compose_service=~".+"}[5m]))
```

The final query counts log entries over five minutes grouped by service.

## Automated checks

Run these after starting the stack:

```powershell
docker compose exec web python manage.py test events
docker compose exec nginx nginx -t
docker compose exec prometheus promtool check config /etc/prometheus/prometheus.yml
curl.exe -k https://localhost/health/
```

Expected results: Django tests pass, Nginx reports a successful configuration test, Prometheus reports valid configuration, and the health endpoint returns HTTP 200.

## Hardening notes

- Django runs as a non-root user inside the container.
- Sensitive values are managed via `.env` instead of being committed.
- The `backend` network isolates PostgreSQL, pgAdmin, exporters, and logging services from direct public access; the `frontend` network connects only services that need web traffic.
- Event creation, editing, and deletion are restricted to staff accounts.
- Nginx exposes only HTTP/HTTPS for external access.
- Security headers are configured in the Nginx reverse proxy.
- PostgreSQL, pgAdmin, Prometheus, Grafana, Loki, and exporter host ports are bound to loopback where published.
- Nginx status metrics are available only on its internal Compose network.
- Use self-signed TLS certificates only for local testing.

## Demo evidence and report

The Vietnamese report draft is available at `docs/Bao_cao_de_tai_26_quan_ly_su_kien.docx`. It includes the architecture illustration and clearly marked screenshot placeholders.

For the submission, capture screenshots showing the website, pgAdmin connected to PostgreSQL, all Prometheus targets up, the Grafana dashboard, at least three successful Loki queries, and the Nginx security headers. Include these in the report along with the student cover page and system/implementation explanations. Do not include `.env` or private keys in screenshots or the GitHub repository.

## Troubleshooting

- If PostgreSQL is not ready, wait for `db` health to become healthy.
- If the app does not start, run `docker compose logs web`.
- If Grafana does not show data, wait a few minutes for Prometheus scrapes.
- If Nginx TLS fails, confirm the certificate files exist and are readable.

## GitHub repository

Repository name: `dtc245200723_QUAN_LY_SU_KIEN`
