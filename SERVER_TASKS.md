# Краткий чеклист задач на сервере

1) Upstream и симлинки Nginx
- Создать/проверить файлы:
  - /etc/nginx/conf.d/dtaskbot-upstreams-blue.conf
  - /etc/nginx/conf.d/dtaskbot-upstreams-green.conf
- Активный include (симлинк):
  - ln -sfn /etc/nginx/conf.d/dtaskbot-upstreams-blue.conf /etc/nginx/conf.d/dtaskbot-upstream-active.conf
- Проверка и reload:
  - nginx -t && systemctl reload nginx

2) Каталоги статики по цветам и активные ссылки
- mkdir -p /var/www/deadlinetaskbot-blue /var/www/deadlinetaskbot-green
- mkdir -p /var/www/webapp-blue /var/www/webapp-green
- Симлинки активной статики:
  - ln -sfn /var/www/deadlinetaskbot-blue /var/www/deadlinetaskbot
  - ln -sfn /var/www/webapp-blue /var/www/webapp

3) Переменные CI/CD
- В GitLab CI Variables задать:
  - BLUE_GREEN=true (для запуска blue/green пайплайна)
  - REACT_APP_DTASKBOT_API_URL, BOT_ADDRESS, VITE_API_BASE_URL, VITE_BOT_USERNAME и др. как раньше
  - доступ к Registry (CI_REGISTRY, логин/токен), если используем build/push

4) Пайплайн blue/green (в .gitlab-ci.yml уже добавлен)
- build_backend_image, build_webapp_image (при необходимости)
- deploy_inactive_color
- smoke_tests_inactive
- nginx_switch_color
- rollback_color (manual)

5) База и миграции (expand-first)
- Миграции должны быть совместимыми с активной версией
- Выполнять upgrade на неактивном деплое перед переключением
- Удаляющие/NOT NULL шаги — после успешного переключения

6) Мониторинг/проверки
- Smoke: curl -f http://<backend-цвет>:8000/api/v1/health
- Проверка доступности статики в /var/www/<app>-<цвет>

Примечание: текущие джобы остаются рабочими; blue/green включается только при BLUE_GREEN=true.
