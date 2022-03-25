![Actions Status](https://github.com/aleksandrtikhonov/yamdb_final/actions/workflows/main.yml/badge.svg)

# api_yamdb
REST API для сервиса YaMDb, который собирает отзывы пользователей на произведения, с возможностью комментирования отзывов.

### Деплой приложения
Склонировать репозиторий https://github.com/aleksandrtikhonov/yamdb_final
Создать github actions https://github.com/ваш_профиль/ваш_репозиторий/actions
Заменить содержимое .github/workflows/main.yaml на данные из yamdb_workflow.yaml(находится в корне проекта)

В https://github.com/ваш_профиль/ваш_репозиторий/settings/secrets/actions создать новые secrets

```shell
DB_ENGINE
DB_HOST
DB_NAME
DB_PORT
POSTGRES_PASSWORD
POSTGRES_USER
DOCKER_PASSWORD
DOCKER_USERNAME
HOST
SSH_KEY
PASSPHRASE
TELEGRAM_TO
TELEGRAM_TOKEN
TELEGRAM_TOKEN
```

Скопировать на сервер файы из папки infra
Запуск проекта:

```shell
docker-compose up -d
```

При внесении изменений в код на github, проект самостоятельно соберётся и задеплоится на сервер.
_______________________________________________________________
Пример развёрнутого приложения:

```shell
http://tikho.site/api/v1/
http://tikho.site/admin
http://tikho.site/redoc
```
