# Краткий обзор архитектуры и изменений

## Архитектура (кратко)
- Backend: FastAPI (/api/v1), RabbitMQ-consumers, Telegram-бот (Aiogram).
- DB/MQ: PostgreSQL 16, RabbitMQ, Adminer (через Nginx proxy).
- Frontend: React (CRA), статика в /var/www/deadlinetaskbot.
- WebApp: Vite/React (TWA), статика в /var/www/webapp.
- Nginx: отдаёт статику, проксирует /api/v1 на активный backend.
- CI/CD: GitLab CI. Добавлены опциональные blue/green job’ы (включаются BLUE_GREEN=true).

## Сделано для Zero Downtime (Blue-Green)
1. Добавлены compose-файлы:
   - docker-compose.core.yml — общий стек (db, rabbitmq, adminer, backup, сеть dtaskbot-net).
   - docker-compose.app-blue.yml и docker-compose.app-green.yml — backend/tg_bot/consumers по цветам, healthcheck.
2. Nginx: активный include для upstream и proxy_pass на dtaskbot_upstream.
3. Backend: эндпоинт GET /api/v1/health для healthchecks и smoke.
4. GitLab CI: blue/green job’ы — build/push, deploy в неактивный цвет, выкладка статики, smoke, switch, rollback.
