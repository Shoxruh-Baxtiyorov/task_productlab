## DEVELOPMENT
### Список зависимостей:
  1. **docker**
  2. **nginx**
  3. **node.js**
  4. **yarn**

### Начало
Копировать репозиторий

    git clone https://git.tablecrm.com/deadlinetaskbot/dtaskbot.git

Установить зависимости
#### Docker
https://docs.docker.com/engine/install/ubuntu/#installation-methods

>Добавить пользователя в группу docker

    sudo usermod -aG docker username
    
#### Nginx
    sudo apt update
    sudo apt install nginx
#### Node.js

    sudo apt update
    sudo apt install nodejs
#### Yarn
https://classic.yarnpkg.com/lang/en/docs/install/#debian-stable
#### Настройка nginx
Из папки nginx файл nginx.conf заменить в /etc/nginx

    sudo cp -i nginx.conf /etc/nginx
    
 Создать файл deadlinetaskbot.conf в /etc/nginx/conf.d
 
    sudo nano /etc/nginx/conf.d/deadlinetaskbot.conf

 Содержимое deadlinetaskbot.conf
 
    server {
        listen 80;
        listen [::]:80;
        server_name localhost www.localhost;

        location / {
        root /var/www/deadlinetaskbot;
        index index.html index.htm;
        try_files $uri /index.html;
    }

    location /api/v1/ {
        proxy_pass http://localhost:8000/;
        include proxy_params;
    }

    location /adminer/ {
        proxy_pass http://localhost:8080/;
        include proxy_params;
        
    }}

#### Backend
Создать .env файл в директории dtaskbot

    ADMINS='[673251511, 5694678303]'


    BOT_ADDRESS=Ссылка на твоего тестового бота - пример(https://t.me/pvemole_bot) (@BotFather)
    TOKEN=Токен твоего тестового бота

    DB_HOST=db
    DB_NAME=bot
    DB_PASSWORD=oV£m2rM>03!0
    DB_PORT=5432
    DB_USER=postgres

    URL=localhost
    RABBIT_HOST=rabbitmq

В директории dtaskbot выпонлить

    docker compose build
    docker compose up -d


Если возникают ошибки - проверьте своё окружение на наличее переменных (логи можно посмотреть через `docker compose logs`)

#### WebApp
В папке WebApp выполнить

    yarn install
    yarn build

Создать папку webapp в /var/www и копировать содержимое dist

    sudo mkdir /var/www/webapp
    sudo cp -r dist/* /var/www/webapp


####  Frontend 
В папке frontend выполнить

    sudo npm install --global yarn
    sudo yarn install
    sudo REACT_APP_DTASKBOT_API_URL=/api/v1 yarn build

Создать папку deadlinetaskbot в /var/www и копировать содрежимое build

    sudo mkdir /var/www/deadlinetaskbot
    sudo cp -r build/* /var/www/deadlinetaskbot
    
Выполнить перезагрузку nginx

    sudo nginx -t
    sudo systemctl reload nginx


URL фронт, апи, админер

    localhost
    localhost/api/v1
    localhost/adminer
    localhost/webapp

## PRODUCTION
### Список зависимостей:
  1. **gitlab-runner** 
  2. **docker** 
  3. **nginx** 
  4. **certbot + python3-certbot-nginx**

### Настройка gitlab-runner

>- Выдача прав раннеру к докеру
> ```shell
> sudo usermod -aG docker gitlab-runner
> ```
>- Выдача прав к папке /etc/nginx
> ```shell
> sudo chown -R gitlab-runner:gitlab-runner /etc/nginx
> ```
>- Выдача прав к папке /var/www
> ```shell
> sudo chown -R gitlab-runner:gitlab-runner /var/www
> ```
>
>- Заходим под пользователем раннера
> ```shell
> sudo su - gitlab-runner
> ```
>
>- Установите [node](https://nodejs.org/en/download/package-manager/all) и [yarn](https://classic.yarnpkg.com/lang/en/docs/install/)
> 
>- Перезапустите раннер
>
> ```shell
> sudo gitlab-runner restart
> ```

### Настройка docker
_Докер не нуждается в настройке_

### Настройка nginx
_Для настройки nginx используйте job=conf_nginx в gitlab-ci_

### Настройка certbot 
`Автообновление через crontab`
> ```shell
> sudo crontab -e
> ```
>- Вставьте строку ниже
> ```text
> 0 3 * * 0 /usr/bin/certbot renew --quiet --nginx && systemctl reload nginx
> ```
